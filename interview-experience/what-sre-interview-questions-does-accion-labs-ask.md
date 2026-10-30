---
title: "What SRE interview questions does Accion Labs ask?"
id: 308
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - accion-labs
  - site-reliability-engineering
  - kubernetes
  - sla-management
  - infrastructure-as-code
  - configuration-management
  - incident-management
  - linux-administration
  - scripting-and-automation
---

# What SRE interview questions does Accion Labs ask?

## Questions

**Reliability and high availability**

- **How do you ensure high availability in a Kubernetes cluster — across the control plane, the nodes, and the workloads?**
- **Define SLI, SLO, and SLA, explain how they relate, and say why each matters to the business.**
- **How do you design a VPC for high availability?**
- **What is the difference between observability and monitoring?**

**Failure scenarios**

- **What is your response when a Kubernetes control-plane (master) node goes down — what breaks immediately, and what keeps running?**
- **What is your response when a worker node goes down, and how does the cluster recover the Pods that were on it?**
- **What is the maximum time a node takes to become Ready again after a failure or restart, and what determines that number?**
- **When an application in the cloud goes down, how do you isolate the root cause?**

**Incidents and performance**

- **Describe a recent major incident you handled end to end — impact, diagnosis, resolution, and follow-up.**
- **How have you resolved severe performance problems or critical incidents? Give a concrete case.**

**Delivery, IaC, and tooling**

- **What is the deployment setup in your current organisation — pipeline, environments, and release mechanism?**
- **Have you written Terraform for deployments? Walk me through what you implemented.**
- **Why do Terraform workspaces exist, and when is a workspace the right tool rather than a separate state or directory?**
- **Describe your hands-on Docker experience — what you built, not what Docker is.**
- **Have you used Ansible, and in what context? What did you automate with it?**
- **Do you script? Which language or tool, and what specifically did you implement with it?**

**Linux**

- **Which Linux command mounts a filesystem, and what would you check if the mount fails?**

## Example

```text
Accion Labs — SRE (17 YOE), reported round
17 questions

  Reliability / HA            4   K8s HA, SLI-SLO-SLA, VPC HA,
                                  observability vs monitoring
  Failure scenarios           4   master down, worker down, node
                                  recovery time, cloud RCA
  Incidents                   2   major incident, performance incident
  IaC and tooling             6   deployment setup, Terraform, workspaces,
                                  Docker, Ansible, scripting
  Linux                       1   mount

SENIORITY SIGNAL
  11 of 17 questions are "what did YOU implement / how did YOU respond".
  At 15+ YOE the round is a portfolio review with vocabulary checks
  attached — not a tools quiz.
```

## Interview tips

- Master-node-down and worker-node-down are a paired question; answer them as a contrast. Control plane down means no scheduling, no API, no self-healing, but existing Pods keep serving traffic. Worker down means the node controller marks it `NotReady`, applies the `node.kubernetes.io/not-ready` or `unreachable` taint, the Pods' default 300-second tolerations expire, and they are evicted and rescheduled elsewhere by their controllers. See [Kubernetes architecture](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md).
- Node recovery time is a numbers question. Name the knobs: `node-monitor-grace-period` before the node is marked `NotReady` (50 seconds by default since Kubernetes 1.32, 40 before), the default 300-second `tolerationSeconds` on the not-ready and unreachable taints before Pods are evicted (the old `--pod-eviction-timeout` flag is gone), then scheduling plus image pull time on the replacement node. A candidate who says "roughly five to six minutes by default, and here is what makes it that" beats one who says "it depends".
- SLI/SLO/SLA at this level must include the error budget and what you do when it is exhausted. See [SLA vs SLO vs SLI vs OLA](../sla-management/what-is-the-difference-between-an-sla-an-slo-an-sli-and-an-ola.md) and [error budgets](../site-reliability-engineering/what-is-error-budget.md).
- Observability versus monitoring is graded on whether you mention unknown-unknowns and high-cardinality data rather than reciting "three pillars". See [monitoring versus logging](../monitoring-and-logging/explain-the-difference-between-monitoring-and-logging.md).
- Have one major incident rehearsed with a timeline, a wrong hypothesis you discarded, the actual fix, and the preventive action. Two separate questions here want that same story, so it must be strong. See [running a major incident](../incident-management/how-do-you-run-a-major-incident-as-incident-commander.md) and [post-mortems](../incident-management/what-is-post-mortem-analysis.md).
- The workspaces question has a preferred answer at senior level: workspaces suit identical infrastructure with different variables, but most teams prefer separate state files and directories per environment because workspaces hide which environment you are targeting. Mechanically, CLI workspaces are just multiple state files in one backend (for S3, under an `env:/` prefix) sharing the same code, backend, and credentials — so they give no access isolation between dev and prod, which is the real reason to split. Note that HCP Terraform workspaces are a different, heavier concept with their own variables and permissions. Say the trade-off. See [managing Terraform state safely](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- The mount question: `mount /dev/sdb1 /mnt/data` (or `mount -a` to test `/etc/fstab`), with `findmnt` or `lsblk -f` to confirm. If it fails, check that the device and filesystem exist (`blkid`), that the filesystem type is supported or given with `-t`, that the mount point exists, `dmesg` for corruption or a dirty journal (`fsck` on an unmounted device), and for network mounts DNS, firewall, and the export's permissions. Mention `nofail` and UUIDs rather than device names in `/etc/fstab`, because a missing disk otherwise drops a server into emergency mode at boot.
- Ansible and Terraform in the same round usually leads to "why both?". Prepare the configuration-versus-provisioning distinction. See [Ansible versus Terraform](../infrastructure-as-code/what-is-the-difference-between-ansible-and-terraform.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between SLI, SLO, SLA, and Error Budgets in SRE practice?]] (`#641`): [What is the difference between SLI, SLO, SLA, and Error Budgets in SRE practice?](../site-reliability-engineering/what-is-the-difference-between-sli-slo-sla-and-error-budgets-in-sre-practice.md)
- [[How do On-Call rotations and escalation policies ensure rapid incident triage without engineer burnout?]] (`#647`): [How do On-Call rotations and escalation policies ensure rapid incident triage without engineer burnout?](../site-reliability-engineering/how-do-on-call-rotations-and-escalation-policies-ensure-rapid-incident-triage-without-engineer-burnout.md)
- [[What is a Blameless Post-Mortem and how do you write effective incident reviews that drive systemic changes?]] (`#645`): [What is a Blameless Post-Mortem and how do you write effective incident reviews that drive systemic changes?](../site-reliability-engineering/what-is-a-blameless-post-mortem-and-how-do-you-write-effective-incident-reviews-that-drive-systemic-changes.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
