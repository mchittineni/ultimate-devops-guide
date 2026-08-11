---
title: "What DevOps interview questions does Aspire ask?"
id: 316
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - aspire
  - kubernetes
  - aws-engineering
  - infrastructure-as-code
  - version-control
  - serverless-architecture
  - scalability-and-high-availability
---

# What DevOps interview questions does Aspire ask?

## Questions

**Kubernetes**

- **What is the difference between a ReplicaSet and a DaemonSet?**
- **What is the difference between a PersistentVolume and a PersistentVolumeClaim?**
- **How do you find orphaned resources in a Kubernetes cluster and remove them safely?**

**Git**

- **What is the difference between `git pull` and `git fetch`?**
- **What do `git stash` and `git stash pop` do, and when would you use them?**

**AWS**

- **What is the difference between a network ACL and a security group?**
- **What is cross-region replication in S3, and what do you need in place for it to work?**
- **What are the different event sources that can trigger an AWS Lambda function?**
- **What is a NAT gateway and what is a NAT instance, and when would you choose one over the other?**
- **What are sticky sessions on an Application Load Balancer, and how are they implemented?**

**Terraform**

- **What does `terraform fmt` do?**
- **What is `terraform import` for?**
- **What is the difference between a provider and a provisioner in Terraform?**

**Troubleshooting**

- **In which situations does a 503 error occur, and how do you diagnose one?**

## Example

```text
Aspire — DevOps Engineer (3.4 YOE), reported round
14 questions

  AWS                         5   NACL vs SG, S3 CRR, Lambda triggers,
                                  NAT gateway vs instance, ALB sticky sessions
  Terraform                   3   fmt, import, provider vs provisioner
  Kubernetes                  3   ReplicaSet vs DaemonSet, PV vs PVC,
                                  orphaned resources
  Git                         2   pull vs fetch, stash and pop
  Troubleshooting             1   when you get a 503

FORMAT WARNING
  9 of 14 are "difference between" or "use of" questions. Answers must be
  two crisp sentences plus one differentiator each. Rambling on a definition
  question reads worse than a short precise answer.
```

## Interview tips

- On a comparison round, give the distinction _and_ the consequence. "A ReplicaSet keeps N replicas anywhere the scheduler fits them; a DaemonSet runs exactly one Pod per matching node, which is why log collectors and node exporters are DaemonSets" is a complete answer. See [DaemonSets](../container-orchestration-advanced/what-are-daemonsets-in-kubernetes.md).
- PV versus PVC is cleanest framed as supply and demand: the PV is the provisioned piece of storage, the PVC is the workload's request for storage, and the StorageClass is what binds them by dynamically provisioning a PV to satisfy the claim. Mention `ReclaimPolicy` to show depth.
- `git fetch` updates your remote-tracking branches and changes nothing in your working tree; `git pull` is `fetch` followed by `merge` or `rebase`. Add that `pull --rebase` avoids the merge commits that make history unreadable. See [git merge, rebase, and cherry-pick](../version-control/what-is-the-difference-between-git-merge-rebase-and-cherry-pick.md).
- NACL versus security group has four contrasts and you should name at least three: NACLs are stateless and evaluate numbered rules in order with explicit allow and deny, and attach to subnets; security groups are stateful, allow-only, evaluated as a set, and attach to network interfaces. See [network segmentation](../network-security/what-is-network-segmentation.md) and [defence in depth for a cloud network](../network-security/how-do-you-design-defence-in-depth-for-a-cloud-network.md).
- The 503 question is the one where you can genuinely stand out. Separate the causes: no healthy targets behind the load balancer, the target group is empty or failing health checks, the application is refusing connections or thread-pool exhausted, or a proxy is rate-limiting or in maintenance mode. Then contrast with 502 (bad upstream response) and 504 (upstream timeout), because that contrast is the natural follow-up. See [what happens when a user opens your application in a browser](../network-security/what-happens-when-a-user-opens-your-application-in-a-browser.md).
- Provider versus provisioner is a favourite because the words look similar. A provider is the plugin that talks to a platform's API and supplies resource types; a provisioner runs scripts on a resource after creation, and HashiCorp explicitly documents it as a last resort because it breaks the declarative model. Saying "last resort" is what marks you as having read the docs. See [Terraform providers](../infrastructure-as-code/what-are-terraform-providers.md).
- `terraform fmt` only rewrites configuration files to canonical style — it changes no infrastructure. State that clearly, because the question exists to check you do not confuse it with `validate` or `plan`.
- Orphaned resources is the most open question in the set. Name the categories — Released PVs and unbound PVCs, Secrets and ConfigMaps no longer mounted, Services with no Endpoints, completed Jobs and their Pods, orphaned cloud load balancers left behind by deleted Services — then say how you find them (label and owner-reference queries, `kubectl get ... --show-labels`, an orphan report in CI) and how you delete safely: check `ownerReferences`, dry-run first, and stage the deletion. Mention that cloud load balancers left behind by deleted Services are the ones that cost real money.
- Sticky sessions on an ALB are implemented with a cookie — either the load balancer's own `AWSALB` cookie or an application-defined one — and the follow-up is always "what breaks when the target dies", so volunteer that the session is lost unless state is externalised to something like Redis. See [load balancing](../scalability-and-high-availability/what-is-load-balancing.md).
- S3 cross-region replication needs versioning enabled on both buckets, a replication role, and a rule; add that it replicates new objects only unless you run batch replication, which is the usual follow-up. See [S3 storage classes](../aws-engineering/what-are-the-s3-storage-classes-and-when-do-you-use-each.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?]] (`#455`): [How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?](../cicd/how-do-you-trigger-a-pipeline-webhooks-polling-schedules-and-upstream-jobs.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
