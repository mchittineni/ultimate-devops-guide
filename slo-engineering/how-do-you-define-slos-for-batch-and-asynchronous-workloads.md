---
title: "How do you define SLOs for batch and asynchronous workloads?"
id: 181
category: "SLO Engineering"
difficulty: "Advanced"
tags:
  - devops
  - slo-engineering
  - interview-questions
---

# How do you define SLOs for batch and asynchronous workloads?

**Short answer:** Request-based availability does not apply, so measure the properties users actually depend on: freshness (how stale is the output), coverage (what fraction of input was processed), correctness, and completion within a deadline. Each becomes a good-events ratio over a window — for example "99% of hourly runs publish data less than 90 minutes old".

## Detail

**The four SLI types for data and async systems:**

| SLI type    | Question it answers                     | Example target                          |
| ----------- | --------------------------------------- | --------------------------------------- |
| Freshness   | How old is the newest usable output?    | 99% of hours, data < 90 min old         |
| Coverage    | What share of records were processed?   | 99.9% of events processed per day       |
| Correctness | Did the output pass validation?         | 99.99% of rows pass schema/range checks |
| Timeliness  | Did the job finish inside its deadline? | 99% of runs finish by 06:00 UTC         |

**Queues need consumer-lag SLIs, not uptime.** For an event-driven service, the user-visible property is end-to-end latency from event publication to effect. Measure the age of the oldest unprocessed message (consumer lag in time, not message count — count means nothing without throughput), and set the SLO as "95% of the time, oldest unacknowledged message is under 60 seconds".

**Count the run, not the request.** With one run per hour, a monthly window contains roughly 720 events, so a single failed run costs 0.14% — enough that 99.9% is unachievable. Choose targets the event count can express: with 720 runs, 99% means about 7 permitted failures.

**Retries change the definition of failure.** If a job succeeds on its second attempt within the deadline, most users do not care. Define whether the SLI counts attempts or outcomes; usually outcome-within-deadline is the honest choice, with retry volume tracked separately as a health signal.

**Idempotency and duplicates.** At-least-once delivery means duplicates, so correctness SLIs should measure the state after deduplication rather than the raw stream, and the pipeline must be idempotent for the SLI to be meaningful at all.

**Watch out for the silent-success failure mode.** A job that completes successfully having processed zero rows satisfies a naive timeliness SLI. Pair timeliness with coverage or a row-count assertion, or the SLO will be green during an outage.

## Example

```promql
# Freshness SLI: fraction of 5-minute samples where the warehouse table is < 90 min stale
avg_over_time(
  (
    (time() - dataset_last_success_timestamp_seconds{dataset="orders_hourly"}) < bool 5400
  )[28d:5m]
)
```

```promql
# Queue timeliness: age of the oldest unprocessed message, the SLI that matters for async
max(kafka_consumergroup_lag_seconds{group="fulfilment"})
```

## Interview tips

- Naming freshness, coverage, correctness, and timeliness immediately shows you have read beyond the availability-and-latency basics.
- "Consumer lag in seconds, not messages" is a small detail that reliably impresses.
- Expect: "a nightly job failed once — did you breach?" Work the event-count arithmetic out loud; it is the real test.

---

[⬅ Back to SLO Engineering](./README.md) · [All topics](../README.md)
