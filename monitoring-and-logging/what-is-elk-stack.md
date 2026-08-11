---
title: "What is ELK Stack?"
id: 32
category: "Monitoring and Logging"
difficulty: "Intermediate"
tags:
  - devops
  - monitoring-and-logging
  - interview-questions
---

# What is ELK Stack?

**Short answer:** The ELK stack is Elasticsearch (search and analytics store), Logstash (ingestion and transformation pipeline), and Kibana (visualisation) - a platform for centralising, searching, and analysing logs. With Beats added it is often called the Elastic Stack.

## Detail

**Elasticsearch** - a distributed, document-oriented search engine built on Lucene. Logs are indexed into shards spread across nodes; queries are fast even over billions of documents. Index lifecycle management moves indices through hot, warm, cold, and delete phases to control cost.

**Logstash** - a pipeline with input, filter, and output stages. Filters do the heavy work: `grok` parses unstructured lines into fields, `mutate` reshapes, `date` normalises timestamps, `geoip` enriches. Powerful, but JVM-based and resource-hungry.

**Kibana** - search UI, dashboards, and alerting on top of Elasticsearch.

**Beats** - lightweight shippers installed at the edge: Filebeat for logs, Metricbeat for metrics, Packetbeat for network data. The common modern topology is Filebeat → Kafka (buffer) → Logstash → Elasticsearch → Kibana, so an ingest spike or an Elasticsearch outage does not lose data.

Alternatives worth naming: OpenSearch (the open-source fork), and Grafana Loki, which indexes only labels rather than full text and is dramatically cheaper for high-volume Kubernetes logs.

## Example

```ruby
# logstash.conf
input { beats { port => 5044 } }

filter {
  grok {
    match => { "message" => "%{TIMESTAMP_ISO8601:ts} %{LOGLEVEL:level} %{GREEDYDATA:msg}" }
  }
  date { match => ["ts", "ISO8601"] target => "@timestamp" }
  mutate { remove_field => ["ts"] }
}

output {
  elasticsearch {
    hosts => ["https://es:9200"]
    index => "app-logs-%{+YYYY.MM.dd}"
  }
}
```

## Interview tips

- Know why you would buffer with Kafka in front of Logstash - backpressure and durability.
- Index lifecycle management and retention are the cost answers; log volume grows faster than anyone plans for.
- Structured JSON logging at source beats grok parsing downstream - say that if asked how to improve a log pipeline.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you add monitoring to an application that has none?]] (`#433`): [How do you add monitoring to an application that has none?](../infrastructure-monitoring/how-do-you-add-monitoring-to-an-application-that-has-none.md)
- [[What are Monitoring Tools?]] (`#132`): [What are Monitoring Tools?](../infrastructure-monitoring/what-are-monitoring-tools.md)
- [[What are Monitoring Best Practices?]] (`#133`): [What are Monitoring Best Practices?](../infrastructure-monitoring/what-are-monitoring-best-practices.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Monitoring and Logging](./README.md) · [All topics](../README.md)
