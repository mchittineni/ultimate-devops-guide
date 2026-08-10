---
title: "How do you manage TLS certificates in production?"
id: 491
category: "Network Security"
difficulty: "Intermediate"
tags:
  - devops
  - network-security
  - interview-questions
  - devsecops
  - security-and-compliance
---

# How do you manage TLS certificates in production?

**Short answer:** Automate issuance and renewal, and monitor expiry independently of the automation. In practice that means: for public endpoints on a cloud load balancer, use the provider's managed certificate service (**ACM**, Azure Key Vault certificates, Google-managed certs) with **DNS validation**, because renewal is then automatic and free; for Kubernetes, **cert-manager** with an ACME issuer (Let's Encrypt) or a private CA, storing the certificate in a Secret and renewing it at roughly two-thirds of its lifetime; for anything internal, run a private CA (AWS Private CA, Vault PKI, or step-ca) and issue **short-lived** certificates so rotation is routine rather than an event. Terminate TLS at the edge (load balancer, ingress, or mesh gateway), and use **end-to-end TLS** or a service mesh with mTLS for the internal hops that need it. Then the control that actually prevents outages: **alert on days-to-expiry from an external probe**, at 30 and 7 days, because every expiry incident is really a monitoring failure - the certificate did not surprise anyone, nobody was watching.

## Detail

### Where certificates come from, and what fits where

| Scenario                                   | Mechanism                                                          | Renewal                                                |
| ------------------------------------------ | ------------------------------------------------------------------ | ------------------------------------------------------ |
| Public HTTPS on ALB/CloudFront/App Gateway | **ACM** / Key Vault certificate / Google-managed                   | Automatic, if the DNS validation record stays in place |
| Kubernetes Ingress                         | **cert-manager** + ACME (HTTP-01 or DNS-01) or a private CA issuer | Automatic at ~2/3 of lifetime                          |
| Any host, any web server                   | **certbot** / Let's Encrypt with a renewal timer + reload hook     | Automatic (90-day certs, renew at 60)                  |
| Internal service-to-service                | Private CA (AWS Private CA, Vault PKI, step-ca) or a service mesh  | Short-lived (hours/days), rotated by the platform      |
| Client certificates / mTLS                 | Private CA, issued per workload                                    | Short-lived                                            |
| Code signing, non-web                      | Dedicated CA + HSM/KMS                                             | Manual, tightly controlled                             |

The general principle: **the shorter the lifetime, the better the hygiene** - a certificate that renews every 60 days has a tested renewal path, while a three-year certificate guarantees that nobody remembers how it was installed. Public CA maximum lifetimes have been shrinking for exactly this reason, and the industry direction is towards much shorter validity, so an answer built on manual annual renewals is already obsolete.

### Validation methods, and why DNS wins

- **DNS-01**: you (or the automation) create a TXT record the CA checks. Works for **wildcards**, works for endpoints that are not publicly reachable, and enables fully automated renewal. Needs API access to the DNS zone - which cert-manager and ACM both have via a role.
- **HTTP-01**: the CA fetches a token from `http://host/.well-known/acme-challenge/...`. Simple, but requires the name to be publicly reachable on port 80 and **cannot** issue wildcards.
- **TLS-ALPN-01**: served on 443, useful when port 80 is closed.

For ACM specifically: DNS validation adds a CNAME that must **stay in place** for renewals to work. Deleting it after issuance is a common own-goal - the certificate renews silently for years and then fails. If a certificate is stuck in `PENDING_VALIDATION`, the record is missing or wrong.

### The lifecycle, end to end

1. **Request** with the right names. A **wildcard** (`*.example.com`) covers one label only - it does **not** cover the apex `example.com` or a second level `a.b.example.com`. A **SAN** certificate lists each name explicitly, which is the answer to "how do you create certificates covering multiple subdomains?" - either a wildcard for one level, or a SAN list, or both.
2. **Issue and install** at the termination point: the load balancer listener, the ingress controller, or the web server. On Azure Application Gateway the certificate belongs on the **HTTPS listener**; the backend HTTP settings hold the **trusted root** for re-encryption, which is a different thing people frequently confuse.
3. **Serve the full chain.** The most common "works in my browser, fails in `curl`/Java" bug is a missing intermediate: browsers often cache or fetch intermediates, other clients do not. Always deploy leaf + intermediate(s), and verify with `openssl s_client -showcerts`.
4. **Renew automatically**, well before expiry, and **reload** the server - a renewed file on disk that nginx has not reloaded is still the old certificate in memory. `systemctl reload nginx` in a deploy hook, or cert-manager updating the Secret and the ingress controller watching it.
5. **Monitor independently.** A blackbox probe (`blackbox_exporter` `probe_ssl_earliest_cert_expiry`, or a synthetic check) measures what clients actually see, which catches the cases automation misses: a stale certificate on one of four load balancers, a manual certificate nobody automated, or a renewal that succeeded but was never reloaded.
6. **Revoke** when a key is compromised (CRL/OCSP), and rotate the key - reissuing with the same key after a compromise achieves nothing.

### The expired-certificate runbook

Asked as a scenario constantly ("the Application Gateway TLS certificate has expired - what steps do you follow?"). Answer as a sequence:

1. **Confirm** what is actually being served: `openssl s_client -connect host:443 -servername host` and read `notAfter`. Check every endpoint - load balancer, origin, and any internal hop - because the expired one may not be the one you assumed.
2. **Reissue or fetch** the current certificate: from ACM/Key Vault (often already renewed and just not deployed), or run the ACME renewal, or import the new `.pfx`/PEM.
3. **Install and reload** at the termination point; verify the full chain and the SNI-matched name.
4. **Check the backend leg** if you use end-to-end TLS - the backend's certificate and the trusted root on the proxy both matter.
5. **Verify from outside**, not from the host: a client-side `curl` plus your synthetic probe going green.
6. **Fix the cause**: move to managed/automated issuance, add the 30/7-day alert, and remove the manual step. If the renewal existed but failed, find out why (DNS record deleted, API credential expired, rate limit, reload hook missing) - that is the actual incident.

### Internal TLS and mTLS

For service-to-service, a public CA is the wrong tool - you cannot get a public certificate for `payments.prod.svc.cluster.local`. Use a **private CA** and issue short-lived certificates automatically: cert-manager with a Vault or AWS Private CA issuer, or let a **service mesh** (Istio, Linkerd, Consul) handle it - the mesh issues workload identities, rotates them every few hours, and enforces mTLS without the application knowing. That is the answer to "how do you secure service-to-service communication": mTLS with automatically rotated, short-lived workload certificates, plus authorisation policy on top.

The trade-off worth naming: a mesh adds a data-plane hop and operational surface, so for a handful of services, cert-manager plus application-level TLS may be simpler. See [running a service mesh in production without the sidecar tax](../api-gateway-and-service-mesh/how-do-you-run-a-service-mesh-in-production-without-the-sidecar-tax.md).

### Hygiene that prevents whole classes of incident

- **CAA records** restricting which CAs may issue for your domain - a cheap control against mis-issuance.
- **Private keys never in Git**; issued on the host or in the vault, stored in Key Vault/Secrets Manager or a Kubernetes Secret with restrictive modes, and never emailed.
- **Inventory**: you cannot renew what you do not know about. Keep a list generated from the estate (ACM, Key Vault, cert-manager resources, plus a scan of your public endpoints) rather than a spreadsheet.
- **Protocol and cipher policy**: TLS 1.2 minimum, prefer 1.3, disable renegotiation and weak suites, and pin the load balancer's security policy explicitly rather than accepting a default that ages.
- **HSTS** once you are confident, so browsers refuse plaintext.
- **The `.csr` → `.cer` → `.pfx` workflow** that people still do by hand: generate the key and CSR, submit to the CA, receive the certificate, combine with the key and chain into a PKCS#12 for Windows/Azure consumers. Automate it end to end (Key Vault certificate policy with an integrated CA, or an ACME client) rather than scripting the manual steps - the goal is to delete the workflow, not to speed it up.

## Example

```bash
# What is actually being served, and until when? (the first command in any incident)
openssl s_client -connect api.example.com:443 -servername api.example.com </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates -ext subjectAltName

# Is the chain complete? (missing intermediate = "works in Chrome, fails in curl/Java")
openssl s_client -connect api.example.com:443 -servername api.example.com -showcerts </dev/null \
  | grep -c 'BEGIN CERTIFICATE'          # expect 2+ (leaf + intermediate)

# Days remaining, for scripting an alert
end=$(openssl s_client -connect api.example.com:443 -servername api.example.com </dev/null 2>/dev/null \
      | openssl x509 -noout -enddate | cut -d= -f2)
echo $(( ( $(date -d "$end" +%s) - $(date +%s) ) / 86400 )) days left

# Does the local key match the certificate? (mismatched pair = handshake failure)
openssl x509 -noout -modulus -in cert.pem | openssl md5
openssl rsa  -noout -modulus -in key.pem  | openssl md5     # the two must be identical
```

```yaml
# cert-manager: automated issuance and renewal for Kubernetes, DNS-01 so wildcards work
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata: { name: letsencrypt-prod }
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: platform@example.com
    privateKeySecretRef: { name: letsencrypt-prod-account }
    solvers:
      - dns01: # DNS-01: works for wildcards and non-public endpoints
          route53:
            region: eu-west-1
            # IRSA-provided credentials; no keys in the cluster
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata: { name: example-wildcard, namespace: istio-system }
spec:
  secretName: example-wildcard-tls
  issuerRef: { name: letsencrypt-prod, kind: ClusterIssuer }
  duration: 2160h # 90 days
  renewBefore: 720h # renew at 60 days: a tested path, well before expiry
  privateKey: { algorithm: ECDSA, size: 256, rotationPolicy: Always }
  dnsNames:
    - "*.example.com" # wildcard: one label only...
    - "example.com" # ...so the apex must be listed explicitly
```

```hcl
# ACM with DNS validation - and the record that must STAY for renewals to work
resource "aws_acm_certificate" "main" {
  domain_name               = "example.com"
  subject_alternative_names = ["*.example.com"] # SAN list for multiple names
  validation_method         = "DNS"
  lifecycle { create_before_destroy = true }
}

resource "aws_route53_record" "validation" {
  for_each = { for o in aws_acm_certificate.main.domain_validation_options : o.domain_name => o }
  zone_id  = aws_route53_zone.main.zone_id
  name     = each.value.resource_record_name
  type     = each.value.resource_record_type
  records  = [each.value.resource_record_value]
  ttl      = 60
  # DO NOT delete these after issuance - ACM re-validates on renewal
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.public.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06" # pin it; do not inherit a default
  certificate_arn   = aws_acm_certificate.main.arn
  default_action { type = "forward"  target_group_arn = aws_lb_target_group.app.arn }
}
```

```text
The alert that prevents the incident - from an EXTERNAL probe, not from the CA's API

  # blackbox_exporter measures what clients actually see
  - alert: TLSCertExpiringSoon
    expr: (probe_ssl_earliest_cert_expiry - time()) / 86400 < 30
    for: 1h
    labels: { severity: ticket }

  - alert: TLSCertExpiringUrgent
    expr: (probe_ssl_earliest_cert_expiry - time()) / 86400 < 7
    for: 10m
    labels: { severity: page }

  Also alert on: cert-manager Certificate not Ready, ACM status != ISSUED,
  and a renewal job that has not succeeded in N days (absence of success, not
  presence of failure - a cron that stopped running emits no errors).
```

## Interview tips

- Lead with automation plus independent monitoring, and say the line that reframes the topic: **every expiry outage is a monitoring failure**, because the expiry date was known months in advance.
- Match the mechanism to the place - ACM/Key Vault for cloud load balancers, cert-manager for Kubernetes, certbot for standalone hosts, a private CA for internal mTLS - rather than naming one tool for everything.
- Explain DNS-01 versus HTTP-01 and say why DNS-01 is preferred: wildcards and non-public endpoints, fully automatable. Then add the ACM detail that the validation CNAME must remain in place for renewals.
- Get the wildcard rule right: `*.example.com` covers one label only, not the apex and not a second level - so you need the apex in the SAN list. That precision is frequently tested.
- Volunteer the missing-intermediate failure mode ("works in the browser, fails in `curl` or Java") and `openssl s_client -showcerts` as the check. It is the most common real TLS bug after expiry.
- Mention that a renewed file is not a renewed service - the server must reload. A renewal that succeeded without a reload is a silent failure.
- Have the expired-certificate runbook as an ordered sequence, ending with "fix the cause and add the 30/7-day alert" rather than just "install the new cert".
- For internal traffic, say a public CA cannot issue for cluster-internal names, so use a private CA or a service mesh with short-lived automatically-rotated workload certificates - and name the mesh trade-off honestly.
- Add the hygiene items that show breadth: CAA records, keys never in Git, an inventory generated from the estate, an explicitly pinned TLS policy at 1.2 minimum, and automating the `.csr`/`.cer`/`.pfx` workflow out of existence. See [what is SSL/TLS](./what-is-ssl-tls.md), [what happens when a user opens your application in a browser](./what-happens-when-a-user-opens-your-application-in-a-browser.md), [choosing between Azure Load Balancer, Application Gateway, and Front Door](../azure-engineering/how-do-you-choose-between-azure-load-balancer-application-gateway-and-front-door.md), and [rotating secrets without downtime](../devsecops/how-do-you-rotate-secrets-without-downtime.md).

---

[⬅ Back to Network Security](./README.md) · [All topics](../README.md)
