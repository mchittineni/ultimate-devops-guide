---
title: "How do you leverage Spot / Preemptible instances in Kubernetes without impacting production workloads?"
id: 637
category: "Cloud Cost Optimization"
difficulty: "Intermediate"
tags:
  - devops
  - cloud-cost-optimization
  - interview-questions
  - kubernetes
  - spot-instances
  - cost-optimization
  - karpenter
quiz:
  stem: "What is the primary risk of configuring an EKS Spot node group to use only a single instance type (e.g. strictly `c5.xlarge`)?"
  options:
    - "Kubernetes will crash on boot"
    - "If AWS exhausts spare capacity for that specific instance type in that zone, new pods will remain Pending and fail to scale"
    - "Spot instances do not support container networking"
    - "The cloud provider will charge full On-Demand prices automatically"
  answer: 2
  explanation: "Spot availability fluctuates. If an autoscaling group is locked to one instance type and AWS reclaims that pool, no replacement instances can be provisioned. Instance diversity prevents this."
---

# How do you leverage Spot / Preemptible instances in Kubernetes without impacting production workloads?

**Short answer:** Spot instances offer up to 90% discounts by utilizing spare cloud capacity, but can be reclaimed with a short interruption notice (2 minutes on AWS, about 30 seconds on Azure and GCP); Kubernetes runs them safely using diverse instance pools, graceful termination handlers, and pairing them with stateless, fault-tolerant workloads.

## Detail

Running everything on on-demand capacity wastes money on work that could tolerate interruption: stateless web replicas behind a load balancer, queue workers, batch jobs, and CI runners. The engineering problem is making interruptions invisible to users.

### Strategies for zero-downtime Spot adoption

1. **Instance diversity.** Each Spot pool (instance type × availability zone) is reclaimed independently. Never restrict a node group to one type: allow 10-20 compatible types across families, generations, and sizes (`c6i`, `c7i`, `m6i`, `m7i`, and Graviton equivalents if your images are multi-arch), across all zones. Use the **price-capacity-optimized** allocation strategy so the provider picks pools with the most spare capacity, not just the lowest price.
2. **Handle the interruption signal.** AWS publishes a two-minute interruption notice (and, often earlier, a rebalance recommendation) through instance metadata and EventBridge; Azure and GCP give about 30 seconds.
   - **Karpenter** handles this natively: it consumes interruption and rebalance events from an SQS queue, cordons and drains the node, and launches replacement capacity immediately.
   - Without Karpenter, the **AWS Node Termination Handler** (queue mode) does the cordon-and-drain for managed or self-managed node groups.
   - Drain respects **PodDisruptionBudgets**, and Pods must shut down cleanly on `SIGTERM` within `terminationGracePeriodSeconds` - less than the notice period.
3. **On-demand baseline plus Spot burst.** Keep the minimum capacity that must always exist (enough replicas to meet the SLO if every Spot node vanished) on on-demand or commitment-covered nodes, and put the elastic remainder on Spot. Karpenter can express this with separate NodePools and weights, or with a capacity-type spread.
4. **Spread replicas.** Topology spread constraints across zones and capacity types stop a single Spot reclaim from taking out most replicas of one service.
5. **Keep the wrong workloads off Spot.** Taint Spot nodes and let only tolerant workloads tolerate the taint. Single-writer databases, stateful singletons, long non-checkpointed jobs, and control-plane components (for example CoreDNS, ingress controllers, Karpenter itself) belong on on-demand capacity.

**Trade-offs.** Savings (commonly 60-90% off on-demand) come with more churn: more pod restarts, cold caches, and occasional capacity droughts when a whole region runs short of Spot. Measure interruption rates, and make sure the on-demand fallback has quota.

## Example

```yaml
# Karpenter v1: a Spot-preferred pool for tolerant workloads, diversified across types.
apiVersion: karpenter.sh/v1
kind: NodePool
metadata: { name: spot-general }
spec:
  template:
    spec:
      nodeClassRef: { group: karpenter.k8s.aws, kind: EC2NodeClass, name: default }
      requirements:
        - { key: karpenter.sh/capacity-type, operator: In, values: ["spot", "on-demand"] } # spot preferred, on-demand fallback
        - { key: karpenter.k8s.aws/instance-category, operator: In, values: ["c", "m", "r"] }
        - { key: karpenter.k8s.aws/instance-generation, operator: Gt, values: ["5"] }
        - { key: kubernetes.io/arch, operator: In, values: ["amd64", "arm64"] }
      taints:
        - { key: capacity, value: spot, effect: NoSchedule } # opt-in only
  disruption: { consolidationPolicy: WhenEmptyOrUnderutilized, consolidateAfter: 1m }
---
# A stateless service that opts in, with a PDB so drains never take too many at once.
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: web }
spec:
  minAvailable: 80%
  selector: { matchLabels: { app: web } }
```

## Interview tips

- Start with the trade: a deep discount for capacity that can be reclaimed with two minutes' notice (30 seconds on Azure and GCP).
- Instance and zone diversity with a capacity-aware allocation strategy is the core reliability answer.
- Explain the drain path: interruption event → Karpenter (or Node Termination Handler) cordons and drains → PDBs and graceful `SIGTERM` handling keep service up.
- Describe the on-demand baseline sized so the SLO holds even if all Spot capacity disappears.
- Say which workloads stay off Spot - stateful singletons, databases, critical cluster add-ons - and enforce it with taints.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[What are ephemeral preview environments and how do you manage their lifecycle and cleanup?]] (`#535`): [What are ephemeral preview environments and how do you manage their lifecycle and cleanup?](../cicd/what-are-ephemeral-preview-environments-and-how-do-you-manage-their-lifecycle-and-cleanup.md)
- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Cost Optimization](./README.md) · [All topics](../README.md)
