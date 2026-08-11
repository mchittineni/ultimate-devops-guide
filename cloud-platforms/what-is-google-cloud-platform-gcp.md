---
title: "What is Google Cloud Platform (GCP)?"
id: 24
category: "Cloud Platforms"
difficulty: "Beginner"
tags:
  - devops
  - cloud-platforms
  - interview-questions
---

# What is Google Cloud Platform (GCP)?

**Short answer:** Google Cloud Platform is Google's cloud, known for Kubernetes (which it created), a genuinely global network, and strong data and machine-learning services such as BigQuery.

## Detail

Signature services:

- **GKE** - the most mature managed Kubernetes offering, with Autopilot mode running nodes for you entirely.
- **BigQuery** - serverless analytics warehouse; separates storage from compute and scales to petabytes with plain SQL.
- **Cloud Run** - run any container serverlessly, scale to zero, pay per request. Often the simplest good answer for a stateless HTTP service.
- **Compute Engine** - VMs, with live migration during host maintenance and sustained-use discounts applied automatically.
- **Cloud Storage** - object storage with a single global namespace and lifecycle-managed classes.
- **Pub/Sub** - global messaging, and **Dataflow** for stream and batch processing.
- **Vertex AI** - managed ML platform.
- **Cloud Operations** (formerly Stackdriver) - monitoring, logging, and tracing.

The resource hierarchy is **organisation → folders → projects → resources**. The **project** is the fundamental unit of isolation, billing, and IAM - a much stronger boundary than an AWS tag and often used per-environment or per-team.

Networking is distinctive: VPCs are global rather than regional, with subnets per region, so a single VPC can span the world.

## Interview tips

- Global VPC and project-based isolation are the GCP-specific answers.
- Workload Identity Federation is how GCP avoids service-account key files - say it when asked about credentials.
- If the interview leans data, BigQuery's separation of storage and compute is the concept to explain.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you design a production-ready VPC on AWS?]] (`#191`): [How do you design a production-ready VPC on AWS?](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md)
- [[What is the difference between ECS, EKS, and Fargate?]] (`#193`): [What is the difference between ECS, EKS, and Fargate?](../aws-engineering/what-is-the-difference-between-ecs-eks-and-fargate.md)
- [[How do Auto Scaling groups and load balancers work together on AWS?]] (`#194`): [How do Auto Scaling groups and load balancers work together on AWS?](../aws-engineering/how-do-auto-scaling-groups-and-load-balancers-work-together-on-aws.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Platforms](./README.md) · [All topics](../README.md)
