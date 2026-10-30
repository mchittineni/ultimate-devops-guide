---
title: "How do you upgrade an Amazon EKS cluster safely?"
id: 755
category: "AWS Engineering"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - aws-engineering
  - kubernetes
  - eks
quiz:
  stem: "An EKS cluster runs Kubernetes 1.34 and its managed node groups run 1.33. What is the correct upgrade order to reach 1.35?"
  options:
    - "Upgrade the node groups to 1.35 first, then the control plane directly to 1.35."
    - "Upgrade the control plane to 1.35 in one step, then the nodes."
    - "Upgrade the control plane to 1.35 (one minor version), then update the add-ons, then roll the nodes to 1.35."
    - "Delete and recreate the cluster, because EKS does not support in-place upgrades."
  answer: 3
  explanation: "EKS upgrades the control plane one minor version at a time and never downgrades, and nodes may not be newer than the control plane - so the control plane goes first (1.34 to 1.35 is a single minor step), then compatible add-on versions, then the data plane. Upgrading nodes first would put kubelets ahead of the API server, which Kubernetes' version-skew policy forbids."
---

# How do you upgrade an Amazon EKS cluster safely?

**Short answer:** In a fixed order: **check** (EKS upgrade insights and a deprecated-API scan, add-on compatibility, five free IPs in the cluster subnets), **control plane** one minor version at a time with `update-cluster-version` (no downgrade, so it is a one-way door), **add-ons** (VPC CNI, CoreDNS, kube-proxy, the Pod Identity agent, CSI drivers) to versions built for the new release, then the **data plane** - managed node groups roll with PDBs respected, Karpenter replaces drifted nodes automatically, Fargate Pods need a restart. Pod disruption budgets, multiple replicas, and readiness probes are what make the node roll invisible to users. Each version gets **14 months of standard support** and then **12 months of paid extended support**, so the honest framing is a quarterly-ish treadmill you plan for, not an occasional project.

## Detail

### Why there is no "skip this year"

Kubernetes ships three minor releases a year, and EKS supports each one for 14 months at the standard price. After that the cluster moves to **extended support** for another 12 months at roughly six times the per-cluster hourly charge - or, if the cluster's **upgrade policy** is set to `STANDARD`, EKS upgrades the control plane for you at the end of standard support. Either way, a version cannot be held forever, and you cannot jump versions: 1.33 to 1.35 is two upgrades.

### The pre-flight checklist

1. **Upgrade insights**: `aws eks list-insights` reports deprecated API usage seen in the audit logs, add-on incompatibilities, and node version skew - the findings EKS itself thinks will break.
2. **Deprecated and removed APIs**: scan the manifests in Git and the live cluster with `pluto` or `kubent`. Removed APIs (an old `flowcontrol` or `autoscaling` version) are the classic failure: the upgrade succeeds and the next Helm release fails.
3. **Add-on matrix**: `describe-addon-versions --kubernetes-version` gives the compatible VPC CNI, CoreDNS, and kube-proxy builds; also check third-party controllers (ingress, cert-manager, Karpenter, the AWS Load Balancer Controller) against their own support matrices.
4. **Capacity**: the control plane upgrade needs up to five free IP addresses in the subnets the cluster was created with - an exhausted subnet blocks it.
5. **Rehearse** on a non-production cluster at the same version, with the same add-ons.

### Control plane, then add-ons, then nodes

- **Control plane**: `update-cluster-version` replaces the API servers behind the endpoint; it takes a while and the API stays available, but watch controllers that hold long watches. It cannot be rolled back.
- **Add-ons**: update managed add-ons with `update-addon` (and `--resolve-conflicts PRESERVE` if you customised their configuration). kube-proxy should match the new minor; VPC CNI and CoreDNS have their own recommended builds.
- **Data plane**: nodes may lag the control plane by up to three minor versions (Kubernetes' skew policy), which gives you time but not permission to forget them.
  - **Managed node groups**: `update-nodegroup-version` launches new nodes, cordons and drains old ones honouring PDBs (with a force option if a PDB blocks forever), within a configurable `maxUnavailable`.
  - **Karpenter**: change the AMI selector (or let it track the EKS-optimised alias) and its **drift** detection replaces nodes gradually under disruption budgets.
  - **Fargate**: running Pods keep their version until they are restarted - roll the Deployments.
  - **EKS Auto Mode** upgrades the nodes it manages for you after the control plane moves.

### What makes the node roll invisible

PodDisruptionBudgets on every multi-replica workload (and none that allow zero disruptions, which deadlocks the drain), at least two replicas spread across zones with `topologySpreadConstraints`, readiness probes so traffic only reaches ready Pods, graceful `SIGTERM` handling with a `preStop` delay so the load balancer deregisters a target before the process exits, and enough spare capacity for the surge.

### Blue/green clusters

For a large jump (several versions behind) or a risky change (a CNI swap), build a new cluster at the target version, deploy everything through GitOps, and shift traffic with weighted DNS or the load balancer. It costs a second cluster for a while and requires stateless workloads or externalised state, but it gives you something in-place upgrades never can: a rollback.

## Example

```bash
CLUSTER=prod
TARGET=1.35   # one minor version above the current control plane

# 1. What does EKS think will break?
aws eks list-insights --cluster-name "$CLUSTER" \
  --query 'insights[].[name,insightStatus.status]' --output table
kubent --target-version "$TARGET"        # removed/deprecated APIs in the live cluster

# 2. Control plane (one-way door)
aws eks update-cluster-version --name "$CLUSTER" --kubernetes-version "$TARGET"
aws eks wait cluster-active --name "$CLUSTER"

# 3. Add-ons: pick the default build for the new version
for addon in vpc-cni coredns kube-proxy eks-pod-identity-agent; do
  v=$(aws eks describe-addon-versions --addon-name "$addon" --kubernetes-version "$TARGET" \
      --query 'addons[0].addonVersions[?compatibilities[0].defaultVersion].addonVersion | [0]' --output text)
  aws eks update-addon --cluster-name "$CLUSTER" --addon-name "$addon" \
    --addon-version "$v" --resolve-conflicts PRESERVE
done

# 4. Data plane: managed node group rolls, honouring PDBs
aws eks update-nodegroup-version --cluster-name "$CLUSTER" --nodegroup-name general \
  --kubernetes-version "$TARGET"
kubectl get nodes -L eks.amazonaws.com/nodegroup -o wide   # watch kubelet versions converge

# Opt out of paid extended support: EKS auto-upgrades at end of standard support instead
aws eks update-cluster-config --name "$CLUSTER" --upgrade-policy supportType=STANDARD
```

```yaml
# The guardrail that keeps a drain from taking a service down
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: checkout, namespace: prod }
spec:
  minAvailable: 2 # with replicas >= 3; never a value that allows zero evictions
  selector: { matchLabels: { app: checkout } }
```

## Interview tips

- Give the order and say why it is fixed: control plane first (nodes may never be newer than the API server), one minor version at a time, no rollback - then add-ons, then nodes.
- Name **upgrade insights** and a deprecated-API scan as the pre-flight, and the removed-API failure mode (the upgrade succeeds, the next deploy fails).
- Know the support numbers: 14 months standard, 12 months extended at a much higher price, and the upgrade policy that lets EKS force the upgrade instead.
- Explain how each data-plane type rolls: managed node groups drain with PDBs, Karpenter replaces drifted nodes, Fargate needs Pod restarts.
- Mention a PDB that allows zero disruptions as the classic stuck drain, and the five-free-IPs requirement as the classic blocked control-plane upgrade.
- Offer blue/green clusters for big jumps, and be honest that it needs GitOps and externalised state. See [how do you upgrade a production Kubernetes cluster with zero downtime](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md), [what is the difference between ECS, EKS, and Fargate](./what-is-the-difference-between-ecs-eks-and-fargate.md), and [securing Pod access with EKS Pod Identity or IRSA](./how-do-you-secure-pod-access-to-aws-resources-using-eks-pod-identity-or-irsa.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?]] (`#407`): [How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-waiting-for-a-persistentvolumeclaim.md)
- [[What is Kubernetes?]] (`#11`): [What is Kubernetes?](../kubernetes/what-is-kubernetes.md)
- [[What are the main components of Kubernetes architecture?]] (`#12`): [What are the main components of Kubernetes architecture?](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
