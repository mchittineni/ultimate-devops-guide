---
title: "How does the Kubernetes Gateway API evolve beyond standard Ingress resources?"
id: 520
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - kubernetes
  - networking
  - gateway-api
  - ingress
quiz:
  stem: "Which structural limitation of standard Kubernetes Ingress did the Gateway API solve through its role-oriented design?"
  options:
    - "Ingress resources were incapable of routing TCP traffic to pods"
    - "Ingress forced cluster infrastructure configuration, TLS management, and application routing into a single un-delegated resource"
    - "Ingress did not support DNS domain names"
    - "Ingress controllers could only run as DaemonSets"
  answer: 2
  explanation: "Standard Ingress conflated cluster admin responsibilities (TLS certs, IP bindings) with app team routing, forcing widespread reliance on incompatible controller annotations."
---

# How does the Kubernetes Gateway API evolve beyond standard Ingress resources?

**Short answer:** Gateway API replaces the single, annotation-heavy `Ingress` object with a family of typed, role-oriented resources: a **GatewayClass** (the implementation, owned by the infrastructure provider), a **Gateway** (listeners, ports, and TLS, owned by the cluster operator), and **Routes** such as `HTTPRoute`, `GRPCRoute`, `TLSRoute`, `TCPRoute`, and `UDPRoute` (owned by application teams in their own namespaces). Features that Ingress could only express through controller-specific annotations - header matching, weighted traffic splitting, redirects, rewrites, timeouts, cross-namespace delegation - are part of the portable spec. Ingress is feature-frozen; Gateway API is where new routing features land.

## Detail

**What was wrong with Ingress.** One `Ingress` object mixes infrastructure concerns (which load balancer, which certificate) with application routing (which path goes to which Service), so it cannot be safely delegated. Its spec only covers host and path routing, so everything else became annotations - `nginx.ingress.kubernetes.io/rewrite-target`, `traefik.ingress.kubernetes.io/router.middlewares` - which are unvalidated, differ per controller, and lock you to one implementation. The retirement of the community Ingress-NGINX controller in March 2026 made that lock-in concrete for many teams.

**The role-oriented model.**

```text
Infrastructure provider  -->  GatewayClass  (e.g. Envoy Gateway, Istio, Cilium, cloud LB controllers)
Cluster operator         -->  Gateway       (listeners on :443, TLS certificates, which namespaces may attach)
Application developer    -->  HTTPRoute     (match /api, filter headers, split traffic across Services)
```

A Route attaches to a Gateway through `parentRefs`, and the Gateway's `allowedRoutes` decides whether that attachment is accepted. Referencing something in another namespace - a Service backend, a certificate Secret - requires a `ReferenceGrant` in the target namespace, so cross-namespace access is explicit consent, not an accident.

**Capabilities in the portable spec.**

- **Rich matching**: path, headers, query parameters, and method.
- **Weighted backends**: canary and blue/green splits (`weight: 90` / `weight: 10`) without a mesh or vendor annotations.
- **Filters**: request and response header modification, redirects, URL rewrites, request mirroring, and CORS.
- **Timeouts and retries** on HTTPRoute rules.
- **Backend TLS** via `BackendTLSPolicy`, for re-encrypting to the upstream.
- **More protocols**: `GRPCRoute`, `TLSRoute` (SNI passthrough), and `TCPRoute`/`UDPRoute` for L4 traffic.
- **Service mesh (GAMMA)**: the same Route types can attach to a `Service` instead of a Gateway to configure east-west mesh traffic.

**Release channels.** Gateway API ships as CRDs, not in-tree, with a **standard** channel (stable, `v1`) and an **experimental** channel. `Gateway`, `GatewayClass`, and `HTTPRoute` went GA in v1.0 (2023), `GRPCRoute` in v1.1, `BackendTLSPolicy` in v1.4, `TLSRoute`, `ListenerSet`, and `ReferenceGrant` in v1.5, and `TCPRoute`/`UDPRoute` in v1.6 (2026). New experimental resources now live in a separate `gateway.networking.x-k8s.io` group, so you cannot adopt an experimental API by accident.

**Trade-offs and limitations.**

- **Conformance varies.** Each implementation declares which features it supports; "Extended" features such as mirroring or some filters may be missing. Check the conformance report before choosing.
- **More objects.** A simple single-host site needs a GatewayClass, Gateway, and HTTPRoute where Ingress needed one object.
- **CRD lifecycle.** The CRDs are installed and upgraded separately from Kubernetes, and several tools may try to own them - managed platforms often pre-install a version, so align with it.
- **Migration.** `ingress2gateway` translates Ingress objects (and common controller annotations) into Gateway API resources, but controller-specific behaviour, such as NGINX regex paths, needs manual review.

## Example

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: public
  namespace: infra
spec:
  gatewayClassName: envoy-gateway
  listeners:
    - name: https
      protocol: HTTPS
      port: 443
      hostname: "*.example.com"
      tls:
        mode: Terminate
        certificateRefs: [{ name: wildcard-example-com }]
      allowedRoutes:
        namespaces:
          from: Selector
          selector: { matchLabels: { gateway-access: "true" } }
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: checkout
  namespace: shop # the app team's namespace
spec:
  parentRefs: [{ name: public, namespace: infra }]
  hostnames: ["shop.example.com"]
  rules:
    - matches:
        - path: { type: PathPrefix, value: /api }
          headers: [{ name: x-beta-user, value: "true" }]
      backendRefs: [{ name: checkout-canary, port: 8080 }]
    - matches: [{ path: { type: PathPrefix, value: /api } }]
      timeouts: { request: 10s }
      backendRefs:
        - { name: checkout-stable, port: 8080, weight: 90 }
        - { name: checkout-canary, port: 8080, weight: 10 }
```

```bash
kubectl get gatewayclass,gateway -A
kubectl describe httproute checkout -n shop   # status.parents shows Accepted / ResolvedRefs per Gateway
```

## Interview tips

- Lead with the role split - GatewayClass, Gateway, Route - and why it matters: the platform team owns listeners and certificates, app teams own their routes without cluster-wide write access.
- Name the annotation problem with Ingress and show the portable replacement: weighted `backendRefs`, header matches, timeouts, filters.
- Mention `ReferenceGrant` for cross-namespace references and `allowedRoutes` for attachment control - interviewers use these to check you understand the multi-tenant design.
- Know the maturity picture: core resources GA since v1.0, more promoted each release, and conformance varies by implementation.
- Bring up the Ingress-NGINX retirement and `ingress2gateway` as the practical reason teams are migrating now.
- When debugging, read the Route's `status.parents` conditions (`Accepted`, `ResolvedRefs`) before anything else - they say why a route is not attached.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do Docker bridge, host, and macvlan network drivers differ in packet routing and isolation?]] (`#517`): [How do Docker bridge, host, and macvlan network drivers differ in packet routing and isolation?](../docker/how-do-docker-bridge-host-and-macvlan-network-drivers-differ-in-packet-routing-and-isolation.md)
- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
