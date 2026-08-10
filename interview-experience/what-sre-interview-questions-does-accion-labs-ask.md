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

- Master-node-down and worker-node-down are a paired question; answer them as a contrast. Control plane down means no scheduling, no API, no self-healing, but existing Pods keep serving traffic. Worker down means the node controller marks it `NotReady`, tolerations expire, and Pods are rescheduled elsewhere. See [Kubernetes architecture](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md).
- Node recovery time is a numbers question. Name the knobs: `node-monitor-grace-period`, the eviction timeout, and image pull time on the replacement node. A candidate who says "about five minutes by default, and here is what makes it that" beats one who says "it depends".
- SLI/SLO/SLA at this level must include the error budget and what you do when it is exhausted. See [SLA vs SLO vs SLI vs OLA](../sla-management/what-is-the-difference-between-an-sla-an-slo-an-sli-and-an-ola.md) and [error budgets](../site-reliability-engineering/what-is-error-budget.md).
- Observability versus monitoring is graded on whether you mention unknown-unknowns and high-cardinality data rather than reciting "three pillars". See [monitoring versus logging](../monitoring-and-logging/explain-the-difference-between-monitoring-and-logging.md).
- Have one major incident rehearsed with a timeline, a wrong hypothesis you discarded, the actual fix, and the preventive action. Two separate questions here want that same story, so it must be strong. See [running a major incident](../incident-management/how-do-you-run-a-major-incident-as-incident-commander.md) and [post-mortems](../incident-management/what-is-post-mortem-analysis.md).
- The workspaces question has a preferred answer at senior level: workspaces suit identical infrastructure with different variables, but most teams prefer separate state files and directories per environment because workspaces hide which environment you are targeting. Say the trade-off. See [managing Terraform state safely](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- Ansible and Terraform in the same round usually leads to "why both?". Prepare the configuration-versus-provisioning distinction. See [Ansible versus Terraform](../infrastructure-as-code/what-is-the-difference-between-ansible-and-terraform.md).

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
