---
title: "What is Serverless Computing?"
id: 106
category: "Serverless Architecture"
difficulty: "Beginner"
tags:
  - devops
  - serverless-architecture
  - interview-questions
---

# What is Serverless Computing?

**Short answer:** Serverless is a cloud execution model where the provider fully manages the servers - provisioning, scaling, and patching - and you are billed only for actual execution, scaling to zero when idle. Servers still exist; you simply never operate them.

## Detail

**Characteristics**

- **No server management.** No instances to size, patch, or monitor for capacity.
- **Automatic, granular scaling** - from zero to thousands of concurrent executions in seconds, driven by events.
- **Pay per use** - billed by invocation count and execution duration, so idle costs nothing.
- **Event-driven** - functions are triggered by HTTP requests, queue messages, object uploads, schedules, or database changes.
- **Stateless** - no persistence between invocations; state goes to a database, cache, or object store.

**The category is broader than functions.** Serverless containers (Cloud Run, AWS Fargate, Azure Container Apps), serverless databases (DynamoDB, Aurora Serverless v2, Aurora DSQL, Firestore), messaging (SQS, EventBridge, Pub/Sub), and workflows (Step Functions) all share the model.

**Trade-offs**

- **Cold starts** - the first invocation after idle pays initialisation latency, from tens of milliseconds to several seconds depending on runtime and package size.
- **Execution limits** - maximum duration, memory, and payload sizes constrain what fits.
- **Vendor lock-in** - event formats and service integrations are provider-specific.
- **Local development and debugging** are harder than with a conventional service.
- **Cost inversion** - extremely cheap for spiky or low-volume workloads, but more expensive than a reserved instance for sustained high throughput.

## Example

```text
The same "resize an uploaded image" job, two operating models

Server-based                              Serverless
  2 VMs (for HA) running 24x7               function triggered by the S3 upload event
  worker polls a queue                      platform delivers the event, retries on failure
  you patch the OS, size the fleet,         provider patches, scales 0 -> N per upload,
  pay for idle nights and weekends          bills per invocation and per ms of execution
  scaling = autoscaling group + alarms      scaling = automatic, bounded by concurrency limits
```

## Interview tips

- "Servers still exist - you just do not manage them" is the framing that avoids sounding naive.
- Cold starts are the guaranteed follow-up; know provisioned concurrency, smaller packages, and lighter runtimes as mitigations.
- Be able to name when serverless is the _wrong_ answer: steady high-volume compute, long-running jobs, and latency-critical paths.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[What is progressive delivery and how does it differ from traditional deployment strategies?]] (`#509`): [What is progressive delivery and how does it differ from traditional deployment strategies?](../core-devops-concepts/what-is-progressive-delivery-and-how-does-it-differ-from-traditional-deployment-strategies.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Serverless Architecture](./README.md) · [All topics](../README.md)
