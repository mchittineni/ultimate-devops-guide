---
title: "What is the difference between a reverse proxy and a forward proxy?"
id: 493
category: "Network Security"
difficulty: "Beginner"
tags:
  - devops
  - network-security
  - interview-questions
  - api-gateway-and-service-mesh
---

# What is the difference between a reverse proxy and a forward proxy?

**Short answer:** The difference is **which side it acts for**. A **forward proxy** sits in front of the **clients** and represents them to the internet: outbound traffic goes through it, so it is where you enforce egress policy, allow or block destinations, cache downloads, and hide the clients' addresses. Clients must be configured to use it (`HTTP_PROXY`, a PAC file, or transparent interception). A **reverse proxy** sits in front of the **servers** and represents them to the world: inbound traffic arrives at it, and it terminates TLS, routes by host and path, load-balances across backends, caches responses, compresses, and shields the origins - clients know nothing about it and address it as if it were the application. So: forward proxy = "who may my machines talk to?"; reverse proxy = "how do requests reach my services?" nginx, HAProxy, Envoy, an ALB, and a Kubernetes ingress controller are reverse proxies; Squid, an Azure Firewall with FQDN rules, and a corporate web gateway are forward proxies.

## Detail

### The two directions

```text
FORWARD PROXY                          REVERSE PROXY

clients ─┐                                        ┌─ app-1
clients ─┼─> proxy ──> internet     internet ──> proxy ─┼─ app-2
clients ─┘   (egress policy,        (TLS, routing,      └─ app-3
              caching, DLP,          LB, cache, WAF)
              audit)

acts for: the CLIENT                   acts for: the SERVER
configured on: the client              configured on: DNS - clients just resolve the name
hides: the clients                     hides: the backends
```

|                   | Forward proxy                                                                    | Reverse proxy                                                                             |
| ----------------- | -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Represents        | Clients                                                                          | Servers                                                                                   |
| Traffic direction | Outbound (egress)                                                                | Inbound (ingress)                                                                         |
| Client awareness  | Must be configured (or transparently intercepted)                                | None - it is just the endpoint                                                            |
| Hides             | Client identity/addresses from the destination                                   | Backend topology from the client                                                          |
| Typical controls  | Destination allowlist/denylist, FQDN filtering, DLP, authentication, audit       | TLS termination, host/path routing, load balancing, caching, rate limiting, WAF           |
| Examples          | Squid, Azure Firewall (FQDN rules), corporate SWG, `HTTP_PROXY` in a build agent | nginx, HAProxy, Envoy, Traefik, ALB, Application Gateway, ingress controllers, CloudFront |
| Cloud analogue    | NAT gateway (address translation only) + egress firewall (policy)                | Load balancer / CDN / API gateway                                                         |

A useful mnemonic: a forward proxy is what your **laptop or CI runner** is configured to use; a reverse proxy is what your **DNS record points at**.

### Why each exists in a real estate

**Forward proxy / egress control** answers a security question that a NAT gateway does not. A NAT gateway lets a private subnet reach _anything_ on the internet; an egress firewall with FQDN rules lets it reach _only_ the package repository, the container registry, and your SaaS endpoints. That matters because it constrains a compromised workload: data exfiltration and command-and-control both need outbound connectivity, and an allowlist breaks them. It also fixes the practical problem of "the vendor gave us an IP allowlist" - all your outbound traffic appears from the proxy's stable address. Use it for build agents (where a supply-chain attack would otherwise phone home freely), regulated environments, and any workload with a documented set of external dependencies.

**Reverse proxy** answers the ingress question and is where most of your traffic policy lives: one public endpoint for many services, TLS terminated once, path-based routing to microservices, canary and blue/green traffic shifting by weight, retries and timeouts, response caching, header manipulation, request-size limits, and a WAF in front. It also decouples clients from topology - you can replace, rename, or move a backend without a client change. In Kubernetes the ingress controller _is_ a reverse proxy; in a service mesh the sidecar is a reverse proxy for inbound traffic and a forward proxy for outbound, which is a neat way to show you understand both terms.

### CORS, which is asked alongside this

**Cross-Origin Resource Sharing** is a browser mechanism, not a proxy feature. Browsers enforce the same-origin policy: JavaScript on `https://app.example.com` may not read a response from `https://api.example.com` unless the **server** opts in with `Access-Control-Allow-Origin` (and `-Methods`, `-Headers`, and `-Credentials` where relevant). For non-simple requests the browser first sends an `OPTIONS` **preflight**, and the server must answer it correctly or the real request never happens.

The DevOps-relevant points:

- A CORS failure is a **browser** error; `curl` succeeds happily, which is why "it works from the terminal but not the app" is nearly always CORS.
- The fix belongs on the **server or the reverse proxy** that responds, not on the client.
- `Access-Control-Allow-Origin: *` cannot be combined with `Access-Control-Allow-Credentials: true` - you must echo a specific, validated origin.
- Putting both the frontend and the API behind **one reverse proxy on one origin** (e.g. `/api` on the same host) removes CORS entirely, which is often the cleanest answer.
- CORS is not a security control. It restricts what a browser will let a page read; it does not protect your API - authentication and authorisation do.

### Ingress versus egress

Simple but frequently asked: **ingress** is traffic entering your network or workload; **egress** is traffic leaving it. Both need policy, and teams almost always over-invest in ingress and under-invest in egress. In Kubernetes a `NetworkPolicy` has `Ingress` and `Egress` rule types, and the moment a policy selects a Pod that direction becomes default-deny - which is why an egress policy that forgets **DNS on port 53** breaks everything. In AWS terms, ingress is the load balancer and its security groups; egress is the NAT gateway plus, if you want control rather than just connectivity, a firewall or proxy.

### Related terms interviewers pair with this

- **NAT** rewrites addresses at layer 3/4; a proxy terminates the connection at layer 7 and makes a new one. NAT gives connectivity, a proxy gives visibility and policy.
- **Load balancer versus reverse proxy**: overlapping. Every layer 7 load balancer is a reverse proxy; a layer 4 load balancer forwards without terminating HTTP, so it is not doing proxy-level work.
- **API gateway**: a reverse proxy with API-specific features - authentication, per-key quotas, request validation, versioning, usage plans.
- **Transparent proxy**: a forward proxy clients are not configured for, imposed by routing. Convenient, but TLS interception requires installing a CA on every client, which has real privacy and operational consequences.
- **Sidecar proxy**: both, per Pod - which is exactly why service meshes can enforce mTLS and egress policy at once.

## Example

```nginx
# Reverse proxy: one public origin, TLS terminated, routed by path, CORS handled here
server {
  listen 443 ssl http2;
  server_name app.example.com;

  ssl_certificate     /etc/ssl/certs/app.pem;
  ssl_certificate_key /etc/ssl/private/app.key;
  ssl_protocols       TLSv1.2 TLSv1.3;

  # same origin for UI and API -> no CORS at all, the cleanest fix
  location / {
    proxy_pass http://frontend:3000;
  }

  location /api/ {
    proxy_pass http://api:8080/;
    proxy_set_header Host              $host;
    proxy_set_header X-Real-IP         $remote_addr;
    proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;   # backends need this to build URLs
    proxy_read_timeout 30s;
    client_max_body_size 10m;
  }

  # if the API must live on another origin, the SERVER opts in - specifically
  location /api/v2/ {
    if ($http_origin ~* '^https://(app|admin)\.example\.com$') {
      add_header Access-Control-Allow-Origin      $http_origin always;  # not "*"
      add_header Access-Control-Allow-Credentials true always;
      add_header Access-Control-Allow-Headers     "Authorization,Content-Type" always;
      add_header Access-Control-Max-Age           86400 always;
    }
    if ($request_method = OPTIONS) { return 204; }   # answer the preflight
    proxy_pass http://api-v2:8080/;
  }
}
```

```bash
# Forward proxy: constrain what the build agents may reach
export HTTP_PROXY=http://proxy.internal:3128
export HTTPS_PROXY=http://proxy.internal:3128
export NO_PROXY=169.254.169.254,localhost,127.0.0.1,.internal,.svc.cluster.local
#              ^ metadata endpoint must NOT go through the proxy

curl -sS -o /dev/null -w '%{http_code}\n' https://registry.example.com/v2/   # 200 (allowed)
curl -sS -o /dev/null -w '%{http_code}\n' https://pastebin.com/              # 403 (denied)
```

```text
# Squid: an egress allowlist, which is what makes the proxy worth running
acl allowed_dsts dstdomain .example.com .npmjs.org .pypi.org registry-1.docker.io
acl CONNECT method CONNECT
http_access allow allowed_dsts
http_access deny all
access_log /var/log/squid/access.log   # the audit trail a NAT gateway cannot give you
```

```yaml
# Kubernetes: the ingress controller is the reverse proxy; NetworkPolicy is the egress control
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: api-egress, namespace: prod }
spec:
  podSelector: { matchLabels: { app: api } }
  policyTypes: [Egress]
  egress:
    - to: # DNS first, or nothing else resolves
        - namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: kube-system } }
      ports: [{ port: 53, protocol: UDP }, { port: 53, protocol: TCP }]
    - to: [{ podSelector: { matchLabels: { app: postgres } } }]
      ports: [{ port: 5432, protocol: TCP }]
    - to: [{ ipBlock: { cidr: 10.20.9.0/24 } }] # the egress proxy - everything external via it
      ports: [{ port: 3128, protocol: TCP }]
```

```bash
# "It works in curl but not in the browser" -> CORS. Prove it with the preflight.
curl -isS -X OPTIONS https://api.example.com/v2/orders \
  -H 'Origin: https://app.example.com' \
  -H 'Access-Control-Request-Method: POST' \
  -H 'Access-Control-Request-Headers: authorization,content-type' | head -20
# look for: Access-Control-Allow-Origin echoing the origin, and the method/headers allowed
```

## Interview tips

- Answer with the one distinction that generates everything else: a forward proxy acts for the **client** (outbound), a reverse proxy acts for the **server** (inbound). Then give two examples of each.
- Add the configuration asymmetry: clients must be configured to use a forward proxy, whereas a reverse proxy is transparent to clients because DNS points at it.
- Make the security argument for egress control, since it is the part most candidates skip: a NAT gateway gives connectivity to anything, an egress proxy or FQDN firewall gives an allowlist - which is what breaks exfiltration and command-and-control from a compromised workload or build agent.
- Say that in Kubernetes the ingress controller is a reverse proxy, and that a service-mesh sidecar is both - reverse for inbound, forward for outbound. That single sentence shows you hold both concepts at once.
- For CORS, state that it is a **browser** mechanism enforced client-side and opted into by the server, that `curl` bypasses it (hence "works in the terminal, fails in the app"), that `*` cannot be combined with credentials, and that serving UI and API on one origin behind one reverse proxy removes it entirely. Add that CORS is not a security control.
- Define ingress and egress plainly, and volunteer the Kubernetes trap - an egress `NetworkPolicy` without DNS on port 53 breaks everything.
- Distinguish NAT (layer 3/4 address rewriting, connectivity) from a proxy (layer 7 termination, visibility and policy), and note that every layer 7 load balancer is a reverse proxy while a layer 4 one is not.
- If transparent proxying comes up, mention that intercepting TLS requires a CA on every client, with the privacy and operational cost that implies. See [what happens when a user opens your application in a browser](./what-happens-when-a-user-opens-your-application-in-a-browser.md), [what is an API gateway](../api-gateway-and-service-mesh/what-is-an-api-gateway.md), [designing defence in depth for a cloud network](./how-do-you-design-defence-in-depth-for-a-cloud-network.md), and [how do Kubernetes NetworkPolicies work](../kubernetes/how-do-kubernetes-networkpolicies-work-and-how-do-you-debug-one-that-blocks-traffic.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you troubleshoot Docker networking between containers?]] (`#415`): [How do you troubleshoot Docker networking between containers?](../docker/how-do-you-troubleshoot-docker-networking-between-containers.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)
- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#20`): [What is the difference between Continuous Delivery and Continuous Deployment?](../cicd/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Network Security](./README.md) · [All topics](../README.md)
