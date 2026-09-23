---
title: "What are the differences between Active-Active and Active-Passive multi-region disaster recovery architectures?"
id: 593
category: "Scalability and High Availability"
difficulty: "Intermediate"
tags:
  - devops
  - scalability-and-high-availability
  - interview-questions
  - high-availability
  - multi-region
  - disaster-recovery
  - architecture
quiz:
  stem: "What is the primary technical challenge when implementing a multi-region Active-Active architecture for transactional databases?"
  options:
    - "Linux kernels cannot communicate across international boundaries"
    - "Speed-of-light network latency prevents low-latency synchronous writes, forcing complex asynchronous conflict resolution"
    - "Cloud providers prohibit the use of DNS across multiple regions"
    - "Active-Active databases cannot store binary data"
  answer: 2
  explanation: "Because physical latency across global regions is tens of milliseconds, synchronous cross-region commits make transactions slow, while asynchronous writes risk data conflicts."
---

# What are the differences between Active-Active and Active-Passive multi-region disaster recovery architectures?

**Short answer:** In Active-Active, all regions serve live customer traffic simultaneously with cross-region data synchronization, providing near-zero RTO; in Active-Passive, primary region serves traffic while secondary region remains on standby (warm or cold) until failover is triggered.

## Detail

Designing multi-region infrastructure balances business Recovery Time Objectives (RTO) and Recovery Point Objectives (RPO) against operational cost and complexity.

### Comparison

| Dimension         | Active-Passive (Pilot Light / Warm Standby)                                            | Active-Active (Multi-Region Live)                                                                        |
| ----------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Traffic           | 100% of traffic handled by the primary region                                          | Traffic split across regions by geo-proximity or latency                                                 |
| Database strategy | Read/write primary in Region 1; asynchronous cross-region replica in Region 2          | Multi-writer (DynamoDB Global Tables, Spanner, CockroachDB, Aurora DSQL) or per-region data partitioning |
| Failover (RTO)    | Minutes to hours: detect, decide, promote the replica, shift DNS, scale up the standby | Seconds to minutes: health checks pull the failed region out of rotation                                 |
| Data loss (RPO)   | Seconds to minutes - whatever async replication had not shipped                        | Zero with synchronous/strongly consistent replication; otherwise the async window                        |
| Write latency     | Fast (local to the primary)                                                            | Higher if cross-region consensus is required on every write                                              |
| Cost & complexity | Lower (standby can run at a fraction of capacity)                                      | High (each region sized to absorb the others' traffic; conflict handling; harder testing)                |

### The data dilemma in active-active

The round trip between US-East and EU-West is roughly 70-80 ms, so a synchronous cross-region commit adds that to every write. That leaves three honest options:

- **Asynchronous multi-writer** (DynamoDB global tables in the default multi-Region eventual consistency mode, Cassandra across data centres): fast local writes, but concurrent edits to the same item in two regions conflict and are resolved - usually by last-writer-wins, which silently discards one update.
- **Strongly consistent multi-region** (Spanner, CockroachDB, DynamoDB global tables with multi-Region strong consistency, Aurora DSQL): RPO of zero and no conflicts, paid for with cross-region latency on writes and a quorum that must span regions.
- **Partition ownership ("cell" or "home region")**: each user or tenant is written in exactly one region, so there are no write conflicts; the other regions serve reads or take over ownership on failover.

**Trade-offs people miss.** Active-active only delivers its RTO if each region has the capacity to absorb a failed peer's load - two regions running at 70% each cannot absorb each other. Active-passive fails most often at the _decision_: failover is a human-approved step, the standby has drifted, or nobody has rehearsed it. Whichever you choose, test it with real failovers, and watch for hidden single-region dependencies (an IAM or DNS control plane, a third-party API, a single-region secrets store).

## Example

```hcl
# Active-passive at the DNS layer: Route 53 failover records driven by a health check.
resource "aws_route53_health_check" "primary" {
  fqdn              = "api-use1.example.com"
  type              = "HTTPS"
  resource_path     = "/healthz"
  failure_threshold = 3
  request_interval  = 10
}

resource "aws_route53_record" "primary" {
  zone_id         = var.zone_id
  name            = "api.example.com"
  type            = "A"
  set_identifier  = "primary"
  health_check_id = aws_route53_health_check.primary.id
  failover_routing_policy { type = "PRIMARY" }
  alias {
    name                   = aws_lb.use1.dns_name
    zone_id                = aws_lb.use1.zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "secondary" {
  zone_id        = var.zone_id
  name           = "api.example.com"
  type           = "A"
  set_identifier = "secondary"
  failover_routing_policy { type = "SECONDARY" }
  alias {
    name                   = aws_lb.euw1.dns_name
    zone_id                = aws_lb.euw1.zone_id
    evaluate_target_health = true
  }
}
# Active-active would instead use latency-based records for both regions,
# each with its own health check - and a data layer that accepts writes in both.
```

## Interview tips

- Define both in one line each, then go straight to RTO, RPO, and cost - that is the real comparison.
- The data layer is the hard part. Explain the speed-of-light problem and the three options: async with conflict resolution, strongly consistent with latency, or per-user home regions.
- Say what last-writer-wins actually does - it discards an update - rather than naming it as a solution.
- Capacity is a common trap: active-active needs each region sized to take over a failed peer's traffic.
- DNS failover is not instant - health-check intervals plus client TTL caching add minutes; global anycast load balancers react faster.
- Close with testing: an unrehearsed failover plan is a hypothesis, not a DR capability.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scalability and High Availability](./README.md) · [All topics](../README.md)
