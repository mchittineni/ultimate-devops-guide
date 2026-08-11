---
title: "How do the ELK and EFK stacks fit together?"
id: 501
category: "Monitoring and Logging"
difficulty: "Intermediate"
tags:
  - devops
  - monitoring-and-logging
  - interview-questions
  - infrastructure-monitoring
  - kubernetes
---

# How do the ELK and EFK stacks fit together?

**Short answer:** Four roles, whatever the letters. A **collector** on each host or node reads log files and ships them - **Filebeat** in ELK, **Fluentd** or **Fluent Bit** in EFK. A **processing layer** parses, enriches, and normalises - **Logstash** in ELK, or Fluentd's own filters, or Elasticsearch **ingest pipelines**. **Elasticsearch** indexes and stores the documents. **Kibana** queries and visualises them. So ELK = Elasticsearch + Logstash + Kibana, and EFK swaps Logstash for Fluentd/Fluent Bit - which is the norm in Kubernetes because Fluent Bit is a tiny C binary that runs happily as a DaemonSet, whereas Logstash is a JVM process better suited to a central aggregation tier. In Kubernetes the collector runs as a **DaemonSet** reading `/var/log/containers/*.log` (symlinks into the container runtime's logs), enriches each line with Kubernetes metadata from the API - namespace, pod, container, labels - and forwards it. The pieces most candidates miss: a **buffer** (Kafka or Redis, or the collector's own disk buffer) so a burst or an Elasticsearch outage does not lose logs, and **index lifecycle management** so the cluster does not fill up and fall over.

## Detail

### The four roles, and the products that fill them

| Role              | ELK                                       | EFK / modern                                       | Notes                                                                    |
| ----------------- | ----------------------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------ |
| Collect           | **Filebeat** (also Metricbeat, Auditbeat) | **Fluent Bit** (lightweight) or Fluentd            | Runs on every host/node. Tails files, tracks position, handles rotation  |
| Buffer            | Kafka / Redis / disk queue                | Kafka / Fluent Bit disk buffer                     | **Not optional at scale** - it absorbs bursts and Elasticsearch downtime |
| Parse / enrich    | **Logstash**                              | Fluentd filters, or Elasticsearch ingest pipelines | grok, JSON parse, GeoIP, drop noise, rename fields, add metadata         |
| Store / index     | **Elasticsearch** (or OpenSearch)         | same                                               | Inverted index; the expensive part                                       |
| Query / visualise | **Kibana** (or OpenSearch Dashboards)     | same                                               | Discover, Lens, dashboards, alerting                                     |

Newer variations worth naming so you sound current: **Vector** as a very efficient collector/router, **Grafana Loki** as a cheaper label-indexed alternative that stores raw logs in object storage, and **OpenTelemetry Collector** as a vendor-neutral pipeline for logs, metrics, and traces together. Loki in particular is the right answer when the cost of a full inverted index is not justified - it indexes labels only, so it is much cheaper but slower for arbitrary full-text search.

### How the pipeline actually flows in Kubernetes

```text
container stdout/stderr
   └─ container runtime writes /var/log/pods/<ns>_<pod>_<uid>/<container>/0.log
        (with /var/log/containers/*.log as symlinks)
            │
   Fluent Bit DaemonSet (hostPath mounts /var/log)
            ├─ tail input, position database so a restart does not re-send
            ├─ kubernetes filter -> adds namespace, pod, container, labels, annotations
            ├─ parser -> JSON if the app logs JSON, multiline for stack traces
            ├─ drop/exclude -> health checks, access-log noise you never query
            └─ output ──> Kafka ──> Logstash/Fluentd aggregator ──> Elasticsearch
                     (or straight to Elasticsearch in smaller setups)
                                                             │
                                                          Kibana
```

Two details that matter operationally. First, **the collector needs the node's log directory**, which is why it is a DaemonSet with a `hostPath` mount and why "we cannot install an agent on the nodes" changes the design. Second, **log rotation**: the runtime rotates container logs (`containerLogMaxSize`), so the collector must handle rotation and keep a position database, or you get duplicates and gaps after every rotation.

### "What if you cannot install an agent on the nodes?"

A real interview scenario, and there are three honest answers: use a **sidecar** container in each Pod that tails the application's log file and ships it (costly - one per Pod, the sidecar tax); have the **application write directly** to the log backend over the network (simple, but couples the app to your logging vendor and loses logs if it is down); or use the **cloud provider's managed collection** - CloudWatch Logs via the awslogs/FireLens driver, Azure Monitor, Cloud Logging - and then export or query there. Say which you would prefer and why: managed collection first, sidecar only for applications that insist on writing to a file inside the container.

### Indices, and the questions asked about them

An **index** is a collection of documents with a mapping (the schema for fields); **indices** is just the plural. Logs are conventionally stored in time-based indices (`logs-app-2026.08.10`) or, better, a **data stream** backed by rolling indices, so you can delete old data cheaply by dropping whole indices instead of deleting documents.

The pieces that keep a cluster alive:

- **Index Lifecycle Management (ILM)** with hot → warm → cold → frozen → delete phases: hot on fast disks and actively written, warm read-only and force-merged, cold/frozen searchable from object storage, then deleted. Without ILM the cluster fills and goes red, which is the most common self-inflicted Elasticsearch outage.
- **Mappings and templates**: define the mapping explicitly. Relying on dynamic mapping means a single log line with a new field shape causes a **mapping conflict** and rejected documents, and unbounded fields cause a **mapping explosion** that bloats the cluster state.
- **Shards**: each index has primary and replica shards; too many small shards waste heap and slow the master, too few makes indexing a bottleneck. Aim for shards in the tens of gigabytes and use ILM rollover on size, not just time.
- **Retention as a decision, not a default**: 7-30 days hot for debugging, longer in cheap storage or S3 for audit. This is where most of the cost is.

### Filtering, and where to do the parsing

Filtering means deciding, per line, what to keep, drop, and transform - and **where** you do it is an architecture choice:

- **At the collector** (Fluent Bit filters, Filebeat processors): cheapest, because dropped lines never travel or get indexed. Drop health-check requests, debug logs from noisy namespaces, and duplicate fields here.
- **In the aggregator** (Logstash, Fluentd): heavier transforms, grok on unstructured legacy formats, lookups, and fan-out to multiple destinations.
- **In Elasticsearch ingest pipelines**: convenient, keeps logic close to the data, but consumes cluster CPU you would rather spend on indexing and search.

The strongest advice, and the one that removes most of the work: make applications emit **structured JSON** with a consistent schema (timestamp, level, service, trace ID, message) so no grok is needed at all. Grok patterns on unstructured logs are the single biggest source of CPU cost and breakage in a Logstash pipeline. See [designing a logging pipeline that stays affordable at scale](./how-do-you-design-a-logging-pipeline-that-stays-affordable-at-scale.md).

### Kibana, and connecting it to Elasticsearch

Kibana is stateless and points at Elasticsearch via `elasticsearch.hosts` in `kibana.yml`, with credentials or a service token and the CA for TLS. It stores its own objects (index patterns/data views, dashboards, saved searches) in a system index inside the same cluster - which is why "Kibana lost my dashboards" usually means it was pointed at a different cluster. Its **data view** (formerly index pattern) is what maps `logs-app-*` into something Discover and Lens can query, and defining the correct time field is what makes the time picker work.

Grafana can also read Elasticsearch, which is common when metrics dashboards already live there - one place for both is a legitimate reason to prefer it over Kibana.

### The design questions worth pre-empting

- **Logging for 100+ microservices across three regions**: collect at the edge with a lightweight agent, buffer through Kafka per region, aggregate and index regionally (data residency and egress cost), and either federate queries or replicate a filtered subset to a global cluster. Enforce a shared schema and a **correlation/trace ID** so one request can be followed across services - without that, a hundred services produce a hundred unrelated log streams.
- **Finding one error quickly** among a hundred applications: structured fields plus a trace ID, not full-text search over everything. Index the fields you filter on, keep the message as text, and give every team a saved view.
- **Incomplete logs** across app, ingress, and infrastructure: check the whole chain - the app is writing to stdout (not a file nobody collects), the collector is running on that node and not crash-looping or rate-limited, the buffer is not full, Elasticsearch is not rejecting documents (mapping conflicts, `429` from a full write queue), and ILM has not deleted the index. Each of those has a distinct signature, and naming them in order is the answer.

## Example

```yaml
# Fluent Bit DaemonSet config: tail, enrich with Kubernetes metadata, drop noise, buffer
apiVersion: v1
kind: ConfigMap
metadata: { name: fluent-bit-config, namespace: logging }
data:
  fluent-bit.conf: |
    [SERVICE]
        Flush         5
        Log_Level     warn
        storage.path  /var/log/flb-storage/     # disk buffer: survives ES downtime
        storage.sync  normal
        storage.backlog.mem_limit 64M

    [INPUT]
        Name              tail
        Path              /var/log/containers/*.log
        Parser            cri
        Tag               kube.*
        DB                /var/log/flb_kube.db   # position DB: no dupes after restart
        Mem_Buf_Limit     32MB
        Skip_Long_Lines   On
        Refresh_Interval  10
        storage.type      filesystem

    [FILTER]
        Name                kubernetes
        Match               kube.*
        Kube_Tag_Prefix     kube.var.log.containers.
        Merge_Log           On                   # parse JSON application logs
        Keep_Log            Off
        Labels              On
        Annotations         Off

    [FILTER]
        Name    grep                             # drop what nobody ever queries
        Match   kube.*
        Exclude log ^.*(GET /healthz|GET /readyz).*$

    [FILTER]
        Name    multiline                        # keep stack traces as ONE document
        Match   kube.*
        multiline.parser  java,go,python

    [OUTPUT]
        Name            es
        Match           kube.*
        Host            elasticsearch.logging.svc
        Port            9200
        Logstash_Format On
        Logstash_Prefix logs-app
        Suppress_Type_Name On
        Retry_Limit     False                    # keep retrying rather than dropping
        tls             On
```

```json
// ILM: the policy that stops the cluster filling up and going red
PUT _ilm/policy/logs-app
{
  "policy": {
    "phases": {
      "hot":    { "actions": { "rollover": { "max_primary_shard_size": "30gb", "max_age": "1d" } } },
      "warm":   { "min_age": "3d",  "actions": { "forcemerge": { "max_num_segments": 1 },
                                                 "shrink": { "number_of_shards": 1 } } },
      "cold":   { "min_age": "14d", "actions": { "searchable_snapshot": { "snapshot_repository": "s3-logs" } } },
      "delete": { "min_age": "90d", "actions": { "delete": {} } }
    }
  }
}
```

```json
// Explicit mapping: prevents mapping conflicts and field explosions
PUT _index_template/logs-app
{
  "index_patterns": ["logs-app-*"],
  "data_stream": {},
  "template": {
    "settings": { "index.lifecycle.name": "logs-app", "number_of_shards": 3, "number_of_replicas": 1 },
    "mappings": {
      "dynamic": "strict",                        // reject unknown fields loudly
      "properties": {
        "@timestamp":  { "type": "date" },
        "level":       { "type": "keyword" },
        "service":     { "type": "keyword" },
        "trace_id":    { "type": "keyword" },     // the field that ties services together
        "kubernetes":  { "properties": { "namespace_name": { "type": "keyword" },
                                         "pod_name": { "type": "keyword" } } },
        "message":     { "type": "text" }         // full-text only where you need it
      }
    }
  }
}
```

```bash
# "Logs are incomplete" - work the chain in order
kubectl logs -n prod deploy/payments --tail=5                 # 1. is the app logging to stdout?
kubectl logs -n logging ds/fluent-bit --tail=50 | grep -iE 'error|retry|backpressure'  # 2. collector
kubectl exec -n logging ds/fluent-bit -- ls -la /var/log/flb-storage/  # 3. buffer backing up?

curl -s 'http://es:9200/_cluster/health?pretty'                # 4. green/yellow/red, unassigned shards
curl -s 'http://es:9200/_cat/indices/logs-app-*?v&s=index'     # 5. are today's indices being written?
curl -s 'http://es:9200/_cat/thread_pool/write?v&h=node_name,active,queue,rejected'  # 429s = rejected docs
curl -s 'http://es:9200/_ilm/explain/logs-app-*?pretty' | head -40   # 6. did ILM delete or fail?

# Kibana cannot see the data?
grep -E 'elasticsearch.hosts|ssl' /etc/kibana/kibana.yml
curl -s 'http://es:9200/_cat/indices/.kibana*?v'               # Kibana's own objects live here
```

## Interview tips

- Answer in **roles**, not product names: collect, buffer, parse, store, visualise - then map ELK and EFK onto them. That structure answers "what does each component do?" completely and survives the interviewer swapping products on you.
- Explain why EFK dominates in Kubernetes: Fluent Bit is a small C binary suited to a DaemonSet, Logstash is a JVM aggregator better placed centrally.
- Describe the Kubernetes path concretely - DaemonSet with a `hostPath` on `/var/log`, the Kubernetes filter adding namespace/pod/labels, and a position database so rotation does not cause duplicates or gaps.
- Volunteer the **buffer**. Saying "Kafka or a disk buffer, so a burst or an Elasticsearch outage does not lose logs" is the single most distinguishing addition, because most candidates draw the pipeline without it.
- Define index versus indices plainly, then spend your time on **ILM** and **explicit mappings** - the two things whose absence causes real outages (a full cluster going red, and mapping conflicts rejecting documents).
- Say where you would filter and why - at the collector, because dropped lines cost nothing downstream - and push the structural fix: applications emitting structured JSON so grok is unnecessary.
- For "no agent allowed on the nodes", give all three options (sidecar, direct-to-backend, managed cloud collection) and state a preference with a reason.
- For the 100-microservices-three-regions design, cover regional aggregation for residency and egress cost, a shared schema, and a **correlation/trace ID** as the thing that makes cross-service debugging possible at all.
- Mention Loki and the OpenTelemetry Collector as the modern alternatives, and be able to say when a label-indexed store beats a full inverted index on cost. See [what is ELK stack](./what-is-elk-stack.md), [designing a logging pipeline that stays affordable at scale](./how-do-you-design-a-logging-pipeline-that-stays-affordable-at-scale.md), [what is log management](../infrastructure-monitoring/what-is-log-management.md), and [adding monitoring to an application that has none](../infrastructure-monitoring/how-do-you-add-monitoring-to-an-application-that-has-none.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you add monitoring to an application that has none?]] (`#433`): [How do you add monitoring to an application that has none?](../infrastructure-monitoring/how-do-you-add-monitoring-to-an-application-that-has-none.md)
- [[What is Infrastructure Monitoring?]] (`#131`): [What is Infrastructure Monitoring?](../infrastructure-monitoring/what-is-infrastructure-monitoring.md)
- [[What is Log Management?]] (`#135`): [What is Log Management?](../infrastructure-monitoring/what-is-log-management.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Monitoring and Logging](./README.md) · [All topics](../README.md)
