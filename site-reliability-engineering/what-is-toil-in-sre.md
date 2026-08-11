---
title: "What is Toil in SRE?"
id: 100
category: "Site Reliability Engineering (SRE)"
difficulty: "Intermediate"
tags:
  - devops
  - site-reliability-engineering
  - interview-questions
---

# What is Toil in SRE?

**Short answer:** Toil is manual, repetitive, automatable, tactical work with no enduring value, that scales linearly with service growth. SRE treats it as a measurable quantity to be capped and systematically eliminated.

## Detail

**The definition has six criteria** - work is toil to the extent that it is:

1. **Manual** - a human performs it.
2. **Repetitive** - done again and again.
3. **Automatable** - a machine could do it.
4. **Tactical** - reactive and interrupt-driven, not strategic.
5. **Without enduring value** - the service is no better afterwards than before.
6. **Linear with service growth** - twice the traffic means twice the work.

**Examples:** manually restarting a stuck service, hand-applying the same configuration change to 50 hosts, processing routine access requests, manually failing over a database, copying data between systems every morning.

**Not toil:** on-call itself (some is inherent), incident response for novel failures, writing automation, capacity planning, design review, post-mortems. Overhead like meetings and email is not toil either - it is just overhead.

**Managing it**

- **Measure it.** Track hours spent on toil per person per week; without a number, it is invisible and always deprioritised.
- **Cap it.** Google's guideline is that SREs spend no more than 50% of their time on operational work, with the rest on engineering.
- **Prioritise by frequency × time × people affected** - automate the highest product first.
- **Eliminate before automating.** The best fix is often making the task unnecessary: fix the root cause of the restarts rather than scripting them.
- **Self-service** removes toil from your team without automating it away entirely - give the requester a safe tool.

**Why it matters:** unmanaged toil grows with the service until the team has no capacity for engineering, at which point reliability stops improving and attrition begins.

## Interview tips

- Reciting the six criteria precisely is the highest-signal answer to this question.
- "Eliminate, then automate, then delegate to self-service" is a good escalation order.
- Have a concrete example: what toil you measured, what you automated, and how many hours a week it returned.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you choose an SLO target?]] (`#177`): [How do you choose an SLO target?](../slo-engineering/how-do-you-choose-an-slo-target.md)
- [[How do you measure a latency SLI correctly?]] (`#179`): [How do you measure a latency SLI correctly?](../slo-engineering/how-do-you-measure-a-latency-sli-correctly.md)
- [[How do you define SLOs for batch and asynchronous workloads?]] (`#181`): [How do you define SLOs for batch and asynchronous workloads?](../slo-engineering/how-do-you-define-slos-for-batch-and-asynchronous-workloads.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Site Reliability Engineering (SRE)](./README.md) · [All topics](../README.md)
