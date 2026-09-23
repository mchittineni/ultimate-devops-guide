---
title: "What are Monitoring Tools?"
id: 132
category: "Infrastructure Monitoring"
difficulty: "Beginner"
tags:
  - devops
  - infrastructure-monitoring
  - interview-questions
---

# What are Monitoring Tools?

**Short answer:** Prometheus with Grafana is the open-source standard for metrics; ELK/OpenSearch or Loki for logs; Jaeger or Tempo for traces; and Datadog, New Relic, or Dynatrace as commercial all-in-one platforms - plus the cloud providers' native offerings.

## Detail

| Category        | Open source                                    | Commercial / cloud                                                 |
| --------------- | ---------------------------------------------- | ------------------------------------------------------------------ |
| Metrics         | Prometheus, VictoriaMetrics, Thanos, Mimir     | Datadog, New Relic, CloudWatch, Azure Monitor                      |
| Visualisation   | Grafana                                        | Datadog dashboards, Kibana                                         |
| Logs            | Loki, Elasticsearch/OpenSearch, Fluent Bit     | Splunk, Datadog Logs, CloudWatch Logs                              |
| Traces          | Jaeger, Tempo, Zipkin                          | Datadog APM, New Relic, X-Ray, Honeycomb                           |
| Collectors      | OpenTelemetry Collector, Grafana Alloy, Vector | Datadog Agent, vendor agents                                       |
| Alerting        | Alertmanager, Grafana Alerting                 | PagerDuty, incident.io, Grafana Cloud IRM, Jira Service Management |
| Synthetic / RUM | Blackbox exporter, Uptime Kuma, k6 browser     | Checkly, Datadog Synthetics, Pingdom                               |
| Profiling       | Pyroscope, Parca                               | Datadog Profiler                                                   |

**OpenTelemetry** is the important development: a vendor-neutral standard for instrumenting applications and shipping metrics, logs, and traces. Instrumenting with OTel means you can change backends without re-instrumenting - which is the strongest defence against observability vendor lock-in and the default recommendation for new work.

**Watch the lifecycle of tools, too.** Several popular components have been retired or replaced recently: Grafana Agent and Promtail gave way to Grafana Alloy, Opsgenie reached end of sale in 2025 (with support ending in April 2027) as Atlassian moves on-call into Jira Service Management, Grafana OnCall OSS was archived in 2026 in favour of Grafana Cloud IRM, and Jaeger v2 is now built on the OpenTelemetry Collector. Instrumenting with OpenTelemetry keeps these changes to the backend side.

**Choosing.** Weigh cost at your data volume (commercial platforms are excellent and become extremely expensive at scale), the operational burden of self-hosting, existing team skills, ecosystem fit (Prometheus is native to Kubernetes), and long-term retention needs.

A very common pattern: Prometheus and Grafana for metrics and dashboards, Loki for logs, Tempo or Jaeger for traces, all instrumented via OpenTelemetry, with PagerDuty for on-call - self-hosted, portable, and cost-predictable.

## Example

```bash
# The OpenTelemetry promise in practice: switch backends by changing endpoints, not code
pip install opentelemetry-distro opentelemetry-exporter-otlp
opentelemetry-bootstrap -a install          # installs instrumentation for detected libraries

export OTEL_SERVICE_NAME=checkout
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317   # Collector routes to any backend
opentelemetry-instrument python app.py
```

## Interview tips

- Lead with OpenTelemetry; it is the answer that shows current thinking rather than tool trivia.
- Be ready to discuss cost - observability spend rivalling infrastructure spend is a real and common problem.
- Have a reasoned opinion on build-versus-buy rather than a favourite tool.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure Monitoring](./README.md) · [All topics](../README.md)
