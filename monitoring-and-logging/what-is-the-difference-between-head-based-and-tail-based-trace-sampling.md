---
title: "What is the difference between head-based and tail-based trace sampling?"
id: 770
category: "Monitoring and Logging"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - monitoring-and-logging
  - tracing
  - sampling
  - opentelemetry
quiz:
  stem: "Why must tail-based sampling in the OpenTelemetry Collector run behind a trace-ID-aware load balancer when there are several Collector replicas?"
  options:
    - "Because tail sampling only works over UDP"
    - "Because the sampling decision needs every span of a trace, so all spans with the same trace ID must reach the same Collector instance"
    - "Because the load balancer encrypts the spans before sampling"
    - "Because head-based sampling has already discarded the trace ID"
  answer: 2
  explanation: "Tail sampling buffers a trace and decides after seeing all of its spans. If spans are spread across replicas, each sees a partial trace and makes an inconsistent decision, so a first tier routes by trace ID (the loadbalancing exporter) to the sampling tier."
---

# What is the difference between head-based and tail-based trace sampling?

**Short answer:** **Head-based sampling** decides whether to keep a trace when it starts, at the root span, and propagates that decision downstream in the `traceparent` sampled flag - cheap and simple, but blind: it keeps 10% of traces whether or not they contain the error you care about. **Tail-based sampling** buffers all spans of a trace and decides after it completes, so it can keep every error and every slow trace while sampling the boring successes - far more useful, but it needs memory, a buffering delay, and every span of a trace routed to the same collector. Most production setups combine them: light head sampling (or none) in the SDKs, tail sampling in a Collector gateway, and metrics computed from spans before any sampling so dashboards stay accurate.

## Detail

### Head-based sampling

- The root service's sampler decides, typically `ParentBased(TraceIdRatioBased(0.1))`: new traces are kept with 10% probability, and every downstream service follows its parent's decision, so traces stay complete.
- Because the decision is a function of the trace ID, every service that makes its own decision reaches the same answer for the same trace.
- **Strengths:** near-zero cost, no buffering, unsampled spans are never even exported.
- **Weakness:** the decision is made before anything interesting has happened. A 0.1% error path sampled at 10% leaves you with almost no error traces.

### Tail-based sampling

- A Collector (the `tail_sampling` processor in `otelcol-contrib`) holds spans in memory for `decision_wait` (for example 10 seconds), groups them by trace ID, then applies policies: keep if any span has status ERROR, keep if duration exceeds a threshold, keep specific routes or tenants, keep a probabilistic remainder, and rate-limit the total.
- **Strengths:** keeps the traces that matter; sampling policy is central, so it changes without redeploying applications.
- **Costs and limits:**
  - **Routing:** with several Collector replicas, all spans of a trace must reach the same one, so you run two tiers - a load-balancing tier using the `loadbalancing` exporter with `routing_key: traceID`, then the sampling tier.
  - **Memory:** buffered traces x decision window; `num_traces` caps it, and when it is exceeded the oldest traces are dropped.
  - **Late spans:** spans arriving after the decision (long async work) are handled by cached decisions, but very long traces are often split at queue boundaries and linked instead.
  - **Egress before sampling:** every span leaves the application, so network and Collector CPU scale with full traffic.

### Getting the numbers right

- **Compute RED metrics before sampling.** Use the `spanmetrics` connector (or application metrics) on the unsampled stream; metrics derived from kept traces over-represent errors and slow requests by design.
- **Adjusted counts.** A trace kept at 1% represents 100 traces. Backends that understand sampling probability can extrapolate counts; otherwise treat sampled traces as examples, not as a population.
- **Consistent probability sampling** in recent OpenTelemetry specifications records the sampling threshold in `tracestate`, so mixed samplers across services can still produce complete traces and correct estimates.

|                                  | Head-based                   | Tail-based                                           |
| -------------------------------- | ---------------------------- | ---------------------------------------------------- |
| Decision point                   | Root span, at start          | After the trace completes, in a Collector            |
| Keeps all errors and slow traces | No                           | Yes, by policy                                       |
| Cost                             | Minimal                      | Memory, CPU, and full-volume egress to the Collector |
| Complexity                       | One env var                  | Two Collector tiers, capacity planning               |
| Change policy                    | Redeploy or reconfigure SDKs | Change Collector config centrally                    |

## Example

```bash
# Head-based sampling in any OpenTelemetry SDK: 10% of new traces, children follow parents
export OTEL_TRACES_SAMPLER=parentbased_traceidratio
export OTEL_TRACES_SAMPLER_ARG=0.1
```

```yaml
# Tier 1 (otelcol-contrib, e.g. a DaemonSet or Deployment): route every span of a trace to one sampler
exporters:
  loadbalancing:
    routing_key: traceID
    protocol:
      otlp:
        tls: { insecure: true }
    resolver:
      dns: { hostname: otel-sampler-headless.observability.svc.cluster.local }
---
# Tier 2 (otelcol-contrib): buffer, then keep errors, slow traces, and 5% of the rest
processors:
  tail_sampling:
    decision_wait: 10s
    num_traces: 100000
    policies:
      - { name: errors, type: status_code, status_code: { status_codes: [ERROR] } }
      - { name: slow, type: latency, latency: { threshold_ms: 1000 } }
      - { name: baseline, type: probabilistic, probabilistic: { sampling_percentage: 5 } }
```

A trace is kept if any policy matches, so this keeps 100% of failed and slow traces plus a 5% baseline of healthy ones for comparison.

## Interview tips

- Define both by when the decision is made, then give the consequence: head sampling is cheap but random; tail sampling sees the outcome but must buffer.
- Explain why head sampling keeps traces complete (parent-based decisions propagated in `traceparent`), and why tail sampling needs trace-ID-aware routing across Collector replicas.
- Say "compute metrics before sampling" - sampled traces are biased towards errors and latency, so they are examples, not statistics.
- Size it: memory = traces per second x decision window x average trace size; mention `num_traces` and watching the Collector's dropped-span metrics.
- Expect "what would you run?": head sampling at 100% (or high) in the SDKs for low-volume services, tail sampling in a gateway for the busy ones, with a rate limit as a cost backstop.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you add monitoring to an application that has none?]] (`#433`): [How do you add monitoring to an application that has none?](../infrastructure-monitoring/how-do-you-add-monitoring-to-an-application-that-has-none.md)
- [[What is Application Performance Monitoring?]] (`#134`): [What is Application Performance Monitoring?](../infrastructure-monitoring/what-is-application-performance-monitoring.md)
- [[What is Site Reliability Engineering?]] (`#96`): [What is Site Reliability Engineering?](../site-reliability-engineering/what-is-site-reliability-engineering.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Monitoring and Logging](./README.md) · [All topics](../README.md)
