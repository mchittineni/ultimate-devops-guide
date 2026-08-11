---
title: "What DevOps consultant interview questions does Amazon ask?"
id: 314
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - amazon
  - aws-engineering
  - kubernetes
  - infrastructure-as-code
  - cicd
  - monitoring-and-logging
  - network-security
  - scripting-and-automation
  - cloud-migration
  - scalability-and-high-availability
---

# What DevOps consultant interview questions does Amazon ask?

## Questions

### Round 1 — DevOps Consultant (9 YOE)

**Logging and automation**

- **What are the steps to ship log files from an EC2 instance into S3?**
- **Build the automated version: collect the log file, evaluate CPU metrics, and raise a CloudWatch alarm that notifies users.**

**AWS services and networking**

- **You are an administrator but still cannot access a particular S3 bucket. What explains that?** The interviewer's own answer was an IAM permission boundary.
- **A bucket exists in one region. Can you access it from a different region, and what changes if you can?**
- **Can a NAT gateway be created in a private subnet? Explain why or why not.**
- **Describe a three-tier architecture.**

**Kubernetes**

- **How do you limit resource usage in Kubernetes without touching the Deployment manifest?** The interviewer was steering toward namespace-level controls.
- **How do you upgrade or replace worker nodes in a running cluster without dropping traffic?**
- **What is the purpose of the CNI in Kubernetes?**
- **How do you configure cluster autoscaling, step by step?**

**CI/CD and Terraform**

- **Walk through the stages of a CI/CD pipeline.**
- **How do you build the container image during CI, and how do you manage it afterwards — tagging, storage, promotion?**
- **Write Terraform that creates a VPC, a subnet, an EC2 instance, and an S3 bucket.**

### Round 2 — DevOps Consultant (7 YOE)

**Monolith migration**

- **You are migrating a monolithic application from on-premises to AWS and it depends on a local filesystem. Which AWS storage service do you use as the replacement?**
- **Where do you store all of that monolith's configuration once it is in the cloud?**
- **When migrating the database, how do you keep source and target in sync during cutover?**

**Observability**

- **What observability capabilities does an application need?** The interviewer's own list was monitoring, alerting, logging, remediation, and paging.
- **If you are not permitted to install Filebeat on the worker nodes, how else do you collect logs?**

**State, sessions, and databases**

- **If a database Pod dies, is the stored data affected?**
- **What happens to sticky-session data when the Pod holding it goes away?** The expected answer is that the session data is lost.
- **Which service would you use instead, so sessions survive a Pod restart?** The interviewer was looking for Redis.
- **When sticky sessions misbehave, what is the load balancer's role in causing it?**

**Architecture, scale, and security**

- **What security controls do you build into a three-tier architecture by design?**
- **Do you run clusters across multiple regions? Is it possible, and how do you manage them if so?**
- **You onboarded a trading application onto AWS. How did you guarantee its availability, scalability, and security?**
- **How do you take a regular backup of an entire Kubernetes cluster?**
- **You must create 20 EC2 instances in each of 10 accounts — 200 machines. How do you give them all connectivity, and which service provides it?**
- **You need to reach a database in a private subnet without a NAT gateway, a NAT instance, or a bastion host. What options remain?**

**Terraform and scripting**

- **What is the difference between a `local` and a `variable` in Terraform?**
- **You created resources with Terraform. How do you ensure nobody modifies them through the console, and how do you automate that check?**
- **Write a Python script that lists the running EC2 instances tagged `PROD`.**

**Linux and networking fundamentals**

- **Explain the OSI model.**
- **What is the difference between a directory and a mount point?**

## Example

```text
Amazon — DevOps Consultant, two reported rounds

  ROUND 1 (9 YOE)                          13 questions
    Logging / automation              2    EC2->S3, CPU metric + alarm
    AWS services and networking       4    permission boundary, cross-region S3,
                                           NAT placement, three-tier
    Kubernetes                        4    namespace limits, node upgrades,
                                           CNI, cluster autoscaler
    CI/CD and Terraform               3    pipeline stages, image build/manage,
                                           VPC+subnet+EC2+S3

  ROUND 2 (7 YOE)                          20 questions
    Monolith migration                3    filesystem, config store, DB sync
    Observability                     2    what's needed, no-Filebeat logging
    State / sessions / DB             4    DB Pod death, sticky sessions, Redis, LB
    Architecture / scale / security    6    three-tier security, multi-region,
                                           trading app, cluster backup,
                                           200 EC2 across 10 accounts, private DB
    Terraform and scripting           3    local vs variable, drift detection,
                                           boto3 PROD filter
    Fundamentals                      2    OSI model, directory vs mount

CONSISTENT ACROSS BOTH
  Every question ends in "which service, and why that one". Naming a service
  is half an answer; the trade-off against the runner-up is the other half.
```

## Interview tips

- The EC2-to-S3 automation is the signature question and it has a full walkthrough in this guide, including the IAM boundary and CloudWatch alarm parts: [automating EC2 log shipping to S3 with IAM boundaries and CloudWatch](../aws-engineering/how-do-you-automate-ec2-log-shipping-to-s3-with-iam-boundaries-and-cloudwatch.md).
- The admin-who-cannot-read-a-bucket question is testing IAM evaluation order. Walk it: an explicit `Deny` anywhere wins, then service control policies, then permission boundaries capping the identity's maximum permissions, then the bucket policy, then the identity policy — plus KMS key policy if the objects are encrypted. See [how AWS IAM evaluates a request](../aws-engineering/how-does-aws-iam-evaluate-a-request.md).
- A NAT gateway in a private subnet is technically creatable and functionally useless — it needs a route to an internet gateway, which only a public subnet has. Say "you can create it, it will not work, and here is why", because the question is worded to catch a flat yes or no.
- Namespace-level resource limits means `ResourceQuota` and `LimitRange`, not editing the Deployment. `LimitRange` supplies defaults so Pods without explicit requests still get some, and `ResourceQuota` caps the namespace total. See [autoscaling workloads and nodes](../kubernetes/how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md).
- Worker-node upgrades should be described as a sequence: `kubectl cordon`, then `drain` respecting PodDisruptionBudgets, then replace the node, then `uncordon` — or, on managed node groups, a rolling surge upgrade. Mentioning PDBs is what signals production experience.
- Sticky sessions form a four-question chain, so answer it as one story: sessions held in Pod memory die with the Pod, the load balancer keeps routing to an instance that no longer has the session, and the fix is externalising session state to Redis so any replica can serve any request. Say "stateless application, state in a datastore" as the principle. See [designing a system to degrade gracefully](../scalability-and-high-availability/how-do-you-design-a-system-to-degrade-gracefully-under-overload.md).
- For the local-filesystem monolith, EFS is the expected answer — shared, POSIX, multi-AZ — with FSx if it needs Windows or Lustre semantics, and EBS only if a single instance is truly enough. Then say configuration belongs in Parameter Store or Secrets Manager, not baked into an AMI. See [core AWS services](../aws-engineering/what-are-the-core-aws-services-a-devops-engineer-uses-daily.md).
- No-Filebeat logging has several valid answers, and naming more than one is the win: a DaemonSet-based collector such as Fluent Bit, the container runtime's log driver shipping directly, a sidecar in the Pod, or CloudWatch Container Insights. If the constraint is "nothing on the node", the sidecar and the runtime driver are the honest answers. See [designing a logging pipeline that stays affordable at scale](../monitoring-and-logging/how-do-you-design-a-logging-pipeline-that-stays-affordable-at-scale.md).
- The 200-instances-across-10-accounts question wants AWS Transit Gateway, shared across accounts with Resource Access Manager, rather than a mesh of VPC peerings. Say why: peering does not transit, so 10 accounts would need dozens of connections. See [structuring a multi-account AWS organisation](../aws-engineering/how-do-you-structure-a-multi-account-aws-organisation.md).
- Reaching a private database with no NAT, no NAT instance, and no bastion leaves Systems Manager Session Manager, VPC endpoints for the control plane, EC2 Instance Connect Endpoint, a VPN or Direct Connect, or a private link from a peered network. Session Manager is the answer they want first. See [connecting an on-premises network to the cloud](../cloud-engineering/how-do-you-connect-an-on-premises-network-to-the-cloud.md).
- Drift detection is the closing question and it has a specific expected shape: run `terraform plan` on a schedule in CI and fail the job on a non-empty diff, deny console write access through SCPs so the situation cannot arise, and alert on `ConfigurationItemChange` events from AWS Config or CloudTrail. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- `local` versus `variable`: variables are inputs supplied from outside the module, locals are computed values named inside it and cannot be overridden. One sentence each is enough.
- For the boto3 script, use a filtered `describe_instances` call with both `instance-state-name` set to `running` and `tag:Environment` set to `PROD` so the filtering happens server-side, and paginate. Filtering in Python after fetching everything is the answer that loses marks. See [what you use Python for as a DevOps engineer](../scripting-and-automation/what-do-you-use-python-for-as-a-devops-engineer.md).
- Cluster backup means etcd snapshots for self-managed control planes and a tool such as Velero for namespaced resources plus persistent volumes. Say which one covers what, since they are not interchangeable. See [what disaster recovery is](../scalability-and-high-availability/what-is-disaster-recovery.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you use Jenkins shared libraries?]] (`#268`): [How do you use Jenkins shared libraries?](../cicd/how-do-you-use-jenkins-shared-libraries.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you scale CI/CD across many services and teams?]] (`#459`): [How do you scale CI/CD across many services and teams?](../cicd/how-do-you-scale-ci-cd-across-many-services-and-teams.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
