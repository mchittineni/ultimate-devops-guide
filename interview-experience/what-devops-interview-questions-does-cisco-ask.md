---
title: "What DevOps interview questions does Cisco ask?"
id: 324
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - cisco
  - infrastructure-as-code
  - configuration-management
  - kubernetes
  - cicd
  - scripting-and-automation
  - api-gateway-and-service-mesh
  - monitoring-and-logging
---

# What DevOps interview questions does Cisco ask?

## Questions

### Round 1

**Reliability and monitoring**

- **Describe a situation where you had to improve the reliability of a critical system.**
- **What proactive monitoring have you implemented in your projects?**

**Ansible**

- **Write a playbook that deploys nginx and ensures the service is both started and enabled on boot. How do you manage secrets in Ansible?**

**Terraform**

- **How would you migrate a Terraform backend from local state to a remote backend such as S3 with DynamoDB locking?**
- **What happens if the Terraform state becomes corrupted, and how do you recover from it?**
- **Write Terraform that provisions an EC2 instance with a security group permitting only SSH.**

**Jenkins**

- **Explain how you would set up a multibranch Jenkins pipeline for a GitHub repository.**
- **How do you generate stages dynamically in a `Jenkinsfile` based on environment variables?**

**Kubernetes**

- **Explain the process for upgrading a Kubernetes cluster with zero downtime, and what you should verify once the upgrade is complete.**

**Scripting**

- **Write a script that watches a directory and automatically copies any new files to a remote server using `scp`.**

### Round 2

**Ansible and Terraform**

- **Write a playbook that installs Apache on a virtual machine.**
- **How do you move the state file from local to an S3 bucket, and what do you do if the state is lost?**
- **Write Terraform for the AWS services you would need, and the accompanying `Jenkinsfile`.**

**Kubernetes**

- **Walk through the upgrade steps for both EKS and an on-premises Kubernetes cluster.**
- **A Pod is restarting constantly. What steps do you follow?**

**Scripting**

- **Write a shell script that copies the directory `/nobackup` from a host called `ubuntu1` to another VM, given that automatic SSH is enabled and you authenticate with `ssh -i` and a private key.**

**APIs, security, and performance**

- **When a deployment hits a timeout, which API gateway were you using and how did that factor in?**
- **How did you handle security at the application level?**
- **How do you secure a public-facing API in an on-premises setup?**
- **Where and how do you check application performance metrics?**

## Example

```text
Cisco — DevOps Engineer (6+ YOE), two reported rounds

  ROUND 1                                  11 questions
    Reliability / monitoring          2    reliability story, proactive monitoring
    Ansible                           1    nginx playbook + secrets
    Terraform                         3    local->S3+DynamoDB, corrupted state,
                                           EC2 with SSH-only SG
    Jenkins                           2    multibranch setup, dynamic stages
    Kubernetes                        1    zero-downtime upgrade + verification
    Scripting                         1    watch dir, scp to remote

  ROUND 2                                  9 questions
    Ansible / Terraform               3    apache playbook, state to S3 + loss,
                                           TF + Jenkinsfile
    Kubernetes                        2    EKS + on-prem upgrades, restarting Pod
    Scripting                         1    copy /nobackup between VMs
    APIs / security / perf            4    gateway timeout, app-level security,
                                           public API on-prem, perf metrics

ASKED TWICE ACROSS ROUNDS
  Terraform state migration to S3, state loss, Ansible playbook authoring,
  cluster upgrades, and an SSH-copy script. If it repeats, it matters.
```

```hcl
# The SSH-only security group they ask you to write. Note the narrow CIDR —
# 0.0.0.0/0 on port 22 is the mistake the question is hunting for.
resource "aws_security_group" "ssh_only" {
  name   = "ssh-only"
  vpc_id = var.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.admin_cidr] # not 0.0.0.0/0
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

## Interview tips

- The backend migration has a precise answer, so give the sequence: create the S3 bucket with versioning and encryption plus a DynamoDB table with `LockID` as the partition key, add the `backend "s3"` block with `dynamodb_table`, run `terraform init -migrate-state`, confirm when prompted that you want to copy the existing state, then verify with `terraform plan` showing no changes and delete the local file. The confirmation prompt and the empty plan are the details that prove you have done it. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- Corrupted or lost state is asked in both rounds, so have the full recovery path: restore from S3 object versioning first, since that is why versioning is enabled; failing that, use a `.tfstate.backup`; failing that, rebuild by importing resources one at a time; and if you must, `terraform state push` a repaired file. Say what you would _not_ do — apply blindly against empty state, which recreates live infrastructure. See [recovering a lost or corrupted Terraform state file](../infrastructure-as-code/how-do-you-recover-a-lost-or-corrupted-terraform-state-file.md).
- On the SSH-only security group, restrict the source CIDR rather than using `0.0.0.0/0`, and volunteer that the better production answer is no inbound SSH at all — use Session Manager. Interviewers at Cisco tend to follow up on exactly that.
- For the nginx and Apache playbooks, keep them idempotent and complete: a `package` task, a `template` or `copy` task for configuration, and a `service` task with `state: started` and `enabled: yes`, plus a handler that restarts on configuration change. The question explicitly says "started and enabled on boot", so both keys must appear. For secrets, name Ansible Vault, `no_log: true` on sensitive tasks, and an external store such as Vault or Parameter Store for anything shared. See [what Ansible is](../infrastructure-as-code/what-is-ansible.md).
- Dynamic Jenkins stages are a Groovy question: build a map or list from the environment and generate stages in a loop, using `parallel` with a map of closures for concurrent work, or wrap stages in `when { environment ... }` for conditional execution. Mention that the declarative `stages` block is largely static, which is why you drop into a `script` block or use scripted syntax. See [Jenkins pipelines](../cicd/what-are-jenkins-pipelines.md).
- The zero-downtime upgrade answer has a fixed order and interviewers listen for it: upgrade the control plane first, one minor version at a time, then node groups; cordon and drain nodes respecting PodDisruptionBudgets; surge new nodes on the new version before removing old ones; and check add-on compatibility — CNI, CSI, CoreDNS, kube-proxy — plus deprecated API versions before you start. For post-upgrade verification, name specifics: all nodes `Ready` on the new version, no Pods pending or crash-looping, add-ons reconciled, `kubectl api-resources` clean, and your own smoke tests and SLO dashboards green. See [main components of Kubernetes architecture](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md).
- Distinguish the two upgrade contexts, because they asked for both: on EKS the control plane is a managed one-click version bump with node groups rolled separately, while on-premises you drive it yourself with `kubeadm upgrade plan`, `kubeadm upgrade apply` on the first control-plane node, then `kubeadm upgrade node` and a kubelet restart per node, and etcd backed up first.
- For the constantly restarting Pod, give an ordered method: `kubectl describe pod` for events and restart count, `logs --previous` for the crashed container, the exit code to separate `OOMKilled` (137) from an application error (1), then check whether a liveness probe is too aggressive and killing a healthy-but-slow container — a very common real cause. See [troubleshooting a Pod stuck in Pending or CrashLoopBackOff](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md) and [how probes differ](../kubernetes/how-do-liveness-readiness-and-startup-probes-differ.md).
- Both scripting questions are the same shape, so prepare one answer: `rsync -avz -e "ssh -i /path/key" /nobackup/ user@host:/dest/` is better than `scp` because it is incremental and resumable, wrapped in a loop or a `systemd` timer, with `set -euo pipefail` and a lock file to prevent overlapping runs. Say why `rsync` over `scp` — that reasoning is the differentiator. See [writing a production-grade Bash script](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md).
- The API gateway timeout question is really about layered timeouts. Say that a gateway has its own integration timeout, the load balancer has an idle timeout, and the application has a request timeout — and a deployment "timeout" is usually a readiness probe or health check failing while the gateway keeps sending traffic. Name the specific gateway you used. See [what a web application firewall is](../network-security/what-is-a-web-application-firewall-waf.md).
- Securing a public API on-premises should reach a reverse proxy or gateway terminating TLS, authentication with OAuth 2.0 or mTLS, rate limiting and quotas, a WAF in front, input validation, and network segmentation so the gateway is the only internet-reachable component. See [zero-trust security](../network-security/what-is-zero-trust-security.md) and [designing defence in depth for a cloud network](../network-security/how-do-you-design-defence-in-depth-for-a-cloud-network.md).
- "Proactive monitoring" is a phrase Cisco uses deliberately — it means catching degradation before users do. Answer with leading indicators: saturation trends, error-budget burn rate, synthetic checks, and capacity forecasting, rather than threshold alerts that fire after the outage. See [designing alerts that page a human](../site-reliability-engineering/how-do-you-design-alerts-that-page-a-human.md) and [capacity planning](../site-reliability-engineering/how-do-you-do-capacity-planning.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
