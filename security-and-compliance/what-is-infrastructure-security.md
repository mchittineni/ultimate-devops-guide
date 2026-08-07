---
title: "What is Infrastructure Security?"
id: 37
category: "Security and Compliance"
difficulty: "Intermediate"
tags:
  - devops
  - security-and-compliance
  - interview-questions
---

# What is Infrastructure Security?

**Short answer:** Infrastructure security is the protection of the compute, network, storage, and identity layers that applications run on - through least-privilege access, network segmentation, encryption, hardening, patching, and continuous monitoring.

## Detail

**Identity and access.** The dominant control in cloud. Use roles and short-lived credentials rather than long-lived keys, enforce MFA, apply least privilege, and separate duties. Workload identity (IRSA on EKS, Workload Identity on GKE, managed identities on Azure) removes secrets from application configuration entirely.

**Network.** Segment with VPCs, subnets, security groups, and NACLs. Keep databases in private subnets with no route to the internet. Use private endpoints for managed services. Inside Kubernetes, default-deny NetworkPolicies then allow explicitly.

**Compute hardening.** Minimal base images, no SSH into production (use session-manager-style brokered access), immutable instances replaced rather than patched, CIS benchmark baselines, and host-level runtime detection.

**Data.** Encryption at rest with managed keys (KMS/Key Vault/Cloud KMS) and in transit with TLS 1.2+. Key rotation, and separation between who can use a key and who can manage it.

**Patch and vulnerability management.** Continuous scanning of hosts, images, and dependencies, with remediation SLAs keyed to severity.

**Detection and audit.** Cloud audit logs (CloudTrail, Activity Log) delivered to an immutable store, with alerts on privilege escalation, policy changes, and anomalous API use.

## Example

```hcl
# Default-deny egress, explicit ingress only from the load balancer
resource "aws_security_group" "app" {
  name   = "app"
  vpc_id = var.vpc_id

  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]   # not 0.0.0.0/0
  }

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

## Interview tips

- Structure the answer by layer - identity, network, compute, data, detection - rather than listing controls randomly.
- Defence in depth and blast-radius reduction are the framing concepts.
- Have an opinion on the highest-leverage control: in cloud it is nearly always IAM.

---

[⬅ Back to Security and Compliance](./README.md) · [All topics](../README.md)
