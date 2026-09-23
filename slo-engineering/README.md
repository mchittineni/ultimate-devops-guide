---
title: "SLO Engineering"
category: "SLO Engineering"
tags:
  - devops
  - slo-engineering
  - index
---

# SLO Engineering

The engineering practice behind SLOs: choosing targets, burn-rate alerting, correct latency SLIs, error budget policies, and SLOs for batch, async, and third-party dependencies.

**14 questions** · 🟢 Beginner: 1 · 🟡 Intermediate: 7 · 🔴 Advanced: 6

## Questions

| #   | Question                                                                                                                                                                       | Difficulty      |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------- |
| 177 | [How do you choose an SLO target?](./how-do-you-choose-an-slo-target.md)                                                                                                       | 🟡 Intermediate |
| 178 | [What is multi-window multi-burn-rate alerting?](./what-is-multi-window-multi-burn-rate-alerting.md)                                                                           | 🔴 Advanced     |
| 179 | [How do you measure a latency SLI correctly?](./how-do-you-measure-a-latency-sli-correctly.md)                                                                                 | 🔴 Advanced     |
| 180 | [What is an error budget policy?](./what-is-an-error-budget-policy.md)                                                                                                         | 🟡 Intermediate |
| 181 | [How do you define SLOs for batch and asynchronous workloads?](./how-do-you-define-slos-for-batch-and-asynchronous-workloads.md)                                               | 🔴 Advanced     |
| 182 | [How do you handle SLOs for dependencies you do not own?](./how-do-you-handle-slos-for-dependencies-you-do-not-own.md)                                                         | 🔴 Advanced     |
| 183 | [What tooling do you use to implement SLOs?](./what-tooling-do-you-use-to-implement-slos.md)                                                                                   | 🟡 Intermediate |
| 304 | [What do you need before you can set your first SLO?](./what-do-you-need-before-you-can-set-your-first-slo.md)                                                                 | 🟢 Beginner     |
| 718 | [What is the Difference Between Request-Based and Window-Based SLIs?](./what-is-the-difference-between-request-based-and-window-based-slis.md)                                 | 🟡 Intermediate |
| 719 | [How Do You Define and Track SLOs for Asynchronous Background Jobs and Queues?](./how-do-you-define-and-track-slos-for-asynchronous-background-jobs-and-queues.md)             | 🟡 Intermediate |
| 720 | [How Do You Handle Planned Maintenance Windows in Error Budget Calculations?](./how-do-you-handle-planned-maintenance-windows-in-error-budget-calculations.md)                 | 🟡 Intermediate |
| 721 | [What is Error Budget Burn-Rate Alerting and How Do You Tune Thresholds?](./what-is-error-budget-burn-rate-alerting-and-how-do-you-tune-thresholds.md)                         | 🔴 Advanced     |
| 722 | [How Do You Establish an Actionable Error Budget Policy with Engineering Leadership?](./how-do-you-establish-an-actionable-error-budget-policy-with-engineering-leadership.md) | 🟡 Intermediate |
| 723 | [How Do You Set SLIs and SLOs for Event-Driven and Streaming Architectures?](./how-do-you-set-slis-and-slos-for-event-driven-and-streaming-architectures.md)                   | 🔴 Advanced     |

## What interviewers probe here

- Multi-window multi-burn-rate alerting, and why the short window exists.
- Latency as a threshold ratio rather than a percentile value.
- Owning the SLO even when the failing dependency is not yours.

---

[⬅ Back to all topics](../README.md)
