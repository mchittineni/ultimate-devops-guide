---
title: "What do you need before you can set your first SLO?"
id: 304
category: "SLO Engineering"
difficulty: "Beginner"
tags:
  - devops
  - slo-engineering
  - interview-questions
---

# What do you need before you can set your first SLO?

**Short answer:** Four things, in order: a **user journey** worth measuring (not a component), an **SLI** that can be computed from data you already collect, **historical data** to see what your reliability actually is today, and an **owner** who can act when the target is missed. If you cannot name the journey or you have no data, you are not ready to pick a number - and a target picked without data is just a wish that will be ignored the first time it is breached.

## Detail

**1 - Pick a user journey, not a component.** SLOs measure what users experience. "The checkout API returns successfully" is a good starting scope; "the database has 99.9% uptime" is not, because a healthy database with a broken cache still means a broken checkout. Start with the one or two journeys that matter most - log in, search, add to cart, check out - and accept that internal components can wait. If you cannot describe the journey in a sentence a non-engineer understands, the scope is wrong.

**2 - Define an SLI you can actually compute.** An SLI is a ratio: good events over valid events. The two that cover most services:

- **Availability** - successful requests ÷ all valid requests. Decide what "successful" means (usually not-5xx; 4xx is often the client's fault and should be excluded from _good_ and possibly from _valid_ too), and decide what "valid" excludes (health checks, bot traffic, requests from your own load tests).
- **Latency** - requests faster than a threshold ÷ all valid requests. Note the shape: it is a _count of fast requests_, not an average. "95% of requests complete within 300ms" is an SLI; "average latency is 200ms" is not, because averages hide the users having a bad time.

Measure it as close to the user as you can. Load balancer or CDN metrics beat application-side metrics, because they include the requests your app never saw.

**3 - Look at the data before choosing a number.** Compute the SLI over the last 30-90 days. Your target should be a small, deliberate step from reality: if you are at 99.5%, set 99.5% or 99.6% - not 99.99%, which would put you permanently in breach and teach everyone to ignore the SLO. And the target must be _achievable and worth achieving_: every extra nine costs real money and engineering time, so the right question is "what do users actually notice, and what would they pay for?" A 99.9% monthly target allows about 43 minutes of downtime; 99.99% allows about 4 minutes, which is less than the time it takes a human to respond to a page - meaning you now need automated failover, and that is a budget conversation.

**4 - Name an owner and decide what happens when you miss.** The **error budget** is the inverse of the target - 0.1% of requests may fail at 99.9% - and it is the whole point: spend it on releases and risk, and when it is exhausted, something changes. Agree that in advance (an error budget policy: freeze risky changes, prioritise reliability work) with the team and their product owner. An SLO with no consequence is a dashboard, not an agreement.

**What you do not need yet.** Perfect instrumentation, a full observability platform, SLOs for every service, or agreement on a formal SLA with customers. Start with one journey, one or two SLIs, a 28- or 30-day rolling window, and a review after a month. The first version being roughly right is the goal; you will revise it once real data arrives, and that is expected rather than a failure.

**Common first-attempt mistakes:** setting 99.99% because it sounds serious; measuring CPU or uptime instead of user-visible success; using averages for latency; forgetting to exclude health checks and bots, which inflates the numbers; SLOs on 40 components before any on a user journey; and no agreement about what happens on a breach.

## Example

```text
The four prerequisites, filled in

1 JOURNEY   "A customer completes checkout"
            served by: web → api-gateway → checkout-svc → payments → db

2 SLI       availability = non-5xx responses to POST /checkout ÷ valid requests
            latency      = POST /checkout responses < 800ms ÷ valid requests
            valid excludes: /healthz, requests tagged synthetic=true, known bots
            measured at:   the load balancer (closest to the user)

3 DATA      last 90 days: availability 99.62%, latency-under-800ms 97.1%
            → target: 99.6% availability, 97% latency, 28-day rolling window
            → error budget: 0.4% of requests ≈ 2h 42m of full outage per 28 days

4 OWNER     checkout team · product owner agreed the budget policy:
            budget exhausted → feature work pauses, reliability work prioritised
            review the SLO itself after one month
```

```promql
# The SLI as a query. Note what is excluded, and that latency counts fast requests.
#
# Define "valid request" ONCE and paste it into every numerator and denominator, unchanged.
# A filter that appears on only one side of a ratio is the classic SLI bug: it divides one
# population by a different one, and the number quietly stops meaning anything.
#   VALID := route="/checkout", route!~"/healthz|/readyz|/metrics",
#            synthetic!="true", user_agent!~"(?i).*(bot|crawler|spider).*"
# (The health-check exclusion is redundant while route is pinned - keep it anyway, because
#  the day someone widens this to route=~"/api/.*" it is the filter they will forget.)

# Availability - VALID on both sides, only code!~"5.." differs
sum(rate(http_requests_total{route="/checkout", route!~"/healthz|/readyz|/metrics",
    synthetic!="true", user_agent!~"(?i).*(bot|crawler|spider).*", code!~"5.."}[28d]))
  /
sum(rate(http_requests_total{route="/checkout", route!~"/healthz|/readyz|/metrics",
    synthetic!="true", user_agent!~"(?i).*(bot|crawler|spider).*"}[28d]))

# Latency: the fraction under the threshold - not an average.
# The _count denominator takes the same VALID selector as the _bucket numerator; only le= differs.
sum(rate(http_request_duration_seconds_bucket{route="/checkout", route!~"/healthz|/readyz|/metrics",
    synthetic!="true", user_agent!~"(?i).*(bot|crawler|spider).*", le="0.8"}[28d]))
  /
sum(rate(http_request_duration_seconds_count{route="/checkout", route!~"/healthz|/readyz|/metrics",
    synthetic!="true", user_agent!~"(?i).*(bot|crawler|spider).*"}[28d]))

# Error budget REMAINING, as a fraction of the budget - the number the team actually watches.
# 1.0 = untouched, 0 = exhausted. clamp_min stops an overspent budget going negative.
clamp_min(
  (
    (1 - 0.996)                                  # allowed failure fraction
      - (1 - <availability_query>)               # observed failure fraction
  ) / (1 - 0.996),
  0
)
```

| Target | Allowed downtime / 30 days | What it implies                                  |
| ------ | -------------------------- | ------------------------------------------------ |
| 99%    | ~7h 12m                    | Internal tools, batch systems                    |
| 99.9%  | ~43m                       | A human can respond to a page in time            |
| 99.95% | ~21m                       | Fast automated rollback needed                   |
| 99.99% | ~4m                        | Automated failover; a human cannot react in time |

## Interview tips

- Give the four prerequisites in order - journey, SLI, historical data, owner with a policy. The ordering is what makes it sound like practice rather than theory.
- "Measure the user journey, not the component" is the sentence to lead with. Uptime SLOs on infrastructure are the classic beginner error.
- Say that latency SLIs count requests under a threshold rather than averaging. Interviewers listen specifically for this.
- Insist on measuring current reality before choosing a target, and on the target being a small step from it. Aspirational nines are how SLOs get ignored.
- Know the downtime arithmetic for 99.9% and 99.99% off the top of your head, and connect 99.99% to needing automated failover.
- Mention excluding health checks, bots, and synthetic traffic from the denominator. It shows you have computed one for real.
- Close on the error budget policy. An SLO without an agreed consequence is just a dashboard, and saying so demonstrates you understand the purpose.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SLO Engineering](./README.md) · [All topics](../README.md)
