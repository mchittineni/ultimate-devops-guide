---
title: "What is the difference between an API Gateway and a Service Mesh and how do they work together?"
id: 615
category: "API Gateway and Service Mesh"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - api-gateway
  - service-mesh
  - istio
  - envoy
  - networking
quiz:
  stem: "In enterprise cloud architecture, which tool is responsible for managing East-West communication, including zero-trust mutual TLS (mTLS) between microservices?"
  options:
    - "Public DNS Registrar"
    - "Service Mesh (such as Istio or Linkerd)"
    - "Edge CDN (Content Delivery Network)"
    - "Network Address Translation (NAT) Gateway"
  answer: 2
  explanation: "Service Meshes govern East-West (service-to-service) internal traffic within clusters, automatically establishing mutual TLS encryption and enforcing service communication policies."
---

# What is the difference between an API Gateway and a Service Mesh and how do they work together?

**Short answer:** An API gateway sits at the edge and handles **north-south** traffic - external clients calling your APIs - with client-facing concerns: authentication of end users and API keys, rate limits and quotas, request transformation, versioning, and developer-portal features. A service mesh handles **east-west** traffic between your own services, adding workload identity and mTLS, retries, timeouts, traffic shifting, and uniform telemetry without code changes. They are complementary: the gateway is the front door, and the mesh governs everything behind it. The overlap - both are often Envoy, both can route and retry - is converging through the Kubernetes Gateway API, which configures both.

## Detail

```text
External clients / partners / mobile apps
        │   north-south: untrusted callers, public API contract
        ▼
  [ API gateway ]  OAuth2/OIDC & API keys · quotas per consumer · WAF · transformation
        │          terminates public TLS, re-originates mTLS into the mesh
════════╪═══════════════════════════════════════════════════════════════
        ▼   east-west: workload-to-workload inside the platform
  [ orders ] ──mTLS──> [ payments ] ──mTLS──> [ ledger ]
       identity, authorisation by service account, retries, timeouts, telemetry
```

| Dimension           | API gateway (north-south)                                          | Service mesh (east-west)                                     |
| ------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------ |
| Callers             | External, untrusted; identified as users, apps, or API keys        | Internal workloads; identified by workload identity (SPIFFE) |
| Core concerns       | AuthN/Z for consumers, quotas, monetisation, API lifecycle         | mTLS, service-level authorisation, resilience, observability |
| Deployment          | A central, horizontally scaled tier at the edge                    | Sidecars in each Pod, or node-level proxies (ambient/eBPF)   |
| Configuration owner | API/product and platform teams                                     | Platform team, with service teams owning their routes        |
| Examples            | Kong, Apigee, AWS API Gateway, Azure API Management, Envoy Gateway | Istio, Linkerd, Cilium service mesh, Consul                  |

**How they fit together in practice**

- The gateway validates the external token, applies the consumer's quota, and forwards a verified identity downstream (a signed header or an internal token); the mesh then enforces **which services** may call which.
- In a mesh, the ingress gateway is itself a mesh workload with its own identity, so authorisation policies must explicitly allow it.
- Either layer can do retries - make sure they do not both, or retries multiply.

**Convergence.** The Kubernetes Gateway API models north-south routing (`Gateway` + `HTTPRoute`), and its **GAMMA** initiative applies the same `HTTPRoute` to east-west mesh traffic by attaching routes to a `Service`. Many teams therefore run one Envoy-based stack for both, while keeping a full API-management product at the edge only when they need consumer onboarding, monetisation, or a developer portal.

**When you need only one:** a small estate with one language may need only a gateway plus a resilience library; a purely internal platform with no public APIs may need only a mesh and an ingress.

## Example

```yaml
# North-south: public Gateway and route (Gateway API)
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata: { name: orders-public, namespace: shop }
spec:
  parentRefs: [{ name: public-gateway, namespace: infra }]
  hostnames: ["api.example.com"]
  rules:
    - matches: [{ path: { type: PathPrefix, value: /v1/orders } }]
      backendRefs: [{ name: orders, port: 80 }]
---
# East-west (GAMMA): the same API attached to a Service governs mesh traffic to it
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata: { name: payments-internal, namespace: shop }
spec:
  parentRefs: [{ group: "", kind: Service, name: payments, port: 80 }]
  rules:
    - backendRefs:
        - { name: payments-v1, port: 80, weight: 90 }
        - { name: payments-v2, port: 80, weight: 10 }
      timeouts: { request: 3s }
```

## Interview tips

- Anchor on north-south versus east-west, then on who the caller is: an external consumer versus an internal workload identity.
- Explain how identity is handed over - the gateway authenticates the user, the mesh authorises service-to-service calls.
- Warn about duplicated retries and timeouts across the two layers.
- Mention Gateway API and GAMMA as the convergence point, and say when one of the two is enough.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do Docker bridge, host, and macvlan network drivers differ in packet routing and isolation?]] (`#517`): [How do Docker bridge, host, and macvlan network drivers differ in packet routing and isolation?](../docker/how-do-docker-bridge-host-and-macvlan-network-drivers-differ-in-packet-routing-and-isolation.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to API Gateway and Service Mesh](./README.md) · [All topics](../README.md)
