---
title: "What is Chaos Engineering and how do GameDays uncover latent systemic flaws in production?"
id: 646
category: "Site Reliability Engineering (SRE)"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - chaos-engineering
  - gameday
  - resilience
  - gremlin
quiz:
  stem: "What is the first step in conducting a scientific Chaos Engineering experiment?"
  options:
    - "Deleting all production Kubernetes namespaces"
    - "Defining a measurable 'Steady State' metric baseline representing normal, healthy system operation"
    - "Submitting a ticket to cancel cloud backups"
    - "Restarting all network routers"
  answer: 2
  explanation: "Chaos experiments require a measurable 'steady state' baseline (e.g. latency and order completion rate) so engineers can verify whether the system maintains normal function under simulated stress."
---

# What is Chaos Engineering and how do GameDays uncover latent systemic flaws in production?

**Short answer:** Chaos Engineering is the discipline of experimenting on a system to build confidence in its capability to withstand turbulent conditions; GameDays are structured cross-team simulations where realistic failures (AZ loss, DB crash, DNS drop) are injected to validate automated recovery.

## Detail

Coined by Netflix (Chaos Monkey), Chaos Engineering is **not** 'randomly breaking things in production'; it follows the scientific method:

### The Chaos Engineering Scientific Method

1. **Define Steady State**: Establish normal metric baselines (e.g. 5,000 req/sec, p99 latency < 80ms, 99.99% success).
2. **Formulate a Hypothesis**: _'If an entire AWS Availability Zone loses power, our multi-zone EKS cluster and Aurora database will failover automatically with zero dropped transactions.'_
3. **Introduce Chaos Experiment (Controlled Blast Radius)**:
   - Terminate worker nodes in AZ-a.
   - Inject network packet delay via Chaos Mesh / Gremlin.
   - Drop master database connection.
4. **Observe & Disprove**:
   - Did the Aurora database promote the replica in 15 seconds?
   - Did application connection pools hang for 5 minutes instead of failing fast?
5. **Remediate**: Fix discovered race conditions and timeouts before real disasters occur.

**Start small and earn the right to go to production.** Run experiments first in staging, then in production with a tiny blast radius (one pod, one AZ, a percentage of traffic), always with an automatic abort condition tied to the steady-state metric and a named person who can stop it. A GameDay adds the human side: the on-call team responds as if it were real, which tests runbooks, alerts, and communication as well as the architecture. The trade-off is real risk and real cost - an experiment without abort conditions is just an outage you scheduled.

## Example

```yaml
# Chaos Mesh: kill one checkout pod every 10 minutes during the GameDay (delete the Schedule to stop)
apiVersion: chaos-mesh.org/v1alpha1
kind: Schedule
metadata:
  name: checkout-pod-kill
  namespace: chaos-testing
spec:
  schedule: "*/10 * * * *"
  concurrencyPolicy: Forbid
  historyLimit: 5
  type: PodChaos
  podChaos:
    action: pod-kill
    mode: one # blast radius: a single pod
    selector:
      namespaces: [checkout]
      labelSelectors: { app: checkout }
```

Hypothesis: "with one of six checkout pods killed every 10 minutes, the p99 stays under 300 ms and the success rate stays above 99.9%". Abort (delete the Schedule) if the burn-rate alert fires.

## Interview tips

- Scientific method: steady state baseline -> hypothesis -> blast radius control -> experiment.
- Not random destruction; targeted hypothesis testing.
- GameDays involving cross-functional engineering, operations, and leadership.
- Surfacing hidden cascading timeouts and failover bugs in controlled environments.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How Do You Handle Planned Maintenance Windows in Error Budget Calculations?]] (`#720`): [How Do You Handle Planned Maintenance Windows in Error Budget Calculations?](../slo-engineering/how-do-you-handle-planned-maintenance-windows-in-error-budget-calculations.md)
- [[How Do You Establish an Actionable Error Budget Policy with Engineering Leadership?]] (`#722`): [How Do You Establish an Actionable Error Budget Policy with Engineering Leadership?](../slo-engineering/how-do-you-establish-an-actionable-error-budget-policy-with-engineering-leadership.md)
- [[What do you do when you breach an SLA?]] (`#190`): [What do you do when you breach an SLA?](../sla-management/what-do-you-do-when-you-breach-an-sla.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Site Reliability Engineering (SRE)](./README.md) · [All topics](../README.md)
