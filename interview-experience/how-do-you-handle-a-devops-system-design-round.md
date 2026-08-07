---
title: "How do you handle a DevOps system design round?"
id: 294
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
---

# How do you handle a DevOps system design round?

**Short answer:** Spend the first five minutes on requirements, not boxes. Establish scale, availability target, and constraints; state your assumptions out loud; sketch the happy path end to end; then go deep exactly where the interviewer pushes. A DevOps design round is graded differently from a developer one - they care less about your data model and more about **how it is deployed, how it fails, how you know, and what it costs**. Say the trade-off you are accepting on every choice, and finish with what you would do differently at ten times the scale.

## Detail

**What the round is actually testing.** Whether you can take a vague prompt ("design the infrastructure for a multi-tenant SaaS", "design the CI/CD for 200 microservices") and produce a defensible system while thinking aloud. The scoring is on structure, trade-off awareness, failure reasoning, and operability - not on arriving at their preferred diagram.

**Minutes 0-5: requirements, before any drawing.** Ask, and write the answers where both of you can see them:

- **Scale** - requests per second, data volume, growth rate, read/write ratio, number of services and teams.
- **Availability and latency targets** - is this 99.9% or 99.99%? Regional or global? What is the p99 budget? These numbers, not taste, decide multi-region.
- **RPO and RTO** - how much data loss and how much downtime is acceptable. This decides the database topology.
- **Constraints** - existing cloud provider, compliance and data residency, team size and skills, budget, migration or greenfield.
- **What is out of scope** - say it explicitly so you are not judged on what you skipped.

If the interviewer will not give numbers, propose them: "I will assume 5,000 requests per second peak, 99.95%, and EU-only data residency - tell me if that is wrong." Proposing beats guessing silently.

**Minutes 5-15: the happy path, end to end.** Draw the request path (client → DNS/CDN → load balancer → service → cache → database) and the _delivery_ path (commit → CI → artifact registry → environments → progressive deploy). DevOps candidates who draw only the runtime architecture and never mention how code reaches it miss most of the marks. Keep it deliberately simple on the first pass; complexity is something you add when a requirement forces it.

**Minutes 15-40: depth where they push, plus the four things they always want.**

1. **Failure.** For each component: what happens when it dies, what is the blast radius, and how does the system recover. AZ loss, region loss, database failover, dependency timeout, retry storms and why you need jitter and circuit breakers, cache stampede on cold start.
2. **Observability.** The SLIs you would define, the handful of alerts that page a human (burn-rate based, symptom not cause), the dashboards, and how you would debug the specific slow request rather than the aggregate.
3. **Delivery and change safety.** Pipeline stages, artifact promotion, canary or blue/green with automated analysis, schema migration strategy (expand/contract), rollback path and how long it takes.
4. **Security and cost.** Identity between services, secret management, network boundaries, and the rough cost shape with the two or three biggest line items and how you would reduce them. Volunteering cost unprompted is a strong senior signal.

**Last 5 minutes: bound it honestly.** Name the bottleneck that appears first at 10x, the piece you are least confident in, and what you would prototype to de-risk it. "This design breaks at the database write path around 10x, and I would shard by tenant" is a better ending than a claim of unlimited scale.

**How to lose the round.** Naming tools instead of reasoning ("we would use Kafka" with no why). Designing for 100x from the start. Silence while thinking - narrate instead. Refusing to commit to a choice when pressed. Ignoring cost and operability entirely. Getting defensive when challenged: the pushback is usually a test of whether you can hold or update a position gracefully, and "you are right, that breaks - here is the fix" scores well.

## Example

```text
Whiteboard order that works. Layers, not a big-bang diagram.

1 REQUIREMENTS   5k rps peak · 99.95% (≈22 min/month) · p99 300ms
                 RPO 5 min · RTO 30 min · EU-only · AWS · 6 teams
                 out of scope: the mobile client, the data warehouse

2 REQUEST PATH   client → Route53 → CloudFront → ALB → ECS/EKS svc
                        → ElastiCache → RDS (Multi-AZ) + read replica
                        → SQS → workers

3 DELIVERY PATH  commit → CI (test, scan, SBOM, sign) → ECR
                        → dev → staging → canary 5% → 100%
                        migrations: expand/contract, separate release

4 FAILURE        AZ loss: 3 AZs, capacity for n-1 · DB: Multi-AZ failover ~60s
                 region loss: out of scope at 99.95% - say so, don't over-build
                 dependency: timeout 500ms, 2 retries w/ jitter, circuit breaker
                 cache: stampede → request coalescing + jittered TTL

5 OBSERVE        SLI availability + p99 latency · multi-window burn-rate alerts
                 traces w/ exemplars · one dashboard per service

6 COST + LIMITS  biggest lines: NAT/egress, RDS, logs retention
                 first bottleneck at 10x: DB writes → shard by tenant
                 least confident: cache invalidation on tenant config change
```

```text
Say the trade-off out loud, every time. This is what is being graded.

"Multi-AZ RDS over multi-region: 99.95% does not justify the cost and the
 write-latency hit of cross-region replication. If the target moved to 99.99%
 I would revisit, and the change would be an active-passive standby with
 async replication - accepting an RPO of seconds instead of zero."

"EKS over Lambda: the team already runs Kubernetes, and the workload is
 steady rather than spiky. Lambda would win on a bursty low-volume service."
```

## Interview tips

- Spend the first five minutes on requirements and write the numbers down. Candidates who start drawing immediately lose points they never recover.
- Always draw the delivery path as well as the request path. In a DevOps round, "how does code get there safely" is half the question.
- Attach the availability target to the topology decision explicitly. 99.95% single-region versus 99.99% multi-region is the trade-off they most want to hear reasoned.
- Narrate your thinking continuously. Silence is scored as absence of thought.
- Volunteer failure modes before being asked - AZ loss, database failover, retry storms, cache stampede - with a mitigation each.
- Bring up cost and its two or three biggest line items unprompted.
- End by naming the first bottleneck at 10x and the part you are least sure about. Confident humility outperforms false certainty every time.

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
