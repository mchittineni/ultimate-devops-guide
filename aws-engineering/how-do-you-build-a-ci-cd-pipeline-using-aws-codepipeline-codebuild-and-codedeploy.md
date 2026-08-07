---
title: "How do you build a CI/CD pipeline using AWS CodePipeline, CodeBuild, and CodeDeploy?"
id: 248
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - aws-engineering
  - interview-questions
---

# How do you build a CI/CD pipeline using AWS CodePipeline, CodeBuild, and CodeDeploy?

**Short answer:** Build an AWS-native CI/CD pipeline by using **AWS CodePipeline** to orchestrate stages (Source, Build, Test, Deploy), **AWS CodeBuild** with a `buildspec.yml` file to compile application artifacts or Docker images, and **AWS CodeDeploy** with an `appspec.yml` file to execute zero-downtime Blue/Green deployments to ECS, EKS, or EC2 Auto Scaling groups.

## Detail

AWS provides a fully managed, serverless suite of developer tools to build continuous integration and continuous deployment pipelines natively:

### 1. AWS CodePipeline (Pipeline Orchestration)

- **Workflow Engine:** Connects stages (Source → Build → Test → Staging → Production Approval → Deploy).
- **Integrations:** Triggered automatically via EventBridge when commits are pushed to GitHub, AWS CodeCommit, or Bitbucket, or when images land in Amazon ECR.

### 2. AWS CodeBuild (Continuous Integration)

- **Serverless Build Execution:** Spins up ephemeral compute containers to execute compilation, unit testing, and Docker image packaging.
- **`buildspec.yml` Specification:** Defines phase instructions (`install`, `pre_build`, `build`, `post_build`), environment variables, and build output artifacts.

### 3. AWS CodeDeploy (Continuous Deployment)

- **Deployment Strategies:** Supports In-Place deployments (rolling updates) and **Blue/Green deployments** (spinning up a parallel green environment and shifting ALB target group traffic).
- **`appspec.yml` Specification:** Defines deployment hooks (`BeforeInstall`, `AfterInstall`, `ApplicationStart`, `ValidateService`) for EC2/On-Premises, or ECS task definition traffic routing configuration.

## Example

**1. AWS CodeBuild specification file (`buildspec.yml`):**

```yaml
version: 0.2

phases:
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
      - REPOSITORY_URI=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/web-app
      - COMMIT_HASH=$(echo $CODEBUILD_RESOLVED_COMMIT_ID | cut -c 1-7)
      - IMAGE_TAG=${COMMIT_HASH:-latest}
  build:
    commands:
      - echo Build started on $(date)
      - echo Building the Docker image...
      - docker build -t $REPOSITORY_URI:latest .
      - docker tag $REPOSITORY_URI:latest $REPOSITORY_URI:$IMAGE_TAG
  post_build:
    commands:
      - echo Build completed on $(date)
      - echo Pushing the Docker image to ECR...
      - docker push $REPOSITORY_URI:latest
      - docker push $REPOSITORY_URI:$IMAGE_TAG
      - echo Writing image definitions file for ECS...
      - printf '[{"name":"web-app","imageUri":"%s"}]' $REPOSITORY_URI:$IMAGE_TAG > imagedefinitions.json

artifacts:
  files:
    - imagedefinitions.json
```

**2. AWS CodeDeploy specification file (`appspec.yml`) for ECS Blue/Green Deployment:**

```yaml
version: 0.0
Resources:
  - TargetService:
      Type: AWS::ECS::Service
      Properties:
        TaskDefinition: <TASK_DEFINITION>
        LoadBalancerInfo:
          ContainerName: "web-app"
          ContainerPort: 80
Hooks:
  - BeforeAllowTraffic: "LambdaFunctionToValidateNewDeployment"
  - AfterAllowTraffic: "LambdaFunctionToRunIntegrationTests"
```

## Interview tips

- Differentiate between `buildspec.yml` (used by **CodeBuild** to define build/test commands) and `appspec.yml` (used by **CodeDeploy** to define deployment hooks and traffic routing).
- Highlight **ECS Blue/Green deployment with AWS CodeDeploy & AWS CodePipeline**: explain how CodeDeploy creates a new ECS task set, routes test traffic to a test listener port, executes a validation Lambda hook, and shifts ALB production traffic dynamically.
- Mention security best practices: grant CodeBuild and CodeDeploy minimal IAM service roles, storing secrets in AWS Secrets Manager or Parameter Store (`/aws/reference/secretsmanager/secret_name`).

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
