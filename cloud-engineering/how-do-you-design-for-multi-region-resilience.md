---
title: "How do you design for multi-region resilience?"
id: 218
category: "Cloud Engineering"
difficulty: "Advanced"
tags:
  - devops
  - cloud-engineering
  - interview-questions
---

# How do you design for multi-region resilience?

**Short answer:** Decide the recovery objectives first, then pick the cheapest pattern that meets them: multi-AZ within one region (covers most failures), active-passive with a warm standby, or active-active. The hard part is never compute - it is data replication, state, and whether you have actually rehearsed a failover.

## Detail

| Pattern              | RTO         | RPO         | Cost   | Real difficulty                      |
| -------------------- | ----------- | ----------- | ------ | ------------------------------------ |
| Multi-AZ, one region | minutes     | near zero   | low    | none beyond good practice            |
| Backup and restore   | hours–days  | hours       | lowest | restore is slow and rarely tested    |
| Pilot light          | tens of min | minutes     | low    | scaling up under pressure            |
| Warm standby         | minutes     | seconds–min | medium | keeping the standby actually current |
| Active-active        | seconds     | ~zero       | high   | write conflicts, data consistency    |

**Most outages are not regional.** Availability zones cover hardware, power, and network failures, which is the majority. Region-wide failures happen, but frequently the practical outage is a control-plane degradation in one region that a multi-region design only helps with if your failover path does not itself depend on that control plane. Multi-AZ first, and be honest about what a second region buys.

**Data is the constraint.** Synchronous replication across regions adds tens of milliseconds to every write and creates a distributed-consistency problem; asynchronous replication means a non-zero RPO - you will lose the last few seconds of writes. Active-active with a relational database means resolving conflicting writes, which is an application design problem (region-partitioned data, last-write-wins with vector clocks, or CRDTs), not an infrastructure toggle. Globally distributed databases (Spanner, DynamoDB global tables, Cosmos DB, Aurora Global) trade cost and semantics for solving part of this.

**Failover must not depend on the failed region.** Common self-inflicted wounds: DNS records or health checks managed from the primary region, the CI/CD pipeline that would deploy the standby, secrets or a container registry that exists only in region A, and the runbook stored in a wiki hosted there. Enumerate every dependency in the failover path and confirm it survives the loss.

**Data residency and latency shape the design as much as resilience.** If EU data may not leave the EU, "multi-region" means multiple EU regions, and an active-active design must partition users by region rather than route freely. That partitioning often makes the design simpler and cheaper - each region owns its own data.

**Practise it, or you do not have it.** Regular, scheduled failover exercises - ideally with real traffic - are the only way to learn that a DNS TTL is 3600, that a replica had drifted, or that nobody has permissions in the standby account. Untested disaster recovery reliably fails when needed; publishing the tested RTO rather than the aspirational one is the mark of a mature team.

## Example

```text
Warm standby that has actually been tested

Traffic     global anycast LB or latency/health-based DNS -> region A (primary)
            health check from 3 external locations; failover TTL 60 s
Compute     region B running at 20% capacity, autoscaling headroom pre-approved,
            same image digests, deployed by the same pipeline every release
Data        primary in A; cross-region async replica in B (RPO ~ 10 s measured)
            object storage replicated both ways; secrets and registry present in both
Failover    promote replica -> scale B -> shift traffic -> revoke A's writes
            one command, no ticket, permissions pre-granted in B
Dependencies checked: DNS control plane (global), CI (multi-region), IdP (SaaS),
            runbook (in Git, mirrored), on-call tooling (SaaS)
Rehearsal   quarterly, in business hours, with a rollback plan; last tested RTO 11 min
```

## Interview tips

- Ask for RTO/RPO before proposing an architecture - jumping straight to active-active is the classic overreach.
- "Failover must not depend on the failed region" plus one concrete example (DNS or CI) is a memorable point.
- Expect: "what is your RTO?" - quote the _tested_ number and say when you last rehearsed.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Engineering](./README.md) · [All topics](../README.md)
