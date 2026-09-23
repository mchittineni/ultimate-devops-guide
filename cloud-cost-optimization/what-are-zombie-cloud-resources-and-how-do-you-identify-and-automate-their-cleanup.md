---
title: "What are Zombie cloud resources and how do you identify and automate their cleanup?"
id: 638
category: "Cloud Cost Optimization"
difficulty: "Beginner"
tags:
  - devops
  - cloud-cost-optimization
  - interview-questions
  - finops
  - zombie-resources
  - cost-optimization
  - aws
quiz:
  stem: "Why does AWS charge an hourly fee for allocated Elastic IP addresses that are NOT attached to a running EC2 instance?"
  options:
    - "Because unattached IPs consume double the network bandwidth"
    - "To discourage IPv4 address hoarding and incentivize customers to release scarce public IP addresses back to the global pool"
    - "To cover encryption licensing costs"
    - "Because DNS servers cannot route unattached IPs"
  answer: 2
  explanation: "Public IPv4 addresses are a scarce resource. Cloud providers impose fees on idle, unassociated Elastic IPs to prevent hoarding - and since February 2024 AWS charges for every public IPv4 address, attached or not."
---

# What are Zombie cloud resources and how do you identify and automate their cleanup?

**Short answer:** Zombie resources are abandoned, forgotten cloud assets that generate continuous billing while providing zero business value; common culprits include unattached EBS volumes, unassociated Elastic IPs, orphaned snapshots, idle load balancers, and abandoned NAT Gateways.

## Detail

Cloud bills accumulate orphaned infrastructure: resources left behind by deleted instances, finished experiments, departed engineers, and failed pipeline runs. Each item is usually small; together they are often a noticeable slice of the bill, and they also widen the attack surface.

### Top zombie offenders

1. **Unattached EBS volumes (`status = available`)**: a volume created with `DeleteOnTermination = false` (the default for additionally attached volumes) survives its instance and keeps billing for storage and provisioned IOPS.
2. **Idle public IPv4 addresses**: since February 2024 AWS charges for **every** public IPv4 address, attached or not (about $0.005 per hour, roughly $3.60 a month each). Unassociated Elastic IPs are pure waste; attached ones are a reason to review whether a resource needs a public address at all.
3. **Orphaned snapshots and AMIs**: backup scripts without retention, and AMIs whose snapshots outlive the images, accumulate for years.
4. **Idle load balancers**: ALBs/NLBs with no targets or no traffic still bill an hourly charge plus capacity units.
5. **Idle NAT gateways and interface endpoints**: hourly charges per gateway or endpoint per AZ, even at zero traffic.
6. **Forgotten environments**: dev/test clusters, databases, and GPU instances nobody turned off; stopped RDS instances restart automatically after seven days.
7. **Log groups and buckets with no retention**, storing data nobody reads.

### Finding and cleaning them up

- **Detect**: AWS Trusted Advisor and Compute Optimizer (idle resource recommendations), Cost Explorer grouped by usage type, provider equivalents (Azure Advisor, Google Recommender), or queries against the Cost and Usage Report.
- **Automate with policy**: **Cloud Custodian** (open source) expresses rules as YAML - find, tag, notify, then delete after a grace period. Scheduled Lambda or Azure Functions "janitor" jobs do the same for simpler cases.
- **Use a staged workflow** rather than deleting immediately: tag the resource with a deletion date, notify the owner (from tags), snapshot volumes before deletion where data might matter, then delete. Immediate deletion is how cleanup automation causes outages.
- **Prevent them**: IaC for everything (so `terraform destroy` removes what was created), mandatory `Owner` and expiry tags, TTLs on ephemeral environments, lifecycle policies (Amazon Data Lifecycle Manager for snapshots, S3 lifecycle rules), and default log retention.

**Trade-off.** Aggressive automation saves money but risks deleting something a team still needs (a detached volume kept for forensics, a DR AMI). Exemption tags, grace periods, and snapshots-before-delete are the price of doing this safely.

## Example

```yaml
# Cloud Custodian: mark unattached volumes, notify, and delete after a grace period.
policies:
  - name: ebs-unattached-mark
    resource: aws.ebs
    filters:
      - State: available
      - "tag:custodian-exempt": absent
    actions:
      - type: mark-for-op
        op: delete
        days: 7
      - type: notify
        to: [resource-owner] # from the Owner tag
        transport: { type: sqs, queue: custodian-mailer }

  - name: ebs-unattached-delete
    resource: aws.ebs
    filters:
      - State: available
      - type: marked-for-op
        op: delete
    actions:
      - type: snapshot # keep a copy before the volume goes
      - delete
```

```bash
# Quick manual sweep: unassociated Elastic IPs and unattached volumes.
aws ec2 describe-addresses --query 'Addresses[?AssociationId==`null`].[PublicIp,AllocationId]' --output table
aws ec2 describe-volumes --filters Name=status,Values=available \
  --query 'Volumes[].[VolumeId,Size,VolumeType,CreateTime]' --output table
```

## Interview tips

- Name the common offenders with the mechanism that creates them - `DeleteOnTermination`, missing retention, forgotten environments.
- Be current on IPv4: AWS has charged for all public IPv4 addresses since 2024, not just idle Elastic IPs.
- Describe a staged cleanup - tag, notify, grace period, snapshot, delete - rather than instant deletion.
- Mention Cloud Custodian (or provider advisors) for detection and automation.
- Close with prevention: IaC, owner and expiry tags, TTLs, and lifecycle policies.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does OpenID Connect (OIDC) eliminate long-lived cloud credentials in CI/CD pipelines?]] (`#533`): [How does OpenID Connect (OIDC) eliminate long-lived cloud credentials in CI/CD pipelines?](../cicd/how-does-openid-connect-oidc-eliminate-long-lived-cloud-credentials-in-ci-cd-pipelines.md)
- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Cost Optimization](./README.md) · [All topics](../README.md)
