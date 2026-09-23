---
title: "How does Kubernetes Rightsizing optimize CPU and memory requests to eliminate over-provisioning?"
id: 639
category: "Cloud Cost Optimization"
difficulty: "Intermediate"
tags:
  - devops
  - cloud-cost-optimization
  - interview-questions
  - kubernetes
  - rightsizing
  - finops
  - kubecost
quiz:
  stem: "Why does declaring excessively high CPU `requests` in a Pod manifest inflate cloud cluster costs even if the application consumes almost no CPU?"
  options:
    - "The Linux kernel throttles CPU speeds on overprovisioned pods"
    - "The Kubernetes scheduler reserves node capacity based on `requests`, forcing the cluster autoscaler to provision more physical nodes than needed"
    - "Cloud providers charge penalties for idle CPU cycles"
    - "Overprovisioned pods automatically disable container caching"
  answer: 2
  explanation: "Kube-scheduler uses `requests` for bin-packing. If a pod requests 4 cores, the scheduler reserves those cores regardless of actual usage, forcing the cluster autoscaler to add expensive nodes."
---

# How does Kubernetes Rightsizing optimize CPU and memory requests to eliminate over-provisioning?

**Short answer:** Kubernetes rightsizing analyzes actual historical CPU and memory utilization against declared `resources.requests`, trimming oversized requests so the cluster scheduler can pack more pods per node, directly reducing the total node count and cloud bill.

## Detail

In Kubernetes, **nodes are provisioned for `requests`, not actual usage**. The scheduler places Pods by summing requests against each node's allocatable capacity, and the cluster autoscaler or Karpenter adds nodes when Pods do not fit. If a developer sets `requests: { cpu: "4", memory: "16Gi" }` for an application that uses 0.2 CPU and 500 MiB, the cluster reserves - and you pay for - the full 4 cores and 16 GiB. Multiply by hundreds of Deployments and the cluster runs mostly idle.

### The slack metric

$$\text{Resource slack} = \text{Resource request} - \text{Observed usage (p95/p99)}$$

Summed across a namespace and priced per core-hour and GiB-hour, slack is the money you can recover.

### Tools and practices

1. **Measure first**: CPU and memory usage per container over at least one to two weeks, including the busiest business periods (month-end, peak days), from Prometheus or metrics-server history.
2. **Vertical Pod Autoscaler (VPA) recommender**: keeps a decaying histogram of usage (an eight-day half-life by default) and recommends target requests. Run it in `Off` mode to get recommendations without changes, and feed them into manifests through pull requests. With **in-place Pod resize** now stable (Kubernetes 1.35), VPA's `InPlaceOrRecreate` mode can apply CPU and memory changes to running Pods without recreating them in most cases.
3. **Cost attribution**: OpenCost or Kubecost price the slack per namespace and workload, which turns it into a number owners respond to (_"team checkout reserves $4,500/month of CPU it never uses"_).
4. **Set sensible values**:
   - **CPU request** near p95 usage plus headroom; many teams omit CPU limits (or set them generously) to avoid CFS throttling, relying on requests for fair sharing.
   - **Memory request and limit** based on p99 plus headroom, usually with limit equal to request for predictable behaviour - memory cannot be throttled, only OOM-killed.
5. **Guardrails**: `LimitRange` defaults so Pods without requests do not become best-effort, and `ResourceQuota` per namespace so savings are not immediately consumed elsewhere.
6. **Close the loop at the node level**: shrinking requests only saves money if the autoscaler removes the freed nodes - enable consolidation (Karpenter) or scale-down (cluster autoscaler).

**Trade-offs.** Cutting requests too close to usage invites CPU contention and OOM kills at peak, and VPA does not work well together with an HPA scaling on the same CPU or memory metric. Right-size gradually, watch error rates and latency SLOs, and exclude workloads with spiky or seasonal profiles from automatic changes.

## Example

```yaml
# VPA in recommendation-only mode: read the numbers, then change manifests via PR.
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata: { name: checkout, namespace: shop }
spec:
  targetRef: { apiVersion: apps/v1, kind: Deployment, name: checkout }
  updatePolicy: { updateMode: "Off" } # "InPlaceOrRecreate" once you trust it
  resourcePolicy:
    containerPolicies:
      - containerName: "*"
        minAllowed: { cpu: 100m, memory: 128Mi }
        maxAllowed: { cpu: "2", memory: 4Gi }
```

```bash
kubectl -n shop get vpa checkout -o jsonpath='{.status.recommendation.containerRecommendations[0]}'
# {"containerName":"checkout","target":{"cpu":"350m","memory":"612Mi"},
#  "upperBound":{"cpu":"900m","memory":"1Gi"}, ...}      <- vs 4 CPU / 16Gi requested

# Cluster-wide view: requested versus used CPU (PromQL via kube-state-metrics + cAdvisor)
# sum(kube_pod_container_resource_requests{resource="cpu"})
#   / sum(rate(container_cpu_usage_seconds_total{container!=""}[5m]))
```

## Interview tips

- Lead with the mechanism: the scheduler and autoscaler work on requests, so over-requesting buys idle nodes.
- Define slack and explain how you would measure it over a representative period.
- Name VPA's recommender (and `Off` mode), and mention in-place Pod resize being stable in 1.35 with VPA's `InPlaceOrRecreate` mode.
- Distinguish CPU (compressible, throttled) from memory (incompressible, OOM-killed) when setting requests and limits.
- Close with the trade-off and the node-level step: savings only materialise if consolidation removes the freed nodes.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[What are ephemeral preview environments and how do you manage their lifecycle and cleanup?]] (`#535`): [What are ephemeral preview environments and how do you manage their lifecycle and cleanup?](../cicd/what-are-ephemeral-preview-environments-and-how-do-you-manage-their-lifecycle-and-cleanup.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Cost Optimization](./README.md) · [All topics](../README.md)
