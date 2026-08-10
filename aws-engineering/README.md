---
title: "AWS Engineering"
category: "AWS Engineering"
tags:
  - devops
  - aws-engineering
  - index
---

# AWS Engineering

Depth on AWS: VPC design, IAM policy evaluation, ECS/EKS/Fargate, Auto Scaling with load balancers, S3 storage classes, highly available databases, multi-account organisations, and IaC choices.

**26 questions** · 🟢 Beginner: 6 · 🟡 Intermediate: 13 · 🔴 Advanced: 7

## Questions

| #   | Question                                                                                                                                                                           | Difficulty      |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 191 | [How do you design a production-ready VPC on AWS?](./how-do-you-design-a-production-ready-vpc-on-aws.md)                                                                           | 🟡 Intermediate |
| 192 | [How does AWS IAM evaluate a request?](./how-does-aws-iam-evaluate-a-request.md)                                                                                                   | 🔴 Advanced     |
| 193 | [What is the difference between ECS, EKS, and Fargate?](./what-is-the-difference-between-ecs-eks-and-fargate.md)                                                                   | 🟡 Intermediate |
| 194 | [How do Auto Scaling groups and load balancers work together on AWS?](./how-do-auto-scaling-groups-and-load-balancers-work-together-on-aws.md)                                     | 🟡 Intermediate |
| 195 | [What are the S3 storage classes and when do you use each?](./what-are-the-s3-storage-classes-and-when-do-you-use-each.md)                                                         | 🟡 Intermediate |
| 196 | [How do you run a highly available database on AWS?](./how-do-you-run-a-highly-available-database-on-aws.md)                                                                       | 🔴 Advanced     |
| 197 | [How do you structure a multi-account AWS organisation?](./how-do-you-structure-a-multi-account-aws-organisation.md)                                                               | 🔴 Advanced     |
| 198 | [When do you choose CloudFormation, CDK, or Terraform on AWS?](./when-do-you-choose-cloudformation-cdk-or-terraform-on-aws.md)                                                     | 🟡 Intermediate |
| 236 | [How do you automate EC2 log shipping to S3 with IAM boundaries and CloudWatch?](./how-do-you-automate-ec2-log-shipping-to-s3-with-iam-boundaries-and-cloudwatch.md)               | 🟡 Intermediate |
| 247 | [How do you secure pod access to AWS resources using EKS Pod Identity or IRSA?](./how-do-you-secure-pod-access-to-aws-resources-using-eks-pod-identity-or-irsa.md)                 | 🟡 Intermediate |
| 248 | [How do you build a CI/CD pipeline using AWS CodePipeline, CodeBuild, and CodeDeploy?](./how-do-you-build-a-ci-cd-pipeline-using-aws-codepipeline-codebuild-and-codedeploy.md)     | 🟡 Intermediate |
| 249 | [How do you architect an end-to-end production DevOps project on AWS?](./how-do-you-architect-an-end-to-end-production-devops-project-on-aws.md)                                   | 🔴 Advanced     |
| 277 | [What are the core AWS services a DevOps engineer uses daily?](./what-are-the-core-aws-services-a-devops-engineer-uses-daily.md)                                                   | 🟢 Beginner     |
| 472 | [What is the difference between a security group and a network ACL?](./what-is-the-difference-between-a-security-group-and-a-network-acl.md)                                       | 🟢 Beginner     |
| 473 | [How does a private subnet reach the internet?](./how-does-a-private-subnet-reach-the-internet.md)                                                                                 | 🟢 Beginner     |
| 474 | [What are VPC endpoints, and when do you use a gateway versus an interface endpoint?](./what-are-vpc-endpoints-and-when-do-you-use-a-gateway-versus-an-interface-endpoint.md)      | 🟡 Intermediate |
| 475 | [How do you connect many VPCs — peering, Transit Gateway, or PrivateLink?](./how-do-you-connect-many-vpcs-peering-transit-gateway-or-privatelink.md)                               | 🔴 Advanced     |
| 476 | [How do you access an instance in a private subnet without SSH keys or a bastion host?](./how-do-you-access-an-instance-in-a-private-subnet-without-ssh-keys-or-a-bastion-host.md) | 🟡 Intermediate |
| 477 | [How do you authenticate to AWS without long-lived access keys?](./how-do-you-authenticate-to-aws-without-long-lived-access-keys.md)                                               | 🔴 Advanced     |
| 478 | [How do you secure and manage the lifecycle of an S3 bucket?](./how-do-you-secure-and-manage-the-lifecycle-of-an-s3-bucket.md)                                                     | 🟡 Intermediate |
| 479 | [How do you choose between EBS, EFS, and S3?](./how-do-you-choose-between-ebs-efs-and-s3.md)                                                                                       | 🟢 Beginner     |
| 480 | [How do you upgrade, scale, and resize an RDS instance without downtime?](./how-do-you-upgrade-scale-and-resize-an-rds-instance-without-downtime.md)                               | 🔴 Advanced     |
| 481 | [What are the DNS record types, and how do you delegate a domain?](./what-are-the-dns-record-types-and-how-do-you-delegate-a-domain.md)                                            | 🟢 Beginner     |
| 482 | [How do you configure Auto Scaling group policies, health checks, and instance refresh?](./how-do-you-configure-auto-scaling-group-policies-health-checks-and-instance-refresh.md) | 🟡 Intermediate |
| 483 | [What is the difference between CloudWatch, CloudTrail, and AWS Config?](./what-is-the-difference-between-cloudwatch-cloudtrail-and-aws-config.md)                                 | 🟢 Beginner     |
| 484 | [How do you run a service on Amazon ECS?](./how-do-you-run-a-service-on-amazon-ecs.md)                                                                                             | 🟡 Intermediate |

## What interviewers probe here

- How IAM evaluates a request, including SCPs and cross-account access.
- Why the account is the blast-radius boundary.
- Making an application survive a database failover.

---

[⬅ Back to all topics](../README.md)
