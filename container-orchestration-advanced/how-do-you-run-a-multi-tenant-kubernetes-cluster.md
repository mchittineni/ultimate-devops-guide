---
title: "How do you run a multi-tenant Kubernetes cluster?"
id: 453
category: "Container Orchestration Advanced"
difficulty: "Advanced"
tags:
  - devops
  - container-orchestration-advanced
  - interview-questions
  - platform-engineering
  - network-security
  - kubernetes
---

# How do you run a multi-tenant Kubernetes cluster?

**Short answer:** Decide first **what kind of tenant** you have, because that decides how hard the boundary must be. Teams inside one company (soft multi-tenancy) can share a cluster with namespace-per-team isolation; untrusted or externally-facing tenants (hard multi-tenancy) should get separate clusters or virtual control planes, because a shared kernel and a shared control plane are not a security boundary you can fully close. For soft multi-tenancy the controls compose in five layers: **namespaces** as the unit of ownership, **RBAC** scoped with Roles rather than ClusterRoles, **ResourceQuota plus LimitRange** so no team can starve another for CPU, memory, or storage, **NetworkPolicy** default-deny so traffic is opt-in, and **admission policy** (Pod Security Admission plus Kyverno/Gatekeeper) so tenants cannot escape their box with `hostNetwork`, `privileged`, or a hostPath mount. Then add the operational layer everyone forgets: per-tenant priority classes, node pools for noisy or sensitive workloads, per-tenant observability and cost attribution, and a **shared upgrade calendar** - because in one cluster the control-plane version is a shared fate.

## Detail

### Soft versus hard, stated up front

|                | Soft multi-tenancy                        | Hard multi-tenancy                                         |
| -------------- | ----------------------------------------- | ---------------------------------------------------------- |
| Tenants        | Teams in one organisation, trusted-ish    | Customers, untrusted code, regulated separation            |
| Boundary       | Namespace + policy                        | Cluster, or virtual cluster / virtual control plane        |
| Threat model   | Accidental interference, noisy neighbours | Deliberate escape attempts                                 |
| Kernel sharing | Accepted                                  | Needs gVisor/Kata or dedicated nodes                       |
| Control plane  | Shared                                    | Per-tenant (vcluster, Capsule-style, or separate clusters) |

Saying "if these are real customers running arbitrary containers, I would not put them in one cluster's namespaces" is a strength, not a dodge. Kubernetes documentation itself is explicit that a namespace is not a security boundary against a determined attacker.

### The five layers for shared clusters

**1. Namespace as the unit of ownership.** One namespace per team-environment (`team-a-prod`), created by automation with the whole policy bundle attached - quota, limit range, default-deny NetworkPolicy, RBAC bindings, and labels for cost allocation. A tenant that can create its own namespaces bypasses all of it, so namespace creation belongs to the platform (or to a controller such as Hierarchical Namespace Controller / Capsule, which model tenant → namespaces properly).

**2. RBAC scoped tightly.** Bind `Role`s in the tenant's namespaces, never `ClusterRole` bindings at cluster scope. Deny the escape hatches: `get secrets` beyond their own namespace, `escalate`/`bind` verbs, `impersonate`, and access to cluster-scoped objects (nodes, PVs, CRDs, webhooks). Disable `automountServiceAccountToken` where unused, and remember that permission to create a Pod is effectively permission to use any ServiceAccount in that namespace - so a tenant with a privileged SA in their namespace has that privilege.

**3. Quotas: the answer to noisy neighbours.** `ResourceQuota` caps namespace totals for `requests.cpu`, `limits.memory`, object counts, PVC counts, and **per-storage-class storage** (which is exactly how you guarantee no team consumes more than its share of storage). `LimitRange` supplies defaults so BestEffort Pods cannot exist and no single container can request the whole node. Deploy the pair together, because a quota on a compute resource makes that resource mandatory on every Pod.

**4. NetworkPolicy default-deny.** Without policy, every Pod can reach every other Pod in the cluster - which is usually the biggest real gap in a "multi-tenant" cluster. Apply a default-deny ingress and egress policy per namespace, then allow: intra-namespace traffic, DNS to CoreDNS (the rule everyone forgets), the specific cross-tenant services that are meant to be shared, and egress to the internet only where required. For tenant-to-tenant rules use `namespaceSelector` on labels the platform controls, not labels tenants can edit.

**5. Admission policy.** Pod Security Admission at `restricted` per namespace stops the obvious escapes (privileged, hostPID/hostNetwork, hostPath, running as root). Layer Kyverno or Gatekeeper for the rest: allowed registries only, required labels for cost allocation, no `LoadBalancer` Services if tenants must not create public endpoints, mandatory `topologySpreadConstraints`, no `NodePort`, image-signature verification. Roll new policies in audit mode first.

### The parts people forget

- **Scheduling and node isolation.** Taints plus tolerations and node selectors give a tenant dedicated node pools - necessary for compliance separation, for GPU or licensed workloads, and for keeping a batch tenant off the nodes serving latency-sensitive traffic. `topologySpreadConstraints` stops one tenant filling one zone.
- **Priority and preemption.** Per-tenant `PriorityClass` values decide who gets capacity when the cluster is full. Without them, "first to submit" wins, which is not a policy.
- **Control-plane fairness.** One tenant's chatty controller can exhaust API server capacity for everyone. API Priority and Fairness (APF) flow schemas per tenant are the mitigation, and it is a genuinely differentiating thing to mention.
- **DNS and CoreDNS load.** A misconfigured tenant with `ndots` amplification can degrade cluster DNS for everybody; NodeLocal DNSCache and CoreDNS autoscaling protect the shared service.
- **Upgrade cycles are shared.** This is usually the deciding argument for separate clusters: in one cluster, everyone gets the control-plane version and the CRD versions at the same time. If a tenant needs a different cadence, they need their own cluster or a virtual one. Publish a maintenance calendar, require PodDisruptionBudgets, and drain on a schedule tenants can plan around.
- **Observability and cost per tenant.** Enforce namespace and team labels at admission, then attribute CPU, memory, storage, and egress with OpenCost/Kubecost. Give each tenant scoped dashboards and their own alert routing - multi-tenancy without per-tenant visibility becomes a support burden on the platform team.

### Virtual clusters, the middle ground

`vcluster` (and similar) run a **separate API server and controller-manager per tenant** inside a host namespace, syncing Pods down to the host cluster. Tenants get cluster-scoped freedom - their own CRDs, their own RBAC, their own apparent cluster version - while the platform keeps one set of nodes. That answers "teams cannot affect each other's resource usage, network traffic, **or upgrade cycles**", which plain namespaces cannot do because CRDs and control-plane versions are cluster-wide. The trade-off is another control plane per tenant to run and monitor.

For genuinely hostile workloads, go further: a sandboxed runtime (gVisor, Kata Containers) so a kernel exploit does not cross tenants, or simply separate clusters and accept the cost.

## Example

```yaml
# The tenant bundle - created by automation, never by the tenant
apiVersion: v1
kind: Namespace
metadata:
  name: team-a-prod
  labels:
    tenant: team-a
    cost-centre: "cc-4417"
    pod-security.kubernetes.io/enforce: restricted # PSA: no privileged, no hostPath
    pod-security.kubernetes.io/warn: restricted
---
apiVersion: v1
kind: ResourceQuota
metadata: { name: quota, namespace: team-a-prod }
spec:
  hard:
    requests.cpu: "40"
    requests.memory: 80Gi
    limits.memory: 120Gi
    pods: "200"
    persistentvolumeclaims: "20"
    gp3-retain.storageclass.storage.k8s.io/requests.storage: 2Ti # storage fairness
    services.loadbalancers: "2" # cap public endpoints
---
apiVersion: v1
kind: LimitRange
metadata: { name: defaults, namespace: team-a-prod }
spec:
  limits:
    - type: Container
      default: { cpu: 500m, memory: 512Mi }
      defaultRequest: { cpu: 100m, memory: 128Mi }
      max: { cpu: "8", memory: 16Gi }
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny, namespace: team-a-prod }
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
  egress: # DNS only, by default; everything else is opt-in
    - to:
        - namespaceSelector:
            matchLabels: { kubernetes.io/metadata.name: kube-system }
      ports: [{ port: 53, protocol: UDP }, { port: 53, protocol: TCP }]
```

```yaml
# RBAC: namespaced Role, no cluster-scoped anything
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata: { name: team-a-devs, namespace: team-a-prod }
subjects: [{ kind: Group, name: "team-a", apiGroup: rbac.authorization.k8s.io }]
roleRef: { kind: ClusterRole, name: edit, apiGroup: rbac.authorization.k8s.io } # bound namespaced
---
# Guardrail the built-in roles do not cover
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: tenant-guardrails }
spec:
  validationFailureAction: Audit # flip to Enforce after reviewing the audit report
  rules:
    - name: images-from-approved-registries
      match: { any: [{ resources: { kinds: [Pod] } }] }
      validate:
        message: "Images must come from registry.example.com"
        pattern: { spec: { containers: [{ image: "registry.example.com/*" }] } }
    - name: require-tenant-labels
      match: { any: [{ resources: { kinds: [Pod, Service, PersistentVolumeClaim] } }] }
      validate:
        message: "tenant and cost-centre labels are required for cost attribution"
        pattern: { metadata: { labels: { tenant: "?*", cost-centre: "?*" } } }
```

```bash
# Verify the boundary rather than assuming it
kubectl auth can-i --list --as system:serviceaccount:team-a-prod:default -n team-b-prod
kubectl auth can-i get nodes --as system:serviceaccount:team-a-prod:default   # expect: no
kubectl describe quota -n team-a-prod                     # used vs hard, per resource
kubectl get networkpolicy -A                              # is every tenant namespace default-deny?

# Prove cross-tenant traffic is actually blocked
kubectl run probe -n team-a-prod --rm -it --image=nicolaka/netshoot -- \
  curl -m 3 http://api.team-b-prod.svc.cluster.local:8080   # expect a timeout

# Who is actually consuming the shared cluster?
kubectl get pods -A -o json | jq -r '.items[] | [.metadata.labels.tenant,
  (.spec.containers[].resources.requests.cpu // "0")] | @tsv' | sort | uniq -c
```

## Interview tips

- Open by asking (or stating) what kind of tenant this is. "Teams in one company or untrusted customers?" changes the whole answer, and saying that a namespace is not a security boundary against a determined attacker is a mark of seriousness, not evasion.
- Structure the soft-tenancy answer in the five layers - namespace, RBAC, quota/limits, NetworkPolicy, admission - and note that they are complementary: quotas stop noisy neighbours, policy stops escapes, and neither substitutes for the other.
- Answer the storage-fairness question precisely: `ResourceQuota` with a per-storage-class `requests.storage` cap, plus `persistentvolumeclaims` count. Interviewers ask this exact scenario.
- Volunteer the DNS egress rule in default-deny policies - omitting it is the most common self-inflicted outage when teams first enforce network policy.
- Mention the operational layer: priority classes for capacity contention, dedicated node pools via taints, API Priority and Fairness so one tenant cannot exhaust the API server, and per-tenant cost attribution enforced by required labels.
- Name upgrade cadence as the honest limit of namespace-based tenancy - control-plane and CRD versions are cluster-wide - and offer virtual clusters (vcluster) as the middle ground and separate clusters or sandboxed runtimes for hostile workloads.
- Say you roll new admission policies in audit mode first. Enforcing a policy across a live estate without an audit pass is a self-inflicted outage. See [how does RBAC work in Kubernetes](../kubernetes/how-does-rbac-work-in-kubernetes.md), [requests, limits, and QoS classes](../kubernetes/how-do-requests-limits-and-qos-classes-work-in-kubernetes.md), [NetworkPolicies](../kubernetes/how-do-kubernetes-networkpolicies-work-and-how-do-you-debug-one-that-blocks-traffic.md), [admission control with Kyverno or OPA Gatekeeper](../devsecops/how-do-you-enforce-kubernetes-admission-control-with-kyverno-or-opa-gatekeeper.md), and [self-service environments for developers](../platform-engineering/how-do-you-provide-self-service-environments-to-developers.md).

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
