---
title: "How do you upgrade a production Kubernetes cluster with zero downtime?"
id: 411
category: "Container Orchestration Advanced"
difficulty: "Advanced"
tags:
  - devops
  - container-orchestration-advanced
  - interview-questions
  - kubernetes
  - scalability-and-high-availability
  - backup-and-disaster-recovery
---

# How do you upgrade a production Kubernetes cluster with zero downtime?

**Short answer:** Upgrade in the supported order - **API deprecations first, then the control plane, then add-ons, then worker nodes** - one minor version at a time, never skipping versions. Before touching anything, run a deprecated-API scan (`kubectl-convert`, Pluto, or `kubent`) and fix the manifests, because a removed API is what actually breaks an upgrade. Nodes are replaced rather than upgraded in place: cordon, drain honouring PodDisruptionBudgets, replace, validate, repeat - or roll a new node group and shift workloads to it. The zero-downtime property comes from the workloads, not the upgrade: multiple replicas, PDBs, correct probes, and topology spread. On managed clusters the control-plane step is one API call; the risk lives entirely in the deprecations and the node roll.

## Detail

### Before the upgrade

1. **Read the release notes and the deprecation guide for every version you are crossing.** Kubernetes supports **one minor version at a time** (n → n+1) and a kubelet may trail the API server by at most 2-3 minor versions depending on the release. Skipping is unsupported and, on managed platforms, blocked.
2. **Scan for removed and deprecated APIs** - this is the step that prevents most upgrade incidents. `kubent` or Pluto over live objects _and_ over your Git manifests and Helm charts, because the chart you deploy tomorrow matters as much as the object running today. Old `policy/v1beta1 PodDisruptionBudget`, `batch/v1beta1 CronJob`, and long-tail CRDs are the usual finds.
3. **Check add-on compatibility** - CNI, CSI drivers, ingress controller, metrics-server, cluster autoscaler or Karpenter, service mesh, and any webhook. A failing admission webhook after an upgrade blocks every write to the cluster, which is as close to a full outage as Kubernetes gets. Also verify controller RBAC still matches, and that mutating/validating webhooks have `failurePolicy` you can live with.
4. **Back up state.** On self-managed clusters, snapshot etcd (`etcdctl snapshot save`) and verify the snapshot restores. On managed clusters the control plane is the provider's problem, but back up cluster resources and PVs anyway (Velero) - your objects and data are yours. See [how do you execute a Disaster Recovery failover with minimal RTO and RPO](../backup-and-disaster-recovery/how-do-you-execute-a-disaster-recovery-failover-with-minimal-rto-and-rpo.md).
5. **Verify the workloads can survive node replacement**: replica count above one, PodDisruptionBudgets that allow progress (a PDB requiring 100% availability blocks drains for ever), readiness probes that mean something, graceful shutdown with `preStop` and a sensible `terminationGracePeriodSeconds`, and topology spread across zones. Any singleton Pod without a PDB will have a gap - decide consciously whether that is acceptable.
6. **Rehearse in a non-production cluster of the same version and shape**, and pick a low-traffic window even though you expect no impact.

### The upgrade order

**Control plane first.** Managed: `aws eks update-cluster-version`, `az aks upgrade --control-plane-only`, `gcloud container clusters upgrade --master`. Self-managed: `kubeapi`/scheduler/controller-manager per control-plane node, one at a time behind their load balancer, with `kubeadm upgrade plan` and `kubeadm upgrade apply`. A newer control plane serving older kubelets is supported; the reverse is not - which is the reason for the order.

**Add-ons next**, to versions that support both the old and new Kubernetes where possible.

**Then worker nodes, by replacement.** Two patterns:

- **In-place rolling replacement** - for each node: `kubectl cordon`, `kubectl drain --ignore-daemonsets --delete-emptydir-data` (which respects PDBs and blocks if they cannot be satisfied), terminate the node, let the node group bring up a replacement on the new version, verify, then continue. Slow, simple, no extra quota.
- **Blue/green node groups** - create a new node group at the new version, cordon the old one, drain progressively, watch, and delete the old group once stable. Faster to abort, needs double capacity briefly, and is the pattern I would default to for large clusters. Karpenter's drift handling does this continuously.

**Validate between steps**: node versions, all system Pods ready, DNS resolving, a test deployment scheduling and passing traffic, your own SLO dashboards, and `kubectl get events -A` for admission or CSI errors.

### The failure modes worth naming

- **A drain that never finishes** - a PDB that cannot be satisfied, a Pod with no controller (bare Pod), or a StatefulSet with one replica. `kubectl drain` waits rather than violating the budget; decide per workload whether to accept the disruption or fix the redundancy first.
- **Long-lived connections** dropped on node replacement even with correct rolling - WebSockets, gRPC streams, and database sessions need client reconnection and a `preStop` grace window.
- **Zonal volumes** - a Pod with an EBS-backed PVC can only be rescheduled into the same availability zone; if the new node group lacks capacity there, the Pod stays `Pending`. See [how do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-waiting-for-a-persistentvolumeclaim.md).
- **No control-plane rollback.** Kubernetes control-plane upgrades are one-way on every managed platform. Your rollback plan is either "restore etcd from snapshot" (self-managed) or "build a new cluster at the old version and fail traffic back" - which is why the deprecation scan and the rehearsal matter so much, and why staying close to the current version is a reliability strategy rather than a chore.

### The strategic answer

Upgrade small and often. A cluster two minors behind requires two sequential upgrades and carries twice the deprecation risk; a cluster six behind is a migration project. Where the estate is large, the least-risk pattern is **immutable clusters**: stand up a new cluster at the new version, deploy everything through GitOps, shift traffic at the DNS or global load-balancer layer, and delete the old one. That converts an upgrade into a deployment - which you already know how to roll back. See [how do you run an application across multiple Kubernetes clusters](./how-do-you-run-an-application-across-multiple-kubernetes-clusters.md).

## Example

```bash
# 1. What will break? Scan live objects AND the manifests you are about to apply.
kubent --target-version 1.31          # deprecated/removed APIs in the cluster
pluto detect-files -d ./manifests -o wide --target-versions k8s=v1.31

# 2. Version skew reality check before starting
kubectl version --short
kubectl get nodes -o custom-columns='NAME:.metadata.name,KUBELET:.status.nodeInfo.kubeletVersion'

# 3. Self-managed control plane, one node at a time
kubeadm upgrade plan v1.31.4 && sudo kubeadm upgrade apply v1.31.4

# 4. Worker replacement loop - drain respects PodDisruptionBudgets
for n in $(kubectl get nodes -l version=old -o name); do
  kubectl cordon "${n#node/}"
  kubectl drain "${n#node/}" --ignore-daemonsets --delete-emptydir-data \
    --timeout=15m --grace-period=60          # blocks if a PDB cannot be satisfied
  aws autoscaling terminate-instance-in-auto-scaling-group \
    --instance-id "$(kubectl get "$n" -o jsonpath='{.spec.providerID}' | awk -F/ '{print $NF}')" \
    --should-decrement-desired-capacity false
  kubectl wait --for=condition=Ready nodes -l version=new --timeout=10m
done

# 5. Validate between every step
kubectl get pods -A --field-selector=status.phase!=Running | grep -v Completed
kubectl -n kube-system get pods && kubectl get events -A --sort-by=.lastTimestamp | tail -20
```

```yaml
# The workload-side prerequisites - without these, "zero downtime" is a wish
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: checkout, namespace: prod }
spec:
  maxUnavailable: 1 # allows drains to progress; minAvailable:100% would block for ever
  selector: { matchLabels: { app: checkout } }
---
# Deployment excerpt
spec:
  replicas: 6
  template:
    spec:
      terminationGracePeriodSeconds: 60
      lifecycle:
        preStop: { exec: { command: ["sh", "-c", "sleep 10"] } } # drain endpoints first
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: ScheduleAnyway
          labelSelector: { matchLabels: { app: checkout } }
```

## Interview tips

- State the order and the reason: control plane before nodes, because a newer API server supports older kubelets but not the reverse. Add "one minor version at a time, no skipping".
- Lead the preparation with the deprecated-API scan. It is the step that actually prevents outages, and naming `kubent` or Pluto - and scanning your Git manifests too, not just live objects - is a strong signal.
- Say clearly that nodes are **replaced, not upgraded in place**, and describe cordon → drain → replace → validate.
- The line interviewers wait for: zero downtime is a property of the **workloads** (replicas, PDBs, probes, graceful shutdown, spread), not of the upgrade procedure.
- Bring up the PDB paradox - a budget too strict blocks the drain for ever - because it is the most common practical blocker.
- Be honest that control-plane upgrades cannot be rolled back, and give the real fallback: etcd snapshot restore, or a new cluster at the old version with traffic failed back.
- Mention add-on and webhook compatibility, and that a broken admission webhook blocks all writes - a failure mode people only learn once.
- Close with the strategy: upgrade small and often, or move to immutable clusters and turn upgrades into deployments. See [what is container orchestration and why do you need it](./what-is-container-orchestration-and-why-do-you-need-it.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
