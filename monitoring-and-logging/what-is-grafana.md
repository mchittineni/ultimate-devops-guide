---
title: "What is Grafana?"
id: 34
category: "Monitoring and Logging"
difficulty: "Beginner"
tags:
  - devops
  - monitoring-and-logging
  - interview-questions
---

# What is Grafana?

**Short answer:** Grafana is an open-source visualisation and dashboarding platform that queries many data sources - Prometheus, Loki, Elasticsearch, CloudWatch, SQL databases - and presents them in unified dashboards with alerting.

## Detail

Grafana is deliberately storage-agnostic: it stores dashboards, not data. That means one dashboard can correlate a Prometheus metric, a Loki log query, and a Tempo trace side by side, which is exactly what you need during an incident.

Capabilities that matter in practice:

- **Templating with variables** - a `$namespace` or `$service` dropdown turns one dashboard into hundreds, and repeated rows generate a panel per instance.
- **Unified alerting** - alert rules defined in Grafana across any data source, with notification policies routing to Slack, PagerDuty, or email.
- **Dashboards as code** - JSON models provisioned from Git, or generated with Grafonnet/Terraform, so dashboards are reviewed and versioned like everything else.
- **Exemplars and correlations** - jump from a latency spike on a graph directly to a matching trace.
- **Annotations** - overlay deploys and incidents onto graphs, which makes "what changed?" answerable in seconds.

The wider Grafana stack pairs it with **Loki** (logs), **Tempo** (traces), **Mimir** (long-term metrics), and **Pyroscope** (profiles).

## Interview tips

- Dashboards-as-code and provisioning is the answer that separates operators from users.
- A good dashboard design principle: top row answers "is it healthy?" in five seconds; detail lives below.
- Deploy annotations are a cheap, high-value practice worth mentioning.

---

[⬅ Back to Monitoring and Logging](./README.md) · [All topics](../README.md)
