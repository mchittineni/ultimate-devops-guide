---
title: "How do you add monitoring to an application that has none?"
id: 433
category: "Infrastructure Monitoring"
difficulty: "Intermediate"
tags:
  - devops
  - infrastructure-monitoring
  - interview-questions
  - monitoring-and-logging
  - site-reliability-engineering
  - cloud-engineering
---

# How do you add monitoring to an application that has none?

**Short answer:** Work from the outside in, so you get value in a day rather than a quarter. **Step 1: black-box monitoring you can add without touching the code** - a synthetic check on the critical user journey plus the four golden signals from whatever already sits in front of the application (load balancer, ingress, or a reverse proxy): traffic, error rate, latency percentiles, saturation. **Step 2: infrastructure and log collection** - host and container metrics from an agent, and existing logs shipped and parsed centrally. **Step 3: instrument the code** - a metrics endpoint, structured logs with a request ID, then tracing. **Step 4: define what "healthy" means** as an SLO, and build alerts on user-visible symptoms rather than on every metric you now have. The failure mode to avoid is starting with 400 dashboards and no alerts anyone trusts.

## Detail

### Step 1: black-box first, because it needs no code changes

You can answer "is it working for users?" today:

- **Synthetic checks** on the two or three journeys that matter - log in, search, checkout - from outside your network, at a 1-minute interval. This is the single highest-value thing you can add to an unmonitored system, and it needs no cooperation from the application.
- **The golden signals from the edge.** Your load balancer or ingress already records request count, status codes, and latency per route. Turn on access logs and scrape or parse them. That gives error rate and latency percentiles for free.
- **Certificate expiry, DNS resolution, and disk fill** - the three unglamorous checks that cause outages in unmonitored systems more often than application bugs.

Deliverable at the end of step 1: one dashboard with traffic, errors, latency, and one alert that pages when the critical journey fails. That is more useful than everything in steps 2-4 combined, which is why it goes first.

### Step 2: infrastructure and logs

- **An agent per host or a DaemonSet per node** (node-exporter/cAdvisor with Prometheus, or the vendor agent) for CPU, memory, disk, network, and per-container resource usage. This tells you about saturation, which is the signal that predicts failures rather than reporting them.
- **Dependency metrics** - the database, cache, and queue, from their own exporters or the cloud provider's metrics. In a legacy system the database is usually where the problem is, and it is usually already emitting metrics nobody reads.
- **Ship the logs you already have.** A legacy application writes files; a log shipper (Fluent Bit, Vector, or the cloud agent) reads and forwards them. Do not rewrite the logging yet - parse what exists, extract timestamp, level, and any request identifier into fields so it becomes searchable.
- Set retention and volume limits from day one, or the log bill becomes the reason the project is cancelled. See [how do you design a logging pipeline that stays affordable at scale](../monitoring-and-logging/how-do-you-design-a-logging-pipeline-that-stays-affordable-at-scale.md).

### Step 3: instrument the application

Now change the code, cheapest first:

- **A metrics endpoint** exposing request rate, error count, and latency histograms per route, plus a handful of business counters (orders placed, payments failed) - business metrics are what convince stakeholders the work was worth doing, and they detect problems that infrastructure metrics never will.
- **Structured logs with a correlation ID** threaded through every layer, so a user's journey can be reassembled. Retrofit at the boundaries first (the HTTP handler and the outbound client), which gets you most of the value for very little code.
- **Distributed tracing** last, but sooner than instinct suggests if the system spans several services - OpenTelemetry auto-instrumentation gives you span-level visibility with almost no code for most runtimes. See [what is tracing in observability](../advanced-devops-cloud/what-is-tracing-in-observability.md).
- **Health endpoints** that reflect real readiness, since they double as monitoring and as deployment safety.

Choose **OpenTelemetry** for instrumentation regardless of backend, so the vendor decision stays reversible.

### Step 4: define healthy, then alert on symptoms

Metrics without a definition of "good" produce dashboards nobody reads. Pick an SLI per journey (availability and latency), set a target from observed behaviour rather than aspiration, and alert on **burn rate** against that budget. The rule: page on **user-visible symptoms**, ticket on causes. High CPU is not a page; a failing checkout is. See [what do you need before you can set your first SLO](../slo-engineering/what-do-you-need-before-you-can-set-your-first-slo.md) and [how do you design alerts that page a human](../site-reliability-engineering/how-do-you-design-alerts-that-page-a-human.md).

Every alert needs an owner, a runbook link, and a reason it is actionable. An alert that fires and is routinely ignored is worse than no alert, because it trains people to ignore the ones that matter.

### The hybrid and legacy realities

Legacy estates are rarely uniform, so expect to handle: **hosts you cannot install an agent on** (use SNMP, or an external check), **an application you cannot rebuild** (parse its logs, and use a sidecar or exporter to translate them into metrics), **on-premises plus cloud** (one metrics backend with a remote-write or an agent per site, and consistent labels for `env`, `site`, `service` so a single dashboard spans both), and **Windows services** alongside Linux. Pick one backend and normalise labels early - two monitoring systems with different naming is the outcome you are trying to avoid, and it is the default if each team chooses its own.

### What "done" looks like

For each critical service: a dashboard with the golden signals, an SLO with a burn-rate alert, structured logs searchable by request ID, traces across service boundaries, one page-worthy alert per user-visible failure mode with a runbook, and a documented owner. That is a small, finite list - and stating it is a stronger answer than naming ten tools. See [what are monitoring best practices](./what-are-monitoring-best-practices.md).

## Example

```text
Rollout plan for an unmonitored legacy application - value in hours, not quarters

  Day 1   Synthetic check on login + checkout (1 min interval, external)
          Ingress/ALB access logs -> metrics: rate, 5xx%, p50/p95/p99 per route
          One dashboard. One page-worthy alert: "checkout journey failing".
  Day 2-3 node-exporter + cAdvisor; database and Redis exporters
          Fluent Bit tails /var/log/app/*.log -> parsed into level/ts/request_id
          Alerts: disk > 85%, cert expiring < 14d, DB connections > 80% of max
  Week 2  /metrics endpoint in the app: per-route histograms + orders_total,
          payments_failed_total.  Structured JSON logs with request_id.
  Week 3  OpenTelemetry auto-instrumentation -> traces across app, DB, and payments
  Week 4  SLO: 99.5% of checkouts succeed, p95 < 800 ms (from 30 days of observed data)
          Multi-window burn-rate alerts replace the ad hoc threshold alerts
          Every alert: owner + runbook link, or it gets deleted

  Result: 1 page-worthy alert on day 1 -> 6 at week 4, all symptom-based.
  Not: 400 dashboards and 90 threshold alerts nobody acknowledges.
```

```yaml
# Step 1 in practice: a synthetic probe of the real journey, no code changes needed
apiVersion: monitoring.coreos.com/v1
kind: Probe
metadata: { name: critical-journeys, namespace: monitoring }
spec:
  interval: 60s
  module: http_2xx
  prober: { url: blackbox-exporter:9115 }
  targets:
    staticConfig:
      static:
        - https://shop.example.com/healthz
        - https://shop.example.com/api/search?q=test
      labels: { service: shop, tier: critical }
```

```promql
# The four golden signals from edge metrics you already have
sum(rate(nginx_ingress_controller_requests{service="shop"}[5m]))                    # traffic
sum(rate(nginx_ingress_controller_requests{service="shop",status=~"5.."}[5m]))
  / sum(rate(nginx_ingress_controller_requests{service="shop"}[5m]))                # errors
histogram_quantile(0.99, sum by (le)
  (rate(nginx_ingress_controller_request_duration_seconds_bucket{service="shop"}[5m])))  # latency
max by (pod) (container_memory_working_set_bytes{container="app"}
  / container_spec_memory_limit_bytes{container="app"})                             # saturation
```

```yaml
# The only alert that matters on day 1: the user journey, not a resource threshold
groups:
  - name: shop-critical
    rules:
      - alert: CheckoutJourneyFailing
        expr: probe_success{service="shop", instance=~".*checkout.*"} == 0
        for: 3m
        labels: { severity: page }
        annotations:
          summary: "Checkout journey failing from outside the network"
          runbook: "https://runbooks.example.com/shop/checkout" # no runbook, no page
```

## Interview tips

- Lead with black-box monitoring and say why: it needs no code changes, so you can answer "is it working for users?" on day one. That sequencing is the whole point of the question.
- Name the four golden signals (traffic, errors, latency, saturation) and note that the first three are already in your load-balancer or ingress logs - free, and nobody uses them.
- Give a concrete day-1 deliverable: one dashboard, one synthetic check, one page-worthy alert. Interviewers are listening for someone who ships value incrementally instead of proposing a platform project.
- Instrument in the order code changes get harder: metrics endpoint, then structured logs with a correlation ID, then tracing. Mention OpenTelemetry so the backend choice stays reversible.
- Say that business metrics (orders, payments failed) are what justify the work and catch failures infrastructure metrics miss.
- The alerting principle is the part most candidates get wrong: page on user-visible symptoms, ticket on causes, and every alert needs an owner and a runbook or it should be deleted.
- Have an answer for the legacy edge cases - hosts without agents, applications you cannot rebuild (parse logs, add an exporter sidecar), and hybrid on-premises plus cloud with consistent labels in one backend.
- Close on cost: retention and cardinality decided up front, because an observability bill is the usual reason these projects get reversed. See [how do you control metric cardinality and monitoring cost at scale](./how-do-you-control-metric-cardinality-and-monitoring-cost-at-scale.md).

---

[⬅ Back to Infrastructure Monitoring](./README.md) · [All topics](../README.md)
