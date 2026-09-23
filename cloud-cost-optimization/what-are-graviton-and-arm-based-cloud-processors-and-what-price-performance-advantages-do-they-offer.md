---
title: "What are Graviton and ARM-based cloud processors and what price-performance advantages do they offer?"
id: 640
category: "Cloud Cost Optimization"
difficulty: "Beginner"
tags:
  - devops
  - cloud-cost-optimization
  - interview-questions
  - aws
  - graviton
  - arm
  - cost-optimization
  - performance
quiz:
  stem: "What must engineering teams update in their CI/CD build pipelines to deploy containerized applications onto AWS Graviton instances?"
  options:
    - "They must rewrite their entire application in C++"
    - "They must build and publish multi-architecture container images targeting `linux/arm64` (e.g. via `docker buildx`)"
    - "They must disable all unit tests"
    - "They must purchase an enterprise license from ARM Holdings"
  answer: 2
  explanation: "Because Graviton uses ARM64 architecture, pipelines must compile binaries and package container images targeting `linux/arm64` using tools like Docker Buildx."
---

# What are Graviton and ARM-based cloud processors and what price-performance advantages do they offer?

**Short answer:** AWS Graviton (and comparable Arm processors - Azure Cobalt, Google Axion, Ampere Altra) are 64-bit Arm server CPUs that typically deliver meaningfully better price-performance than comparable x86 instances - AWS quotes up to 40% for many workloads - because instances are priced lower and each vCPU is a full physical core.

## Detail

Moving suitable workloads from x86 to Arm64 is one of the highest-return cost optimisations available, because for interpreted and managed languages it is often a rebuild rather than a rewrite.

### Architectural differences that matter

- **x86_64 (Intel Xeon, AMD EPYC)**: on most Intel-based and older AMD-based instance families a vCPU is one hardware thread, so two vCPUs share a physical core via SMT (Hyper-Threading). AWS's newer AMD families (for example `m7a`/`c7a`) disable SMT, so a vCPU is a full core there too.
- **Arm64 (Graviton2/3/4, and Graviton5 in `m9g` since mid-2026)**: every vCPU is a dedicated physical core with no sibling hyperthread, which gives more predictable per-vCPU performance and no cross-thread contention.

### Where the savings come from

- **Lower hourly price**: a Graviton instance is typically around 20% cheaper per hour than the equivalent x86 size in the same generation (compare `c7g.xlarge` with `c7i.xlarge` in your region).
- **Performance per vCPU**: many workloads run as fast or faster, because a full core per vCPU and large caches help throughput-oriented services. The gain varies widely by workload, so **benchmark your own service** rather than trusting a headline number.
- **Managed services**: RDS, Aurora, ElastiCache, OpenSearch, Lambda, and Fargate offer Graviton options, often a one-line change with no code involved.

### Migration effort and pitfalls

- **Build multi-architecture images** in CI (`docker buildx --platform linux/amd64,linux/arm64`, or native Arm runners, which avoid slow QEMU emulation) and publish them under a single manifest list.
- **Check native dependencies**: Go, Java 11+ (17+ recommended), Node.js, Python, .NET 6+, and Rust generally just work; C/C++ extensions, old binary-only agents, and hand-tuned x86 assembly (SIMD intrinsics) are where migrations stall.
- **Mixed-arch clusters** need `kubernetes.io/arch` node affinity or a scheduler-aware tool (Karpenter can offer both architectures) until every image is multi-arch.
- **Commitments**: EC2 Instance Savings Plans and standard RIs are tied to an instance family, so Compute Savings Plans are safer while you move.

## Example

```bash
# One pipeline step: build and push a multi-arch image (manifest list for amd64 + arm64).
docker buildx create --use --name multiarch
docker buildx build --platform linux/amd64,linux/arm64 \
  -t registry.example.com/api:1.9.0 --push .

docker buildx imagetools inspect registry.example.com/api:1.9.0
# Manifests:
#   Platform: linux/amd64
#   Platform: linux/arm64      <- Graviton nodes pull this one automatically
```

```yaml
# Kubernetes: allow the scheduler (or Karpenter) to use either architecture.
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - { key: kubernetes.io/arch, operator: In, values: ["amd64", "arm64"] }
```

## Interview tips

- Explain where the saving comes from: lower hourly price plus a full physical core per vCPU.
- Be precise: "no SMT" is true for Graviton but also for AWS's newer AMD families, and headline percentages need your own benchmarks.
- The migration work is multi-arch images and native dependencies - name `docker buildx` and native Arm CI runners.
- Mention managed services (RDS, ElastiCache, Lambda, Fargate) as the easiest wins.
- Note the commitment interaction: prefer Compute Savings Plans while architectures are changing.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[How does OpenID Connect (OIDC) eliminate long-lived cloud credentials in CI/CD pipelines?]] (`#533`): [How does OpenID Connect (OIDC) eliminate long-lived cloud credentials in CI/CD pipelines?](../cicd/how-does-openid-connect-oidc-eliminate-long-lived-cloud-credentials-in-ci-cd-pipelines.md)
- [[How does Docker BuildKit work and what caching and build features does it unlock?]] (`#515`): [How does Docker BuildKit work and what caching and build features does it unlock?](../docker/how-does-docker-buildkit-work-and-what-caching-and-build-features-does-it-unlock.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Cost Optimization](./README.md) · [All topics](../README.md)
