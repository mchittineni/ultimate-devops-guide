---
title: "Why did your autoscaling not kick in during a traffic spike?"
id: 420
category: "Scalability and High Availability"
difficulty: "Advanced"
tags:
  - devops
  - scalability-and-high-availability
  - interview-questions
  - kubernetes
  - aws-engineering
  - infrastructure-monitoring
---

# Why did your autoscaling not kick in during a traffic spike?

**Short answer:** Autoscaling fails in one of four places, and you diagnose it by asking where the chain broke: **the signal** (the metric was missing, lagging, or the wrong one - CPU does not move for an I/O-bound service), **the decision** (thresholds, cooldowns, stabilisation windows, or min/max bounds that pinned the desired count), **the provisioning** (quota, capacity, subnet IP exhaustion, a bad launch template or AMI, spot unavailability, image pull failures), or **the timing** (it did scale, but the total time to serve traffic - metric delay + decision + boot + warm-up + health check - was longer than the spike). The most common real answer is the last one: autoscaling is reactive, and a spike that arrives in 60 seconds cannot be met by a 4-minute provisioning path. The fixes are headroom, pre-scaling, and load shedding - not a lower threshold.

## Detail

### 1. The signal

- **Metrics missing entirely.** In Kubernetes, the Horizontal Pod Autoscaler shows `<unknown>` for the metric when metrics-server is not installed or unhealthy, or when the Pods have **no resource requests** - CPU utilisation is computed as a percentage _of the request_, so no request means no percentage and no scaling. This is the single most common HPA failure.
- **The wrong metric.** CPU is a poor proxy for an I/O-bound or connection-bound service; it stays at 20% while queue depth explodes. Scale on the thing that actually saturates - requests per second, in-flight requests, queue length (KEDA with SQS/Kafka/Redis), or p95 latency. Custom or external metrics are the mature answer.
- **Metric lag.** A 60-second scrape plus a 30-second aggregation window means the autoscaler is reacting to conditions that are already two minutes old.

### 2. The decision

- **Bounds.** `maxReplicas` or the ASG's `MaxSize` already reached - the autoscaler is working perfectly and is simply not allowed to help. Check this first; it is embarrassing and frequent.
- **Cooldowns and stabilisation.** The HPA's default 300-second scale-down stabilisation window is deliberate, but a short scale-up `stabilizationWindowSeconds` plus a `Pods`/`Percent` policy is what gives you a fast response. Classic ASG cooldowns suppress consecutive scaling activities; step scaling with multiple steps reacts far better to a large excursion than a single-threshold simple policy.
- **Target tracking maths.** Target-tracking aims to keep the average at the target, so with a target of 70% CPU and a spike to 100%, it computes a proportional increase - not "add everything now". If your service falls over above 80%, your target must be lower, and you must have headroom, not a tight fit.
- **Conflicting controllers.** Two HPAs on one Deployment, or an HPA plus a Deployment `replicas` value managed by GitOps, fight each other - the GitOps controller reverts the HPA's change every sync. Remove `replicas` from the manifest or mark it as ignored, or nothing will ever scale.
- **VPA and HPA on the same CPU metric** conflict by design; use VPA for requests and HPA for replica count on a different signal.

### 3. The provisioning

- **Quota and capacity.** vCPU service quota, instance-type unavailability in the availability zone, spot capacity withdrawn, or an on-demand capacity shortfall. The ASG's **activity history** states the reason verbatim, and this is the first place to look for "it tried and failed".
- **Networking.** Subnet IP exhaustion is a favourite: the ASG launches, the instance cannot get an address, and scaling silently stops. In EKS, the same problem appears as Pods stuck `Pending` because the ENI/IP budget per node is exhausted.
- **A broken launch path.** Invalid or deleted AMI, a launch template referencing a missing security group, a user-data script that fails, an IAM instance profile without permissions, or a registry rate limit stopping image pulls. New instances appear and never become healthy - which looks like "scaling did nothing".
- **Cluster autoscaler specifics.** It only acts on **unschedulable Pods**, so it is reactive by definition. It will not act if the Pods are pending for a reason more capacity cannot fix (a zonal PVC, a node selector matching nothing, taints without tolerations), and it needs correctly tagged/labelled node groups to know what a new node would look like. Karpenter is faster because it provisions directly for the pending Pods, but it still needs quota and compatible instance types.

### 4. The timing - usually the real answer

Add up the real end-to-end latency: metric scrape (up to 60 s) + autoscaler evaluation (15-60 s) + instance launch (30-90 s) + boot and bootstrap (30-120 s) + image pull (10-120 s) + application warm-up and JIT (10-120 s) + health check passes (10-60 s). Three to six minutes is normal. A flash sale, a marketing email, or a cache stampede does not wait three minutes. So the answer to "it did not scale in time" is architectural:

- **Run with headroom.** Target utilisation low enough (say 50-60%) that the existing fleet absorbs the first minutes.
- **Pre-scale for known events.** Scheduled scaling before a sale, a match, or a batch window is not a failure of automation; it is the correct use of information you already have.
- **Make new capacity fast.** Small images, pre-pulled or cached layers, prebuilt AMIs (Packer) instead of long user-data scripts, warm pools, and Kubernetes overprovisioning with a low-priority balloon Deployment that gets preempted to create instant space.
- **Degrade instead of failing.** Queue, shed load by priority, serve cached or reduced responses, and put a CDN in front of anything cacheable. This is what actually protects the service in the first 60 seconds. See [how do you design a system to degrade gracefully under overload](./how-do-you-design-a-system-to-degrade-gracefully-under-overload.md).
- **Check the bottleneck is even scalable.** Scaling the stateless tier into a database at connection limit makes the incident worse - more Pods, more connections, more timeouts. See [how do you troubleshoot a database that is slow or timing out under load](../database-management-in-devops/how-do-you-troubleshoot-a-database-that-is-slow-or-timing-out-under-load.md).

## Example

```bash
# Kubernetes: what does the HPA think, and why?
kubectl get hpa checkout -n prod
# NAME      TARGETS          MINPODS MAXPODS REPLICAS
# checkout  <unknown>/70%    3       30      3        <- no metric: requests missing?
kubectl describe hpa checkout -n prod | tail -15
#   FailedGetResourceMetric  missing request for cpu   <- the actual cause
#   ScalingLimited  True  TooManyReplicas ... at maxReplicas   <- or this one

kubectl top pods -n prod -l app=checkout      # is metrics-server even working?
kubectl get pods -n prod --field-selector=status.phase=Pending -o wide
kubectl -n kube-system logs -l app=cluster-autoscaler --tail=50 | grep -i 'scale_up\|no candidates'

# AWS: the ASG tells you in plain text why a launch failed
aws autoscaling describe-scaling-activities --auto-scaling-group-name prod-api \
  --max-items 5 --query 'Activities[].[StartTime,StatusCode,StatusMessage]' --output table
# Failed | "Could not launch On-Demand Instances. InsufficientInstanceCapacity ..."
# Failed | "There are not enough free addresses in subnet subnet-0ab1"

aws service-quotas get-service-quota --service-code ec2 \
  --quota-code L-1216C47A            # running on-demand standard vCPUs
```

```yaml
# An HPA that reacts fast on the way up and cautiously on the way down
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: { name: checkout, namespace: prod }
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: checkout }
  minReplicas: 6 # headroom: not 1. The first minute is served by what exists.
  maxReplicas: 60 # high enough that the cap is not the incident
  metrics:
    - type: Resource # requires resources.requests.cpu to be set - or no metric at all
      resource: { name: cpu, target: { type: Utilization, averageUtilization: 55 } }
    - type: Pods # the signal that actually saturates this service
      pods:
        metric: { name: http_inflight_requests }
        target: { type: AverageValue, averageValue: "30" }
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0 # react immediately
      policies:
        - { type: Percent, value: 100, periodSeconds: 30 } # double every 30s if needed
        - { type: Pods, value: 10, periodSeconds: 30 }
      selectPolicy: Max
    scaleDown:
      stabilizationWindowSeconds: 300 # slow down: avoid flapping
      policies: [{ type: Percent, value: 10, periodSeconds: 60 }]
```

## Interview tips

- Structure the answer as a chain - signal, decision, provisioning, timing - and say you would find which link broke rather than listing tuning knobs.
- The HPA showing `<unknown>` because Pods have no CPU **requests** is the highest-value specific: utilisation is a percentage of the request, so no request means no scaling.
- Check `maxReplicas`/`MaxSize` first and say so. It is the most common cause and admitting it is the fastest route to credibility.
- Name the provisioning failures with their real messages - `InsufficientInstanceCapacity`, "not enough free addresses in subnet" - and say the ASG activity history states the reason verbatim.
- The end-to-end timing arithmetic is what separates a senior answer: three to six minutes from metric to serving traffic, so a 60-second spike is an architecture problem, not a threshold problem.
- Therefore give headroom, scheduled pre-scaling, fast-boot images, overprovisioning balloons, and load shedding as the real answers - and say that lowering the threshold alone just makes you scale earlier on noise.
- Mention the GitOps conflict (a `replicas` field in Git fighting the HPA every sync). It is a real and very common bug.
- Close with the bottleneck check: scaling the stateless tier into a saturated database makes the outage worse. See [what is auto scaling](./what-is-auto-scaling.md) and [how do you autoscale workloads and nodes in Kubernetes](../kubernetes/how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scalability and High Availability](./README.md) · [All topics](../README.md)
