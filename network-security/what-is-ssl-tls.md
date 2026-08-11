---
title: "What is SSL/TLS?"
id: 118
category: "Network Security"
difficulty: "Beginner"
tags:
  - devops
  - network-security
  - interview-questions
---

# What is SSL/TLS?

**Short answer:** TLS (Transport Layer Security, the successor to SSL) encrypts network traffic and authenticates the server, providing confidentiality, integrity, and identity for connections such as HTTPS.

## Detail

**What it provides**

- **Confidentiality** - traffic is encrypted with a symmetric key negotiated per session.
- **Integrity** - an authenticated cipher detects tampering.
- **Authentication** - the certificate proves the server is who it claims, validated against a trusted certificate authority chain. Client certificates authenticate the caller too (mutual TLS).

**The handshake (TLS 1.3, simplified)**

1. Client sends `ClientHello` with supported cipher suites and a key share.
2. Server responds with `ServerHello`, its chosen cipher, its key share, and its certificate chain.
3. Both derive the same shared secret via Diffie-Hellman; the client verifies the certificate chain, expiry, hostname, and revocation status.
4. Encrypted application data flows - in TLS 1.3 this takes one round trip, and zero with session resumption.

**Versions.** SSL 2.0/3.0 and TLS 1.0/1.1 are deprecated and insecure. TLS 1.2 is the minimum acceptable; TLS 1.3 is faster and removes legacy cipher suites entirely.

**Post-quantum key exchange is already the default on the public web.** NIST standardised ML-KEM as FIPS 203 in August 2024, and browsers now negotiate the hybrid group `X25519MLKEM768` by default (Chrome 131+, Firefox 132+, Safari, plus Cloudflare and OpenSSL 3.5). It is _hybrid_ deliberately: an attacker must break both the classical X25519 exchange and ML-KEM-768. This defends against "harvest now, decrypt later" - traffic captured today and decrypted once a cryptographically relevant quantum computer exists. Note the scope: this protects the _key exchange_ only. Certificate signatures are still classical (RSA/ECDSA); post-quantum signatures are a later migration.

**Operational concerns**

- **Certificate expiry** is a leading cause of outages, and the window is shrinking fast. CA/Browser Forum ballot SC-081v3 (adopted April 2025) steps the maximum public TLS certificate lifetime down from 398 days to **200 days on 15 March 2026, 100 days on 15 March 2027, and 47 days on 15 March 2029**. Manual renewal stops being viable well before the end of that schedule - ACME automation (Let's Encrypt, cert-manager in Kubernetes, ACM in AWS) becomes mandatory, not a convenience. _Monitor days-to-expiry as a metric with an alert_ regardless.
- **Perfect forward secrecy** via ephemeral key exchange, so a future key compromise cannot decrypt past traffic.
- **HSTS** to force HTTPS, and redirect all HTTP traffic.
- **Termination point** - at the load balancer, re-encrypted to the backend, or passed through. Internal traffic should also be encrypted.

## Example

```bash
openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates

# Check protocol and cipher negotiated
curl -sI --tlsv1.3 https://example.com | head -1
```

## Interview tips

- Know that TLS 1.3 completes in one round trip and why that matters for latency.
- Certificate expiry monitoring is the operational answer interviewers most want to hear - and in 2026 the follow-up is the 47-day lifetime schedule and what it forces you to automate.
- Naming `X25519MLKEM768` and "harvest now, decrypt later" shows you have kept current; being clear that it protects key exchange and not certificate signatures shows you actually understand it.
- Be precise: TLS authenticates the _server_ by default; mutual TLS is required to authenticate the client.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you troubleshoot Docker networking between containers?]] (`#415`): [How do you troubleshoot Docker networking between containers?](../docker/how-do-you-troubleshoot-docker-networking-between-containers.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Network Security](./README.md) · [All topics](../README.md)
