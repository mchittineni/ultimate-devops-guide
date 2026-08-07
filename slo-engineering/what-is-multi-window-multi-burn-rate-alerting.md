---
title: "What is multi-window multi-burn-rate alerting?"
id: 178
category: "SLO Engineering"
difficulty: "Advanced"
tags:
  - devops
  - slo-engineering
  - interview-questions
---

# What is multi-window multi-burn-rate alerting?

**Short answer:** Instead of alerting when an error rate crosses a fixed threshold, you alert on how fast the error budget is being consumed. Two burn-rate conditions run in parallel - a fast one (page: a large fraction of the budget in hours) and a slow one (ticket: steady erosion over days) - and each requires both a long and a short window to fire, so alerts are sensitive without being flappy.

## Detail

**Burn rate defined.** Burn rate is the ratio of the observed error rate to the rate that would exactly exhaust the budget over the SLO window. Burning at 1× spends the budget precisely by the end of the window; 14.4× spends a 30-day budget in about two days.

**Why a short window is paired with the long one.** The long window (say 6 hours) gives statistical confidence and low false-positive rate; alone it also stays firing long after the incident ends. Adding a short window (30 minutes, one twelfth of the long one) as an AND condition means the alert clears quickly once the burn stops. This pairing is the "multi-window" half.

**The canonical configuration** from the Google SRE workbook, for a 30-day window:

| Severity | Burn rate | Long window | Short window | Budget consumed when it fires |
| -------- | --------- | ----------- | ------------ | ----------------------------- |
| Page     | 14.4×     | 1 hour      | 5 minutes    | 2%                            |
| Page     | 6×        | 6 hours     | 30 minutes   | 5%                            |
| Ticket   | 3×        | 1 day       | 2 hours      | 10%                           |
| Ticket   | 1×        | 3 days      | 6 hours      | 10%                           |

**What it fixes.** A static "error rate > 1%" threshold pages at 3am for a two-minute blip that consumed 0.1% of the budget, and stays silent during a 0.5% error rate that will burn the entire month. Burn-rate alerting ties the page to consequence: you are woken only when the budget is genuinely at risk.

**Practical cautions.** Low-traffic services produce noisy ratios - either aggregate to a longer window, alert on absolute failure counts, or accept fewer, coarser alerts. Precompute the SLI ratio as a recording rule so alert expressions stay readable, and keep the ratio numerator and denominator consistent between the fast and slow rules.

## Example

```yaml
# Prometheus: recording rule for the SLI, then a fast-burn page
groups:
  - name: checkout-slo
    rules:
      - record: job:sli_error_ratio:rate5m
        expr: |
          sum(rate(http_requests_total{job="checkout",code=~"5.."}[5m]))
            / sum(rate(http_requests_total{job="checkout"}[5m]))
      - record: job:sli_error_ratio:rate1h
        expr: |
          sum(rate(http_requests_total{job="checkout",code=~"5.."}[1h]))
            / sum(rate(http_requests_total{job="checkout"}[1h]))
      - alert: CheckoutErrorBudgetFastBurn
        # 14.4 x (1 - 0.999) = 0.0144
        expr: |
          job:sli_error_ratio:rate1h > 0.0144
            and job:sli_error_ratio:rate5m > 0.0144
        for: 2m
        labels: { severity: page }
        annotations:
          summary: "Checkout burning error budget at 14.4x - 2% of the 30d budget gone"
```

## Interview tips

- Define burn rate as a multiplier of the budget-exhausting rate; that one sentence carries the concept.
- Explain the short window's purpose (fast reset, less flapping) - most candidates only mention the long one.
- Expect: "what about a service with 10 requests a minute?" Say the ratio is too noisy and describe the alternatives.

---

[⬅ Back to SLO Engineering](./README.md) · [All topics](../README.md)
