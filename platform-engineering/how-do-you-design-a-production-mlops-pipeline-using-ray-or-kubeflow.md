---
title: "How do you design a production MLOps pipeline using Ray or Kubeflow?"
id: 243
category: "Platform Engineering"
difficulty: "Advanced"
tags:
  - devops
  - platform-engineering
  - interview-questions
---

# How do you design a production MLOps pipeline using Ray or Kubeflow?

**Short answer:** Design a production MLOps pipeline on Kubernetes using Kubeflow Pipelines (KFP) or KubeRay to orchestrate data ingestion, feature extraction, distributed GPU training, automated evaluation gates, model artifact registration (MLflow / Weights & Biases), and GitOps-driven deployment to inference clusters.

## Detail

MLOps (Machine Learning Operations) extends DevOps principles to machine learning, automating the lifecycle of data pipelines, model training, evaluation, and continuous deployment.

### 1. Orchestration Engine: Kubeflow vs Ray

- **Kubeflow Pipelines (KFP):** Container-native workflow engine for defining and running multi-step ML workflows. Each pipeline step runs as an isolated Kubernetes Pod with defined artifact inputs and outputs.
- **Ray / KubeRay:** Compute engine optimized for distributed AI workloads (Ray Train, Ray Data, Ray Serve). Ray allows scaling Python functions across thousands of worker cores and GPUs seamlessly.

### 2. Core MLOps Pipeline Lifecycle Stages

1. **Data Extraction & Feature Store:** Ingest batch/streaming data, clean, and store versioned features in a feature store (e.g. Feast, Hopsworks).
2. **Distributed Model Training:** Execute training across GPU worker nodes using PyTorch DDP or Ray Train, writing checkpoints to object storage (S3/GCS).
3. **Model Evaluation & Validation Gates:** Evaluate candidate models against baseline metrics (e.g., accuracy, BLEU score, latency, safety guardrails). Block pipeline progression if performance degrades.
4. **Model Registry & Provenance:** Log artifacts, hyperparameter configurations, datasets, and container image SHAs in a Model Registry (MLflow / W&B).
5. **GitOps Deployment:** Update image tags or model URI references in Helm/Kustomize manifests, triggering automated canary rollout via Argo CD.

## Example

Kubeflow Pipeline definition (Python SDK v2) running training and validation steps:

```python
from kfp import dsl
from kfp.dsl import ContainerOp, Input, Output, Dataset, Model

@dsl.component(
    base_image="python:3.10-slim",
    packages_to_install=["torch", "transformers"]
)
def train_model(
    dataset: Input[Dataset],
    model_artifact: Output[Model],
    epochs: int = 3
):
    import torch
    print(f"Loading data from {dataset.path} and training for {epochs} epochs...")
    # Training logic executing on GPU...
    with open(model_artifact.path, "w") as f:
        f.write("model_weights_v1.bin")

@dsl.component(
    base_image="python:3.10-slim",
    packages_to_install=["scikit-learn"]
)
def evaluate_model(
    model_artifact: Input[Model],
    passed_evaluation: Output[Dataset]
):
    print(f"Evaluating model at {model_artifact.path}...")
    accuracy = 0.94
    if accuracy >= 0.90:
        print("Model passed evaluation gate!")
        with open(passed_evaluation.path, "w") as f:
            f.write("APPROVED")
    else:
        raise ValueError("Model evaluation score below threshold!")

@dsl.pipeline(
    name="llm-fine-tuning-pipeline",
    description="Fine-tune and evaluate LLM model on Kubernetes"
)
def mlops_pipeline(epochs: int = 5):
    train_task = train_model(epochs=epochs)
    train_task.set_gpu_limit("2")

    eval_task = evaluate_model(model_artifact=train_task.outputs["model_artifact"])
```

RayCluster manifest snippet managed via KubeRay operator:

```yaml
apiVersion: ray.io/v1
kind: RayCluster
metadata:
  name: ray-training-cluster
  namespace: ai-platform
spec:
  rayVersion: '2.9.0'
  headGroupSpec:
    rayStartParams:
      dashboard-host: '0.0.0.0'
    template:
      spec:
        containers:
          - name: ray-head
            image: rayproject/ray:2.9.0-py310
  workerGroupSpecs:
    - groupName: gpu-workers
      replicas: 4
      template:
        spec:
          containers:
            - name: ray-worker
              image: rayproject/ray:2.9.0-py310-gpu
              resources:
                limits:
                  nvidia.com/gpu: "1"
```

## Interview tips

- Contrast **DevOps CI/CD** with **MLOps CT/CD (Continuous Training & Continuous Deployment)**: DevOps deploys code changes; MLOps re-trains and redeploys when data distribution shifts occur.
- Highlight **Model Registry & Reproducibility**: emphasize logging code Git commit SHA, dataset version/hash, hyperparameters, and environment docker image to ensure 100% reproducible model builds.
- Explain **Feature Stores**: centralize feature engineering logic so training pipelines and low-latency inference services share consistent data features without skew.

---

[⬅ Back to Platform Engineering](./README.md) · [All topics](../README.md)
