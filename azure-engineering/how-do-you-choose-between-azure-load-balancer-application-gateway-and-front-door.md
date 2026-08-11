---
title: "How do you choose between Azure Load Balancer, Application Gateway, and Front Door?"
id: 487
category: "Azure Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - azure-engineering
  - interview-questions
  - network-security
  - scalability-and-high-availability
---

# How do you choose between Azure Load Balancer, Application Gateway, and Front Door?

**Short answer:** Pick by **layer** and **scope**. **Azure Load Balancer** is layer 4 (TCP/UDP), **regional**, and pass-through - fastest, cheapest, no TLS termination, no URL awareness; use it for non-HTTP protocols, for very high throughput, and as the backend for AKS `LoadBalancer` Services. **Application Gateway** is layer 7 (HTTP/HTTPS), **regional**, and terminates TLS - it gives you host- and path-based routing, cookie-based session affinity, URL rewriting, autoscaling, and **WAF** (as Application Gateway WAF v2); use it in front of regional web workloads and AKS ingress. **Front Door** is layer 7 and **global**, an edge service - anycast entry points, Microsoft's backbone, caching/CDN, split-TCP acceleration, global failover across regions, and WAF at the edge; use it as the single global front door for a multi-region application, typically with Application Gateway or an internal load balancer behind it in each region. **Traffic Manager** is the fourth option and it is **DNS-only** - it hands out a different answer per policy and never sees your traffic, so it works for any protocol but fails over only as fast as DNS caching allows.

## Detail

### The comparison

|                    | Load Balancer       | Application Gateway                | Front Door             | Traffic Manager      |
| ------------------ | ------------------- | ---------------------------------- | ---------------------- | -------------------- |
| Layer              | 4 (TCP/UDP)         | 7 (HTTP/S)                         | 7 (HTTP/S)             | DNS only             |
| Scope              | Regional            | Regional                           | **Global** (edge)      | Global               |
| TLS termination    | No                  | Yes (and end-to-end re-encryption) | Yes                    | N/A                  |
| Host/path routing  | No                  | Yes                                | Yes                    | No                   |
| WAF                | No                  | Yes (WAF v2)                       | Yes (at the edge)      | No                   |
| Caching / CDN      | No                  | No                                 | **Yes**                | No                   |
| Session affinity   | 5-tuple / source-IP | Cookie-based                       | Cookie-based           | N/A                  |
| Health probes      | TCP/HTTP            | HTTP with custom probes            | HTTP from many edges   | HTTP/TCP from probes |
| Failover speed     | Seconds             | Seconds                            | Seconds (edge decides) | **DNS TTL bound**    |
| Non-HTTP protocols | **Yes**             | No                                 | No (HTTP/S only)       | Yes (any)            |
| Typical cost       | Lowest              | Middle                             | Highest                | Low                  |

The mapping to AWS, in case the interviewer asks: Load Balancer ≈ NLB, Application Gateway ≈ ALB (+ WAF), Front Door ≈ CloudFront + Global Accelerator + WAF, Traffic Manager ≈ Route 53 routing policies.

### Which layer is Application Gateway?

Asked verbatim, and the answer is **layer 7** - it parses HTTP, which is precisely what lets it route on host and path, insert and rewrite headers, terminate TLS, and run WAF rules against request bodies. A layer 4 load balancer cannot do any of that because it only sees addresses and ports. If someone asks why you would not just use Load Balancer for a web application, that is the answer: no TLS termination, no path routing, no WAF, and no cookie affinity.

### Combining them, which is the real production answer

```text
user
 └─ Front Door (global anycast edge)      TLS, WAF, caching, global failover, geo-filtering
     ├─ region eu-west  ──> Application Gateway (WAF v2) ──> AKS ingress / App Service
     └─ region us-east  ──> Application Gateway (WAF v2) ──> AKS ingress / App Service
                                              └─ internal Load Balancer for non-HTTP tiers
```

Front Door does global traffic management and edge protection; Application Gateway does regional layer 7 routing and is the one that sits inside your VNet with private backends. Two things to say about the combination: lock the Application Gateway's NSG so it only accepts traffic from **Front Door's** service tag plus the `X-Azure-FDID` header check, otherwise someone can bypass the edge WAF entirely by hitting the regional endpoint directly; and do not duplicate WAF rules at both layers without a reason - decide where the policy lives.

### Certificates, and the classic renewal question

Application Gateway terminates TLS, so the certificate lives on the **listener**. The right way is to reference a certificate in **Key Vault** (via a user-assigned managed identity with Get on secrets/certificates), so renewal happens in Key Vault - with auto-renewal from an integrated CA - and the gateway picks up the new version automatically. Uploading a `.pfx` directly to the listener means a manual replacement every year, which is exactly the "the TLS certificate has expired, what steps do you follow?" scenario. The answer to that: renew or reissue in Key Vault (or import the new `.pfx`), confirm the gateway's listener now serves the new certificate (`openssl s_client` and check the expiry), verify the whole chain including intermediates, and if backends use end-to-end TLS check the backend HTTP settings' trusted root certificate too. Then fix the cause - move to Key Vault with auto-renewal and an expiry alert 30 days out.

The related setting question - _which Application Gateway setting is used to upload the SSL certificate, and why?_ - is the **HTTPS listener** (the listener is where TLS terminates, so that is where the server certificate belongs). Backend HTTP settings hold the **trusted root** for re-encrypting to the backend, which is a different thing and a common mix-up.

### Blocking a domain or a path

_"How do you block a particular domain in Application Gateway?"_ Depends which side:

- **Inbound host**: a listener only accepts the hostnames you configure, and a **WAF custom rule** can block or allow by `Host` header, request URI, geography, IP set, or rate limit. That is the mechanism for blocking a specific hostname or path.
- **Outbound to a domain**: Application Gateway is not an egress control - that is **Azure Firewall** with FQDN rules or a proxy. Getting this distinction right matters; people reach for the wrong product.

WAF is where rate limiting, geo-filtering, bot protection, and the OWASP managed rule set live. Run new rules in **Detection** mode, review the logs for false positives, then switch to **Prevention** - deploying a WAF straight into blocking mode against a live application is a self-inflicted outage.

### Troubleshooting a 404 or 502 with healthy backends

The frequent scenario - _"backend services are healthy and I am getting a 404 (or 502); how do you troubleshoot?"_ - has a fixed order for Application Gateway:

1. **Listener and host name**: does the request's `Host` match a listener? A multi-site gateway with no matching hostname returns 404 from the gateway itself.
2. **Rule and path map**: is the URL path matched by a path-based rule, and does the default backend pool exist? A path pattern that matches nothing produces a 404 even with healthy backends.
3. **Backend health**, not just "the app is up": `az network application-gateway show-backend-health` reports per-member status with a reason. A **custom probe** matching the wrong path, host header, or expected status code marks a healthy backend unhealthy.
4. **Backend HTTP settings**: wrong port, HTTP vs HTTPS mismatch, `Pick host name from backend address` needed for App Service or a multi-tenant backend, and cookie affinity settings.
5. **NSG / UDR / private endpoint**: does the gateway's subnet actually reach the backend? Application Gateway needs its **own dedicated subnet** and its required ports open.
6. **Path rewriting**: the backend may expect `/` where the gateway forwards `/api/` - a URL rewrite or path override is the fix.
7. **502 specifically** usually means the gateway reached the backend and got an invalid or no response: timeout too low, backend TLS certificate untrusted for end-to-end, or the app returning a malformed response.

Diagnose with Application Gateway access, performance, and firewall **diagnostic logs** to Log Analytics and a KQL query - that is faster than guessing, and naming it shows you have done this.

### AKS specifics

AKS `Service type=LoadBalancer` provisions an Azure Load Balancer; an ingress controller (nginx, or **Application Gateway Ingress Controller**) puts layer 7 in front. AGIC programmes an Application Gateway directly from Ingress resources, which removes a hop and gives you WAF at the ingress - at the cost of tighter coupling and slower config propagation than an in-cluster controller. Given nginx ingress controller changes in the ecosystem, the sensible answer to "which ingress controller would you suggest?" is: AGIC when you want the managed WAF and no in-cluster data plane, or a maintained in-cluster controller (Traefik, HAProxy, Envoy Gateway / Gateway API implementations) when you want speed of config and portability.

## Example

```hcl
# Application Gateway WAF v2: certificate from Key Vault, autoscaling, custom probe
resource "azurerm_application_gateway" "app" {
  name                = "agw-prod"
  resource_group_name = azurerm_resource_group.prod.name
  location            = "westeurope"

  sku { name = "WAF_v2"  tier = "WAF_v2" }
  autoscale_configuration { min_capacity = 2  max_capacity = 10 }
  zones = ["1", "2", "3"]                       # zone-redundant

  identity {                                     # to read the cert from Key Vault
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.agw.id]
  }

  gateway_ip_configuration { name = "gw-ip"  subnet_id = azurerm_subnet.agw.id } # dedicated subnet

  ssl_certificate {
    name                = "wildcard-example-com"
    key_vault_secret_id = azurerm_key_vault_certificate.wildcard.secret_id  # auto-renewal
  }

  http_listener {
    name                           = "https"
    frontend_ip_configuration_name = "public"
    frontend_port_name             = "port-443"
    protocol                       = "Https"
    ssl_certificate_name           = "wildcard-example-com"   # TLS terminates on the LISTENER
    host_names                     = ["www.example.com", "api.example.com"]
  }

  probe {                                        # a wrong probe marks healthy backends down
    name                = "app-health"
    protocol            = "Https"
    path                = "/healthz"
    host                = "www.example.com"
    interval            = 15
    timeout             = 10
    unhealthy_threshold = 3
    match { status_code = ["200-299"] }
  }

  backend_http_settings {
    name                                = "https-backend"
    protocol                            = "Https"
    port                                = 443
    pick_host_name_from_backend_address = true   # required for App Service backends
    probe_name                          = "app-health"
    request_timeout                     = 30
    trusted_root_certificate_names      = ["internal-ca"]   # end-to-end TLS
  }

  waf_configuration {
    enabled          = true
    firewall_mode    = "Detection"               # Detection first, then Prevention
    rule_set_type    = "OWASP"
    rule_set_version = "3.2"
  }
}
```

```hcl
# Front Door in front, and the NSG rule that stops the edge being bypassed
resource "azurerm_cdn_frontdoor_firewall_policy" "waf" {
  name                = "fd-waf"
  resource_group_name = azurerm_resource_group.prod.name
  sku_name            = "Premium_AzureFrontDoor"
  mode                = "Prevention"
  custom_rule {
    name     = "rate-limit"
    type     = "RateLimitRule"
    action   = "Block"
    priority = 100
    rate_limit_threshold = 1000
    rate_limit_duration_in_minutes = 1
    match_condition { match_variable = "RequestUri"  operator = "Contains"  match_values = ["/api/"] }
  }
}

resource "azurerm_network_security_rule" "only_front_door" {
  name                        = "allow-front-door-only"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  destination_port_range      = "443"
  source_address_prefix       = "AzureFrontDoor.Backend"   # service tag, not 0.0.0.0/0
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.prod.name
  network_security_group_name = azurerm_network_security_group.agw.name
}
# plus validate the X-Azure-FDID header at the gateway, or the edge can be bypassed
```

```bash
# 404/502 with "healthy" backends - work the layers in order
az network application-gateway show-backend-health -g rg-prod -n agw-prod \
  --query 'backendAddressPools[].backendHttpSettingsCollection[].servers[].[address,health,healthProbeLog]' -o table

# Does the certificate on the listener actually serve what you think?
openssl s_client -connect www.example.com:443 -servername www.example.com </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates

# The fastest diagnosis: access + firewall logs in Log Analytics (KQL)
#   AzureDiagnostics
#   | where Category == "ApplicationGatewayAccessLog" and httpStatus_d in (404, 502)
#   | summarize count() by requestUri_s, host_s, backendPoolName_s, serverStatus_s
#   | order by count_ desc
```

## Interview tips

- Answer on two axes - **layer** (4 versus 7) and **scope** (regional versus global) - and place all four products on them, including Traffic Manager as DNS-only. That structure covers every variant of the question.
- Say **Application Gateway is layer 7** without hesitation, and justify it by what layer 7 enables: TLS termination, host/path routing, header rewriting, cookie affinity, and WAF.
- Give the production combination - Front Door globally, Application Gateway regionally - and then volunteer the bypass risk: restrict the gateway's NSG to the `AzureFrontDoor.Backend` service tag and validate `X-Azure-FDID`, or the edge WAF is optional for an attacker.
- On certificates, say the cert belongs on the **HTTPS listener** and should come from **Key Vault** so renewal is automatic. Distinguish that from the backend HTTP settings' **trusted root** for end-to-end TLS - the two get confused constantly.
- Have the expired-certificate runbook ready: renew in Key Vault, confirm the listener serves it, check the full chain, check the backend trust if end-to-end, then add a 30-day expiry alert.
- For blocking a domain, separate inbound (listener host names plus WAF custom rules) from outbound (Azure Firewall FQDN rules). Reaching for the wrong product here is a common mistake.
- Say WAF goes into **Detection** mode first. Deploying straight to Prevention against a live application causes an outage.
- For the 404/502-with-healthy-backends scenario, walk the layers in order - listener host match, path rule, real backend health with the probe's own host and status match, backend HTTP settings, NSG/subnet reachability, then rewriting - and name diagnostic logs plus a KQL query as how you would actually find it. See [how do you design an Azure virtual network](./how-do-you-design-an-azure-virtual-network.md), [what is Azure Kubernetes Service (AKS)](./what-is-azure-kubernetes-service-aks.md), [what is a layer 4 versus a layer 7 load balancer](../scalability-and-high-availability/what-is-the-difference-between-a-layer-4-and-a-layer-7-load-balancer.md), and [protecting a public web application against the OWASP Top 10 and DDoS](../network-security/how-do-you-protect-a-public-web-application-against-the-owasp-top-10-and-ddos.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you troubleshoot a DNS problem in production?]] (`#435`): [How do you troubleshoot a DNS problem in production?](../cloud-engineering/how-do-you-troubleshoot-a-dns-problem-in-production.md)
- [[How do you debug a Kubernetes Ingress that is not routing traffic?]] (`#406`): [How do you debug a Kubernetes Ingress that is not routing traffic?](../kubernetes/how-do-you-debug-a-kubernetes-ingress-that-is-not-routing-traffic.md)
- [[What happens when a Kubernetes control-plane node or etcd fails?]] (`#448`): [What happens when a Kubernetes control-plane node or etcd fails?](../kubernetes/what-happens-when-a-kubernetes-control-plane-node-or-etcd-fails.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Azure Engineering](./README.md) · [All topics](../README.md)
