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
2. **Database Promotion:** Promote cross-region read replica (e.g. Amazon Aurora Global Database or RDS Read Replica) to standalone primary write master.
3. **Traffic Shift:** Update Route 53 Failover Routing Policy or Cloudflare DNS records to direct incoming user requests to secondary region endpoints.
4. **Workload Auto-Scaling:** Scale up secondary compute resources (EKS/ECS/EC2 ASGs) to match peak production traffic load.
5. **Post-Failover Audit & Failback:** Once primary region recovers, synchronize delta data and execute planned failback runbook.

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

  set_identifier = "us-east-1-primary"
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

Promoting RDS Aurora Global Database Secondary Cluster via AWS CLI:

```bash
# Fail over global database to secondary region us-west-2
aws rds failover-global-cluster \
    --global-cluster-identifier prod-global-db \
    --target-db-cluster-identifier arn:aws:rds:us-west-2:123456789012:cluster:prod-us-west-2-cluster
```

## Interview tips

- Memorize definitions: **RPO** = Data loss window (backed up data), **RTO** = Downtime window (time to recover).
- Explain the trade-offs: Active-Active provides zero downtime but introduces split-brain risks, data consistency complexity, and doubled infrastructure costs.
- Emphasize regular **Game Days** (Chaos Engineering / simulated region outages) to validate that automated failover runbooks actually work when real outages occur.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Backup and Disaster Recovery](./README.md) · [All topics](../README.md)
