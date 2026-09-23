---
title: "How Do You Reconcile Multi-Region Uptime Guarantees with Underlying Cloud Provider SLAs?"
id: 727
category: "SLA Management"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - sla-management
  - multi-region
  - composite-availability
quiz:
  stem: "Why can an application deployed across two 99.9% cloud regions still fail to achieve a 99.99% overall SLA?"
  options:
    - "Because multi-region deployments require twice the number of developer commits."
    - "Because global shared serial dependencies (such as DNS, IAM, or centralized databases) limit total composite availability to their individual lower SLAs."
    - "Because cloud providers automatically void SLAs when traffic crosses regional boundaries."
    - "Because TCP connections cannot route between geographic regions."
  answer: 2
  explanation: "Even if regional compute is redundant in parallel, any shared global component (such as Route 53, an identity provider, or a global database) acts as a serial bottleneck that bounds the overall composite availability."
---

# How Do You Reconcile Multi-Region Uptime Guarantees with Underlying Cloud Provider SLAs?

**Short answer:** Reconciling multi-region guarantees requires calculating parallel composite availability across regions, identifying single-point-of-failure shared global dependencies (DNS, IAM, control planes), and offering an application SLA that leaves an adequate risk margin above calculated limits.

## Detail

### The Arithmetic of Multi-Region Availability

A single cloud region typically offers a 99.9% to 99.99% availability SLA depending on the service. To offer an enterprise customer an aggressive SLA (e.g., 99.99% or 'four nines'), engineering must deploy across multiple independent regions in an active-active or active-passive pattern.

### Parallel Availability Calculation

When two regions operate in parallel, both regions must fail simultaneously for the entire service to go down:

$$A_{\text{parallel}} = 1 - (1 - A_{\text{region1}}) \times (1 - A_{\text{region2}})$$

If each region provides $99.9\%$ availability ($0.001$ failure probability):

$$A_{\text{parallel}} = 1 - (0.001 \times 0.001) = 1 - 0.000001 = 99.9999\% \text{ (Six Nines)}$$

### The Shared Global Component Trap (Serial Dependencies)

In reality, multi-region architectures are **never completely independent**. They rely on global shared services for DNS, global load balancing, and identity:

- Global DNS routing (AWS Route 53, Cloudflare)
- Global Control Plane / IAM
- Cross-region database replication (DynamoDB Global Tables, Aurora Global Database)

$$\text{Availability}_{\text{Total}} = A_{\text{DNS}} \times A_{\text{IAM}} \times A_{\text{Parallel Compute}}$$

```text
[User Request]
       │
       ▼
 [Global DNS (Route 53 / 100% SLA)] ◄─── Global Serial Dependency
       │
 ┌─────┴─────────────────────────┐
 ▼                               ▼
[Region A (99.9%)]              [Region B (99.9%)]
 └─────┬─────────────────────────┘
       ▼
 [Global Database Sync (99.99%)]    ◄─── Global Serial Dependency
```

If your global DNS SLA is $99.99\%$ and database replication is $99.99\%$, your composite maximum availability cannot exceed:

$$0.9999 \times 0.9999 \times 0.999999 = 99.98\%$$

Promising a 99.99% customer SLA under these conditions creates guaranteed financial liability over time.

**Provider SLAs are not availability predictions.** A provider SLA is a credit commitment, often defined per resource and per region with its own measurement rules; the real availability you get can be higher or lower. Use your own measured history for the model and the provider SLA only to size the financial backstop. Also remember the parallel formula assumes independent failures and instant failover - include failover detection time and correlated risks (the same bad deploy rolled to both regions) as downtime.

### Real-World Production Scenario

A healthtech startup promises a 99.99% availability SLA to hospital systems by deploying across AWS us-east-1 and us-west-2. However, both regions depend on a single third-party identity provider tenant for user authentication, whose SLA is only 99.9%. During an identity-provider outage, both regions fail to authenticate doctors, breaching the hospital SLA and triggering heavy contractual penalties.

## Example

```python
def parallel(*a):  # all must fail for the tier to fail
    p = 1.0
    for x in a:
        p *= 1 - x
    return 1 - p

regions = parallel(0.999, 0.999)   # 0.999999 in theory
dns     = 0.9999                   # planning figure, not Route 53's 100% SLA credit promise
idp     = 0.999                    # single global identity-provider tenant
db_sync = 0.9999

composite = dns * idp * db_sync * regions
print(f"{composite:.2%}")          # 99.88% -> the IdP, not the regions, is the ceiling
```

## Interview tips

- Demonstrate the formula for parallel components: $1 - (1 - A_1)(1 - A_2)$.
- Always highlight the risk of global shared components (DNS, IAM, global databases) that act as serial single points of failure.
- Explain why offering a 99.99% SLA is dangerous if your end-to-end composite calculation yields 99.95%.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SLA Management](./README.md) · [All topics](../README.md)
