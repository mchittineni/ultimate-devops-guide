---
title: "How do you debug a service mesh that is breaking service-to-service traffic?"
id: 427
category: "API Gateway and Service Mesh"
difficulty: "Advanced"
tags:
  - devops
  - api-gateway-and-service-mesh
  - interview-questions
  - kubernetes
  - network-security
  - container-orchestration-advanced
---

# How do you debug a service mesh that is breaking service-to-service traffic?

**Short answer:** Work out which layer is refusing the request, because a mesh adds three new ones. Read the **sidecar's own response flags** first - Envoy tells you exactly why it failed (`UF` upstream failure, `UO` overflow/circuit-breaker, `URX` retry limit, `UAEX` authorization denied, `NR` no route) - then check, in order: **was the sidecar injected at all** (an uninjected Pod cannot participate in mTLS and gets connection resets), **is the mTLS mode consistent** (`STRICT` on one side and plain text on the other is the classic outage), **does an `AuthorizationPolicy` deny it** (they are default-allow until one selects the workload, then default-deny for that workload), and **do `VirtualService`/`DestinationRule` actually route where you think** - `istioctl proxy-config` shows the effective configuration rather than your intent. The single most useful habit: compare the _intended_ config with the _programmed_ config, because a mesh failure is nearly always a divergence between the two.

## Detail

### First: is the request even reaching the mesh's data plane?

- **Sidecar present?** `kubectl get pod -o jsonpath='{.spec.containers[*].name}'` - two containers (or the native-sidecar init container) means injected. Missing injection is caused by a namespace without the `istio-injection=enabled` label or the wrong revision label, a Pod annotated `sidecar.istio.io/inject: "false"`, or a workload created before injection was enabled. With Istio's ambient mode there is no sidecar at all, and the equivalent check is whether the Pod is enrolled in the ztunnel data path.
- **Sidecar healthy and configured?** `istioctl proxy-status` compares each proxy against the control plane: `SYNCED` is good, `STALE` means the proxy is not receiving updates (control-plane connectivity, resource pressure, or a rejected configuration). A `NOT SENT` cluster is a strong hint the resource you wrote was never accepted.
- **Startup races.** An application container that opens connections before the sidecar is ready fails at boot. Native sidecars (init container with `restartPolicy: Always`) fix the ordering properly; `holdApplicationUntilProxyStarts` is the older workaround.
- **Ports and protocols.** The mesh needs correctly **named** Service ports (`http`, `grpc`, `tcp-*`) or it guesses the protocol - and a misdetected protocol produces baffling behaviour like HTTP retries applied to a database connection. Headless services, `hostNetwork` Pods, and non-standard ports all need explicit handling.

### Then: read the proxy's verdict

Envoy access logs carry a response-flag field that names the failure. Learn the common ones:

| Flag            | Meaning                                     | Where to look                                           |
| --------------- | ------------------------------------------- | ------------------------------------------------------- |
| `UF`, `UC`      | Upstream connection failure / termination   | Backend down, wrong port, mTLS mismatch                 |
| `UO`            | Upstream overflow - circuit breaker tripped | `DestinationRule` connection pool limits                |
| `URX`           | Retry limit exceeded                        | Retry policy plus a genuinely failing upstream          |
| `UT`            | Upstream request timeout                    | `VirtualService` timeout versus real dependency latency |
| `NR`            | No route configured                         | `VirtualService` host/port mismatch                     |
| `RBAC` / `UAEX` | Denied by authorization policy              | `AuthorizationPolicy`                                   |
| `DC`            | Downstream connection termination           | Client gave up, or its own timeout is shorter           |

A `503` with `UF` and an `upstream_reset_before_response_started{connection_failure,TLS_error}` message is almost always mTLS: one side speaks TLS and the other does not.

### mTLS: the most common self-inflicted outage

`PeerAuthentication` sets whether a workload requires mTLS (`STRICT`, `PERMISSIVE`, `DISABLE`), and `DestinationRule` sets whether the client originates it (`ISTIO_MUTUAL`, `SIMPLE`, `DISABLE`). Every mismatch has a signature failure, and the safe migration path is always the same: enable `PERMISSIVE` mesh-wide, confirm from telemetry that all traffic is already mTLS, then move to `STRICT` namespace by namespace. Going straight to `STRICT` breaks every uninjected client - including health checkers, Prometheus scrapes that are not mesh-aware, and anything outside the mesh - which is exactly the incident this question is usually drawn from. Watch too for expired or rotating certificates (`istioctl proxy-config secret` shows what the proxy holds) and for the trust domain mismatch that appears in multi-cluster meshes.

### Authorization policies: default-allow until they are not

`AuthorizationPolicy` has a trap worth stating precisely: with no policy, all traffic is allowed. As soon as **one** ALLOW policy selects a workload, everything not matched by a policy is denied for that workload. So adding a narrow policy for one caller silently cuts off every other caller. Principals are SPIFFE identities (`cluster.local/ns/prod/sa/checkout`) and depend on mTLS being in place - a policy keyed on a principal cannot match a plain-text request, which is why authorization and mTLS problems present together. `istioctl proxy-config rbac` (or the proxy's debug endpoint) shows what the sidecar actually enforces.

### Routing: intent versus programmed configuration

`VirtualService` and `DestinationRule` errors are usually a mismatch between the host you wrote and the host the client actually calls - a short name versus an FQDN, a missing `exportTo`, a subset named in a route with no matching label in the `DestinationRule` (which yields `NR`/503 for that subset), two `VirtualService` resources for the same host silently merging in an order you did not intend, or an `Sidecar` resource restricting egress so an unrelated host becomes unreachable. Validate before applying (`istioctl analyze`) and inspect the result afterwards (`istioctl proxy-config route|cluster|endpoint`). For traffic leaving the mesh, `ServiceEntry` and the outbound traffic policy determine whether unknown hosts are allowed or blocked - a `REGISTRY_ONLY` policy is a common cause of "our service cannot reach the payment provider any more".

### And the layer beneath

A mesh does not replace Kubernetes networking. If the Service has no endpoints, or a `NetworkPolicy` drops the packet, the mesh will report an upstream failure that has nothing to do with mesh configuration. Check those before rewriting policies: see [how do you troubleshoot a Kubernetes Service that has no endpoints](../kubernetes/how-do-you-troubleshoot-a-kubernetes-service-that-has-no-endpoints.md) and [how do Kubernetes NetworkPolicies work, and how do you debug one that blocks traffic](../kubernetes/how-do-kubernetes-networkpolicies-work-and-how-do-you-debug-one-that-blocks-traffic.md).

## Example

```bash
# 1. Is the data plane there and in sync with the control plane?
istioctl proxy-status                 # SYNCED / STALE / NOT SENT per proxy
kubectl get pod checkout-7d9f -n prod -o jsonpath='{.spec.containers[*].name}'
# api istio-proxy                     <- injected. One name only = not in the mesh.

# 2. Validate intent, then inspect what was actually programmed
istioctl analyze -n prod              # catches most config errors before they bite
istioctl proxy-config route   deploy/orders -n prod --name 80 -o json | jq '.[].virtualHosts[].domains'
istioctl proxy-config cluster deploy/orders -n prod --fqdn checkout.prod.svc.cluster.local
istioctl proxy-config endpoint deploy/orders -n prod --cluster 'outbound|80||checkout.prod.svc.cluster.local'
# no endpoints here = a Kubernetes problem, not a mesh problem

# 3. The proxy's own verdict, per request
kubectl logs -n prod deploy/orders -c istio-proxy --tail=20 | grep checkout
# "GET /price HTTP/1.1" 503 UF upstream_reset_before_response_started{connection_failure,TLS_error}
#                            ^^ mTLS mismatch, not a routing problem

# 4. mTLS and authorization state, as enforced
istioctl proxy-config secret deploy/orders -n prod          # certs and expiry
kubectl get peerauthentication,destinationrule,authorizationpolicy -A
istioctl proxy-config rbac deploy/checkout -n prod          # what the sidecar enforces

# 5. Prove the hop end to end, from inside the client's namespace
kubectl exec -n prod deploy/orders -c istio-proxy -- \
  curl -s -o /dev/null -w '%{http_code}\n' http://checkout.prod.svc.cluster.local/healthz
```

```yaml
# The migration order that avoids the classic mTLS outage
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata: { name: default, namespace: prod }
spec:
  mtls: { mode: PERMISSIVE } # step 1: accept both, verify telemetry is 100% mTLS
  # then, per namespace:      mode: STRICT      <- step 2, never step 1
---
# AuthorizationPolicy: the moment this exists, everything NOT listed is denied
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata: { name: checkout-allow, namespace: prod }
spec:
  selector: { matchLabels: { app: checkout } }
  action: ALLOW
  rules:
    - from:
        - source:
            principals: # SPIFFE identities - require mTLS to match at all
              - cluster.local/ns/prod/sa/orders
              - cluster.local/ns/istio-system/sa/istio-ingressgateway # do not forget the gateway
      to:
        - operation: { methods: [GET, POST], paths: ["/api/*"] }
---
# Circuit breaker: the source of 503 UO under load - tune it, do not remove it
apiVersion: networking.istio.io/v1
kind: DestinationRule
metadata: { name: checkout, namespace: prod }
spec:
  host: checkout.prod.svc.cluster.local
  trafficPolicy:
    tls: { mode: ISTIO_MUTUAL } # client side must agree with PeerAuthentication
    connectionPool:
      tcp: { maxConnections: 200 }
      http: { http2MaxRequests: 1000, maxRequestsPerConnection: 0 }
    outlierDetection: # eject the one bad instance owning your p99
      consecutive5xxErrors: 5
      interval: 10s
      baseEjectionTime: 30s
```

## Interview tips

- Say first that a mesh adds layers, so the job is identifying **which** layer refused the request - and that Envoy's response flags tell you directly. Naming `UF`, `UO`, `NR`, `RBAC` is the single strongest signal in this answer.
- "Compare intended configuration with programmed configuration" is the sentence that shows mesh experience. `istioctl proxy-status` and `proxy-config` are how you do it.
- The mTLS `STRICT` migration story is the best war story: go `PERMISSIVE` first, verify from telemetry, then `STRICT` per namespace. Straight to `STRICT` breaks every uninjected client.
- Get the `AuthorizationPolicy` semantics exactly right - default-allow until one policy selects the workload, then default-deny for it. Mention the ingress gateway's own identity as the thing people forget to allow.
- Mention the sidecar startup race and native sidecars as the modern fix. It is a real production bug with a clean answer.
- Bring up named Service ports and protocol detection - a mis-detected protocol produces symptoms that look nothing like a configuration error.
- Say that you would rule out plain Kubernetes first: no endpoints or a NetworkPolicy drop will be reported by the mesh as an upstream failure.
- Close with `outlierDetection` and circuit-breaker limits as things you tune rather than disable, and note that `503 UO` means your own connection-pool limits, not the backend. See [what is a service mesh](../cloud-native-architecture/what-is-service-mesh.md) and [what is Istio](../container-orchestration-advanced/what-is-istio.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot Docker networking between containers?]] (`#415`): [How do you troubleshoot Docker networking between containers?](../docker/how-do-you-troubleshoot-docker-networking-between-containers.md)
- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to API Gateway and Service Mesh](./README.md) · [All topics](../README.md)
