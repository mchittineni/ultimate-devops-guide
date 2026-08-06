---
title: "What is Error Budget?"
id: 99
category: "Site Reliability Engineering (SRE)"
difficulty: "Intermediate"
tags:
  - devops
  - site-reliability-engineering-sre
  - interview-questions
---

# What is Error Budget?

**Short answer:** The error budget is the amount of unreliability an SLO permits — `1 − SLO` over the window. It converts reliability from an argument into an accounting exercise: while budget remains, ship; when it is spent, fix.

## Detail

**The arithmetic.** A 99.9% availability SLO over 30 days allows 0.1% failure — 43.2 minutes of downtime, or 0.1% of requests failing. If you serve 100 million requests a month, that is 100,000 permitted failures.

| SLO    | Error budget / 30 days |
| ------ | ---------------------- |
| 99%    | 7.2 hours              |
| 99.5%  | 3.6 hours              |
| 99.9%  | 43.2 minutes           |
| 99.95% | 21.6 minutes           |
| 99.99% | 4.3 minutes            |

**The policy is what makes it work.** Agreed in advance by engineering, product, and leadership:

- **Budget remaining** — normal feature velocity, and risky experiments are permitted.
- **Budget nearly exhausted** — increased caution: more canary time, no risky migrations.
- **Budget exhausted** — reliability work takes priority over features until the budget recovers.

Without an agreed consequence, the error budget is just a dashboard.

**Burn rate** is the multiplier at which you are consuming the budget: burning at 1× exactly exhausts it over the window; at 14.4× you exhaust a 30-day budget in about two days. Alerting on burn rate over multiple windows catches both sudden outages and slow degradation, with far fewer false pages than static thresholds.

**Planned consumption.** Budget can be spent deliberately — on a risky migration, a load test in production, or a chaos experiment. That is a feature, not an abuse: unspent budget suggests the SLO is too loose or the team is over-investing in reliability.

## Interview tips

- The policy — the agreed consequence of exhaustion — is the answer that distinguishes real practice from theory.
- Multi-window burn-rate alerting is the implementation detail to name.
- "Consistently unspent budget means the target is wrong" is a nuanced point that lands well.

---

[⬅ Back to Site Reliability Engineering (SRE)](./README.md) · [All topics](../README.md)
