---
title: "How do you debug a Kubernetes Ingress that is not routing traffic?"
id: 406
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - kubernetes
  - interview-questions
  - network-security
  - api-gateway-and-service-mesh
---

# How do you debug a Kubernetes Ingress that is not routing traffic?

**Short answer:** Follow the request path from the outside in and stop at the first hop that fails - **DNS → the controller's external load balancer → the controller Pod → the Ingress object (class, host, path, TLS) → the backend Service → the Pod**. The error tells you where you are: a connection timeout is DNS or the load balancer, the controller's own 404 page means no rule matched (wrong `ingressClassName`, host, or `pathType`), a 503 means the rule matched but the Service has no ready endpoints, and a 502 means the backend answered badly - wrong port, wrong scheme, or a broken TLS assumption. The controller log for a single request is worth more than any amount of YAML re-reading.

## Detail

### Walk the path in order

1. **DNS.** Does the hostname resolve to the load balancer that fronts your ingress controller? `dig +short shop.example.com` compared with `kubectl get svc -n ingress-nginx`. A stale record after a controller reinstall - new load balancer, old address - is a routine cause. See [how do you manage DNS and global traffic routing](../cloud-engineering/how-do-you-manage-dns-and-global-traffic-routing.md).
2. **The controller's Service.** `EXTERNAL-IP` stuck at `<pending>` means no cloud controller, missing subnet tags, or exhausted quota; the Service's events say which. Check the cloud load balancer's own health checks and its security group - it has health checks separate from your readiness probes, and a failing one produces 5xx with perfectly healthy Pods.
3. **The controller Pods.** Running and ready? `kubectl -n ingress-nginx get pods`. Then the key step most people skip: **tail the controller log while you send one request.** The access log line shows the matched host, the matched path, the chosen upstream, the status, and the upstream response time. If your request never appears, it never reached the controller and everything downstream is irrelevant.
4. **Did the controller adopt the Ingress at all?** `kubectl describe ingress` shows the controller's events and, importantly, `spec.ingressClassName`. With multiple controllers - or an unlabelled `IngressClass` and no default - an Ingress with no class is picked up by nobody, and there is no error anywhere except its absence from the controller's configuration. The deprecated `kubernetes.io/ingress.class` annotation still exists in older setups; mixing the two is a classic misconfiguration.
5. **Host and path matching.** The `host` must match the `Host` header exactly (wildcards match one label only, and `Host: shop.example.com:8443` with a port still matches the host). `pathType` matters more than people expect: `Prefix` matches whole path segments (`/api` matches `/api/v1` but not `/apiv1`), `Exact` matches the entire path, and `ImplementationSpecific` delegates to the controller - which is why an NGINX regex path silently fails to behave on a different controller. A rewrite annotation with a capture group and no matching regex in the path is the classic "404 for a valid URL".
6. **The backend Service and its endpoints.** A 503 from the controller almost always means the Service has no ready endpoints, or the Ingress names a Service or port that does not exist. The Ingress's `port.number` must be the **Service** port, not the container port - a mismatch here gives a 502 or a connection refused upstream. See [how do you troubleshoot a Kubernetes Service that has no endpoints](./how-do-you-troubleshoot-a-kubernetes-service-that-has-no-endpoints.md).
7. **TLS.** `curl -v` shows which certificate was served. The default self-signed "Kubernetes Ingress Controller Fake Certificate" means the controller found no matching secret: the TLS secret must exist **in the same namespace as the Ingress**, be of type `kubernetes.io/tls`, and its certificate must cover the requested host - and with cert-manager, check the `Certificate`, `CertificateRequest`, `Order`, and `Challenge` objects in that order, because a stuck HTTP-01 challenge is usually an ingress rule that does not route `/.well-known/acme-challenge/`. SNI matters: a request without SNI gets the default certificate.
8. **Backend protocol assumptions.** If the upstream speaks HTTPS or gRPC and the controller assumes plain HTTP, you get 502s or a protocol error. That is what `nginx.ingress.kubernetes.io/backend-protocol: "HTTPS"` (or `GRPC`) exists for.
9. **NetworkPolicy.** A default-deny in the application namespace blocks the controller's Pods from reaching the backend even though every Kubernetes object is correct. Allow the ingress controller namespace explicitly.

### Isolate with a bypass test

Take layers away rather than reasoning about all of them: `kubectl port-forward svc/checkout 8080:80` proves the app and Service work; `curl` from inside the controller Pod to the Service DNS name proves the controller can reach the backend; `curl --resolve shop.example.com:443:<lb-ip>` proves routing without touching DNS. Whichever test first fails is your layer.

### Securing it properly once it routes

Redirect HTTP to HTTPS at the controller (`force-ssl-redirect`), terminate TLS with a real certificate from cert-manager, set HSTS, put a WAF or the cloud provider's equivalent in front for public endpoints, and rate-limit per client. See [what is SSL/TLS](../network-security/what-is-ssl-tls.md) and [what is a Web Application Firewall](../network-security/what-is-a-web-application-firewall-waf.md). If you find yourself needing traffic splitting, retries, header manipulation, and per-route authentication, that is the point at which Gateway API or a service mesh replaces annotation sprawl. See [how do you run a service mesh in production without the sidecar tax](../api-gateway-and-service-mesh/how-do-you-run-a-service-mesh-in-production-without-the-sidecar-tax.md).

## Example

```bash
# Watch the controller handle one request - the single highest-value step
kubectl -n ingress-nginx logs -l app.kubernetes.io/name=ingress-nginx -f --tail=0 &
curl -sv --resolve shop.example.com:443:203.0.113.10 https://shop.example.com/api/orders
# 192.0.2.7 - - "GET /api/orders HTTP/2.0" 503 ... upstream: "" host: "shop.example.com"
#                                          ^^^ matched the rule, no endpoints behind it

# Was the Ingress adopted, and by which controller?
kubectl describe ingress shop -n prod | sed -n '/Class/,/Events/p'
kubectl get ingressclass                       # is any class the default?

# Does the controller see the backend at all?
kubectl -n ingress-nginx exec deploy/ingress-nginx-controller -- \
  curl -s -o /dev/null -w '%{http_code}\n' http://checkout.prod.svc.cluster.local:80/healthz

# Take the Ingress out of the picture entirely
kubectl -n prod port-forward svc/checkout 8080:80 & curl -s localhost:8080/healthz
```

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: shop
  namespace: prod # the TLS secret must live here too
  annotations:
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    # Only add a rewrite if the path is a regex with a capture group - otherwise
    # this is the classic cause of a 404 on a URL that looks correct.
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  ingressClassName: nginx # omit this and no controller may claim the Ingress
  tls:
    - hosts: [shop.example.com] # certificate must cover this exact host
      secretName: shop-tls
  rules:
    - host: shop.example.com # must equal the Host header
      http:
        paths:
          - path: /api(/|$)(.*) # regex pairs with the rewrite above
            pathType: ImplementationSpecific
            backend:
              service:
                name: checkout
                port: { number: 80 } # the SERVICE port, not the container port
```

## Interview tips

- Answer as a path walk from DNS inward, and say that you stop at the first failing hop. Structure is what is being assessed.
- Map the status codes: controller 404 = no rule matched, 503 = no ready endpoints, 502 = backend answered badly or wrong protocol, timeout = never reached the controller. Reciting this mapping alone demonstrates real experience.
- Say "I would tail the controller log while sending a single request" early. It is the step that resolves most of these and few candidates mention it.
- Bring up `ingressClassName` and the no-default-class case - an Ingress that no controller owns fails with no error message at all.
- Know `pathType` semantics and the rewrite-with-capture-group trap. This is the most common cause of a 404 on a URL that looks right.
- For TLS, mention the fake certificate as the tell, the same-namespace secret requirement, and the cert-manager chain (`Certificate` → `CertificateRequest` → `Order` → `Challenge`).
- Close with the bypass tests (`port-forward`, `curl` from inside the controller Pod, `--resolve`) - taking layers away is more convincing than reading YAML harder. See [how do you expose an application running in Kubernetes to the outside world](./how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you run a multi-tenant Kubernetes cluster?]] (`#453`): [How do you run a multi-tenant Kubernetes cluster?](../container-orchestration-advanced/how-do-you-run-a-multi-tenant-kubernetes-cluster.md)
- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do you run an application across multiple Kubernetes clusters?]] (`#414`): [How do you run an application across multiple Kubernetes clusters?](../container-orchestration-advanced/how-do-you-run-an-application-across-multiple-kubernetes-clusters.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
