---
title: "What are the Three Pillars of Observability and where do their operational boundaries blur?"
id: 556
category: "Monitoring and Logging"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - monitoring-and-logging
  - observability
  - metrics
  - logs
  - traces
  - opentelemetry
quiz:
  stem: "How does modern OpenTelemetry correlate distributed traces with application logs?"
  options:
    - "By sorting both logs and traces in alphabetical order"
    - "By injecting active `TraceID` and `SpanID` metadata into structured log messages"
    - "By storing all application logs inside etcd"
    - "By converting all log messages into Prometheus histograms"
  answer: 2
  explanation: "Injecting the current TraceID and SpanID into structured application logs allows operators to jump directly from a failing trace span to the exact corresponding log entries."
---

# What are the Three Pillars of Observability and where do their operational boundaries blur?

**Short answer:** Metrics (aggregated numerical time-series), Logs (timestamped discrete event records), and Traces (end-to-end request journeys across distributed services); modern OpenTelemetry unifies them via shared trace and span context.

## Detail

Traditional monitoring was siloed into independent dashboards, log searchers, and APMs:

### The Three Pillars

1. **Metrics**: Low overhead, numeric time-series data aggregated over intervals (CPU %, HTTP request rate). Excellent for alerting and detecting _that_ a system is failing.
2. **Logs**: Detailed text or structured JSON lines capturing individual events. Crucial for understanding _why_ a specific transaction failed, but expensive to store and index at petabyte scale.
3. **Traces**: Follows a specific request as it hops across distributed microservices via context propagation (W3C traceparent headers), measuring latency at each span. Essential for pinpointing distributed bottlenecks.

### Correlating Pillars with OpenTelemetry

Modern observability connects these via correlation:

- A metric spike alerts on elevated error rates.
- The alert links to distributed traces exhibiting high latency.
- The trace's span ID correlates directly with structured log lines emitted during that exact request execution.

### Where the Boundaries Blur

- **Exemplars** attach a sample trace ID to a metric data point, so a latency spike on a graph links to a real slow request.
- **Metrics from traces and logs**: span metrics (RED metrics generated from spans) and log-derived metrics mean one signal is often computed from another.
- **Wide events**: a structured log line with many attributes per request is, functionally, a span - which is why some tools store them the same way.
- **Profiles** are increasingly treated as a fourth signal; OpenTelemetry's profiles signal entered public alpha in 2026 (traces, metrics, and logs are stable), and continuous profilers such as Grafana Pyroscope, Parca, and the eBPF-based OpenTelemetry profiling agent already link flame graphs to spans.

The limitation of the "three pillars" framing is that it encourages three separate tools and three bills; the value is in the correlation, not in having all three.

## Example

```python
# Python: put the active trace and span IDs on every log line so logs and traces join up
import logging
from opentelemetry import trace

class TraceContextFilter(logging.Filter):
    def filter(self, record):
        ctx = trace.get_current_span().get_span_context()
        record.trace_id = format(ctx.trace_id, "032x") if ctx.is_valid else ""
        record.span_id = format(ctx.span_id, "016x") if ctx.is_valid else ""
        return True

handler = logging.StreamHandler()
handler.addFilter(TraceContextFilter())
handler.setFormatter(logging.Formatter(
    '{"ts":"%(asctime)s","level":"%(levelname)s","trace_id":"%(trace_id)s",'
    '"span_id":"%(span_id)s","msg":"%(message)s"}'))
logging.getLogger().addHandler(handler)
```

The OpenTelemetry logging instrumentation (`opentelemetry-instrumentation-logging`) can inject the same fields automatically.

## Interview tips

- Metrics for detection/alerting; traces for localising the failing hop; logs for root-cause context. Say how you move between them, not just what they are.
- Cost profile differs: metrics are cheap per request because they aggregate; logs and traces cost per event, which is why traces are sampled and logs are filtered.
- Correlation is the real answer: TraceID/SpanID in every log line, exemplars on latency histograms, and shared resource attributes (`service.name`, `k8s.pod.name`) across all signals.
- If the interviewer pushes on "pillars", mention the critique: observability is the ability to ask new questions of high-cardinality data, not owning three tools.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you add monitoring to an application that has none?]] (`#433`): [How do you add monitoring to an application that has none?](../infrastructure-monitoring/how-do-you-add-monitoring-to-an-application-that-has-none.md)
- [[What are Monitoring Tools?]] (`#132`): [What are Monitoring Tools?](../infrastructure-monitoring/what-are-monitoring-tools.md)
- [[What are Monitoring Best Practices?]] (`#133`): [What are Monitoring Best Practices?](../infrastructure-monitoring/what-are-monitoring-best-practices.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Monitoring and Logging](./README.md) · [All topics](../README.md)
