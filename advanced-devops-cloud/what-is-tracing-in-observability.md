---
title: "What is Tracing in Observability?"
id: 154
category: "Advanced DevOps & Cloud"
difficulty: "Intermediate"
tags:
  - devops
  - advanced-devops-cloud
  - interview-questions
---

# What is Tracing in Observability?

**Short answer:** Distributed tracing follows a single request across every service it touches, recording each operation as a timed span, so you can see exactly where time was spent and where a failure occurred in a distributed system.

## Detail

**Model**

- A **trace** represents one end-to-end request, identified by a `trace_id`.
- A **span** is one unit of work within it - an HTTP handler, a database query, a queue publish - with a start time, duration, status, parent span, and arbitrary attributes.
- **Context propagation** carries the trace and span IDs across process boundaries, using the W3C `traceparent` header for HTTP and message headers for asynchronous flows.

**What it answers that logs and metrics cannot:** which of the twelve services in this request path is slow; whether latency is in the service, the database, or the network; how errors cascade through dependencies; and what the actual service dependency graph looks like in production, as opposed to the architecture diagram.

**Sampling.** Tracing every request at scale is prohibitively expensive.

- **Head-based** - the decision is made at the start, propagated through the trace. Cheap and simple, but you may discard the rare failing request.
- **Tail-based** - buffer the complete trace, then decide. Lets you keep 100% of errors and slow requests while sampling the boring ones. More useful, and considerably more infrastructure.

**Practices:** instrument with OpenTelemetry rather than a vendor SDK; propagate context through asynchronous boundaries (queues and background jobs are where propagation usually breaks); add business attributes such as tenant, user tier, and feature-flag state to spans, which is what makes traces answer product-shaped questions; and include `trace_id` in every log line so a trace links directly to its logs.

## Example

```text
trace_id=b7e1  ├─ gateway            240ms
               │  ├─ auth-service     12ms
               │  └─ checkout        225ms
               │     ├─ inventory     18ms
               │     ├─ pricing        9ms
               │     └─ payments     190ms   ← the actual problem
               │        └─ stripe-api 185ms
```

## Interview tips

- Head-based versus tail-based sampling is the depth question - know why tail-based is preferable and costlier.
- Context propagation across queues is the most common real-world instrumentation gap.
- Adding business attributes to spans is what elevates tracing from debugging to product insight.

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
