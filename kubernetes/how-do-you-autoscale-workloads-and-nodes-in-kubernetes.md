---
title: "How do you autoscale workloads and nodes in Kubernetes?"
id: 258
category: "Kubernetes"
difficulty: "Advanced"
tags:
  - devops
  - kubernetes
  - interview-questions
---

# How do you autoscale workloads and nodes in Kubernetes?

**Short answer:** Three layers that must be designed together - the **Horizontal Pod Autoscaler** adds replicas, the **Vertical Pod Autoscaler** right-sizes each replica's requests, and the **Cluster Autoscaler or Karpenter** adds nodes when Pods cannot be placed. KEDA extends the HPA to scale on external signals such as queue depth. Scaling Pods without a way to add nodes just produces `Pending` Pods.

## Detail

**HPA - horizontal, the default.** A controller loop compares an observed metric against a target and computes `desiredReplicas = ceil(currentReplicas × currentMetric / targetMetric)`. CPU and memory come from the metrics-server; custom and external metrics need an adapter (commonly Prometheus Adapter). `autoscaling/v2` allows several metrics at once - the largest resulting replica count wins.

**The trap in CPU-target HPAs:** utilisation is a percentage _of the Pod's CPU request_, not of the node. If requests are set far above real usage, utilisation never reaches the target and the HPA never scales. HPA correctness depends on sane requests, which is why HPA and VPA are a pair.

**VPA - vertical, the right-sizing tool.** It observes real consumption and recommends or applies `requests`/`limits`. Historically applying a change meant evicting and recreating the Pod; in-place Pod resizing has since reduced that disruption. **Never run VPA and HPA on the same CPU or memory metric** - they fight, one changing the denominator the other divides by. The supported combination is VPA on memory with HPA on a custom metric, or VPA in recommendation-only mode feeding your requests back into Git.

**KEDA - event-driven, and usually the right answer for workers.** CPU is a poor proxy for backlog. KEDA provides 70+ scalers (SQS, Kafka lag, RabbitMQ, Azure Service Bus, Prometheus queries, cron) and generates an HPA underneath, so you keep standard HPA semantics. It also scales to **zero**, which plain HPA cannot do (its floor is 1).

**Node-level: Cluster Autoscaler vs Karpenter.** Cluster Autoscaler scales pre-defined node groups up and down and requires each group to be reasonably homogeneous. Karpenter skips node groups: it reads the `Pending` Pods' actual requirements and provisions a right-sized instance directly, typically in well under a minute, and consolidates underutilised nodes by rescheduling their Pods onto fewer, cheaper machines. On AWS, Karpenter is the current default choice; GKE Autopilot and Azure's node autoprovisioning solve the same problem managed.

**Making it behave under real traffic:**

- **Set `behavior` policies.** Scale up fast, scale down slowly. The default `stabilizationWindowSeconds` of 300 on scale-down exists to stop flapping - do not remove it, and do add a scale-up policy so a traffic spike is not throttled.
- **Pair with a PodDisruptionBudget.** Consolidation, node upgrades, and scale-down all respect PDBs; without one, the autoscaler can drain your last healthy replicas.
- **Overprovision for latency.** Node provisioning takes tens of seconds at best. A low-priority "balloon" Deployment holding spare capacity, which real Pods preempt, converts a cold-start into an instant schedule.
- **Watch the cascade.** An HPA that scales on latency can amplify an incident: slow database → high latency → more replicas → more connections → slower database. Scale on the signal that represents _demand_ (queue depth, RPS), not on the symptom.

## Example

```yaml
# HPA v2: two metrics, asymmetric behaviour.
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 3
  maxReplicas: 50
  metrics:
    - type: Resource
      resource:
        name: cpu
        target: { type: Utilization, averageUtilization: 70 }
    - type: Pods # requests-per-second per Pod, via Prometheus Adapter
      pods:
        metric: { name: http_requests_per_second }
        target: { type: AverageValue, averageValue: "100" }
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      policies: [{ type: Percent, value: 100, periodSeconds: 30 }] # double every 30s
    scaleDown:
      stabilizationWindowSeconds: 300 # wait 5 min of calm before shrinking
      policies: [{ type: Percent, value: 10, periodSeconds: 60 }]
```

```yaml
# KEDA: scale a worker on SQS backlog, all the way to zero.
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: worker
spec:
  scaleTargetRef: { name: worker }
  minReplicaCount: 0
  maxReplicaCount: 100
  cooldownPeriod: 300
  triggers:
    - type: aws-sqs-queue
      metadata:
        queueURL: https://sqs.eu-west-1.amazonaws.com/123456789012/jobs
        queueLength: "20" # ~20 messages per replica
        awsRegion: eu-west-1
```

```bash
kubectl get hpa api --watch          # current vs target, and replica moves
kubectl describe hpa api             # events explain every refusal to scale
kubectl top pods -l app=api          # is the metrics-server even reporting?
```

## Interview tips

- Answer in three layers - Pod count, Pod size, node count - and say explicitly that HPA without a node autoscaler just produces `Pending` Pods.
- The CPU-utilisation-is-relative-to-requests detail is the most common real-world HPA bug; volunteering it is a strong signal.
- Never claim you run HPA and VPA on the same metric. Knowing they conflict is a standard checkpoint.
- For queue-backed workers, name KEDA and scale-to-zero. "We scaled workers on CPU" invites the follow-up about why that does not track backlog.
- Karpenter vs Cluster Autoscaler: node-group-free, right-sized instances, and consolidation for cost. Expect a cost follow-up right after.
- Have a cascading-failure story ready - "a misconfigured HPA made an incident worse" is now a common senior-level scenario question.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you troubleshoot a failed Helm release?]] (`#412`): [How do you troubleshoot a failed Helm release?](../container-orchestration-advanced/how-do-you-troubleshoot-a-failed-helm-release.md)
- [[How do you run and scale a stateful application on Kubernetes?]] (`#413`): [How do you run and scale a stateful application on Kubernetes?](../container-orchestration-advanced/how-do-you-run-and-scale-a-stateful-application-on-kubernetes.md)
- [[What are CustomResourceDefinitions and operators in Kubernetes?]] (`#452`): [What are CustomResourceDefinitions and operators in Kubernetes?](../container-orchestration-advanced/what-are-customresourcedefinitions-and-operators-in-kubernetes.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
