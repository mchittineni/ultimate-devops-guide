---
title: "What is Auto Scaling?"
id: 59
category: "Scalability and High Availability"
difficulty: "Beginner"
tags:
  - devops
  - scalability-and-high-availability
  - interview-questions
---

# What is Auto Scaling?

**Short answer:** Auto scaling automatically adds or removes capacity in response to demand signals, keeping performance acceptable during peaks and cost low during troughs, without human intervention.

## Detail

**Types**

- **Reactive / dynamic** - scale on observed metrics (CPU, request rate, queue depth). Simple, but always lagging by the time it takes to detect and start capacity.
- **Scheduled** - scale ahead of known patterns (business hours, a Monday batch run, a marketing campaign).
- **Predictive** - machine-learning forecasts from historical patterns, provisioning before the load arrives.
- **Target tracking** - declare a target ("keep average CPU at 60%") and let the controller work out the maths. Usually the best default.

**Choosing the metric.** CPU is the default but often wrong. For a queue worker, scale on queue depth or age of the oldest message. For a web API, requests per instance or p95 latency reflect user experience far better. Kubernetes supports custom and external metrics through KEDA or the Prometheus adapter for exactly this reason.

**Getting it right in practice**

- **Warm-up / stabilisation windows** - do not count a booting instance's metrics; do not scale down within minutes of scaling up (flapping).
- **Asymmetric policies** - scale out quickly and aggressively, scale in slowly and cautiously.
- **Fast startup** - pre-baked images and lean containers; if an instance takes five minutes to be ready, autoscaling cannot save a two-minute spike.
- **Graceful shutdown** - connection draining and `SIGTERM` handling so scale-in does not drop requests.
- **Sensible bounds** - a maximum that protects the budget and downstream databases from connection storms.

At the cluster level, the pod autoscaler needs the **Cluster Autoscaler** or Karpenter beneath it to add nodes when pods cannot be scheduled.

## Interview tips

- "What metric do you scale on?" is the real question - answering "CPU" without qualification is a weak signal.
- Mention flapping and stabilisation windows; they are the practical failure mode.
- Note the downstream effect: scaling the app tier can overwhelm the database connection pool.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scalability and High Availability](./README.md) · [All topics](../README.md)
