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

**Architecture.** `istiod` is the control plane - it handles service discovery, configuration distribution, and certificate issuance. The data plane is Envoy, injected as a sidecar into each pod - or, in **ambient mode** (GA since Istio 1.24), a per-node `ztunnel` that handles mTLS and L4 policy for every Pod on the node, plus optional per-namespace or per-service **waypoint** proxies (Envoy) only where L7 features are needed. Ambient removes per-pod sidecars, so Pods no longer need restarting to join or upgrade the mesh.

**Sidecar versus ambient.** Sidecars give every Pod full L7 features and isolate failures per Pod, at the cost of CPU and memory in every replica and a proxy upgrade that means a rolling restart of the fleet. Ambient is far cheaper for the common "mTLS plus L4 policy" case, but L7 routing and policy require deploying waypoints, and the shared node proxy is a different failure and multi-tenancy model.

**Core APIs**

- **VirtualService** - routing rules: weighted splits, header matching, rewrites, timeouts, retries, fault injection.
- **DestinationRule** - what happens after routing: subsets, load-balancing policy, connection pool limits, outlier detection (ejecting unhealthy endpoints), and TLS settings.
- **Gateway** - ingress and egress at the mesh edge. Istio also implements the Kubernetes **Gateway API** (`Gateway`, `HTTPRoute`), which Istio positions as its future default for traffic management and uses to deploy ambient waypoints; the Istio `VirtualService`/`Gateway` APIs remain supported.
- **PeerAuthentication** - enforce strict mTLS.
- **AuthorizationPolicy** - allow/deny rules by source identity, namespace, method, or path.
- **ServiceEntry** / **Sidecar** - external services, and scoping proxy configuration to reduce memory.

**What it buys you:** automatic mTLS with rotating SPIFFE identities, progressive delivery through traffic weighting (the foundation for Argo Rollouts and Flagger), consistent golden-signal metrics for every service, and fault injection for resilience testing.

**What it costs:** meaningful CPU and memory overhead, added latency, a complex control plane to upgrade, and a steep debugging curve - `istioctl analyze` and `proxy-config` become essential tools.

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
- Ambient mode is the current answer to the sidecar overhead criticism - worth knowing.
- Compare with Linkerd (simpler, lighter, less featureful; stable open-source releases now come via Buoyant, with the project itself shipping edge releases) and Cilium's mesh to show you evaluated options.
- Know the trade-off in one line: a mesh buys identity, mTLS, and uniform telemetry at the price of latency, resource overhead, and a critical control plane you must upgrade carefully.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
