---
title: "How do you plan a migration to post-quantum cryptography?"
id: 764
category: "Network Security"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - network-security
  - post-quantum
  - cryptography
  - tls
quiz:
  stem: "Why do most organisations migrate TLS key exchange to post-quantum algorithms before migrating certificate signatures?"
  options:
    - "Because post-quantum signatures are already mandatory in all browsers"
    - "Because recorded traffic can be decrypted later ('harvest now, decrypt later'), while a forged signature only matters once a quantum computer exists at the moment of the attack"
    - "Because key exchange uses symmetric cryptography only"
    - "Because certificates cannot be changed until 2035"
  answer: 2
  explanation: "Confidentiality has a long tail: traffic captured today can be broken retroactively. Authentication only needs to resist attackers at connection time, so signature migration can follow once PQ certificates are practical."
---

# How do you plan a migration to post-quantum cryptography?

**Short answer:** Start with an **inventory**, because you cannot migrate cryptography you have not found; then prioritise by **data lifetime**, fixing key exchange first because of "harvest now, decrypt later"; then roll out **hybrid** schemes (classical plus post-quantum, such as the TLS group `X25519MLKEM768`) through the components you already patch - TLS libraries, load balancers, CDNs, service meshes, VPNs - while building **crypto agility** so the next change is configuration, not a rewrite. The standards are settled enough to act on: NIST published ML-KEM (FIPS 203) for key establishment and ML-DSA (FIPS 204) and SLH-DSA (FIPS 205) for signatures in August 2024, and its transition plan (NIST IR 8547) deprecates quantum-vulnerable public-key algorithms such as RSA and ECC after 2030 and disallows them after 2035.

## Detail

### What a quantum computer actually breaks

- **Public-key cryptography falls**: Shor's algorithm breaks RSA, finite-field Diffie-Hellman, and elliptic-curve schemes (ECDH, ECDSA, Ed25519). That covers TLS key exchange, certificate signatures, SSH, IPsec/IKE, code signing, and JWT signatures using RS256/ES256.
- **Symmetric cryptography survives**: Grover's algorithm only halves effective key strength, so AES-256 and SHA-256/384 remain fine. AES-128 is usually still considered acceptable, but long-lived data should prefer AES-256.

So the migration is about **asymmetric** algorithms, and it splits into two problems with different urgency:

| Problem                     | Threat timing                                       | Urgency | Current answer                                           |
| --------------------------- | --------------------------------------------------- | ------- | -------------------------------------------------------- |
| Key exchange / encryption   | Traffic recorded **today** can be decrypted later   | Now     | Hybrid ML-KEM (`X25519MLKEM768`) in TLS 1.3, SSH, IKEv2  |
| Signatures / authentication | Forgery needs a quantum computer **at attack time** | Planned | ML-DSA / SLH-DSA, once ecosystems (PKI, HSMs) support it |

The question that sets priority is **Mosca's inequality**: if _how long the data must stay secret_ plus _how long your migration takes_ exceeds _the time until a cryptographically relevant quantum computer exists_, you are already late for that data. Health records, state secrets, and long-term financial data qualify; a session cookie does not.

### Step 1 - inventory (the part that takes longest)

Build a cryptographic inventory, ideally as a **CBOM** (Cryptography Bill of Materials, supported by CycloneDX): which algorithms, key sizes, and libraries each system uses, where keys live, and which protocols carry what data. Sources: TLS scans of your endpoints, load balancer and CDN policies, certificate inventories, SBOMs (to find OpenSSL, BoringSSL, Go, Java versions), code search for crypto APIs, HSM and KMS key listings, and vendor questionnaires for SaaS and appliances. Expect the hard cases to be hardcoded algorithms, embedded devices, and third parties.

### Step 2 - get key exchange onto hybrid PQ

Much of this arrives through upgrades rather than projects:

- **Browsers and CDNs** already negotiate `X25519MLKEM768` by default (Chrome, Firefox, Safari, Cloudflare). OpenSSL 3.5, Go 1.24+, and recent BoringSSL and Java releases support it.
- **Load balancers**: select a PQ-capable policy explicitly (on AWS, the `ELBSecurityPolicy-TLS13-1-2-Res-PQ-2025-09` family) rather than relying on defaults.
- **Internal traffic**: service meshes and gateways inherit it from their TLS libraries - check the Envoy/ztunnel version and whether the PQ group is enabled.
- **SSH**: OpenSSH 10 defaults to the hybrid `mlkem768x25519-sha256` key exchange.
- **VPNs**: IKEv2 supports hybrid ML-KEM through multiple key exchanges (RFC 9370); WireGuard needs a pre-shared key or an add-on such as Rosenpass.

**Why hybrid?** ML-KEM is young. Combining it with X25519 means an attacker must break both, so a flaw in the new algorithm does not make you weaker than today.

### Step 3 - plan signatures and PKI

Post-quantum signatures are much larger (an ML-DSA-65 signature is about 3.3 KB versus 64 bytes for ECDSA P-256), which hurts certificate chains, handshakes, and constrained devices. Public WebPKI certificates with PQ signatures are not yet issued at scale, so plan rather than rush: start with **private PKI** and long-lived roots (firmware and code signing, internal CAs, HSM-backed keys), confirm your HSM and KMS vendors' ML-DSA roadmap, and use stateful hash-based signatures (LMS/XMSS) where they are already approved for firmware signing.

### Step 4 - build crypto agility

The lesson from SHA-1 and TLS 1.0 is that migrations take a decade when algorithms are hardcoded. Centralise crypto in maintained libraries, make algorithms configuration, keep certificate lifetimes short and issuance automated (the same automation that handles 47-day certificates handles an algorithm change), and track the inventory continuously rather than once.

### Regulatory and timeline anchors

- **NIST IR 8547**: quantum-vulnerable algorithms deprecated after 2030, disallowed after 2035.
- **NSA CNSA 2.0** (US national security systems): post-quantum preferred now, required across most categories by the early 2030s.
- **EU coordinated roadmap**: member states start transitions by 2026 and complete high-risk use cases by 2030.
- **HQC** was selected by NIST in 2025 as a backup KEM based on different mathematics, which is another argument for agility.

## Example

```bash
# Is an endpoint negotiating hybrid post-quantum key exchange? (OpenSSL 3.5+)
openssl s_client -connect example.com:443 -servername example.com \
  -groups X25519MLKEM768 </dev/null 2>/dev/null | grep -E 'Negotiated TLS1.3 group|Protocol'
#   Negotiated TLS1.3 group: X25519MLKEM768

# Which key exchange does SSH use?
ssh -Q kex | grep -i mlkem        # client support
ssh -vv host 2>&1 | grep 'kex: algorithm'

# AWS: list post-quantum load balancer policies, then pin one explicitly
aws elbv2 describe-ssl-policies \
  --query "SslPolicies[?contains(Name, 'PQ')].Name" --output table
```

```text
Minimal CBOM-style inventory row - what every system should be able to answer

system         protocol   key exchange      signature        data lifetime   PQ status
payments-api   TLS 1.3    X25519MLKEM768    ECDSA P-256      10 years        KEX done; sig planned
legacy-sftp    SSH        ecdh-sha2-p256    RSA-2048         7 years         upgrade OpenSSH -> mlkem768x25519
partner-vpn    IKEv2      DH group 14       RSA-3072         7 years         vendor roadmap requested
```

## Interview tips

- Separate the two problems immediately: key exchange is urgent because of **harvest now, decrypt later**; signatures matter only once an attacker has a quantum computer, so they follow.
- Say what breaks and what does not: RSA and ECC fall to Shor's algorithm; AES-256 and SHA-2 survive Grover's with margin.
- Name the standards precisely - ML-KEM (FIPS 203), ML-DSA (FIPS 204), SLH-DSA (FIPS 205) - and the NIST IR 8547 dates: deprecated after 2030, disallowed after 2035.
- Explain **hybrid** and why it is the default: you only lose if both the classical and the post-quantum algorithm break.
- Lead the plan with the **inventory** (a CBOM), prioritise by data lifetime (Mosca's inequality), and show that most key-exchange migration arrives through library and load-balancer upgrades you already run.
- Volunteer the practical pain points: larger handshakes that trip old middleboxes, much larger PQ signatures, HSM and vendor readiness, and hardcoded algorithms - which is why **crypto agility** is the lasting deliverable. See [what is TLS 1.3](./what-is-tls-1-3-and-what-security-and-performance-improvements-does-it-introduce-over-tls-1-2.md), [what is SSL/TLS](./what-is-ssl-tls.md), and [how do you manage TLS certificates in production](./how-do-you-manage-tls-certificates-in-production.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot Docker networking between containers?]] (`#415`): [How do you troubleshoot Docker networking between containers?](../docker/how-do-you-troubleshoot-docker-networking-between-containers.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Network Security](./README.md) · [All topics](../README.md)
