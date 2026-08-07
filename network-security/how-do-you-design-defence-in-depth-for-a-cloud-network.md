---
title: "How do you design defence in depth for a cloud network?"
id: 297
category: "Network Security"
difficulty: "Advanced"
tags:
  - devops
  - network-security
  - interview-questions
---

# How do you design defence in depth for a cloud network?

**Short answer:** Assume every single control will fail, and make sure no single failure is sufficient. Layer them from the outside in: **edge** (DDoS protection, WAF, TLS), **perimeter** (public/private subnet split, no direct internet ingress to workloads), **segmentation** (per-tier security groups referencing each other, network policies inside the cluster), **identity** (mTLS and workload identity so the network is not the only trust boundary), **egress control** (nothing reaches the internet without passing an allowlist), and **detection** (flow logs, DNS logs, IDS) so you find out when a layer is bypassed. Then verify continuously - policy-as-code and a periodic exposure scan - because the real risk is drift, not design.

## Detail

**Layer 1 - edge.** Anycast DDoS protection (Shield Advanced, Cloud Armor, Azure DDoS Protection) in front of a CDN, with a WAF running managed rulesets for the OWASP categories plus rate limiting per IP and per token. Terminate TLS at the edge and re-encrypt inward; enforce TLS 1.2 minimum, HSTS, and modern ciphers. Keep origin addresses non-public and only reachable from the CDN's ranges or via a signed header - an origin discoverable by IP scan makes the entire edge optional for an attacker.

**Layer 2 - perimeter and topology.** Public subnets hold only load balancers and NAT; every workload sits in private subnets with no public IP. Administrative access is via a bastion-free path - SSM Session Manager, Azure Bastion, IAP - so there is no port 22 open anywhere and every session is logged and authorised by IAM. Management planes (databases, caches, control APIs) get their own subnets and their own rules.

**Layer 3 - segmentation, which is where most designs are thin.** Per-tier security groups that reference _each other_ rather than CIDR ranges: `db` accepts 5432 only from `app`'s security group. That is identity-based microsegmentation and it survives IP changes. Inside Kubernetes, a **default-deny** NetworkPolicy per namespace plus explicit allows - without it, any compromised Pod can reach every service in the cluster, which is the single most common gap in otherwise well-secured clusters. Separate environments into separate accounts, subscriptions, or projects rather than separate subnets; an account boundary is far harder to cross by mistake.

**Layer 4 - identity as a network control.** The network should not be your only trust boundary. mTLS between services (via a mesh, or in-application) means a machine on the right subnet still cannot talk to a service without a valid workload identity. This is the core of zero trust: authenticate and authorise every connection, and treat the internal network as hostile. Practical minimum: workload identity federation instead of long-lived keys, short-lived certificates, and authorisation policies keyed on service identity.

**Layer 5 - egress, the layer teams forget.** Most designs are strict inbound and wide open outbound, which is exactly backwards for containing a compromise - exfiltration and command-and-control are outbound. Route egress through a NAT plus a firewall that allowlists destinations by FQDN (AWS Network Firewall, Azure Firewall, Cloud NGFW, or Squid), block direct outbound from workload subnets, use private endpoints for provider services so that traffic never touches the internet, and log every DNS query - DNS logs catch beaconing that HTTP logs miss.

**Layer 6 - detection and response.** VPC flow logs and DNS query logs into your SIEM with retention long enough for an investigation, GuardDuty / Defender for Cloud / Security Command Center for managed detection, an IDS on the traffic mirror for high-value segments, and alerts on the things that mean a layer already failed: a new public IP or open security group, egress to a destination outside the allowlist, an unusual cross-account API call, a spike in denied connections. Have the containment runbook written: how you isolate a compromised instance (swap to a quarantine security group, snapshot for forensics, revoke its role's sessions) without destroying evidence.

**Layer 7 - keep it from decaying.** Design is easy; drift is what gets you. Policy-as-code in the pipeline (no `0.0.0.0/0` on anything but 443 to a load balancer, no public S3, no unencrypted transit), SCPs or Azure Policy as the guardrail that cannot be overridden by a team, an automated external exposure scan that compares reality against the intended surface, and a periodic review of every remaining `0.0.0.0/0` rule with a named owner. Most breaches trace back to a control that existed on the diagram and not in the account.

## Example

```hcl
# Segmentation by identity, not by CIDR. The db rule survives every IP change.
resource "aws_security_group" "app" { vpc_id = aws_vpc.main.id }
resource "aws_security_group" "db"  { vpc_id = aws_vpc.main.id }

resource "aws_security_group_rule" "db_ingress_from_app" {
  type                     = "ingress"
  security_group_id        = aws_security_group.db.id
  source_security_group_id = aws_security_group.app.id # identity-based
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
}

# Egress: deny by default, then allowlist. The layer most designs skip.
resource "aws_security_group_rule" "app_egress_https_only" {
  type              = "egress"
  security_group_id = aws_security_group.app.id
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  prefix_list_ids   = [aws_ec2_managed_prefix_list.allowed_egress.id]
}

resource "aws_networkfirewall_rule_group" "fqdn_allowlist" {
  capacity = 100
  type     = "STATEFUL"
  rule_group {
    rules_source {
      rules_source_list {
        generated_rules_type = "ALLOWLIST"
        target_types         = ["TLS_SNI", "HTTP_HOST"]
        targets              = ["api.stripe.com", ".amazonaws.com", "registry.npmjs.org"]
      }
    }
  }
}
```

```yaml
# Default-deny inside the cluster. Without this, one compromised Pod reaches everything.
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny-all, namespace: payments }
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: allow-checkout-and-dns, namespace: payments }
spec:
  podSelector: { matchLabels: { app: payments } }
  policyTypes: [Ingress, Egress]
  ingress:
    - from:
        - namespaceSelector: { matchLabels: { name: checkout } }
          podSelector: { matchLabels: { app: checkout } }
      ports: [{ port: 8443, protocol: TCP }]
  egress:
    - to: [{ namespaceSelector: { matchLabels: { name: kube-system } } }]
      ports: [{ port: 53, protocol: UDP }] # DNS must be allowed explicitly
    - to: [{ ipBlock: { cidr: 10.20.30.0/24 } }] # database subnet only
      ports: [{ port: 5432, protocol: TCP }]
```

```yaml
# The guardrail a team cannot override, and the drift alert for when one is added anyway.
# SCP: deny removing flow logs, and deny security-group ingress edits outside network-admin.
# Note: these EC2 actions cannot be conditioned on port or CIDR, so the SCP is a blunt
# "only network-admin edits ingress" control - the SSH-to-0.0.0.0/0 case is caught by the
# drift query below (and a Config rule), not by the policy condition.
Statement:
  - Effect: Deny
    Action:
      - "ec2:DeleteFlowLogs"
      - "ec2:ModifyVpcAttribute"
      - "ec2:AuthorizeSecurityGroupIngress"
      - "ec2:ModifySecurityGroupRules"
    Resource: "*"
    Condition: { ArnNotLike: { "aws:PrincipalArn": "arn:aws:iam::*:role/network-admin" } }
```

```bash
# Find the layer that already drifted.
aws ec2 describe-security-groups \
  --query "SecurityGroups[?IpPermissions[?contains(IpRanges[].CidrIp, '0.0.0.0/0')
           && ToPort != \`443\`]].[GroupId,GroupName]" --output table
kubectl get netpol -A                       # namespaces with none are wide open internally
aws ec2 describe-instances \
  --query 'Reservations[].Instances[?PublicIpAddress!=null].[InstanceId,PublicIpAddress]'
```

## Interview tips

- Frame it as "assume each control fails" and then walk outside-in through the layers. The framing matters more than the tool names.
- Security groups referencing security groups is the concrete detail that shows real design experience. Contrast it with CIDR-based rules.
- Default-deny NetworkPolicy in Kubernetes is the gap interviewers most often test. Say that without it, lateral movement inside the cluster is free.
- Egress control is the layer most candidates omit entirely. Bring it up unprompted, and connect it to exfiltration and command-and-control.
- Say the network is not the only trust boundary - mTLS and workload identity - and name that as the zero-trust position.
- Include detection and the containment runbook: quarantine security group, snapshot for forensics, revoke role sessions. Preserving evidence is a senior detail.
- Finish on drift: policy-as-code, SCPs, and an exposure scan. "The control was on the diagram, not in the account" is the sentence that lands.

---

[⬅ Back to Network Security](./README.md) · [All topics](../README.md)
