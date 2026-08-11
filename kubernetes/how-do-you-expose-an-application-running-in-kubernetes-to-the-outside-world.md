---
title: "How do you expose an application running in Kubernetes to the outside world?"
id: 259
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - kubernetes
  - interview-questions
---

# How do you expose an application running in Kubernetes to the outside world?

**Short answer:** Four escalating options - `ClusterIP` (in-cluster only, the default), `NodePort` (a port on every node), `LoadBalancer` (one cloud load balancer per Service), and an **Ingress** or **Gateway API** resource, which puts a single layer-7 router in front of many Services. Production HTTP traffic almost always terminates at an ingress controller or Gateway, because one load balancer serving fifty Services is dramatically cheaper and more capable than fifty load balancers.

## Detail

**The Service types, and what each actually creates:**

| Type           | What you get                                             | Use for                                     |
| -------------- | -------------------------------------------------------- | ------------------------------------------- |
| `ClusterIP`    | A virtual IP reachable only inside the cluster           | Service-to-service calls (the default)      |
| `NodePort`     | The same, plus a port 30000-32767 open on **every** node | Bare metal, or behind an external LB        |
| `LoadBalancer` | The above, plus a provisioned cloud load balancer        | Non-HTTP protocols; one-off public services |
| `ExternalName` | A CNAME to an external DNS name - no proxying at all     | Pointing at a managed database or SaaS      |

`LoadBalancer` builds on `NodePort`, which builds on `ClusterIP` - they are layered, not alternatives.

**Why not a LoadBalancer per Service?** Cost and capability. Each one is a billed cloud resource with its own public IP and its own certificate to manage, and a layer-4 load balancer cannot route on hostname or path. Fifty microservices become fifty bills and fifty DNS records.

**Ingress** solves that: one controller (NGINX, Traefik, HAProxy, or a cloud-native one like AWS Load Balancer Controller) sits behind a single load balancer and routes by host and path to many Services, terminating TLS centrally. The controller is what does the work - the `Ingress` object is just configuration, so nothing happens until a controller is installed.

**Ingress is feature-frozen, and Gateway API is its successor.** Ingress's weakness is that anything beyond host/path routing - header matching, traffic splitting for canaries, timeouts, retries - has to be expressed in controller-specific annotations, which are not portable and are not validated. Gateway API replaces that with typed resources and a role split that matches how organisations actually work:

- `GatewayClass` - the controller implementation (platform team).
- `Gateway` - the listener, ports, and TLS config (cluster operator).
- `HTTPRoute` / `GRPCRoute` / `TCPRoute` - the routing rules (application team, in their own namespace).

That separation is the real selling point: app teams change routes without needing write access to shared ingress config, and `ReferenceGrant` controls cross-namespace access explicitly. New clusters should start on Gateway API; existing Ingress keeps working.

**TLS.** Certificates live in a Secret of type `kubernetes.io/tls` referenced by the Ingress or Gateway listener. In practice cert-manager issues and renews them automatically via ACME - which matters more every year as maximum public certificate lifetimes shrink.

**Non-HTTP traffic** (databases, gRPC streaming over raw TCP, UDP, MQTT) does not fit Ingress. Use a `LoadBalancer` Service, or Gateway API's `TCPRoute`/`UDPRoute`.

## Example

```yaml
# Gateway API: one shared gateway, per-team routes.
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: public
  namespace: infra
spec:
  gatewayClassName: envoy
  listeners:
    - name: https
      protocol: HTTPS
      port: 443
      hostname: "*.acme.com"
      tls:
        certificateRefs: [{ name: acme-wildcard-tls }]
      allowedRoutes:
        namespaces: { from: Selector, selector: { matchLabels: { gateway-access: "true" } } }
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: api
  namespace: payments
spec:
  parentRefs: [{ name: public, namespace: infra }]
  hostnames: ["api.acme.com"]
  rules:
    - matches: [{ path: { type: PathPrefix, value: /v2 } }]
      # 90/10 canary - impossible in plain Ingress without vendor annotations
      backendRefs:
        - { name: api-stable, port: 8080, weight: 90 }
        - { name: api-canary, port: 8080, weight: 10 }
```

```yaml
# The equivalent classic Ingress, for comparison.
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls: [{ hosts: [api.acme.com], secretName: api-tls }]
  rules:
    - host: api.acme.com
      http:
        paths:
          - path: /v2
            pathType: Prefix
            backend: { service: { name: api-stable, port: { number: 8080 } } }
```

```bash
kubectl get svc api -o wide                    # type, cluster IP, external IP, ports
kubectl get endpointslices -l kubernetes.io/service-name=api   # are there any backends?
kubectl describe ingress api                   # controller events explain 404s and cert failures
```

## Interview tips

- List the four Service types and note they are layered - `LoadBalancer` includes `NodePort` includes `ClusterIP`.
- "Why not one LoadBalancer per Service?" is the standard follow-up. Cost, one public IP each, certificate sprawl, and no layer-7 routing.
- Say that the `Ingress` object does nothing without a controller. Interviewers ask this to check whether you have actually installed one.
- Know that Ingress is frozen and Gateway API is the successor, and explain the role split - platform owns the `Gateway`, app teams own their `HTTPRoute`.
- A frequent scenario: "an Ingress returns 404 / the certificate is not issued." Answer with `kubectl describe ingress`, then check the EndpointSlice actually has backends and that the readiness probe is passing.
- If asked about `targetPort` being omitted on a Service - it defaults to the value of `port`.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)
- [[How do you troubleshoot a failed Helm release?]] (`#412`): [How do you troubleshoot a failed Helm release?](../container-orchestration-advanced/how-do-you-troubleshoot-a-failed-helm-release.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
