---
title: "What DevOps interview questions does HCL ask?"
id: 336
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - hcl
  - kubernetes
  - aws-engineering
  - version-control
  - cicd
  - container-orchestration-advanced
  - backup-and-disaster-recovery
  - docker
  - devsecops
---

# What DevOps interview questions does HCL ask?

## Questions

### Round set 1 — Git, Azure DevOps, and SonarQube (4-5 YOE)

- **What Git branching strategy does your organisation use?**
- **How is deployment to different environments driven from the Git repository?**
- **Where do you clone the repository from, and do you work through a local repository before pushing to the remote?** The candidate noted they did not follow this question.
- **What is a PAT — a personal access token?**
- **How do you handle a merge conflict in Git? If two people edit the same file, both commit, and a conflict results, in how many ways can it be resolved?**
- **How do you configure SonarQube?**
- **What does SonarQube output, and how do you fix code smells or vulnerabilities it reports?**
- **How do you integrate Azure Key Vault into Jenkins or an Azure pipeline?**
- **Where do you write the pipeline code or YAML file?**
- **What goes inside a Dockerfile?**
- **How do you schedule a pipeline? Say you have validated a pipeline with an update and want to schedule it against the stage or main branch — how?**

### Round set 2 — Kubernetes deep round

- **Explain the Kubernetes architecture.**
- **What is the difference between a PersistentVolume and a PersistentVolumeClaim?**
- **What is the difference between a Deployment and a StatefulSet?**
- **What is a StatefulSet?**
- **What is Calico?**
- **What is etcd?**
- **How do you back up a Kubernetes cluster?**
- **You have taken an etcd backup and the old VM is corrupted. Can you build a new VM and restore that etcd backup onto it?**
- **How do you upgrade an EKS cluster, and what are the steps?**
- **What is a rolling update?**
- **Which deployment strategy are you using?**
- **Can one container run in two Pods?**
- **In a StatefulSet with Pods named `mongo-0`, `mongo-1`, and `mongo-2`, what happens when `mongo-0` dies — what name does the replacement Pod get?**
- **If some Pods belong to a Deployment and some to a StatefulSet, how does the rolling update strategy behave differently for each?**
- **What is an ingress controller?**
- **What is a Docker multi-stage build, why is it used?**
- **Have you built VMs with Terraform?**
- **Have you worked with Argo CD and Helm?**
- **Have you worked with Grafana?**

### Round set 3 — AWS, IAM, and governance (5 YOE)

The candidate marked which questions they answered well and which they did not; the unanswered ones are worth extra preparation.

- **Explain landing zone, guardrails, service control policies, and Control Tower.**
- **Share an AMI from account 1 to account 2 when it is KMS-encrypted. Walk me through it.**
- **An EC2 instance has IAM roles attached. What can you discover from that?**
- **An EC2 instance and an S3 bucket are in the same region. How does the instance access the bucket?**
- **An EC2 instance has no internet connectivity. How do you deal with that?**
- **Two instances need to communicate. What is the best approach — create a new network interface, or attach something?**
- **With multiple IAM users, which is the better approach: attach the policy to each user individually, or add the users to a group and attach the policy to the group?**
- **Inline policy or managed policy attachment — which is the right approach?**
- **Have you used permission boundaries?**
- **What is the advantage of S3 lifecycle rules?**
- **Have you worked on Transit Gateway?**
- **Have you used ALB and NLB?**
- **There is a public and a private subnet with a NAT gateway. What is the NAT gateway actually doing, and by what mechanism does it protect the resources in the private subnet?**
- **Have you worked with KMS and Secrets Manager?**
- **Someone manually resized an EC2 instance from `t3.medium` to `t3.large`, updated the code and committed it, but the pipeline did not run. If you now run the pipeline, what happens?**
- **Can you reuse the same buildspec in AWS CodeBuild?**
- **What is a DaemonSet, and which DaemonSets ship with Kubernetes by default?**
- **What is an init container?**
- **What are taints and tolerations?**
- **How do you reserve compute in a manifest file?**

### Round set 4 — software-focused round (5 YOE)

- **How do you display the last 10 lines of a large log file without opening it fully?**
- **In Kubernetes, how would you configure a Deployment to double its CPU allocation once usage crosses 70%?**
- **Write a basic Dockerfile for your application.**
- **Which top-level OWASP security risks do you routinely check for?**
- **How do you configure Prometheus and Grafana for monitoring?**
- **You have an on-premises application. How would you migrate and deploy it in a cloud-native environment?**
- **Explain Docker Compose and how it helps with multi-container deployments.**

## Example

```text
HCL — DevOps Engineer, four reported interviews (~59 questions)

  SET 1  Git / Azure DevOps / Sonar   11   branching, PAT, merge conflicts,
                                           SonarQube config + output,
                                           Key Vault in pipeline, scheduling
  SET 2  Kubernetes deep round        19   etcd backup + restore to new VM,
                                           StatefulSet naming, PV vs PVC,
                                           mixed rolling updates, Calico,
                                           EKS upgrade steps
  SET 3  AWS / IAM / governance       20   cross-account KMS-encrypted AMI,
                                           group vs per-user policy, inline vs
                                           managed, NAT masking, permission
                                           boundaries, Control Tower
  SET 4  Software-focused              7   tail a big log, scale CPU at 70%,
                                           Dockerfile, OWASP, Prom+Grafana,
                                           on-prem to cloud-native, Compose

WHAT MAKES HCL DIFFERENT
  Round 3's candidate marked their own misses: landing zone vocabulary,
  cross-account encrypted AMI, no-internet EC2, inline vs managed policy,
  permission boundaries, Transit Gateway, taints. That is a ready-made
  revision list.
```

## Interview tips

- The StatefulSet naming question has one exact answer: the replacement Pod is called `mongo-0` again. Stable, ordinal identity is the entire point of a StatefulSet — the name, the DNS record, and the bound PersistentVolumeClaim all persist, so the new Pod re-attaches to the same volume and rejoins as the same member. Contrast it with a Deployment, where the replacement gets a fresh random suffix and any identity is lost. See [StatefulSets](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md).
- The mixed rolling-update question follows from that. A Deployment's rolling update is governed by `maxSurge` and `maxUnavailable` and replaces Pods in no particular order, potentially several at once. A StatefulSet updates strictly in reverse ordinal order — highest index first — one Pod at a time, waiting for each to become Ready before moving on, and `partition` in `updateStrategy` lets you stage a canary. Say that the StatefulSet is deliberately slower because ordered, one-at-a-time replacement is what protects a quorum.
- "Can one container run in two Pods?" is a definitional trap. No — a container instance belongs to exactly one Pod. The same _image_ can of course run in many Pods, which is almost certainly what they are probing. Correct the premise and give both halves.
- The etcd restore question is a yes with conditions, and the conditions are the answer: you can restore a snapshot onto a new machine with `etcdctl snapshot restore` into a fresh data directory, but you must stop the API server first, restore on every control-plane member, and reconcile the cluster's peer identity — and on EKS you cannot do this at all, because AWS owns etcd. Making the managed-versus-self-managed distinction is what separates a real answer from a memorised one. See [what disaster recovery is](../scalability-and-high-availability/what-is-disaster-recovery.md).
- Cluster backup should distinguish two layers: etcd snapshots capture the whole API state for a self-managed control plane, while Velero backs up namespaced resources plus persistent volume data and is the right tool on managed clusters. Say which you would use where.
- The cross-account encrypted AMI question is the hardest in set 3 and it is pure sequence. Share the AMI with the target account, and separately grant that account use of the customer-managed KMS key via the key policy — a default AWS-managed key cannot be shared, so the AMI must be encrypted with a CMK. Then, in the target account, the caller needs `kms:DescribeKey`, `kms:CreateGrant`, and `kms:ReEncrypt`, and typically copies the AMI to re-encrypt it with a local key. The line to land is "you cannot share an AMI encrypted with an AWS-managed key". See [how AWS IAM evaluates a request](../aws-engineering/how-does-aws-iam-evaluate-a-request.md).
- Group-versus-individual policy and inline-versus-managed have clear best-practice answers, so commit to them: attach to groups (or better, roles) because it scales and stays auditable; prefer managed policies because they are reusable and versioned, and reserve inline policies for a one-off relationship you want to guarantee cannot be attached elsewhere. Then mention permission boundaries as the mechanism that caps what an identity can ever be granted, which is the next question anyway. See [least-privilege identity in the cloud](../cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md).
- The NAT gateway "masking" question is asking for the concept by name: network address translation — specifically source NAT, where the private address is rewritten to the gateway's public address, and because the translation table only holds outbound-initiated flows, unsolicited inbound traffic has nowhere to go. That is _why_ it protects the subnet: it is a consequence of statefulness, not a firewall rule. Say that explicitly. See [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md).
- The manually-resized-instance question is a drift-plus-CI puzzle and the honest answer depends on what is in the repository. If the instance is Terraform-managed and the code still says `t3.medium`, the pipeline plans to change it _back_, which is the drift being tested. If the commit was never pushed, the pipeline builds the old code, because CI clones the remote and knows nothing about a developer's local machine. Say which assumption you are answering under. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- No-internet EC2 is answered with VPC endpoints for AWS services, Session Manager for access, and a NAT gateway only if general egress is genuinely required — plus an internal repository mirror if the instance needs packages. Say that "no internet" is often the desired state, not a fault.
- Two instances communicating is not a NIC question. In the same VPC they route to each other natively via private IPs subject to security groups; across VPCs you need peering, Transit Gateway, or PrivateLink. Adding a second network interface is for multi-homing or appliance patterns, not basic connectivity — say so, because the question offers a wrong answer on purpose.
- For the 70%-CPU-doubling question, name the HPA: `averageUtilization: 70` on a CPU resource metric, which requires `requests.cpu` to be set, plus `minReplicas` and `maxReplicas` — and note that HPA doubles _replicas_, not the CPU of one Pod. If they genuinely mean growing a single Pod's allocation, that is VPA or the newer in-place resize. Distinguishing the two is the point.
- SonarQube's output is a quality gate result plus issues classified as bugs, vulnerabilities, code smells, security hotspots, coverage, and duplication. Say that you fix by severity, that the gate should fail the build on new code rather than the whole legacy baseline, and that a "won't fix" needs a documented reason. See [SAST, DAST, IAST, and SCA](../devsecops/what-is-the-difference-between-sast-dast-iast-and-sca.md).
- Default DaemonSets on a typical cluster are `kube-proxy` and the CNI agent (`aws-node` on EKS, `calico-node` with Calico), plus a log or metrics agent if installed. CoreDNS is a _Deployment_, not a DaemonSet — that distinction is often the follow-up. See [DaemonSets](../container-orchestration-advanced/what-are-daemonsets-in-kubernetes.md).
- Merge conflict resolution "in how many ways" wants a list: edit the file by hand and mark it resolved, take one side wholesale with `--ours` or `--theirs`, use a merge tool, abort and rebase instead, or reset and redo the work. Add that prevention — small commits, short-lived branches, frequent integration — is the real answer. See [handling merge conflicts](../version-control/how-to-handle-merge-conflicts-in-git.md).
- `tail -n 10 file.log` for the last ten lines, and mention `tail -f` for following and `less +G` for navigating a huge file without loading it. See [analysing logs with grep, awk, and sed](../linux-administration/how-do-you-analyse-logs-and-text-files-with-grep-awk-and-sed.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)
- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
