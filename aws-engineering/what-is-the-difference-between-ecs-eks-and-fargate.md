---
title: "What is the difference between ECS, EKS, and Fargate?"
id: 193
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - aws-engineering
  - interview-questions
---

# What is the difference between ECS, EKS, and Fargate?

**Short answer:** ECS and EKS are orchestrators - ECS is AWS's own, simpler and tightly integrated; EKS is managed Kubernetes, portable and far more extensible. Fargate is not an orchestrator at all: it is a serverless compute engine that either can use instead of EC2 instances, so you stop managing nodes.

## Detail

|                    | ECS                                 | EKS                                                        |
| ------------------ | ----------------------------------- | ---------------------------------------------------------- |
| API                | AWS-proprietary                     | Kubernetes (portable)                                      |
| Control plane cost | free                                | hourly per cluster                                         |
| Learning curve     | low                                 | high                                                       |
| Ecosystem          | AWS services                        | the whole CNCF ecosystem                                   |
| Config             | task definitions, services          | manifests, Helm, operators, CRDs                           |
| Best fit           | AWS-only teams, small platform team | multi-cloud strategy, platform team exists, need operators |

**Fargate versus EC2 as the capacity provider.** Fargate removes node patching, scaling, and AMI management, and bills per vCPU-second and GB-second of the task's reservation. In exchange you lose daemonsets that need host access, GPU support, custom kernels, privileged containers, and the ability to bin-pack many small containers onto one large instance. On a per-vCPU basis it is more expensive than a well-utilised EC2 fleet, and cheaper than a badly utilised one - utilisation is the real comparison, not list price.

**On EKS, the modern node options are worth naming.** Karpenter provisions right-sized nodes on demand from the pending-Pod spec (far better bin-packing than cluster-autoscaler with fixed node groups), EKS Auto Mode manages that layer for you, and Fargate profiles suit isolated or spiky workloads. Most teams end up mixing: Karpenter-managed Spot for stateless work, on-demand for critical baseline.

**The honest recommendation.** If the team has no Kubernetes experience, no multi-cloud requirement, and no need for the operator ecosystem, ECS on Fargate delivers the same business outcome with a fraction of the operational surface. Choose EKS when you need Kubernetes-specific tooling, portability, or the hiring pool that comes with a standard API - and budget for a platform team, because a cluster nobody upgrades is a liability.

**Operational differences that bite.** EKS requires Kubernetes version upgrades roughly every 12–14 months as versions leave standard support (extended support costs more), plus add-on compatibility management. ECS has no version treadmill. Conversely, ECS service discovery, autoscaling, and deployment semantics are less expressive than Kubernetes equivalents, and diagnosing them means learning AWS-specific behaviour that transfers nowhere else.

## Example

```json
{
  "family": "api",
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "512",
  "memory": "1024",
  "runtimePlatform": { "cpuArchitecture": "ARM64" },
  "executionRoleArn": "arn:aws:iam::111122223333:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::111122223333:role/api-task",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "111122223333.dkr.ecr.eu-west-1.amazonaws.com/api@sha256:1f4b",
      "portMappings": [{ "containerPort": 8080 }],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8080/healthz || exit 1"],
        "interval": 15,
        "retries": 3
      },
      "logConfiguration": { "logDriver": "awslogs", "options": { "awslogs-group": "/ecs/api" } }
    }
  ]
}
```

## Interview tips

- The crisp framing: "ECS and EKS are orchestrators; Fargate is a capacity type both can use."
- Naming Karpenter and the EKS version-support treadmill shows current, hands-on knowledge.
- Expect: "when would you not choose Kubernetes?" - answer honestly; recommending EKS unconditionally reads as inexperience.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?]] (`#407`): [How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-waiting-for-a-persistentvolumeclaim.md)
- [[What is AWS (Amazon Web Services)?]] (`#22`): [What is AWS (Amazon Web Services)?](../cloud-platforms/what-is-aws-amazon-web-services.md)
- [[What is Azure?]] (`#23`): [What is Azure?](../cloud-platforms/what-is-azure.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
