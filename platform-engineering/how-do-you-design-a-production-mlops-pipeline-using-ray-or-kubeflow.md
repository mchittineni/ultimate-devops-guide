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

**Choosing between them.** They are complementary rather than rivals: KFP (or Argo Workflows underneath it) orchestrates the DAG, lineage, and artefacts, while Ray does the distributed compute inside a step - a KFP step can submit a `RayJob` via KubeRay. The trade-off is operational weight: Kubeflow is a large platform to run and upgrade, and for smaller teams a managed service (Vertex AI Pipelines, SageMaker Pipelines) or a lighter orchestrator is often the better call.

## Example

Kubeflow Pipeline definition (KFP SDK v2 - `ContainerOp` and `set_gpu_limit` are v1-era APIs that no longer exist or are deprecated):

```python
from kfp import compiler, dsl
from kfp.dsl import Dataset, Input, Model, Output


@dsl.component(base_image="python:3.12-slim", packages_to_install=["torch", "transformers"])
def train_model(dataset: Input[Dataset], model_artifact: Output[Model], epochs: int = 3):
    print(f"Loading data from {dataset.path} and training for {epochs} epochs...")
    # Training logic executing on GPU...
    with open(model_artifact.path, "w") as f:
        f.write("model_weights_v1.bin")
    model_artifact.metadata["epochs"] = epochs


@dsl.component(base_image="python:3.12-slim")
def evaluate_model(model_artifact: Input[Model], threshold: float = 0.90) -> float:
    print(f"Evaluating model at {model_artifact.path}...")
    accuracy = 0.94  # replace with a real evaluation against a held-out set
    if accuracy < threshold:
        raise ValueError(f"accuracy {accuracy} below gate {threshold}")  # fails the run
    return accuracy


@dsl.pipeline(name="llm-fine-tuning-pipeline", description="Fine-tune and evaluate a model")
def mlops_pipeline(dataset_uri: str, epochs: int = 5):
    data = dsl.importer(artifact_uri=dataset_uri, artifact_class=Dataset, reimport=False)
    train_task = train_model(dataset=data.output, epochs=epochs)
    train_task.set_accelerator_type("nvidia.com/gpu").set_accelerator_limit(2)
    evaluate_model(model_artifact=train_task.outputs["model_artifact"])


if __name__ == "__main__":
    compiler.Compiler().compile(mlops_pipeline, "pipeline.yaml")  # upload to KFP or Vertex AI
```

RayCluster manifest snippet managed via KubeRay operator:

```yaml
apiVersion: ray.io/v1
kind: RayCluster
metadata:
  name: ray-training-cluster
  namespace: ai-platform
spec:
  rayVersion: '2.58.0'
  headGroupSpec:
    rayStartParams:
      dashboard-host: '0.0.0.0'
    template:
      spec:
        containers:
          - name: ray-head
            image: rayproject/ray:2.58.0-py312
  workerGroupSpecs:
    - groupName: gpu-workers
      replicas: 4
      template:
        spec:
          containers:
            - name: ray-worker
              image: rayproject/ray:2.58.0-py312-gpu
              resources:
                limits:
                  nvidia.com/gpu: "1"
```

## Interview tips

- Contrast **DevOps CI/CD** with **MLOps CT/CD (Continuous Training & Continuous Deployment)**: DevOps deploys code changes; MLOps re-trains and redeploys when data distribution shifts occur.
- Highlight **Model Registry & Reproducibility**: emphasize logging code Git commit SHA, dataset version/hash, hyperparameters, and environment docker image to ensure 100% reproducible model builds.
- Explain **Feature Stores**: centralize feature engineering logic so training pipelines and low-latency inference services share consistent data features without skew.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you structure Terraform code for multiple environments and providers?]] (`#422`): [How do you structure Terraform code for multiple environments and providers?](../infrastructure-as-code/how-do-you-structure-terraform-code-for-multiple-environments-and-providers.md)
- [[What is Backstage and how does it build an Internal Developer Portal (IDP) with software catalogs?]] (`#634`): [What is Backstage and how does it build an Internal Developer Portal (IDP) with software catalogs?](../devops-tools-and-automation/what-is-backstage-and-how-does-it-build-an-internal-developer-portal-idp-with-software-catalogs.md)
- [[What is Infrastructure as Code?]] (`#26`): [What is Infrastructure as Code?](../infrastructure-as-code/what-is-infrastructure-as-code.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Platform Engineering](./README.md) · [All topics](../README.md)
