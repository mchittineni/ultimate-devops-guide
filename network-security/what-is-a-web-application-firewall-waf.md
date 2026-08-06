---
title: "What is a Web Application Firewall (WAF)?"
id: 119
category: "Network Security"
difficulty: "Beginner"
tags:
  - devops
  - network-security
  - interview-questions
---

# What is a Web Application Firewall (WAF)?

**Short answer:** A WAF inspects HTTP/HTTPS traffic at layer 7 and blocks malicious requests — SQL injection, cross-site scripting, path traversal, bot abuse — before they reach the application, complementing rather than replacing secure coding.

## Detail

**How it differs from a network firewall.** A network firewall filters on IP, port, and protocol. A WAF understands HTTP: URLs, headers, cookies, and request bodies. It can tell a legitimate `POST /login` from one carrying an injection payload.

**Detection models**

- **Negative security (blocklist)** — signatures for known attack patterns. The OWASP Core Rule Set is the standard open ruleset. Easy to deploy, imperfect coverage.
- **Positive security (allowlist)** — define exactly what valid requests look like per endpoint. Stronger, but requires effort to build and maintain.
- **Behavioural / ML** — anomaly scoring against a learned baseline; catches novel attacks with more false positives.

**Typical capabilities:** OWASP Top 10 protection, rate limiting, bot management, geo-blocking, IP reputation, virtual patching (blocking exploitation of a known CVE while the real fix is developed), and request/response inspection with detailed logging.

**Deployment:** cloud-managed at the CDN edge (AWS WAF, Cloudflare, Azure Front Door), reverse proxy (ModSecurity with NGINX), or embedded as a library or sidecar.

**Operating one well.** Always start in **detection/count mode**, review what would have been blocked against real traffic, tune out false positives, then enforce. Blocking on day one will break legitimate users — file uploads, rich-text content, and API payloads trip generic rules constantly. Monitor blocked-request rates and review them; a WAF nobody looks at is theatre.

## Example

```hcl
resource "aws_wafv2_web_acl" "app" {
  name  = "app-waf"
  scope = "REGIONAL"
  default_action { allow {} }

  rule {
    name     = "common-rule-set"
    priority = 1
    override_action { count {} }        # start in count mode, then switch to none {}
    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesCommonRuleSet"
      }
    }
    visibility_config { cloudwatch_metrics_enabled = true, metric_name = "common", sampled_requests_enabled = true }
  }
}
```

## Interview tips

- "Count mode first, then enforce" is the practical answer that shows you have deployed one.
- Virtual patching is a strong concept: a WAF buys time while the real fix ships.
- Be clear that a WAF is defence in depth, never a substitute for input validation and parameterised queries.

---

[⬅ Back to Network Security](./README.md) · [All topics](../README.md)
