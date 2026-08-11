---
title: "How do you calculate composite availability across dependencies?"
id: 186
category: "SLA Management"
difficulty: "Advanced"
tags:
  - devops
  - sla-management
  - interview-questions
---

# How do you calculate composite availability across dependencies?

**Short answer:** Components in series multiply (`A × B × C`), so availability always falls; redundant components in parallel combine as `1 − (1−A)^n`, so availability rises. Model the request path as a graph of serial and parallel segments, and the result is the ceiling on any SLA you can honestly offer.

## Detail

**Serial - every hop must work.** A request through CDN (99.99%), load balancer (99.99%), application (99.95%), and database (99.95%) yields `0.9999 × 0.9999 × 0.9995 × 0.9995 ≈ 99.88%` - worse than every individual component. This is why "our cloud provider offers 99.99%" never translates into a 99.99% product.

**Parallel - one of n must work.** Two independent replicas at 99.9% give `1 − 0.001² = 99.9999%` in theory. Reality is lower because of correlated failure and because failover is not instant.

**Correlated failure is where the maths misleads.** Two AZs in the same region share a control plane; two instances share a deployment pipeline, a config store, and a bad release. If a common cause takes out both, independence does not hold and the parallel formula overstates reality badly. Add an explicit common-cause term or, more practically, treat the shared component as a serial element in the model.

**Failover cost is real.** Health-check detection plus DNS TTL plus connection re-establishment can be minutes. A model showing five nines with a two-minute failover is arithmetic, not availability - include the switch time as downtime per failover event.

**Degradation breaks the serial chain productively.** If the recommendation service is optional, its availability drops out of the serial product entirely. Rewriting a hard dependency as a soft one is usually cheaper than adding redundancy, and it is the strongest answer to "how do you get another nine?".

## Example

```python
def serial(*a):   # every component must be up
    out = 1.0
    for x in a:
        out *= x
    return out

def parallel(a, n=2):  # any one of n identical components suffices
    return 1 - (1 - a) ** n

# Single-AZ request path
serial(0.9999, 0.9999, 0.9995, 0.9995)      # 0.99880 -> 99.88%

# Redundant app tier and database, still serial through CDN and LB
serial(0.9999, 0.9999, parallel(0.9995), parallel(0.9995))  # ~0.99980 -> 99.98%

# Honest version: both replicas share one deployment pipeline (99.99%) and
# failover costs ~2 min per event; add the shared component as a serial term
serial(0.9999, 0.9999, parallel(0.9995), parallel(0.9995), 0.9999)  # ~99.97%
```

## Interview tips

- Reproduce both formulas without hesitation - serial multiplies, parallel is `1 − (1−A)^n`.
- Volunteer the correlated-failure caveat; that is what separates an engineer from a spreadsheet.
- The strong close: "the cheapest additional nine usually comes from making a dependency optional, not from adding replicas."

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SLA Management](./README.md) · [All topics](../README.md)
