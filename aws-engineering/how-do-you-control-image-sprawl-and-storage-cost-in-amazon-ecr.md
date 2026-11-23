---
title: "How do you control image sprawl and storage cost in Amazon ECR?"
id: 795
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - aws-engineering
  - ecr
  - containers
  - cloud-cost-optimization
quiz:
  stem: "A team wants ECR to delete untagged images after 7 days and keep only the 30 most recent `build-` images. What is the recommended mechanism?"
  options:
    - "A scheduled Lambda function that lists images and calls batch-delete-image every night"
    - "An ECR lifecycle policy with one rule for untagged images (sinceImagePushed) and one for the build- prefix (imageCountMoreThan)"
    - "An S3 lifecycle rule on the bucket that stores ECR layers"
    - "Enabling tag immutability, which removes older images automatically"
  answer: 2
  explanation: "ECR lifecycle policies are the native, free way to expire images by age or count, selected by tag status and tag prefix or pattern. ECR's backing storage is not exposed as an S3 bucket, and tag immutability only prevents tags being overwritten - it deletes nothing."
---

# How do you control image sprawl and storage cost in Amazon ECR?

**Short answer:** Attach an **ECR lifecycle policy** to every repository, managed in IaC, instead of writing a cleanup Lambda. A typical policy has a rule that expires **untagged** images a few days after push, a rule that keeps only the last N **build or PR** images by tag prefix, and a longer-lived rule for **release** tags, so anything you might roll back to survives. Preview the policy before enforcing it, turn on **tag immutability** so a tag always means one image, and remember that a lifecycle policy has no idea what is deployed - retention for release tags has to cover your rollback window.

## Detail

### Why registries grow without limit

Every CI build pushes an image. Overwriting a mutable tag such as `latest` or `main` leaves the previous image behind as **untagged**, still billed for storage. Multi-arch builds add per-architecture manifests and attestations. Nobody deletes anything because nobody is sure what is still in use, so storage grows linearly with build count, along with the scan findings and noise that come with thousands of stale images.

### How lifecycle policies work

A lifecycle policy is a JSON document of **rules**, each with:

- `rulePriority`: a unique integer; lower numbers are evaluated first, and an image is handled by the first rule that selects it.
- `selection`: `tagStatus` (`tagged`, `untagged` or `any`), a `tagPrefixList` or `tagPatternList` (wildcards) for tagged rules, and a count:
  - `countType: imageCountMoreThan` with `countNumber` - keep the newest N matching images, expire the rest.
  - `countType: sinceImagePushed` with `countUnit: days` - expire images older than N days.
- `action`: `expire`.

Rules worth knowing precisely:

- A rule with `tagStatus: any` must have the **highest** `rulePriority` value, so it acts as the catch-all at the end.
- If a rule lists several prefixes or patterns, an image must match **all** of them to be selected - not any of them. One prefix per rule avoids surprises.
- Expiry is asynchronous; images are usually removed within about a day of becoming eligible, so do not expect an instant drop in storage.
- Lifecycle policies are free; you only stop paying for the storage they release.

**Preview before enforcing.** `start-lifecycle-policy-preview` evaluates a draft policy against the repository and lists exactly which images it would expire, without deleting anything. Run it on the largest repositories before rolling out a shared policy.

### The part a policy cannot know

ECR does not know which images are running. If a Deployment still references `api:build-1234` and the policy expires it, nothing breaks until a node is replaced or a Pod reschedules - then you get `ImagePullBackOff` during an incident, which is the worst possible moment. Mitigations:

- Deploy **release tags** (`v1.42.0`) or digests from a release process, and give that prefix a generous retention (for example 180 days, or the last 50) that comfortably exceeds your rollback window.
- Keep aggressive count limits for disposable prefixes only (`pr-`, `build-`, `feature-`).
- Enable **tag immutability** so a release tag can never be overwritten and orphaned - which also means pipelines must stop pushing moving tags such as `latest` to that repository.
- If you need "never delete anything currently deployed", add a guard - a script or admission check that compares cluster image references with the expiry preview - rather than replacing lifecycle policies with a hand-written deleter.

### Why not a scheduled Lambda

A daily Lambda that keeps the last five images works, but it is code to own: pagination, multi-arch manifest lists, image indexes, permissions, retries and failure alerting. The native policy does the same job declaratively and is applied the same way to every repository through a shared Terraform module. Reach for custom code only for logic the policy cannot express.

### Related cost and hygiene levers

- **Pull-through cache** repositories for Docker Hub, Quay or GitHub Container Registry, with their own lifecycle policies, so you are not storing full mirrors forever.
- **Replication** rules multiply storage: replicate only the repositories and prefixes another region actually needs.
- **Scanning**: with enhanced scanning (Amazon Inspector) you are billed per image scanned, so fewer stale images also means a smaller scanning bill and fewer irrelevant findings.
- Non-registry waste usually travels with this question - idle EC2 and non-production RDS at night. That is a scheduling problem (EventBridge Scheduler or Instance Scheduler on AWS), not a registry problem.

## Example

```json
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Untagged images: gone 7 days after push",
      "selection": {
        "tagStatus": "untagged",
        "countType": "sinceImagePushed",
        "countUnit": "days",
        "countNumber": 7
      },
      "action": { "type": "expire" }
    },
    {
      "rulePriority": 2,
      "description": "CI and PR builds: keep the newest 30",
      "selection": {
        "tagStatus": "tagged",
        "tagPrefixList": ["build-"],
        "countType": "imageCountMoreThan",
        "countNumber": 30
      },
      "action": { "type": "expire" }
    },
    {
      "rulePriority": 3,
      "description": "Releases: keep 180 days for rollback",
      "selection": {
        "tagStatus": "tagged",
        "tagPatternList": ["v*"],
        "countType": "sinceImagePushed",
        "countUnit": "days",
        "countNumber": 180
      },
      "action": { "type": "expire" }
    }
  ]
}
```

```bash
REPO=payments-api

# Dry run: which images would this policy expire?
aws ecr start-lifecycle-policy-preview --repository-name "$REPO" \
  --lifecycle-policy-text file://lifecycle.json
aws ecr get-lifecycle-policy-preview --repository-name "$REPO" \
  --query 'previewResults[].[imageTags[0],imagePushedAt,appliedRulePriority]' --output table

# Enforce it, and stop tags from being overwritten
aws ecr put-lifecycle-policy --repository-name "$REPO" --lifecycle-policy-text file://lifecycle.json
aws ecr put-image-tag-mutability --repository-name "$REPO" --image-tag-mutability IMMUTABLE
```

```hcl
# Applied to every repository by one module, so new repos are never unmanaged
resource "aws_ecr_repository" "this" {
  for_each             = toset(var.repositories)
  name                 = each.key
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration { scan_on_push = true }
}

resource "aws_ecr_lifecycle_policy" "this" {
  for_each   = aws_ecr_repository.this
  repository = each.value.name
  policy     = file("${path.module}/lifecycle.json")
}
```

## Interview tips

- Lead with "a lifecycle policy per repository, in Terraform". A scheduled Lambda that keeps the latest few images is a common answer and it works, but it rebuilds a free native feature and gives you code to maintain - say why you would not do it.
- Know the rule anatomy: `rulePriority`, `tagStatus`, prefix or pattern lists, and `imageCountMoreThan` versus `sinceImagePushed`. Mention that a `tagStatus: any` rule must come last.
- Raise the trap yourself: the policy does not know what is deployed, so expiring a running image causes `ImagePullBackOff` the next time a Pod reschedules. Long retention for release tags and short retention for build tags is the answer.
- Mention the preview API as the safe rollout step, and tag immutability as the control that stops mutable tags from creating untagged orphans.
- Expect follow-ups on cross-region replication and pull-through caches, both of which add storage you also need to govern. See [what is the difference between ECS, EKS, and Fargate](./what-is-the-difference-between-ecs-eks-and-fargate.md) and [zombie cloud resources](../cloud-cost-optimization/what-are-zombie-cloud-resources-and-how-do-you-identify-and-automate-their-cleanup.md).

**Telling it as a STAR story** (an adaptable example)

- **Situation:** Registry storage had grown to several terabytes because every CI build pushed an image and nothing was ever deleted; a homegrown cleanup Lambda kept failing on multi-arch images.
- **Task:** Bring registry cost under control without deleting anything a deployment might need to roll back to.
- **Action:** Replaced the Lambda with ECR lifecycle policies applied to every repository by a shared Terraform module: untagged images expired after 7 days, the newest 30 `build-` images kept, and `v*` release images kept for 180 days to cover the GitOps rollback window. Ran the lifecycle policy preview on the largest repositories first, and enabled tag immutability and scan-on-push.
- **Result:** Registry storage fell sharply within a week, the Lambda and its alerts were retired, and new repositories were covered automatically from the day they were created.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?]] (`#407`): [How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-waiting-for-a-persistentvolumeclaim.md)
- [[How do requests, limits, and QoS classes work in Kubernetes?]] (`#444`): [How do requests, limits, and QoS classes work in Kubernetes?](../kubernetes/how-do-requests-limits-and-qos-classes-work-in-kubernetes.md)
- [[How do you choose a cloud provider for a new workload?]] (`#281`): [How do you choose a cloud provider for a new workload?](../cloud-platforms/how-do-you-choose-a-cloud-provider-for-a-new-workload.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
