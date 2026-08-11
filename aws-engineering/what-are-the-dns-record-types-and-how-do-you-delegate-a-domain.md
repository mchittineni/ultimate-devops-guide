---
title: "What are the DNS record types, and how do you delegate a domain?"
id: 481
category: "AWS Engineering"
difficulty: "Beginner"
tags:
  - devops
  - aws-engineering
  - interview-questions
  - network-security
  - cloud-engineering
---

# What are the DNS record types, and how do you delegate a domain?

**Short answer:** The records you actually use: **A** (hostname → IPv4), **AAAA** (→ IPv6), **CNAME** (hostname → another hostname, and it cannot coexist with other records at the same name or exist at the zone apex), **MX** (mail servers, with a priority), **TXT** (arbitrary text - SPF, DKIM, DMARC, and domain-ownership verification), **NS** (delegation: which nameservers are authoritative for a zone), **SOA** (zone metadata), **SRV** (service, port, and target - what Kubernetes headless Services use), **PTR** (reverse lookup), and **CAA** (which certificate authorities may issue for the domain). Route 53 adds a non-standard **alias** record - it looks like an A record to clients but points at an AWS resource (ALB, CloudFront, S3 website, another record in the zone), which is how you solve the "you cannot CNAME the apex" problem, and it is **free to query**. Delegation is done with **NS records**: whoever holds the parent zone points a subdomain's NS records at your nameservers, and from that moment your zone is authoritative for it.

## Detail

### The records, and the traps in each

| Record               | Maps                                          | Trap worth knowing                                                                                                                           |
| -------------------- | --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **A**                | name → IPv4                                   | Multiple A records for one name = simple round-robin, with no health awareness                                                               |
| **AAAA**             | name → IPv6                                   | Publishing AAAA when your path is IPv4-only breaks dual-stack clients                                                                        |
| **CNAME**            | name → another **name**                       | **Cannot exist at the zone apex**, and cannot coexist with any other record type at the same name. Each lookup costs an extra resolution hop |
| **MX**               | domain → mail servers                         | Has a **priority** (lower wins). Must point at a hostname, never an IP                                                                       |
| **TXT**              | name → text                                   | SPF, DKIM, DMARC, and ownership proofs. 255-character string limit per string (concatenated)                                                 |
| **NS**               | zone → nameservers                            | **The delegation mechanism.** Must match at parent and child                                                                                 |
| **SOA**              | zone metadata                                 | Serial, refresh, and the **negative caching TTL** - which is why a typo can be cached as NXDOMAIN longer than you expect                     |
| **SRV**              | service → host + **port** + priority + weight | How Kubernetes headless Services and SIP/LDAP discovery work                                                                                 |
| **PTR**              | IP → name                                     | Reverse DNS; needed for mail deliverability, controlled by whoever owns the IP block                                                         |
| **CAA**              | domain → allowed CAs                          | Cheap control that stops another CA issuing a certificate for your domain                                                                    |
| **Alias** (Route 53) | name → AWS resource                           | Not standard DNS. Works at the apex, resolves to the target's current IPs, **free**, and health-check aware                                  |

### The apex problem, and the alias answer

The RFC says a CNAME cannot coexist with other records at the same name, and a zone apex (`example.com`) must have NS and SOA records - so `example.com CNAME my-alb...` is invalid. Every provider solves this with a proprietary record: Route 53 calls it an **alias**, others call it ALIAS or ANAME or flattened CNAME. Route 53 aliases can target an ALB/NLB, CloudFront, API Gateway, S3 website endpoints, Global Accelerator, another record in the same hosted zone, and a few more. Two extra reasons to prefer alias over CNAME even where CNAME would work: alias queries are **not charged**, and an alias to a load balancer automatically tracks the balancer's changing IPs and its health.

So: **`www.example.com` → CNAME or alias to the ALB is fine; `example.com` → must be an alias** (or an A record you maintain, which you should not for an ALB whose IPs change).

### Delegating a domain, including from an external registrar

The "we bought the domain at GoDaddy and want to use Route 53" question, step by step:

1. Create a **public hosted zone** for `example.com` in Route 53. It is created with four **NS** records and an **SOA**.
2. Copy those four nameservers into the **registrar's** nameserver settings (at GoDaddy, Namecheap, wherever the domain is registered). This is the delegation - the registrar updates the parent zone (`.com`) to point at your nameservers.
3. Recreate your records inside the hosted zone **before** switching, so nothing goes dark at cutover.
4. Wait for propagation - bounded by the parent zone's TTL for the NS records (often 24-48 hours for a registrar change, though usually much faster in practice).
5. Verify with `dig NS example.com @8.8.8.8` and `dig +trace`.

Do **not** copy the nameservers from a _different_ hosted zone for the same domain - creating two hosted zones for one domain and delegating to the wrong one is the single most common Route 53 mistake.

**Subdomain delegation** is the same mechanism one level down and is how you give a team or another account their own zone: create a hosted zone for `dev.example.com` (possibly in another AWS account), then in the **parent** zone add an `NS` record for `dev` listing that zone's nameservers. This is also the answer to "how do you configure subdomains registered with an external registrar?" - the parent does not have to be in Route 53 at all; it just needs the NS record.

### Private hosted zones, and public versus private

A **private hosted zone** is associated with one or more VPCs and resolves only from inside them, which is how you give internal services names (`db.internal.example.com`) that do not exist publicly. It requires `enableDnsSupport` and `enableDnsHostnames` on the VPC. **Split-horizon** DNS - the same name resolving differently inside and outside - is achieved by having both a public and a private zone for the same domain; the private one wins for queries from associated VPCs. For on-premises resolution in both directions you add **Route 53 Resolver** inbound and outbound endpoints with forwarding rules.

### TTL: what it is for and how to use it during a change

TTL is how long a resolver may cache the answer. The operational pattern that matters: **lower the TTL well in advance of a planned change** (to 60 seconds, at least one old-TTL period before), make the change, confirm, then raise it back. A record sitting at TTL 86400 cannot be moved quickly no matter what you do, because caches worldwide are entitled to hold the old answer for a day. Low TTLs cost more queries and add a little latency; high TTLs are cheaper and faster but slow to change. Also remember **negative caching** (from the SOA) applies to NXDOMAIN answers, and that some clients - notably older JVMs - cache DNS forever regardless of TTL, which is why `networkaddress.cache.ttl` appears in every failover runbook.

### Routing policies, briefly

Records can carry a policy: **simple**, **weighted** (a percentage split - the DNS-level canary), **latency-based** (send users to the lowest-latency region), **failover** (primary/secondary driven by health checks), **geolocation** and **geoproximity**, and **multivalue answer** (several healthy IPs, with health checks). The failover mechanism people ask about - "one IP becomes unreachable, what happens?" - depends entirely on **health checks**: plain multiple A records keep handing out the dead address, whereas failover or multivalue-with-health-checks stops returning it. Say that; assuming DNS notices failures on its own is a common misconception. For deeper coverage of the policies see [managing DNS and global traffic routing](../cloud-engineering/how-do-you-manage-dns-and-global-traffic-routing.md).

### Certificates and DNS

Two links worth knowing: **ACM validates a certificate by DNS** (a CNAME it asks you to create, which then enables automatic renewal - leave the record in place or renewals fail), and **CAA** records restrict which CAs may issue for your domain. For multiple subdomains, either a wildcard (`*.example.com`, one level only) or a SAN certificate listing each name - and a wildcard does **not** cover the apex or a second level (`a.b.example.com`), which catches people out.

## Example

```hcl
# Alias at the apex (CNAME is illegal there), CNAME for www
resource "aws_route53_zone" "main" { name = "example.com" }

resource "aws_route53_record" "apex" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "example.com"
  type    = "A"
  alias { # not a real A record: tracks the ALB's IPs, free to query
    name                   = aws_lb.public.dns_name
    zone_id                = aws_lb.public.zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "www" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "www.example.com"
  type    = "CNAME"
  ttl     = 300
  records = [aws_lb.public.dns_name]
}

# Mail: MX with priorities, plus the three TXT records that make mail work
resource "aws_route53_record" "mx" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "example.com"
  type    = "MX"
  ttl     = 3600
  records = ["10 mail1.example.com", "20 mail2.example.com"] # lower = preferred
}

resource "aws_route53_record" "spf_dmarc" {
  for_each = {
    "example.com"        = "v=spf1 include:_spf.google.com -all"
    "_dmarc.example.com" = "v=DMARC1; p=reject; rua=mailto:dmarc@example.com"
  }
  zone_id = aws_route53_zone.main.zone_id
  name    = each.key
  type    = "TXT"
  ttl     = 3600
  records = [each.value]
}

resource "aws_route53_record" "caa" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "example.com"
  type    = "CAA"
  ttl     = 3600
  records = ["0 issue \"amazon.com\"", "0 issuewild \"amazon.com\""] # only ACM may issue
}
```

```hcl
# Subdomain delegation: the child zone lives elsewhere (another team, another account)
resource "aws_route53_zone" "dev" { name = "dev.example.com" } # in the dev account

resource "aws_route53_record" "dev_delegation" {               # in the PARENT zone
  zone_id = aws_route53_zone.main.zone_id
  name    = "dev.example.com"
  type    = "NS"
  ttl     = 172800
  records = aws_route53_zone.dev.name_servers # this is the delegation
}

# Private hosted zone: internal names, resolvable only inside the VPCs
resource "aws_route53_zone" "internal" {
  name = "internal.example.com"
  vpc { vpc_id = aws_vpc.prod.id }
  vpc { vpc_id = aws_vpc.shared.id }
}
```

```bash
# Verify delegation from the top down - this is the command that ends arguments
dig +trace example.com
dig NS example.com @8.8.8.8 +short            # what the world thinks is authoritative
dig NS example.com @ns-123.awsdns-45.com +short   # what YOUR zone says (must match)

# Is the apex an alias, and where does it point?
dig A example.com +short
aws route53 list-resource-record-sets --hosted-zone-id Z123 \
  --query "ResourceRecordSets[?Name=='example.com.'].[Type,AliasTarget.DNSName]" --output table

# TTL before a planned change: lower it, wait a full old-TTL period, then change
dig +noall +answer www.example.com            # shows the current TTL counting down
aws route53 change-resource-record-sets --hosted-zone-id Z123 --change-batch '{
  "Changes":[{"Action":"UPSERT","ResourceRecordSet":{
    "Name":"www.example.com","Type":"CNAME","TTL":60,
    "ResourceRecords":[{"Value":"old-alb-123.eu-west-1.elb.amazonaws.com"}]}}]}'

# The classic mistake: two hosted zones for one domain, delegated to the wrong one
aws route53 list-hosted-zones --query "HostedZones[?Name=='example.com.'].[Id,Config.PrivateZone]"
```

## Interview tips

- Run through the record types with one purpose each, and attach the trap to each: CNAME cannot live at the apex or beside other records; MX has priorities and must point at a name; TXT carries SPF/DKIM/DMARC; NS is delegation; SRV carries a port.
- Explain the apex problem and Route 53 **alias** as the answer, including the two bonuses - free queries and health-aware targeting of a load balancer whose IPs change. This is the highest-value single fact in the topic.
- For the external-registrar question, give the ordered steps: create the hosted zone, copy **its** four nameservers to the registrar, recreate records before cutover, then verify with `dig +trace`. Warn about the two-hosted-zones mistake.
- Describe subdomain delegation as an NS record in the parent pointing at the child's nameservers, and note the parent does not need to be in Route 53. That covers cross-account and cross-provider setups in one sentence.
- Cover private hosted zones and split-horizon DNS, plus Route 53 Resolver endpoints for on-premises resolution in both directions.
- On TTL, give the operational pattern rather than a definition: lower it in advance of a change, wait a full old-TTL period, change, verify, raise it back. Mention negative caching and JVM DNS caching as the two things that make failovers appear not to work.
- If routing policies come up, name them and then make the key point: DNS does not notice failures by itself - **health checks** are what stop a dead address being handed out.
- Add the certificate links - ACM's DNS validation CNAME must stay in place for renewals, CAA restricts which CAs may issue, and a wildcard covers one level only. See [managing DNS and global traffic routing](../cloud-engineering/how-do-you-manage-dns-and-global-traffic-routing.md), [troubleshooting a DNS problem in production](../cloud-engineering/how-do-you-troubleshoot-a-dns-problem-in-production.md), [managing TLS certificates in production](../network-security/how-do-you-manage-tls-certificates-in-production.md), and [what happens when a user opens your application in a browser](../network-security/what-happens-when-a-user-opens-your-application-in-a-browser.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you troubleshoot a DNS problem in production?]] (`#435`): [How do you troubleshoot a DNS problem in production?](../cloud-engineering/how-do-you-troubleshoot-a-dns-problem-in-production.md)
- [[What is a cloud landing zone?]] (`#215`): [What is a cloud landing zone?](../cloud-engineering/what-is-a-cloud-landing-zone.md)
- [[How do you manage DNS and global traffic routing?]] (`#220`): [How do you manage DNS and global traffic routing?](../cloud-engineering/how-do-you-manage-dns-and-global-traffic-routing.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
