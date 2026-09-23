---
title: "What is Kubernetes Topology Spread Constraints and how does it differ from Pod Anti-Affinity?"
id: 526
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - kubernetes
  - scheduling
  - high-availability
  - topology
quiz:
  stem: "Why do Topology Spread Constraints scale better than hard Pod Anti-Affinity across multi-zone Kubernetes clusters?"
  options:
    - "Topology Spread Constraints bypass Kubelet health checks"
    - "Pod Anti-Affinity prevents running more pods than available zones, while Topology Spread allows proportional distribution with a configurable maxSkew"
    - "Topology Spread Constraints only function on bare-metal clusters"
    - "Pod Anti-Affinity requires disabling cluster autoscaling"
  answer: 2
  explanation: "Hard anti-affinity blocks scheduling once every zone has 1 pod. Topology Spread Constraints allow scaling to arbitrary replica counts while maintaining a balanced distribution across zones (e.g. 4-4-3)."
---

# What is Kubernetes Topology Spread Constraints and how does it differ from Pod Anti-Affinity?

**Short answer:** Topology spread constraints tell the scheduler to keep matching Pods **evenly distributed** across a topology domain - zones, nodes, racks - within a tolerated imbalance, `maxSkew`. Pod anti-affinity is a **per-domain yes/no rule**: "do not put this Pod in a domain that already has a matching Pod". That makes hard anti-affinity a cap (with three zones you can never run more than three Pods), while spread constraints scale to any replica count and simply keep the distribution balanced, such as 4-3-3. Use spread constraints for HA distribution and keep anti-affinity for strict "never co-locate" rules.

## Detail

**Anti-affinity, and why it caps you.** `podAntiAffinity` with `requiredDuringSchedulingIgnoredDuringExecution` and `topologyKey: topology.kubernetes.io/zone` forbids a second matching Pod in any zone. With three zones the fourth replica has nowhere legal to go and stays `Pending`. The `preferred` form avoids the cap but gives no balance guarantee - once every zone has one Pod, the preference cannot be satisfied and later Pods may pile into one zone. Required anti-affinity is also expensive for the scheduler to evaluate on large clusters.

**How spread constraints work.** For each candidate node, the scheduler counts matching Pods (by `labelSelector`) in each domain of `topologyKey` and computes the **skew**: the count in the candidate's domain after placement minus the minimum count across eligible domains. A node is acceptable if the skew stays within `maxSkew`.

- `maxSkew: 1` across three zones with ten replicas yields 4-3-3.
- `whenUnsatisfiable: DoNotSchedule` makes it a hard filter (the Pod stays `Pending` rather than breaking the spread); `ScheduleAnyway` makes it a scoring preference.
- Multiple constraints combine - typically one per zone (hard) and one per node (soft).

**Fields worth knowing.**

- `minDomains` - with `DoNotSchedule`, treat fewer than N eligible domains as a skew violation, so a cluster autoscaler brings up nodes in a new zone instead of stacking Pods into the zones that exist.
- `matchLabelKeys: [pod-template-hash]` - compute skew per Deployment revision, so a rolling update spreads the new ReplicaSet evenly instead of counting old and new Pods together.
- `nodeAffinityPolicy` / `nodeTaintsPolicy` - whether nodes excluded by the Pod's node affinity or by taints count as domains.
- Cluster-level defaults can be set in the scheduler configuration, so every workload gets a sensible spread without each team writing it.

**Limitations and trade-offs.**

- Spread is enforced **only at scheduling time**. Scale-down, evictions, or a node failure can leave the distribution skewed, and nothing moves running Pods back; the descheduler's `RemovePodsViolatingTopologySpreadConstraint` plugin is the usual fix.
- A hard zone constraint plus a zone outage means new replicas go `Pending` rather than piling into surviving zones - availability versus balance is a choice you make with `whenUnsatisfiable`.
- Skew is computed over nodes that exist; without `minDomains`, an empty zone with no nodes is invisible.

| Need                                                 | Tool                                                   |
| ---------------------------------------------------- | ------------------------------------------------------ |
| Balanced replicas across zones or nodes at any scale | `topologySpreadConstraints`                            |
| "Never two of these on one node" (e.g. a quorum set) | Required pod anti-affinity on `kubernetes.io/hostname` |
| "Keep these apart from that noisy workload"          | Pod anti-affinity against the other workload's labels  |
| "Co-locate with the cache"                           | Pod affinity                                           |

## Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: payment-api }
spec:
  replicas: 10
  selector: { matchLabels: { app: payment-api } }
  template:
    metadata: { labels: { app: payment-api } }
    spec:
      topologySpreadConstraints:
        - maxSkew: 1 # zones differ by at most one Pod: 4-3-3
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          minDomains: 3 # insist on three zones, so the autoscaler adds one if needed
          labelSelector: { matchLabels: { app: payment-api } }
          matchLabelKeys: [pod-template-hash] # spread each rollout revision on its own
        - maxSkew: 1 # and spread across nodes, softly
          topologyKey: kubernetes.io/hostname
          whenUnsatisfiable: ScheduleAnyway
          labelSelector: { matchLabels: { app: payment-api } }
      containers:
        - name: api
          image: registry.example.com/payment-api:2.4.1
```

```bash
# Count replicas per zone to check the spread actually holds
kubectl get pods -l app=payment-api -o wide --no-headers \
  | awk '{print $7}' | xargs -I{} kubectl get node {} -L topology.kubernetes.io/zone --no-headers \
  | awk '{print $NF}' | sort | uniq -c
```

## Interview tips

- Give the headline contrast: anti-affinity is binary per domain and caps replicas at the domain count; spread constraints balance within `maxSkew` at any scale.
- Explain skew with numbers - ten replicas, three zones, `maxSkew: 1`, so 4-3-3.
- Know `DoNotSchedule` versus `ScheduleAnyway`, and the availability-versus-balance trade-off during a zone outage.
- Volunteer `minDomains` and `matchLabelKeys: [pod-template-hash]` - they fix the two classic surprises (empty zones ignored, rollouts skewing the spread).
- Point out that spread is not maintained after scheduling and name the descheduler as the rebalancing tool.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)
- [[How do you troubleshoot a failed Helm release?]] (`#412`): [How do you troubleshoot a failed Helm release?](../container-orchestration-advanced/how-do-you-troubleshoot-a-failed-helm-release.md)
- [[How do you run and scale a stateful application on Kubernetes?]] (`#413`): [How do you run and scale a stateful application on Kubernetes?](../container-orchestration-advanced/how-do-you-run-and-scale-a-stateful-application-on-kubernetes.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
