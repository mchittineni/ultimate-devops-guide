---
title: "How do you design alerts that page a human?"
id: 233
category: "Site Reliability Engineering (SRE)"
difficulty: "Advanced"
tags:
  - devops
  - site-reliability-engineering
  - interview-questions
---

# How do you design alerts that page a human?

**Short answer:** Page only on user-visible symptoms that are urgent, actionable, and real - in practice, error-budget burn rate against an SLO. Everything else becomes a ticket or a dashboard. Every page must have a documented action; if the responder's only option is to watch, the alert should not have woken them.

## Detail

**The four tests for a paging alert:** it reflects something users are experiencing (symptom, not cause); it is urgent enough that waiting until morning would cause harm; the responder can do something about it now; and it is precise enough that the page is usually real. An alert failing any of these belongs in a ticket queue.

**Symptoms over causes.** "Checkout error rate is burning the budget at 14×" is one alert that catches every underlying cause. "Node CPU > 90%", "disk 80% full", "Pod restarted" are causes that may or may not affect users - high CPU on a batch node at 2am is expected. Cause-based alerts are how alert fatigue starts; keep them as dashboards and tickets, with the exception of predictive resource alerts where exhaustion is inevitable and slow (a disk filling in four hours warrants a ticket now, and a page only if it will exhaust before working hours).

**Burn-rate alerting is the concrete mechanism.** Fast burn (a large fraction of the budget in an hour) pages; slow burn (steady erosion over days) opens a ticket. Multi-window conditions keep it sensitive without flapping. This ties every page directly to a consequence you have already agreed matters.

**Every alert needs a runbook and an owner.** The alert annotation should link to a document that states what is affected, how to confirm, the first three diagnostic steps, mitigation options, and when to escalate. Alerts whose runbook is "investigate" are a tax on the responder - and reviewing them is one of the highest-value things an on-call retrospective can do.

**Measure your alerting.** Pages per shift (a common target is fewer than two actionable pages per 12-hour shift), the fraction of pages that were actionable, the fraction that led to a real incident, and time to acknowledge. Any alert that is repeatedly non-actionable gets fixed or deleted - deleting a bad alert is a legitimate, valuable engineering outcome, not an admission of defeat.

**Reduce noise structurally, not by ignoring it.** Group related alerts into one notification, inhibit downstream alerts when an upstream cause is already firing, suppress during announced maintenance, and require a duration (`for:`) so transient blips do not page. Route by ownership from the service catalogue so the page reaches the team that can act.

**Design the on-call experience alongside the alerts.** Sustainable rotations (enough people, compensated, with a follow-the-sun option), a handover with open issues, and post-shift review of every page. If a rotation is unsustainable, the fix is usually fewer and better alerts plus reliability work - not more stoicism.

## Example

```yaml
# Page on budget burn (symptom); ticket on saturation (cause)
groups:
  - name: checkout-alerts
    rules:
      - alert: CheckoutErrorBudgetFastBurn
        expr: |
          job:sli_error_ratio:rate1h{job="checkout"} > 0.0144
            and job:sli_error_ratio:rate5m{job="checkout"} > 0.0144
        for: 2m
        labels: { severity: page, team: payments }
        annotations:
          summary: "Checkout burning error budget at 14.4x (2% of 30d budget gone)"
          runbook: "https://runbooks.acme.com/checkout/error-budget-burn"
          dashboard: "https://grafana.acme.com/d/checkout"

      - alert: CheckoutDiskWillFill
        # predictive, slow, and actionable in hours - a ticket, not a page
        expr: predict_linear(node_filesystem_avail_bytes{job="checkout"}[6h], 12 * 3600) < 0
        for: 30m
        labels: { severity: ticket, team: payments }
        annotations:
          summary: "Checkout node disk projected to fill within 12h"
          runbook: "https://runbooks.acme.com/checkout/disk-pressure"
```

## Interview tips

- "Page on symptoms, ticket on causes, and burn rate is the symptom" is the compressed answer.
- Give a target for pages per shift and say that deleting a non-actionable alert is a valid fix.
- Expect: "what would you do with an alert that fires weekly and is never real?" - delete or retune it, and say so without hedging.

---

[⬅ Back to Site Reliability Engineering (SRE)](./README.md) · [All topics](../README.md)
