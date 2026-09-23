---
title: "What is Multi-Window Multi-Burn-Rate alerting and why does it eliminate alert fatigue?"
id: 642
category: "Site Reliability Engineering (SRE)"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - sre
  - burn-rate
  - alerting
  - prometheus
  - slo
quiz:
  stem: "Why does Google SRE recommend checking both a long window (e.g. 1 hour) and a short window (e.g. 5 minutes) in Multi-Window Burn Rate alerting?"
  options:
    - "Because Prometheus cannot compute metrics over a single window"
    - "To ensure that brief, self-resolving error spikes reset the alert quickly and prevent unnecessary on-call pages"
    - "To reduce the number of Prometheus servers required"
    - "To guarantee that all alerts result in immediate server reboots"
  answer: 2
  explanation: "If a spike lasts only 2 minutes, it burns budget briefly but poses no threat to the monthly SLO. The short window check clears as soon as the spike subsides, preventing noisy on-call wake-ups."
---

# What is Multi-Window Multi-Burn-Rate alerting and why does it eliminate alert fatigue?

**Short answer:** Multi-Window Multi-Burn-Rate alerting calculates how fast the error budget is being consumed over multiple time windows (short and long), paging humans only for catastrophic burns that will exhaust the monthly budget quickly while preventing noise on transient spikes.

## Detail

Traditional alerting (e.g. 'Page if CPU > 80% for 5 minutes' or 'Page if errors > 1%') results in severe alert fatigue: on-call engineers are woken up at 3 a.m. for temporary spikes that resolve themselves in 2 minutes.

### The Math of Burn Rate

A **Burn Rate of 1** means the entire 30-day error budget will be consumed in exactly 30 days.

- **Burn Rate 14.4**: Consumes **2% of the budget in 1 hour**. This is an emergency! **Page the on-call engineer immediately.**
- **Burn Rate 6**: Consumes **5% of the budget in 6 hours**. Urgent: Page engineer.
- **Burn Rate 1 (over 3 days)**: Consumes 10% of the budget in 3 days. Do not page; file a ticket.

### The Dual-Window Requirement (Short + Long)

To avoid false alarms from transient blips:

- An alert only fires if **both** a long window (e.g. 1 hour) AND a short window (e.g. 5 minutes, one-twelfth of the long one) are simultaneously burning at that rate.
- The long window provides significance (a brief blip cannot push a 1-hour average over 14.4x); the short window makes the alert **reset quickly** once the burn stops, instead of firing for the next hour.
- Combined with a short `for:` duration, a spike that ends before the condition has held stops alerting without paging anyone.

**Limitations.** It needs enough traffic for the ratios to be meaningful - on a service with a handful of requests per minute, one failure is a huge burn rate. And it only works for SLOs you have actually defined; a failure mode the SLI does not capture will never burn budget.

## Example

```yaml
# Prometheus rules for a 99.9% SLO (budget = 0.001). Recording rules for each window assumed.
groups:
  - name: checkout-burn-rate
    rules:
      - alert: CheckoutBurnRateFast
        expr: |
          job:slo_errors_per_request:ratio_rate1h{job="checkout"} > (14.4 * 0.001)
          and
          job:slo_errors_per_request:ratio_rate5m{job="checkout"} > (14.4 * 0.001)
        for: 2m
        labels: { severity: page }
      - alert: CheckoutBurnRateMedium
        expr: |
          job:slo_errors_per_request:ratio_rate6h{job="checkout"} > (6 * 0.001)
          and
          job:slo_errors_per_request:ratio_rate30m{job="checkout"} > (6 * 0.001)
        for: 15m
        labels: { severity: page }
      - alert: CheckoutBurnRateSlow
        expr: |
          job:slo_errors_per_request:ratio_rate3d{job="checkout"} > (1 * 0.001)
          and
          job:slo_errors_per_request:ratio_rate6h{job="checkout"} > (1 * 0.001)
        for: 1h
        labels: { severity: ticket }
```

## Interview tips

- Replacing threshold alerts (CPU > 80%) with budget burn rate alerts.
- Burn rate measuring speed of error budget consumption.
- Requiring both long and short windows to avoid waking humans for transient blips.
- Paging only when budget will be exhausted within hours.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Error Budget Burn-Rate Alerting and How Do You Tune Thresholds?]] (`#721`): [What is Error Budget Burn-Rate Alerting and How Do You Tune Thresholds?](../slo-engineering/what-is-error-budget-burn-rate-alerting-and-how-do-you-tune-thresholds.md)
- [[What are Incident Severity Levels (Sev-1 to Sev-4) and how do they govern response SLAs and war rooms?]] (`#675`): [What are Incident Severity Levels (Sev-1 to Sev-4) and how do they govern response SLAs and war rooms?](../incident-management/what-are-incident-severity-levels-sev-1-to-sev-4-and-how-do-they-govern-response-slas-and-war-rooms.md)
- [[What is the Difference Between an SLA, an SLO, and an OLA?]] (`#724`): [What is the Difference Between an SLA, an SLO, and an OLA?](../sla-management/what-is-the-difference-between-an-sla-an-slo-and-an-ola.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Site Reliability Engineering (SRE)](./README.md) · [All topics](../README.md)
