---
title: "How Do You Secure and Inspect Egress Traffic on AWS Using AWS Network Firewall?"
id: 733
category: "AWS Engineering"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - aws-engineering
  - network-firewall
  - egress-filtering
  - vpc-security
quiz:
  stem: "Why can AWS Network Firewall filter outbound HTTPS traffic by domain name (e.g., allow only *.github.com) without breaking TLS encryption?"
  options:
    - "It forces all clients to use unencrypted HTTP ports."
    - "It inspects the plaintext Server Name Indication (SNI) field present in the client's initial TLS handshake."
    - "It installs a private root certificate inside every internet web server."
    - "It translates all outbound domain names to private RFC 1918 IP addresses."
  answer: 2
  explanation: "During the initial TLS handshake, the client sends the Server Name Indication (SNI) in plaintext before encryption is established. AWS Network Firewall inspects this SNI header to enforce domain allowlists."
---

# How Do You Secure and Inspect Egress Traffic on AWS Using AWS Network Firewall?

**Short answer:** AWS Network Firewall provides stateful egress inspection, domain name allowlisting/denylisting, and Suricata-compatible IPS rules. It is deployed in dedicated inspection VPC subnets using route table manipulation to intercept and filter all internet-bound traffic before reaching the NAT Gateway.

## Detail

### The Vulnerability of Unrestricted Egress

While organizations invest heavily in securing ingress traffic (WAF, ALB, security groups), egress traffic is frequently left uninspected (`0.0.0.0/0` allowed through NAT Gateways). Compromised instances can freely exfiltrate data, query malware command-and-control (C2) servers, or download remote payloads.

### AWS Network Firewall Architecture

AWS Network Firewall is a managed, stateful network inspection service that scales automatically with VPC traffic.

### Egress Routing Architecture

To inspect all outbound internet traffic from private subnets:

1. **Workload Subnet Route Table**: Routes `0.0.0.0/0` to the **Network Firewall endpoint** in the same AZ.
2. **Firewall Subnet Route Table**: Routes permitted traffic `0.0.0.0/0` to the **NAT Gateway**.
3. **NAT Gateway (public) Subnet Route Table**: Routes `0.0.0.0/0` to the **Internet Gateway**, and routes the **workload subnet CIDRs back to the firewall endpoint** so return traffic is inspected symmetrically.
4. **IGW ingress route table** (edge association) is only needed when the firewall must also inspect traffic to resources with public IPs, such as a public ALB.

In multi-VPC estates the usual pattern is a central **inspection VPC** attached to Transit Gateway (with appliance mode enabled so flows stay symmetric), and Network Firewall can now attach to a Transit Gateway directly, removing the need to build and route the inspection VPC yourself.

```text
[Workload EC2 / Pod]
         │
         ▼ (Route 0.0.0.0/0)
[AWS Network Firewall Endpoint] ──► Stateful Domain & IPS Inspection
         │ (If Allowed)
         ▼
[NAT Gateway]
         │
         ▼
[Internet Gateway (IGW)] ──► Public Internet
```

### Key Inspection Capabilities

- **Stateful Domain Name Filtering**: Uses SNI (Server Name Indication) in TLS handshakes and HTTP Host headers to enforce strict domain allowlists (e.g., only allow `*.github.com` and `pypi.org`; drop everything else).
- **Suricata-Compatible Intrusion Prevention (IPS)**: Inspects packet payloads for known malware signatures, exploit patterns, and unauthorized SSH/tunnel protocols.
- **Stateless Rules**: High-speed 5-tuple filtering (source/dest IP, port, protocol) evaluated before stateful engines.
- **TLS inspection** (optional): decrypts and re-encrypts traffic with your certificate for payload inspection - powerful, but it adds certificate management and breaks certificate-pinned clients.

**Limitations.** SNI filtering sees the hostname the client claims, so a malicious client can lie or use encrypted ClientHello; domain filtering is a strong control for well-behaved workloads, not a guarantee. The firewall is also billed per endpoint-hour per AZ plus per GB, on top of NAT.

### Real-World Production Scenario

A payment processing cluster inside a private VPC must only communicate with approved external banking APIs. Using AWS Network Firewall, engineers apply stateful domain allowlist rules permitting only the banks' API domains (for example `.api.examplebank.com`). When an attacker exploits an SSRF vulnerability on an application server to exfiltrate database credentials to an external pastebin site, the firewall drops the packet and logs the alert to CloudWatch.

## Example

```bash
# Stateful domain allowlist: only these domains may be reached over TLS (SNI) or HTTP (Host)
aws network-firewall create-rule-group --rule-group-name egress-allowlist \
  --type STATEFUL --capacity 100 \
  --rule-group '{
    "RulesSource": {
      "RulesSourceList": {
        "Targets": [".github.com", "pypi.org", ".api.examplebank.com"],
        "TargetTypes": ["TLS_SNI", "HTTP_HOST"],
        "GeneratedRulesType": "ALLOWLIST"
      }
    }
  }'

# Workload subnet: default route to the firewall endpoint in the same AZ
aws ec2 create-route --route-table-id rtb-workload-a \
  --destination-cidr-block 0.0.0.0/0 --vpc-endpoint-id vpce-0fw1234567890abcd

# NAT subnet: return path to the workload CIDR goes back through the firewall (symmetry)
aws ec2 create-route --route-table-id rtb-nat-a \
  --destination-cidr-block 10.0.16.0/20 --vpc-endpoint-id vpce-0fw1234567890abcd
```

```text
# Suricata-compatible stateful rule: block SSH leaving the VPC, alert on it
drop tcp $HOME_NET any -> $EXTERNAL_NET 22 (msg:"Outbound SSH blocked"; sid:1000001; rev:1;)
```

## Interview tips

- Explain that standard NAT Gateways and Security Groups cannot filter traffic by domain name (FQDN); AWS Network Firewall solves this with stateful SNI inspection.
- Describe the routing path: private subnet -> firewall endpoint -> NAT gateway -> Internet gateway, and the return route from the NAT subnet back through the firewall endpoint (symmetric routing).
- Mention Suricata rule compatibility as a major advantage for security teams with existing signature libraries.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?]] (`#407`): [How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-waiting-for-a-persistentvolumeclaim.md)
- [[What is Cloud Computing?]] (`#21`): [What is Cloud Computing?](../cloud-platforms/what-is-cloud-computing.md)
- [[What is AWS (Amazon Web Services)?]] (`#22`): [What is AWS (Amazon Web Services)?](../cloud-platforms/what-is-aws-amazon-web-services.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
