---
title: "What is the difference between AWS Lambda, Fargate, and EC2 compute models?"
id: 656
category: "Serverless Architecture"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - aws
  - lambda
  - fargate
  - ec2
  - compute
quiz:
  stem: "Which AWS compute option is optimal for a web scraping job that runs for 45 continuous minutes twice a day?"
  options:
    - "AWS Lambda"
    - "AWS Fargate or EC2"
    - "AWS API Gateway"
    - "Amazon S3 Select"
  answer: 2
  explanation: "AWS Lambda enforces a strict maximum execution timeout of 15 minutes. Jobs exceeding 15 minutes must execute on containerized runners like AWS Fargate, ECS, or EC2."
---

# What is the difference between AWS Lambda, Fargate, and EC2 compute models?

**Short answer:** They sit at three points on the control-versus-operations spectrum. **EC2** gives you virtual machines: full control of the OS, instance type, and hardware, and full responsibility for patching, scaling, and capacity. **Fargate** runs containers (under ECS or EKS) without you managing hosts: you size each task or Pod in vCPU and memory and pay per second while it runs. **Lambda** runs functions in response to events, scales per request, bills per millisecond of execution (plus requests), and scales to zero - but caps each invocation at 15 minutes and constrains the runtime environment. Choose by workload shape: event-driven and spiky suits Lambda, long-running containerised services suit Fargate, and specialised hardware, steady high utilisation, or OS-level control suits EC2.

## Detail

| Dimension       | EC2                                                             | Fargate (ECS/EKS)                                             | Lambda                                                                                                           |
| --------------- | --------------------------------------------------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Unit            | Virtual machine                                                 | Container task / Pod                                          | Function invocation                                                                                              |
| You manage      | OS, patching, agents, capacity, scaling                         | Image, task size, scaling policy                              | Code, memory size, concurrency limits                                                                            |
| Scaling         | Auto Scaling groups; minutes to add instances                   | Service auto scaling; new tasks in tens of seconds to minutes | Per request; each function adds up to 1,000 concurrent environments every 10 seconds, within account concurrency |
| Scale to zero   | No (stop instances yourself)                                    | Possible (desired count 0), but not request-driven            | Yes, automatically                                                                                               |
| Max run time    | Unlimited                                                       | Unlimited                                                     | 15 minutes per invocation                                                                                        |
| Billing         | Per second (Linux) while running; Savings Plans, Reserved, Spot | Per second for vCPU and memory; Savings Plans and Spot        | Per request plus GB-seconds (including init)                                                                     |
| Hardware choice | Any instance family, GPUs, local NVMe, bare metal               | Limited vCPU/memory combinations; x86 and Graviton; no GPUs   | Memory 128 MB-10 GB (CPU scales with it); x86 or Graviton                                                        |
| Cold start      | Instance boot (minutes)                                         | Image pull and task start                                     | Environment init (milliseconds to seconds)                                                                       |

**How to choose**

- **Lambda** - event handlers (S3, SQS, EventBridge), APIs with spiky or low traffic, glue and automation. Watch cost at sustained high throughput and the downstream effects of fast scaling.
- **Fargate** - web services and workers that run continuously, need more than 15 minutes, use long-lived connections (WebSockets, gRPC streams), or already ship as containers. The price per vCPU is higher than equivalent EC2, in exchange for no node management.
- **EC2** (including ECS/EKS on EC2) - GPUs and accelerators, high steady utilisation where Savings Plans or Spot make it cheapest, licensing tied to hosts, kernel or OS customisation, or very large fleets where bin-packing pays off.

**The boundaries are blurring:** Lambda supports container images up to 10 GB and response streaming; Lambda Managed Instances runs functions on EC2 capacity you choose; ECS Express Mode (the recommended replacement for App Runner) simplifies running web services on Fargate; and Karpenter or EKS Auto Mode automates EC2 node management for Kubernetes.

## Example

```text
Rough monthly cost comparison for a steady API (illustrative - check current regional prices)

Workload: 50 requests/second, 120 ms average duration, 512 MB, 24x7  (~130 M requests/month)

  Lambda   130 M requests x $0.20/M                           ~  $26
           130 M x 0.12 s x 0.5 GB = 7.8 M GB-s x ~$0.0000167  ~ $130     -> ~ $156
  Fargate  2 tasks x 0.5 vCPU / 1 GB, always on (on-demand)   ~  $65
  EC2      2 x small Graviton burstable instances, on-demand   ~  $25     + your ops time

At this steady load, containers or VMs are cheaper; at 1 request/second or with long idle
periods, Lambda's scale-to-zero wins. The crossover depends on utilisation, not on the service.
```

## Interview tips

- Frame it as a spectrum of control versus operational responsibility, then map workload shapes to each.
- Quote the hard limits correctly: 15 minutes and up to 10 GB memory for Lambda; per-second billing for EC2 and Fargate.
- Describe the cost crossover - Lambda is cheapest for spiky or idle workloads, containers or VMs for steady high utilisation.
- Mention that Lambda scaling is fast but bounded (1,000 environments per function every 10 seconds, within account concurrency), which matters for downstream systems.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What are Jenkins Pipelines?]] (`#18`): [What are Jenkins Pipelines?](../cicd/what-are-jenkins-pipelines.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Serverless Architecture](./README.md) · [All topics](../README.md)
