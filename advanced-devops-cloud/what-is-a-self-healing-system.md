---
title: "What is a Self-Healing System?"
id: 158
category: "Advanced DevOps & Cloud"
difficulty: "Advanced"
tags:
  - devops
  - advanced-devops-cloud
  - interview-questions
---

# What is a Self-Healing System?

**Short answer:** A self-healing system automatically detects failures and recovers from them without human intervention - restarting failed processes, replacing unhealthy instances, failing over, and reverting bad changes.

## Detail

**Mechanisms by layer**

- **Process** - a supervisor (systemd, the kubelet) restarts a crashed process, with backoff to avoid a crash loop consuming resources.
- **Instance / node** - health checks remove an unhealthy instance from the load balancer, and an autoscaling group or node autoprovisioner replaces it.
- **Workload** - Kubernetes controllers continuously reconcile: a deleted pod is recreated, a failing readiness probe removes the pod from Service endpoints, and a node failure triggers rescheduling elsewhere.
- **Data** - managed database failover promotes a replica automatically within tens of seconds.
- **Traffic** - health-check-based DNS or global load balancer failover routes users away from an unhealthy region.
- **Deployment** - progressive delivery with automated analysis aborts and rolls back a release whose error rate or latency breaches thresholds.
- **Configuration** - GitOps reconciliation reverts manual drift automatically.

**Design requirements.** Self-healing depends on the application being restartable without side effects: stateless or externalised state, idempotent operations, graceful shutdown on `SIGTERM`, and meaningful health checks. A shallow health check that returns 200 regardless of the application's real state makes the whole mechanism useless.

**The important caveats**

- **Do not mask root causes.** A pod restarting fifty times a day is "healed" and also badly broken. Alert on restart _rates_, not just on final failure.
- **Recovery loops can amplify failure.** Aggressive restarts under load, or an autoscaler reacting to a downstream outage, can make things worse. Use backoff, rate limits, and circuit breakers.
- **Retain observability.** Automatic recovery destroys evidence; capture logs, metrics, and ideally a core dump before replacing the instance.

## Interview tips

- "Self-healing must not hide chronic failure" is the mature caveat - alert on restart rates.
- Kubernetes reconciliation is the canonical example; explain the control loop rather than naming the feature.
- Graceful shutdown and idempotency as prerequisites shows you understand what makes it safe.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
