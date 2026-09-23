---
title: "How do you deploy and scale LLM inference serving with vLLM or Triton on Kubernetes?"
id: 241
category: "Platform Engineering"
difficulty: "Advanced"
tags:
  - devops
  - platform-engineering
  - interview-questions
---

# How do you deploy and scale LLM inference serving with vLLM or Triton on Kubernetes?

**Short answer:** Deploy LLM inference engines (such as vLLM or Triton Inference Server) on Kubernetes by mounting model weights via fast local NVMe caches or streaming from S3/OCI, enabling PagedAttention for KV cache optimization, using tensor parallelism across multiple GPUs, and managing zero-downtime model deployments with progressive traffic routing.

## Detail

Serving Large Language Models (LLMs) in production presents distinct infrastructure challenges compared to conventional web APIs due to massive model weight footprints (tens of gigabytes), high VRAM requirements, and streaming token responses.

### 1. High-Performance Inference Engines

- **vLLM:** Designed specifically for LLM serving with **PagedAttention**, an algorithm that manages Key-Value (KV) cache memory efficiently, achieving up to 24x higher throughput than standard HuggingFace Transformers.
- **Triton Inference Server:** NVIDIA's enterprise serving platform (now branded NVIDIA Dynamo Triton) offering multi-model execution, dynamic batching, and support for TensorRT-LLM, vLLM, ONNX, and PyTorch backends.

### 2. Model Weight Management & Fast Startup

- **Storage Bottleneck:** Downloading a 70B parameter model weights file (~140GB) on container startup causes extreme latency.
- **Solution - PVC Caching / ReadOnlyMany Volumes:** Use high-speed CSI drivers (e.g. FSx for Lustre, Filestore, or local NVMe instance storage pre-populated with the `hf download` CLI - the successor to `huggingface-cli` - or from S3) to share pre-downloaded weights across pods instantly.

### 3. Parallelism & Scaling Strategy

- **Tensor Parallelism (`--tensor-parallel-size`):** Splits single model matrix multiplications across multiple GPUs on the same node (e.g. 4x A10G GPUs).
- **Pipeline Parallelism:** Distributes model layers across multiple nodes over high-speed interconnects (NVIDIA NVLink / InfiniBand).
- **Zero-Downtime Model Updates:** Use Istio or Argo Rollouts to perform canary releases when deploying updated model weights or prompt templates.
- **Autoscale on the right signal:** GPU utilisation sits near 100% whenever a batch is running, so it says little about headroom. Scale on queue depth (`vllm:num_requests_waiting`), KV-cache usage, or TTFT, and route with a model-aware layer (the Gateway API Inference Extension, KServe, or llm-d) that considers each replica's load and cached prefixes.
- **Trade-off:** GPU replicas take minutes to become ready (node provisioning, image pull, weight loading), so scale-from-zero saves money at the price of long cold starts; latency-sensitive endpoints keep a warm minimum.

## Example

vLLM Kubernetes Deployment serving Llama-3-8B with GPU limits and PagedAttention:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-llama3-server
  namespace: ai-platform
spec:
  replicas: 2
  selector:
    matchLabels:
      app: vllm-llama3
  template:
    metadata:
      labels:
        app: vllm-llama3
    spec:
      containers:
        - name: vllm-container
          image: vllm/vllm-openai:v0.30.0
          args:
            - "--model"
            - "meta-llama/Meta-Llama-3-8B-Instruct"
            - "--tensor-parallel-size"
            - "2"
            - "--max-model-len"
            - "4096"
            - "--gpu-memory-utilization"
            - "0.90"
          env:
            - name: HF_TOKEN # HUGGING_FACE_HUB_TOKEN is the deprecated name
              valueFrom:
                secretKeyRef:
                  name: hf-token-secret
                  key: token
          ports:
            - containerPort: 8000
              name: http
          resources:
            limits:
              nvidia.com/gpu: "2"
              memory: 64Gi
              cpu: "16"
            requests:
              nvidia.com/gpu: "2"
              memory: 32Gi
              cpu: "8"
          volumeMounts:
            - mountPath: /root/.cache/huggingface
              name: model-cache-storage
      volumes:
        - name: model-cache-storage
          persistentVolumeClaim:
            claimName: model-weights-pvc
```

Testing OpenAI-compatible completion API served by vLLM:

```bash
curl http://vllm-llama3.ai-platform.svc.cluster.local:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Meta-Llama-3-8B-Instruct",
    "messages": [{"role": "user", "content": "Explain Kubernetes CNI in 2 sentences."}],
    "temperature": 0.7
  }'
```

## Interview tips

- Explain **PagedAttention**: explain how standard attention causes VRAM fragmentation due to pre-allocating contiguous memory for KV cache, whereas PagedAttention allocates memory in non-contiguous pages like virtual memory in operating systems.
- Highlight model weight loading strategies: downloading weights on container boot creates 15-minute start times; using persistent storage or OCI artifacts dramatically reduces cold start latency.
- Mention **OpenAI Protocol compatibility**: engines like vLLM expose OpenAI-compatible REST endpoints (`/v1/chat/completions`), simplifying frontend API integration.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you structure Terraform code for multiple environments and providers?]] (`#422`): [How do you structure Terraform code for multiple environments and providers?](../infrastructure-as-code/how-do-you-structure-terraform-code-for-multiple-environments-and-providers.md)
- [[What is Backstage and how does it build an Internal Developer Portal (IDP) with software catalogs?]] (`#634`): [What is Backstage and how does it build an Internal Developer Portal (IDP) with software catalogs?](../devops-tools-and-automation/what-is-backstage-and-how-does-it-build-an-internal-developer-portal-idp-with-software-catalogs.md)
- [[How do you write and structure a reusable Terraform module?]] (`#463`): [How do you write and structure a reusable Terraform module?](../infrastructure-as-code/how-do-you-write-and-structure-a-reusable-terraform-module.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Platform Engineering](./README.md) · [All topics](../README.md)
