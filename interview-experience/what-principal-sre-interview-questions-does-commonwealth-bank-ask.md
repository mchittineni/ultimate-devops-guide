---
title: "What principal SRE interview questions does Commonwealth Bank ask?"
id: 325
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - commonwealth-bank
  - site-reliability-engineering
  - monitoring-and-logging
  - slo-engineering
  - sla-management
  - infrastructure-monitoring
  - network-security
---

# What principal SRE interview questions does Commonwealth Bank ask?

## Questions

**Observability architecture**

- **What is observability architecture? Explain how the pieces fit together.**
- **What is the difference between observability and monitoring?**
- **Explain metrics, logs, and traces, and name the tools you have used for each.**
- **If you already have logs, why do you also need distributed tracing?**
- **How does observability help you maintain site reliability in practice?**

**SLIs, SLOs, and SLAs**

- **How are an SLA and an SLO set for an application? Explain it from a business perspective, not as a formula.**
- **How do you decide which SLI to use for an application?**

**Fundamentals**

- **What is DNS, and what exactly happens in the background when you type `google.com` into a browser?**

## Example

```text
Commonwealth Bank — Principal SRE (4-5 YOE), reported round
8 questions

  Observability               5   architecture, vs monitoring, the three
                                  signals + tools, why traces, tie to reliability
  SLI / SLO / SLA             2   how targets are set (business framing),
                                  how you pick the SLI
  Fundamentals                1   DNS and the request path

WHAT IS ABSENT IS THE SIGNAL
  No Terraform. No CI/CD. No Docker. A principal-level SRE round at a bank
  tests judgement about reliability, not tool operation. Prepare depth on
  one topic rather than breadth across ten.
```

```text
PICKING AN SLI — the shape of a good answer

  Start from the user journey, not the infrastructure.
    "Can a customer log in and see their balance?"

  Then choose a measurable proxy for that journey:
    availability  = successful requests / valid requests   (not "server is up")
    latency       = 99th percentile of the balance-view endpoint
    correctness   = balance matches the ledger

  Reject bad candidate SLIs out loud:
    CPU utilisation      -> a cause, not a user experience
    "server uptime"      -> the box can be up while the journey is broken
    average latency      -> hides the tail that customers actually feel
```

## Interview tips

- The SLA and SLO question comes with an explicit instruction to avoid the formula, so do not recite nines. Frame it as a negotiation: the business decides how much unreliability its customers and regulators will tolerate and what it costs to buy more, the SLA is the externally promised number with financial consequences, and the SLO is the tighter internal target you manage to so you never approach the SLA. Say that the SLO is deliberately stricter than the SLA to leave headroom. See [what belongs in a well-written SLA](../sla-management/what-belongs-in-a-well-written-sla.md) and [SLA versus SLO versus SLI versus OLA](../sla-management/what-is-the-difference-between-an-sla-an-slo-an-sli-and-an-ola.md).
- Then close that answer with the error budget, because it is the mechanism that turns an SLO into a decision: the budget is what remains of the tolerated unreliability, and when it is spent, feature work yields to reliability work. At a bank, add that this makes the risk trade-off explicit and auditable rather than a matter of opinion. See [error budgets](../site-reliability-engineering/what-is-error-budget.md).
- For choosing an SLI, work from the customer journey inwards and say why infrastructure metrics are disqualified — CPU is a cause, not an experience. Name the good-events-over-valid-events form, and mention that an SLI must be something the user would notice. See [service level indicators](../site-reliability-engineering/what-are-service-level-indicators-slis.md) and [service level objectives](../site-reliability-engineering/what-are-service-level-objectives-slos.md).
- Observability versus monitoring is asked separately from the architecture question, so keep them distinct. Monitoring answers questions you knew to ask in advance through predefined dashboards and thresholds; observability lets you ask new questions of a running system after the fact, which requires high-cardinality, high-dimensionality data. Use the phrase "unknown unknowns" and give an example of a question you could not have predicted. See [monitoring versus logging](../monitoring-and-logging/explain-the-difference-between-monitoring-and-logging.md) and [monitoring in DevOps](../monitoring-and-logging/what-is-monitoring-in-devops.md).
- "Why traces when you have logs" is the sharpest question in the set. The answer is causality across service boundaries: logs are per-service events with no inherent relationship, while a trace carries a shared trace ID and parent-child spans, so you can see that a slow checkout was caused by one downstream call and exactly how much of the total latency it owned. Add that in a microservice architecture logs cannot tell you _which_ of forty services caused a p99 regression, and traces can. Mention OpenTelemetry for propagation and sampling as the practical concern.
- For observability architecture, describe it as a pipeline with decisions at each stage: instrumentation (OpenTelemetry SDKs, auto-instrumentation), collection (agent or collector, DaemonSet or sidecar), transport and processing (batching, sampling, redaction of customer data), storage per signal type (a time-series database for metrics, an indexed store for logs, a trace backend), and consumption (dashboards, alerting on SLOs, exemplars linking a metric spike to a trace). Naming retention tiers and cost control is what makes it an architecture rather than a tool list. See [designing a logging pipeline that stays affordable at scale](../monitoring-and-logging/how-do-you-design-a-logging-pipeline-that-stays-affordable-at-scale.md).
- When naming tools per signal, pair them honestly with what you have actually run — for example Prometheus and Grafana for metrics, the ELK stack or Loki for logs, Jaeger or Tempo for traces — and mention correlation between them, since a principal-level interviewer is listening for whether your three signals are joined by trace and request IDs or sit in three disconnected products. See [what Prometheus is](../monitoring-and-logging/what-is-prometheus.md), [what Grafana is](../monitoring-and-logging/what-is-grafana.md), and [what the ELK stack is](../monitoring-and-logging/what-is-elk-stack.md).
- Tie observability to reliability with outcomes rather than adjectives: it shortens detection and diagnosis time, so it moves MTTR; it makes SLOs measurable, so it enables the error-budget conversation; and it turns postmortems into evidence-based reviews. See [designing alerts that page a human](../site-reliability-engineering/how-do-you-design-alerts-that-page-a-human.md) and [post-mortem analysis](../incident-management/what-is-post-mortem-analysis.md).
- The DNS question is the only fundamentals question, and in an observability-heavy round it is best answered with the full request path — resolver cache, recursive resolution, TCP, TLS, load balancer, application, response, render — then a sentence on where you would observe each hop. There is a full walkthrough at [what happens when a user opens your application in a browser](../network-security/what-happens-when-a-user-opens-your-application-in-a-browser.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between SRE, DevOps, and Platform Engineering?]] (`#232`): [What is the difference between SRE, DevOps, and Platform Engineering?](../site-reliability-engineering/what-is-the-difference-between-sre-devops-and-platform-engineering.md)
- [[What is Site Reliability Engineering?]] (`#96`): [What is Site Reliability Engineering?](../site-reliability-engineering/what-is-site-reliability-engineering.md)
- [[What are Service Level Objectives (SLOs)?]] (`#97`): [What are Service Level Objectives (SLOs)?](../site-reliability-engineering/what-are-service-level-objectives-slos.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
