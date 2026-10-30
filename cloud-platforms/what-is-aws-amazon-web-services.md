---
title: "What is AWS (Amazon Web Services)?"
id: 22
category: "Cloud Platforms"
difficulty: "Beginner"
tags:
  - devops
  - cloud-platforms
  - interview-questions
---

# What is AWS (Amazon Web Services)?

**Short answer:** AWS is Amazon's cloud platform and the largest provider by market share, offering 200+ services across compute, storage, networking, databases, and managed application services in regions worldwide.

## Detail

Services a DevOps engineer touches constantly:

- **Compute** - EC2 (virtual machines), ECS and EKS (containers), Lambda (functions), Fargate (serverless containers), Auto Scaling Groups.
- **Storage** - S3 (object), EBS (block volumes), EFS (shared file), Glacier tiers (archive).
- **Networking** - VPC, subnets, security groups, NACLs, Route 53 (DNS), CloudFront (CDN), ALB/NLB, Transit Gateway, PrivateLink.
- **Databases** - RDS and Aurora (relational), DynamoDB (key-value), ElastiCache (Valkey, Redis OSS, Memcached).
- **Identity and security** - IAM roles and policies, KMS (encryption keys), Secrets Manager, GuardDuty, Security Hub.
- **DevOps tooling** - CloudFormation and CDK (IaC), CodePipeline/CodeBuild, ECR (registry), Systems Manager (patching, Parameter Store, session access).
- **Observability** - CloudWatch metrics, logs, and alarms; X-Ray for tracing (instrument with OpenTelemetry/ADOT - the X-Ray SDKs and daemon entered maintenance mode in February 2026, with end of support in February 2027).

Structurally, AWS is organised into **regions** (independent geographies) containing multiple **availability zones** (physically separate data centres with low-latency links). Designing across at least two AZs (three is better) is the baseline for high availability; multi-region is for disaster recovery, latency, and data residency. Most services are regional, but a few - IAM, Organizations, Route 53, CloudFront - are global, with control planes concentrated in one region (historically us-east-1), which is why failover paths should rely on their data planes rather than on making changes during an outage.

**Accounts are the hard boundary.** An AWS account is the unit of isolation for blast radius, billing, and quotas; real estates use many accounts under AWS Organizations with SCPs as guardrails and IAM Identity Center for human access, rather than one big account separated by tags.

## Example

```bash
# Prefer roles over long-lived keys; assume a role for a session
aws sts assume-role --role-arn arn:aws:iam::123456789012:role/deploy \
  --role-session-name ci

aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=production" \
  --query 'Reservations[].Instances[].[InstanceId,State.Name,PrivateIpAddress]' \
  --output table
```

## Interview tips

- IAM is the most-asked AWS topic: roles over users, least privilege, no long-lived access keys, and EKS Pod Identity (or IRSA) and OIDC federation for workloads and CI.
- Understand the AZ/region distinction well enough to design a highly available architecture on a whiteboard.
- Know a cost lever or two - S3 lifecycle policies, Graviton instances, savings plans.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you design a production-ready VPC on AWS?]] (`#191`): [How do you design a production-ready VPC on AWS?](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md)
- [[What is the difference between ECS, EKS, and Fargate?]] (`#193`): [What is the difference between ECS, EKS, and Fargate?](../aws-engineering/what-is-the-difference-between-ecs-eks-and-fargate.md)
- [[How do Auto Scaling groups and load balancers work together on AWS?]] (`#194`): [How do Auto Scaling groups and load balancers work together on AWS?](../aws-engineering/how-do-auto-scaling-groups-and-load-balancers-work-together-on-aws.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Platforms](./README.md) · [All topics](../README.md)
