---
title: "What are Ambient Mesh and Sidecarless service mesh architectures and why were they developed?"
id: 618
category: "API Gateway and Service Mesh"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - service-mesh
  - ambient-mesh
  - istio
  - ebpf
  - cilium
quiz:
  stem: "Which operational challenge of traditional sidecar service meshes did Istio Ambient Mesh solve by introducing node-level ztunnels?"
  options:
    - "It eliminated the need for Linux operating systems"
    - "It eliminated the requirement to inject sidecar containers and restart every application Pod to enable mTLS"
    - "It forced all microservices to use gRPC exclusively"
    - "It banned the use of network encryption"
  answer: 2
  explanation: "Ambient mesh uses node-level proxies, allowing clusters to enable zero-trust mTLS encryption without injecting sidecar containers or restarting application workloads."
---

# What are Ambient Mesh and Sidecarless service mesh architectures and why were they developed?

**Short answer:** A sidecarless mesh moves the proxy out of every Pod. Istio's **ambient mode** (generally available since Istio 1.24) splits the data plane into a per-node **ztunnel** that provides mTLS, workload identity, and L4 authorisation for every enrolled Pod, and optional **waypoint** proxies (Envoy) deployed per namespace or per service only where L7 features are needed. Cilium takes a similar approach with eBPF in the kernel plus a per-node Envoy for L7. The motivation was the sidecar tax - memory and CPU per Pod, Pod restarts to join or upgrade the mesh, and lifecycle races - at the cost of a shared, node-level component whose failure or compromise affects every Pod on that node.

## Detail

**What was wrong with sidecars**

- **Resource cost** - one Envoy per Pod, each holding configuration for the services it can reach; across thousands of Pods that is a large, mostly idle memory footprint.
- **Invasive lifecycle** - injection happens at Pod creation, so joining the mesh or upgrading the proxy means restarting every workload.
- **Ordering problems** - apps starting before their proxy, and Jobs that never completed because the sidecar kept running. Kubernetes native sidecars (init containers with `restartPolicy: Always`) fixed these, but not the cost.
- **L7 everywhere** - every hop paid for full HTTP processing even when only mTLS was wanted.

**How ambient works**

1. The **istio-cni** node agent redirects traffic for Pods in namespaces labelled `istio.io/dataplane-mode=ambient` into the node's ztunnel - no Pod restart, no injected container.
2. **ztunnel** (a Rust L4 proxy, one per node) holds the SPIFFE identities of the Pods on its node, and carries traffic between nodes over **HBONE** - mTLS-encrypted HTTP CONNECT tunnels on port 15008. It enforces L4 `AuthorizationPolicy` (source identity, port) and emits TCP telemetry.
3. A **waypoint** is an Envoy deployment created with a Gateway API `Gateway` of class `istio-waypoint`. Labelling a namespace or service with `istio.io/use-waypoint` routes its inbound traffic through it for HTTP routing, retries, fault injection, L7 authorisation, and request metrics.

**Cilium's variant.** Cilium enforces identity-based L3/L4 policy in eBPF and sends L7 traffic to a per-node Envoy; its mutual authentication and encryption options (WireGuard or IPsec for transport, SPIFFE-based mutual auth) differ from Istio's per-connection mTLS model, so compare the security properties rather than assuming they are equivalent.

**Trade-offs to state**

- **Shared failure and trust domain** - ztunnel is a node-level component holding keys for every Pod on the node; compromise or a crash affects them all, whereas a sidecar confines both to one Pod.
- **An extra hop for L7** - traffic to a waypoint may cross nodes, so L7 latency can be higher than with a co-located sidecar.
- **Feature parity and maturity** - multicluster, some Envoy extensions, and VM workloads have lagged behind sidecar mode; check the release notes for your version.
- **Mixed estates** - sidecar and ambient workloads interoperate, which allows gradual migration but adds a second data-plane model to understand.

## Example

```bash
# Enrol a namespace in ambient mode - existing Pods are captured without restarts
kubectl label namespace payments istio.io/dataplane-mode=ambient

# Add L7 only where it is needed: create a waypoint and point the namespace at it
istioctl waypoint apply -n payments --enroll-namespace
kubectl get gateway -n payments      # waypoint, gatewayClassName: istio-waypoint

# Verify: which workloads ztunnel manages, and via which waypoint
istioctl ztunnel-config workloads | grep payments
```

```yaml
# L4 policy enforced by ztunnel (no L7 fields, so no waypoint required)
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata: { name: allow-checkout, namespace: payments }
spec:
  action: ALLOW
  rules:
    - from:
        - source: { principals: ["cluster.local/ns/checkout/sa/checkout"] }
      to:
        - operation: { ports: ["8443"] }
```

## Interview tips

- Lead with the problem - sidecar memory, restarts to join or upgrade, lifecycle races - then the split between L4 (ztunnel) and L7 (waypoint).
- Say that L4 mTLS and identity come for every Pod at node cost, and L7 is paid for only where a waypoint is deployed.
- Give the honest trade-off: a node-level shared component widens the blast radius and trust boundary compared with per-Pod sidecars.
- Note that ambient is GA in Istio and that Cilium's eBPF model is related but not identical in its security guarantees.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to API Gateway and Service Mesh](./README.md) · [All topics](../README.md)
