---
title: "What is Service Mesh?"
id: 68
category: "Cloud Native Architecture"
difficulty: "Advanced"
tags:
  - devops
  - cloud-native-architecture
  - interview-questions
---

# What is Service Mesh?

**Short answer:** A service mesh is a dedicated infrastructure layer that handles service-to-service communication - traffic management, mutual TLS, retries, and telemetry - by intercepting traffic in sidecar proxies, so applications do not implement these concerns themselves.

## Detail

**Architecture.** A **data plane** of proxies intercepts all inbound and outbound traffic - classically a sidecar in every Pod (Envoy for Istio, the Rust-based `linkerd2-proxy` for Linkerd), with iptables or a CNI plugin redirecting the Pod's traffic through it. A **control plane** (Istio's istiod, Linkerd's control plane) configures those proxies from declarative policy and acts as the certificate authority that issues each workload a short-lived identity certificate (SPIFFE IDs in Istio).

**Sidecar-less data planes are now mainstream.** Istio's **ambient mode** (GA since Istio 1.24, late 2024) splits the job in two: a per-node `ztunnel` handles mTLS and L4 policy for every Pod on the node, and optional per-namespace **waypoint** proxies are deployed only where L7 features (HTTP routing, retries, header-based authorisation) are needed. Cilium's mesh uses eBPF in the kernel plus a per-node Envoy. The trade-off is a shared, node-level component (bigger blast radius per node, noisier-neighbour concerns) in exchange for far less per-Pod CPU and memory and no sidecar injection or restart on mesh upgrades. Configuration is also converging on the Kubernetes **Gateway API** (`HTTPRoute` attached to a Service, the GAMMA initiative) rather than mesh-specific CRDs.

**What it provides without application changes**

- **Traffic management** - weighted routing for canaries, header-based routing, mirroring, timeouts, retries, and circuit breaking.
- **Security** - automatic mutual TLS between all services with certificate rotation, plus service-level authorisation policies. This is the foundation of zero trust inside the cluster.
- **Observability** - consistent golden-signal metrics, distributed trace propagation, and access logs for every call, regardless of language.
- **Resilience** - fault injection for chaos testing, outlier detection ejecting unhealthy endpoints, and rate limiting.

**Costs.** A proxy per pod adds latency (typically low single-digit milliseconds), memory, and CPU. The control plane is another critical system to operate and upgrade, and mesh configuration introduces genuinely difficult debugging. Retries configured in the mesh _and_ in application code multiply each other - a common cause of retry storms.

**When it is worth it:** many services, multiple languages (so a shared library is impractical), and a real requirement for mTLS everywhere or fine-grained traffic control. For five services in one language, a library plus an ingress controller is usually the better engineering decision.

## Example

```yaml
apiVersion: networking.istio.io/v1
kind: VirtualService
metadata: { name: reviews }
spec:
  hosts: [reviews]
  http:
    - route:
        - destination: { host: reviews, subset: v1 }
          weight: 90
        - destination: { host: reviews, subset: v2 }
          weight: 10 # canary
      retries: { attempts: 3, perTryTimeout: 2s }
      timeout: 10s
---
# Subsets referenced above must be defined, or the route fails.
apiVersion: networking.istio.io/v1
kind: DestinationRule
metadata: { name: reviews }
spec:
  host: reviews
  subsets:
    - { name: v1, labels: { version: v1 } }
    - { name: v2, labels: { version: v2 } }
```

## Interview tips

- Explain the sidecar interception model - that is the mechanism the question is really testing.
- Automatic mTLS is the single most compelling reason teams adopt a mesh; say so.
- Be honest about the operational cost and name the situation where you would not use one.
- Know the sidecar-less options (Istio ambient with ztunnel and waypoints, Cilium) and the trade-off they make.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Native Architecture](./README.md) · [All topics](../README.md)
