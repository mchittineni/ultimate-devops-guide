---
title: "How do Auto Scaling groups and load balancers work together on AWS?"
id: 194
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - aws-engineering
  - interview-questions
---

# How do Auto Scaling groups and load balancers work together on AWS?

**Short answer:** The Auto Scaling group owns instance lifecycle and registers instances into a target group; the load balancer health-checks the targets and only routes to healthy ones. Attaching the ASG to the target group with `health_check_type = "ELB"` is what makes the ASG replace an instance that is running but not serving.

## Detail

**Two health checks, and the one that matters.** By default an ASG uses EC2 status checks, which pass as long as the instance is booted - an application that has crashed stays in service. Setting the ASG's health check type to ELB means it inherits the load balancer's application-level check (`/healthz`) and terminates and replaces instances that fail it. This single setting is the most common gap in real deployments.

**Load balancer choice.** ALB for HTTP/HTTPS with path and host routing, WAF integration, and OIDC authentication. NLB for TCP/UDP, extreme throughput, static IPs, and preserving client IPs. GWLB for inline security appliances. CLB is legacy. Note that ALB scales its own capacity gradually - for an instant, very large traffic spike, either pre-warm via support or use NLB.

**Connection draining and graceful shutdown.** Deregistration delay (default 300s) keeps the target receiving in-flight responses while new requests stop. The application must also handle `SIGTERM` by finishing work and closing listeners; a container that exits immediately on `SIGTERM` produces 502s during every scale-in and deploy. Add a lifecycle hook if you need to flush state before termination.

**Scaling policy choice.** Target tracking (keep average CPU at 60%, or requests-per-target at 1,000) is the default recommendation because it self-tunes. Step scaling suits known non-linear responses; scheduled scaling handles predictable business cycles; predictive scaling helps when warm-up time exceeds the traffic ramp. Base the metric on a real bottleneck - CPU is often wrong for I/O-bound services, where `ALBRequestCountPerTarget` or queue depth is the honest signal.

**Warm-up and cooldown prevent thrash.** Instance warm-up tells the ASG to ignore a new instance's metrics until it is genuinely serving; without it, the group scales again while the first instance is still booting. Combine with a health-check grace period long enough for application start-up, or the ASG will kill instances mid-boot in a loop.

**Spot capacity.** A mixed-instances policy with several instance types across AZs, on-demand for a baseline and Spot for the remainder, plus handling of the two-minute interruption notice, is the standard cost pattern for stateless tiers.

## Example

```hcl
resource "aws_autoscaling_group" "api" {
  name                      = "api"
  vpc_zone_identifier       = module.vpc.private_subnets
  min_size                  = 3
  max_size                  = 30
  desired_capacity          = 3
  target_group_arns         = [aws_lb_target_group.api.arn]
  health_check_type         = "ELB" # not "EC2" - the point of the whole design
  health_check_grace_period = 120
  default_instance_warmup   = 90

  mixed_instances_policy {
    instances_distribution {
      on_demand_base_capacity                  = 3
      on_demand_percentage_above_base_capacity = 0 # everything above baseline on Spot
      spot_allocation_strategy                 = "price-capacity-optimized"
    }
    launch_template {
      launch_template_specification { launch_template_id = aws_launch_template.api.id }
      override { instance_type = "m6i.large" }
      override { instance_type = "m6a.large" }
      override { instance_type = "m5.large" }
    }
  }
}

resource "aws_autoscaling_policy" "api_rps" {
  name                   = "api-rps"
  autoscaling_group_name = aws_autoscaling_group.api.name
  policy_type            = "TargetTrackingScaling"
  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.api.arn_suffix}/${aws_lb_target_group.api.arn_suffix}"
    }
    target_value = 1000
  }
}
```

## Interview tips

- Say `health_check_type = "ELB"` explicitly and explain what breaks without it - that is the question behind the question.
- Deregistration delay plus `SIGTERM` handling is the answer to "why do we see 502s during deploys?".
- Expect: "which metric would you scale on?" - reject CPU as a reflex and name the actual bottleneck.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?]] (`#407`): [How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-waiting-for-a-persistentvolumeclaim.md)
- [[What is AWS (Amazon Web Services)?]] (`#22`): [What is AWS (Amazon Web Services)?](../cloud-platforms/what-is-aws-amazon-web-services.md)
- [[What is Google Cloud Platform (GCP)?]] (`#24`): [What is Google Cloud Platform (GCP)?](../cloud-platforms/what-is-google-cloud-platform-gcp.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
