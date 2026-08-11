---
title: "How do you troubleshoot a DNS problem in production?"
id: 435
category: "Cloud Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - cloud-engineering
  - interview-questions
  - network-security
  - incident-management
  - scalability-and-high-availability
---

# How do you troubleshoot a DNS problem in production?

**Short answer:** Query the authoritative server directly and compare it with what clients are actually getting - the gap between those two answers is the whole diagnosis. `dig +trace` walks the delegation from the root, `dig @ns1.provider.net name` gives you the authoritative truth, and `dig name` from an affected client shows what the resolver chain is really returning, including a cached stale record. Then classify: **a wrong record** (fix it, and wait out the TTL), **a delegation or NS problem** (registrar or parent zone), **propagation and caching** (nothing to fix but time, which is why low TTLs are a change-management tool), **DNSSEC validation failure** (SERVFAIL everywhere, and the scariest of the set), or **not-DNS-at-all** (resolution is fine and the target is unhealthy). The prevention that matters more than any of the debugging: manage records as code, lower the TTL **before** a planned change, and monitor resolution from outside your network.

## Detail

### The four-command diagnosis

1. **What does authority say?** `dig @<authoritative-ns> shop.example.com A +norecurse` - bypasses every cache and tells you what the zone actually contains right now. If this is wrong, the problem is your record, full stop.
2. **What is the delegation?** `dig +trace shop.example.com` follows root → TLD → your nameservers, revealing a broken delegation, an inconsistent NS set, or a lame server. `dig NS example.com @a.gtld-servers.net` compares the parent's view with your own zone's NS records - a mismatch is a classic and confusing failure.
3. **What do clients get?** `dig shop.example.com` from an affected host, plus `dig @8.8.8.8` and `@1.1.1.1` for a third-party view. A stale answer here with correct authority means caching, and `dig` prints the remaining TTL so you know exactly how long you are waiting.
4. **Is it even DNS?** If the name resolves to the right address, stop looking at DNS: test TCP reachability and the application. "It must be DNS" is right often enough to be a meme and wrong often enough to waste an hour.

### Classify the failure

- **Wrong or missing record.** Someone changed an A/CNAME/ALIAS, a Terraform apply removed a record, or a new deployment created a new load balancer and the record still points at the old one. Fix the record; then the wait is bounded by the TTL you set _before_ the change.
- **Delegation and registrar problems.** NS records at the registrar not matching the zone, an expired domain, a nameserver that no longer serves the zone (lame delegation), or a missing glue record. These produce total, sudden, hard-to-explain outages and are outside your cloud console.
- **Propagation and caching.** There is no "propagation" mechanism - only caches expiring. A record with a 24-hour TTL will take up to 24 hours to disappear from resolvers, and some resolvers and client libraries ignore short TTLs. Negative caching (the SOA minimum TTL) means a **failed** lookup can also be cached, which is why fixing a missing record does not always give instant relief.
- **DNSSEC.** An expired signature, a broken chain of trust after a key rollover, or a DS record that no longer matches gives `SERVFAIL` from validating resolvers while non-validating ones work - a symptom that looks like partial insanity. `dig +dnssec +cd` (checking disabled) distinguishes it in one command: if `+cd` works and the normal query fails, it is DNSSEC.
- **Resolver-side problems.** A client's `/etc/resolv.conf`, search-domain surprises, a full conntrack table or UDP packet loss, responses over 512 bytes failing where TCP fallback or EDNS is blocked by a middlebox, or an internal resolver that cannot reach forwarders. In Kubernetes this is its own topic - see [how do you debug DNS resolution failures inside a Kubernetes cluster](../kubernetes/how-do-you-debug-dns-resolution-failures-inside-a-kubernetes-cluster.md).
- **Split-horizon confusion.** A private hosted zone resolving internally and a public zone resolving differently is by design, but it means "works from my laptop, fails in the VPC" is expected rather than a bug. Always say **from where** you are testing.

### During the incident

Mitigate before you perfect. If a record is wrong, correct it and simultaneously reduce blast radius: publish the corrected record with a short TTL, and if the intended target is unavailable, fail over to a known-good one rather than waiting for a fix. If the failure is at the provider level, remember DNS is one of the few services where a **second provider** is a genuine resilience strategy (secondary nameservers on a different vendor), because a DNS outage takes everything with it regardless of how healthy your application is. Communicate carefully: clients see the failure for as long as their caches hold, so a status update saying "fixed" while users still see errors damages trust - say "corrected; you may see cached failures for up to N minutes", using the actual TTL.

### Prevention, which is where the real answer lives

- **Records as code.** Terraform or `external-dns`, reviewed in a pull request, so an accidental deletion is visible and revertible - and so you can tell what changed and when. A manual console edit during an incident is how the next incident starts.
- **Lower the TTL before planned changes** (to 60 seconds, a day ahead) and raise it afterwards. This is a scheduled activity, not a permanent setting - permanently low TTLs increase query volume and cost, and buy nothing until you need them.
- **Know your failover time honestly.** DNS-based failover is TTL plus resolver behaviour plus client caching - minutes, not seconds. If you need seconds, you need Anycast or a global load balancer, and saying so is what distinguishes an engineer from a diagram. See [how do you manage DNS and global traffic routing](./how-do-you-manage-dns-and-global-traffic-routing.md).
- **Health-checked routing** (Route 53 health checks, Traffic Manager probes) so failover does not depend on a human editing a record at 3 a.m.
- **Monitor from outside**: resolution from multiple geographies, the answer's correctness (not just that a response came back), delegation consistency, DNSSEC signature expiry, and domain and certificate expiry dates. Domain expiry is the most embarrassing outage in this category and the easiest to prevent.

## Example

```bash
# 1. Authoritative truth - no caches involved
dig @ns-1234.awsdns-56.org shop.example.com A +norecurse +short
# 203.0.113.10                              <- this is what the zone really says

# 2. What clients are getting, and how long they will keep getting it
dig shop.example.com A
# shop.example.com.  842  IN  A  198.51.100.4   <- WRONG, and cached for 842 more seconds
dig @8.8.8.8 shop.example.com +short           # a second opinion from outside

# 3. Delegation: does the parent agree with the zone?
dig +trace shop.example.com | tail -8
dig NS example.com @a.gtld-servers.net +short  # parent's view
dig NS example.com @ns-1234.awsdns-56.org +short  # zone's own view - they must match

# 4. SERVFAIL everywhere? Test whether DNSSEC validation is the cause.
dig shop.example.com                    # status: SERVFAIL
dig shop.example.com +cd                # checking disabled: NOERROR -> it IS DNSSEC
dig example.com DNSKEY +dnssec | grep -c RRSIG

# 5. Is it DNS at all, or a healthy name pointing at a broken thing?
getent hosts shop.example.com && nc -zv 203.0.113.10 443
curl -sv --resolve shop.example.com:443:203.0.113.10 https://shop.example.com/healthz
#   ^ bypasses DNS entirely: if this works, DNS was never the problem

# 6. Client-side reality check (and the Kubernetes/hostNetwork trap)
cat /etc/resolv.conf; systemd-resolve --status 2>/dev/null | head -20
```

```hcl
# Prevention: records as code, health-checked failover, TTL as a deliberate choice
resource "aws_route53_record" "shop" {
  zone_id = aws_route53_zone.public.zone_id
  name    = "shop.example.com"
  type    = "A"

  alias {                                  # alias: works at the apex, no per-query charge
    name                   = aws_lb.prod.dns_name
    zone_id                = aws_lb.prod.zone_id
    evaluate_target_health = true          # failover without a human editing records
  }
  set_identifier = "primary"
  failover_routing_policy { type = "PRIMARY" }
}

resource "aws_route53_record" "shop_dr" {
  zone_id        = aws_route53_zone.public.zone_id
  name           = "shop.example.com"
  type           = "A"
  ttl            = 60                      # lowered ahead of the planned cutover
  records        = [var.dr_ip]
  set_identifier = "secondary"
  failover_routing_policy { type = "SECONDARY" }
  health_check_id = aws_route53_health_check.dr.id
}
```

```text
The change-management habit that prevents most DNS incidents

  T-24h  lower TTL 3600 -> 60 on the records you will change (and only those)
  T-0    change the record; verify authority immediately with dig @ns
  T+2m   verify from three public resolvers and two geographies
  T+2h   confirm clean, then raise the TTL back to 3600
  Never: edit records in the console during an incident and forget to update Terraform
         (the next apply will silently revert your fix)
```

## Interview tips

- Lead with the comparison: authoritative answer versus what clients receive. That single framing organises the entire diagnosis and is what interviewers are listening for.
- Know `dig +trace`, `dig @<ns> +norecurse`, and `dig +cd` and what each proves. Naming `+cd` to isolate DNSSEC is a strong differentiator.
- Say there is no propagation, only cache expiry - and that negative caching means a fixed missing record can still fail for a while. It corrects a very common misconception.
- Bring up lowering TTL **before** a planned change as a scheduled activity, and raising it afterwards. It shows you plan changes rather than react to them.
- Be honest about DNS failover timing: TTL plus resolver plus client caching means minutes. If seconds are required, that is Anycast or a global load balancer.
- Mention split-horizon and always stating **where** you tested from. "Works from my laptop, fails in the VPC" is expected behaviour with a private hosted zone, not a fault.
- Domain expiry, DNSSEC signature expiry, and delegation drift are the three catastrophic-but-preventable causes. Monitoring them is cheap and almost nobody does it.
- Close on records as code, and the specific trap of fixing a record in the console during an incident so the next Terraform apply reverts it. That detail lands because everyone has seen it happen. See [what happens when a user opens your application in a browser](../network-security/what-happens-when-a-user-opens-your-application-in-a-browser.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot Docker networking between containers?]] (`#415`): [How do you troubleshoot Docker networking between containers?](../docker/how-do-you-troubleshoot-docker-networking-between-containers.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Engineering](./README.md) · [All topics](../README.md)
