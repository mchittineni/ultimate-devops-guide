---
title: "How does a private subnet reach the internet?"
id: 473
category: "AWS Engineering"
difficulty: "Beginner"
tags:
  - devops
  - aws-engineering
  - interview-questions
  - network-security
---

# How does a private subnet reach the internet?

**Short answer:** Through a **NAT gateway that lives in a public subnet**. What makes a subnet "public" or "private" is only its **route table**: a public subnet has a route `0.0.0.0/0 → internet gateway`; a private subnet has `0.0.0.0/0 → nat-xxxx`. The NAT gateway sits in the public subnet (so _its_ default route reaches the internet gateway), holds an Elastic IP, and translates the private instance's source address on the way out. That gives **outbound-only** connectivity: the private instance can initiate connections out, but nothing on the internet can initiate a connection in, because the NAT has no way to map an unsolicited inbound packet to a private host. For inbound traffic to a private instance you do not use NAT at all - you put a **load balancer in the public subnets** with targets in the private ones, or use a VPC endpoint / PrivateLink for AWS and partner services.

## Detail

### What makes a subnet public or private

Nothing about the subnet object itself - it is the route table association:

```text
public subnet   route table:  10.20.0.0/16 -> local
                              0.0.0.0/0    -> igw-xxxx        <- this line, and only this
private subnet  route table:  10.20.0.0/16 -> local
                              0.0.0.0/0    -> nat-xxxx        <- via NAT, outbound only
isolated subnet route table:  10.20.0.0/16 -> local           <- no default route at all
```

So the answer to "how can you tell whether a subnet is public or private?" is: look at its route table for a `0.0.0.0/0` route to an internet gateway. Auto-assign public IP being enabled is a hint, not the definition - an instance with a public IP in a subnet with no IGW route still cannot reach the internet, and that is a genuinely common misconfiguration.

### Why the NAT gateway must be in a public subnet

This is the question interviewers ask to see whether you understand routing rather than diagrams. The NAT gateway is itself a resource that needs to reach the internet: it takes the private instance's traffic, rewrites the source to its own Elastic IP, and forwards it - to its subnet's default route. If you place it in a private subnet, its own default route points at a NAT gateway (possibly itself), and the traffic goes nowhere. **A NAT gateway in a private subnet is a black hole.**

The protection it provides is a consequence of translation, not a firewall feature: outbound connections create a mapping in the NAT's translation table, and replies match that mapping. An unsolicited inbound packet has no mapping, so there is nothing to forward it to. That is why "the NAT protects the private subnet" is true but should be explained as _no inbound mapping exists_, not as _the NAT filters traffic_.

### High availability and cost - the design decisions

A NAT gateway is **zonal**. If it lives in `eu-west-1a` and that AZ fails, every private subnet routed through it loses egress - including instances in healthy AZs. So:

- **Production**: one NAT gateway **per availability zone**, each in that AZ's public subnet, with each private subnet's route table pointing at the NAT in its own AZ. This also avoids cross-AZ data-transfer charges on every outbound byte.
- **Dev/test**: a single NAT gateway shared by all AZs is a legitimate cost saving (a NAT gateway has an hourly charge plus a per-GB processing charge, and three of them add up), as long as you accept the availability and cross-AZ-transfer trade-off.

The "how many NAT gateways do you need for two public and two private subnets in one VPC?" question has a range as its answer: **minimum one** (functional, single point of failure, cross-AZ charges), **maximum/recommended two** - one per AZ, matching the number of AZs, not the number of subnets. Say both numbers and the reasoning; that is what the question is testing.

### NAT gateway versus NAT instance

|                                | NAT gateway                      | NAT instance                                                  |
| ------------------------------ | -------------------------------- | ------------------------------------------------------------- |
| Managed                        | Yes - AWS operates it            | No - you patch, monitor, and size an EC2 instance             |
| Bandwidth                      | Scales automatically to 100 Gbps | Bounded by the instance type                                  |
| HA                             | Zonal; you deploy one per AZ     | You build it (ASG, health check, route table failover script) |
| Security groups                | **Cannot** attach one            | Can - it is an ENI                                            |
| Port forwarding / bastion duty | Not possible                     | Possible (it is just a Linux box with `iptables`)             |
| Cost                           | Hourly + per-GB processing       | Instance cost only (often cheaper at low volume)              |

Choose the gateway by default. Choose a NAT instance only when you need something it uniquely offers - a security group on the egress path, port forwarding, custom filtering, or a genuinely tiny footprint where the gateway's hourly charge dominates.

### Cheaper and safer than NAT: VPC endpoints

The most important cost and security point, and one many candidates miss: **traffic to AWS services does not need to leave the VPC**. A **gateway endpoint** (S3 and DynamoDB, free, a route-table entry) and **interface endpoints** (PrivateLink to most other services, hourly + per-GB but usually far cheaper than NAT for high volume) keep the traffic on the AWS network. A private subnet whose workload only talks to S3, ECR, Secrets Manager, and CloudWatch may need **no NAT gateway at all** - which is both cheaper and a tighter security posture, since the workload has no route to the internet whatsoever. See [what are VPC endpoints](./what-are-vpc-endpoints-and-when-do-you-use-a-gateway-versus-an-interface-endpoint.md).

### Getting _inbound_ traffic to a private subnet

The frequent scenario is "frontend, backend, and database are all in private subnets - how does an external user reach the application?" Answer with the traffic path:

```text
user → Route 53 → ALB (in the PUBLIC subnets, security group allows 443 from 0.0.0.0/0)
        └→ target group → app instances/Pods in PRIVATE subnets (SG allows 8080 from the ALB's SG)
              └→ RDS in the DATA subnets (SG allows 5432 from the app's SG)
        egress for patching/API calls → NAT gateway (public subnet) or VPC endpoints
```

The load balancer is the only thing with a public presence; targets are reached over the VPC's internal routing, so the private instances never need a public IP or a NAT for the inbound path. Add CloudFront in front for static content, caching, and DDoS absorption.

Other inbound paths that do **not** involve NAT, and which interviewers use as follow-ups: **SSM Session Manager** or an EC2 Instance Connect Endpoint for administrative access (no bastion, no inbound port); **PrivateLink** to expose a service to another VPC or account without any internet path; **Direct Connect or a site-to-site VPN** for on-premises users; and an internal (`internal` scheme) load balancer for private clients.

### IPv6 - the egress-only gateway

For IPv6 there is no NAT. The equivalent is an **egress-only internet gateway**: outbound IPv6 connectivity, inbound blocked, routed as `::/0 → eigw-xxxx`. Mentioning this shows breadth, and it comes up increasingly as IPv4 address exhaustion pushes teams towards dual-stack VPCs.

## Example

```hcl
# One NAT per AZ - the production layout
resource "aws_internet_gateway" "this" { vpc_id = aws_vpc.this.id }

resource "aws_eip" "nat" { for_each = toset(var.azs)  domain = "vpc" }

resource "aws_nat_gateway" "this" {
  for_each      = toset(var.azs)
  subnet_id     = aws_subnet.public[each.key].id # MUST be a public subnet
  allocation_id = aws_eip.nat[each.key].id
  depends_on    = [aws_internet_gateway.this]
}

# public: default route to the IGW  ->  this is what makes it "public"
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id
  route { cidr_block = "0.0.0.0/0", gateway_id = aws_internet_gateway.this.id }
}

# private: default route to the NAT in the SAME AZ (HA + no cross-AZ transfer charges)
resource "aws_route_table" "private" {
  for_each = toset(var.azs)
  vpc_id   = aws_vpc.this.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.this[each.key].id
  }
}

# S3 traffic bypasses the NAT entirely: free, and no internet route needed
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.this.id
  service_name      = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [for rt in aws_route_table.private : rt.id]
}
```

```bash
# Is this subnet public or private? Look at the route table, not the name.
aws ec2 describe-route-tables \
  --filters "Name=association.subnet-id,Values=subnet-0abc123" \
  --query 'RouteTables[0].Routes[?DestinationCidrBlock==`0.0.0.0/0`].[GatewayId,NatGatewayId]' \
  --output table
#   igw-...  -> public        nat-...  -> private        (empty) -> isolated

# From the instance: prove which public IP the world sees (the NAT's EIP)
curl -s https://checkip.amazonaws.com
# and confirm the route
ip route get 1.1.1.1

# Cost check: how much are the NAT gateways processing?
aws cloudwatch get-metric-statistics --namespace AWS/NATGateway \
  --metric-name BytesOutToDestination --statistics Sum --period 86400 \
  --start-time "$(date -u -d '-7 days' +%FT%TZ)" --end-time "$(date -u +%FT%TZ)" \
  --dimensions Name=NatGatewayId,Value=nat-0abc123
```

## Interview tips

- Define public versus private by the **route table**, not by the presence of a public IP. That single reframe answers several questions at once, including "how can you tell whether a subnet is public?"
- Explain why the NAT gateway must sit in a public subnet - it needs its own default route to the internet gateway - and say plainly that a NAT in a private subnet is a black hole.
- Describe the protection as "no inbound translation mapping exists", not as filtering. It shows you understand NAT rather than repeating a diagram caption.
- For the how-many-NAT-gateways question, give minimum one and recommended one **per AZ**, and justify it with both AZ failure isolation and cross-AZ data-transfer cost.
- Volunteer VPC endpoints as the cheaper, tighter alternative: a workload that only talks to S3, ECR, Secrets Manager, and CloudWatch may need no NAT at all. This is the highest-value thing you can add here.
- Compare NAT gateway with NAT instance in terms of managed-versus-DIY, bandwidth, and the two things only an instance can do (security group on the egress path, port forwarding).
- For inbound to private subnets, draw the path: Route 53 → public ALB → private targets → data tier, with security groups chained by reference. Then add SSM Session Manager and PrivateLink as the non-NAT inbound answers.
- Mention the egress-only internet gateway for IPv6 - there is no NAT in IPv6, and few candidates know the equivalent. See [designing a production-ready VPC on AWS](./how-do-you-design-a-production-ready-vpc-on-aws.md), [security groups versus network ACLs](./what-is-the-difference-between-a-security-group-and-a-network-acl.md), [accessing an instance in a private subnet without SSH keys or a bastion](./how-do-you-access-an-instance-in-a-private-subnet-without-ssh-keys-or-a-bastion-host.md), and [designing a secure, highly available three-tier architecture](../cloud-native-architecture/how-do-you-design-a-secure-highly-available-three-tier-architecture.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How does Pod networking and service discovery work in Kubernetes?]] (`#447`): [How does Pod networking and service discovery work in Kubernetes?](../kubernetes/how-does-pod-networking-and-service-discovery-work-in-kubernetes.md)
- [[How do you troubleshoot a Kubernetes Service that has no endpoints?]] (`#403`): [How do you troubleshoot a Kubernetes Service that has no endpoints?](../kubernetes/how-do-you-troubleshoot-a-kubernetes-service-that-has-no-endpoints.md)
- [[How do Kubernetes NetworkPolicies work, and how do you debug one that blocks traffic?]] (`#405`): [How do Kubernetes NetworkPolicies work, and how do you debug one that blocks traffic?](../kubernetes/how-do-kubernetes-networkpolicies-work-and-how-do-you-debug-one-that-blocks-traffic.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
