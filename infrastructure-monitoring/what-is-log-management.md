---
title: "What is Log Management?"
id: 135
category: "Infrastructure Monitoring"
difficulty: "Intermediate"
tags:
  - devops
  - infrastructure-monitoring
  - interview-questions
---

# What is Log Management?

**Short answer:** Log management is the pipeline that collects, parses, enriches, stores, indexes, and expires log data from across a system, making it searchable for debugging, auditing, and security investigation.

## Detail

**The pipeline**

1. **Generate** - applications write structured JSON to stdout, including a timestamp, level, service, version, and correlation/trace ID.
2. **Collect** - an agent (Fluent Bit, Vector, Promtail) reads container or file output, typically as a DaemonSet in Kubernetes.
3. **Buffer** - Kafka or a disk buffer absorbs spikes and protects against downstream outages.
4. **Process** - parse, enrich with Kubernetes metadata, redact sensitive fields, drop noise, and sample high-volume debug lines.
5. **Store and index** - Elasticsearch/OpenSearch (full-text indexing, powerful, expensive) or Loki (indexes labels only, cheap, requires more disciplined labelling).
6. **Query and visualise** - Kibana or Grafana.
7. **Retain and expire** - lifecycle policies moving data to cheaper tiers and deleting on schedule.

**Practices that matter**

- **Structured logging.** JSON with consistent field names removes the need for fragile parsing and makes queries reliable.
- **Correlation IDs** on every line, propagated across services, so one identifier reconstructs an entire request.
- **Sensible levels.** `INFO` for business events, `WARN` for recoverable anomalies, `ERROR` for genuine failures. Debug logging in production should be sampled or dynamically enabled.
- **Never log secrets or personal data.** Redact at the source, and again in the pipeline as a safety net.
- **Cost control.** Log volume grows faster than traffic; sample, drop known-noisy lines, and set retention deliberately. Long-term archive to object storage is far cheaper than keeping everything hot.
- **Compliance.** Audit logs often have mandated retention and immutability requirements, and belong in a separate store with restricted access.

## Example

```json
{
  "ts": "2026-03-14T10:32:11.482Z",
  "level": "error",
  "service": "checkout",
  "version": "1.8.2",
  "trace_id": "b7e1c4...",
  "span_id": "9a2f...",
  "user_id": "u_8821",
  "msg": "payment authorisation failed",
  "provider": "stripe",
  "status": 402,
  "duration_ms": 812
}
```

## Interview tips

- Structured logs plus correlation IDs is the highest-value practice - say it first.
- Buffering with Kafka shows you have run a pipeline that survived an Elasticsearch outage.
- Cost and retention is a legitimate senior concern; volunteer it before being asked.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure Monitoring](./README.md) · [All topics](../README.md)
