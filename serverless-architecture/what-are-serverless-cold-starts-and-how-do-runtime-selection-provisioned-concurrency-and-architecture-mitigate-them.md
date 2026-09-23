---
title: "What are Serverless Cold Starts and how do runtime selection, provisioned concurrency, and architecture mitigate them?"
id: 655
category: "Serverless Architecture"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - serverless
  - aws-lambda
  - cold-starts
  - performance
quiz:
  stem: "How does AWS Lambda SnapStart dramatically reduce cold start latency for Java applications?"
  options:
    - "By rewriting Java bytecode into Python automatically"
    - "By initializing the JVM ahead of time, taking an encrypted memory snapshot, and restoring new environments from that snapshot, typically in well under a second"
    - "By disabling TLS encryption on outgoing connections"
    - "By running functions exclusively on bare-metal mainframes"
  answer: 2
  explanation: "SnapStart initializes the Java execution environment, takes an immutable Firecracker VM memory snapshot, and caches it. New instances resume directly from the snapshot, bypassing JVM initialization."
---

# What are Serverless Cold Starts and how do runtime selection, provisioned concurrency, and architecture mitigate them?

**Short answer:** A cold start is the extra latency of a request that has to wait for a new execution environment: the platform creates the sandbox (a Firecracker microVM on Lambda), downloads the code or image, starts the runtime, and runs your initialisation code before the handler. Warm requests reuse an existing environment and skip all of that. Mitigations work at three levels: make init cheap (small packages, lazy loading, fast runtimes), keep environments ready (**provisioned concurrency**) or restore them from a snapshot (**SnapStart** for Java, Python, and .NET), and design so the user-facing path is not waiting (queues, async work, or a container service for steady latency-critical traffic). Since August 2025 Lambda bills the init phase for all functions, so cold starts are now a cost as well as a latency issue.

## Detail

**What happens on a cold start**

1. **Environment creation** - the platform places and boots a sandbox. You do not control this, beyond memory size and whether the function uses a VPC (modern Lambda VPC networking made this small).
2. **Code download** - larger zip packages and container images take longer (Lambda caches image layers, so image size matters less than it did).
3. **Runtime init** - starting the language runtime: fast for Node.js, Python, Go, and Rust; slower for the JVM and .NET without mitigation.
4. **Function init** - your global-scope code: imports, SDK clients, configuration fetches, framework start-up. This is usually the largest and most controllable part.

Typical figures range from well under 100 ms for a small Node.js or Python function to several seconds for an unoptimised Spring Boot application - measure your own with the `Init Duration` field in `REPORT` log lines.

**Mitigations**

- **Trim init.** Bundle and tree-shake (esbuild), drop unused dependencies, import heavy libraries lazily on the paths that need them, avoid framework reflection at start-up, and do not fetch configuration synchronously on every cold start if it can be cached.
- **Choose the runtime deliberately.** Compiled Go or Rust, or Node.js and Python, start fastest; for Java, use SnapStart or ahead-of-time compilation (GraalVM native image) if start-up matters.
- **More memory = more CPU**, which shortens init as well as execution.
- **SnapStart** - Lambda runs init once when a version is published, snapshots the initialised memory and disk state, and restores new environments from it. Supported for Java 11+, Python 3.12+, and .NET 8+ managed runtimes. Caveats: uniqueness (random seeds, generated IDs) and network connections captured in the snapshot must be refreshed with runtime hooks, and it is not combinable with provisioned concurrency or EFS.
- **Provisioned concurrency** - keeps a configured number of environments initialised. It removes cold starts up to that number (traffic above it spills over to on-demand), costs money while idle, and can be scheduled or auto-scaled with Application Auto Scaling.
- **Architecture** - keep synchronous user paths short; move heavy work behind a queue where a cold start is invisible; avoid function-to-function chains where cold starts compound; and for steady, latency-critical traffic consider a container service (ECS/Fargate, Cloud Run with minimum instances) or Lambda Managed Instances.

Scheduled "warmer" pings are a legacy workaround: they keep only a handful of environments warm and do nothing for concurrent bursts.

## Example

```yaml
# SAM: SnapStart on a Java function; provisioned concurrency on a latency-critical Node.js API
Resources:
  QuoteJava:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: java21
      Handler: com.example.QuoteHandler::handleRequest
      MemorySize: 2048
      SnapStart: { ApplyOn: PublishedVersions }
      AutoPublishAlias: live # SnapStart applies to published versions
  CheckoutApi:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: nodejs22.x
      Handler: index.handler
      MemorySize: 1024
      AutoPublishAlias: live
      ProvisionedConcurrencyConfig: { ProvisionedConcurrentExecutions: 20 }
```

```text
CloudWatch Logs Insights - how often, and how bad, are cold starts?
  filter @type = "REPORT"
  | stats count(*) as invocations,
          count(@initDuration) as cold_starts,
          avg(@initDuration) as avg_init_ms,
          pct(@duration, 99) as p99_ms
    by bin(1h)
```

## Interview tips

- Break a cold start into its phases and say which you control - mostly package size and init code.
- Distinguish SnapStart (snapshot restore, cheap, runtime-limited, needs uniqueness hooks) from provisioned concurrency (always warm, costs money, capped by the number you buy).
- Mention that init is now billed on Lambda, so optimising it saves money too.
- Show judgement: for steady latency-critical traffic, a container service or managed instances may be the better model, and warmer pings are not a real fix.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does Docker BuildKit work and what caching and build features does it unlock?]] (`#515`): [How does Docker BuildKit work and what caching and build features does it unlock?](../docker/how-does-docker-buildkit-work-and-what-caching-and-build-features-does-it-unlock.md)
- [[How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?]] (`#541`): [How do you design a robust CI/CD caching strategy to minimize build duration without cache poisoning?](../cicd/how-do-you-design-a-robust-ci-cd-caching-strategy-to-minimize-build-duration-without-cache-poisoning.md)
- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Serverless Architecture](./README.md) · [All topics](../README.md)
