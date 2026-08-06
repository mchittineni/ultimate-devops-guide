---
title: "What is Istio?"
id: 84
category: "Container Orchestration Advanced"
difficulty: "Advanced"
tags:
  - devops
  - container-orchestration-advanced
  - interview-questions
---

# What is Istio?

**Short answer:** Istio is a service mesh for Kubernetes that manages service-to-service traffic through Envoy proxies, providing mutual TLS, fine-grained traffic routing, resilience policies, and uniform telemetry without changing application code.

## Detail

**Architecture.** `istiod` is the control plane — it handles service discovery, configuration distribution, and certificate issuance. The data plane is Envoy, injected as a sidecar into each pod (or, in **ambient mode**, run as a per-node ztunnel plus optional waypoint proxies, removing per-pod sidecars).

**Core APIs**

- **VirtualService** — routing rules: weighted splits, header matching, rewrites, timeouts, retries, fault injection.
- **DestinationRule** — what happens after routing: subsets, load-balancing policy, connection pool limits, outlier detection (ejecting unhealthy endpoints), and TLS settings.
- **Gateway** — ingress and egress at the mesh edge.
- **PeerAuthentication** — enforce strict mTLS.
- **AuthorizationPolicy** — allow/deny rules by source identity, namespace, method, or path.
- **ServiceEntry** / **Sidecar** — external services, and scoping proxy configuration to reduce memory.

**What it buys you:** automatic mTLS with rotating SPIFFE identities, progressive delivery through traffic weighting (the foundation for Argo Rollouts and Flagger), consistent golden-signal metrics for every service, and fault injection for resilience testing.

**What it costs:** meaningful CPU and memory overhead, added latency, a complex control plane to upgrade, and a steep debugging curve — `istioctl analyze` and `proxy-config` become essential tools.

## Example

```yaml
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata: { name: default, namespace: prod }
spec:
  mtls: { mode: STRICT } # all in-mesh traffic must be mTLS
---
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata: { name: payments-access, namespace: prod }
spec:
  selector: { matchLabels: { app: payments } }
  action: ALLOW
  rules:
    - from: [{ source: { principals: ["cluster.local/ns/prod/sa/checkout"] } }]
      to: [{ operation: { methods: ["POST"], paths: ["/charge"] } }]
```

## Interview tips

- Naming the four or five main CRDs and what each controls demonstrates hands-on use.
- Ambient mode is the current answer to the sidecar overhead criticism — worth knowing.
- Compare with Linkerd (simpler, lighter, less featureful) to show you evaluated options.

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
