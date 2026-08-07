---
title: "How do you design a production-ready VPC on AWS?"
id: 191
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - aws-engineering
  - interview-questions
---

# How do you design a production-ready VPC on AWS?

**Short answer:** Three subnet tiers (public, private with egress, isolated) spread across at least three Availability Zones, a NAT gateway per AZ, VPC endpoints for the AWS services you use heavily, security groups referencing other security groups rather than CIDRs, and flow logs enabled. Size the CIDR generously and non-overlapping with everything you might ever peer to.

## Detail

**Subnet tiers and what belongs in each.** Public subnets (route to an internet gateway) hold only load balancers and NAT gateways. Private subnets hold application workloads and reach the internet through NAT. Isolated subnets hold databases and have no route to the internet at all. The tiering is what makes "the database is not reachable from the internet" a property of routing rather than of a firewall rule someone might change.

**Availability Zones and NAT cost.** Use three AZs for quorum-based systems and to survive one AZ loss without capacity panic. A NAT gateway per AZ avoids cross-AZ data charges and removes a single AZ as a dependency for all egress — but each one costs an hourly fee plus per-GB processing, and NAT data processing is a top-three surprise on many AWS bills. Gateway endpoints for S3 and DynamoDB are free and remove that traffic from NAT entirely; interface endpoints for other services cost per hour per AZ but often still win against NAT charges.

**CIDR planning is the decision you cannot undo cheaply.** Pick a /16 from RFC 1918 space that does not overlap your on-premises networks, other accounts, or acquisitions. Subnets should be large enough for EKS, where each Pod consumes a VPC IP address with the AWS VPC CNI — /20 per AZ for a Pod subnet is common, and IP exhaustion is the single most frequent EKS scaling wall. Secondary CIDRs can be added later, but not overlapping ones.

**Security groups over NACLs.** Security groups are stateful and can reference other security groups, so "the app tier may reach the database tier" is expressed as identity rather than as addresses that change. Network ACLs are stateless, per-subnet, and mainly useful as a coarse, rarely-changed guardrail (for example, denying a known-bad range).

**Observability and egress control.** Enable VPC flow logs (to S3 for cost, or CloudWatch for querying) — you cannot investigate an incident without them. For regulated environments, force egress through a central inspection point (Network Firewall or a proxy in a shared services account, reached via Transit Gateway) rather than letting every VPC talk directly to the internet.

## Example

```hcl
# Three-tier, three-AZ VPC with per-AZ NAT and free S3/DynamoDB endpoints
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.13"

  name = "prod"
  cidr = "10.40.0.0/16"

  azs              = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
  public_subnets   = ["10.40.0.0/20", "10.40.16.0/20", "10.40.32.0/20"]
  private_subnets  = ["10.40.64.0/19", "10.40.96.0/19", "10.40.128.0/19"] # Pod IPs live here
  database_subnets = ["10.40.200.0/24", "10.40.201.0/24", "10.40.202.0/24"]

  enable_nat_gateway     = true
  single_nat_gateway     = false # one per AZ: no cross-AZ charge, no shared failure
  one_nat_gateway_per_az = true

  enable_flow_log                      = true
  flow_log_destination_type            = "s3"
  create_flow_log_cloudwatch_log_group = false

  tags = { environment = "prod", owner = "platform" }
}
```

## Interview tips

- Lead with the three-tier, three-AZ layout, then justify per-AZ NAT on both cost and failure-domain grounds.
- EKS IP exhaustion with the VPC CNI is the practical war story worth naming.
- Expect: "security groups or NACLs?" — security groups referencing security groups, with NACLs as a coarse guardrail only.

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
