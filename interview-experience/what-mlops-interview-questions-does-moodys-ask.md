---
title: "What MLOps interview questions does Moodys ask?"
id: 348
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - moodys
  - infrastructure-as-code
  - cicd
  - aws-engineering
  - cloud-cost-optimization
  - monitoring-and-logging
  - devsecops
  - docker
---

# What MLOps interview questions does Moodys ask?

## Questions

**Infrastructure and images for ML**

- **How do you set up the infrastructure for deploying ML models using Terraform?**
- **How do you manage and version Docker images stored in Amazon ECR?**

**ML platform and training**

- **Besides SageMaker, which AWS or open-source services have you used — or are aware of — for training models?**
- **If batch jobs are running ML workloads, how do you deploy without disrupting processing that is already in flight?**

**CI/CD for models**

- **How do you design and implement a complete CI/CD pipeline for ML models?**
- **Given a GitHub Actions workflow snippet, how would you identify incorrect steps and suggest improvements or missing steps for a robust pipeline?**

**Governance, cost, and monitoring**

- **How do you prevent misuse or unauthorised usage if someone tries to spin up ML services in AWS?**
- **What strategies do you use to optimise and control AWS costs for ML workloads?**
- **How do you set up monitoring and observability for models in production?**

**Background**

- **Introduce yourself and explain the background that is relevant to DevOps and MLOps.**

## Example

```text
Moodys — MLOps Engineer (3-4 YOE), reported round
10 questions

  Governance / cost / monitor  3   block unauthorised ML service creation,
                                   control GPU spend, model observability
  CI/CD for models             2   full ML pipeline design, critique a
                                   GitHub Actions snippet
  Infrastructure and images    2   Terraform for model deployment,
                                   ECR image versioning
  ML platform and training     2   alternatives to SageMaker, deploying
                                   without disrupting in-flight batch jobs
  Background                   1   DevOps/MLOps relevance

WHAT MAKES THIS AN MLOPS ROUND, NOT A DEVOPS ONE
  Three questions have no DevOps equivalent: model observability (drift, not
  just latency), the training-service landscape, and cost control where a
  single GPU instance can outspend an entire web tier. Everything else is
  standard DevOps wearing ML clothing.
```

## Interview tips

- Model observability is the question that separates an MLOps candidate from a DevOps one, so answer it in two layers. The infrastructure layer is what you already know — latency, throughput, error rate, saturation, endpoint availability. The model layer is the part they are actually testing: input data drift, prediction drift, feature distribution skew between training and serving, and — when labels eventually arrive — accuracy, precision, and recall degradation over time. Add the operational pieces: log every prediction with its inputs and model version for later audit, track which model version served which request, and alert on drift thresholds rather than on accuracy you cannot measure in real time. For a ratings agency, mention explainability and audit retention as regulatory requirements. See [monitoring in DevOps](../monitoring-and-logging/what-is-monitoring-in-devops.md).
- The batch-jobs deployment question is the best scenario here, and the key insight is that you must not interrupt work in flight. Give the mechanisms: drain rather than kill — stop accepting new work and let running jobs finish before swapping the image; version the job definition so already-queued jobs keep using the old one; make jobs idempotent and checkpointed so a retry is safe; use a queue with visibility timeouts so an interrupted message is redelivered rather than lost; and deploy the new version alongside, routing only new submissions to it. Say that blue-green works for endpoints but for batch you need generation-based versioning. See [deployment strategies](../devops-tools-and-automation/what-are-deployment-strategies.md).
- The unauthorised-ML-services question is a governance answer, not a technical one, and it has a specific shape on AWS: service control policies at the organisation level denying expensive instance families or whole services outside approved accounts, IAM conditions restricting `ec2:InstanceType` and requiring tags, permission boundaries so even administrators cannot escalate, Service Quotas capped deliberately low, budgets with anomaly detection and alerts, and Config rules flagging non-compliant resources. Say that SCPs are the only control an account administrator cannot work around — that is why they are the right answer. See [structuring a multi-account AWS organisation](../aws-engineering/how-do-you-structure-a-multi-account-aws-organisation.md) and [least-privilege identity in the cloud](../cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md).
- ML cost control differs from general cloud cost work in ways worth naming explicitly: GPU instances dominate the bill, so use Spot for training with checkpointing so an interruption costs minutes rather than the whole run; right-size the instance to the model rather than defaulting to the largest available; use managed spot training if you are on SageMaker; separate training from inference so you are not paying for accelerators to sit idle serving requests; use serverless or auto-scaling inference endpoints that scale to zero for infrequent models; and cap notebook instances with automatic shutdown, because forgotten notebooks are a classic line item. See [cloud cost optimisation](../cloud-cost-optimization/what-is-cloud-cost-optimization.md).
- For the ML CI/CD pipeline, do not describe an application pipeline. The distinguishing feature is that you version three things — code, data, and the model — and that there are two pipelines, not one: a training pipeline (data validation, feature engineering, train, evaluate against a baseline, register the model if it beats the incumbent) and a deployment pipeline (pull the approved model from the registry, build the serving image, deploy behind a canary, monitor, roll back on regression). Name a model registry and experiment tracking (MLflow or SageMaker Model Registry), say that a model is promoted on evaluation metrics rather than a green test suite, and mention that retraining may be triggered by drift rather than by a commit. See [what a CI/CD pipeline is](../cicd/what-is-ci-cd-pipeline.md).
- The GitHub Actions critique question is a review exercise, so go in with a checklist you can apply to any snippet: are actions pinned to a commit SHA rather than a mutable tag; are permissions minimised with a top-level `permissions` block; is authentication done through OIDC rather than a stored access key; is there a `concurrency` group to stop overlapping deploys; are dependencies and layers cached; is `needs` used so jobs are correctly ordered; are secrets referenced rather than echoed; is there a timeout; and are environments with approvals used for production. Saying "here is the checklist I would apply" is stronger than reacting line by line.
- ECR image versioning should reach immutability: enable tag immutability on the repository so a tag can never be moved, tag with the Git SHA or a semantic version rather than `latest`, and deploy by digest so what runs is cryptographically identical to what you tested. Add lifecycle policies to expire untagged and old images so storage does not grow forever, scan on push, and — for ML — include the framework version and model version in the tag scheme so an image is traceable to the model it serves. See [signing and verifying container images](../devsecops/how-do-you-sign-and-verify-container-images.md).
- For training alternatives to SageMaker, group them rather than listing at random: on AWS, EC2 with deep-learning AMIs, Batch for queued training jobs, EKS with Kubeflow or Ray for distributed training, and EMR for Spark-based feature work; open-source, Kubeflow, Ray, MLflow for tracking, Metaflow, and Airflow or Dagster for orchestration. Be honest about which you have run versus which you are aware of — the question explicitly offers that distinction, so use it.
- The Terraform-for-ML question wants the ML-specific resources, not a generic VPC answer: the model registry and artefact buckets with versioning and encryption, ECR repositories, the training and inference IAM roles, the endpoint or serving infrastructure with autoscaling, GPU node groups or instance types with the right quotas, VPC endpoints so training data never traverses the internet, and KMS keys for data at rest. Say you would keep environments in separate state and expose the model version as a variable so promotion is a configuration change, not a code change. See [what Terraform is](../infrastructure-as-code/what-is-terraform.md).
- Moodys is a ratings and analytics business, so lineage and auditability carry weight. Wherever you can, add the sentence that a given prediction can be traced back to a specific model version, training dataset, and code commit — that reproducibility claim is what a regulated financial employer is listening for.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
