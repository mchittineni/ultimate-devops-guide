---
title: "What are Blackbox vs Whitebox monitoring and when should each be used?"
id: 688
category: "Infrastructure Monitoring"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - monitoring
  - blackbox
  - whitebox
  - synthetic
quiz:
  stem: "Which monitoring approach is best suited for detecting that an external SSL/TLS certificate is expiring in 14 days?"
  options:
    - "Whitebox CPU profiling"
    - "Blackbox synthetic probing against the public domain port 443"
    - "Application thread dump analysis"
    - "Database slow query logging"
  answer: 2
  explanation: "Blackbox monitoring probes the public endpoint from the outside just like a real client, checking the presented TLS certificate expiration date and cipher negotiation."
---

# What are Blackbox vs Whitebox monitoring and when should each be used?

**Short answer:** Whitebox monitoring inspects internal system telemetry from the inside (CPU, database query latency, thread pools, app logs); Blackbox monitoring tests system behavior from the outside (probing HTTP endpoints, DNS, SSL certs), evaluating what real users experience.

## Detail

Effective reliability requires combining both perspectives:

| Dimension     | Blackbox Monitoring (Outside-In)                                             | Whitebox Monitoring (Inside-Out)                                                |
| ------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| Vantage Point | External synthetic probes (Datadog Synthetics, Prometheus Blackbox Exporter) | Internal agents, metrics, logs, traces (Prometheus, OTel)                       |
| What it Sees  | 'Can a user log in? Is SSL valid? Did HTTP return 200?'                      | 'Why is it slow? Is JVM GC freezing? Is connection pool full?'                  |
| Alerts        | Paging alerts on symptom-based failures (user cannot pay)                    | Diagnostic debugging; early warning before outage                               |
| Blind Spots   | Cannot see internal queues or pending memory exhaustion                      | Can show 100% green metrics while a network firewall drops 100% of user traffic |

### Real-World Example

- **Blackbox**: Probes `https://app.com/api/health` every 30s. If it times out or returns 502, it pages the on-call engineer: **'System is down!'**
- **Whitebox**: The engineer opens Grafana and inspects PostgreSQL lock tables and CPU metrics to diagnose **why** it failed.

**Trade-offs.** Blackbox probes are cheap and honest but coarse: a probe every 30 seconds from three locations sees a tiny sample of traffic and cannot detect a failure affecting 2% of users. Whitebox telemetry sees every request but only from the inside, so it misses DNS, CDN, TLS, and network problems in front of the service. The usual design is to page on SLOs computed from edge/whitebox request metrics, with blackbox probes as an independent backstop and for low-traffic or external dependencies.

## Example

```yaml
# blackbox.yml - Prometheus Blackbox Exporter module: expect 2xx, HTTPS only, check body
modules:
  http_2xx_login:
    prober: http
    timeout: 5s
    http:
      method: GET
      valid_status_codes: [] # empty = any 2xx
      fail_if_not_ssl: true
      fail_if_body_not_matches_regexp: ["Sign in"]
```

```promql
probe_success{job="blackbox", instance="https://app.example.com/login"} == 0   # blackbox: page
(probe_ssl_earliest_cert_expiry - time()) / 86400 < 14                           # blackbox: cert expiring
pg_stat_activity_count{state="idle in transaction"} > 20                        # whitebox: diagnose
```

## Interview tips

- Blackbox: testing from the outside without internal knowledge (synthetic probes).
- Whitebox: monitoring internal mechanics from inside (JVM, queues, memory, logs).
- Blackbox alerts on symptoms affecting users.
- Whitebox provides diagnostic root-cause context.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure Monitoring](./README.md) · [All topics](../README.md)
