---
title: "What are namespaces in Kubernetes, and what do they isolate?"
id: 789
category: "Kubernetes"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - kubernetes
  - namespaces
  - multi-tenancy
  - rbac
quiz:
  stem: "Which of these resources is cluster-scoped rather than namespaced?"
  options:
    - "Secret"
    - "PersistentVolumeClaim"
    - "PersistentVolume"
    - "ServiceAccount"
  answer: 3
  explanation: "PersistentVolumes, Nodes, StorageClasses, ClusterRoles and CRDs are cluster-scoped, so a namespace does not contain or isolate them. The PVC that claims a PV is namespaced."
---

# What are namespaces in Kubernetes, and what do they isolate?

**Short answer:** A namespace is a named scope inside one cluster. It gives object names their own space (two teams can each have a Service called `api`) and it is the unit that **RBAC, ResourceQuota, LimitRange, Pod Security Admission, and NetworkPolicy** attach to. What it does **not** do by default is isolate anything at runtime: Pods in different namespaces can talk to each other over the network, share the same nodes and kernel, and share the same control plane. Namespaces are a boundary for administration, and only become a security boundary once you add policies on top.

## Detail

**What lives in a namespace.** Most workload objects are namespaced: Pods, Deployments, Services, ConfigMaps, Secrets, PVCs, ServiceAccounts, Roles, and RoleBindings. Some objects are **cluster-scoped** and belong to no namespace: Nodes, PersistentVolumes, StorageClasses, ClusterRoles, CustomResourceDefinitions, IngressClasses, and Namespaces themselves. `kubectl api-resources --namespaced=false` lists them.

**Built-in namespaces.**

- `default` - where objects go when no namespace is given. Fine for experiments, poor for real workloads.
- `kube-system` - control-plane add-ons such as CoreDNS, kube-proxy, and CNI agents.
- `kube-public` - readable by everyone, including unauthenticated clients; rarely used.
- `kube-node-lease` - one Lease object per node, used for cheap node heartbeats.

**What a namespace gives you.**

- **Name scoping and DNS.** A Service is reachable as `api` inside its own namespace and as `api.payments.svc.cluster.local` from anywhere else.
- **Access control.** A `Role` and `RoleBinding` grant permissions inside one namespace only, so "team A can deploy to `team-a`" is a RoleBinding.
- **Resource limits.** `ResourceQuota` caps total CPU, memory, storage, and object counts per namespace; `LimitRange` sets default and maximum requests and limits for each container.
- **Policy targeting.** Pod Security Admission is turned on with labels on the namespace (`pod-security.kubernetes.io/enforce: restricted`), and NetworkPolicies select peers with `namespaceSelector`, often using the automatic `kubernetes.io/metadata.name` label.
- **Lifecycle.** Deleting a namespace deletes everything in it, which is handy for preview environments and dangerous with a typo.

**What it does not isolate.**

- **Network.** With no NetworkPolicy, any Pod can reach any other Pod in the cluster. A default-deny policy per namespace is what makes the boundary real, and it needs a CNI that enforces policy.
- **Nodes and the kernel.** Pods from different namespaces share nodes unless you add taints, tolerations, and node affinity, and a container escape crosses namespaces.
- **Cluster-scoped resources.** A user with cluster-wide rights, a CRD, or a webhook affects every namespace.
- **The control plane.** One noisy tenant can still load the API server; API Priority and Fairness reduces this but does not remove it.

**Namespaces versus clusters.** Using `dev`, `test`, and `prod` namespaces in one cluster is a common first answer, and it is fine for small teams or non-production stages. For production it is usually the wrong default: a bad upgrade, a broken admission webhook, or a cluster-wide permission mistake hits every environment at once. Most organisations run production in its own cluster (often its own cloud account) and use namespaces to separate **teams or services** inside each cluster.

## Example

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: payments
  labels:
    pod-security.kubernetes.io/enforce: restricted
    team: payments
---
apiVersion: v1
kind: ResourceQuota
metadata: { name: payments-quota, namespace: payments }
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    persistentvolumeclaims: "10"
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny-ingress, namespace: payments }
spec:
  podSelector: {} # every Pod in the namespace
  policyTypes: ["Ingress"] # no ingress rules listed, so all inbound traffic is denied
```

```bash
kubectl get ns
kubectl get pods -n payments
kubectl config set-context --current --namespace=payments   # change the default for this context
kubectl api-resources --namespaced=false                    # what a namespace cannot contain
```

## Interview tips

- The common short answer is "namespaces separate dev, test, and prod." Correct it: they separate names and attach policy, but they do not isolate network, nodes, or the control plane by themselves, and production usually gets its own cluster.
- List what makes a namespace a real tenant boundary: RBAC RoleBindings, ResourceQuota and LimitRange, Pod Security Admission labels, and default-deny NetworkPolicies.
- Know two or three cluster-scoped kinds (Nodes, PersistentVolumes, ClusterRoles) because "is X namespaced?" is a frequent follow-up.
- Be ready for "a namespace is stuck in `Terminating`": that is a finalizer waiting on a resource or an unavailable API service. See [what are Kubernetes finalizers](./what-are-kubernetes-finalizers-and-how-do-you-resolve-a-namespace-stuck-in-the-terminating-state.md) and [how does RBAC work in Kubernetes](./how-does-rbac-work-in-kubernetes.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[Why does a container image that works locally fail on Kubernetes or ECS?]] (`#793`): [Why does a container image that works locally fail on Kubernetes or ECS?](../docker/why-does-a-container-image-that-works-locally-fail-on-kubernetes-or-ecs.md)
- [[How do you troubleshoot a failed Helm release?]] (`#412`): [How do you troubleshoot a failed Helm release?](../container-orchestration-advanced/how-do-you-troubleshoot-a-failed-helm-release.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
