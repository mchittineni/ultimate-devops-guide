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

**Architecture.** A **data plane** of proxies (usually Envoy) deployed beside each service intercepts all inbound and outbound traffic. A **control plane** (Istio's istiod, Linkerd's controller) configures those proxies from declarative policy.

**What it provides without application changes**

- **Traffic management** - weighted routing for canaries, header-based routing, mirroring, timeouts, retries, and circuit breaking.
- **Security** - automatic mutual TLS between all services with certificate rotation, plus service-level authorisation policies. This is the foundation of zero trust inside the cluster.
- **Observability** - consistent golden-signal metrics, distributed trace propagation, and access logs for every call, regardless of language.
- **Resilience** - fault injection for chaos testing, outlier detection ejecting unhealthy endpoints, and rate limiting.

**Costs.** A proxy per pod adds latency (typically low single-digit milliseconds), memory, and CPU. The control plane is another critical system to operate and upgrade, and mesh configuration introduces genuinely difficult debugging. **Ambient mode** in Istio and the sidecar-free **Cilium mesh** are responses to this overhead.

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
```

## Interview tips

- Explain the sidecar interception model - that is the mechanism the question is really testing.
- Automatic mTLS is the single most compelling reason teams adopt a mesh; say so.
- Be honest about the operational cost and name the situation where you would not use one.

---

[⬅ Back to Cloud Native Architecture](./README.md) · [All topics](../README.md)
