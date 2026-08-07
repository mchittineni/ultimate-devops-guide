---
title: "How do you calculate allowed downtime for an availability target?"
id: 185
category: "SLA Management"
difficulty: "Beginner"
tags:
  - devops
  - sla-management
  - interview-questions
---

# How do you calculate allowed downtime for an availability target?

**Short answer:** Allowed downtime is `(1 − target) × window`. For 99.9% over a 30-day month that is `0.001 × 43,200 minutes ≈ 43.2 minutes`. Know the common values by heart, and be precise about the window (30 days versus a calendar month versus a year) because the same percentage yields very different budgets.

## Detail

**The table worth memorising:**

| Availability | Per day  | Per 30 days | Per year  |
| ------------ | -------- | ----------- | --------- |
| 99%          | 14.4 min | 7.2 h       | 3.65 days |
| 99.5%        | 7.2 min  | 3.6 h       | 1.83 days |
| 99.9%        | 1.44 min | 43.2 min    | 8.77 h    |
| 99.95%       | 43 s     | 21.6 min    | 4.38 h    |
| 99.99%       | 8.6 s    | 4.3 min     | 52.6 min  |
| 99.999%      | 0.86 s   | 26 s        | 5.26 min  |

**Time-based versus request-based.** Downtime minutes assume you can define "down" for the whole service, which suits infrastructure. For a request-serving system, the request-ratio definition (failed requests / total requests) is more honest: a 5% error rate for two hours is real damage that a time-based definition may score as fully available. Most cloud provider SLAs are request-based or "unavailable minute"-based for exactly this reason — read the definition, not just the number.

**The window changes everything.** 99.99% annually permits 52 minutes in one bad incident and remains compliant; 99.99% monthly permits only 4.3 minutes and would breach. Vendors prefer monthly windows for credits (small credits, frequent resets); customers pushing for annual windows get a larger tolerance but slower remedies.

**Sampling defines reality.** If availability is computed from one-minute health-check samples, a 20-second outage may register as zero or as a full minute depending on timing. Contracts should state the sample interval and what fraction of a sample counts as unavailable.

**Nines are not free.** Each additional nine typically requires eliminating another single point of failure — multi-AZ, then multi-region, then multi-provider — and beyond 99.99% the constraint is usually your change process and your dependencies, not hardware.

## Example

```python
# Allowed downtime for any target and window
def budget_minutes(target_pct: float, window_days: float = 30) -> float:
    return (1 - target_pct / 100) * window_days * 24 * 60

budget_minutes(99.9)          # 43.2  minutes per 30 days
budget_minutes(99.99)         # 4.32  minutes per 30 days
budget_minutes(99.99, 365)    # 52.56 minutes per year

# Serial dependencies multiply — this is the ceiling your own service inherits
0.999 * 0.999 * 0.9995        # 0.99750 -> 99.75%, about 1.8 h per 30 days
```

## Interview tips

- Have 99.9% = 43 minutes and 99.99% = 4.3 minutes ready instantly; hesitating here reads badly.
- Ask which window and which definition (time or request) before answering — that question is itself the signal.
- Expect: "can you offer 99.99% on top of three 99.9% dependencies?" — no, not serially; the answer is redundancy or degradation.

---

[⬅ Back to SLA Management](./README.md) · [All topics](../README.md)
