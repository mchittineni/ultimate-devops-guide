---
title: "How do you run a service on Amazon ECS?"
id: 484
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - aws-engineering
  - interview-questions
  - container-orchestration-advanced
  - cicd
---

# How do you run a service on Amazon ECS?

**Short answer:** Four objects, in order. A **cluster** is a logical grouping with a capacity provider (Fargate, or EC2 instances running the ECS agent). A **task definition** is the immutable, versioned blueprint - container image, CPU and memory, ports, environment and secrets, log configuration, and two distinct IAM roles: the **task execution role** (for the agent, to pull the image and write logs) and the **task role** (for your application's own AWS calls). A **task** is one running instance of that definition. A **service** keeps N tasks running, replaces unhealthy ones, registers them with a load balancer target group, and performs rolling deployments. So a deploy is: build and push the image, register a **new task definition revision**, and update the service to that revision - ECS then starts new tasks, waits for them to pass health checks, drains and stops the old ones. The distinction interviewers test most: a **task** is a run, a **service** is a supervisor that maintains desired count and handles rollout.

## Detail

### Task versus service, and Fargate versus EC2

|                           | Task                                                                         | Service                                       |
| ------------------------- | ---------------------------------------------------------------------------- | --------------------------------------------- |
| Lifetime                  | Runs, then exits (or dies)                                                   | Continuously maintains `desiredCount`         |
| Replaces failures         | No                                                                           | Yes                                           |
| Load balancer integration | No                                                                           | Yes, via target group registration            |
| Deployment strategy       | N/A                                                                          | Rolling, blue/green (CodeDeploy), or external |
| Use for                   | Batch jobs, one-off migrations (`run-task`), scheduled tasks via EventBridge | Long-running APIs and workers                 |

**Fargate versus EC2 launch type** is the other axis, and the honest comparison:

- **Fargate**: no instances to patch, per-task CPU/memory billing, task-level ENI so security groups apply per task, faster to operate. Costs more per vCPU-hour, has a limited set of CPU/memory combinations, no privileged mode or GPU (Fargate has no GPU support), and no daemon-style placement.
- **EC2**: cheaper at steady high utilisation (especially with Spot or Savings Plans), gives you GPUs, privileged containers, custom kernel settings, and larger local storage - but you own the AMI, patching, and cluster capacity (via a capacity provider with managed scaling).

Choose Fargate by default and EC2 when a specific requirement forces it. Fargate Spot for interruption-tolerant work is a large, easy saving.

### The two IAM roles - a classic exam question

- **Task execution role**: used by the ECS agent, **not** your code. It pulls from ECR, writes to CloudWatch Logs, and fetches Secrets Manager/SSM values referenced in the task definition. Missing permissions here show up as a task that never starts, with a `CannotPullContainerError` or a secrets-resolution failure.
- **Task role**: assumed by **your application** so the SDK can call S3, DynamoDB, SQS. Credentials arrive from the container credentials endpoint automatically - no keys, and it is per-task, not per-instance.

Conflating them is the usual reason a task starts but cannot reach S3, or cannot start at all. Say both names and what each is for.

### Networking

Use **`awsvpc`** network mode (mandatory on Fargate): each task gets its own ENI and private IP in your subnets, so **security groups apply per task** and flow logs show task-level traffic. That is the answer to "how do you isolate one service from another in ECS" - security groups, not host ports. The older `bridge`/`host` modes with dynamic port mapping still exist for EC2 launch type and cost you per-task network identity.

Place tasks in **private subnets** with an ALB in the public subnets. Fargate tasks in private subnets need either a NAT gateway or VPC endpoints (`ecr.api`, `ecr.dkr`, `logs`, `secretsmanager`, `sts`, plus the **S3 gateway endpoint** because ECR layers come from S3) - the same endpoint set as any private workload pulling images.

### Service discovery and load balancing

- **ALB + target group** with `target_type = "ip"` for `awsvpc`: path- and host-based routing, and the ALB health check is what gates a deployment.
- **ECS Service Connect** (or the older **Service Discovery** via Cloud Map) for service-to-service calls by name, with built-in retries, load balancing, and per-call metrics. Service Connect is the modern answer for internal traffic and worth naming over "put an internal ALB in front of everything".
- **Health check grace period** on the service: if the application takes 90 seconds to become ready and the grace period is 0, ECS kills tasks before they can pass the ALB health check - the same replacement loop as with Auto Scaling groups, and the most common "my deployment keeps cycling" cause.

### Deployments

- **Rolling update** is the default, controlled by `minimumHealthyPercent` and `maximumPercent`. `100/200` means ECS may double capacity briefly and never drop below the desired count - the safe production setting. `50/100` avoids extra capacity but runs degraded during the rollout.
- **Deployment circuit breaker** (`enable: true, rollback: true`) detects a failing deployment and rolls back to the previous task definition automatically. Turn it on; it converts a bad deploy from an incident into a non-event.
- **Blue/green via CodeDeploy** with two target groups and a listener shift, including canary and linear traffic-shifting options plus automatic rollback on CloudWatch alarms. This is the answer to "how do you do blue/green on ECS".
- **`appspec.yml`** is the CodeDeploy file that ties it together for ECS (and for EC2/on-premises deployments): it names the task definition, the container and port, and the lifecycle hooks (`BeforeAllowTraffic`, `AfterAllowTraffic`) where you run validation.
- **Task definitions are immutable**: every deploy registers a new revision. Roll back by updating the service to the previous revision - which is why keeping revisions and deploying by revision (not `:latest`) matters. Deploy images by **digest or an immutable tag**, never `latest`, or you cannot say what is running.

### Scaling

**Service auto scaling** uses Application Auto Scaling: target tracking on `ECSServiceAverageCPUUtilization`, `ECSServiceAverageMemoryUtilization`, or `ALBRequestCountPerTarget`, plus step scaling and scheduled scaling. For queue workers, target-track a custom metric of backlog per task. On EC2 launch type you additionally need **capacity provider managed scaling** so the cluster acquires instances when tasks cannot be placed - forgetting that half is why tasks sit in `PROVISIONING` with "unable to place".

### Operating it

- **Logs**: `awslogs` driver to CloudWatch, or FireLens (Fluent Bit sidecar) to route to OpenSearch, S3, or a third party with filtering. Set a retention policy on the log group.
- **Getting a shell**: `aws ecs execute-command` (ECS Exec) - requires the task role to allow the SSM channel actions and `enableExecuteCommand` on the service. That is the answer to "what is the command to connect to a container in ECS", and it needs no SSH and no bastion.
- **Stopped-task diagnosis**: `describe-tasks` `stoppedReason` plus the container `exitCode` tells you almost everything - `CannotPullContainerError` (execution role, endpoints, or a bad tag), `ResourceInitializationError` (secrets or networking), exit 137 (OOM - raise memory or fix a leak), exit 1 (application crash - read the logs), or `Task failed ELB health checks` (grace period or a wrong health path).
- **Cost**: right-size task CPU/memory from observed usage, Fargate Spot for tolerant workloads, Compute Savings Plans, scale to zero out of hours in non-production, and stop paying for `desiredCount` you do not need.

### ECS versus EKS, briefly

ECS is simpler, AWS-native, has no control-plane charge, integrates directly with IAM, ALB, and CloudWatch, and needs no Kubernetes expertise. EKS gives you the Kubernetes API and ecosystem - Helm, operators, CRDs, portability across clouds - at the cost of more moving parts, a control-plane charge, and version upgrades to manage. Choose ECS when you are all-in on AWS and want the lowest operational burden; choose EKS when you need the ecosystem, portability, or already have Kubernetes skills. See [what is the difference between ECS, EKS, and Fargate](./what-is-the-difference-between-ecs-eks-and-fargate.md).

## Example

```json
// Task definition: note the TWO roles, secrets by ARN, and a container health check
{
  "family": "payments",
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::111122223333:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::111122223333:role/payments-task",
  "containerDefinitions": [
    {
      "name": "app",
      "image": "111122223333.dkr.ecr.eu-west-1.amazonaws.com/payments@sha256:9f2c8b1d...",
      "portMappings": [{ "containerPort": 8080, "name": "http", "appProtocol": "http" }],
      "environment": [{ "name": "LOG_LEVEL", "value": "info" }],
      "secrets": [
        {
          "name": "DB_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:eu-west-1:111122223333:secret:prod/payments/db-AbCdEf"
        }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -fsS http://localhost:8080/healthz || exit 1"],
        "interval": 15, "timeout": 5, "retries": 3, "startPeriod": 60
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/payments",
          "awslogs-region": "eu-west-1",
          "awslogs-stream-prefix": "app"
        }
      },
      "readonlyRootFilesystem": true,
      "user": "10001:10001"
    }
  ]
}
```

```hcl
# Service: private subnets, ALB, circuit breaker, ECS Exec, autoscaling
resource "aws_ecs_service" "payments" {
  name            = "payments"
  cluster         = aws_ecs_cluster.prod.id
  task_definition = aws_ecs_task_definition.payments.arn
  desired_count   = 4
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [for s in aws_subnet.private : s.id]
    security_groups  = [aws_security_group.payments.id] # per-task SG, thanks to awsvpc
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.payments.arn # target_type = "ip"
    container_name   = "app"
    container_port   = 8080
  }

  health_check_grace_period_seconds = 90 # longer than real startup, or tasks cycle

  deployment_minimum_healthy_percent = 100 # never below desired during a deploy
  deployment_maximum_percent         = 200
  deployment_circuit_breaker { enable = true, rollback = true } # auto-rollback a bad deploy

  enable_execute_command = true # `aws ecs execute-command` for a shell
  propagate_tags         = "SERVICE"
}

resource "aws_appautoscaling_policy" "payments_requests" {
  name               = "track-requests"
  service_namespace  = "ecs"
  resource_id        = "service/${aws_ecs_cluster.prod.name}/${aws_ecs_service.payments.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  policy_type        = "TargetTrackingScaling"
  target_tracking_scaling_policy_configuration {
    target_value = 1000
    predefined_metric_specification { predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label = "${aws_lb.public.arn_suffix}/${aws_lb_target_group.payments.arn_suffix}" }
  }
}
```

```bash
# Deploy: new revision, then point the service at it, then wait for stability
TD=$(aws ecs register-task-definition --cli-input-json file://taskdef.json \
      --query 'taskDefinition.taskDefinitionArn' --output text)
aws ecs update-service --cluster prod --service payments --task-definition "$TD"
aws ecs wait services-stable --cluster prod --services payments   # exits non-zero on failure

# Roll back: point at the previous revision (task definitions are immutable)
aws ecs update-service --cluster prod --service payments --task-definition payments:47

# One-off task (a migration), not a service
aws ecs run-task --cluster prod --task-definition payments-migrate:12 --launch-type FARGATE \
  --network-configuration 'awsvpcConfiguration={subnets=[subnet-0aaa],securityGroups=[sg-0bbb]}'

# Why did the task stop? stoppedReason + exitCode answer most of it.
aws ecs describe-tasks --cluster prod --tasks "$TASK_ARN" \
  --query 'tasks[].[lastStatus,stoppedReason,containers[].[name,exitCode,reason]]'

# Shell inside a running container - no SSH, no bastion
aws ecs execute-command --cluster prod --task "$TASK_ARN" \
  --container app --interactive --command "/bin/sh"
```

## Interview tips

- Lay out the four objects in order - cluster, task definition, task, service - then give the one-line distinction: a task is a run, a service is a supervisor that maintains desired count, replaces failures, and rolls out changes.
- Name **both IAM roles** and what each is for: execution role for the agent (image pull, logs, secrets) and task role for your application's AWS calls. This is the most reliably asked ECS detail.
- Use `awsvpc` and say what it buys you - a per-task ENI, so **security groups apply per task**. Then mention the VPC endpoints a private Fargate task needs, including the S3 gateway endpoint for ECR layers.
- Describe a deploy accurately: build, push, register a **new immutable revision**, update the service. Rollback is pointing at the previous revision, which is why you never deploy `:latest`.
- Volunteer the **deployment circuit breaker** with rollback and `100/200` min/max healthy percentages. Those two settings are what make ECS deploys safe.
- Have the health-check-grace-period trap ready - tasks cycling because ECS kills them before the app is ready - because "my deployment keeps failing" usually means this.
- For blue/green, name CodeDeploy with two target groups, a listener shift, canary/linear options, and `appspec.yml` with its lifecycle hooks.
- Cover scaling in two halves on EC2 launch type: service auto scaling for task count **and** capacity provider managed scaling for instances, or tasks sit unplaceable.
- Know `aws ecs execute-command` as the way into a container, and the `stoppedReason`/`exitCode` diagnostic path (`CannotPullContainerError`, 137 for OOM, ELB health check failures).
- Give a fair ECS-versus-EKS answer: ECS for lowest operational burden on AWS, EKS for the Kubernetes ecosystem and portability. See [what is the difference between ECS, EKS, and Fargate](./what-is-the-difference-between-ecs-eks-and-fargate.md), [building a CI/CD pipeline with CodePipeline, CodeBuild, and CodeDeploy](./how-do-you-build-a-ci-cd-pipeline-using-aws-codepipeline-codebuild-and-codedeploy.md), [what are deployment strategies](../devops-tools-and-automation/what-are-deployment-strategies.md), and [what are VPC endpoints](./what-are-vpc-endpoints-and-when-do-you-use-a-gateway-versus-an-interface-endpoint.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?]] (`#407`): [How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-waiting-for-a-persistentvolumeclaim.md)
- [[How does persistent storage work in Kubernetes?]] (`#443`): [How does persistent storage work in Kubernetes?](../kubernetes/how-does-persistent-storage-work-in-kubernetes.md)
- [[What is Google Cloud Platform (GCP)?]] (`#24`): [What is Google Cloud Platform (GCP)?](../cloud-platforms/what-is-google-cloud-platform-gcp.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
