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

**Operational concerns**

- **Certificate expiry** is a leading cause of outages. Automate issuance and renewal (Let's Encrypt with ACME, cert-manager in Kubernetes, ACM in AWS) and _monitor days-to-expiry as a metric with an alert_.
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
- Certificate expiry monitoring is the operational answer interviewers most want to hear.
- Be precise: TLS authenticates the _server_ by default; mutual TLS is required to authenticate the client.

---

[⬅ Back to Network Security](./README.md) · [All topics](../README.md)
