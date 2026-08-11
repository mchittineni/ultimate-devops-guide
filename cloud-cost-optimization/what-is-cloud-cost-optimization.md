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

**The discipline is FinOps:** inform (visibility and allocation), optimise (the levers above), operate (continuous governance). It is a cross-functional practice between engineering, finance, and product - not a quarterly cleanup.

## Interview tips

- Order the levers by effort-to-saving; waste elimination before commitments is the correct sequence.
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
