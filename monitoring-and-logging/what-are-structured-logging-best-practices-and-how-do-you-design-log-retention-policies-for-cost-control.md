---
title: "What are structured logging best practices and how do you design log retention policies for cost control?"
id: 561
category: "Monitoring and Logging"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - logging
  - json
  - retention
  - elasticsearch
  - loki
quiz:
  stem: "Which filtering practice yields the highest log volume reduction in high-scale Kubernetes clusters without impacting incident debugging?"
  options:
    - "Deleting all error logs immediately after generation"
    - "Dropping routine HTTP 200 health-check probe logs (`/healthz`) at the node logging agent"
    - "Converting all JSON logs into XML"
    - "Restricting logging access to senior managers only"
  answer: 2
  explanation: "Health check probes from Kubernetes readiness and liveness checks execute every few seconds across thousands of pods, generating up to 60% of total cluster log volume with zero diagnostic value."
---

# What are structured logging best practices and how do you design log retention policies for cost control?

**Short answer:** Structured logging formats events as JSON with standard key-value metadata (timestamp, level, service, trace_id, environment); cost-effective retention uses hot/warm/cold tiering, aggressive sampling of 200 OKs, and short retention periods for debug logs.

## Detail

Unstructured plain text logs (`2026-09-23 error happened in db`) require expensive regex parsing (Logstash/Fluentd grok filters) that degrades pipeline performance and breaks silently when string formatting changes.

### Structured JSON Logging

```json
{
  "timestamp": "2026-09-23T20:15:30.124Z",
  "level": "ERROR",
  "service": "checkout-service",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "message": "payment gateway timeout",
  "http_status": 504,
  "user_id": "usr_99182"
}
```

### Log Lifecycle & Cost Optimization

1. **Log Level Hygiene**: Never run `DEBUG` logging in production indefinitely; use dynamic log level adjustments.
2. **Tiered Storage**:
   - **Hot Tier (NVMe/SSD)**: Last 7 days for real-time investigation.
   - **Warm Tier (HDD/Standard)**: Days 8-30 for historical debugging.
   - **Cold / Glacier Tier (Object Storage S3/GCS)**: Compressed raw archives for 1-7 years for regulatory compliance.
3. **Drop or Sample Repetitive Success Logs**: In high-throughput services, drop health-check endpoint logs (`/healthz`) at the collector agent before ingestion.
4. **Keep Sensitive Data Out**: The `user_id` above is a pseudonymous ID, not an email; never log tokens, passwords, or full request bodies. Redact at the source, with collector-side redaction as a safety net.

**Trade-off.** Retention cuts are irreversible: the 30-day log you deleted is the one a security investigation needs on day 45. Decide retention per log class (debug, access, audit) with security and compliance, rather than one global number chosen for cost.

## Example

```yaml
# Loki 3.x: 31-day default retention, 24 h for debug streams (retention is applied by the compactor)
compactor:
  working_directory: /var/loki/compactor
  retention_enabled: true
  delete_request_store: s3
limits_config:
  retention_period: 744h
  retention_stream:
    - selector: '{level="debug"}'
      priority: 1
      period: 24h
    - selector: '{namespace="payments", log_class="audit"}'
      priority: 2
      period: 8760h # audit streams kept a year here; long-term archive lives elsewhere
```

## Interview tips

- Structured JSON eliminating regex parsing fragility.
- Standard metadata fields (timestamp, level, service, trace_id).
- Dropping health checks and debug logs before transmission.
- Hot, warm, cold storage tiering to object storage for cost reduction.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are Monitoring Tools?]] (`#132`): [What are Monitoring Tools?](../infrastructure-monitoring/what-are-monitoring-tools.md)
- [[What are Monitoring Best Practices?]] (`#133`): [What are Monitoring Best Practices?](../infrastructure-monitoring/what-are-monitoring-best-practices.md)
- [[What is Application Performance Monitoring?]] (`#134`): [What is Application Performance Monitoring?](../infrastructure-monitoring/what-is-application-performance-monitoring.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Monitoring and Logging](./README.md) · [All topics](../README.md)
