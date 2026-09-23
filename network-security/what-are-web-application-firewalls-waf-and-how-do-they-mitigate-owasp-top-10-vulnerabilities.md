---
title: "What are Web Application Firewalls (WAF) and how do they mitigate OWASP Top 10 vulnerabilities?"
id: 669
category: "Network Security"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - network-security
  - waf
  - owasp
  - security
  - firewall
quiz:
  stem: "Why are traditional Layer 4 network firewalls (like AWS Security Groups) incapable of blocking SQL Injection attacks?"
  options:
    - "Layer 4 firewalls only operate on UDP traffic"
    - "Layer 4 firewalls inspect only IP addresses and port numbers; they cannot inspect the encrypted Layer 7 HTTP application payload containing the malicious SQL string"
    - "SQL Injection attacks do not use the internet"
    - "Layer 4 firewalls are prohibited by PCI-DSS"
  answer: 2
  explanation: "L4 firewalls only evaluate source/destination IPs and TCP ports. Inspecting request bodies and detecting SQL syntax requires a Layer 7 Web Application Firewall (WAF)."
---

# What are Web Application Firewalls (WAF) and how do they mitigate OWASP Top 10 vulnerabilities?

**Short answer:** A Web Application Firewall (WAF) inspects Layer 7 HTTP/HTTPS traffic at the network edge, filtering malicious payloads (SQL Injection, Cross-Site Scripting, SSRF) before requests reach backend application servers.

## Detail

Traditional L3/L4 network firewalls (like AWS Security Groups) only inspect IP addresses and TCP/UDP ports. They cannot detect an attacker sending `' OR 1=1 --` inside an HTTP POST JSON payload over port 443.

### How a WAF Protects Applications

1. **Rule Evaluation Engine**:
   - Inspects headers, cookies, query parameters, and request body.
   - Evaluates against regular expressions, signatures, and anomaly scoring (OWASP Core Rule Set).
2. **Mitigating OWASP Top 10**:
   - **SQL Injection (SQLi)**: Detects SQL keywords and quote manipulations.
   - **Cross-Site Scripting (XSS)**: Blocks `<script>` tags and JavaScript payload injections.
   - **Server-Side Request Forgery (SSRF)**: Blocks attempts to access cloud metadata IPs (`http://169.254.169.254/`).
3. **Rate Limiting & Bot Control**:
   - Blocks automated credential-stuffing attacks by rate limiting login endpoints (`/api/login`) by IP or client fingerprint.

## Example

```nginx
# Open-source WAF: ModSecurity v3 with the OWASP Core Rule Set in front of an app
load_module modules/ngx_http_modsecurity_module.so;

server {
  listen 443 ssl;
  modsecurity on;
  modsecurity_rules_file /etc/nginx/modsec/main.conf;   # includes crs-setup.conf and rules/*.conf
  location / { proxy_pass http://app:8080; }
}
```

```text
# /etc/nginx/modsec/modsecurity.conf - start in detection mode, enforce after tuning
SecRuleEngine DetectionOnly
# crs-setup.conf: raise the paranoia level only when false positives are under control
SecAction "id:900000,phase:1,pass,nolog,setvar:tx.blocking_paranoia_level=1"
```

## Interview tips

- Explain the mechanism: the WAF terminates or inspects HTTP after TLS decryption, normalises the request (decoding, case, path), then scores it against signatures; the OWASP CRS uses **anomaly scoring**, blocking only when the combined score passes a threshold.
- Be precise about coverage: WAFs are good at pattern-shaped attacks (injection, XSS, known CVE exploits via virtual patching, bots) and weak at logic flaws - broken access control, the top OWASP category, looks like a normal request.
- SSRF blocking at the WAF (matching `169.254.169.254` in parameters) is a useful backstop, but the real fixes are server-side URL allowlists, egress controls, and IMDSv2 on AWS.
- Always deploy in detection/count mode first and tune exclusions per path and parameter; a WAF that blocks real users on day one gets switched off.
- Note the ecosystem: Trustwave ended support for ModSecurity in 2024 and handed it to OWASP, and Coraza (a Go, CRS-compatible engine) is the common choice for proxies such as Envoy and Caddy.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Shift-Left and how is it practically implemented across the SDLC?]] (`#510`): [What is Shift-Left and how is it practically implemented across the SDLC?](../core-devops-concepts/what-is-shift-left-and-how-is-it-practically-implemented-across-the-sdlc.md)
- [[How does OpenID Connect (OIDC) eliminate long-lived cloud credentials in CI/CD pipelines?]] (`#533`): [How does OpenID Connect (OIDC) eliminate long-lived cloud credentials in CI/CD pipelines?](../cicd/how-does-openid-connect-oidc-eliminate-long-lived-cloud-credentials-in-ci-cd-pipelines.md)
- [[How do you secure CI/CD runners against supply-chain attacks and untrusted pull requests?]] (`#538`): [How do you secure CI/CD runners against supply-chain attacks and untrusted pull requests?](../cicd/how-do-you-secure-ci-cd-runners-against-supply-chain-attacks-and-untrusted-pull-requests.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Network Security](./README.md) · [All topics](../README.md)
