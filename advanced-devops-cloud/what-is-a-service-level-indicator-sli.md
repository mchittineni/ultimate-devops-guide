---
title: "What is a Service Level Indicator (SLI)?"
id: 150
category: "Advanced DevOps & Cloud"
difficulty: "Beginner"
tags:
  - devops
  - advanced-devops-cloud
  - interview-questions
---

# What is a Service Level Indicator (SLI)?

**Short answer:** An SLI is the quantitative measurement underpinning an SLO — typically the ratio of good events to valid events — chosen to reflect what users actually experience.

## Detail

**The standard form:** `good events / valid events`. This ratio is preferred over raw gauges because it is bounded between 0 and 1, aggregates cleanly across time windows, and converts directly into an error budget.

**The main SLI types**

- **Availability** — successful responses / all valid responses.
- **Latency** — responses faster than a threshold / all responses. Expressed as a proportion, not an average.
- **Throughput** — where a minimum service rate is the commitment.
- **Freshness** — data updated within a threshold / all data (pipelines, caches, replicas).
- **Correctness** — records processed correctly / all records.
- **Coverage** — items successfully processed / items that should have been processed.

**Design decisions that determine whether the SLI is meaningful**

- **Where you measure.** Closer to the user is better. Load balancer metrics capture failures the application never observes; client-side or synthetic monitoring captures DNS and network problems too.
- **What counts as valid.** Usually exclude 4xx client errors and health-check traffic — but a 429 from your own rate limiter or a 400 caused by your own broken API version arguably counts against you. Document the decision.
- **How you bucket latency.** Prometheus histogram buckets must include your threshold, or the SLI cannot be computed accurately.

**Start small.** One availability SLI and one latency SLI per critical journey is a complete, useful starting point. Precision in defining two indicators beats vagueness across twenty.

## Interview tips

- The good/valid ratio phrasing is the canonical SRE formulation — use it.
- Latency as "proportion under a threshold" rather than a percentile is a subtle differentiator.
- Discuss the measurement point; measuring inside the application misses whole categories of user-visible failure.

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
