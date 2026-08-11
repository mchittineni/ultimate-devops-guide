---
title: "What SRE interview questions does Altimetrik ask?"
id: 312
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - altimetrik
  - site-reliability-engineering
  - slo-engineering
  - monitoring-and-logging
  - infrastructure-as-code
  - kubernetes
  - container-orchestration-advanced
  - gcp-engineering
  - incident-management
---

# What SRE interview questions does Altimetrik ask?

## Questions

**Observability, SLOs, and alerting**

- **Which observability tools and frameworks are you using today, and what do your dashboards actually show?**
- **Do you build dashboards and alerts yourself, rather than consuming ones someone else made?**
- **Walk me through the specific dashboards you have built and the specific alerts you have configured.**
- **Are your dashboards and alerts built around the SRE golden signals, and do you use them day to day?**
- **Have you implemented SLO-based alerting in your project — and if so, how is it configured?**
- **Explain what an error budget is.**
- **What counts as an ideal or acceptable error-budget burn rate, and what do you do when you exceed it?**
- **What is your experience with alerting, logging, and incident or problem resolution?**

**Kubernetes and Helm**

- **Walk me through what is inside your Helm charts, how they are integrated into your delivery flow, and what is actually written in them.**
- **What is defined in your `values.yaml`, and how does it differ per environment?**
- **A microservice is being deployed to a Pod in GKE, but the deployment is failing — the Pod is in an error state and getting terminated. How do you troubleshoot that, and what is your general troubleshooting approach?**
- **You list "optimised Kubernetes deployment configs" on your CV. What was your role there and what did you actually change?**

**Terraform**

- **How do you import a resource into Terraform that was created manually in AWS or GCP, and what is the exact command?**
- **How are you using Terraform to provision the cluster nodes?**
- **What goes inside your provider file and your `main.tf` when you stand up nodes and their supporting infrastructure?**
- **Write Terraform for AWS that creates a VPC and a subnet — public or private, your choice — and attaches the subnet to the VPC.**

**Incidents and continuous improvement**

- **You mention architecting a blameless postmortem framework for continuous learning. What did you do with it that actually reduced the recurrence of critical incidents?**
- **You also claim a reduction in MTTR. Which automation delivered that?**

**Platform and operations breadth**

- **Describe your exposure to distinct Dev, QA, and Prod environments.**
- **What is your understanding of the components of a software architecture — load balancers, web servers, application servers, databases, and the integrations between them?**
- **What do you know about production system sizing, provisioning, setup, ongoing maintenance, and decommissioning?**
- **What is your experience with infrastructure administration duties such as licensing, billing, cost reduction, and security?**

## Example

```text
Altimetrik — SRE, reported round
22 questions

  Observability / SLO         8   tools, self-built dashboards, golden signals,
                                  SLO alerting, error budget, burn rate
  Kubernetes and Helm         4   chart contents, values.yaml, GKE Pod failure,
                                  config optimisation (CV audit)
  Terraform                   4   import, node provisioning, provider + main.tf,
                                  live VPC + subnet
  Incidents / improvement     2   blameless postmortems, MTTR automation
  Platform breadth            4   environments, architecture components,
                                  sizing and lifecycle, licensing and cost

THE PATTERN TO NOTICE
  The interviewer escalates: tool -> did you build it -> which ones ->
  on what principles -> did you do SLO alerting -> what burn rate.
  Each answer is a foothold for the next question. Shallow answers get
  found out within two follow-ups.
```

## Interview tips

- Burn rate is the question most candidates fail. Give the arithmetic: burn rate is how fast you are consuming the error budget relative to the rate that would exhaust it exactly at the end of the window, so 1× lands precisely on budget and 2× exhausts it in half the period. Then name multi-window multi-burn-rate alerting — a fast window at roughly 14× for pages and a slower window at around 6× or 3× for tickets. See [error budgets](../site-reliability-engineering/what-is-error-budget.md) and [designing alerts that page a human](../site-reliability-engineering/how-do-you-design-alerts-that-page-a-human.md).
- Say the golden signals explicitly — latency, traffic, errors, saturation — and then say which of your dashboards covers each. Naming Grafana without naming the signals reads as tool familiarity, not SRE practice. See [service level indicators](../site-reliability-engineering/what-are-service-level-indicators-slis.md) and [service level objectives](../site-reliability-engineering/what-are-service-level-objectives-slos.md).
- SLO-based alerting means alerting on budget consumption rather than on raw thresholds, so a brief spike that does not threaten the objective stays quiet. Contrast it with CPU-threshold alerting to show you understand why it exists.
- The GKE Pod failure question wants a repeatable method, so give one: `kubectl get pod` for phase and restart count, `describe` for events, image pull errors and scheduling failures, `logs --previous` for the crashed container, then the exit code to separate `OOMKilled` from a config or secret error from a failing probe. See [troubleshooting a Pod stuck in Pending or CrashLoopBackOff](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md) and [how probes differ](../kubernetes/how-do-liveness-readiness-and-startup-probes-differ.md).
- Two questions here audit your CV directly. Anything you have written about postmortems, config optimisation, or MTTR must come with a number and a mechanism — action items tracked to closure, requests and limits right-sized from observed usage, a runbook turned into automation. Unsupported CV claims are the fastest way to lose this round. See [post-mortem analysis](../incident-management/what-is-post-mortem-analysis.md).
- For `terraform import`, give the command shape — `terraform import <address> <cloud-id>` — and add that current Terraform prefers `import` blocks in configuration, which make the operation reviewable and planned rather than a local state mutation. See [importing existing infrastructure](../infrastructure-as-code/how-do-you-import-existing-cloud-infrastructure-into-terraform.md).
- When describing Helm, cover `Chart.yaml`, `values.yaml`, the `templates/` directory, `_helpers.tpl`, and how you override values per environment; then say whether you use `helm upgrade --install` from CI or a GitOps controller. See [what Helm is](../container-orchestration-advanced/what-is-helm.md) and [Argo CD](../devops-tools-and-automation/what-is-argocd.md).
- Practise writing `aws_vpc`, `aws_subnet`, `aws_internet_gateway`, and `aws_route_table` from memory. Being asked to write it live, out of an SRE conversation, is a fluency test rather than a design test. See [what Terraform is](../infrastructure-as-code/what-is-terraform.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is Site Reliability Engineering?]] (`#96`): [What is Site Reliability Engineering?](../site-reliability-engineering/what-is-site-reliability-engineering.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you design alerts that page a human?]] (`#233`): [How do you design alerts that page a human?](../site-reliability-engineering/how-do-you-design-alerts-that-page-a-human.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
