---
title: "What is the Difference Between Request-Based and Window-Based SLIs?"
id: 718
category: "SLO Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - slo-engineering
  - sli
  - sre-metrics
quiz:
  stem: "Why are window-based (time-slice) SLIs frequently preferred over request-based SLIs for low-throughput enterprise services?"
  options:
    - "Window-based SLIs eliminate the need to collect monitoring metrics."
    - "In low-traffic services, a single failed request can dramatically drop a request-based percentage and cause false alarms, whereas window-based SLIs measure whether the service was healthy during each time bucket."
    - "Window-based SLIs are required by cloud providers to issue service credits."
    - "Request-based SLIs cannot measure HTTP 500 error responses."
  answer: 2
  explanation: "In low-throughput services, small request counts distort request-based percentages (e.g., 1 failure in 5 requests = 80% availability). Window-based SLIs evaluate whether each discrete time interval satisfied health criteria, avoiding low-volume distortion."
---

# What is the Difference Between Request-Based and Window-Based SLIs?

**Short answer:** Request-based SLIs evaluate reliability as the ratio of successful requests to total requests over a period. Window-based SLIs evaluate the percentage of discrete time windows (e.g., 1-minute or 5-minute intervals) during which performance met defined quality thresholds.

## Detail

### Measuring Reliability: Requests vs Time

Service Level Indicators (SLIs) must accurately represent user happiness. The choice between request-based and window-based SLIs directly influences how traffic spikes, off-peak incidents, and long-tail latencies impact your error budget.

### Request-Based SLIs

A request-based SLI evaluates each individual transaction or request against a quality criterion.

$$\text{SLI}_{\text{request}} = \frac{\sum \text{Successful Requests}}{\sum \text{Total Valid Requests}} \times 100\%$$

- **Best For**: High-throughput web APIs, payment gateways, and microservices where every single user interaction matters equally.
- **Traffic Sensitivity**: Heavy traffic periods contribute proportionally more to the SLI. An outage during peak traffic burns the error budget much faster than an identical outage at 3 AM on a Sunday.

### Window-Based SLIs (Time-Slice SLIs)

A window-based SLI divides time into discrete intervals (e.g., 1-minute or 5-minute slices). A window is considered 'good' if performance metrics during that interval satisfy defined conditions (e.g., error rate $< 1\%$ and 99th percentile latency $< 300\text{ms}$).

$$\text{SLI}_{\text{window}} = \frac{\sum \text{Good Windows}}{\sum \text{Total Measurement Windows}} \times 100\%$$

- **Best For**: Low-throughput systems, asynchronous batch processors, streaming pipelines, and enterprise SaaS where users expect continuous platform availability regardless of instantaneous volume.
- **Traffic Sensitivity**: Equalizes off-peak and on-peak hours. An outage at midnight counts the exact same number of bad windows as an outage at noon.

### Comparison Summary

| Attribute               | Request-Based SLI                                                | Window-Based (Time-Slice) SLI                             |
| :---------------------- | :--------------------------------------------------------------- | :-------------------------------------------------------- |
| **Mathematical Unit**   | Count of requests                                                | Count of minutes/intervals                                |
| **Low-Volume Behavior** | Single failed request during low volume heavily skews percentage | Absorbed if the rest of the window meets threshold        |
| **High-Volume Outage**  | Exhausts budget rapidly in direct proportion to dropped volume   | Caps maximum budget loss to the minutes the outage lasted |
| **Common Use Cases**    | Public REST/gRPC endpoints, e-commerce checkouts                 | Background daemons, internal portals, data ingestion      |

### Real-World Production Scenario

An enterprise payroll system serves 100,000 requests on a Friday afternoon, but only about 10 requests per minute on Tuesday night. An engineer misconfigures a database connection on Tuesday night, causing every request to fail for 15 minutes. Under a request-based SLI over a monthly window of about 1,000,000 requests, 150 failed requests are 0.015% - they barely dent a 99.9% budget of 1,000 failures. Under a window-based SLI, 15 consecutive minutes of 100% failure correctly flag a serious service impairment.

## Example

```promql
# Request-based: good requests / all requests over 28 days
sum(rate(http_requests_total{job="payroll",code!~"5.."}[28d]))
  / sum(rate(http_requests_total{job="payroll"}[28d]))

# Window-based: fraction of 1-minute windows where error ratio < 1% AND p99 < 300 ms
avg_over_time(
  (
    (
      sum(rate(http_requests_total{job="payroll",code=~"5.."}[1m]))
        / sum(rate(http_requests_total{job="payroll"}[1m])) < bool 0.01
    )
    *
    (
      histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket{job="payroll"}[1m]))) < bool 0.3
    )
  )[28d:1m]
)
```

Minutes with no traffic produce no sample and drop out of the window count, which is one reason window-based SLIs for very quiet services are often paired with a synthetic probe.

## Interview tips

- Explain that low-traffic services often fail with request-based SLIs because 1 failed request out of 10 drops the SLI to 90%, triggering false alarms.
- Discuss the common guidance: request-based SLIs for high-volume synchronous HTTP/gRPC services, window-based SLIs for batch or low-traffic services - and the trade-off that window-based SLIs undercount a short, total outage at peak (one bad minute is one bad minute, however many users hit it).
- Note that window-based SLIs allow combining multiple conditions (e.g., latency AND error rate) into a single pass/fail evaluation per minute.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SLO Engineering](./README.md) · [All topics](../README.md)
