---
title: "How do you execute a Disaster Recovery failover with minimal RTO and RPO?"
id: 239
category: "Backup and Disaster Recovery"
difficulty: "Advanced"
tags:
  - devops
  - backup-and-disaster-recovery
  - interview-questions
---

# How do you execute a Disaster Recovery failover with minimal RTO and RPO?

**Short answer:** Execute a Disaster Recovery (DR) failover by maintaining cross-region automated data replication (RPO), declaring outage triggers based on health checks, switching global DNS / Route 53 routing policies (RTO), promoting standby databases, scaling target infrastructure, and verifying application traffic flow.

## Detail

Disaster Recovery strategies are evaluated on two core metrics:

- **Recovery Point Objective (RPO):** Maximum acceptable data loss duration measured in time (e.g. 5 seconds of lost transactions).
- **Recovery Time Objective (RTO):** Maximum acceptable service downtime duration measured in time (e.g. 15 minutes to restore operation).

### Disaster Recovery Strategies Spectrum

1. **Backup and Restore (Highest RTO/RPO, Lowest Cost):** Periodic snapshots copied across regions; restored manually upon disaster.
2. **Pilot Light (Low RTO/RPO):** Core database continuously replicated cross-region; application servers provisioned as dormant templates (AMI/Terraform) and spun up on failover.
3. **Warm Standby (Very Low RTO/RPO):** Scaled-down shadow environment running continuously in secondary region; auto-scales up during primary region failure.
4. **Multi-Site Active-Active (Zero/Near-Zero RTO/RPO, Highest Cost):** Active traffic routed to both regions concurrently using global load balancing (AWS Global Accelerator / Route 53 latency routing).

### Step-by-Step Production Failover Runbook Execution

1. **Detection & Declaration:** Automated synthetic monitoring or health checks alert on primary region outage. Incident Commander officially declares DR activation.
2. **Fence the old primary first:** stop writes in the failed region (revoke its write path, pause its workers or queues) so that if it comes back it cannot accept writes beside the new primary and cause split-brain.
3. **Database Promotion:** Promote cross-region read replica (e.g. Amazon Aurora Global Database or RDS Read Replica) to standalone primary write master.
4. **Traffic Shift:** Let Route 53 failover records (driven by health checks) or Cloudflare load-balancing pools move incoming requests to the secondary region's endpoints. Do not depend on editing records during the incident: Route 53's record-change API is a control plane that lives in one region. Health checks, Application Recovery Controller routing controls, and ARC Region switch plans (which sequence the database promotion, scaling, and traffic steps as one rehearsed plan) work through the data plane and are built for this.
5. **Workload Auto-Scaling:** Scale up secondary compute resources (EKS/ECS/EC2 ASGs) to match peak production traffic load.
6. **Post-Failover Audit & Failback:** Once primary region recovers, synchronize delta data and execute planned failback runbook.

## Example

AWS Route 53 Failover Record Configuration with Terraform:

```hcl
# Primary Region Endpoint (Active)
resource "aws_route53_record" "primary" {
  zone_id = var.dns_zone_id
  name    = "api.example.com"
  type    = "A"

  failover_routing_policy {
    type = "PRIMARY"
  }

  set_identifier  = "us-east-1-primary"
  health_check_id = aws_route53_health_check.primary_health.id

  alias {
    name                   = aws_lb.primary_alb.dns_name
    zone_id                = aws_lb.primary_alb.zone_id
    evaluate_target_health = true
  }
}

# Secondary Region Endpoint (Passive / Standby)
resource "aws_route53_record" "secondary" {
  zone_id = var.dns_zone_id
  name    = "api.example.com"
  type    = "A"

  failover_routing_policy {
    type = "SECONDARY"
  }

  set_identifier = "us-west-2-secondary"

  alias {
    name                   = aws_lb.secondary_alb.dns_name
    zone_id                = aws_lb.secondary_alb.zone_id
    evaluate_target_health = true
  }
}
```

Promoting an Aurora Global Database secondary cluster via the AWS CLI:

```bash
# Unplanned regional outage: fail over to us-west-2, accepting loss of any
# writes not yet replicated (typically seconds - this IS your RPO).
aws rds failover-global-cluster \
    --global-cluster-identifier prod-global-db \
    --target-db-cluster-identifier arn:aws:rds:us-west-2:123456789012:cluster:prod-us-west-2-cluster \
    --allow-data-loss

# Planned DR drill or failback with a healthy primary: zero-data-loss switchover
aws rds switchover-global-cluster \
    --global-cluster-identifier prod-global-db \
    --target-db-cluster-identifier arn:aws:rds:us-west-2:123456789012:cluster:prod-us-west-2-cluster
```

Without `--allow-data-loss`, `failover-global-cluster` defaults to a switchover, which needs the primary region to be reachable - exactly what you do not have in a real regional outage.

## Interview tips

- Memorize definitions: **RPO** = Data loss window (backed up data), **RTO** = Downtime window (time to recover).
- Explain the trade-offs: Active-Active provides zero downtime but introduces split-brain risks, data consistency complexity, and doubled infrastructure costs.
- Know the difference between a **switchover** (planned, zero data loss, primary must be healthy) and a **failover** (unplanned, accepts replication lag as data loss). Also mention DNS TTLs and client-side caching: Route 53 health checks flip the record quickly, but resolvers and clients cache the old answer for the record's TTL (and some clients ignore TTLs entirely), so DNS propagation is part of your effective RTO.
- Emphasize regular **Game Days** (Chaos Engineering / simulated region outages) to validate that automated failover runbooks actually work when real outages occur.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Backup and Disaster Recovery](./README.md) · [All topics](../README.md)
