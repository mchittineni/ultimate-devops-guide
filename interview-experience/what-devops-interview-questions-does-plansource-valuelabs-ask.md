---
title: "What DevOps interview questions does Plansource ValueLabs ask?"
id: 370
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - plansource-valuelabs
  - aws-engineering
  - kubernetes
  - network-security
  - cloud-cost-optimization
  - infrastructure-as-code
  - monitoring-and-logging
---

# What DevOps interview questions does Plansource ValueLabs ask?

## Questions

**VPC and networking**

- **How many subnets can you add to a VPC?**
- **What happens when you hit a DNS name from a browser?**
- **What is the difference between HTTP and HTTPS?**
- **What is the difference between an ALB and an ELB, which layer does each operate at, and when and why would you choose each?**

**ECS, EKS, and scaling**

- **What is the difference between a Service and a Task in ECS?**
- **How does autoscaling work in ECS?**
- **How do you scale an EKS cluster based on metrics or logs?**
- **How does autoscaling work with an ALB?**

**S3**

- **How do you speed up an S3 upload for large files? And if a client uploading a 10 GB file failed after 5 GB, how do you confirm that 5 GB reached S3?**
- **How do you optimise S3 cost?**
- **How do you secure an S3 bucket that holds sensitive client data?**

**Logging and pipelines**

- **How do you stream logs from a specific path inside a Docker container to S3?**
- **How do you manage Terraform variables across different environments — dev, live, and feature?**

## Example

```text
Plansource ValueLabs — DevOps Engineer, reported round
13 questions

  S3                          3   speed up large uploads + verify a partial
                                  upload, cost optimisation, securing
                                  sensitive data
  ECS / EKS / scaling         4   Service vs Task, ECS autoscaling,
                                  EKS scaling on metrics/logs, ASG + ALB
  VPC and networking          4   subnets per VPC, DNS from browser,
                                  HTTP vs HTTPS, ALB vs ELB and layers
  Logging and pipelines       2   container path -> S3, Terraform variables
                                  per environment

THE QUESTION WITH A SINGLE CORRECT MECHANISM
  "10 GB upload failed at 5 GB — how do you confirm 5 GB arrived?" There is
  exactly one right answer (multipart upload parts), and it also answers the
  first half of the same question about speeding uploads up.
```

## Interview tips

- The failed-upload question is the best in this round and both halves share one answer: **multipart upload**. To speed up large uploads you split the object into parts and upload them in parallel — which the CLI and SDKs do automatically above a threshold, and Transfer Acceleration routes those parts through a nearby edge location. To verify a partial upload, list the in-progress multipart upload with `list-multipart-uploads` and then `list-parts`, which shows exactly which parts arrived with their sizes and ETags — so you resume by uploading only the missing parts rather than starting again. Then add the operational point that earns the mark: incomplete multipart uploads keep consuming billable storage invisibly, so you set a lifecycle rule to abort them after a few days. That single detail connects this question to the cost question. See [S3 storage classes](../aws-engineering/what-are-the-s3-storage-classes-and-when-do-you-use-each.md).
- The subnets-per-VPC question wants a number and a reason. The service quota is 200 subnets per VPC by default (raisable), but the practical limit is your address space: a VPC's CIDR is between `/16` and `/28`, AWS reserves five IPs in every subnet, and if you are running EKS with the VPC CNI assigning an IP per Pod you will exhaust addresses long before you approach the subnet count. Say "200 by quota, but IP space is the real constraint" — that is the answer of someone who has run out.
- ALB versus ELB needs the naming untangled before the comparison. "ELB" is the umbrella service and, historically, the Classic Load Balancer; the current family is ALB at layer 7, NLB at layer 4, and Gateway Load Balancer for appliance insertion. So: ALB for HTTP and HTTPS with host and path routing, header inspection, and WAF integration; NLB for raw TCP or UDP, static IPs, extreme throughput, or TLS passthrough; Classic is legacy and should be migrated. Saying "Classic is deprecated in practice" is the currency signal. See [layer 4 versus layer 7 load balancers](../scalability-and-high-availability/what-is-the-difference-between-a-layer-4-and-a-layer-7-load-balancer.md).
- ECS Service versus Task is a precise distinction: a _task definition_ is the blueprint (image, CPU, memory, ports, environment), a _task_ is a running instance of it, and a _service_ is the controller that keeps a desired number of tasks running, replaces unhealthy ones, and registers them with a load balancer target group. So a one-off batch job is a task you run directly; a long-running API is a service. That mapping — task for batch, service for long-running — is the answer.
- ECS autoscaling has two independent layers and naming both is what distinguishes the answer: **service** autoscaling adjusts the desired task count using Application Auto Scaling with target-tracking on `ECSServiceAverageCPUUtilization`, memory, or ALB requests per target; and **cluster capacity** scaling adds EC2 instances via a capacity provider with managed scaling — which does not apply on Fargate, because AWS provides the capacity. Say that people often configure the first and forget the second, so tasks sit `PENDING` with nowhere to run.
- The ALB-plus-autoscaling question is really about health checks and warm-up. The ASG launches instances, the ALB target group health-checks them, and only healthy targets receive traffic — so the details that matter are a health check grace period long enough for the application to boot, a warm-up period so new instances do not skew the scaling metric, deregistration delay for connection draining on scale-in, and target-tracking on `RequestCountPerTarget` rather than CPU when the workload is request-bound. See [how auto-scaling groups and load balancers work together](../aws-engineering/how-do-auto-scaling-groups-and-load-balancers-work-together-on-aws.md).
- "Scale EKS based on metrics or logs" should distinguish the three autoscalers and then address the _logs_ part honestly, because that is the unusual half. Metrics: HPA on CPU or memory via metrics-server, or on custom and external metrics through an adapter — with KEDA as the practical answer for queue depth or an HTTP rate. Cluster capacity: Cluster Autoscaler or Karpenter reacting to unschedulable Pods. Scaling on _logs_ is not a native concept, so say you would convert log signals into metrics first — a log-based metric filter, or an exporter that counts matching lines — because autoscalers consume metrics, not logs. Naming that translation step is the correct answer. See [autoscaling workloads and nodes](../kubernetes/how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md).
- The container-logs-to-S3 question has a preferred shape: do not write logs to a path inside the container and then ship the file. The right answer is that the application logs to stdout, the container runtime or a sidecar collector picks it up, and an agent such as Fluent Bit routes it onward — with S3 as an archive destination and CloudWatch or OpenSearch for query. If a specific in-container path is unavoidable, mount it as a shared volume and run a sidecar that tails and uploads. Say why the file-in-container approach is fragile: the filesystem is ephemeral, the disk fills, and nothing survives a restart. See [designing a logging pipeline that stays affordable at scale](../monitoring-and-logging/how-do-you-design-a-logging-pipeline-that-stays-affordable-at-scale.md).
- Securing a sensitive-data bucket is a layered answer, so list the controls: Block Public Access at the account and bucket level, SSE-KMS with a customer-managed key, a bucket policy denying any request without TLS and any unencrypted `PutObject`, access only via IAM roles with no long-lived keys, a gateway VPC endpoint so traffic never leaves the private network, versioning plus Object Lock if the data must be immutable, server access logging or CloudTrail data events for audit, and Access Analyzer to detect unintended external access. Mention lifecycle-based deletion because retention is part of protecting client data.
- S3 cost optimisation should be prioritised rather than listed: lifecycle transitions to Standard-IA, then Glacier tiers, or Intelligent-Tiering when the access pattern is unpredictable; expiry for data past its retention; aborting incomplete multipart uploads; deleting noncurrent versions; and Storage Lens to find what is actually costing money. Name the two traps — minimum storage durations mean early deletion is charged, and transition requests themselves cost money, so tiering millions of tiny objects can cost more than it saves. See [cloud cost optimisation](../cloud-cost-optimization/what-is-cloud-cost-optimization.md).
- The Terraform per-environment variables question wants a concrete layout: `terraform.tfvars` per environment or `-var-file=envs/prod.tfvars`, environment-specific values committed for non-sensitive settings, secrets injected at run time from a secret manager as `TF_VAR_*` or fetched by a data source, and separate state per environment. Say that a secret read via a data source still lands in state in plain text, which is why state must be encrypted — that detail is what makes the answer credible. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- HTTP versus HTTPS should go past "one is encrypted": HTTPS is HTTP over TLS, so it provides confidentiality, integrity, and _server authentication_ via a certificate chain — that third property is the one candidates omit. Add that HTTP/2 and HTTP/3 effectively require TLS, and that browsers now treat plain HTTP as insecure. Pair it with the browser-DNS question, which is the full request path. See [what SSL/TLS is](../network-security/what-is-ssl-tls.md) and [what happens when a user opens your application in a browser](../network-security/what-happens-when-a-user-opens-your-application-in-a-browser.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[How do you scale CI/CD across many services and teams?]] (`#459`): [How do you scale CI/CD across many services and teams?](../cicd/how-do-you-scale-ci-cd-across-many-services-and-teams.md)
- [[What is the difference between SRE, DevOps, and Platform Engineering?]] (`#232`): [What is the difference between SRE, DevOps, and Platform Engineering?](../site-reliability-engineering/what-is-the-difference-between-sre-devops-and-platform-engineering.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
