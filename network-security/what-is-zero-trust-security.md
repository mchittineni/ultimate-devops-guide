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

**Core principles** (the widely used three-part summary; NIST SP 800-207 states them as seven tenets, and the CISA Zero Trust Maturity Model v2 turns them into a staged roadmap across identity, devices, networks, applications, and data):

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

## Example

```yaml
# Service-to-service zero trust in Istio: mTLS required, then allow by workload identity
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata: { name: default, namespace: payments }
spec:
  mtls: { mode: STRICT } # plaintext from anything without a mesh identity is rejected
---
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata: { name: payments-api, namespace: payments }
spec:
  selector: { matchLabels: { app: payments-api } }
  action: ALLOW
  rules:
    - from:
        - source: { principals: ["cluster.local/ns/checkout/sa/checkout"] } # SPIFFE identity, not an IP
      to:
        - operation: { methods: ["POST"], paths: ["/v1/charges"] }
```

## Interview tips

- "Never trust, always verify" plus the three principles is the conceptual answer; citing NIST SP 800-207 (policy decision point and enforcement point) and the CISA maturity model shows you know where they come from.
- Emphasise that zero trust is an architecture, not a product - vendors claiming otherwise are selling.
- Service mesh mTLS and identity-aware proxies are the concrete implementations to name.
- Name the limitation honestly: zero trust moves the risk to the identity provider and policy engine - if the IdP is compromised or down, everything is - and migrations take years, so expect to run a hybrid of perimeter and zero-trust controls.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot Docker networking between containers?]] (`#415`): [How do you troubleshoot Docker networking between containers?](../docker/how-do-you-troubleshoot-docker-networking-between-containers.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Network Security](./README.md) · [All topics](../README.md)
