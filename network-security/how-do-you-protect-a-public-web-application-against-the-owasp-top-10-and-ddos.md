---
title: "How do you protect a public web application against the OWASP Top 10 and DDoS?"
id: 492
category: "Network Security"
difficulty: "Advanced"
tags:
  - devops
  - network-security
  - interview-questions
  - devsecops
  - api-gateway-and-service-mesh
---

# How do you protect a public web application against the OWASP Top 10 and DDoS?

**Short answer:** Two different problems, two different sets of controls, and neither is solved by a single product. The **OWASP Top 10** is mostly about application logic - broken access control, injection, insecure design, misconfiguration - so the primary controls are in the software: parameterised queries, server-side authorisation on every request, validated input, secure defaults, dependency scanning, and secrets management. A **WAF** at the edge is a valuable second layer that blocks known attack patterns and buys you time to patch, but it cannot fix broken access control, which is the number one category. **DDoS** is a capacity and traffic-shaping problem: absorb volumetric floods at a **CDN and anycast edge** (CloudFront/Front Door with Shield or the equivalent), use **rate limiting and bot management** for layer 7 floods, autoscale with a circuit breaker so you degrade rather than collapse, and make sure the origin is **only reachable through the edge** - otherwise an attacker bypasses every control you just paid for.

## Detail

### Mapping the OWASP Top 10 to actual controls

| Category                            | Primary control (in the application)                                                         | Secondary (platform / WAF)                                                   |
| ----------------------------------- | -------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **A01 Broken access control**       | Server-side authorisation on every request; deny by default; never trust client-supplied IDs | **WAF cannot fix this.** Detect with logging on 403 spikes and IDOR patterns |
| **A02 Cryptographic failures**      | TLS everywhere, strong ciphers, no secrets in code, encrypt at rest                          | Load balancer TLS policy, HSTS, certificate automation                       |
| **A03 Injection**                   | **Parameterised queries / prepared statements**, output encoding, no shell interpolation     | WAF SQLi/XSS rule sets, CSP header                                           |
| **A04 Insecure design**             | Threat modelling, rate limits on business logic, abuse cases in the design                   | Quotas at the API gateway                                                    |
| **A05 Security misconfiguration**   | Hardened defaults, no default credentials, minimal features enabled                          | IaC scanning, CIS benchmarks, admission policy                               |
| **A06 Vulnerable components**       | SCA in CI, patch cadence, SBOM                                                               | Image scanning, virtual patching in the WAF while you fix                    |
| **A07 Auth failures**               | MFA, proper session handling, lockout/backoff, no credential stuffing viability              | WAF credential-stuffing and bot rules, rate limits on `/login`               |
| **A08 Software/data integrity**     | Signed artefacts, verified dependencies, no untrusted deserialisation                        | Admission control verifying signatures                                       |
| **A09 Logging/monitoring failures** | Log auth events, log access decisions, alert on anomalies                                    | WAF logs to SIEM, GuardDuty-style detection                                  |
| **A10 SSRF**                        | Allowlist outbound destinations, block link-local, validate URLs server-side                 | Egress firewall with FQDN rules, **IMDSv2 required**                         |

Two points to make explicitly, because they separate a real answer from a product pitch. First, **A01 is the top category and a WAF cannot see it** - a request to `/api/orders/12345` looks identical whether or not that order belongs to you, so authorisation must be in the application. Second, the WAF's genuine superpower is **virtual patching**: when a CVE lands in a framework you cannot redeploy for three days, a targeted WAF rule blocks exploitation while you fix properly. Framing the WAF as time-buying rather than as protection is the mature position.

### DDoS: three layers, three answers

```text
L3/L4 volumetric (SYN flood, UDP amplification, 2 Tbps of nothing)
  -> absorbed by the provider's scrubbing at the edge: AWS Shield, Azure DDoS Protection,
     Cloud Armor. Anycast spreads the load across many PoPs. You mostly do not see these.

L7 application floods (HTTP GET/POST storms, cache-busting query strings, expensive endpoints)
  -> rate limiting per IP/session/token, bot management, CAPTCHA/JS challenge, caching,
     request-size limits, and killing expensive unauthenticated endpoints.

Application-layer abuse (credential stuffing, scraping, inventory hoarding, API misuse)
  -> authentication, quotas per API key, anomaly detection, and business-logic limits.
```

For the frequent scenario _"there is a DDoS on your cluster nodes or services consuming 100% of resources - what do you do to recover and prevent it?"_, answer in two halves:

**Recover**: identify the pattern from the edge logs (source IPs, ASNs, user agents, target path); apply an immediate WAF rule or rate limit at the edge, geo-block if the traffic is clearly from a region you do not serve; enable challenge/CAPTCHA on the affected path; scale out if it is genuinely absorbable and shed load if it is not (return 429 with `Retry-After` rather than falling over); protect the tiers behind - connection limits and a queue in front of the database, circuit breakers so timeouts do not cascade; and engage the provider's DDoS response team, which is included with the paid tiers.

**Prevent**: put a CDN/anycast edge in front permanently and **lock the origin to the edge only**; enable the managed DDoS tier so protection is automatic rather than reactive; keep rate limits and bot rules as standing configuration; cache aggressively so the origin sees a fraction of requests; autoscale with sensible ceilings so a flood cannot bankrupt you (a cost-DDoS is real); design endpoints so nothing expensive is unauthenticated; and run a game day so the runbook has been used before it matters.

### The bypass problem - the highest-value single point

_"An instance has a security group, a WAF, and DDoS protection - will that combination protect it from a bot attack?"_ The answer is **not necessarily**, and the reason is architecture: if the instance or load balancer is directly reachable on the internet, an attacker who resolves its address can skip the CDN and the WAF entirely. So the controls only work if:

- The origin's security group / NSG accepts traffic **only** from the CDN's address ranges or service tag (`AzureFrontDoor.Backend`, CloudFront's managed prefix list).
- A shared secret header is validated (`X-Azure-FDID`, or a custom header the edge injects), so someone using the CDN's own IPs cannot proxy around it.
- The origin has no public DNS name, or its address is not discoverable from historical DNS records and certificate transparency logs (which is how attackers usually find origins).

That answer - "the products are fine, the topology is the vulnerability" - is what a senior interviewer is listening for. Similarly, "do I need a network ACL when I have a security group?" and "will DDoS protection stop a bot?" are both really questions about layers and coverage, not about product features.

### Bots specifically

Volumetric DDoS and bots are different problems: bots are often **low volume and highly targeted** - credential stuffing at 5 requests per second from thousands of residential IPs looks like normal traffic to a rate limiter keyed on IP. The controls are behavioural: fingerprinting and managed bot rule sets, rate limits keyed on **session or account** rather than IP, progressive challenges (JS challenge → CAPTCHA → block), device attestation for mobile clients, honeypot fields, and monitoring of business metrics (login failure ratio, gift-card checks per minute) rather than request counts. Also allow the good bots - publish `robots.txt`, verify search-engine crawlers by reverse DNS rather than user agent.

### WAF operations, which is where people go wrong

- **Detection mode first.** Deploy the managed rule set in count/detection mode, review the logs for false positives against real traffic, tune exclusions, then switch to prevention. Going straight to blocking on a live application is a self-inflicted outage - and the WAF gets disabled permanently after the first one.
- **Tune with data.** Managed rules fire on legitimate traffic (rich text editors trip XSS rules, base64 payloads trip SQLi rules). Exclude specific rule IDs for specific paths or parameters, not the whole rule set.
- **Custom rules** for what managed rules cannot know: rate limits per path, geo restrictions, allowlisting your own IP ranges for admin paths, blocking a specific abusive ASN, and size limits on request bodies.
- **Log to a SIEM** and alert on blocked-request spikes; the WAF's logs are also your best source during an incident.
- **Test it.** A staging WAF with the same rules, plus periodic verification that a known-bad request is actually blocked, so you find out the WAF was accidentally in detection mode before an attacker does.

### The rest of the stack

Headers and platform controls that cost nothing: **HSTS**, **CSP** (the real mitigation for XSS), `X-Content-Type-Options`, `Referrer-Policy`, secure cookies with `HttpOnly`/`SameSite`, and CORS configured deliberately rather than `*`. Then an **API gateway** for authentication, per-key quotas, and request validation before traffic reaches the service; **egress control** (FQDN-based firewall) so an SSRF or a compromised container cannot phone home; and **IMDSv2 required** on instances so SSRF cannot lift cloud credentials. And run the whole thing through a pipeline that does SAST, SCA, secret scanning, and IaC scanning, so the classes a WAF cannot see get caught before deployment.

## Example

```hcl
# Edge WAF: managed rules in COUNT first, plus custom rate limiting
resource "aws_wafv2_web_acl" "edge" {
  name  = "edge-protection"
  scope = "CLOUDFRONT"
  default_action { allow {} }

  rule {
    name     = "AWSManagedCommonRuleSet"
    priority = 10
    override_action { count {} } # <- COUNT first; switch to none{} after tuning
    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesCommonRuleSet"
        rule_action_override { # tune specific rules, not the whole set
          name           = "SizeRestrictions_BODY"
          action_to_use { count {} }
        }
      }
    }
    visibility_config { cloudwatch_metrics_enabled = true  metric_name = "common"  sampled_requests_enabled = true }
  }

  rule {
    name     = "RateLimitLogin"
    priority = 20
    action { block {} }
    statement {
      rate_based_statement {
        limit              = 100 # per 5 minutes
        aggregate_key_type = "IP"
        scope_down_statement {
          byte_match_statement {
            positional_constraint = "STARTS_WITH"
            search_string         = "/login"
            field_to_match { uri_path {} }
            text_transformation { priority = 0  type = "LOWERCASE" }
          }
        }
      }
    }
    visibility_config { cloudwatch_metrics_enabled = true  metric_name = "ratelimit"  sampled_requests_enabled = true }
  }

  rule { # bot control: challenge rather than block, to avoid false positives
    name     = "BotControl"
    priority = 30
    override_action { none {} }
    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesBotControlRuleSet"
        managed_rule_group_configs {
          aws_managed_rules_bot_control_rule_set { inspection_level = "TARGETED" }
        }
      }
    }
    visibility_config { cloudwatch_metrics_enabled = true  metric_name = "bots"  sampled_requests_enabled = true }
  }
}
```

```hcl
# The control that makes all the others real: the origin accepts ONLY the edge
resource "aws_security_group_rule" "origin_from_cloudfront_only" {
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.alb.id
  prefix_list_ids   = [data.aws_ec2_managed_prefix_list.cloudfront.id] # not 0.0.0.0/0
}

resource "aws_cloudfront_distribution" "app" {
  # ... origin config ...
  origin {
    domain_name = aws_lb.public.dns_name
    origin_id   = "alb"
    custom_header { # shared secret: prevents proxying via CloudFront's own IPs
      name  = "X-Origin-Verify"
      value = var.origin_verify_secret
    }
    custom_origin_config {
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
      http_port              = 80
      https_port             = 443
    }
  }
  web_acl_id = aws_wafv2_web_acl.edge.arn
}
# ...and the ALB listener rule rejects any request without that header.
```

```bash
# During an attack: find the pattern, then act on it
aws logs start-query --log-group-name aws-waf-logs-edge \
  --start-time $(date -d '-15 min' +%s) --end-time $(date +%s) \
  --query-string 'fields httpRequest.clientIp, httpRequest.uri, httpRequest.country,
                          terminatingRuleId, action
                  | filter action = "BLOCK" or action = "COUNT"
                  | stats count(*) as n by httpRequest.clientIp, httpRequest.uri
                  | sort n desc | limit 20'

# Shed load rather than fall over - 429 with Retry-After beats a timeout
curl -sS -o /dev/null -w '%{http_code}\n' https://app.example.com/api/search

# Verify the WAF is actually blocking (and is not silently in count mode)
curl -s -o /dev/null -w '%{http_code}\n' "https://app.example.com/?q=1%27%20OR%20%271%27=%271"
#   expect 403. A 200 means detection mode, a bypass, or a rule that never matched.
```

## Interview tips

- Separate the two problems in your first sentence: OWASP is mostly application logic, DDoS is capacity and traffic shaping. Answering them as one thing with "we use a WAF" is the failure mode.
- Say plainly that **broken access control is number one and a WAF cannot fix it** - the request looks legitimate. Then frame the WAF's real value as a second layer plus **virtual patching** while you fix properly.
- Map at least four Top 10 categories to concrete controls (parameterised queries, server-side authorisation, SCA in CI, egress control plus IMDSv2 for SSRF). Specificity beats listing the ten names.
- For DDoS, give the three layers - volumetric at the anycast edge, L7 floods with rate limiting and bot management, application abuse with quotas and anomaly detection - and add graceful degradation: 429 with `Retry-After` and circuit breakers beat collapsing.
- Volunteer the **origin bypass** point when asked whether a security group plus WAF plus DDoS protection is enough. "The products are fine; the topology is the vulnerability" - lock the origin to the CDN's prefix list or service tag and validate a shared header. This is the strongest thing you can say in this answer.
- Distinguish bots from volumetric attacks: bots are low-volume and targeted, so IP-based rate limiting misses them and you need behavioural controls plus rate limits keyed on session or account.
- Insist on **detection mode first** and tuning with real traffic, and explain the consequence of not doing it - a false-positive outage, after which the WAF gets disabled forever.
- Mention the free wins: HSTS, CSP as the real XSS mitigation, secure cookies, deliberate CORS, and an API gateway doing authentication and quotas before traffic reaches the service. Then say the pipeline catches the classes the WAF cannot see. See [what is a web application firewall (WAF)](./what-is-a-web-application-firewall-waf.md), [designing defence in depth for a cloud network](./how-do-you-design-defence-in-depth-for-a-cloud-network.md), [what is API security](../api-gateway-and-service-mesh/what-is-api-security.md), [what is rate limiting](../api-gateway-and-service-mesh/what-is-rate-limiting.md), and [designing a system to degrade gracefully under overload](../scalability-and-high-availability/how-do-you-design-a-system-to-degrade-gracefully-under-overload.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do you harden a container image and a Dockerfile?]] (`#441`): [How do you harden a container image and a Dockerfile?](../docker/how-do-you-harden-a-container-image-and-a-dockerfile.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Network Security](./README.md) · [All topics](../README.md)
