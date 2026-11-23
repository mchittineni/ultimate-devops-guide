---
title: "What is AWS PrivateLink and How Does It Enable Secure Cross-VPC Service Consumption?"
id: 734
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - aws-engineering
  - privatelink
  - vpc-endpoints
  - security
quiz:
  stem: "Which major networking problem does AWS PrivateLink resolve that traditional AWS VPC Peering cannot handle?"
  options:
    - "PrivateLink eliminates the need for DNS servers across the organization."
    - "PrivateLink connects services across VPCs with overlapping CIDR IP blocks without requiring network re-addressing."
    - "PrivateLink enables public internet users to bypass web application firewalls."
    - "PrivateLink allows physical on-premises servers to run EC2 AMIs natively."
  answer: 2
  explanation: "VPC Peering strictly prohibits overlapping IP address ranges between VPCs. PrivateLink connects services via an ENI in the consumer VPC, entirely avoiding IP conflicts and routing table peering requirements."
---

# What is AWS PrivateLink and How Does It Enable Secure Cross-VPC Service Consumption?

**Short answer:** AWS PrivateLink exposes services hosted in one VPC to consumers in other VPCs or on-premises over the private AWS network backbone using Interface VPC Endpoints and Network Load Balancers, without requiring VPC peering, internet gateways, or route table changes.

## Detail

### The Architectural Challenge of Cross-VPC Sharing

When sharing internal microservices or consuming third-party SaaS platforms (e.g., Snowflake, Datadog), traditional options like VPC Peering or public internet routing present drawbacks:

- **IP Overlap**: VPC Peering fails if consumer and provider VPCs share overlapping CIDR blocks (e.g., both use `10.0.0.0/16`).
- **Broad Exposure**: VPC Peering connects entire network subnets rather than exposing a single specific service.
- **Security Risks**: Routing over the public internet requires NAT Gateways, public IPs, and firewall rules.

### How AWS PrivateLink Works

PrivateLink establishes a private, unidirectional connection between a **Service Provider VPC** and a **Consumer VPC**.

1. **Provider Setup**:
   - The provider runs services behind a **Network Load Balancer (NLB)**.
   - The provider creates an **Endpoint Service** configuration, specifying allowed AWS account IDs.
2. **Consumer Setup**:
   - The consumer creates an **Interface VPC Endpoint** targeting the provider's Endpoint Service.
   - AWS automatically provisions an **Elastic Network Interface (ENI)** inside the consumer's private subnet.
   - The ENI receives a private IP address directly from the consumer's local subnet CIDR.
3. **Data Path**:
   - Consumer applications send traffic to the local ENI private IP.
   - Traffic flows securely over the AWS private hypervisor fabric directly to the provider's NLB.

```text
[Consumer VPC (10.0.0.0/16)]               [Provider VPC (10.0.0.0/16)]
 Workload Pod                               Application Pods
      │                                            ▲
      ▼ (Local Private IP)                         │
 [Interface Endpoint ENI] ──► AWS Hypervisor ──► [NLB]
                               Private Fabric
```

### Key Architectural Benefits

- **Overlapping CIDRs**: Because traffic terminates at the local ENI and undergoes network address translation at the hypervisor, overlapping IP ranges are completely supported.
- **Least-Privilege Connectivity**: Consumers only reach the specific TCP ports and services exposed by the provider's NLB—not other resources in the provider's VPC.
- **Secure SaaS Consumption**: Connect to external SaaS providers without traffic ever traversing the public internet.
- **Cross-region**: interface endpoints can now connect to endpoint services in other Regions natively, without building a relay in each Region.
- **Resource endpoints (VPC Lattice-based)**: you can share a specific resource such as an RDS database or an IP/DNS target through PrivateLink without putting an NLB in front of it.

**Limitations.** Connections are one-way and TCP only through the NLB, the provider sees traffic from NLB addresses rather than the consumer's real IPs (unless you use proxy protocol), and interface endpoints cost per AZ-hour plus per GB - many services times many AZs adds up.

### Real-World Production Scenario

A SaaS provider hosts an analytics platform in AWS and sells to Fortune 500 banks. The banks refuse to allow their financial data to traverse the public internet or peer VPCs due to overlapping IP space. The SaaS provider configures AWS PrivateLink, allowing the banks to query the service as a local private IP inside their existing private subnets.

### Scenario: a third party needs direct access to our database

A frequent follow-up is "a partner needs to query our RDS database - do we put it in a public subnet?" Push back first: a publicly reachable database is the last resort. In order of preference:

1. **Keep it private and use PrivateLink.** If the partner has an AWS account, share the database as a **resource endpoint** (or put an NLB in front and publish an endpoint service). They get a private IP in their own VPC; nothing has a public address, and overlapping CIDRs do not matter.
2. **Site-to-Site VPN** (or the partner's Direct Connect) if they are on-premises, with security groups allowing only their routed ranges.
3. **A narrow API or proxy** in front of the data, which is often what they actually need, rather than SQL access at all.

If it genuinely must be public, compensate with layered controls:

- Security group allowing only the partner's fixed **/32 egress IPs** on the database port - never `0.0.0.0/0` - and ideally a **read replica** in a dedicated subnet rather than the primary.
- **TLS enforced** on the server (`rds.force_ssl = 1` for PostgreSQL, `require_secure_transport = ON` for MySQL) with the client verifying the RDS CA certificate (`sslmode=verify-full`).
- A **dedicated least-privilege database user** (read-only, limited to specific views or schemas), with IAM database authentication or Secrets Manager rotation rather than a shared password.
- **Audit and expiry**: database audit logging (for example `pgaudit`), GuardDuty RDS Protection, alarms on failed logins and connection counts, and a review date after which the access is removed.

IP allowlisting plus TLS plus IAM authentication is a reasonable answer, but naming the private options first is what shows judgement.

## Example

```bash
# Provider: endpoint service in front of an NLB, restricted to one consumer account
aws ec2 create-vpc-endpoint-service-configuration \
  --network-load-balancer-arns arn:aws:elasticloadbalancing:eu-west-1:111122223333:loadbalancer/net/analytics/abc123 \
  --acceptance-required
aws ec2 modify-vpc-endpoint-service-permissions --service-id vpce-svc-0abc123 \
  --add-allowed-principals arn:aws:iam::444455556666:root

# Consumer (in their own VPC, same CIDR is fine): interface endpoint with its own SG
aws ec2 create-vpc-endpoint --vpc-id vpc-0consumer --vpc-endpoint-type Interface \
  --service-name com.amazonaws.vpce.eu-west-1.vpce-svc-0abc123 \
  --subnet-ids subnet-0a subnet-0b --security-group-ids sg-0endpoint

# Provider accepts the connection request
aws ec2 accept-vpc-endpoint-connections --service-id vpce-svc-0abc123 \
  --vpc-endpoint-ids vpce-0consumer123
```

```bash
# Last-resort public database for a partner: only their egress IP, TLS enforced
aws ec2 authorize-security-group-ingress --group-id sg-0partnerdb \
  --protocol tcp --port 5432 --cidr 203.0.113.10/32
aws rds modify-db-parameter-group --db-parameter-group-name partner-replica-pg \
  --parameters "ParameterName=rds.force_ssl,ParameterValue=1,ApplyMethod=immediate"
```

## Interview tips

- Highlight that PrivateLink works seamlessly across overlapping CIDR blocks, which is a major limitation of VPC Peering.
- Explain the difference between Gateway Endpoints (free, routing-table based for S3 and DynamoDB) and Interface Endpoints (ENI-based, powered by PrivateLink).
- Mention unidirectional connectivity: consumers can initiate connections to providers, but providers cannot initiate connections back into consumer networks.
- For "a third party needs our database", offer PrivateLink (a resource endpoint or an NLB-backed endpoint service) or a VPN before a public endpoint; if it must be public, list /32 allowlisting, enforced TLS, a dedicated least-privilege user, audit logging and an expiry date.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does the Cloud Shared Responsibility Model divide security obligations between IaaS, PaaS, and SaaS?]] (`#543`): [How does the Cloud Shared Responsibility Model divide security obligations between IaaS, PaaS, and SaaS?](../cloud-platforms/how-does-the-cloud-shared-responsibility-model-divide-security-obligations-between-iaas-paas-and-saas.md)
- [[How does Cloud IAM Role Federation differ from static Service Account keys?]] (`#546`): [How does Cloud IAM Role Federation differ from static Service Account keys?](../cloud-platforms/how-does-cloud-iam-role-federation-differ-from-static-service-account-keys.md)
- [[What is Cloud Computing?]] (`#21`): [What is Cloud Computing?](../cloud-platforms/what-is-cloud-computing.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
