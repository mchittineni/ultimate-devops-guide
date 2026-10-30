---
title: "How does Grafana Loki store logs, and how do you query them with LogQL?"
id: 769
category: "Monitoring and Logging"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - monitoring-and-logging
  - loki
  - logql
  - logging
quiz:
  stem: "Why is putting `trace_id` or `user_id` in Loki stream labels a mistake?"
  options:
    - "Loki labels cannot contain hexadecimal characters"
    - "Every unique label combination creates a new stream, so unbounded values explode the stream count, the index, and the number of tiny chunks"
    - "Labels are stored in plain text and expose personal data, while log lines are encrypted"
    - "LogQL cannot filter on labels, only on line contents"
  answer: 2
  explanation: "Loki indexes only stream labels, and each unique label set is a separate stream with its own chunks. High-cardinality values belong in the log line or in structured metadata, where they can still be filtered at query time."
---

# How does Grafana Loki store logs, and how do you query them with LogQL?

**Short answer:** Loki indexes only a small set of **labels** per log stream (namespace, app, container, level) and stores the log lines themselves as compressed **chunks in object storage**. A query first uses the label index to pick the streams, then brute-force scans those chunks in parallel. That makes ingest and storage far cheaper than a full-text index like Elasticsearch, at the cost of slower "search everything for this string" queries. **LogQL** mirrors PromQL: a stream selector (`{namespace="prod", app="checkout"}`), then a pipeline of line filters (`|= "timeout"`), parsers (`| json`, `| logfmt`, `| pattern`), and label filters (`| status >= 500`), and optionally a metric function (`rate`, `count_over_time`, `quantile_over_time`) that turns logs into time series for dashboards and alerts.

## Detail

### The storage model

- **Stream** = one unique set of labels. Each stream's lines are appended to chunks, compressed, and flushed to S3/GCS/Azure Blob.
- **Index** = labels to chunk references only (the TSDB index format is the default in current schemas). It stays small because labels are few and bounded.
- **Structured metadata** (Loki 3.x) attaches per-line key-values such as `trace_id` without making them labels, so they are filterable but do not create streams. OTLP ingestion uses it for resource and log attributes.
- **Retention** is applied by the compactor, globally or per stream selector.

The design rule follows directly: **labels must be low-cardinality and describe where the log came from, not what it says.** A `trace_id`, `user_id`, or `path` label creates a stream per value - millions of tiny chunks, a bloated index, and ingestion limits (`max_global_streams_per_user`) being hit. Loki also needs lines within a stream to arrive roughly in time order (out-of-order writes are accepted within a window).

### Architecture in one paragraph

Agents (Grafana Alloy, which replaced Promtail; Fluent Bit; Vector; the OTel Collector) push to **distributors**, which hash streams to **ingesters** that build chunks in memory and flush them. **Query frontends** split queries by time and shard them by stream, **queriers** read recent data from ingesters and older data from object storage, and the **compactor** handles index compaction and retention. Small installations run all of this as one binary (monolithic mode); large ones run the components separately.

### LogQL in four steps

1. **Select streams** (mandatory, and the main cost control): `{namespace="prod", app="checkout"}`.
2. **Filter lines** cheaply before parsing: `|= "error"`, `!= "healthz"`, `|~ "timeout|refused"`.
3. **Parse and filter fields**: `| json | status >= 500 and route="/pay"`, `| logfmt`, or `| pattern "<ip> - - [<_>] \"<method> <path> <_>\" <status>"`.
4. **Aggregate into metrics**: `sum by (route) (count_over_time({...} | json | status >= 500 [5m]))`, or `quantile_over_time(0.99, {...} | json | unwrap duration_ms [5m]) by (route)`.

Put the cheapest, most selective filters first: label selector, then line filters, then parsers. A query like `{namespace=~".+"} |= "abc"` over seven days scans everything and is exactly the workload Loki is worst at.

### Trade-offs versus Elasticsearch/OpenSearch

|                                            | Loki                                                            | Elasticsearch / OpenSearch                                                 |
| ------------------------------------------ | --------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Index                                      | Labels only                                                     | Every field (inverted index)                                               |
| Ingest and storage cost                    | Low; object storage                                             | High; indexing CPU and disk                                                |
| Needle-in-haystack search over wide ranges | Slow, brute force                                               | Fast                                                                       |
| Operational burden                         | Mostly stateless plus object storage                            | Shard sizing, mappings, ILM, heap                                          |
| Best fit                                   | Kubernetes app logs, "show me logs for this service/time/trace" | Security analytics, ad-hoc full-text search, aggregations over many fields |

Many teams use both: Loki for high-volume operational logs, a search engine or SIEM for security and audit data.

## Example

```logql
# 1. Errors for one service in the last hour, excluding health checks
{namespace="prod", app="checkout"} |= "error" != "/healthz"

# 2. Parse JSON and filter on fields - status is a parsed field, not a label
{namespace="prod", app="checkout"} | json | status >= 500 | line_format "{{.route}} {{.msg}}"

# 3. Jump from a trace to its logs via structured metadata (no label needed)
{namespace="prod"} | trace_id="4bf92f3577b34da6a3ce929d0e0e4736"

# 4. Metric query for a dashboard or alert: 5xx log lines per second, by route
sum by (route) (rate({namespace="prod", app="checkout"} | json | status >= 500 [5m]))

# 5. p99 latency extracted from a log field
quantile_over_time(0.99, {namespace="prod", app="checkout"} | json | unwrap duration_ms [5m]) by (route)
```

```bash
# The same queries from the command line with logcli
export LOKI_ADDR=http://loki-gateway.logging.svc
logcli query '{namespace="prod", app="checkout"} |= "timeout"' --since=1h --limit=50
logcli series '{namespace="prod"}' --analyze-labels   # which labels drive stream count?
```

## Interview tips

- Lead with the design choice: index labels, not content - and its consequence, cheap ingest with slower full-text search.
- Say what belongs in a label (source: cluster, namespace, app, level) and what does not (trace IDs, user IDs, paths); mention structured metadata as the place for high-cardinality per-line fields.
- Write a LogQL query out loud in the right order: stream selector, line filter, parser, field filter, then a metric function. Interviewers notice when the label selector is too broad.
- Show you know LogQL metric queries can drive Grafana dashboards and Loki ruler alerts, but prefer real metrics for anything you alert on at high volume.
- Know the agent landscape: Promtail is end-of-life, Grafana Alloy is its replacement, and Fluent Bit, Vector, and the OTel Collector all push to Loki.
- Be honest about the limit: when security or compliance teams need fast arbitrary search over months, Loki alone is usually the wrong tool.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you add monitoring to an application that has none?]] (`#433`): [How do you add monitoring to an application that has none?](../infrastructure-monitoring/how-do-you-add-monitoring-to-an-application-that-has-none.md)
- [[What are Monitoring Tools?]] (`#132`): [What are Monitoring Tools?](../infrastructure-monitoring/what-are-monitoring-tools.md)
- [[What are Monitoring Best Practices?]] (`#133`): [What are Monitoring Best Practices?](../infrastructure-monitoring/what-are-monitoring-best-practices.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Monitoring and Logging](./README.md) · [All topics](../README.md)
