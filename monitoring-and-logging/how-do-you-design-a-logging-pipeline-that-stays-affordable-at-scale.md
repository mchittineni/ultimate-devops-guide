---
title: "How do you design a logging pipeline that stays affordable at scale?"
id: 296
category: "Monitoring and Logging"
difficulty: "Advanced"
tags:
  - devops
  - monitoring-and-logging
  - interview-questions
---

# How do you design a logging pipeline that stays affordable at scale?

**Short answer:** Decide what each log line is _for_ before you ship it. Structure everything as JSON with a small stable schema, filter and sample at the edge (drop health checks and debug noise, tail-sample traces, keep all errors), route by value into tiers - hot searchable index for days, warm object storage for weeks, cold compressed archive for compliance years - and convert repetitive log-derived questions into metrics. The single biggest lever is not the storage engine; it is **not ingesting lines nobody will ever read**.

## Detail

**Know the three jobs logs do**, because they have different retention and different economics: **debugging** (high volume, valuable for hours to days), **audit and compliance** (low volume, must be immutable and kept for years), and **analytics or business events** (belongs in a warehouse, not a log index). Mixing them into one pipeline with one retention is how a logging bill grows faster than traffic.

**Structure at the source.** JSON logs with a consistent field set (`timestamp`, `level`, `service`, `env`, `trace_id`, `message`, plus typed context) cost a fraction of the effort to query and let you filter cheaply in the pipeline. Include `trace_id` on every line - it is what links a log to a trace and removes the need for verbose "context" logging. Never log secrets, tokens, full request bodies, or personal data you would then have to redact under a deletion request; scrubbing at the collector is a safety net, not a design.

**Reduce at the edge, in this order:**

1. **Drop what has no reader.** Health-check and readiness-probe access logs, successful static asset requests, framework startup banners, chatty third-party libraries at DEBUG. In a typical service this is 40-70% of volume.
2. **Set levels correctly and make them runtime-configurable.** DEBUG off in production, with the ability to raise it for one service or one tenant for fifteen minutes when investigating - that capability is what makes it safe to keep DEBUG off by default.
3. **Sample the repetitive.** Head-sample high-volume success paths (keep 1%), but **keep 100% of errors, warnings, and anything with an error trace**. Tail-based sampling in the OTel Collector is the sophisticated version: buffer a trace, decide after seeing the outcome, keep everything that failed or was slow.
4. **Aggregate instead of logging.** "Request completed in 41ms" logged 50,000 times per second is a histogram, not a log line. Converting the top few repetitive lines into metrics routinely removes the largest single contributor to volume.
5. **Deduplicate storms.** One misconfigured client can generate millions of identical lines; rate-limit per source and per message signature at the collector so an incident does not also become an invoice.

**Tier the storage, because query patterns decay fast.** Almost all queries are against the last few hours.

| Tier | Window     | Store                                         | Query cost    |
| ---- | ---------- | --------------------------------------------- | ------------- |
| Hot  | 3-7 days   | Indexed search (OpenSearch, Loki, vendor)     | Fast, dear    |
| Warm | 30-90 days | Object storage, compressed, queried on demand | Slow, cheap   |
| Cold | 1-7 years  | Glacier / Archive tier, audit only            | Restore first |

Loki's model - index only labels, store the raw log compressed in object storage - is cheap precisely because it does not build a full inverted index; ClickHouse-based systems make a similar trade with columnar compression. If you are on a per-GB-ingested vendor, the tiering has to happen _before_ ingest, in the collector, or you pay for everything regardless of tier.

**Own the pipeline shape.** Agent (Fluent Bit, Vector, OTel Collector) on each node → an aggregation tier that does the heavy filtering, enrichment, and routing → sinks. Put a buffer between them: a disk buffer on the agent so a collector restart does not lose logs, and a queue (Kafka) in front of the aggregation tier at large scale so a backend outage becomes latency rather than loss. Then apply back pressure deliberately - if the pipeline is saturated, dropping sampled INFO lines while preserving ERROR is a design decision you should make in advance rather than discover.

**Govern the cost.** Per-team ingest attribution with quotas, an alert on volume growth per service (a bad deploy that adds a log line inside a hot loop is the classic 10x event), and a periodic review of which indexes are actually queried. Publish cost per GB to teams and they will fix their own noise; keep it central and nobody will.

## Example

```yaml
# Vector: drop, redact, sample, route - all before anything is paid for.
sources:
  k8s:
    type: kubernetes_logs

transforms:
  parse:
    type: remap
    inputs: [k8s]
    source: |
      . = parse_json!(.message) ?? { "message": .message, "level": "info" }
      .service = .kubernetes.container_name
      .env     = get_env_var!("CLUSTER_ENV")

  drop_noise:
    type: filter
    inputs: [parse]
    condition: |
      # health checks and static assets have no reader
      !(.http.path == "/healthz" || .http.path == "/readyz") &&
      !(.level == "debug" && .env == "prod")

  redact:
    type: remap
    inputs: [drop_noise]
    source: |
      .authorization = null
      .message = replace(string!(.message), r'Bearer [A-Za-z0-9._-]+', "Bearer [REDACTED]")

  split_audit:
    type: route
    inputs: [redact]
    route:
      # Explicit classification only - an event is audit because the emitter said so,
      # never because it happened to mention a user id.
      audit: '.log_class == "audit" || .log_class == "compliance"'
      # General branch for events not classified as audit or compliance
      general: '!(.log_class == "audit" || .log_class == "compliance")'

  sample_success:
    type: sample
    inputs: [split_audit.general]
    rate: 100 # keep 1%...
    exclude: '.level == "error" || .level == "warn" || exists(.error)' # ...but never errors

sinks:
  hot:
    type: loki
    inputs: [sample_success]
    labels: { service: "{{ service }}", env: "{{ env }}", level: "{{ level }}" }
    # labels only - the log body stays unindexed in object storage
  archive:
    type: aws_s3
    inputs: [split_audit.general] # unsampled, compressed, cheap - operational replay, NOT audit retention
    compression: zstd
    key_prefix: "logs/%Y/%m/%d/"
    server_side_encryption: aws:kms
    ssekms_key_id: "${GENERAL_KMS_KEY_ARN}"
    # 30-day lifecycle then expire: general events must not inherit audit retention,
    # which is what makes an audit bucket both expensive and legally risky.

  audit_archive:
    type: aws_s3
    inputs: [split_audit.audit] # only events explicitly classified as audit/compliance
    compression: zstd
    key_prefix: "audit/%Y/%m/%d/"
    server_side_encryption: aws:kms
    ssekms_key_id: "${AUDIT_KMS_KEY_ARN}" # separate CMK, separate key policy
    # Bucket is provisioned with Object Lock in COMPLIANCE mode for the statutory
    # retention period (7 years here) and no lifecycle expiry inside it: nobody -
    # including the root account - can delete or overwrite an object before it expires.
    # Deletion after expiry is a documented, ticketed job, not a lifecycle rule.
```

```yaml
# OTel Collector: tail-based sampling - decide after you know the outcome.
processors:
  tail_sampling:
    decision_wait: 10s
    policies:
      - { name: keep-errors, type: status_code, status_code: { status_codes: [ERROR] } }
      - { name: keep-slow, type: latency, latency: { threshold_ms: 1000 } }
      - { name: sample-rest, type: probabilistic, probabilistic: { sampling_percentage: 1 } }
```

```promql
# Two alerts that pay for themselves.
- alert: LogVolumeSpike
  expr: |
    sum by (service) (rate(vector_component_sent_events_total[30m]))
      > 3 * sum by (service) (rate(vector_component_sent_events_total[30m] offset 1d))
  for: 20m
  annotations: { summary: "{{ $labels.service }} log volume 3x vs yesterday - check deploys" }

- alert: LoggingPipelineBackpressure
  expr: sum(rate(vector_buffer_discarded_events_total[5m])) > 0
  for: 10m
```

## Interview tips

- Start with "what is each log line for" and split debugging, audit, and analytics. One pipeline with one retention is the mistake being probed.
- Say the biggest lever is not ingesting what nobody reads, and give the concrete examples: health checks, static assets, DEBUG in prod.
- Keep 100% of errors while sampling success paths. Volunteering that asymmetry shows you understand the risk of sampling.
- Name tail-based sampling and explain why deciding after the outcome beats head sampling for traces.
- Converting a repetitive log line into a histogram is the sharpest single optimisation. Have that example ready.
- Explain Loki's label-only indexing versus a full inverted index. It shows you understand _why_ one is cheaper, not just which is cheaper.
- Mention buffering, back pressure, and the deliberate drop policy. "What happens when the backend is down" is a standard follow-up.

---

[⬅ Back to Monitoring and Logging](./README.md) · [All topics](../README.md)
