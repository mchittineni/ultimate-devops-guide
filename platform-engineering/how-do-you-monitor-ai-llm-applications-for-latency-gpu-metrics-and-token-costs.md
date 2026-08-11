---
title: "How do you monitor AI/LLM applications for latency, GPU metrics, and token costs?"
id: 242
category: "Platform Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - platform-engineering
  - interview-questions
---

# How do you monitor AI/LLM applications for latency, GPU metrics, and token costs?

**Short answer:** Monitor AI/LLM applications by collecting hardware telemetry via NVIDIA DCGM Exporter (GPU utilization, VRAM, temperature), tracking inference performance metrics (TTFT, ITL, queue depth), capturing LLM app traces via OpenTelemetry/LangSmith, and calculating per-tenant token consumption for FinOps cost governance.

## Detail

Monitoring generative AI workloads requires expanding traditional RED (Rate, Errors, Duration) metrics to include GPU hardware metrics, streaming token dynamics, and model cost allocation:

### 1. GPU Hardware Telemetry (NVIDIA DCGM Exporter)

- **DCGM Exporter:** Scrapes low-level GPU metrics via the NVIDIA Data Center GPU Manager (DCGM) and exposes them to Prometheus.
- **Key DCGM Metrics:**
  - `DCGM_FI_DEV_GPU_UTIL`: GPU compute core utilization percentage.
  - `DCGM_FI_DEV_FB_USED` / `DCGM_FI_DEV_FB_FREE`: Frame buffer (VRAM) memory allocation.
  - `DCGM_FI_DEV_POWER_USAGE`: Power draw in watts (crucial for energy & cooling management).
  - `DCGM_FI_DEV_XID_ERRORS`: Hardware errors reported by the GPU driver (e.g. XID 31 memory fault).

### 2. Streaming LLM Inference Metrics

Unlike standard HTTP endpoints returning single payloads, LLM responses stream over Time:

- **Time to First Token (TTFT):** Latency from request receipt until the first generated token arrives. Critical for user-perceived responsiveness.
- **Inter-Token Latency (ITL):** Time taken to generate each subsequent token (determines streaming smooth reading speed).
- **Tokens Per Second (TPS):** Total throughput generated across batch requests.

### 3. AI FinOps & Token Cost Management

- **Prompt & Completion Token Tracking:** Instrument application code (or API Gateway proxies) to record `prompt_tokens` and `completion_tokens` parsed from model response metadata.
- **Cost Allocation:** Multiply token counts by provider pricing models (e.g. AWS Bedrock, OpenAI, or self-hosted GPU node hourly costs) grouped by team, application, or user environment tags.

## Example

Prometheus ServiceMonitor scraping NVIDIA DCGM Exporter metrics:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: dcgm-exporter-monitor
  namespace: ai-platform
spec:
  selector:
    matchLabels:
      app: dcgm-exporter
  endpoints:
    - port: metrics
      interval: 10s
      path: /metrics
```

Python application tracing LLM calls with OpenTelemetry and token metrics:

```python
import time
from prometheus_client import Counter, Histogram

TTFT_HISTOGRAM = Histogram(
    "llm_time_to_first_token_seconds",
    "Time to first token latency in seconds",
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)
TOKEN_COUNTER = Counter(
    "llm_tokens_total",
    "Total tokens processed",
    ["type", "model", "team"]
)

def track_llm_inference(prompt: str, model_name: str, team_id: str):
    start_time = time.time()

    # Call vLLM or OpenAI streaming client
    stream = call_llm_api_streaming(prompt, model=model_name)

    first_token_received = False
    prompt_tokens = len(prompt.split()) # Approximate or parse from API
    completion_tokens = 0

    for chunk in stream:
        if not first_token_received:
            TTFT_HISTOGRAM.observe(time.time() - start_time)
            first_token_received = True
        completion_tokens += 1

    TOKEN_COUNTER.labels(type="prompt", model=model_name, team=team_id).inc(prompt_tokens)
    TOKEN_COUNTER.labels(type="completion", model=model_name, team=team_id).inc(completion_tokens)
```

Useful Grafana PromQL Queries:

```promql
# Average GPU VRAM Utilization percentage across node pool
sum(DCGM_FI_DEV_FB_USED) / sum(DCGM_FI_DEV_FB_USED + DCGM_FI_DEV_FB_FREE) * 100

# GPU Hardware XID Errors (Alert if > 0)
sum(increase(DCGM_FI_DEV_XID_ERRORS[5m])) by (pod, gpu)
```

## Interview tips

- Define **TTFT** (Time to First Token) vs **ITL** (Inter-Token Latency) clearly: TTFT reflects model startup/prompt processing time, while ITL reflects generation throughput.
- Know the critical **DCGM metrics**: `DCGM_FI_DEV_GPU_UTIL`, `DCGM_FI_DEV_FB_USED`, and `DCGM_FI_DEV_XID_ERRORS`.
- Explain how **AI FinOps** operates: tracking token usage at the API Gateway level (e.g. Kong, Ambassador, or LiteLLM Proxy) allows enforcing per-team rate limits and cost budgets.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you structure Terraform code for multiple environments and providers?]] (`#422`): [How do you structure Terraform code for multiple environments and providers?](../infrastructure-as-code/how-do-you-structure-terraform-code-for-multiple-environments-and-providers.md)
- [[How do you write and structure a reusable Terraform module?]] (`#463`): [How do you write and structure a reusable Terraform module?](../infrastructure-as-code/how-do-you-write-and-structure-a-reusable-terraform-module.md)
- [[What is Service Mesh?]] (`#68`): [What is Service Mesh?](../cloud-native-architecture/what-is-service-mesh.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Platform Engineering](./README.md) · [All topics](../README.md)
