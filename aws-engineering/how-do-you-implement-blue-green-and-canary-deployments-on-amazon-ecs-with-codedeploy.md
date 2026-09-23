---
title: "How Do You Implement Blue-Green and Canary Deployments on Amazon ECS with CodeDeploy?"
id: 737
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - aws-engineering
  - ecs
  - codedeploy
  - canary-deployment
quiz:
  stem: "What is the primary advantage of keeping the original 'Blue' ECS tasks running while CodeDeploy shifts traffic to the 'Green' tasks?"
  options:
    - "It halves the cost of AWS Fargate compute billing."
    - "It enables near-instantaneous rollback without rebuilding containers if an error occurs during traffic shifting."
    - "It allows two different versions of code to write to the same SQLite database file concurrently."
    - "It eliminates the need for an Application Load Balancer."
  answer: 2
  explanation: "Because the healthy original tasks remain active and registered during the shift, CodeDeploy can immediately swing the ALB listener back to the original target group in seconds if a CloudWatch alarm triggers."
---

# How Do You Implement Blue-Green and Canary Deployments on Amazon ECS with CodeDeploy?

**Short answer:** ECS blue-green deployments use AWS CodeDeploy and Application Load Balancer target groups to provision replacement tasks, validate health checks via a test listener port, shift traffic incrementally (e.g., 10% canary for 15 minutes), and execute automatic rollback upon CloudWatch alarm triggers.

## Detail

### Moving Beyond Rolling Updates

Default ECS rolling updates replace tasks incrementally. However, if a regression or runtime failure only manifests under production load, rolling updates can degrade the service before rollback completes.

AWS CodeDeploy integrated with Amazon ECS and an Application Load Balancer (ALB) provides automated, zero-downtime Blue-Green and Canary deployments. Since 2025, ECS also has **built-in** blue/green, canary, and linear deployments in its own deployment controller (with Lambda lifecycle hooks and alarm-based rollback), so new services can get the same result without CodeDeploy; the CodeDeploy route remains common in existing pipelines and is what this answer describes.

### Infrastructure Prerequisites

- **Two ALB Target Groups**:
  - **Target Group 1 (Production)**: Routes live user traffic from the production listener (e.g., port 443).
  - **Target Group 2 (Test/Replacement)**: Routes traffic from a test listener (e.g., port 8443) for validation before shifting live users.
- **ECS Service Configuration**: `deploymentController: CODE_DEPLOY`.
- **AppSpec.yaml File**: Defines the task definition, target network configuration, and lifecycle hooks.
- **Limitations of the CodeDeploy controller**: the service's deployment configuration, load balancers, and some settings can only be changed through CodeDeploy deployments, and features such as ECS Service Connect are not supported with `CODE_DEPLOY` - another reason new services often choose the built-in ECS strategies.

### Deployment Process Flow

1. **Provision Green Tasks**: CodeDeploy registers new container tasks in the inactive target group (Target Group 2).
2. **Execute Test Validation (`AfterAllowTestTraffic` hook)**: CodeDeploy invokes an AWS Lambda function to run synthetic tests against the test listener (port 8443).
3. **Shift Traffic Based on Strategy**:
   - **Canary**: `CodeDeployDefault.ECSCanary10Percent15Minutes` shifts 10% of traffic immediately, waits 15 minutes, then shifts the remaining 90%.
   - **Linear**: `CodeDeployDefault.ECSLinear10PercentEvery3Minutes` shifts 10% every 3 minutes until 100%.
   - **All-at-Once**: Switches 100% of live traffic immediately after validation.
4. **CloudWatch Alarm Monitoring**: If any metric (e.g., ALB 5XX error rate, high latency) breaches during the deployment window, CodeDeploy triggers an **instant automated rollback** by swinging traffic back to Target Group 1.
5. **Terminate Blue Tasks**: Once stable for a configured bake time, original tasks are terminated.

```text
[ALB Port 443] ──────► [Target Group 1 (Blue / Active)]  ──► [v1 Tasks]
       │
       ▼ (Shift Traffic 10% ──► 100%)
[ALB Port 8443 (Test)] ──► [Target Group 2 (Green / Test)]  ──► [v2 Tasks]
```

### Real-World Production Scenario

A payments company releases a new microservice version on Amazon ECS. CodeDeploy spins up the new tasks and routes 10% of live customer traffic. Within 4 minutes, an elevated 502 Bad Gateway alarm triggers on CloudWatch due to a database connection pool leak. CodeDeploy instantly aborts the deployment and routes 100% of traffic back to the healthy blue target group with zero customer outage.

## Example

```yaml
# appspec.yml for an ECS blue/green deployment through CodeDeploy
version: 0.0
Resources:
  - TargetService:
      Type: AWS::ECS::Service
      Properties:
        TaskDefinition: "arn:aws:ecs:eu-west-1:111122223333:task-definition/payments:48"
        LoadBalancerInfo:
          ContainerName: "app"
          ContainerPort: 8080
Hooks:
  - AfterAllowTestTraffic: "payments-smoke-tests" # Lambda: hit the 8443 test listener
  - BeforeAllowTraffic: "payments-predeploy-checks"
```

```hcl
resource "aws_codedeploy_deployment_group" "payments" {
  app_name               = aws_codedeploy_app.payments.name # compute_platform = "ECS"
  deployment_group_name  = "payments-prod"
  service_role_arn       = aws_iam_role.codedeploy.arn
  deployment_config_name = "CodeDeployDefault.ECSCanary10Percent15Minutes"

  deployment_style {
    deployment_type   = "BLUE_GREEN"
    deployment_option = "WITH_TRAFFIC_CONTROL"
  }

  auto_rollback_configuration {
    enabled = true
    events  = ["DEPLOYMENT_FAILURE", "DEPLOYMENT_STOP_ON_ALARM"]
  }

  alarm_configuration {
    enabled = true
    alarms  = [aws_cloudwatch_metric_alarm.payments_5xx.alarm_name]
  }

  blue_green_deployment_config {
    deployment_ready_option {
      action_on_timeout = "CONTINUE_DEPLOYMENT"
    }
    terminate_blue_instances_on_deployment_success {
      action                           = "TERMINATE"
      termination_wait_time_in_minutes = 30 # instant rollback window
    }
  }

  ecs_service {
    cluster_name = aws_ecs_cluster.prod.name
    service_name = aws_ecs_service.payments.name # deployment_controller { type = "CODE_DEPLOY" }
  }

  load_balancer_info {
    target_group_pair_info {
      prod_traffic_route {
        listener_arns = [aws_lb_listener.https.arn]
      }
      test_traffic_route {
        listener_arns = [aws_lb_listener.test_8443.arn]
      }
      target_group {
        name = aws_lb_target_group.blue.name
      }
      target_group {
        name = aws_lb_target_group.green.name
      }
    }
  }
}
```

## Interview tips

- Explain the role of the two ALB target groups: one serves live production traffic, the other receives test traffic before traffic shifting starts.
- Discuss CodeDeploy lifecycle hooks for ECS (`BeforeInstall`, `AfterInstall`, `AfterAllowTestTraffic`, `BeforeAllowTraffic`, `AfterAllowTraffic`).
- Mention that ECS now offers built-in blue/green, canary, and linear strategies, and when you would still pick CodeDeploy (existing pipelines, org standard).
- Highlight the instant rollback capability: because the blue tasks remain running until the end of the bake time, rolling back takes seconds.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Cloud Computing?]] (`#21`): [What is Cloud Computing?](../cloud-platforms/what-is-cloud-computing.md)
- [[How does networking differ across AWS, Azure, and GCP?]] (`#282`): [How does networking differ across AWS, Azure, and GCP?](../cloud-platforms/how-does-networking-differ-across-aws-azure-and-gcp.md)
- [[How does the Cloud Shared Responsibility Model divide security obligations between IaaS, PaaS, and SaaS?]] (`#543`): [How does the Cloud Shared Responsibility Model divide security obligations between IaaS, PaaS, and SaaS?](../cloud-platforms/how-does-the-cloud-shared-responsibility-model-divide-security-obligations-between-iaas-paas-and-saas.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
