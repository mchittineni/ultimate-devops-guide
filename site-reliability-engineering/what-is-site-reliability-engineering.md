---
title: "What is Site Reliability Engineering?"
id: 96
category: "Site Reliability Engineering (SRE)"
difficulty: "Beginner"
tags:
  - devops
  - site-reliability-engineering
  - interview-questions
---

# What is Site Reliability Engineering?

**Short answer:** SRE is Google's discipline of applying software engineering to operations - running services against explicit reliability targets, using error budgets to balance velocity against stability, and automating away repetitive operational work.

## Detail

**The founding idea:** treat operations as a software problem. Rather than scaling operations by hiring more people, you write software that makes the system self-managing.

**Core practices**

- **SLIs, SLOs, and error budgets.** Define what reliability means numerically, agree the target, and use the remaining budget to decide whether to ship features or fix reliability.
- **Toil budget.** SRE teams cap manual operational work - Google's guideline is 50% - with the remainder spent on engineering that reduces it.
- **Blameless post-mortems.** Every significant incident produces a written analysis focused on systemic causes and concrete actions.
- **Release engineering.** Canaries, progressive rollout, and automated rollback owned as first-class engineering work.
- **Capacity planning and demand forecasting** based on measured headroom, not guesses.
- **Monitoring and observability** designed around user-visible symptoms.

**The error budget is the cultural mechanism.** A 99.9% SLO permits 43 minutes of unreliability per month. While budget remains, teams ship freely. When it is exhausted, the agreed consequence - typically a feature freeze until reliability is restored - applies automatically. This converts an argument between development and operations into a data-driven policy both sides agreed to in advance.

**SRE vs DevOps:** DevOps is a set of cultural goals; SRE is a specific, opinionated implementation of them. As the saying goes, "class SRE implements DevOps."

## Interview tips

- Lead with error budgets - they are what makes SRE distinct from "operations with a better name."
- "100% is the wrong reliability target" is a genuinely SRE thing to say, and true: the cost curve is exponential.
- Mention the 50% toil cap; interviewers listen for whether you know SRE has structural rules, not just principles.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you choose an SLO target?]] (`#177`): [How do you choose an SLO target?](../slo-engineering/how-do-you-choose-an-slo-target.md)
- [[What is multi-window multi-burn-rate alerting?]] (`#178`): [What is multi-window multi-burn-rate alerting?](../slo-engineering/what-is-multi-window-multi-burn-rate-alerting.md)
- [[How do you measure a latency SLI correctly?]] (`#179`): [How do you measure a latency SLI correctly?](../slo-engineering/how-do-you-measure-a-latency-sli-correctly.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Site Reliability Engineering (SRE)](./README.md) · [All topics](../README.md)
