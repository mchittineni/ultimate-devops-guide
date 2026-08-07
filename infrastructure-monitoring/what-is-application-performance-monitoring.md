---
title: "What is Application Performance Monitoring?"
id: 134
category: "Infrastructure Monitoring"
difficulty: "Intermediate"
tags:
  - devops
  - infrastructure-monitoring
  - interview-questions
---

# What is Application Performance Monitoring?

**Short answer:** APM instruments applications to measure their internal behaviour - request latency broken down by code path, database and external call timings, error rates, and traces - so you can find _why_ a service is slow, not merely that it is.

## Detail

**What APM provides beyond infrastructure metrics**

- **Distributed tracing** - the full path of a request across services, with per-span timings that immediately reveal which hop is slow.
- **Transaction breakdown** - time spent in application code, database queries, cache, and external HTTP calls.
- **Database insight** - the specific slow query, with its call site in the code.
- **Error tracking** - grouped exceptions with stack traces, release attribution, and affected-user counts.
- **Runtime metrics** - garbage collection pauses, heap use, thread and connection pool saturation.
- **Continuous profiling** - CPU and memory flame graphs from production, pinpointing hot functions.
- **Real user monitoring** - actual browser and mobile performance, including Core Web Vitals.

**How it is instrumented.** Auto-instrumentation agents attach to the runtime and instrument common frameworks with no code change; manual instrumentation with the OpenTelemetry SDK adds spans and attributes for business-specific operations. In practice you use both.

**Sampling matters at scale.** Head-based sampling decides at the start of a trace (cheap, may miss rare errors); tail-based sampling decides after the trace completes, so you can keep all errors and slow requests while sampling successful fast ones. Tail sampling is more useful and more expensive to run.

**Getting value from it:** propagate a correlation ID through every service and into logs, tag spans with release version and tenant, and connect trace exemplars to your metrics dashboards so a latency spike is one click from an example trace.

## Interview tips

- Tail-based versus head-based sampling is the depth question here - know the trade-off.
- OpenTelemetry as the instrumentation standard is the modern answer.
- The workflow - alert → dashboard → trace → log line - demonstrates how you actually debug.

---

[⬅ Back to Infrastructure Monitoring](./README.md) · [All topics](../README.md)
