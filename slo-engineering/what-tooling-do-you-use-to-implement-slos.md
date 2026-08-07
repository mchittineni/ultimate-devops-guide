---
title: "What tooling do you use to implement SLOs?"
id: 183
category: "SLO Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - slo-engineering
  - interview-questions
---

# What tooling do you use to implement SLOs?

**Short answer:** Define SLOs declaratively in the service repository — OpenSLO or Sloth YAML — and generate the recording rules, burn-rate alerts, and dashboards from that definition. Hand-written PromQL for every SLO does not survive contact with 40 services; the specification should be reviewed like code and the artefacts should be generated.

## Detail

**The layers you need:**

| Layer           | Purpose                                    | Options                                              |
| --------------- | ------------------------------------------ | ---------------------------------------------------- |
| Specification   | one declarative source of truth per SLO    | OpenSLO, Sloth YAML, Nobl9/Datadog definitions       |
| Rule generation | recording rules + multi-window burn alerts | `sloth generate`, Pyrra, provider-native             |
| Storage         | long-window queries over 28–90 days        | Prometheus + Thanos/Mimir, Datadog, Cloud Monitoring |
| Presentation    | budget remaining, burn rate, trend         | Grafana dashboards, Pyrra UI, provider consoles      |
| Governance      | ownership, review cadence, policy link     | catalogue entry (Backstage), quarterly review        |

**Why generation matters.** A correct SLO needs a ratio recording rule at several windows (5m, 30m, 1h, 6h, 1d, 3d), four or more burn-rate alerts, and a budget-remaining query. That is roughly 15 hand-maintained expressions per SLO, and inconsistency between them is how "the alert fired but the dashboard was green" happens. `sloth generate` turns 20 lines of YAML into all of it, deterministically.

**Long windows need remote storage.** A 28-day query against a single Prometheus with 15 days of retention silently returns nonsense. Either shorten the window honestly or run Thanos/Mimir/Cortex. Recording rules that pre-aggregate the ratio keep those queries affordable.

**Managed platforms trade control for convenience.** Datadog SLOs, Google Cloud Monitoring's SLO API, and Nobl9 give you UI, history, and reporting without maintaining rules — at the cost of provider lock-in and per-SLO pricing. A common hybrid: burn-rate paging in Prometheus (where your other alerts live) and executive reporting in the managed tool.

**Keep the SLO next to the service.** The definition belongs in the service repository, owned by the team, referenced from the service catalogue, and changed by pull request. SLOs edited only in a vendor UI drift from reality and have no review trail.

## Example

```yaml
# sloth.yaml — one declarative definition; sloth generates rules and alerts
version: prometheus/v1
service: checkout
labels: { team: payments, tier: "1" }
slos:
  - name: requests-availability
    objective: 99.9
    description: 99.9% of checkout requests succeed over 30 days
    sli:
      events:
        error_query: sum(rate(http_requests_total{job="checkout",code=~"5.."}[{{.window}}]))
        total_query: sum(rate(http_requests_total{job="checkout"}[{{.window}}]))
    alerting:
      name: CheckoutAvailability
      page_alert: { labels: { severity: page } }
      ticket_alert: { labels: { severity: ticket } }
```

```bash
sloth generate -i sloth.yaml -o rules/checkout-slo.yaml   # committed and reviewed
promtool check rules rules/checkout-slo.yaml
```

## Interview tips

- "Declare the SLO, generate the rules" is the answer; hand-maintained PromQL signals small-scale experience.
- Raise the long-window retention problem — it is the mistake most teams hit at the 28-day mark.
- Expect: "why not just use the vendor's SLO feature?" — fine for reporting, but keep the definition in Git and paging where your on-call already looks.

---

[⬅ Back to SLO Engineering](./README.md) · [All topics](../README.md)
