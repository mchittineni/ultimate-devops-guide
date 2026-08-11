---
title: "What DevOps interview questions does Optum ask?"
id: 360
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - optum
  - infrastructure-as-code
  - aws-engineering
  - serverless-architecture
  - cloud-engineering
  - cloud-cost-optimization
---

# What DevOps interview questions does Optum ask?

## Questions

**Terraform**

- **What are Terraform lifecycle policies?**
- **Why do we use workspaces in Terraform?**
- **What is the Terraform `external` provider or command, and when should it be used?**
- **What are meta-arguments in Terraform?**
- **What are Terraform provisioners?**
- **How do you ensure a particular AMI is present in an AWS account using Terraform?**

**AWS and IAM**

- **How do you transfer payloads between Lambda functions in two different AWS accounts?**
- **How do you ensure least-privilege access for IAM users?**
- **What are S3 bucket lifecycle policies?**

## Example

```text
Optum — DevOps Engineer (5 YOE), reported round
9 questions

  Terraform                   6   lifecycle meta-argument, workspaces,
                                  external provider, meta-arguments,
                                  provisioners, guarantee an AMI exists
  AWS and IAM                 3   cross-account Lambda payloads,
                                  least privilege for IAM users,
                                  S3 lifecycle policies

TWO KINDS OF "LIFECYCLE" IN ONE ROUND
  Terraform's `lifecycle` block and S3's lifecycle *policies* are unrelated
  concepts asked five questions apart. Do not blur them — one controls how
  Terraform replaces resources, the other controls how S3 ages objects.
```

## Interview tips

- The `external` provider question is the most specialised here and the answer worth having exactly. `external` is a _data source_ that runs an arbitrary program on the machine executing Terraform, passes it JSON on stdin, and reads a flat JSON object of strings from stdout — it is the escape hatch for fetching something no provider exposes. Then give the caveats, because that is where the marks are: it runs on every plan so it must be fast and side-effect free, it must be idempotent, the program has to exist on every machine including CI runners, and it returns only strings. Say you would reach for a proper provider, a `data` source, or generating the value outside Terraform first, and use `external` as a genuine last resort. There is also an `external` _provisioner_-like pattern people confuse it with — clarifying that you mean the data source shows precision.
- Meta-arguments have a definite list and naming it completely is an easy win: `count`, `for_each`, `provider`, `depends_on`, `lifecycle`, and — for modules — `source` and `version`. Say they are arguments Terraform itself interprets rather than passing to the provider, which is why they work on every resource type regardless of provider.
- The `lifecycle` block should be covered argument by argument: `create_before_destroy` for zero-downtime replacement of a resource that cannot briefly disappear, `prevent_destroy` as a guard on databases and state buckets, `ignore_changes` for fields mutated outside Terraform such as auto-generated tags or an autoscaling desired count, and `replace_triggered_by` to force replacement when a referenced resource changes. Say that `prevent_destroy` fails the apply rather than silently skipping, and that `ignore_changes` is how you stop fighting drift you do not own. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- The "ensure a particular AMI is present" question is really about the difference between reading and owning. If the AMI already exists, use a `data "aws_ami"` block with `most_recent` and owner and name filters, which _asserts_ it exists — the plan fails if the lookup returns nothing, which is the guarantee they are asking about. If you need to _guarantee_ it exists in the account, you copy or share it: `aws_ami_copy` to bring it into the account and region, or build it with Packer or EC2 Image Builder as part of the pipeline. Say that pinning to a specific AMI ID is reproducible but goes stale, while `most_recent` is current but makes builds non-deterministic — and that the usual resolution is to pin a version and update it deliberately. See [what are Terraform providers](../infrastructure-as-code/what-are-terraform-providers.md).
- Cross-account Lambda payload transfer should be answered by naming the _pattern_, not just a service. Direct invocation: give the caller a role that can `lambda:InvokeFunction` on the target, and add a resource-based policy on the target function allowing the source account — the resource policy is the half people forget. Decoupled, which is the better answer: publish to an SNS topic or an EventBridge event bus with a cross-account resource policy, or an SQS queue the other account's function polls, or S3 with a cross-account bucket policy for large payloads. Then mention the constraint that decides it — the synchronous invocation payload limit is 6 MB, so anything larger goes through S3 with a pointer in the message. Naming that limit is what marks the answer as experienced. See [how AWS IAM evaluates a request](../aws-engineering/how-does-aws-iam-evaluate-a-request.md) and [structuring a multi-account AWS organisation](../aws-engineering/how-do-you-structure-a-multi-account-aws-organisation.md).
- Least privilege for IAM users deserves a process answer rather than a slogan. Start by not having IAM users at all — federate through Identity Center or an external IdP so humans get short-lived credentials and workloads use roles. Then: grant permissions to groups or roles rather than individuals, start from a deny-by-default position and add what is needed, use IAM Access Analyzer to generate policies from CloudTrail activity and to find unused permissions, apply permission boundaries so an administrator cannot escalate, scope with conditions on tags and source IP or VPC endpoint, enforce MFA, and review access keys and unused roles on a schedule. Say that generating policies from observed activity is how you get to least privilege in practice instead of guessing. See [least-privilege identity in the cloud](../cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md).
- S3 lifecycle policies should be answered with the transitions and the traps: rules matched by prefix or tag that transition objects between storage classes — Standard to Standard-IA to Glacier Instant, Flexible, or Deep Archive — and expire current or noncurrent versions, plus aborting incomplete multipart uploads, which is a commonly forgotten source of silent cost. Name the traps: minimum storage durations mean early deletion is charged, transition requests themselves cost money so tiering millions of tiny objects can cost more than it saves, and retrieval from Deep Archive takes hours. Add Intelligent-Tiering as the answer when the access pattern is unpredictable. See [S3 storage classes](../aws-engineering/what-are-the-s3-storage-classes-and-when-do-you-use-each.md) and [cloud cost optimisation](../cloud-cost-optimization/what-is-cloud-cost-optimization.md).
- On workspaces, give the honest recommendation rather than the textbook definition. Workspaces give you multiple state files from one configuration and suit infrastructure that is identical except for variable values — but most teams prefer separate directories with separate state per environment, because a workspace hides which environment you are targeting, makes it easy to apply to the wrong one, and cannot express genuine structural differences between dev and production. Say which you use and why.
- Provisioners should come with HashiCorp's own framing: `local-exec`, `remote-exec`, and `file` exist as a last resort because they break the declarative model — they are not tracked in state, have no meaningful retry semantics, and require network reachability from wherever Terraform runs. Say you prefer `user_data`, a baked image, or a configuration-management tool, and that reaching for a provisioner is usually a signal the design should change.
- Optum is a healthcare organisation, so wherever it fits naturally, add the compliance angle — encryption with customer-managed keys, audit trails, and data-retention rules driven by regulation rather than convenience. It costs one sentence and it lands.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
