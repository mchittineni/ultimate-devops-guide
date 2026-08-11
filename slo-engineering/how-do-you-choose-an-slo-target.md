---
title: "How do you choose an SLO target?"
id: 177
category: "SLO Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - slo-engineering
  - interview-questions
---

# How do you choose an SLO target?

**Short answer:** Start from measured current performance and user expectation, not from a round number. Look at the last 4–8 weeks of the SLI, ask whether users complained during the worse periods, and set the target just above the level users tolerate - then check that the resulting error budget is large enough to permit normal change. Tighten later; a target you cannot meet teaches everyone to ignore SLOs.

## Detail

**The three inputs.** _Measured history_ - what the service already delivers. _User tolerance_ - the point at which complaints, abandoned sessions, or retries begin. _Cost of the next nine_ - each additional nine typically multiplies infrastructure and engineering effort, and 99.99% is unreachable if your dependencies are 99.9%.

**Do not aim for 100%.** A target of 100% leaves no error budget, so every deploy is a violation and the SLO stops guiding decisions. It also over-invests: users on mobile networks cannot perceive the difference between 99.95% and 99.99%.

**Check the budget is workable.** A 99.99% monthly target allows about 4.3 minutes of downtime - less than one bad rollback. If your deploy process routinely costs 10 minutes of degradation, the target is incompatible with your delivery practice; either fix the practice or set an honest target.

**Different journeys deserve different targets.** Checkout and login are more important than an admin report export. Setting one availability number for a whole product either over-protects the report or under-protects checkout. Per-critical-user-journey SLOs are the practice worth naming.

**Iterate on a schedule.** Review quarterly with real data: consistently unspent budget means the target is too loose (or you are over-investing in reliability); chronic exhaustion means it is too tight or the service needs work. Both are useful findings, and both should change something.

## Example

```promql
# Measure first: 28-day availability from request counters, before picking a number
sum(rate(http_requests_total{job="checkout",code!~"5.."}[28d]))
  /
sum(rate(http_requests_total{job="checkout"}[28d]))
```

```text
Result: 99.93% measured, no user complaints in the two worst weeks
→ set SLO at 99.9% (budget 43 min/30d), review in a quarter
→ NOT 99.99% (4.3 min/30d), which the current deploy process cannot respect
```

## Interview tips

- "Measure first, then set the target slightly above user tolerance" is the answer; arbitrary nines are the trap.
- Say explicitly that 100% is the wrong target and explain why - no budget means no ability to ship.
- Strong follow-up to anticipate: "your dependency is 99.9%, can you promise 99.99%?" - not without redundancy or graceful degradation, and the maths should be your reply.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SLO Engineering](./README.md) · [All topics](../README.md)
