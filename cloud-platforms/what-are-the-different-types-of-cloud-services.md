---
title: "What are the different types of cloud services?"
id: 25
category: "Cloud Platforms"
difficulty: "Beginner"
tags:
  - devops
  - cloud-platforms
  - interview-questions
---

# What are the different types of cloud services?

**Short answer:** The three classic models are IaaS (you manage the OS upwards), PaaS (you manage the application only), and SaaS (you just use the software). Serverless and containers-as-a-service sit between IaaS and PaaS.

## Detail

**IaaS - Infrastructure as a Service.** Raw compute, storage, and networking: EC2, Azure VMs, Compute Engine. You own the operating system, patching, runtime, and everything above. Maximum control, maximum operational burden.

**PaaS - Platform as a Service.** A managed runtime: App Service, Elastic Beanstalk, Cloud Run, Heroku. You deploy code; the provider handles OS, scaling, and patching. Less control, far less toil.

**SaaS - Software as a Service.** Finished applications: Microsoft 365, Salesforce, Datadog. You configure and use; you own only your data and access control.

**FaaS / serverless.** Lambda, Azure Functions, Cloud Run functions (formerly Cloud Functions) - event-driven functions, scale to zero, billed per invocation and duration. The trade-off is less control over the runtime: cold starts, execution-time limits, and provider-specific event wiring.

**CaaS - Containers as a Service.** ECS, EKS, AKS, GKE, and serverless container runtimes such as Fargate, Azure Container Apps, and Cloud Run: you supply container images, the platform schedules them.

Who manages what:

| Layer                    | On-prem | IaaS     | PaaS     | SaaS     |
| ------------------------ | ------- | -------- | -------- | -------- |
| Application              | You     | You      | You      | Provider |
| Runtime / middleware     | You     | You      | Provider | Provider |
| OS                       | You     | You      | Provider | Provider |
| Virtualisation / servers | You     | Provider | Provider | Provider |
| Networking / facilities  | You     | Provider | Provider | Provider |

The boundaries blur in practice: the same provider service can sit at different levels depending on configuration (GKE Standard vs Autopilot, EKS with managed node groups vs EKS Auto Mode), so describe _what you still operate_ rather than arguing about the label.

## Example

The same "hello" HTTP service at three levels of abstraction - note what you stop owning at each step:

```bash
# IaaS: you own the VM, OS patching, the runtime, and the process supervisor
gcloud compute instances create web-1 --zone=europe-west1-b \
  --machine-type=e2-small --image-family=debian-12 --image-project=debian-cloud

# CaaS / serverless containers: you own the image; the platform owns nodes and scaling
gcloud run deploy hello --image=us-docker.pkg.dev/cloudrun/container/hello \
  --region=europe-west1 --allow-unauthenticated

# SaaS: nothing to deploy - you own configuration, identities, and data only
```

## Interview tips

- Draw or describe that responsibility table - it answers the question and the shared-responsibility follow-up at once.
- Give a concrete example of each from a platform you have used.
- Good closing judgement: "use the highest-level service that meets the requirement" - it minimises undifferentiated work.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you design a production-ready VPC on AWS?]] (`#191`): [How do you design a production-ready VPC on AWS?](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md)
- [[What is the difference between ECS, EKS, and Fargate?]] (`#193`): [What is the difference between ECS, EKS, and Fargate?](../aws-engineering/what-is-the-difference-between-ecs-eks-and-fargate.md)
- [[How do you run a highly available database on AWS?]] (`#196`): [How do you run a highly available database on AWS?](../aws-engineering/how-do-you-run-a-highly-available-database-on-aws.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Platforms](./README.md) · [All topics](../README.md)
