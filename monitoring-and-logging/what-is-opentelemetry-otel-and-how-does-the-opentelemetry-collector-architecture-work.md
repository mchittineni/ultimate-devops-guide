---
title: "What is OpenTelemetry (OTel) and how does the OpenTelemetry Collector architecture work?"
id: 558
category: "Monitoring and Logging"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - monitoring-and-logging
  - opentelemetry
  - otel
  - tracing
  - collector
quiz:
  stem: "Which component of an OpenTelemetry Collector pipeline is responsible for scrubbing personally identifiable information (PII) before telemetry leaves the cluster?"
  options:
    - "The Receiver"
    - "The Processor"
    - "The Exporter"
    - "The DNS resolver"
  answer: 2
  explanation: "Processors sit between Receivers and Exporters in the OTel pipeline, transforming, filtering, batching, and redacting sensitive PII from telemetry data."
---

# What is OpenTelemetry (OTel) and how does the OpenTelemetry Collector architecture work?

**Short answer:** OpenTelemetry is a vendor-neutral CNCF framework providing unified APIs, SDKs, and tooling for telemetry data; the OTel Collector is a proxy pipeline composed of Receivers, Processors, and Exporters that ingests, transforms, and routes telemetry to multiple backends.

## Detail

Before OpenTelemetry, applications had to embed vendor-specific libraries (Datadog agent, New Relic SDK, Jaeger client). Changing backends required rewriting application instrumentation. OpenTelemetry (formed in 2019 from the merger of OpenTracing and OpenCensus) splits the problem into an **API** (what libraries call), an **SDK** (sampling, batching, export), the **OTLP** wire protocol, **semantic conventions** (standard attribute names such as `service.name` and `http.response.status_code`), and the **Collector**.

**Signal maturity** is a common follow-up: traces, metrics, and logs are stable in the specification and OTLP, though SDK maturity still varies by language (logs in particular usually flow through a bridge from existing loggers such as Log4j or Python `logging`, rather than a new logging API). **Profiles** are the fourth signal and entered public alpha in 2026 - fine to evaluate, not yet something to bet production on.

### The OTel Collector Architecture

```text
[Apps (OTLP)] ──> [Receivers] ──> [Processors] ──> [Exporters] ──> [Backends (Prometheus, Jaeger, CloudWatch)]
```

1. **Receivers**: Ingests telemetry across diverse protocols (OTLP, Jaeger, Zipkin, Prometheus pull/push).
2. **Processors**: Transforms, scrubs, and batches data in memory:
   - `batch`: Groups telemetry into efficient chunked network requests.
   - `memory_limiter`: Drops data or applies backpressure if collector RAM reaches limits.
   - `redaction`: Scrubs PII (passwords, credit card numbers, auth tokens) before egress.
3. **Exporters**: Translates internal telemetry models and sends data to downstream backends (Honeycomb, Tempo, Grafana Cloud, Datadog). Jaeger v2 is itself built on the Collector and ingests OTLP natively, so the old Jaeger-specific exporter is no longer needed.
4. **Connectors and extensions**: connectors join pipelines (e.g. `spanmetrics` turns traces into RED metrics); extensions add health checks, authentication, and `zpages`.

### Deployment Patterns

- **Agent** (DaemonSet or sidecar next to the app): cheap local hop, adds host/Kubernetes metadata.
- **Gateway** (a central, horizontally scaled Deployment): tail sampling, redaction, and routing in one place.
- **Distributions**: `otelcol` (core components) and `otelcol-contrib` (everything, including `redaction` and `tail_sampling`); production teams often build a minimal distribution with the OpenTelemetry Collector Builder (`ocb`).

The trade-off: the Collector becomes a critical part of the telemetry path, so it needs its own resource limits, monitoring, and queue/retry settings - otherwise a backend outage turns into dropped telemetry or an OOM-killed collector.

## Example

```yaml
# otelcol-contrib gateway: receive OTLP, protect memory, scrub PII, batch, export
receivers:
  otlp:
    protocols:
      grpc: { endpoint: 0.0.0.0:4317 } # recent Collectors default to localhost; bind explicitly
      http: { endpoint: 0.0.0.0:4318 }
processors:
  memory_limiter: { check_interval: 1s, limit_percentage: 80, spike_limit_percentage: 20 }
  redaction:
    allow_all_keys: true
    blocked_values: ["[0-9]{13,16}"] # card-number-shaped values are masked
  batch: {}
exporters:
  otlp_grpc/tempo: # named `otlp` before Collector v0.144; the old name is a deprecated alias
    endpoint: tempo:4317
    tls: { insecure: true }
  prometheusremotewrite:
    endpoint: http://mimir:9009/api/v1/push
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, redaction, batch]
      exporters: [otlp_grpc/tempo]
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheusremotewrite]
```

The HTTP exporter was renamed the same way (`otlphttp` -> `otlp_http`); older configs still load but log a deprecation warning.

## Interview tips

- Frame the value precisely: OTel removes lock-in at the instrumentation layer; you still choose (and pay for) a backend.
- Processor order matters: `memory_limiter` first, then filtering/redaction, then batching, so you refuse load before spending memory on it.
- Tail sampling needs every span of a trace on the same Collector instance, which is why it runs in a gateway tier behind a trace-ID-aware load balancer (the `loadbalancing` exporter).
- Know the alternatives that wrap the Collector: Grafana Alloy and vendor distributions are Collector-based, so the same pipeline concepts apply.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you add monitoring to an application that has none?]] (`#433`): [How do you add monitoring to an application that has none?](../infrastructure-monitoring/how-do-you-add-monitoring-to-an-application-that-has-none.md)
- [[What is Application Performance Monitoring?]] (`#134`): [What is Application Performance Monitoring?](../infrastructure-monitoring/what-is-application-performance-monitoring.md)
- [[What is Log Management?]] (`#135`): [What is Log Management?](../infrastructure-monitoring/what-is-log-management.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Monitoring and Logging](./README.md) · [All topics](../README.md)
