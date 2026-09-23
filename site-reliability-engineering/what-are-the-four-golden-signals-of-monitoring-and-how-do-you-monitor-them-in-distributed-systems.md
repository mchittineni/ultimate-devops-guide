---
title: "What are the Four Golden Signals of Monitoring and how do you monitor them in distributed systems?"
id: 644
category: "Site Reliability Engineering (SRE)"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - sre
  - monitoring
  - golden-signals
  - prometheus
quiz:
  stem: "Which of Google's Four Golden Signals measures the fraction of constrained system resources currently in use (such as thread pool queues or memory headroom)?"
  options:
    - "Latency"
    - "Traffic"
    - "Errors"
    - "Saturation"
  answer: 4
  explanation: "Saturation measures how full the most constrained system resource is, providing early warning before memory exhaustion or thread queue overflows degrade user experience."
---

# What are the Four Golden Signals of Monitoring and how do you monitor them in distributed systems?

**Short answer:** The Four Golden Signals are Latency (time to service a request), Traffic (demand on the system), Errors (rate of failed requests), and Saturation (how full the most constrained resource is); together they provide high-fidelity visibility into user experience and system capacity.

## Detail

Google SRE established the Four Golden Signals as the core telemetry foundation for any user-facing service:

### The Signals Defined

1. **Latency**: The time it takes to service a request.
   - Crucial rule: **Differentiate success latency from failure latency!** A failing 500 error returning in 2ms should not artificially lower your perceived p95 response time.
2. **Traffic**: A measure of how much demand is being placed on your system.
   - HTTP requests per second for web services; concurrent network sessions or I/O rate for databases.
3. **Errors**: The rate of requests that fail.
   - Explicit failures (HTTP 500s) and implicit failures (HTTP 200 containing 'Empty payload' or incorrect content).
4. **Saturation**: How 'full' your service is, measuring the most constrained hardware or software resource.
   - CPU % on compute nodes; connection pool queue depth; memory pressure; disk IOPS limits.

**In a distributed system, measure them per service and per dependency.** Each service exposes its own RED metrics (rate, errors, duration) from its server-side instrumentation or the mesh/gateway in front of it, and client-side metrics for every outbound call, so a slow dependency shows up as latency in the caller as well as in the callee. Traces then connect the signals across hops. The limitation: the golden signals tell you _that_ a service is unhealthy, not _why_ - saturation in particular is service-specific (a thread pool, a Kafka partition, a database connection pool) and has to be chosen deliberately rather than defaulted to CPU.

## Example

```promql
# Latency: p99 of successful requests only, so fast failures do not flatter it
histogram_quantile(0.99,
  sum by (le, service) (rate(http_server_request_duration_seconds_bucket{http_response_status_code!~"5.."}[5m])))

# Traffic: requests per second per service
sum by (service) (rate(http_server_request_duration_seconds_count[5m]))

# Errors: fraction of requests returning 5xx
sum by (service) (rate(http_server_request_duration_seconds_count{http_response_status_code=~"5.."}[5m]))
  / sum by (service) (rate(http_server_request_duration_seconds_count[5m]))

# Saturation: a resource that actually queues - here, DB connection pool usage
max by (service) (db_client_connections_usage{state="used"} / db_client_connections_max)
```

Metric names follow the OpenTelemetry HTTP and database semantic conventions as exported to Prometheus; adjust them to whatever your instrumentation emits.

## Interview tips

- Listing all four signals: Latency, Traffic, Errors, Saturation.
- Separating error latency from successful request latency.
- Saturation measuring capacity constraints before failure occurs.
- Mapping signals to PromQL queries.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are Incident Severity Levels (Sev-1 to Sev-4) and how do they govern response SLAs and war rooms?]] (`#675`): [What are Incident Severity Levels (Sev-1 to Sev-4) and how do they govern response SLAs and war rooms?](../incident-management/what-are-incident-severity-levels-sev-1-to-sev-4-and-how-do-they-govern-response-slas-and-war-rooms.md)
- [[How do you choose an SLO target?]] (`#177`): [How do you choose an SLO target?](../slo-engineering/how-do-you-choose-an-slo-target.md)
- [[How do you measure a latency SLI correctly?]] (`#179`): [How do you measure a latency SLI correctly?](../slo-engineering/how-do-you-measure-a-latency-sli-correctly.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Site Reliability Engineering (SRE)](./README.md) · [All topics](../README.md)
