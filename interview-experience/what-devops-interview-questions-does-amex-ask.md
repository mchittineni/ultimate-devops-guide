---
title: "What DevOps interview questions does AMEX ask?"
id: 306
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - amex
  - kubernetes
  - docker
  - monitoring-and-logging
  - sla-management
  - site-reliability-engineering
  - devops-tools-and-automation
  - cloud-migration
  - incident-management
---

# What DevOps interview questions does AMEX ask?

## Questions

**Containers and Kubernetes**

- **What is the difference between Docker and Kubernetes, and why do you need an orchestrator on top of a container runtime at all?**
- **How does authentication to the Kubernetes API endpoint work — what happens between `kubectl` presenting a credential and the API server authorising the request?**
- **Walk me through how you diagnosed a Pod stuck in `CrashLoopBackOff`. What did you look at, in what order, and what was the root cause?**

**Deployments and release engineering**

- **How do you reduce or eliminate downtime during a deployment? Which strategy did you use, and how did you verify there was no user impact?**

**Monitoring, logging, and observability**

- **Which monitoring or logging agents have you deployed, and what does each one collect?**
- **Name a specific agent you rolled out for a customer or in-house, and explain why that one was chosen over the alternatives.**
- **Suppose you have 100 applications emitting logs. How do you design log collection and analysis so an engineer can still find one error quickly?**

**Reliability vocabulary**

- **What is an SLA and what is an SLO, how do they differ, and how does an SLI relate to both?**
- **What is the difference between SRE and DevOps — as practices, and in how the two roles are held accountable?**

**Experience walkthrough**

- **Describe the cloud architecture you have worked on: the components, how traffic flows through it, and why it was designed that way.**
- **Have you migrated workloads from on-premises to the cloud? If so, what specific challenges did you hit and how did you resolve them?**
- **Take me through a production issue you personally handled — detection, diagnosis, fix, and what you changed so it could not recur.**

## Example

```text
AMEX — DevOps Engineer (~3 YOE), reported round
12 questions

  Kubernetes / containers     3   Docker vs K8s, API auth, CrashLoopBackOff
  Observability               3   agents deployed, agent choice, 100-app logging
  Reliability vocabulary      2   SLA vs SLO, SRE vs DevOps
  Experience walkthrough      3   architecture, migration, production incident
  Release engineering         1   zero-downtime deployment

WHERE THE WEIGHT SITS
  ~42% experience-led ("what did you do")  -> prepare stories, not definitions
  ~58% mechanism-led ("how does it work")  -> prepare the mechanism one level deeper
```

## Interview tips

- Three of the twelve questions are open experience prompts. Have one production incident, one migration, and one architecture rehearsed as 90-second narratives with a number in each (users affected, minutes of downtime, cost saved).
- "How does endpoint authentication work in Kubernetes" is the depth probe in this set. Answer in stages — authentication (certificates, tokens, OIDC), then authorisation (RBAC), then admission control — and say which your cluster actually used. See [how RBAC works](../kubernetes/how-does-rbac-work-in-kubernetes.md).
- For the 100-applications logging question, do not name a tool and stop. Describe the pipeline: structured logs, an agent per node, a central store, retention tiers, and an index or label scheme that makes search possible. See [PromQL and Alertmanager](../monitoring-and-logging/how-do-you-write-effective-promql-queries-and-alertmanager-rules.md).
- SLA versus SLO is asked as a definition but graded on whether you mention the error budget. Add it unprompted — see [error budgets](../site-reliability-engineering/what-is-error-budget.md).
- Financial-services interviews follow the deployment question with change control: who approves a release, what the rollback plan is, and how you prove it worked. Be ready even though it was not asked here.
- The CrashLoopBackOff answer should name `kubectl logs --previous`, the container exit code, and the split between `OOMKilled`, a bad config or secret, and a failing probe. See [debugging Pods](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md).

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
