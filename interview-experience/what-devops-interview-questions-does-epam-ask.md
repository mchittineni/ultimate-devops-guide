---
title: "What DevOps interview questions does EPAM ask?"
id: 327
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - epam
  - aws-engineering
  - kubernetes
  - infrastructure-as-code
  - cicd
  - devsecops
  - network-security
  - linux-administration
  - scripting-and-automation
---

# What DevOps interview questions does EPAM ask?

## Questions

### Round set 1 — Kubernetes, Terraform, AWS, Linux (9 YOE)

**Kubernetes**

- **How do you create and use custom resources — CRDs — in Kubernetes?**
- **What are namespaces in Kubernetes and what do they isolate?**
- **What is the difference between a Deployment and a StatefulSet?**
- **What is role-based access control?**
- **What is the difference between the cluster autoscaler and the horizontal Pod autoscaler?**

**Terraform**

- **What is a provider?**
- **How do you manage Terraform state?**
- **Do you keep state locally or remotely, and which configuration block do you use to store it remotely?**
- **What is a Terraform module?**
- **How do you manage multiple environments in Terraform?**

**AWS**

- **What are the use cases for CloudWatch?**
- **What are ECS and EKS, and how do they differ?**
- **What is Fargate?**
- **What are the limitations of Lambda?**
- **How does Lambda work with container images?**
- **What is an EC2 instance?**
- **What is Direct Connect?**
- **What is Storage Gateway?**
- **Explain VPC, NAT gateway, S3, Route 53, VPC peering, Transit Gateway, and auto-scaling groups.**
- **What is the difference between a security group and a network ACL?**

**Docker and Linux**

- **What is the difference between `COPY` and `ADD` in a Dockerfile?**
- **What is the difference between `CMD` and `ENTRYPOINT`?**
- **What do `RUN` and `docker exec` each do, and how do they differ?**
- **What lives under `/var` and `/opt` on a Linux filesystem?**
- **Write a script that takes `test.log` as an argument, searches it for the patterns `error` and `warning`, and writes the error matches to one file and the warning matches to another.**

### Round set 2 — AWS specialist round (7 YOE, AWS DevOps)

**Load balancing, networking, and IP addressing**

- **What is the difference between an ALB and an NLB?**
- **What is a VPC endpoint for, with a use case?**
- **What is Transit Gateway in AWS?**
- **Having connected several VPCs through a Transit Gateway, how do you block traffic from A to B and from B to C?**
- **An EC2 instance in a private subnet needs to receive inbound traffic. How do you enable that — without using a NAT gateway?**
- **How do you tighten security on your load balancer?**
- **Can you attach multiple load balancers to different sub-pages of one site?**
- **Can a single VPC carry two different CIDR blocks — a `172.` range and a `192.` range?**
- **What is the difference between a public and a private IP address?**
- **Given an address, how do you determine whether it is public or private? For example, is `90.0.0.9/0` public or private, and is `192.90.90.88/12` a private address or a host address?**

**Images, instances, and scaling**

- **What is the difference between an AMI and a snapshot?**
- **Can you derive AMI details from a snapshot?**
- **The development team changed the AMI in an auto-scaling group's launch template. How do you make sure the new version actually gets deployed?**
- **What is `user_data` on an EC2 instance used for?**
- **What are the different instance profile types?**
- **What are the different EC2 instance families?**
- **What is the difference between Spot and Reserved Instances?**
- **The auto-scaling group is under heavy load and has launched two instances, but provisioning takes two to three minutes and the ASG terminates them before they are ready. How do you prevent that?**
- **Traffic is consistently heavy between 5 PM and 8 PM every day. How do you configure the ASG for that?**
- **What is AWS Image Builder?**

**Containers**

- **What is the difference between Fargate and EKS worker nodes?**
- **How do you update an EKS cluster?**

**Monitoring and logs**

- **How do you check load balancer health through an AWS service?**
- **How do you separate the critical entries out of VPC Flow Logs?**
- **If all your VPC Flow Logs are going to an S3 bucket, how do you actually query them?**

**Edge and API**

- **How do you customise a WAF?**
- **How do you configure CloudFront?**
- **How do you configure API Gateway?**

### Round set 3 — architecture and DevSecOps round (6 YOE)

**Platform and CI/CD design**

- **How would you design a scalable, highly available CI/CD system serving microservices across multiple teams?**
- **What are the best practices for managing pipeline-as-code in large, distributed teams?**
- **How would you dynamically provision ephemeral dev and test environments from pipelines?**
- **In a monorepo, how do you ensure only the affected services are built and deployed?**
- **How do you implement GitOps in a Kubernetes environment?**
- **How would you build a fully automated blue-green deployment for Kubernetes microservices?**
- **How do you implement canary deployment with real-time monitoring and automatic rollback?**

**Kubernetes at scale**

- **Explain the Kubernetes control-plane components and how you would harden each for production.**
- **How would you scale a cluster horizontally across regions while still guaranteeing zero-downtime upgrades?**
- **What is a PodDisruptionBudget and how do you use one for critical workloads?**
- **How do you implement and manage network policies for strict inter-service communication?**
- **How do you manage secrets and configuration securely at scale in Kubernetes without breaking a GitOps workflow?**

**Terraform at scale**

- **How would you manage cross-region deployments with Terraform in a multi-cloud setup?**
- **How would you refactor a legacy Terraform codebase shared by several teams to follow DRY and modular practice?**
- **Explain the internals of how Terraform builds its dependency graph during planning.**
- **How do you isolate state files across multiple environments and teams?**
- **What is your strategy for preventing and recovering from a corrupted or deleted remote backend state file?**
- **Have you implemented policy-as-code with Sentinel or OPA alongside Terraform? Give a real use case.**

**Security, compliance, and DR**

- **How would you design an end-to-end DevSecOps pipeline for a fintech application under strict compliance requirements such as PCI-DSS?**
- **What is your strategy for container image security across every stage of the pipeline?**
- **How would you add runtime threat detection to Kubernetes using Falco or Sysdig?**
- **How do you enforce compliance and auditability in CI/CD across global regions — GDPR, HIPAA?**
- **How do you secure cloud-native DevOps infrastructure using identity federation, for example Entra ID with AWS IAM?**
- **How do you set up workload identity federation between GitHub Actions and Google Cloud or Azure securely?**

**Observability, cost, and resilience**

- **How would you implement centralised logging across multiple cloud platforms and environments?**
- **How do you keep autoscaling cost-efficient when CI/CD drives high workloads?**
- **Describe a case where you designed a disaster recovery strategy for DevOps infrastructure.**

## Example

```text
EPAM — DevOps Engineer, three reported interviews (~80 questions)

  SET 1  Fundamentals (9 YOE)          25   K8s CRDs/RBAC/autoscaling,
                                            Terraform state + modules, AWS
                                            service sweep, Docker directives,
                                            /var and /opt, log-splitting script
  SET 2  AWS specialist (7 YOE)        29   ALB vs NLB, TGW traffic blocking,
                                            IP classification, AMI vs snapshot,
                                            ASG warm-up + scheduled scaling,
                                            Flow Logs in S3, WAF/CloudFront/APIGW
  SET 3  Architecture + DevSecOps      27   HA CI/CD design, GitOps, monorepo
         (6 YOE)                             builds, PCI-DSS pipeline, Terraform
                                            graph internals, OPA, Falco,
                                            workload identity federation

EPAM SCALES THE ROUND TO THE LEVEL
  Set 1 is "what is X". Set 3 is "design X for multiple teams under
  compliance". Same company, completely different preparation.
```

```bash
# The log-splitting script from set 1. Argument-driven, case-insensitive,
# and it fails loudly rather than producing empty files silently.
#!/usr/bin/env bash
set -euo pipefail

logfile="${1:?usage: $0 <logfile>}"
[[ -r "$logfile" ]] || { echo "cannot read $logfile" >&2; exit 1; }

grep -i "error"   "$logfile" > errors.log   || true
grep -i "warning" "$logfile" > warnings.log || true

printf 'errors: %d, warnings: %d\n' \
  "$(wc -l < errors.log)" "$(wc -l < warnings.log)"
```

## Interview tips

- The private-subnet inbound question explicitly rules out a NAT gateway, and for good reason — NAT is egress-only. Inbound to a private instance comes from something public in front of it: an internet-facing load balancer with private targets, an API Gateway with a VPC link, or a reverse proxy in a public subnet. Say why NAT is the wrong tool before giving the right one. See [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md).
- Blocking A-to-B and B-to-C over a Transit Gateway is answered with multiple TGW route tables, not security groups. Associate each attachment with a route table that propagates only the routes it is allowed to reach — that is precisely why TGW has separate association and propagation. Mention that a single shared route table gives full mesh by default.
- The IP-classification questions are malformed by transcription, so state the rule rather than guessing at the addresses: RFC 1918 private ranges are `10.0.0.0/8`, `172.16.0.0/12`, and `192.168.0.0/16`. Note that `192.90.x.x` is _public_ despite starting with 192, because only `192.168.` is reserved — that is very likely the trap. Also note that a `/0` prefix means "all addresses", not a host.
- The ASG terminating instances during a two-to-three-minute boot is a health-check timing question. The answer is a health check grace period long enough to cover provisioning, plus a warm-up period for scaling metrics, plus lifecycle hooks if bootstrapping is genuinely slow — and the better fix is a pre-baked AMI so boot time drops. See [how auto-scaling groups and load balancers work together](../aws-engineering/how-do-auto-scaling-groups-and-load-balancers-work-together-on-aws.md).
- Predictable 5-to-8 PM traffic is a scheduled scaling action, not a target-tracking policy. Say you would set a scheduled minimum capacity ahead of the window and keep target tracking underneath as a safety net. Naming both is the complete answer. See [auto-scaling](../scalability-and-high-availability/what-is-auto-scaling.md).
- Two CIDR blocks in one VPC: yes — a VPC supports secondary CIDR blocks, which is the standard fix for subnet IP exhaustion, though the ranges must not overlap and some combinations are restricted. This pairs with the AMI-versus-snapshot answer: a snapshot is a point-in-time copy of one EBS volume, an AMI is the launchable template that references one or more snapshots plus metadata, and yes, you can build an AMI from a snapshot by registering it.
- Querying Flow Logs in S3 means Athena with a table over the log location and partitions by date — say Athena explicitly, since "download and grep" is the answer that fails. For the CloudWatch variant, name Logs Insights and a filter on `srcAddr`. See [designing a logging pipeline that stays affordable at scale](../monitoring-and-logging/how-do-you-design-a-logging-pipeline-that-stays-affordable-at-scale.md).
- `COPY` versus `ADD` has a preferred answer: use `COPY`, because `ADD` additionally auto-extracts local tar archives and can fetch remote URLs, which makes builds surprising. Interviewers want to hear that you default to `COPY`. See [what a Dockerfile is](../docker/what-is-dockerfile.md).
- Set 3's Terraform graph question is unusually deep. Say that Terraform builds a directed acyclic graph from explicit references and `depends_on`, walks it in dependency order, parallelises independent nodes up to `-parallelism`, and that `terraform graph` will render it. Mention that resources with no reference between them may be created in any order, which is why implicit dependencies matter.
- For secrets at scale without breaking GitOps, name the two viable patterns: encrypted-in-Git with Sealed Secrets or SOPS, or a reference-in-Git model with the External Secrets Operator or the Secrets Store CSI driver pulling from Vault or a cloud secret manager. Say the second is preferred because rotation does not require a commit. See [managing secrets in CI/CD pipelines](../devsecops/how-do-you-manage-secrets-in-ci-cd-pipelines.md) and [GitOps](../devops-tools-and-automation/what-is-gitops.md).
- Workload identity federation should be described without any stored key: GitHub Actions requests an OIDC token, the cloud provider trusts that issuer with a condition on repository and branch, and returns short-lived credentials. Emphasise the subject-claim condition, because a trust policy that omits it lets any repository assume the role. See [least-privilege identity in the cloud](../cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md).
- The monorepo question wants change detection: compute the changed paths against the merge base, map them to owning services with a dependency graph, and build only those, using tooling such as Bazel, Nx, or Turborepo. Mention that a shared library change must fan out to its dependents — that is the subtlety.
- For the PCI-DSS pipeline, structure the answer as controls rather than tools: separation of duties with mandatory review, signed commits, SAST and SCA gates, image scanning and signing, immutable artefacts with provenance, no production access from developer laptops, full audit trail of who deployed what, and segregated cardholder-data environments. See [what a DevSecOps pipeline looks like end to end](../devsecops/what-does-a-devsecops-pipeline-look-like-end-to-end.md) and [SLSA and securing the software supply chain](../devsecops/what-is-slsa-and-how-do-you-secure-the-software-supply-chain.md).
- PodDisruptionBudgets appear in both this round and several others in this collection. Define one crisply — `minAvailable` or `maxUnavailable` constraining _voluntary_ disruptions such as drains and upgrades, with no effect on a node crashing — and say that a badly set PDB can block a node drain indefinitely. See [autoscaling workloads and nodes](../kubernetes/how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md).

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
