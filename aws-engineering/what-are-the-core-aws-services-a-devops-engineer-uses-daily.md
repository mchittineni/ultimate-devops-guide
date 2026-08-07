---
title: "What are the core AWS services a DevOps engineer uses daily?"
id: 277
category: "AWS Engineering"
difficulty: "Beginner"
tags:
  - devops
  - aws-engineering
  - interview-questions
---

# What are the core AWS services a DevOps engineer uses daily?

**Short answer:** A working set of about fifteen, grouped by job: **IAM** for identity, **VPC** for the network, **EC2 / ECS / EKS / Lambda** for compute, **S3 / EBS / EFS** for storage, **RDS / DynamoDB** for data, **CloudWatch** for telemetry, **CloudFormation or Terraform** for provisioning, **Secrets Manager / Parameter Store** for configuration, and **Route 53 / ELB** for getting traffic in. Everything else in the 200-service catalogue is reachable once you know these.

## Detail

**Identity comes first, always.** IAM defines who can do what. You will touch **users** rarely, **roles** constantly - an EC2 instance profile, a Lambda execution role, an EKS Pod identity. The habit interviewers look for: humans get temporary credentials through IAM Identity Center (SSO), machines get roles, and nobody gets a long-lived access key.

**The network you build once and live in forever.** A VPC with public and private subnets across at least two Availability Zones, an internet gateway for public traffic, a NAT gateway so private instances can reach out, security groups as the per-resource firewall, and route tables tying it together. Most "the app cannot connect" tickets end in a security group or route table.

**Compute, and how to choose:**

| Service         | Use it when                                                      |
| --------------- | ---------------------------------------------------------------- |
| **EC2**         | You need the whole machine, a custom AMI, or a legacy workload   |
| **ECS Fargate** | Containers with no cluster to manage and no Kubernetes ambitions |
| **EKS**         | Kubernetes, usually because the team already has it elsewhere    |
| **Lambda**      | Event-driven, spiky, short-lived work - glue and automation      |

**Storage and data.** S3 for objects (artifacts, backups, logs, static sites) with versioning and lifecycle rules; EBS for a single instance's disk; EFS when several instances need the same filesystem. RDS for managed relational databases with automated backups and Multi-AZ failover; DynamoDB when you want a key-value store that scales without you thinking about capacity.

**Operations.** CloudWatch is three things people conflate - **metrics**, **logs**, and **alarms**; CloudTrail is the separate audit log of every API call, and it is the first place you look after an incident. Systems Manager (SSM) gives you shell access without SSH keys or open port 22.

**Delivery.** CodePipeline / CodeBuild / CodeDeploy if you stay inside AWS, though most teams drive AWS from GitHub Actions or GitLab CI instead. Provisioning is CloudFormation (native), CDK (CloudFormation in a real language), or Terraform (multi-cloud, and the market default).

**Configuration.** Parameter Store for plain config, Secrets Manager for credentials that need rotation. Neither belongs in an environment variable committed to Git.

## Example

```bash
# Who am I, and in which account? The first command of every AWS session.
aws sts get-caller-identity

# Compute and network reality check
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query 'Reservations[].Instances[].[InstanceId,InstanceType,PrivateIpAddress]' --output table

# Storage
aws s3 ls s3://my-artifacts/releases/
aws s3 cp build.tar.gz s3://my-artifacts/releases/

# Logs for a Lambda, tailed live
aws logs tail /aws/lambda/order-processor --follow

# Shell onto an instance with no SSH key and no open port 22
aws ssm start-session --target i-0123456789abcdef0

# Read a secret at deploy time instead of baking it into an image
aws secretsmanager get-secret-value --secret-id prod/db/password --query SecretString --output text
```

```hcl
# The same services, declared instead of clicked.
resource "aws_instance" "app" {
  ami                    = data.aws_ami.al2023.id
  instance_type          = "t3.small"
  subnet_id              = aws_subnet.private_a.id
  vpc_security_group_ids = [aws_security_group.app.id]
  iam_instance_profile   = aws_iam_instance_profile.app.name # role, not keys

  tags = { Name = "app", Environment = "prod" }
}
```

## Interview tips

- Group the services by job - identity, network, compute, storage, data, observability, delivery - rather than reciting an alphabetical list. It shows you think in systems.
- Say "roles, not access keys" early. It is the fastest way to signal you have worked in a real account.
- Be ready for "EC2 vs ECS vs EKS vs Lambda" as an immediate follow-up, with one sentence of justification each.
- Know that CloudWatch is metrics/logs/alarms and CloudTrail is the API audit trail. Mixing them up is a common junior tell.
- Mention tagging (`Environment`, `Owner`, `CostCenter`) unprompted - it connects to cost and governance questions later.
- If you have only used one provider, say so plainly and map the concepts: VPC ≈ VNet, IAM role ≈ managed identity, S3 ≈ Blob Storage.

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
