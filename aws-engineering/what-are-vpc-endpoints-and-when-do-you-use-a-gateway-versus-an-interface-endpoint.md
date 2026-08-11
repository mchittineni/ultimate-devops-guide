---
title: "What are VPC endpoints, and when do you use a gateway versus an interface endpoint?"
id: 474
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - aws-engineering
  - interview-questions
  - network-security
  - cloud-cost-optimization
---

# What are VPC endpoints, and when do you use a gateway versus an interface endpoint?

**Short answer:** A VPC endpoint lets resources inside your VPC reach an AWS service **without traversing the internet** - no internet gateway, no NAT gateway, no public IP. There are two kinds and they work completely differently. A **gateway endpoint** exists only for **S3 and DynamoDB**: it is a **route-table entry** pointing at a prefix list, it costs nothing, and it is regional. An **interface endpoint** (PrivateLink) puts an **actual ENI with a private IP into your subnets** for the service, and you reach it by DNS - it works with most AWS services, supports cross-VPC and cross-account access, works over Direct Connect and VPN, and charges per hour per AZ plus per GB. So: S3 and DynamoDB at high volume → gateway endpoint (free, and the reason "does S3 sit inside a VPC?" has a nuanced answer); everything else, or anything that must be reachable from on-premises or another VPC → interface endpoint.

## Detail

### The comparison

|                                               | Gateway endpoint                            | Interface endpoint (PrivateLink)                         |
| --------------------------------------------- | ------------------------------------------- | -------------------------------------------------------- |
| Services                                      | **S3 and DynamoDB only**                    | Most AWS services, plus partner and your own services    |
| Mechanism                                     | Route table entry → prefix list             | ENI with a private IP in each chosen subnet              |
| How traffic is directed                       | Routing - transparent, same public DNS name | **DNS** - private hosted zone overrides the service name |
| Cost                                          | **Free**                                    | Hourly per endpoint per AZ + per GB processed            |
| Reachable from on-premises (DX/VPN)           | **No**                                      | **Yes**                                                  |
| Reachable from a peered VPC / another account | No                                          | Yes                                                      |
| Security controls                             | Endpoint policy                             | Endpoint policy **and a security group** on the ENI      |
| Scope                                         | Regional, per route table                   | Per subnet/AZ                                            |

The two limitations of gateway endpoints - no on-premises reachability and no cross-VPC use - are the reason S3 also has an interface endpoint option. If your data centre needs private S3 access over Direct Connect, you need the interface endpoint even though the gateway one is free.

### "Does S3 live inside your VPC?"

This is asked constantly, and the precise answer earns credit: **no**. S3 is a regional service with a public endpoint, outside any VPC, reached over the AWS network. A VPC-bound workload gets to it in one of three ways:

1. Via a **NAT gateway** and internet gateway - the traffic leaves your VPC (it stays on the AWS backbone, but it goes out through your public egress path) and you pay NAT processing charges on every byte.
2. Via a **gateway endpoint** - a route for the S3 prefix list sends the traffic straight out of the VPC to S3 privately, free, with no NAT involved.
3. Via an **interface endpoint** - an ENI in your subnet, so S3 has a private IP inside your address space, reachable from peered VPCs and on-premises.

The same reasoning applies to DynamoDB, and to the general class of "the service is regional, not in your VPC".

### Why this is a cost answer as much as a security answer

A private subnet whose workloads pull container images from ECR, read secrets from Secrets Manager, write logs to CloudWatch, and store objects in S3 will push **all** of that through the NAT gateway if you do nothing - and NAT charges per GB processed on top of its hourly rate. Container image pulls alone can dominate a NAT bill. Adding a gateway endpoint for S3 (free) plus interface endpoints for `ecr.api`, `ecr.dkr`, `logs`, `secretsmanager`, and `sts` frequently cuts NAT costs by most of their value, and in some architectures removes the need for a NAT gateway entirely - at which point the subnet has **no route to the internet at all**, which is a materially stronger security posture.

Note the arithmetic though: an interface endpoint costs per hour **per AZ**, so a handful of endpoints across three AZs has a real floor. For low-volume traffic, NAT may still be cheaper. Do the sum rather than reciting a rule.

### The ECR gotcha

Pulling from ECR needs **three** things privately: the `ecr.api` interface endpoint (authentication and metadata), the `ecr.dkr` interface endpoint (the Docker registry protocol), **and** an **S3 gateway endpoint**, because the image layers themselves are served from S3. Teams add the two ECR endpoints, remove the NAT, and then discover image pulls fail on layer download. Knowing that detail is a strong signal of hands-on work.

### Endpoint policies - the security control people forget

An endpoint has its own resource policy, which is a second, independent gate on top of IAM. That lets you enforce things IAM alone cannot:

- **Only my buckets**: an S3 endpoint policy that denies access to any bucket outside your organisation, which blocks data exfiltration to a personal bucket even by a principal with broad S3 permissions.
- **Only my organisation**: `aws:PrincipalOrgID` conditions.
- From the other direction, a **bucket policy** with `aws:SourceVpce` can require that access arrives through your endpoint - so credentials leaked outside the VPC are useless against that bucket.

That pairing (endpoint policy restricting destinations, bucket policy restricting sources) is the exfiltration-prevention pattern worth naming.

### Private DNS, and the failure mode

Interface endpoints work by DNS. With **`privateDnsEnabled: true`**, AWS creates a private hosted zone so `secretsmanager.eu-west-1.amazonaws.com` resolves to the endpoint's private IP inside your VPC - meaning your application and SDKs need **no code change**. This requires `enableDnsSupport` and `enableDnsHostnames` on the VPC; if either is off, resolution silently falls back to the public IP and your traffic goes out via NAT (or fails, if there is no NAT). "I created the endpoint and traffic still goes through the NAT" is almost always private DNS being disabled or a VPC DNS attribute being off.

The other common failure is the **security group on the endpoint ENI**: it must allow inbound 443 from your workload's CIDR or security group. A new endpoint with a default security group that allows nothing produces timeouts that look like a routing problem.

### PrivateLink for your own services

The same mechanism exposes a service you own to other VPCs or accounts without peering, without overlapping-CIDR problems, and with a one-way relationship: put an NLB (or GWLB) in front of your service, create a **VPC endpoint service**, and share it with specific principals who create interface endpoints in their own VPCs. This is the clean answer to "two VPCs must communicate but their CIDRs overlap and Transit Gateway is not allowed" - PrivateLink is unidirectional and address-space agnostic, so overlap does not matter. See [how do you connect many VPCs](./how-do-you-connect-many-vpcs-peering-transit-gateway-or-privatelink.md).

## Example

```hcl
# Gateway endpoint: free, route-based, S3 and DynamoDB only
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.this.id
  service_name      = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [for rt in aws_route_table.private : rt.id] # it IS a route

  policy = jsonencode({          # a second gate: no exfiltration to foreign buckets
    Statement = [{
      Effect    = "Allow"
      Principal = "*"
      Action    = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
      Resource  = ["arn:aws:s3:::acme-*", "arn:aws:s3:::acme-*/*",
                   "arn:aws:s3:::prod-*-ecr-layers/*"]  # ECR layer bucket
    }]
  })
}

# Interface endpoints: ENIs in your subnets, reached by DNS
locals {
  interface_services = [
    "ecr.api", "ecr.dkr",        # image pulls: BOTH, plus the S3 gateway endpoint above
    "logs", "monitoring",        # CloudWatch Logs and metrics
    "secretsmanager", "ssm", "ssmmessages", "ec2messages", # SSM Session Manager
    "sts", "kms", "elasticloadbalancing",
  ]
}

resource "aws_vpc_endpoint" "interface" {
  for_each            = toset(local.interface_services)
  vpc_id              = aws_vpc.this.id
  service_name        = "com.amazonaws.${var.region}.${each.key}"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [for s in aws_subnet.private : s.id] # one ENI per AZ
  security_group_ids  = [aws_security_group.endpoints.id]
  private_dns_enabled = true # without this, SDKs still resolve the PUBLIC name
}

resource "aws_security_group" "endpoints" {
  name   = "vpc-endpoints"
  vpc_id = aws_vpc.this.id
  ingress {                                   # the endpoint ENI must accept 443
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.this.cidr_block]
  }
}
```

```json
// Bucket policy: require that access arrives through OUR endpoint.
// Leaked credentials used from outside the VPC then fail.
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyAccessNotThroughOurVpce",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": ["arn:aws:s3:::acme-prod-data", "arn:aws:s3:::acme-prod-data/*"],
      "Condition": { "StringNotEquals": { "aws:SourceVpce": "vpce-0abc123def456" } }
    }
  ]
}
```

```bash
# Is my traffic actually private? Resolve the service name from inside the VPC.
nslookup secretsmanager.eu-west-1.amazonaws.com
#   10.20.3.47  -> private IP: going through the interface endpoint
#   52.x.x.x    -> public IP:  private DNS is off, or a VPC DNS attribute is disabled

aws ec2 describe-vpc-attribute --vpc-id vpc-0abc --attribute enableDnsSupport
aws ec2 describe-vpc-attribute --vpc-id vpc-0abc --attribute enableDnsHostnames

# Confirm the S3 route exists (gateway endpoints are routes, not DNS)
aws ec2 describe-route-tables --route-table-ids rtb-0abc \
  --query 'RouteTables[0].Routes[?starts_with(DestinationPrefixListId || ``, `pl-`)]'

# Prove the cost case before and after
aws cloudwatch get-metric-statistics --namespace AWS/NATGateway \
  --metric-name BytesOutToDestination --statistics Sum --period 86400 \
  --start-time "$(date -u -d '-14 days' +%FT%TZ)" --end-time "$(date -u +%FT%TZ)" \
  --dimensions Name=NatGatewayId,Value=nat-0abc123
```

## Interview tips

- Distinguish the two types by **mechanism** first: a gateway endpoint is a route-table entry (S3 and DynamoDB only, free); an interface endpoint is an ENI with a private IP reached by DNS (most services, costs money). That framing makes the rest derivable.
- Name the two things a gateway endpoint cannot do - on-premises access over Direct Connect/VPN, and cross-VPC or cross-account use - because that is exactly when you pay for an interface endpoint to S3 instead.
- Answer "does S3 sit in your VPC?" with a clear no plus the three access paths (NAT, gateway endpoint, interface endpoint). Interviewers use this to check whether you know where AWS service boundaries actually are.
- Make the cost argument concretely: ECR pulls, CloudWatch Logs, and S3 through a NAT gateway are charged per GB, and endpoints often remove most of that - sometimes removing the NAT entirely, which also removes any internet route from the subnet.
- Volunteer the ECR gotcha: `ecr.api` **and** `ecr.dkr` **and** an S3 gateway endpoint, because layers come from S3. It is the detail that proves you have built this.
- Mention endpoint policies as a second, independent gate, and the `aws:SourceVpce` bucket-policy condition as the exfiltration control. Very few candidates raise data-exfiltration prevention here.
- Have the two failure modes ready: private DNS disabled (or VPC DNS attributes off) so traffic silently uses the public endpoint, and a security group on the endpoint ENI that does not allow 443.
- Close with PrivateLink for your own services as the answer to overlapping CIDRs where peering or Transit Gateway is not an option. See [how does a private subnet reach the internet](./how-does-a-private-subnet-reach-the-internet.md), [connecting many VPCs](./how-do-you-connect-many-vpcs-peering-transit-gateway-or-privatelink.md), [designing a production-ready VPC](./how-do-you-design-a-production-ready-vpc-on-aws.md), and [cutting a cloud bill without hurting reliability](../cloud-cost-optimization/how-do-you-cut-a-cloud-bill-without-hurting-reliability.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you debug DNS resolution failures inside a Kubernetes cluster?]] (`#404`): [How do you debug DNS resolution failures inside a Kubernetes cluster?](../kubernetes/how-do-you-debug-dns-resolution-failures-inside-a-kubernetes-cluster.md)
- [[How do requests, limits, and QoS classes work in Kubernetes?]] (`#444`): [How do requests, limits, and QoS classes work in Kubernetes?](../kubernetes/how-do-requests-limits-and-qos-classes-work-in-kubernetes.md)
- [[How does Pod networking and service discovery work in Kubernetes?]] (`#447`): [How does Pod networking and service discovery work in Kubernetes?](../kubernetes/how-does-pod-networking-and-service-discovery-work-in-kubernetes.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
