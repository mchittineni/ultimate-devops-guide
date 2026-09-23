---
title: "What is Error Budget Burn-Rate Alerting and How Do You Tune Thresholds?"
id: 721
category: "SLO Engineering"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - slo-engineering
  - burn-rate
  - alerting
quiz:
  stem: "In Google SRE multi-window burn-rate alerting, what is the primary purpose of requiring the short window (e.g., 5 minutes) to exceed the burn threshold alongside the long window (e.g., 1 hour)?"
  options:
    - "To reduce the number of metrics collected by Prometheus."
    - "To ensure the alert only fires if the failure is still actively ongoing, preventing pages for brief transient spikes that have already resolved."
    - "To ensure that database queries are executed in parallel across all worker nodes."
    - "To calculate legal service credit percentages automatically."
  answer: 2
  explanation: "If a massive burst of errors lasts only 2 minutes and ends, the 1-hour average may remain elevated, but the short 5-minute window will have recovered. Requiring both ensures the system does not page on-call engineers for incidents that are already over."
---

# What is Error Budget Burn-Rate Alerting and How Do You Tune Thresholds?

**Short answer:** Burn-rate alerting measures how rapidly an error budget is being consumed relative to time. Multi-window, multi-burn-rate alerting combines short-window detection for catastrophic outages (e.g., 14.4x burn over 1 hour) with long-window detection for subtle degradation (e.g., 1x burn over 3 days) to eliminate alert fatigue.

## Detail

### The Failure of Traditional Threshold Alerts

Traditional alerting triggers when an error rate crosses a fixed static percentage (e.g., `error_rate > 1% for 5 minutes`). This causes two critical problems:

1. **Low-volume false alarms**: Brief transient spikes page engineers at 3 AM even though they consume negligible budget.
2. **Slow bleed misses**: A 0.5% error rate sustained over two weeks completely destroys a 99.9% monthly SLO budget without ever triggering the 1% alert threshold.

### Burn Rate Mechanics

A **Burn Rate of 1** means the service will consume exactly 100% of its error budget over the defined SLO period (typically 30 days).

- **Burn Rate 14.4**: Consumes 2% of budget in 1 hour; 100% of budget in 2 days. Requires immediate P1 paging.
- **Burn Rate 6**: Consumes 5% of budget in 6 hours; exhausts it in 5 days. Pages, but less urgently (P2).
- **Burn Rate 1**: Normal consumption rate.

$$\text{Burn Rate} = \frac{\text{Observed Error Rate}}{1 - \text{SLO Target}}$$

For a $99.9\%$ SLO ($0.1\%$ allowed error rate), an observed error rate of $1.44\%$ represents a burn rate of:

$$\text{Burn Rate} = \frac{1.44\%}{0.1\%} = 14.4$$

### Google SRE Multi-Window Multi-Burn-Rate Pattern

To prevent alerting on transient spikes that have already self-resolved, alerts require that both a **long window** (e.g., 1 hour) and a **short window** (e.g., 5 minutes) exceed the target burn rate simultaneously before paging.

```text
Long Window (1 Hour) Burn Rate > 14.4
                 AND
Short Window (5 Minutes) Burn Rate > 14.4
                 │
                 ├──► YES: Page On-Call Engineer (P1 Active Emergency)
                 └──► NO : Spike already ended; suppress page
```

### Recommended Alerting Matrix (30-Day Budget)

| Severity        | Burn Rate | % Budget Consumed | Long Window | Short Window | Notification Channel               |
| :-------------- | :-------- | :---------------- | :---------- | :----------- | :--------------------------------- |
| **Page (P1)**   | 14.4      | 2%                | 1 hour      | 5 minutes    | PagerDuty / Phone call             |
| **Page (P2)**   | 6.0       | 5%                | 6 hours     | 30 minutes   | PagerDuty / Escalation             |
| **Ticket (P3)** | 3.0       | 10%               | 1 day       | 2 hours      | Jira / Slack during business hours |
| **Ticket (P4)** | 1.0       | 10%               | 3 days      | 6 hours      | Weekly reliability review          |

Budget consumed = burn rate x long window / SLO period, e.g. 3 x 1 day / 30 days = 10%. The two page rows are the Google SRE Workbook's recommendation; the 3x/1-day ticket row is a common addition (it is part of Sloth's defaults).

### Tuning Thresholds

- **Low traffic**: with a few requests per minute, a single failure is a huge burn rate. Lengthen windows, alert on minimum failure counts (`and sum(increase(errors[1h])) > 10`), or use synthetic traffic.
- **Measure precision and recall**: review every page for a month - pages that were not real mean the thresholds are too low or the windows too short; incidents that were found by humans first mean they are too high.
- **Different SLO windows**: for a 28-day window, recompute the multipliers (e.g. 2% of a 28-day budget in 1 hour is a burn rate of 13.44, not 14.4).

### Real-World Production Scenario

A payment gateway experiences a misconfigured DNS update that drops 15% of transactions. The 14.4x burn rate alert triggers within about six minutes (the time for 15% errors to push the 1-hour average above 1.44%, plus the `for` duration), paging the on-call engineer before more than 2% of the monthly budget is lost. Later, a minor third-party partner timeout causes a sustained 0.2% error rate (2x burn); rather than waking someone up at midnight, the 1x/3-day ticket alert routes it to the team queue for the following morning.

## Example

```yaml
# Sloth generates all four windows (page + ticket) from one definition
version: prometheus/v1
service: payment-gateway
slos:
  - name: requests-availability
    objective: 99.9
    sli:
      events:
        error_query: sum(rate(http_requests_total{job="payment-gateway",code=~"5.."}[{{.window}}]))
        total_query: sum(rate(http_requests_total{job="payment-gateway"}[{{.window}}]))
    alerting:
      name: PaymentGatewayAvailability
      page_alert: { labels: { severity: page } } # 14.4x/1h+5m and 6x/6h+30m
      ticket_alert: { labels: { severity: ticket } } # 3x/1d+2h and 1x/3d+6h
```

## Interview tips

- Explain why the short window is essential: it confirms that the error condition is still actively happening right now, preventing pages for spikes that already finished.
- Know the Google SRE formula for 14.4x burn rate: it consumes 2% of the monthly error budget in exactly one hour.
- Contrast burn-rate alerting with simple static percentage threshold alerting.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[What is progressive delivery and how does it differ from traditional deployment strategies?]] (`#509`): [What is progressive delivery and how does it differ from traditional deployment strategies?](../core-devops-concepts/what-is-progressive-delivery-and-how-does-it-differ-from-traditional-deployment-strategies.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SLO Engineering](./README.md) · [All topics](../README.md)
