---
title: "What is Chaos Engineering?"
id: 144
category: "Advanced DevOps & Cloud"
difficulty: "Advanced"
tags:
  - devops
  - advanced-devops-cloud
  - interview-questions
---

# What is Chaos Engineering?

**Short answer:** Chaos engineering is the disciplined practice of running controlled experiments that inject failure into a system to test a hypothesis about its resilience - finding weaknesses before they cause an outage.

## Detail

**It is not "randomly breaking things."** It is the scientific method applied to reliability:

1. **Define steady state** - a measurable indicator of normal health (order rate, p99 latency, error rate).
2. **Form a hypothesis** - "if one availability zone becomes unreachable, error rate stays below 0.1% and p99 latency stays under 500 ms."
3. **Design the experiment** with the smallest blast radius that tests the hypothesis, and a defined abort condition.
4. **Run it**, starting in a non-production environment, then in production with limited scope and everyone watching.
5. **Observe and analyse** - either the hypothesis holds (confidence gained) or it does not (a weakness found before customers found it).
6. **Fix and repeat**, then automate the experiment as a regression test.

**Failure modes to inject:** instance and pod termination, availability-zone loss, network latency and packet loss, dependency failure and timeout, DNS failure, resource exhaustion (CPU, memory, disk), clock skew, and certificate expiry.

**Safety requirements are non-negotiable:** a clearly bounded blast radius, an automated abort/rollback ("stop button"), strong observability so you can see the impact immediately, business-hours execution with the team present, and stakeholder awareness.

**Tools:** Chaos Mesh and LitmusChaos for Kubernetes, AWS Fault Injection Service (FIS, formerly Fault Injection Simulator), Azure Chaos Studio, Gremlin (commercial), and Netflix's Chaos Monkey, the original.

**Maturity note:** do not start here. If you do not yet have good observability, tested rollback, and known-good SLOs, chaos experiments will only tell you things you already suspect.

## Example

```yaml
# Chaos Mesh: kill one checkout Pod every 10 minutes, bounded to a labelled canary set
apiVersion: chaos-mesh.org/v1alpha1
kind: Schedule
metadata:
  name: checkout-pod-kill
  namespace: chaos
spec:
  schedule: "*/10 * * * *"
  concurrencyPolicy: Forbid
  type: PodChaos
  podChaos:
    action: pod-kill
    mode: one # blast radius: a single Pod per run
    selector:
      namespaces: [checkout]
      labelSelectors: { chaos: "allowed" } # only Pods that opted in
# Hypothesis: checkout error rate stays < 0.1% and p99 < 500 ms during each kill.
# Abort: delete the Schedule (kubectl delete schedule checkout-pod-kill -n chaos).
```

## Interview tips

- Leading with "hypothesis and blast radius" immediately separates you from candidates who think it means random destruction.
- The abort condition and stop button are the safety details interviewers listen for.
- "Do not start chaos engineering before you have observability" is a mature caveat.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
