---
title: "What is Cloud Cost Optimization?"
id: 91
category: "Cloud Cost Optimization"
difficulty: "Beginner"
tags:
  - devops
  - cloud-cost-optimization
  - interview-questions
---

# What is Cloud Cost Optimization?

**Short answer:** Cloud cost optimisation is the continuous practice of reducing cloud spend without harming performance or reliability - through right-sizing, commitment discounts, eliminating waste, architectural change, and making cost visible to the teams that create it.

## Detail

**The levers, roughly in order of return**

1. **Eliminate waste.** Unattached volumes, idle load balancers, orphaned snapshots, forgotten dev environments, over-provisioned non-production. Typically the fastest wins with zero risk.
2. **Right-size.** Match instance types and container requests to actual observed utilisation. Most workloads are provisioned for a peak that never arrives.
3. **Schedule.** Shut down non-production outside working hours - that is roughly a 65% saving on those environments alone.
4. **Commitment discounts.** Reserved instances and savings plans for predictable baseline load; 30–70% off on-demand.
5. **Spot / preemptible capacity** for fault-tolerant work: batch jobs, CI runners, stateless workers. Up to 90% off.
6. **Storage lifecycle.** Move cold objects to infrequent-access and archive tiers; delete old snapshots and logs on a policy.
7. **Architecture.** Serverless for spiky workloads, caching to cut database load, ARM/Graviton instances for better price-performance, and reducing data transfer - especially cross-AZ and egress, which quietly become enormous.
8. **Visibility and accountability.** Tag everything, show each team its own spend, and set budgets with alerts.

**Scheduling non-production databases, concretely.** Running 12 hours on weekdays is 60 of 168 hours, so stopping a dev database outside working hours saves roughly 60-65% of its instance cost. On AWS:

- Use **EventBridge Scheduler** with a cron expression and a time zone. It can call `rds:StopDBInstance` / `StartDBInstance` (or `StopDBCluster` / `StartDBCluster` for Aurora) directly as a universal target, or invoke a small Lambda that selects databases by tag (for example `Schedule=office-hours`) so new databases are covered automatically. **Instance Scheduler on AWS** is a ready-made, tag-driven alternative for EC2 and RDS.
- A stopped RDS instance or Aurora cluster **restarts automatically after 7 days**, so the schedule must keep stopping it - a weekly "stop on Friday" rule alone silently stops saving money.
- **Storage and backups are still billed** while stopped; only instance hours stop. Instances that have read replicas, and read replicas themselves, cannot be stopped.
- Give developers an opt-out tag and a self-service "start now" for out-of-hours work, or the schedule gets disabled.

**The discipline is FinOps:** inform (visibility and allocation), optimise (the levers above), operate (continuous governance). It is a cross-functional practice between engineering, finance, and product - not a quarterly cleanup.

**The trade-off to keep in view.** Every lever touches something else: right-sizing reduces headroom, Spot adds interruptions, commitments reduce flexibility, and removing redundancy lowers availability. Tie each saving to the service's SLO so the reliability cost is explicit.

## Example

```bash
# Two of the fastest wins, found in minutes.
aws ec2 describe-volumes --filters Name=status,Values=available \
  --query 'Volumes[].{id:VolumeId,gb:Size,type:VolumeType}' --output table   # unattached disks

aws compute-optimizer get-ec2-instance-recommendations \
  --filters name=Finding,values=Overprovisioned \
  --query 'instanceRecommendations[].[instanceArn,currentInstanceType,recommendationOptions[0].instanceType]' \
  --output table                                                             # right-sizing candidates
```

```bash
# Stop a dev database every weekday evening, local time, with no Lambda at all.
# (A matching start schedule calls rds:startDBInstance in the morning.)
aws scheduler create-schedule --name stop-dev-orders-db \
  --schedule-expression "cron(0 20 ? * MON-FRI *)" \
  --schedule-expression-timezone "Asia/Kolkata" \
  --flexible-time-window Mode=OFF \
  --target '{
    "Arn": "arn:aws:scheduler:::aws-sdk:rds:stopDBInstance",
    "RoleArn": "arn:aws:iam::111122223333:role/scheduler-rds-stop-start",
    "Input": "{\"DbInstanceIdentifier\": \"dev-orders\"}"
  }'
```

## Interview tips

- Order the levers by effort-to-saving; waste elimination before commitments is the correct sequence.
- For "stop non-prod databases outside office hours", name the mechanism (EventBridge Scheduler or Instance Scheduler, selected by tag) and the two caveats: RDS restarts a stopped instance after 7 days, and storage and backups keep billing.
- Data transfer costs are the ones teams miss - naming cross-AZ traffic signals real experience.
- Emphasise that cost is an engineering quality attribute, owned by teams and made visible, not a finance problem.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Cost Optimization](./README.md) · [All topics](../README.md)
