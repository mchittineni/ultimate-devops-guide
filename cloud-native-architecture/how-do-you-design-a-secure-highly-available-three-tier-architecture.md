---
title: "How do you design a secure, highly available three-tier architecture?"
id: 505
category: "Cloud Native Architecture"
difficulty: "Advanced"
tags:
  - devops
  - cloud-native-architecture
  - interview-questions
  - scalability-and-high-availability
  - aws-engineering
  - network-security
---

# How do you design a secure, highly available three-tier architecture?

**Short answer:** Three logical tiers - **presentation**, **application**, **data** - mapped onto network layers so that only the first is reachable from the internet. Concretely: a CDN and WAF at the edge, a **public-subnet load balancer** terminating TLS, **application instances or Pods in private subnets** across at least three availability zones behind it, and a **managed database in isolated data subnets** with a synchronous standby in another AZ. Every tier spans multiple AZs, every tier scales independently, and the security groups are **chained by reference** - the app tier accepts traffic only from the load balancer's security group, the database only from the app's - so nothing is expressed as a CIDR and nothing is reachable it should not be. High availability comes from redundancy per tier plus health checks that remove failed members; security comes from the layering plus encryption in transit and at rest, no public IPs below the edge, IAM roles instead of credentials, and secrets from a managed store. The sentence that frames it well: **the tiers are a logical separation of responsibility; the subnets and security groups are how you make that separation enforceable.**

## Detail

### The tiers, and what each one is responsible for

| Tier                    | What it does                                       | Where it lives                                                      | Scales on                                   |
| ----------------------- | -------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------- |
| **Presentation (web)**  | Serves UI, static assets, TLS termination, routing | CDN + public-subnet load balancer; static content in object storage | Cache hit ratio, request rate               |
| **Application (logic)** | Business logic, APIs, sessions, integrations       | **Private** subnets - EC2/ASG, ECS, or Kubernetes                   | Requests per instance, latency, queue depth |
| **Data**                | Persistence, caching, search                       | **Isolated** subnets - managed database, cache, object storage      | Connections, IOPS, storage                  |

Two-tier versus three-tier, since it is the usual follow-up: two-tier is client → database (or web+app combined → database), which is simpler and has fewer hops but couples presentation to logic, cannot scale them independently, and puts the thing that talks to the database in the same failure and security domain as the thing exposed to users. Three-tier buys independent scaling, an enforceable network boundary, and the ability to replace one tier without touching the others - at the cost of one more hop and more infrastructure.

### The reference layout

```text
                         Route 53 (health-checked, alias to the edge)
                                    │
                        CloudFront / Front Door  ── WAF, TLS, caching, DDoS absorption
                                    │  (origin locked to the CDN's prefix list + a shared header)
   ┌────────────────────────────────┴─────────────────────────────────┐
   │ VPC 10.20.0.0/16                                                 │
   │  public subnets   (AZ-a / AZ-b / AZ-c)   ALB + NAT gateway/AZ    │
   │        │  sg-alb: 443 from the CDN only                          │
   │  private subnets  (AZ-a / AZ-b / AZ-c)   app ASG / Pods          │
   │        │  sg-app: 8080 from sg-alb                               │
   │  data subnets     (AZ-a / AZ-b / AZ-c)   RDS Multi-AZ, ElastiCache│
   │           sg-db:  5432 from sg-app       (no default route out)  │
   │                                                                  │
   │  VPC endpoints: S3 (gateway), ECR, Secrets Manager, SSM, logs     │
   └──────────────────────────────────────────────────────────────────┘
```

Three subnet tiers per AZ, so nine subnets plus a small infra subnet per AZ for endpoints and Transit Gateway attachments. The data subnets have **no route to the internet at all** - not even via NAT - which is a meaningful posture improvement and possible because patching comes from a managed service and any needed AWS API access goes through VPC endpoints.

### Where the security actually comes from

- **Security groups chained by reference**, not by CIDR: `sg-app` allows 8080 from `sg-alb`; `sg-db` allows 5432 from `sg-app`. The rules keep working as instances scale and are replaced, and the intent is readable. Answering this question with CIDR ranges is the tell that someone has not built it.
- **No public IPs below the edge.** The ALB is the only internet-facing component; app instances and the database have private addresses only. Administrative access is **SSM Session Manager**, not a bastion with port 22 open.
- **TLS everywhere**: terminate at the edge and at the ALB with ACM-managed certificates, and re-encrypt to the app tier where the data warrants it. Encrypt at rest with KMS (EBS, RDS, S3) and enforce TLS-only access with a bucket policy.
- **IAM roles, not credentials**: an instance profile / task role / IRSA for the app tier, and application secrets from Secrets Manager or Parameter Store fetched at runtime - never baked into an AMI or an image.
- **WAF at the edge** with managed rule sets in detection mode first, plus rate limiting and bot rules. And the point people miss: **lock the origin to the CDN** (a managed prefix list or service tag, plus a shared secret header), or an attacker can resolve the ALB and bypass the WAF entirely.
- **Defence in depth**: NACLs as a coarse subnet guardrail (particularly an explicit deny for known-bad CIDRs, which security groups cannot express), VPC Flow Logs, GuardDuty, and Config rules for continuous drift detection.
- **Least privilege in the data tier**: separate database users per service with only the grants they need, no shared admin account, and IAM database authentication where supported.

### Where the availability comes from

- **Three AZs, not two.** With two AZs, losing one removes 50% of capacity, so you must run 100% headroom to survive it; with three, you lose 33% and need 50% headroom. Three is materially cheaper for the same resilience, and it is the answer to give.
- **Redundancy per tier**: an ALB is inherently multi-AZ; the app tier is an ASG or Deployment with a minimum of three and `topologySpreadConstraints`/AZ balancing; the database is Multi-AZ with a synchronous standby (and read replicas for read scaling, which is a different concern).
- **Health checks that actually check the app**: the target group probes `/healthz`, and the ASG uses `ELB` health check type so an instance that boots but never serves is replaced - with a grace period longer than real startup time, or you get a replacement loop.
- **Graceful removal**: connection draining (deregistration delay), `preStop` hooks, and a shutdown sequence that stops accepting work before exiting.
- **Stateless application tier.** This is the design constraint that makes everything else possible: sessions in ElastiCache/Redis or a signed token, uploads in S3, nothing on local disk. Sticky sessions are a workaround that reintroduces the problem - when the Pod or instance holding a session goes away, that session is lost, which is why the answer to "what happens to sticky-session data when the Pod dies?" is "it is gone, so put sessions in Redis".
- **Autoscaling per tier** with sensible ceilings, and **graceful degradation** under overload: shed load with 429s, circuit-break to protect the database, and serve cached or reduced functionality rather than failing entirely.
- **Multi-region only when the requirement justifies it.** Multi-AZ handles an AZ failure and covers most availability targets; multi-region handles a regional failure and roughly doubles cost and complexity. Ask for the RTO/RPO before proposing it, and then choose active-passive with a promoted replica (cheap, minutes of RTO) or active-active (expensive, needs conflict handling).

### Latency and cost, which are part of the design

Low latency for distant users comes from the **CDN** (cached static content served from the nearest edge, plus split-TCP acceleration for dynamic requests) and, if needed, a second region with latency-based routing - not from a bigger instance. Cost control comes from: right-sized instances with Savings Plans or Reserved capacity for the steady baseline and Spot for tolerant work, **VPC endpoints so S3/ECR traffic does not pay NAT processing charges**, one NAT gateway per AZ (avoiding cross-AZ transfer charges), lifecycle policies on object storage and logs, and scaling non-production to zero out of hours.

### How to answer this on a whiteboard

Interviewers use this question to see whether you drive from requirements. Start by asking (or stating assumptions about) **traffic volume, availability target, RTO/RPO, data residency, and budget** - then draw the tiers, then the traffic path end to end, then the security groups, then failure scenarios ("AZ-a is gone: what happens?"). Choosing components with reasons stated is worth more than naming products: a managed database rather than a StatefulSet because you do not want to own backup, failover, and patching; S3 plus CloudFront for the frontend rather than Pods because it is cheaper, faster, and has no capacity to manage; EKS rather than ECS only if you actually need the Kubernetes ecosystem.

## Example

```hcl
# The security-group chain: intent, not CIDRs
resource "aws_security_group" "alb" {
  name   = "alb"
  vpc_id = aws_vpc.this.id
  ingress { # only the CDN may reach the ALB - this is what makes the WAF unbypassable
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    prefix_list_ids = [data.aws_ec2_managed_prefix_list.cloudfront.id]
  }
  egress { from_port = 0, to_port = 0, protocol = "-1", cidr_blocks = ["0.0.0.0/0"] }
}

resource "aws_security_group" "app" {
  name   = "app"
  vpc_id = aws_vpc.this.id
  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id] # <- reference, survives scaling
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
  # no egress rule: stateful, and the data tier has nowhere to go anyway
}
```

```hcl
# Three AZs per tier, health checks that check the app, Multi-AZ data
resource "aws_autoscaling_group" "app" {
  min_size                  = 3 # one per AZ minimum
  max_size                  = 30
  desired_capacity          = 6
  vpc_zone_identifier       = [for s in aws_subnet.private : s.id]
  health_check_type         = "ELB" # replace instances that boot but never serve
  health_check_grace_period = 300   # longer than real startup, or you loop
  target_group_arns         = [aws_lb_target_group.app.arn]
  launch_template { id = aws_launch_template.app.id, version = "$Latest" }
  instance_refresh { strategy = "Rolling", preferences { min_healthy_percentage = 90 } }
}

resource "aws_lb_target_group" "app" {
  name                 = "app"
  port                 = 8080
  protocol             = "HTTP"
  vpc_id               = aws_vpc.this.id
  deregistration_delay = 60 # connection draining on scale-in
  health_check { path = "/healthz", interval = 15, healthy_threshold = 2, unhealthy_threshold = 3 }
}

resource "aws_db_instance" "orders" {
  identifier              = "orders-prod"
  engine                  = "postgres"
  multi_az                = true # synchronous standby in another AZ
  storage_encrypted       = true
  kms_key_id              = aws_kms_key.rds.arn
  db_subnet_group_name    = aws_db_subnet_group.data.name # isolated subnets, no NAT route
  backup_retention_period = 14
  deletion_protection     = true
  performance_insights_enabled = true
  lifecycle { prevent_destroy = true }
}
```

```text
Failure walk-through - answer this before you are asked

  AZ-a disappears entirely
    edge      CDN unaffected (global)
    LB        ALB stops sending to AZ-a targets; the other two AZs absorb traffic
    app       ASG replaces the lost third in AZ-b/AZ-c; capacity dips ~33% (why 3 AZs, not 2)
    data      RDS fails over to the standby in AZ-b; the endpoint stays the same,
              in-flight transactions fail and clients reconnect (~60s)
    egress    the NAT gateway in AZ-a is gone, but each AZ has its own -> no impact
    session   sessions are in Redis (Multi-AZ), so users are not logged out
    action    none manual; verify error rate and latency recover, then post-incident review

  One app instance is unhealthy
    target group health check fails -> deregistered after 3 checks -> ASG replaces it
    connection draining lets in-flight requests finish; users see nothing

  Traffic triples in ten minutes
    CDN absorbs the cacheable share; target-tracking scales the app tier;
    the DB does not scale on demand -> connection pooling + RDS Proxy + read replicas,
    and load shedding (429 + Retry-After) rather than collapse
```

## Interview tips

- Open by asking for requirements - traffic, availability target, RTO/RPO, residency, budget - then design to them. Candidates who start naming services lose to candidates who start with numbers.
- Draw the mapping explicitly: three **logical** tiers onto public / private / isolated **subnets** across three AZs. Say that the tiers are the responsibility split and the subnets plus security groups are what make it enforceable.
- Describe the security groups as a **chain of references** (`sg-app` from `sg-alb`, `sg-db` from `sg-app`). This is the single strongest signal in the whole answer.
- Say **three AZs, not two**, and give the arithmetic: losing one of three costs 33% of capacity instead of 50%, so you carry less headroom for the same resilience.
- Insist the application tier is **stateless** - sessions in Redis, uploads in object storage - and answer the sticky-session question honestly: the session dies with the instance, which is why you externalise it.
- Volunteer the origin-lockdown point: a WAF only helps if the ALB is not directly reachable, so restrict it to the CDN's prefix list and validate a shared header.
- Mention that the data subnets need **no route to the internet**, with VPC endpoints covering the AWS API access the app tier needs - which is both cheaper than NAT and a tighter posture.
- Walk a failure scenario unprompted ("AZ-a is gone: here is what happens at each tier"), including the ~60-second RDS failover and the fact that in-flight transactions fail so clients must retry.
- Be deliberate about multi-region: multi-AZ covers AZ failure and most SLAs; multi-region roughly doubles cost, so ask for the RTO/RPO first. See [designing a production-ready VPC on AWS](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md), [security groups versus network ACLs](../aws-engineering/what-is-the-difference-between-a-security-group-and-a-network-acl.md), [how do you design for multi-region resilience](../cloud-engineering/how-do-you-design-for-multi-region-resilience.md), [designing a system to degrade gracefully under overload](../scalability-and-high-availability/how-do-you-design-a-system-to-degrade-gracefully-under-overload.md), and [what happens when a user opens your application in a browser](../network-security/what-happens-when-a-user-opens-your-application-in-a-browser.md).

---

[⬅ Back to Cloud Native Architecture](./README.md) · [All topics](../README.md)
