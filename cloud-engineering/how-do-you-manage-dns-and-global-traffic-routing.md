---
title: "How do you manage DNS and global traffic routing?"
id: 220
category: "Cloud Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - cloud-engineering
  - interview-questions
---

# How do you manage DNS and global traffic routing?

**Short answer:** Manage zones as code with short TTLs on anything used for failover, use health-checked routing policies (latency, weighted, geolocation, failover) for cross-region steering, and prefer an anycast global load balancer over DNS-based failover when you need seconds rather than minutes. Split-horizon DNS keeps internal names private, and DNSSEC plus registrar locks protect the zone itself.

## Detail

**TTL is your failover floor.** DNS-based failover cannot be faster than the record's TTL plus resolver and client caching — and some clients (notably JVMs with default settings, and some libraries) cache far longer than the TTL instructs. Use 60 seconds for failover-relevant records, accept the extra query volume, and never rely on DNS alone for sub-minute recovery.

**Routing policies and what each is for:** simple (one target), weighted (canary and blue/green splits, gradual migration between providers), latency-based (send users to the nearest healthy region), geolocation/geoproximity (data residency and localised content), failover (active-passive with health checks), and multi-value with health checks (crude client-side load spreading). Health checks are what makes any of them resilient — a routing policy without health checks happily sends traffic into a dead region.

**Anycast load balancers beat DNS failover.** A single global IP with regional backends (Google's global external Application Load Balancer, AWS Global Accelerator, Azure Front Door) reroutes within the network in seconds, with no client caching involved. The cost is another managed component and, for some, TLS termination at the edge. If your requirement is a fast RTO, this is the answer, and DNS is the coarser fallback.

**Split-horizon for internal names.** Private hosted zones resolve internal services for VPC clients only, while the same domain resolves publicly to different records. In hybrid environments this needs inbound and outbound resolvers so on-premises and cloud can resolve each other's names — a step that is missed often enough to be worth calling out.

**Protect the zone as a critical asset.** DNS takeover is a full compromise of your brand: enable registrar lock and two-person change control on the registrar, DNSSEC where your registrar and resolvers support it, CAA records to constrain which CAs may issue certificates, and monitoring for dangling records pointing at deprovisioned cloud resources — subdomain takeover is a routine bug-bounty finding.

**Manage it as code.** Zone records in Terraform or a dedicated controller (external-dns for Kubernetes), reviewed in pull requests, with drift detection. Manual record edits during incidents are how stale records survive for years; if an emergency edit happens, reconcile it back into code the same day.

## Example

```hcl
# Failover with health checks, short TTL, and a weighted canary on the primary
resource "aws_route53_health_check" "eu" {
  fqdn              = "eu.api.acme.com"
  type              = "HTTPS"
  resource_path     = "/healthz"
  failure_threshold = 2
  request_interval  = 10
}

resource "aws_route53_record" "api_primary" {
  zone_id         = aws_route53_zone.public.zone_id
  name            = "api.acme.com"
  type            = "A"
  ttl             = 60 # the floor on DNS failover time
  set_identifier  = "eu-primary"
  health_check_id = aws_route53_health_check.eu.id
  failover_routing_policy { type = "PRIMARY" }
  records = ["203.0.113.10"]
}

resource "aws_route53_record" "api_secondary" {
  zone_id        = aws_route53_zone.public.zone_id
  name           = "api.acme.com"
  type           = "A"
  ttl            = 60
  set_identifier = "us-standby"
  failover_routing_policy { type = "SECONDARY" }
  records = ["198.51.100.20"]
}

# Constrain who may issue certificates for the domain
resource "aws_route53_record" "caa" {
  zone_id = aws_route53_zone.public.zone_id
  name    = "acme.com"
  type    = "CAA"
  ttl     = 3600
  records = ["0 issue \"amazon.com\"", "0 issuewild \";\""]
}
```

## Interview tips

- "TTL plus client caching is the floor on DNS failover" is the key technical point; name the JVM caching gotcha.
- Recommend an anycast global load balancer when the RTO requirement is seconds — DNS is the coarse tool.
- Expect: "what is subdomain takeover?" — a dangling CNAME to a deprovisioned resource that an attacker can claim; monitor for it.

---

[⬅ Back to Cloud Engineering](./README.md) · [All topics](../README.md)
