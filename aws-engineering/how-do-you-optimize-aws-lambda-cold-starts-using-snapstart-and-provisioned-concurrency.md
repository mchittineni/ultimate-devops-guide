---
title: "How Do You Optimize AWS Lambda Cold Starts Using SnapStart and Provisioned Concurrency?"
id: 735
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - aws-engineering
  - lambda
  - serverless
  - cold-start
quiz:
  stem: "How does AWS Lambda SnapStart drastically reduce cold start times for supported runtimes such as Java?"
  options:
    - "It permanently keeps physical EC2 instances running 24/7 in every availability zone."
    - "It initializes the code during deployment and takes an encrypted snapshot of the MicroVM memory and disk, resuming subsequent invocations from this snapshot."
    - "It converts all Java bytecode directly into static HTML web pages."
    - "It bypasses all AWS IAM and VPC network security checks."
  answer: 2
  explanation: "SnapStart initializes the execution environment at deployment time and caches a snapshot of the MicroVM memory state. New execution environments are restored directly from this snapshot in under 200ms."
---

# How Do You Optimize AWS Lambda Cold Starts Using SnapStart and Provisioned Concurrency?

**Short answer:** AWS Lambda cold starts occur when a new execution environment is initialized. Provisioned Concurrency eliminates cold starts by keeping pre-warmed execution instances ready, while AWS Lambda SnapStart takes a Firecracker microVM snapshot of the initialized environment when you publish a version and restores from it (supported for Java, Python, and .NET managed runtimes), typically cutting heavy-runtime cold starts to a few hundred milliseconds or less.

## Detail

### The Anatomy of a Serverless Cold Start

When an AWS Lambda function receives a request and no idle execution environment exists, Lambda must:

1. Download the function code/container image.
2. Initialize the MicroVM execution environment (Firecracker).
3. Initialize the runtime (e.g., JVM, Node.js, Python).
4. Run the function's initialization code (class loading, database connection setups, dependency injection).

This sequence is the **cold start**. While lightweight runtimes (Node.js, Python, Go) experience cold starts of 100ms–500ms, heavy enterprise runtimes (Java/Spring Boot, .NET) often experience cold starts of 5 to 15 seconds.

### Optimization Strategies

#### 1. AWS Lambda SnapStart (Java, Python, .NET)

- **Mechanism**: Initializes the function during deployment, takes an encrypted snapshot of the Firecracker MicroVM memory and disk state, and caches it.
- **Execution**: When invoked, Lambda resumes the environment from the snapshot cache rather than initializing from scratch, reducing cold starts from 8 seconds to under 200 milliseconds.
- **Cost**: **no extra charge for Java** managed runtimes; for Python and .NET, SnapStart adds a snapshot caching charge (per published version) and a restoration charge each time an environment is restored.
- **Requirements and limits**: works on published versions and aliases, not `$LATEST`; cannot be combined with provisioned concurrency, Amazon EFS, or ephemeral storage above 512 MB; supported runtimes only (not container images or custom runtimes).
- **Caveat**: Uniqueness/randomness must not be pre-computed during initialization (e.g., seeding random number generators), and network connections opened during init must be re-established after restore - use the runtime hooks (CRaC `beforeCheckpoint`/`afterRestore` on Java, and the equivalent hooks on Python and .NET).

#### 2. Provisioned Concurrency

- **Mechanism**: Pre-initializes a requested number of execution environments that remain running and ready to respond immediately.
- **Execution**: Completely eliminates cold starts for requests within the provisioned threshold.
- **Cost**: Incurs an ongoing hourly cost per provisioned concurrency capacity unit in addition to standard request duration charges.
- **Autoscaling**: Can be managed with Application Auto Scaling based on schedule or utilization metrics.

**Billing note.** Since August 2025, Lambda bills the INIT phase for on-demand invocations of managed runtimes the same way as the handler, so a slow cold start now costs money as well as latency - another reason to shrink initialization.

```text
Standard Cold Start:
[Download Code] ──► [Init MicroVM] ──► [Init Runtime] ──► [Init Code] ──► [Invoke Function]
└────────────────────────── 5 to 10 Seconds ─────────────────────────┘

SnapStart Invocation:
[Restore MicroVM Snapshot from Cache] ──► [Invoke Function]
└────────────── < 200 ms ────────────┘
```

#### 3. Architectural Best Practices

- Minimize package size: remove unused dependencies.
- Lazy-load heavy SDK clients inside handlers if they are not needed on every invocation.
- Increase memory allocation: Lambda allocates proportional CPU power, speeding up initialization code.
- Use `arm64` (Graviton) where dependencies allow - usually cheaper per GB-second - and keep runtimes current (for example Java 21, Python 3.13, Node.js 22), since deprecated runtimes stop receiving patches and eventually block updates.

### Real-World Production Scenario

A financial banking service builds a transaction authorization API using Java 17 and Spring Boot on AWS Lambda. Initial cold starts take 9 seconds, causing API Gateway timeouts. By enabling AWS Lambda SnapStart, initialization runs at deployment time and runtime resume duration drops to 160ms, meeting the strict 500ms P99 latency SLA without the added cost of Provisioned Concurrency.

## Example

```yaml
# AWS SAM: SnapStart on a Java function (applies to published versions via the alias)
Resources:
  AuthorizeFn:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: java21
      Architectures: [arm64]
      Handler: com.acme.Authorize::handleRequest
      MemorySize: 2048
      CodeUri: target/authorize.jar
      AutoPublishAlias: live # SnapStart needs a published version
      SnapStart:
        ApplyOn: PublishedVersions
```

```bash
# Provisioned concurrency on the alias for a latency-critical Node.js API (not combinable with SnapStart)
aws lambda put-provisioned-concurrency-config --function-name checkout-api \
  --qualifier live --provisioned-concurrent-executions 20

# Measure: Init Duration (and Restore Duration for SnapStart) in the REPORT log lines
aws logs filter-log-events --log-group-name /aws/lambda/checkout-api \
  --filter-pattern '"Init Duration"' --max-items 5 --query 'events[].message'
```

## Interview tips

- Explain the difference in cost model: SnapStart is free for Java and charged for Python/.NET, limited to supported managed runtimes on published versions; Provisioned Concurrency works with all runtimes but costs an ongoing fee whether or not it is used - and the two cannot be combined on the same version.
- Discuss the 'snapshot uniqueness' caveat with SnapStart: secrets or random seeds generated during init might be reused across resumed snapshots unless refreshed via runtime hooks.
- Highlight that increasing function memory also increases CPU allocation, directly shortening initialization code duration.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is AWS (Amazon Web Services)?]] (`#22`): [What is AWS (Amazon Web Services)?](../cloud-platforms/what-is-aws-amazon-web-services.md)
- [[What is Azure?]] (`#23`): [What is Azure?](../cloud-platforms/what-is-azure.md)
- [[What is Google Cloud Platform (GCP)?]] (`#24`): [What is Google Cloud Platform (GCP)?](../cloud-platforms/what-is-google-cloud-platform-gcp.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
