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

**Limitations.** Autoscaling is reactive (or, with predictive scaling, only as good as the forecast), so it cannot absorb a spike shorter than the time to provision and warm up capacity - that needs headroom or load shedding. It also only helps when the bottleneck is the tier being scaled; adding app instances in front of a saturated database makes things worse.

## Example

```hcl
# AWS: target tracking on an Auto Scaling group - keep average CPU near 60%.
resource "aws_autoscaling_policy" "cpu_target" {
  name                   = "cpu-60"
  autoscaling_group_name = aws_autoscaling_group.api.name
  policy_type            = "TargetTrackingScaling"
  estimated_instance_warmup = 120 # ignore metrics from instances still booting

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 60
  }
}

# Scheduled scaling for a known peak: capacity is there before the load arrives.
resource "aws_autoscaling_schedule" "weekday_morning" {
  scheduled_action_name  = "weekday-morning"
  autoscaling_group_name = aws_autoscaling_group.api.name
  recurrence             = "0 7 * * MON-FRI"
  time_zone              = "Europe/London"
  min_size               = 6
  max_size               = 40
  desired_capacity       = 10
}
```

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
