---
title: "What DevOps interview questions does Alphadyne ask?"
id: 311
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - alphadyne
  - aws-engineering
  - azure-engineering
  - cicd
  - kubernetes
  - configuration-management
  - infrastructure-as-code
  - version-control
  - linux-administration
---

# What DevOps interview questions does Alphadyne ask?

## Questions

### Round 1 — technical discussion (5 YOE)

**AWS architecture and migration**

- **An application currently runs on a public EC2 instance. How do you move it into a private subnet while following AWS best practices for security, networking, and high availability?**
- **Once the application is in a private subnet, how do you give users HTTPS access to it?**
- **Follow-on discussion: when do you choose an ALB over an NLB, how are ACM certificates attached and terminated, how does routing reach private targets, and how are the security groups chained?**

**Experience and incidents**

- **Which infrastructure changes have you led? Go deep on the architecture you changed, the optimisations you made, and the problems you actually hit.**
- **Describe the one production Kubernetes incident you still remember — and take me through root cause analysis, your troubleshooting path, the fix, and the preventive measures you put in place.**

**Git and delivery**

- **Explain your branching strategy in depth, and justify why that strategy was chosen over the alternatives.**
- **How does your branching model support multiple environments, scheduled releases, and emergency hotfixes at the same time?**
- **A developer hands you nothing but application source code. As the DevOps engineer, how do you design the CI/CD pipeline and promote builds through DEV, QA, and PROD using best practices?**
- **How do you configure a Jenkins multibranch pipeline, what problem does it solve, and why is it preferred over an ordinary SCM-triggered pipeline?**

### Round 2 — written assessment

**Multiple choice**

- **Which tool should a company use to automate deployment and configuration management across both virtual machines and containers?**
- **Which Ansible module installs the nginx web server when provisioning a new server?**
- **Which Ansible module do you use to guarantee a specific package is present on a newly configured web server?**
- **Which Kubernetes object do you use to guarantee a Pod always receives a specific amount of CPU and memory?**
- **Which command is the best choice for monitoring disk reads and writes?**
- **You have a developer's public key and need to grant them access to a server. Where on the server does that public key belong?**
- **On a modern Linux system, in which file are user password hashes stored?**

**Terraform on Azure — hands-on build**

- **Write Terraform that provisions an Azure Virtual Network with a given address range.**
- **Create separate subnets for the bastion, application, and database tiers.**
- **Create network interfaces and attach each to the correct subnet.**
- **Provision virtual machines on those NICs using username and password authentication.**
- **Create public IP addresses only where they are actually required.**
- **Set up an Azure Bastion host for secure administrative access to the VMs.**
- **Configure an Azure Load Balancer that distributes traffic to the application-tier VMs.**

## Example

```text
Alphadyne — DevOps Engineer, two reported stages

  ROUND 1 (5 YOE, discussion)              9 questions
    AWS architecture / migration      3    public->private EC2, HTTPS,
                                           ALB vs NLB + ACM + SGs
    Experience and incidents          2    infra changes, K8s production issue
    Git and delivery                  4    branching depth, environments,
                                           greenfield CI/CD, Jenkins multibranch

  ROUND 2 (written assessment)             14 items
    Multiple choice                   7    Ansible modules, K8s resources,
                                           iostat, authorized_keys, /etc/shadow
    Terraform on Azure (build)        7    VNet, tiered subnets, NICs, VMs,
                                           public IPs, Bastion, Load Balancer

NOTE THE CLOUD SWITCH
  The discussion round is AWS. The written task is Azure. Prepare the
  networking primitives in both, because the concepts transfer and the
  resource names do not.
```

## Interview tips

- The public-to-private EC2 migration is the anchor question. Answer it as a sequence, not a list: move the instance to private subnets across at least two availability zones, put an internet-facing load balancer in the public subnets, terminate TLS there with an ACM certificate, allow only the load balancer's security group into the instance security group, and add NAT for egress patching. That single narrative also answers the HTTPS question and most of the ALB/NLB discussion. See [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md).
- ALB versus NLB should come with a reason, not a table: ALB for HTTP routing, header inspection, and path rules; NLB for raw TCP, extreme throughput, static IPs, or TLS passthrough. See [layer 4 versus layer 7 load balancers](../scalability-and-high-availability/what-is-the-difference-between-a-layer-4-and-a-layer-7-load-balancer.md).
- Branching strategy is asked in depth and then attacked from the environments and hotfix angle. Pick one model, name it, and describe how a hotfix reaches production without dragging unreleased work with it. Do not describe a model you have not used. See [Git branching strategy](../version-control/what-is-git-branching-strategy.md) and [trunk-based development](../version-control/what-is-trunk-based-development.md).
- For the greenfield pipeline, cover stages in order — build, unit test, static analysis and image scan, artefact or image push with an immutable tag, deploy to DEV automatically, QA behind an approval, PROD behind a change gate — and say how promotion reuses the same artefact rather than rebuilding it. See [what a CI/CD pipeline is](../cicd/what-is-ci-cd-pipeline.md) and [deployment strategies](../devops-tools-and-automation/what-are-deployment-strategies.md).
- Multibranch pipelines exist so every branch and pull request gets a pipeline automatically from the `Jenkinsfile` in that branch, with jobs created and destroyed as branches come and go. That last clause is the answer to "why is it preferred". See [Jenkins pipelines](../cicd/what-are-jenkins-pipelines.md).
- The assessment answers worth memorising: Ansible's `apt`/`yum`/`dnf` or the generic `package` module for installing nginx and ensuring packages, with `state: present` as the idempotent form; `resources.requests` and `resources.limits` on the Pod spec, plus `ResourceQuota` and `LimitRange` at namespace level; `iostat` (or `iotop`) for disk reads and writes; `~/.ssh/authorized_keys` for the developer's public key; and `/etc/shadow` for password hashes. See [what Ansible is](../infrastructure-as-code/what-is-ansible.md).
- The Azure Terraform build is graded on structure as much as correctness: one resource group, a VNet with non-overlapping subnet CIDRs, NSGs that keep the database tier unreachable from the internet, and public IPs only on the load balancer and Bastion — never on the application VMs. Note in passing that username-and-password VM authentication was requested but SSH keys are the production choice. See [what Terraform is](../infrastructure-as-code/what-is-terraform.md) and [network segmentation](../network-security/what-is-network-segmentation.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?]] (`#402`): [How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?](../cicd/how-do-you-troubleshoot-a-jenkins-pipeline-that-never-starts-or-hangs-in-the-queue.md)
- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)
- [[How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?]] (`#455`): [How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?](../cicd/how-do-you-trigger-a-pipeline-webhooks-polling-schedules-and-upstream-jobs.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
