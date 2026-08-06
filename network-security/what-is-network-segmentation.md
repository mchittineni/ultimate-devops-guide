---
title: "What is Network Segmentation?"
id: 120
category: "Network Security"
difficulty: "Intermediate"
tags:
  - devops
  - network-security
  - interview-questions
---

# What is Network Segmentation?

**Short answer:** Network segmentation divides a network into isolated zones so that a compromise in one cannot move freely into another — limiting lateral movement, reducing blast radius, and shrinking compliance scope.

## Detail

**Why it works.** Most breaches involve lateral movement: an attacker gains a foothold on a low-value host, then pivots towards data. Segmentation makes each pivot require crossing an enforced, logged boundary.

**Levels of granularity**

- **Physical / VLAN** — traditional network zones.
- **Cloud networks** — separate VPCs or VNets, ideally separate accounts or subscriptions per environment, with subnet tiers: public (load balancers only), private (application), and data (databases, no internet route at all).
- **Security groups / firewall rules** — instance-level, referencing other security groups rather than CIDR blocks so rules follow the workload.
- **Micro-segmentation** — per-workload policy. In Kubernetes, NetworkPolicies; in a service mesh, identity-based authorisation policies that do not depend on IP addresses at all.
- **Application-level** — separate services and databases per domain, with authorisation at each boundary.

**Practical guidance**

- Segment by trust level and data sensitivity, not by convenience.
- Databases never get an internet gateway route; access is via bastion-free brokered sessions or private endpoints.
- Use egress control at boundaries, not only ingress.
- Keep management and CI/CD networks separate from production workloads.

**Compliance value:** PCI-DSS explicitly permits segmentation to reduce the cardholder data environment scope, which can dramatically reduce audit cost. Auditors will ask for evidence that the segmentation is effective — usually penetration test results.

**Watch out for** the segmentation that exists on the diagram but not in the rules, and for over-segmentation that makes the network unmanageable and encourages engineers to open broad exceptions.

## Interview tips

- Lateral movement is the threat to name — it explains _why_ segmentation matters.
- Referencing security groups by group rather than CIDR is a practical detail that shows cloud experience.
- Mention PCI scope reduction if the role touches regulated environments.

---

[⬅ Back to Network Security](./README.md) · [All topics](../README.md)
