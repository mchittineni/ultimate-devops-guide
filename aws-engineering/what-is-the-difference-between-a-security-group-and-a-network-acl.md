---
title: "What is the difference between a security group and a network ACL?"
id: 472
category: "AWS Engineering"
difficulty: "Beginner"
tags:
  - devops
  - aws-engineering
  - interview-questions
  - network-security
---

# What is the difference between a security group and a network ACL?

**Short answer:** A **security group** is a **stateful** firewall attached to an ENI (so, effectively, to an instance, load balancer, or Pod with a VPC-native CNI). It has **allow rules only**, and because it is stateful, return traffic for an allowed connection is automatically permitted regardless of the outbound rules. A **network ACL** is a **stateless** firewall attached to a **subnet**, evaluated on every packet in both directions, with **numbered allow _and_ deny rules** processed lowest-number-first until one matches - so you must explicitly allow the return traffic on ephemeral ports. Practically: security groups are your primary control and where nearly all your rules should live, because they are stateful and can reference other security groups; NACLs are a coarse, subnet-wide backstop whose main real use is **explicitly denying** something (a hostile CIDR) that a security group cannot express.

## Detail

### The comparison

|                       | Security group                                                    | Network ACL                                                                                         |
| --------------------- | ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Attached to           | ENI (instance, ALB/NLB, RDS, Lambda in VPC, EKS Pod)              | Subnet - so every resource in it                                                                    |
| State                 | **Stateful** - return traffic auto-allowed                        | **Stateless** - each direction evaluated separately                                                 |
| Rule types            | Allow only                                                        | Allow **and** deny                                                                                  |
| Evaluation            | **All rules evaluated**; if any allows, traffic passes            | **In rule-number order**, first match wins, then stops                                              |
| Default (new, custom) | Deny all inbound, allow all outbound                              | A **custom** NACL denies all in and out until you add rules; the **default** NACL allows everything |
| Can reference         | Other security groups, prefix lists, CIDRs                        | CIDRs only                                                                                          |
| Rule limit            | 60 inbound + 60 outbound per SG, up to 5 SGs per ENI (adjustable) | 20 inbound + 20 outbound (extendable to 40)                                                         |
| Typical use           | The actual access control                                         | Coarse subnet guardrail, explicit denies                                                            |

### Statefulness, and why it matters more than anything else here

If a security group allows inbound TCP 443, the response leaves without needing an outbound rule. With a NACL, allowing inbound 443 is not enough - the reply goes back to the client's **ephemeral port** (1024-65535), so you need an outbound rule covering that range. Forgetting it is the classic NACL mistake: connections appear to establish and then hang. This is also why tightening NACLs breaks things that security groups would have handled cleanly.

### Order of evaluation for an inbound packet

The frequently-asked question - _a request arrives from the internet through the internet gateway; which layer evaluates it first?_ - has a definite answer:

```text
internet → Internet Gateway → route table → **NACL** (subnet boundary)
                                              → **security group** (ENI)
                                                  → the instance's own host firewall
```

The NACL sees the packet first because it guards the subnet boundary; the security group is evaluated at the interface. The follow-up - _a NACL denies a CIDR but a security group allows the same IP: can it reach the load balancer?_ - is **no**. The packet is dropped at the subnet boundary and the security group never sees it. Deny at the outer layer always wins, and that is the only way to express "block this source" in AWS networking, because security groups have no deny rules.

### Security group referencing - the feature that changes designs

A security group rule can name **another security group** as its source. That is how you express intent rather than addresses:

```text
sg-web    inbound 443 from 0.0.0.0/0
sg-app    inbound 8080 from sg-web      <- not a CIDR: "whatever the web tier is"
sg-db     inbound 5432 from sg-app      <- the database only accepts the app tier
```

The rule keeps working as instances scale, get replaced, or change IP, and it makes the security posture readable. It works within a VPC and across peered VPCs in the same region. This chaining is what interviewers mean when they ask how the security groups are "wired" in a three-tier architecture - and a candidate who answers with CIDR ranges instead of SG references is signalling less experience.

Self-referencing (`sg-cluster` allowing traffic from `sg-cluster`) is the idiomatic way to let members of a cluster talk to each other.

### What each one cannot do

- **A security group cannot deny.** So it cannot block one abusive IP inside an allowed range - that needs a NACL, a WAF rule, or AWS Shield/Network Firewall.
- **A security group cannot filter by port range plus deny**, nor act as a subnet-wide control - which is why compliance requirements phrased as "the subnet must not accept X" map to NACLs.
- **A NACL cannot reference a security group** or a logical group of instances, and it cannot be applied per resource. Tightening one affects everything in the subnet, including things you did not think about (the NAT gateway, VPC endpoints, health checks).
- **Neither inspects payload.** Layer 7 filtering, SQL injection, and bot protection are WAF or Network Firewall concerns.

### Do you actually need a NACL if you have a security group?

The honest answer, and one interviewers reward: usually **no** for routine access control - security groups are more precise, stateful, and referenceable, and the default NACL allowing everything is a reasonable posture. Add NACL rules when you need one of three things: an **explicit deny** for a known-bad CIDR, a **subnet-wide guardrail** that survives someone misconfiguring a security group (defence in depth, and often a compliance requirement), or **isolation of a sensitive subnet** where you want a second independent control. Keep NACL rules few and coarse, leave numbering gaps (increments of 100) so you can insert rules later, and remember they are the harder of the two to debug.

### Debugging

Both layers are visible in **VPC Flow Logs**, and this is the fastest way to tell them apart: a packet blocked by a NACL shows `REJECT` on the **inbound** record only; a packet blocked by a security group... also shows `REJECT`, so use **Reachability Analyzer** (which tells you the exact blocking component) or check whether the traffic reaches the instance at all. The mental model: if traffic reaches the instance and nothing responds, look at the host firewall or the application; if the flow log shows a REJECT at ingress, work out which layer by testing from inside the subnet.

## Example

```hcl
# Security groups referencing each other - the readable, scale-proof pattern
resource "aws_security_group" "web" {
  name   = "web"
  vpc_id = aws_vpc.this.id
  ingress { from_port = 443, to_port = 443, protocol = "tcp", cidr_blocks = ["0.0.0.0/0"] }
  egress  { from_port = 0,   to_port = 0,   protocol = "-1",  cidr_blocks = ["0.0.0.0/0"] }
}

resource "aws_security_group" "app" {
  name   = "app"
  vpc_id = aws_vpc.this.id
  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id] # intent, not addresses
  }
  egress { from_port = 0, to_port = 0, protocol = "-1", cidr_blocks = ["0.0.0.0/0"] }
}

resource "aws_security_group" "db" {
  name   = "db"
  vpc_id = aws_vpc.this.id
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id] # only the app tier, ever
  }
  # no egress rule needed: stateful, so replies flow back automatically
}
```

```hcl
# NACL: a coarse subnet guardrail. Note the ephemeral-port rule.
resource "aws_network_acl" "private" {
  vpc_id     = aws_vpc.this.id
  subnet_ids = [for s in aws_subnet.private : s.id]

  ingress { rule_no = 100, action = "deny",  protocol = "-1",  from_port = 0,    to_port = 0,     cidr_block = "203.0.113.0/24" } # explicit deny FIRST
  ingress { rule_no = 200, action = "allow", protocol = "tcp", from_port = 5432, to_port = 5432,  cidr_block = "10.20.0.0/16" }
  ingress { rule_no = 300, action = "allow", protocol = "tcp", from_port = 1024, to_port = 65535, cidr_block = "0.0.0.0/0" }      # RETURN traffic - stateless!

  egress  { rule_no = 100, action = "allow", protocol = "-1",  from_port = 0,    to_port = 0,     cidr_block = "0.0.0.0/0" }
}
```

```bash
# Which layer is blocking me? Let AWS answer instead of guessing.
aws ec2 create-network-insights-path \
  --source i-0abc123 --destination i-0def456 --protocol tcp --destination-port 5432
aws ec2 start-network-insights-analysis --network-insights-path-id nip-0123456789abcdef0
aws ec2 describe-network-insights-analyses --network-insights-analysis-ids nia-0123 \
  --query 'NetworkInsightsAnalyses[0].{Path:NetworkPathFound,Blocked:Explanations[*].ExplanationCode}'

# Flow logs: REJECT at ingress means a NACL or SG dropped it before the host
aws logs start-query --log-group-name /aws/vpc/flowlogs \
  --start-time $(date -d '-15 min' +%s) --end-time $(date +%s) \
  --query-string 'fields srcaddr, dstaddr, dstport, action
                  | filter action = "REJECT" and dstport = 5432
                  | stats count(*) by srcaddr | sort by count(*) desc'

# Audit for the rule nobody meant to leave open
aws ec2 describe-security-groups --query \
  'SecurityGroups[?IpPermissions[?IpRanges[?CidrIp==`0.0.0.0/0`] && FromPort==`22`]].[GroupId,GroupName]' \
  --output table
```

## Interview tips

- Lead with **stateful versus stateless** and **ENI versus subnet**. Those two axes explain every other difference, and you can derive the rest live if you remember them.
- Immediately add the two rule differences: security groups are allow-only and evaluate all rules; NACLs have numbered allow **and** deny rules and stop at the first match.
- Answer the evaluation-order question definitively: NACL first (subnet boundary), then security group (ENI). Then the corollary - a NACL deny beats a security group allow, so the IP cannot reach the load balancer.
- Volunteer that a security group **cannot deny**, which is the reason NACLs exist at all and the answer to "how do you block one abusive IP?"
- Bring up security-group referencing and describe a three-tier chain (`web → app → db`) in terms of SG references rather than CIDRs. It is the single best signal of real AWS experience in this topic.
- Mention the ephemeral-port return rule on NACLs and the symptom when it is missing - connections that hang rather than fail cleanly.
- If asked "do I need a NACL when I already have a security group?", say usually not for access control, and name the three genuine cases: explicit deny, subnet-wide guardrail for defence in depth or compliance, and isolating a sensitive subnet.
- Close with debugging: VPC Flow Logs plus Reachability Analyzer, which names the blocking component instead of leaving you to guess. See [designing a production-ready VPC on AWS](./how-do-you-design-a-production-ready-vpc-on-aws.md), [how does a private subnet reach the internet](./how-does-a-private-subnet-reach-the-internet.md), [defence in depth for a cloud network](../network-security/how-do-you-design-defence-in-depth-for-a-cloud-network.md), and [what is network segmentation](../network-security/what-is-network-segmentation.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you debug DNS resolution failures inside a Kubernetes cluster?]] (`#404`): [How do you debug DNS resolution failures inside a Kubernetes cluster?](../kubernetes/how-do-you-debug-dns-resolution-failures-inside-a-kubernetes-cluster.md)
- [[How do Kubernetes NetworkPolicies work, and how do you debug one that blocks traffic?]] (`#405`): [How do Kubernetes NetworkPolicies work, and how do you debug one that blocks traffic?](../kubernetes/how-do-kubernetes-networkpolicies-work-and-how-do-you-debug-one-that-blocks-traffic.md)
- [[How do you debug a Kubernetes Ingress that is not routing traffic?]] (`#406`): [How do you debug a Kubernetes Ingress that is not routing traffic?](../kubernetes/how-do-you-debug-a-kubernetes-ingress-that-is-not-routing-traffic.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
