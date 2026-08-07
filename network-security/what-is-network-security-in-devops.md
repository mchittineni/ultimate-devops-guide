---
title: "What is Network Security in DevOps?"
id: 116
category: "Network Security"
difficulty: "Intermediate"
tags:
  - devops
  - network-security
  - interview-questions
---

# What is Network Security in DevOps?

**Short answer:** Network security in DevOps means designing, provisioning, and continuously verifying network controls as code - segmentation, least-privilege firewall rules, encryption in transit, and monitoring - so protection is deployed and audited automatically alongside the workloads it protects.

## Detail

**Design principles**

- **Default deny.** Start with nothing allowed and open only what is needed, in both directions. Egress filtering matters as much as ingress: it is what stops data exfiltration and command-and-control traffic.
- **Segmentation.** Public, private, and data subnets; separate VPCs or accounts per environment; namespaces and NetworkPolicies inside Kubernetes.
- **Defence in depth.** Security groups plus network ACLs plus host firewalls plus application-level authorisation. No single control is the whole answer.
- **Encryption everywhere**, including internal traffic - mutual TLS between services, not just at the edge.
- **No implicit trust from network location.** Being inside the VPC should not grant access; that is the zero-trust principle.

**As code.** Firewall rules, NetworkPolicies, and routing live in Terraform or Kubernetes manifests, reviewed in pull requests, scanned by policy (`checkov`, OPA) for over-permissive rules, and reconciled continuously so drift is corrected.

**Operationally:** VPC flow logs and DNS query logs shipped to a security account, alerting on unexpected egress destinations, intrusion detection (GuardDuty, Falco for containers), and periodic review of every rule that allows `0.0.0.0/0`.

## Example

```yaml
# Kubernetes: default-deny, then allow exactly what is required
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny, namespace: prod }
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: api-allow, namespace: prod }
spec:
  podSelector: { matchLabels: { app: api } }
  policyTypes: [Ingress, Egress]
  ingress:
    - from: [{ podSelector: { matchLabels: { app: gateway } } }]
      ports: [{ port: 8080 }]
  egress:
    - to: [{ podSelector: { matchLabels: { app: postgres } } }]
      ports: [{ port: 5432 }]
    - to:
        [
          {
            namespaceSelector:
              { matchLabels: { kubernetes.io/metadata.name: kube-system } },
          },
        ]
      ports: [{ port: 53, protocol: UDP }] # DNS
```

## Interview tips

- Egress filtering is the control most teams neglect - raising it unprompted is a strong signal.
- Remember the DNS rule when writing default-deny NetworkPolicies; forgetting it is the classic mistake.
- Frame network controls as code, reviewed and scanned, not as tickets to a firewall team.

---

[⬅ Back to Network Security](./README.md) · [All topics](../README.md)
