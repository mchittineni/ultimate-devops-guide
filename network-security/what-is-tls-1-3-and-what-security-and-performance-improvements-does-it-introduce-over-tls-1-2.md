---
title: "What is TLS 1.3 and what security and performance improvements does it introduce over TLS 1.2?"
id: 672
category: "Network Security"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - network-security
  - tls
  - cryptography
  - ssl
  - performance
quiz:
  stem: "Why does TLS 1.3 mandate Ephemeral Diffie-Hellman key exchange and eliminate static RSA key exchange?"
  options:
    - "RSA keys can only be generated on Windows machines"
    - "To enforce Perfect Forward Secrecy (PFS), guaranteeing that compromising the server's long-term private key in the future cannot decrypt previously recorded traffic"
    - "Diffie-Hellman requires less memory on mobile phones"
    - "RSA was banned by the W3C"
  answer: 2
  explanation: "With static RSA, an attacker who captures encrypted traffic today can decrypt all historical sessions if they steal the server's private key years later. Ephemeral Diffie-Hellman generates disposable session keys, guaranteeing PFS."
---

# What is TLS 1.3 and what security and performance improvements does it introduce over TLS 1.2?

**Short answer:** TLS 1.3 reduces the handshake from two round trips to one (1-RTT) and introduces 0-RTT session resumption for faster connections, while deprecating weak cryptographic ciphers (RSA key exchange, SHA-1, CBC) in favor of mandatory Perfect Forward Secrecy.

## Detail

Published in RFC 8446, TLS 1.3 was the largest overhaul of internet encryption in 20 years:

### 1. Performance: Faster 1-RTT Handshake

- **TLS 1.2**: Required **two full round trips (2-RTT)** between client and server before encrypted application data could be sent.
- **TLS 1.3**: Reduces the handshake to **one round trip (1-RTT)** by combining key exchange parameters with the initial `ClientHello`.
- **0-RTT Resumption (Early Data)**: Clients reconnecting to a known server can send encrypted HTTP data in the first flight using a pre-shared key from the previous session. The catch: early data can be **replayed**, so it is only safe for idempotent requests and many servers leave it disabled.

### 2. Security: Removal of Vulnerable Legacy Ciphers

TLS 1.3 removed obsolete primitives and features behind a decade of attacks (padding oracles such as Lucky13 and POODLE, downgrade attacks such as FREAK and Logjam, compression attacks such as CRIME):

- **Removed Static RSA Key Exchange**: Mandated **Ephemeral Diffie-Hellman (ECDHE)**, ensuring **Perfect Forward Secrecy (PFS)**—even if a server's private key is leaked in the future, past encrypted traffic cannot be decrypted!
- **Removed CBC Mode Ciphers**: Replaced with Authenticated Encryption with Associated Data (AEAD) ciphers (AES-GCM, ChaCha20-Poly1305).
- **Removed renegotiation, compression, and arbitrary DH groups**, and cut the cipher-suite list to five, so there is far less to misconfigure or downgrade.
- **Encrypted more of the handshake**: everything after `ServerHello`, including the server certificate, is encrypted. Encrypted Client Hello (ECH) extends this to the SNI.
- **Post-quantum ready**: the hybrid `X25519MLKEM768` key exchange that browsers now negotiate by default is a TLS 1.3 key-share group - another reason to make 1.3 the preferred version.

## Example

```bash
# Confirm TLS 1.3 and see the negotiated group and cipher
openssl s_client -connect example.com:443 -servername example.com -tls1_3 </dev/null 2>/dev/null \
  | grep -E 'Protocol|Cipher|Negotiated TLS1.3 group|Server Temp Key'

# Prove legacy versions are refused (should fail the handshake)
openssl s_client -connect example.com:443 -servername example.com -tls1_1 </dev/null
```

```nginx
# Server side: TLS 1.2 minimum, 1.3 preferred; keep 0-RTT off unless requests are idempotent
ssl_protocols TLSv1.2 TLSv1.3;
ssl_early_data off;
```

## Interview tips

- Lead with the two headline changes: a 1-RTT handshake (the client sends its key share in `ClientHello`) and a much smaller, safer design - only (EC)DHE key exchange, only AEAD ciphers, no renegotiation, no compression, no static RSA.
- Qualify 0-RTT: early data can be **replayed** by an attacker and lacks forward secrecy for that first flight, so servers should accept it only for idempotent requests, or disable it.
- Mention that more of the handshake is encrypted - the server certificate is no longer visible on the wire - and that **Encrypted Client Hello (ECH)** extends this to the SNI.
- Current practice: TLS 1.2 minimum, 1.3 preferred, TLS 1.0/1.1 formally deprecated by RFC 8996; and modern clients negotiate hybrid post-quantum key exchange (`X25519MLKEM768`) over TLS 1.3.
- Trade-off to name: mandatory forward secrecy breaks passive decryption with a static server key, so middleboxes and IDS that relied on it must move to terminating proxies or endpoint visibility.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?]] (`#541`): [How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?](../cicd/how-do-you-design-a-robust-ci-cd-caching-strategy-to-minimize-build-duration-without-cache-poisoning.md)
- [[How do you troubleshoot Docker networking between containers?]] (`#415`): [How do you troubleshoot Docker networking between containers?](../docker/how-do-you-troubleshoot-docker-networking-between-containers.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Network Security](./README.md) · [All topics](../README.md)
