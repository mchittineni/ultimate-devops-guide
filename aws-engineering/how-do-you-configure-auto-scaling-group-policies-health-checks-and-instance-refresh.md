---
title: "How do you configure Auto Scaling group policies, health checks, and instance refresh?"
id: 482
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - aws-engineering
  - interview-questions
  - scalability-and-high-availability
  - cloud-cost-optimization
---

# How do you configure Auto Scaling group policies, health checks, and instance refresh?

**Short answer:** An Auto Scaling group has three scaling mechanisms and you should reach for them in this order: **target tracking** (pick a metric and a target value - "keep average CPU at 50%" or "keep requests-per-target at 1000" - and AWS manages the rest), **step scaling** (explicit CloudWatch alarms with graduated adjustments, for when target tracking's model does not fit), and **scheduled scaling** (a cron-like capacity change for known patterns such as heavy traffic every evening between 17:00 and 20:00). Health checks decide what gets replaced: **EC2** status checks catch a dead instance, but you want **ELB** health checks (and, better, ASG **health check types including `ELB`** plus a **health check grace period** long enough for the application to start) so an instance that boots but never serves is also replaced. And **instance refresh** is how you roll out a new AMI or launch template version - it replaces instances in batches respecting a minimum healthy percentage, with checkpoints and automatic rollback. The failure everyone hits at least once is a **grace period that is shorter than boot time**, which makes the ASG kill each new instance before it can pass a health check - a replacement loop that looks like a capacity problem.

## Detail

### The three scaling policies

| Policy              | How you configure it                                                                                              | When to use it                                                                                         |
| ------------------- | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| **Target tracking** | A metric + a target value (`ASGAverageCPUUtilization` 50%, `ALBRequestCountPerTarget` 1000, or any custom metric) | Default choice. AWS creates and manages the alarms and scales both directions                          |
| **Step scaling**    | Your own CloudWatch alarms with tiered adjustments (+1 at 60%, +3 at 80%)                                         | When the response should be non-linear, or you need different behaviour at different breach magnitudes |
| **Simple scaling**  | One alarm, one adjustment, with a cooldown                                                                        | Legacy. Blocked during cooldown, so it reacts slowly. Avoid                                            |
| **Scheduled**       | `recurrence` cron + min/max/desired                                                                               | Known patterns: business hours, a nightly batch, "traffic is heavy 17:00-20:00 daily"                  |
| **Predictive**      | ML forecast from history, provisioning **ahead** of demand                                                        | Regular daily/weekly cycles where warm-up time is the constraint                                       |

The **target tracking value** interviewers ask about ("what is the target?") is the number you want the metric to hover around - not a threshold to breach. Target tracking then adds and removes capacity to hold the metric near it, and it deliberately scales **out fast and in slowly** to avoid flapping.

For the daily-evening-peak question, the good answer combines two: **scheduled** scaling to raise the minimum before 17:00 (so capacity exists before demand arrives), plus **target tracking** to handle the actual variability. Scheduled alone is brittle; target tracking alone is always a few minutes late.

Also know **which metric**: CPU is the default but often wrong. For a web tier, `ALBRequestCountPerTarget` or p95 latency tracks user experience much better; for a queue worker, backlog per instance (`ApproximateNumberOfMessagesVisible / instance count` as a custom metric) is the correct signal, because CPU on a worker waiting on I/O tells you nothing. Memory is **not** a default EC2 metric at all - it requires the CloudWatch agent, which is the answer to "how do you create auto-scaling policies based on memory and disk usage?": publish those as custom metrics from the agent, then target-track or step-scale on them.

### Health checks, and the grace period trap

An ASG replaces instances it considers unhealthy. Which signals it uses is configurable:

- **EC2 status checks** (default): the hypervisor and the instance's own system checks. Catches a dead or unreachable instance, not a broken application.
- **ELB health checks**: add `ELB` to the ASG's health check types and the target group's health check becomes the arbiter, so an instance whose application is failing gets replaced. Almost always what you want.
- **Custom health checks** via `set-instance-health` from your own monitoring, for signals nothing else can see.

The **health check grace period** is the number of seconds after launch during which the ASG ignores health checks. If your application takes 3 minutes to become ready and the grace period is 300 seconds, you are fine; if it is 60, the ASG marks every new instance unhealthy, terminates it, launches another, and repeats - the exact scenario in "the ASG launched two instances but provisioning takes two to three minutes and they get terminated before they are ready". The fix is a grace period comfortably longer than realistic boot-plus-warm-up time, and the better fix is **reducing boot time** with a baked AMI so you are not fighting the clock. Add lifecycle hooks if you need to complete work (register with a service, warm a cache) before the instance is put into service.

Two related settings: **`default_instance_warmup`** tells scaling policies how long a new instance takes to contribute, so its metrics are not counted while it is still starting (this replaced per-policy warm-up and cooldown for most cases), and a **warm pool** keeps pre-initialised, stopped instances ready so scale-out is seconds rather than minutes.

### Rolling out a new AMI: instance refresh

The question _"the development team changed the AMI in the launch template - how do you make sure the new version is actually deployed?"_ has a specific answer, because **an ASG does not replace running instances when the launch template changes**. Existing instances keep running the old AMI; only new launches get the new version. To roll it out:

1. **Instance refresh** (`start-instance-refresh`): replaces instances in batches with `MinHealthyPercentage`, `InstanceWarmup`, optional **checkpoints** (pause at 20%, 50%, 100% so you can validate), `SkipMatching` so instances already on the desired version are left alone, and **auto-rollback** on failure. This is the modern, built-in answer.
2. **Terraform/CloudFormation-driven replacement**: `create_before_destroy` on the launch template plus an ASG `instance_refresh` block, or a CloudFormation `UpdatePolicy` with `AutoScalingRollingUpdate`.
3. **Blue/green at the ASG level**: stand up a second ASG on the new version behind the same target group (or a second target group and shift listener weights), verify, then drain the old one. Slower, but the safest for high-risk changes.

Make sure the launch template's version is pinned deliberately - an ASG pointing at `$Latest` picks up changes on the next launch without any review, while `$Default` or a specific version number makes rollout an explicit act.

### Connection draining and graceful shutdown

Scale-in and refresh both terminate instances, and users notice unless you drain. **Target group deregistration delay** (connection draining, default 300s) keeps existing connections alive while stopping new ones - the answer to "what is connection draining and what problem does it solve?" Pair it with a **lifecycle hook** on `EC2_INSTANCE_TERMINATING` so your own shutdown work happens, and set the application's shutdown to stop accepting new work first. Also configure **termination policies** (default, oldest instance, closest to next instance hour, or a custom order) and **instance scale-in protection** for stateful members you do not want chosen.

### Mixed instance types and Spot

A mixed-instances policy with several instance types across several AZs, a base of On-Demand plus a Spot percentage, and `capacity-optimized` allocation is the standard cost play - typically 60-70% cheaper for the Spot portion. It requires the workload to tolerate a 2-minute interruption notice, so pair it with a lifecycle hook or the Spot interruption handler to drain gracefully. Say this when asked for real cost optimisations; it is more credible than "we right-sized instances".

### Self-healing without a load balancer

"I need EC2 instances to configure themselves automatically, or replace themselves when they fail" is an ASG question even for a single instance: an ASG with `min=max=desired=1` plus ELB or custom health checks will replace a failed instance automatically, and `user_data`/a baked AMI makes the replacement come up configured. That combination - ASG for self-healing, immutable AMI plus cloud-init for configuration - is the answer, not a cron job that restarts services.

## Example

```hcl
# Launch template with a baked AMI, IMDSv2, and a version you change deliberately
resource "aws_launch_template" "app" {
  name_prefix   = "app-"
  image_id      = data.aws_ami.app_baked.id   # Packer-built: fast boot, no fighting the grace period
  instance_type = "m6i.large"
  iam_instance_profile { name = aws_iam_instance_profile.app.name }
  metadata_options { http_tokens = "required" }
  user_data = base64encode(templatefile("cloud-init.yaml", { env = var.environment }))
  lifecycle { create_before_destroy = true }
}

resource "aws_autoscaling_group" "app" {
  name                = "app"
  min_size            = 3
  max_size            = 30
  desired_capacity    = 6
  vpc_zone_identifier = [for s in aws_subnet.private : s.id]  # spread across AZs

  health_check_type         = "ELB"   # not just EC2: replace instances that boot but never serve
  health_check_grace_period = 300     # LONGER than realistic boot + warm-up
  default_instance_warmup    = 180    # new instances excluded from metrics while starting
  target_group_arns          = [aws_lb_target_group.app.arn]

  mixed_instances_policy {
    instances_distribution {
      on_demand_base_capacity                  = 3
      on_demand_percentage_above_base_capacity = 20   # 80% Spot above the base
      spot_allocation_strategy                 = "capacity-optimized"
    }
    launch_template {
      launch_template_specification { launch_template_id = aws_launch_template.app.id }
      override { instance_type = "m6i.large" }
      override { instance_type = "m5.large" }
      override { instance_type = "m6a.large" }   # diversity = fewer Spot interruptions
    }
  }

  instance_refresh {                  # AMI changes actually roll out
    strategy = "Rolling"
    preferences {
      min_healthy_percentage = 90
      instance_warmup        = 180
      skip_matching          = true   # leave instances already on this version alone
      checkpoint_percentages = [20, 50, 100]
      checkpoint_delay       = 600    # pause to validate between batches
      auto_rollback          = true
    }
    triggers = ["launch_template"]
  }
}
```

```hcl
# Target tracking on a metric that reflects users, not the machine
resource "aws_autoscaling_policy" "requests" {
  name                   = "track-requests-per-target"
  autoscaling_group_name = aws_autoscaling_group.app.name
  policy_type            = "TargetTrackingScaling"
  target_tracking_configuration {
    target_value = 1000            # the value to hold, not a threshold to breach
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.public.arn_suffix}/${aws_lb_target_group.app.arn_suffix}"
    }
  }
}

# Scheduled: capacity exists BEFORE the 17:00-20:00 peak, target tracking handles the rest
resource "aws_autoscaling_schedule" "evening_up" {
  scheduled_action_name  = "evening-peak-up"
  autoscaling_group_name = aws_autoscaling_group.app.name
  recurrence             = "45 16 * * *"   # 16:45 UTC, ahead of demand
  min_size               = 12
  desired_capacity       = 12
  max_size               = 30
}
resource "aws_autoscaling_schedule" "evening_down" {
  scheduled_action_name  = "evening-peak-down"
  autoscaling_group_name = aws_autoscaling_group.app.name
  recurrence             = "30 20 * * *"
  min_size               = 3
  desired_capacity       = 6
  max_size               = 30
}

# Graceful removal: drain connections before the instance goes
resource "aws_lb_target_group" "app" {
  name                 = "app"
  port                 = 8080
  protocol             = "HTTP"
  vpc_id               = aws_vpc.this.id
  deregistration_delay = 60          # connection draining
  health_check {
    path                = "/healthz"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 15
    timeout             = 5
    matcher             = "200"
  }
}
```

```bash
# Roll out a new AMI and watch it
aws autoscaling start-instance-refresh --auto-scaling-group-name app \
  --preferences '{"MinHealthyPercentage":90,"InstanceWarmup":180,"SkipMatching":true,
                  "AutoRollback":true,"CheckpointPercentages":[20,50,100],"CheckpointDelay":600}'
aws autoscaling describe-instance-refreshes --auto-scaling-group-name app \
  --query 'InstanceRefreshes[0].[Status,PercentageComplete,StatusReason]' --output table
aws autoscaling cancel-instance-refresh --auto-scaling-group-name app   # if it goes wrong

# Diagnose the replacement loop: why did it terminate my new instances?
aws autoscaling describe-scaling-activities --auto-scaling-group-name app --max-items 10 \
  --query 'Activities[].[StartTime,StatusCode,Cause]' --output table
# "failed ELB health checks" within the grace period -> the grace period is too short
aws elbv2 describe-target-health --target-group-arn "$TG" \
  --query 'TargetHealthDescriptions[].[Target.Id,TargetHealth.State,TargetHealth.Reason]' --output table

# Memory/disk based scaling needs the CloudWatch agent publishing custom metrics
aws cloudwatch list-metrics --namespace CWAgent --metric-name mem_used_percent
```

## Interview tips

- Give the three policy types with a one-line rule each, and recommend **target tracking** as the default because AWS manages the alarms and scales asymmetrically (out fast, in slow).
- Define the target tracking "target" correctly - the value to hold, not a threshold - since that is the literal question people are asked.
- For the daily 17:00-20:00 peak, answer with **scheduled plus target tracking**: raise the minimum ahead of demand, let target tracking absorb variability. Combining them is the answer that sounds like production experience.
- Challenge CPU as the scaling metric. Requests-per-target or latency for a web tier, queue backlog per instance for workers, and note that **memory is not a default EC2 metric** - it needs the CloudWatch agent as a custom metric.
- Nail the health-check answer: add `ELB` to the health check types so an instance that boots but never serves is replaced, and set the **grace period longer than real boot time**. Then give the replacement-loop scenario and its two fixes - longer grace period, and a baked AMI to shorten boot.
- Say explicitly that changing the launch template does **not** replace running instances, then name **instance refresh** with `MinHealthyPercentage`, checkpoints, `SkipMatching`, and auto-rollback. Offer a second ASG behind the same target group as the blue/green alternative.
- Bring up connection draining (target group deregistration delay) and lifecycle hooks for graceful shutdown, plus termination policies and scale-in protection.
- Mention mixed instances with Spot and `capacity-optimized` allocation as a real cost lever, with the interruption-handling caveat. And for "instances should replace themselves when they fail", answer ASG with min=max=1 plus health checks and an immutable AMI. See [how do Auto Scaling groups and load balancers work together on AWS](./how-do-auto-scaling-groups-and-load-balancers-work-together-on-aws.md), [why did your autoscaling not kick in during a traffic spike](../scalability-and-high-availability/why-did-your-autoscaling-not-kick-in-during-a-traffic-spike.md), [what is immutable infrastructure](../infrastructure-as-code/what-is-immutable-infrastructure-and-how-do-you-adopt-it.md), and [troubleshooting a load balancer returning 5xx errors](../scalability-and-high-availability/how-do-you-troubleshoot-a-load-balancer-returning-5xx-errors-or-sending-traffic-unevenly.md).

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
