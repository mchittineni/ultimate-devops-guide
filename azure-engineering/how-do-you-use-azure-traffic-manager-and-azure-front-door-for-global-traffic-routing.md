---
title: "How Do You Use Azure Traffic Manager and Azure Front Door for Global Traffic Routing?"
id: 743
category: "Azure Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - azure-engineering
  - front-door
  - traffic-manager
  - global-routing
quiz:
  stem: "Why does Azure Front Door achieve significantly faster regional failover than Azure Traffic Manager for web applications?"
  options:
    - "Front Door does not use Microsoft network infrastructure."
    - "Front Door acts as a Layer 7 anycast reverse proxy terminating connections at edge POPs, bypassing DNS caching delays that limit Traffic Manager."
    - "Traffic Manager only supports FTP and SMTP protocols."
    - "Front Door requires no health probe configurations."
  answer: 2
  explanation: "Traffic Manager relies on DNS responses, which are subject to client and ISP caching (TTL). Front Door terminates connections at anycast edge nodes and dynamically routes traffic over Microsoft's backbone, shifting traffic as soon as edge health probes mark an origin unhealthy."
---

# How Do You Use Azure Traffic Manager and Azure Front Door for Global Traffic Routing?

**Short answer:** Azure Traffic Manager is a DNS-based global traffic balancer operating at Layer 4, routing clients via DNS responses. Azure Front Door is an anycast Layer 7 global reverse proxy combining HTTP/HTTPS routing, global load balancing, SSL offload, CDN caching, and integrated Web Application Firewall (WAF) capabilities.

**Short answer:** **Traffic Manager** is DNS-based: it answers the DNS query for your name with the endpoint chosen by its routing method (priority, weighted, performance, geographic, multivalue, subnet) and never sees the traffic itself, so it works for any protocol but fails over only as fast as DNS caches expire. **Front Door** is a global Layer 7 reverse proxy on Microsoft's edge: clients connect to an anycast edge location, which terminates TLS, applies WAF and caching, and forwards over the Microsoft backbone to the healthiest origin - so failover does not depend on DNS, but it only handles HTTP/HTTPS.

## Detail

### DNS Steering vs an Anycast Reverse Proxy

### Azure Traffic Manager (DNS-Based)

- **Mechanism**: A CNAME points `app.contoso.com` at `contoso.trafficmanager.net`; Traffic Manager returns the chosen endpoint's name or IP based on routing method and endpoint health (probes over HTTP, HTTPS, or TCP).
- **Protocols**: Any - the client connects directly to the endpoint, so TCP, UDP, and non-Azure endpoints all work.
- **Failover**: Bounded by probe interval, tolerated failures, and DNS TTL - and by resolvers and clients that ignore or extend TTLs. Expect tens of seconds to minutes.
- **Limits**: No TLS termination, no path or header routing, no WAF, and clients keep hitting a failed endpoint until their cached answer expires.

### Azure Front Door (Layer 7 Anycast Reverse Proxy)

- **Mechanism**: A global HTTP/HTTPS reverse proxy across Microsoft's edge points of presence. Split TCP means the client's TCP and TLS handshakes complete at a nearby edge; the edge keeps warm connections to origins across the backbone.
- **Failover**: Driven by health probes from the edge and origin priorities/weights; because clients never had the origin's address, traffic shifts as soon as the edge marks an origin unhealthy (typically seconds to tens of seconds, depending on probe settings) with no DNS cache in the way.
- **Capabilities**: WAF at the edge, TLS termination with managed certificates, path-based routing (`/api` to AKS, `/static` to Blob storage), rules engine rewrites, caching, and **Private Link to origins** (Premium) so origins need no public exposure.
- **Tiers**: Front Door Standard and Premium are current; Front Door (classic) retires in March 2027. Restrict origins to Front Door traffic (Private Link, or the `AzureFrontDoor.Backend` service tag plus `X-Azure-FDID` header check) so the edge cannot be bypassed.

```text
Traffic Manager:
[Client] ──► [DNS query] ──► [Traffic Manager answers: region 1] ──► [Client connects directly to region 1]

Front Door:
[Client] ──► anycast ──► [Microsoft edge POP: TLS / WAF / cache] ──► [Microsoft backbone] ──► [Origin region 1 / 2]
```

**When to combine them.** Traffic Manager can sit above Front Door and a fallback path for very high availability, or front non-HTTP services alongside Front Door for the web tier. Front Door is also a shared global dependency - its own rare outages argue for a documented bypass plan for critical services.

### Real-World Production Scenario

A retail bank's mobile users stayed pinned to a failed region for minutes during an outage because resolvers cached Traffic Manager answers. The bank moves the web and API tier to Front Door Premium with Private Link origins in two regions: connections terminate at the nearest edge, WAF policies block attacks before they reach the regions, and the next regional failure shifts traffic as soon as the edge probes fail. Traffic Manager remains in use for a TCP-based partner integration that Front Door cannot carry.

## Example

```bash
# Traffic Manager: priority (active/passive) failover with a low TTL
az network traffic-manager profile create -g rg-global -n tm-partner \
  --routing-method Priority --unique-dns-name contoso-partner --ttl 30 \
  --protocol TCP --port 8443
az network traffic-manager endpoint create -g rg-global --profile-name tm-partner \
  -n weu --type externalEndpoints --target partner-weu.contoso.com --priority 1

# Front Door Standard/Premium: profile, endpoint, origin group with health probes
az afd profile create -g rg-global --profile-name fd-web --sku Premium_AzureFrontDoor
az afd endpoint create -g rg-global --profile-name fd-web --endpoint-name web
az afd origin-group create -g rg-global --profile-name fd-web --origin-group-name app \
  --probe-request-type GET --probe-protocol Https --probe-path /healthz \
  --probe-interval-in-seconds 30 --sample-size 4 --successful-samples-required 3 \
  --additional-latency-in-milliseconds 50
az afd origin create -g rg-global --profile-name fd-web --origin-group-name app \
  --origin-name weu --host-name app-weu.azurewebsites.net --origin-host-header app-weu.azurewebsites.net \
  --priority 1 --weight 100 --enabled-state Enabled --https-port 443
```

## Interview tips

- Frame it as DNS steering (Traffic Manager) versus a Layer 7 proxy (Front Door) - Traffic Manager never carries traffic.
- Explain why DNS failover is slow: TTLs, resolver caching, and clients that ignore TTL.
- Choose Traffic Manager for non-HTTP protocols or non-Azure endpoints; Front Door for web apps and APIs needing WAF, TLS offload, caching, and fast failover.
- Mention origin lockdown (Private Link or service tag plus `X-Azure-FDID`) so attackers cannot bypass the edge.
- Know the lifecycle: Front Door (classic) retires in March 2027; Standard/Premium is current.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the different types of cloud services?]] (`#25`): [What are the different types of cloud services?](../cloud-platforms/what-are-the-different-types-of-cloud-services.md)
- [[How does networking differ across AWS, Azure, and GCP?]] (`#282`): [How does networking differ across AWS, Azure, and GCP?](../cloud-platforms/how-does-networking-differ-across-aws-azure-and-gcp.md)
- [[How do you manage DNS and global traffic routing?]] (`#220`): [How do you manage DNS and global traffic routing?](../cloud-engineering/how-do-you-manage-dns-and-global-traffic-routing.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Azure Engineering](./README.md) · [All topics](../README.md)
