---
title: "What is Mean Time to Recovery (MTTR)?"
id: 102
category: "DevOps Metrics and KPIs"
difficulty: "Beginner"
tags:
  - devops
  - devops-metrics-and-kpis
  - interview-questions
---

# What is Mean Time to Recovery (MTTR)?

**Short answer:** MTTR is the average time from the start of a service-affecting incident to full restoration. It measures how quickly you recover rather than how rarely you fail — and it is usually the more improvable of the two.

## Detail

**The family of related measures**, which are frequently confused:

- **MTTD** — mean time to _detect_: incident begins → monitoring notices.
- **MTTA** — mean time to _acknowledge_: alert fires → a human responds.
- **MTTR** — mean time to _recover/restore_: incident begins → service restored. (Sometimes "repair", which is narrower.)
- **MTBF** — mean time _between_ failures: reliability of the component.

For distributed systems, MTTR usually matters more than MTBF. Failures are inevitable; the differentiator is how fast you notice and recover.

**What drives it down**

- **Detection** — good alerting on user-facing symptoms, with SLO burn-rate alerts instead of noisy thresholds.
- **Diagnosis** — observability that lets you find the cause quickly: traces, correlated logs, and deploy annotations answering "what changed?"
- **Recovery** — one-command rollback, feature flags to disable the offending behaviour instantly, and runbooks for known failure modes.
- **Process** — clear on-call ownership, an incident commander role, and rehearsed escalation.

**Measure it honestly.** Use the mean _and_ the distribution — a single 12-hour incident distorts an average built from twenty 5-minute ones. Report the median and p90 alongside, and segment by severity.

**The fastest single win** in most organisations is making rollback trivial and rehearsed. If the first action for any incident can be "revert the last deploy", recovery time collapses.

## Interview tips

- Distinguish MTTD/MTTA/MTTR/MTBF clearly — the acronym soup is the usual test.
- "Optimise for recovery, not just prevention" is the mature framing.
- Mention reporting distribution rather than mean alone; it shows statistical care.

---

[⬅ Back to DevOps Metrics and KPIs](./README.md) · [All topics](../README.md)
