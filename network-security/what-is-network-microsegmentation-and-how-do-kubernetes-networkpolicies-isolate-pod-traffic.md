---
title: "What is Network Microsegmentation and how do Kubernetes NetworkPolicies isolate pod traffic?"
id: 668
category: "Network Security"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - network-security
  - kubernetes
  - networkpolicy
  - microsegmentation
quiz:
  stem: "Why does applying a Kubernetes NetworkPolicy have zero effect if the cluster is using basic Flannel as its CNI plugin?"
  options:
    - "NetworkPolicies only work on bare-metal servers"
    - "Flannel only handles packet routing and lacks an internal policy enforcement engine (like iptables or eBPF) to drop unauthorized packets"
    - "NetworkPolicies must be compiled into Go binaries"
    - "Flannel automatically deletes NetworkPolicy resources"
  answer: 2
  explanation: "Flannel provides overlay networking only and does not implement the Kubernetes NetworkPolicy specification. Enforcing policies requires a security-capable CNI like Calico or Cilium."
---

# What is Network Microsegmentation and how do Kubernetes NetworkPolicies isolate pod traffic?

**Short answer:** Microsegmentation divides network environments into granular security zones down to individual workloads; Kubernetes NetworkPolicies implement this at L3/L4 using pod labels, enforcing a default-deny posture and explicitly allowing permitted ingress and egress traffic.

## Detail

By default in Kubernetes, the network is flat: **any Pod can communicate with any other Pod across any namespace!** If an attacker compromises a frontend PHP container, they can query internal Redis caches, payment databases, or the control plane API.

### Default-Deny Architecture

Mature security starts by isolating the namespace completely:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {} # Selects all pods in namespace
  policyTypes:
    - Ingress
    - Egress
```

Once default-deny is applied, all incoming and outgoing connections are dropped - including DNS, so the first allow rule you add is usually egress to CoreDNS on port 53. NetworkPolicies are additive allow-lists: there is no deny rule, and a Pod is isolated in a direction only once some policy selects it for that direction.

### Explicit Allow Rule

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-backend-from-frontend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8080
```

This guarantees that only pods labeled `app: frontend` can establish TCP connections on port 8080. All other traffic is silently dropped by the CNI (Calico, Cilium).

## Example

```bash
# Verify the policy is actually enforced (the CNI must support NetworkPolicy)
kubectl -n production run probe --rm -it --image=busybox:1.37 --labels=app=frontend \
  -- wget -qO- -T 2 http://backend:8080/healthz          # allowed
kubectl -n production run probe --rm -it --image=busybox:1.37 --labels=app=other \
  -- wget -qO- -T 2 http://backend:8080/healthz          # times out: blocked

kubectl -n production get networkpolicy
```

## Interview tips

- State the default precisely: without any policy, every Pod can reach every Pod in every namespace; a Pod becomes isolated only in the direction(s) a policy selects it for.
- Remember policies are additive allow-lists - there is no deny rule and no ordering in the core API. Cluster-wide guardrails and explicit denies come from CNI CRDs (Calico `GlobalNetworkPolicy`, `CiliumClusterwideNetworkPolicy`) or the upstream AdminNetworkPolicy work, which is not GA.
- Default-deny breaks DNS: add an egress rule to CoreDNS on port 53 (UDP and TCP) immediately.
- Enforcement needs a policy-capable CNI (Cilium, Calico, Antrea, or the managed options on EKS/AKS/GKE); plain Flannel silently ignores NetworkPolicy objects.
- Name the limitation: core NetworkPolicy is L3/L4 and IP/label based. For L7 rules (HTTP methods, paths) or identity-based mTLS authorisation, use Cilium L7 policies or a service mesh `AuthorizationPolicy`.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[What are ephemeral preview environments and how do you manage their lifecycle and cleanup?]] (`#535`): [What are ephemeral preview environments and how do you manage their lifecycle and cleanup?](../cicd/what-are-ephemeral-preview-environments-and-how-do-you-manage-their-lifecycle-and-cleanup.md)
- [[How do you troubleshoot Docker networking between containers?]] (`#415`): [How do you troubleshoot Docker networking between containers?](../docker/how-do-you-troubleshoot-docker-networking-between-containers.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Network Security](./README.md) · [All topics](../README.md)
