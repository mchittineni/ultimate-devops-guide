---
title: "What is Spot Instance pricing?"
id: 93
category: "Cloud Cost Optimization"
difficulty: "Intermediate"
tags:
  - devops
  - cloud-cost-optimization
  - interview-questions
---

# What is Spot Instance pricing?

**Short answer:** Spot instances sell a cloud provider's spare capacity at up to 90% off on-demand, on the condition that it can be reclaimed with a short warning - typically two minutes - making it ideal for interruptible workloads.

## Detail

**How it works.** AWS Spot, Azure Spot VMs, and GCP Spot/Preemptible VMs all offer unused capacity at a steep discount. AWS prices Spot on supply and demand per instance type and availability zone, and issues a two-minute interruption notice before reclaiming. GCP preemptible VMs are capped at 24 hours; GCP Spot VMs have no time cap.

**Good fits:** CI/CD runners, batch and ETL jobs, data processing (Spark, Flink), machine-learning training with checkpointing, stateless web tiers behind an autoscaler, and rendering. Poor fits: single-instance databases, licence-bound software, and anything where a two-minute eviction cannot be tolerated.

**Designing for interruption**

- Spread across many instance types and availability zones - diversification is the single biggest reliability factor, since each pool is reclaimed independently.
- Handle the interruption notice: drain connections, checkpoint work, deregister from the load balancer.
- Mix capacity types: a base of on-demand or reserved capacity plus a spot layer for elasticity.
- On Kubernetes, run spot node groups with taints and tolerations, use PodDisruptionBudgets, and let Karpenter or the Cluster Autoscaler consolidate. The AWS Node Termination Handler cordons and drains on the interruption signal.

## Example

```yaml
# Karpenter: prefer spot, fall back to on-demand, diversified instance types
apiVersion: karpenter.sh/v1
kind: NodePool
metadata: { name: batch }
spec:
  template:
    spec:
      requirements:
        - {
            key: karpenter.sh/capacity-type,
            operator: In,
            values: ["spot", "on-demand"],
          }
        - { key: kubernetes.io/arch, operator: In, values: ["amd64", "arm64"] }
      taints:
        - { key: workload, value: batch, effect: NoSchedule }
  disruption: { consolidationPolicy: WhenEmptyOrUnderutilized }
```

## Interview tips

- Instance-type and AZ diversification is the answer to "how do you make spot reliable?"
- Describe what your application does in the two-minute window - that is the practical test.
- The mature pattern is a blended fleet: reserved baseline, on-demand buffer, spot for burst.

---

[⬅ Back to Cloud Cost Optimization](./README.md) · [All topics](../README.md)
