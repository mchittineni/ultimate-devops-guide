---
title: "What is Zero Trust Security?"
id: 117
category: "Network Security"
difficulty: "Intermediate"
tags:
  - devops
  - network-security
  - interview-questions
---

# What is Zero Trust Security?

**Short answer:** Zero trust is a security model that removes implicit trust based on network location. Every request is authenticated, authorised, and encrypted regardless of where it originates - "never trust, always verify."

## Detail

**What it replaces.** The perimeter model assumed everything inside the corporate network or VPC was trustworthy. That failed for obvious reasons: cloud workloads, remote work, SaaS, and the fact that one compromised host historically meant free movement across the whole internal network.

**Core principles** (as codified in NIST SP 800-207):

1. **Verify explicitly** - authenticate and authorise on every request using all available signals: identity, device posture, location, and behaviour.
2. **Least privilege** - just-enough, just-in-time access, scoped narrowly and time-limited.
3. **Assume breach** - segment aggressively to minimise blast radius, encrypt everything, and monitor continuously.

**Implementation components**

- **Strong identity** for both humans (SSO, MFA, phishing-resistant factors) and workloads (SPIFFE identities, IRSA, managed identities).
- **Device trust** - posture checks before access is granted.
- **Micro-segmentation** - per-workload policy rather than per-subnet.
- **Policy enforcement points** - an identity-aware proxy for user access (BeyondCorp-style, replacing VPNs), and a service mesh enforcing mTLS and authorisation between services.
- **Continuous verification** - sessions re-evaluated, not granted indefinitely.
- **Comprehensive logging** of every access decision.

**In practice for a DevOps engineer:** mTLS between all services, workload identity instead of static credentials, short-lived access to production through a broker with audit trails, and NetworkPolicies that express identity-based rather than IP-based rules.

## Interview tips

- "Never trust, always verify" plus the three NIST principles is the complete conceptual answer.
- Emphasise that zero trust is an architecture, not a product - vendors claiming otherwise are selling.
- Service mesh mTLS and identity-aware proxies are the concrete implementations to name.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot Docker networking between containers?]] (`#415`): [How do you troubleshoot Docker networking between containers?](../docker/how-do-you-troubleshoot-docker-networking-between-containers.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Network Security](./README.md) · [All topics](../README.md)
