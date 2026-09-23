---
title: "How does DNSSEC prevent DNS spoofing and cache poisoning attacks?"
id: 670
category: "Network Security"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - network-security
  - dns
  - dnssec
  - cryptography
quiz:
  stem: "Does DNSSEC encrypt DNS queries to prevent internet service providers from seeing what domains users visit?"
  options:
    - "Yes, DNSSEC uses AES-256 to encrypt all DNS traffic"
    - "No, DNSSEC provides authentication and cryptographic integrity to prove records were not forged; it does not provide confidentiality or encryption (which is handled by DoH or DoT)"
    - "DNSSEC only encrypts `.gov` and `.mil` domains"
    - "DNSSEC converts DNS to IPv6"
  answer: 2
  explanation: "DNSSEC provides authentication and integrity via digital signatures, proving records are genuine. It does not provide privacy; encryption is handled by DNS-over-HTTPS (DoH) or DNS-over-TLS (DoT)."
---

# How does DNSSEC prevent DNS spoofing and cache poisoning attacks?

**Short answer:** DNSSEC (Domain Name System Security Extensions) adds digital signatures to DNS records, so a validating resolver can verify each answer against an unbroken chain of trust back to the root zone and reject forged responses, which defeats cache poisoning. It provides authenticity and integrity, not confidentiality, and a signing mistake takes your whole domain offline for validating resolvers.

## Detail

The original 1983 DNS protocol is unauthenticated: clients send a UDP query on port 53, and whatever response arrives first with the matching 16-bit Transaction ID is accepted.

### The Kaminsky DNS Cache Poisoning Attack

Dan Kaminsky's 2008 attack made poisoning practical: the attacker makes a recursive resolver query many random, non-existent names (`a1.bank.com`, `a2.bank.com`, ...) and races each real answer with forged responses. Every query is a fresh chance to guess the 16-bit Transaction ID, and the forged response carries a malicious NS/glue record for the whole `bank.com` zone - so one win poisons the domain for every user of that resolver. The emergency fix was **source-port randomisation** (adding roughly 16 more bits to guess); DNSSEC is the cryptographic fix.

### How DNSSEC Solves This

DNSSEC does **not** encrypt DNS queries (they remain visible plaintext). Instead, it **digitally signs DNS records**:

- **RRSIG (Resource Record Signature)**: Every DNS record (A, CNAME, MX) is accompanied by a cryptographic signature.
- **DNSKEY**: Public key used to verify the RRSIG.
- **DS (Delegation Signer)**: A hash of the child zone's public key stored in the parent zone (e.g. `.com` signs for `example.com`).
- **NSEC / NSEC3**: Signed proof that a name does _not_ exist, so an attacker cannot forge an NXDOMAIN either (NSEC3 hashes names to make zone walking harder).
- **Chain of Trust**: Validating resolvers check signatures up the tree to the root zone (`.`), whose key-signing key is the configured trust anchor. If an attacker forges a record, the signature check fails and the resolver returns `SERVFAIL` instead of the forged answer.

### Limitations and Operational Risk

- **Last-mile gap**: validation normally happens at the recursive resolver; the path from resolver to the client is unprotected unless you validate locally or use DNS over TLS/HTTPS (which encrypt but do not authenticate the data itself). DNSSEC and DoT/DoH are complementary.
- **Availability risk**: an expired signature or a botched key rollover makes your domain fail to resolve for every validating resolver - DNSSEC outages are self-inflicted far more often than attacks are prevented. Automate signing (managed DNS such as Route 53 or Cloudflare) and monitor signature expiry.
- **Algorithms**: prefer ECDSA P-256 (algorithm 13) or Ed25519 (15); RSA/SHA-1 algorithms are deprecated.
- **Root KSK rollover**: the root zone switches its signing key from KSK-2017 (key tag 20326) to KSK-2024 (key tag 38696) on 11 October 2026; validating resolvers without the new trust anchor will fail to resolve anything.

## Example

```bash
# Ask a validating resolver: the "ad" (authenticated data) flag means the chain verified
dig +dnssec example.com A @1.1.1.1
#   ;; flags: qr rd ra ad; ...
#   example.com.  300  IN  RRSIG  A 13 2 300 ...   <- signature, algorithm 13 (ECDSA P-256)

# Deliberately broken test zone: a validating resolver refuses to answer
dig dnssec-failed.org @1.1.1.1        # status: SERVFAIL
dig +cd dnssec-failed.org @1.1.1.1    # +cd (checking disabled) returns the unvalidated answer

# Walk and diagnose the whole chain of trust (DS in the parent -> DNSKEY -> RRSIG)
delv example.com A +rtrace

# Resolver operators: is the new root trust anchor (key tag 38696) configured?
unbound-anchor -v   # Unbound; BIND users check managed-keys / trust-anchors
```

## Interview tips

- Say clearly what DNSSEC does and does not do: **authenticity and integrity** of DNS data, not **confidentiality** - queries stay in plaintext. For privacy you add DoT/DoH; the two solve different problems.
- Explain the chain of trust in one breath: RRSIG signs the record set, DNSKEY holds the zone's keys (ZSK signs records, KSK signs the DNSKEY set), and a DS record in the parent pins the child's KSK - repeated up to the root trust anchor.
- Mention authenticated denial (NSEC/NSEC3), because "what stops a forged NXDOMAIN?" is a common follow-up.
- Be honest about the trade-off: DNSSEC failures are outages. Expired signatures, a DS record left in the parent after changing DNS provider, or a mishandled rollover make the domain unresolvable for validating resolvers - so use managed signing and alert on signature expiry.
- Know why adoption is uneven: many large domains still do not sign, because the attacks it prevents are rare compared with the outages it can cause, and TLS certificates already authenticate the server for HTTPS.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot Docker networking between containers?]] (`#415`): [How do you troubleshoot Docker networking between containers?](../docker/how-do-you-troubleshoot-docker-networking-between-containers.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Network Security](./README.md) · [All topics](../README.md)
