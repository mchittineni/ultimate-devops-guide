---
title: "How Do You Architect Multi-Region Active-Active Deployments on AWS with DynamoDB Global Tables?"
id: 731
category: "AWS Engineering"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - aws-engineering
  - dynamodb
  - multi-region
  - active-active
quiz:
  stem: "How does Amazon DynamoDB Global Tables resolve write conflicts when concurrent updates occur on the same item in two different regions?"
  options:
    - "It raises an unhandled exception and rolls back both writes in all regions."
    - "It employs a last-writer-wins reconciliation strategy based on internal update timestamps."
    - "It prompts a system administrator via AWS SNS to resolve the conflict manually."
    - "It preserves only the record written in the primary us-east-1 region."
  answer: 2
  explanation: "DynamoDB Global Tables resolves concurrent write conflicts using a last-writer-wins reconciliation mechanism, where the update with the latest timestamp prevails across all replica tables."
---

# How Do You Architect Multi-Region Active-Active Deployments on AWS with DynamoDB Global Tables?

**Short answer:** Multi-region active-active architectures route users to the nearest AWS region using latency-based Route 53 DNS, execute local compute against regional API Gateways or ECS/EKS clusters, and replicate data across regions with DynamoDB Global Tables - by default asynchronously (multi-Region eventual consistency, typically sub-second, last-writer-wins conflicts), or with multi-Region strong consistency (GA June 2025) when you need zero RPO and can accept higher write latency.

## Detail

### Architectural Pillars of Active-Active Multi-Region

Deploying true active-active multi-region systems achieves near-zero Recovery Time Objective (RTO) and, depending on the consistency mode, a Recovery Point Objective (RPO) of seconds (eventual) or zero (strong) during regional failures, while delivering minimal latency to geographically distributed users.

### Component Design

1. **Global Traffic Management**:
   - **Amazon Route 53**: Latency-Based Routing (LBR) routes clients to the fastest responding region, backed by DNS health checks to automatically fail over if a region degrades.
   - **AWS Global Accelerator**: Utilizes anycast IP addresses on the AWS global fiber backbone to route TCP/UDP traffic to healthy regional endpoints.
2. **Stateless Compute Tier**:
   - Identical application stacks deployed in both regions (e.g., `us-east-1` and `eu-west-1`) using Amazon ECS, EKS, or Lambda behind Application Load Balancers.
   - Session data must **never** be stored locally in memory or local disk; all state resides in distributed data stores.
3. **Multi-Region Data Tier (DynamoDB Global Tables)**:
   - Fully managed multi-master database replicating data across selected regions asynchronously, typically within sub-second intervals.
   - **Two consistency modes**: **multi-Region eventual consistency (MREC)** - the default, any number of replica Regions, asynchronous replication; and **multi-Region strong consistency (MRSC)** - exactly three Regions (or two replicas plus a witness), writes are synchronously replicated so a strongly consistent read in any Region sees the latest write, with RPO zero but higher write latency and a narrower set of supported Regions and features.
   - **Conflict Resolution (MREC)**: **last-writer-wins at the item level**, based on internal timestamps - if the same item is updated in two Regions concurrently, one whole item version wins and the other write is silently lost (attributes are not merged).
   - **DynamoDB Streams**: MREC replication is built on Streams, which must be enabled with new and old images.

```text
                    [Global User Traffic]
                              │
                    [Route 53 / Anycast]
                   ┌──────────┴──────────┐
                   ▼                     ▼
          [Region 1: us-east-1]   [Region 2: eu-west-1]
           ├─ ALB / ECS Compute    ├─ ALB / ECS Compute
           └─ DynamoDB Table       └─ DynamoDB Table
                   │                     │
                   └──◄── Sub-Second ──►─┘
                         Replication
```

### Critical Engineering Challenges

- **Concurrent Write Conflicts**: If a user updates their profile in both regions within milliseconds, last-writer-wins overwrites the earlier write. Mitigate by using account partitioning, write-affinity routing, or idempotent CRDT-style data structures.
- **Read-After-Write Consistency**: With MREC, a user writing in Region 1 who immediately queries Region 2 might observe stale data for up to a second or so. MRSC removes that at the cost of write latency, which is the core trade-off to discuss.
- **Failover Blast Radius**: Regional failover doubles traffic load on the surviving region; capacity planning and autoscaling limits must account for 100% load during failover.
- **Controlled failover**: DNS health checks alone can flap; Route 53 Application Recovery Controller (routing controls and readiness checks) gives an explicit, tested switch for evacuating a Region.
- **Everything else must be multi-Region too**: secrets, KMS keys (multi-Region keys), container images (ECR replication), and configuration - a Region that has data but no working dependencies is not active.

### Real-World Production Scenario

A global gaming service maintains player inventories across `us-west-2` and `ap-northeast-1`. By utilizing DynamoDB Global Tables, players enjoy sub-10ms inventory updates in their local region. When a network event isolates the Tokyo region, Route 53 health checks redirect all Asian players to Oregon within about a minute (health-check interval plus DNS TTL), maintaining 100% availability with zero manual intervention.

## Example

```hcl
# MREC global table: on-demand capacity, streams, replicas in two more Regions
resource "aws_dynamodb_table" "profiles" {
  name             = "profiles"
  billing_mode     = "PAY_PER_REQUEST"
  hash_key         = "user_id"
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES" # required for global table replication

  attribute {
    name = "user_id"
    type = "S"
  }

  point_in_time_recovery { enabled = true } # replication is not a backup

  replica { region_name = "eu-west-1" }
  replica { region_name = "ap-northeast-1" }
}
```

```bash
# Write in one Region, read in another: eventually consistent across Regions (MREC)
aws dynamodb put-item --region us-east-1 --table-name profiles \
  --item '{"user_id":{"S":"u-42"},"tier":{"S":"gold"}}'
aws dynamodb get-item --region eu-west-1 --table-name profiles \
  --key '{"user_id":{"S":"u-42"}}'

# Watch replication lag per replica Region
aws cloudwatch get-metric-statistics --region us-east-1 --namespace AWS/DynamoDB \
  --metric-name ReplicationLatency --statistics Average --period 60 \
  --dimensions Name=TableName,Value=profiles Name=ReceivingRegion,Value=eu-west-1 \
  --start-time "$(date -u -d '-1 hour' +%FT%TZ)" --end-time "$(date -u +%FT%TZ)"
```

## Interview tips

- Explain DynamoDB Global Tables conflict resolution: last-writer-wins per item (not per attribute) in the default MREC mode.
- Discuss the two consistency modes: MREC (asynchronous, eventually consistent across Regions) versus MRSC (zero RPO, strongly consistent reads in any Region, higher write latency, three Regions).
- Highlight the importance of over-provisioning or dynamic autoscaling so one region can absorb 100% of global traffic during a regional outage.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is AWS (Amazon Web Services)?]] (`#22`): [What is AWS (Amazon Web Services)?](../cloud-platforms/what-is-aws-amazon-web-services.md)
- [[What is Google Cloud Platform (GCP)?]] (`#24`): [What is Google Cloud Platform (GCP)?](../cloud-platforms/what-is-google-cloud-platform-gcp.md)
- [[How does networking differ across AWS, Azure, and GCP?]] (`#282`): [How does networking differ across AWS, Azure, and GCP?](../cloud-platforms/how-does-networking-differ-across-aws-azure-and-gcp.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
