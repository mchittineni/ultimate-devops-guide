---
title: "What is the difference between Kubernetes Horizontal Pod Autoscaler and Vertical Pod Autoscaler?"
id: 521
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - kubernetes
  - scaling
  - hpa
  - vpa
quiz:
  stem: "Why is it generally discouraged to configure both HPA and VPA to act concurrently on CPU utilization for the same workload?"
  options:
    - "The Kubernetes API server will reject the manifest with a validation error"
    - "Both controllers enter a conflicting race loop: VPA enlarges the pod while HPA simultaneously adds more replicas"
    - "VPA does not support CPU metrics, only memory metrics"
    - "HPA can only scale DaemonSets while VPA can only scale Deployments"
  answer: 2
  explanation: "If both target the same metric, high load triggers both horizontal scaling (more replicas) and vertical resizing (larger pods) simultaneously, wasting resources and destabilizing metrics."
---

# What is the difference between Kubernetes Horizontal Pod Autoscaler and Vertical Pod Autoscaler?

**Short answer:** The **Horizontal Pod Autoscaler** changes how many replicas run, reacting within seconds to a live metric such as CPU utilisation, requests per second, or queue depth. The **Vertical Pod Autoscaler** changes how big each replica is - its CPU and memory requests (and proportionally its limits) - based on usage history observed over days. HPA is built into Kubernetes; VPA is a separate add-on from the Kubernetes autoscaler project. Use HPA for load that varies with traffic and VPA for right-sizing; do not let both act on the same CPU or memory signal, because each changes the number the other is measuring.

## Detail

| Aspect          | HPA (horizontal)                                                                  | VPA (vertical)                                                                                       |
| --------------- | --------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| What it changes | `replicas` on a Deployment, StatefulSet, or any `scale` subresource               | `resources.requests`/`limits` of the Pods' containers                                                |
| Signal          | Current metrics: Metrics Server (CPU/memory), custom or external metrics adapters | Historical usage percentiles from the VPA recommender                                                |
| Reaction time   | Seconds to a minute (15 s sync loop plus stabilisation windows)                   | Hours to days - it is a sizing tool, not a burst tool                                                |
| Disruption      | Scale-out adds Pods; scale-in removes them (PDBs do not apply)                    | `Recreate` evicts Pods to apply; `InPlaceOrRecreate` resizes running Pods and evicts only if it must |
| Where it shines | Stateless services and workers whose load tracks traffic                          | Workloads that cannot scale out easily, and finding correct requests for everything else             |
| Ships with      | Kubernetes (`autoscaling/v2`)                                                     | Separate install (CRDs plus recommender, updater, and admission controller)                          |

**HPA mechanics.** Every 15 seconds the controller computes `desiredReplicas = ceil(currentReplicas × currentValue / targetValue)` for each metric and takes the largest. Resource utilisation is a percentage **of the Pod's request**, so bad requests produce bad scaling. A 10% tolerance and the `behavior` stabilisation windows (300 s on scale-down by default) stop flapping. KEDA builds on HPA to scale on event sources and to zero.

**VPA mechanics.** The recommender builds usage histograms and produces a target plus lower and upper bounds per container. The `updateMode` decides what happens next:

- `Off` - recommendations only, written to the VPA object's status. The safe starting point.
- `Initial` - applies the recommendation only when Pods are created.
- `Recreate` - evicts Pods whose requests are far from the recommendation so they come back resized. (The old `Auto` mode is now a deprecated alias for this.)
- `InPlaceOrRecreate` - uses in-place Pod resize (GA in Kubernetes 1.35) to change requests on the running Pod, falling back to eviction when the node cannot accommodate the change.

**Running them together.** Both acting on CPU creates a feedback loop: VPA raises the CPU request, utilisation (usage ÷ request) drops, HPA removes replicas, per-Pod usage rises, VPA raises requests again. Safe combinations:

- VPA in `Off` mode feeding recommendations into your manifests, with HPA active.
- HPA on a custom or external metric (RPS, queue depth) with VPA managing CPU and memory.
- VPA restricted with `controlledResources: ["memory"]` while HPA scales on CPU.

**Limitations.** VPA needs enough history to be useful, can recommend more than any node offers (cap it with `maxAllowed`), and in `Recreate` mode evicts through the Eviction API, so a tight PDB can stop it applying recommendations at all. HPA cannot scale below one replica without an add-on like KEDA and depends on metrics availability - if the metrics pipeline breaks, scaling stops.

## Example

```yaml
# HPA on CPU for the web tier
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: { name: web }
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: web }
  minReplicas: 3
  maxReplicas: 30
  metrics:
    - type: Resource
      resource: { name: cpu, target: { type: Utilization, averageUtilization: 70 } }
---
# VPA on the same Deployment, but memory only - no fight over CPU
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata: { name: web }
spec:
  targetRef: { apiVersion: apps/v1, kind: Deployment, name: web }
  updatePolicy: { updateMode: InPlaceOrRecreate }
  resourcePolicy:
    containerPolicies:
      - containerName: "*"
        controlledResources: ["memory"]
        maxAllowed: { memory: 4Gi }
```

```bash
kubectl get hpa web                         # TARGETS: current/target, REPLICAS
kubectl describe vpa web | sed -n '/Recommendation/,$p'   # target, lower and upper bounds
```

## Interview tips

- One line each: HPA changes the replica count from live metrics; VPA changes Pod size from usage history.
- Explain why they conflict on CPU with the utilisation-is-relative-to-requests loop, then give the safe combinations.
- Name the VPA modes - `Off`, `Initial`, `Recreate`, `InPlaceOrRecreate` - and mention that in-place resize removed most of VPA's disruption.
- Point out that VPA is an add-on, not part of core Kubernetes, and that HPA quality depends on correct requests.
- Mention KEDA for event-driven and scale-to-zero cases, and the cluster autoscaler or Karpenter as the third layer that adds nodes.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)
- [[How do you troubleshoot a failed Helm release?]] (`#412`): [How do you troubleshoot a failed Helm release?](../container-orchestration-advanced/how-do-you-troubleshoot-a-failed-helm-release.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
