---
title: "What belongs in a well-written SLA?"
id: 187
category: "SLA Management"
difficulty: "Intermediate"
tags:
  - devops
  - sla-management
  - interview-questions
---

# What belongs in a well-written SLA?

**Short answer:** Scope, a precise measurement method, the targets, exclusions, the remedy, the claim process, and a review clause. The number is the least interesting part - most disputes are about how availability was measured and whether an exclusion applied, so those clauses are where engineering input matters most.

## Detail

**The sections, and the engineering question behind each:**

| Clause        | What it must say                                                | Engineering must confirm                |
| ------------- | --------------------------------------------------------------- | --------------------------------------- |
| Scope         | which services, endpoints, regions, and plan tiers are covered  | can we measure per that boundary?       |
| Definitions   | what "unavailable" means; sample interval; vantage point        | do we have that telemetry, retained?    |
| Targets       | availability, and often latency and support response times      | is it below our internal SLO?           |
| Exclusions    | maintenance, force majeure, customer error, beta, third parties | can we evidence the exclusion?          |
| Remedies      | credit tiers, caps, and termination rights                      | what is the worst-case exposure?        |
| Claim process | how and by when a customer claims; who arbitrates               | can we produce evidence in that window? |
| Reporting     | what is published, how often                                    | is the status page automated?           |
| Review        | how the SLA changes and with what notice                        | -                                       |

**Measurement is the contested clause.** "Measured by our monitoring" invites disputes; "measured at the external load balancer using 1-minute synthetic probes from three regions, excluding requests that fail client-side validation" can be argued about honestly. Whoever owns the measurement in effect owns the outcome, so expect customers to push for third-party monitoring or for their own telemetry to count.

**Exclusions must be narrow and evidenced.** A maintenance exclusion needs a notice period and a cap (for example, four hours per month with seven days' notice). "Failures caused by third-party providers" is a red flag for the customer - if you use a payment provider, that is your architecture choice, and mature vendors do not exclude it.

**Support-response SLAs are separate and often more contentious than uptime.** Define severity levels, response versus resolution (never promise resolution times), business hours versus 24/7, and the escalation path. Response time is measurable and controllable; resolution time is not.

**Know your maximum exposure.** Credits are usually capped at a percentage of the monthly fee, which means the financial risk is bounded - but reputational and renewal risk is not. When engineering is asked "can we promise this?", the answer should reference the internal SLO, the composite dependency ceiling, and the historical measurement, not optimism.

## Interview tips

- Say early that measurement definition and exclusions cause more disputes than the target itself.
- "Promise response times, not resolution times" is a crisp, credible detail.
- Expect: "sales wants 99.99% - what do you say?" Reference measured history, the dependency ceiling, what it would cost to reach, and offer a tiered alternative rather than a flat refusal.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SLA Management](./README.md) · [All topics](../README.md)
