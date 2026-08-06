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

- **Compute** — EC2 (virtual machines), ECS and EKS (containers), Lambda (functions), Fargate (serverless containers), Auto Scaling Groups.
- **Storage** — S3 (object), EBS (block volumes), EFS (shared file), Glacier tiers (archive).
- **Networking** — VPC, subnets, security groups, NACLs, Route 53 (DNS), CloudFront (CDN), ALB/NLB, Transit Gateway, PrivateLink.
- **Databases** — RDS and Aurora (relational), DynamoDB (key-value), ElastiCache (Redis/Memcached).
- **Identity and security** — IAM roles and policies, KMS (encryption keys), Secrets Manager, GuardDuty, Security Hub.
- **DevOps tooling** — CloudFormation and CDK (IaC), CodePipeline/CodeBuild, ECR (registry), Systems Manager (patching, Parameter Store, session access).
- **Observability** — CloudWatch metrics, logs, and alarms; X-Ray for tracing.

Structurally, AWS is organised into **regions** (independent geographies) containing multiple **availability zones** (physically separate data centres with low-latency links). Designing across at least two AZs is the baseline for high availability; multi-region is for disaster recovery and latency.

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

- IAM is the most-asked AWS topic: roles over users, least privilege, no long-lived access keys, and IRSA/OIDC for workloads.
- Understand the AZ/region distinction well enough to design a highly available architecture on a whiteboard.
- Know a cost lever or two — S3 lifecycle policies, Graviton instances, savings plans.

---

[⬅ Back to Cloud Platforms](./README.md) · [All topics](../README.md)
