---
title: "What are Serverless Best Practices?"
id: 109
category: "Serverless Architecture"
difficulty: "Intermediate"
tags:
  - devops
  - serverless-architecture
  - interview-questions
---

# What are Serverless Best Practices?

**Short answer:** Keep functions small and single-purpose, make handlers idempotent, initialise expensive resources outside the handler, mind cold starts, apply least-privilege IAM per function, and instrument everything with structured logs and traces.

## Detail

**Function design**

- One function, one responsibility - easier to reason about, secure, and scale.
- Keep the deployment package small; large dependency trees lengthen cold starts.
- Initialise SDK clients, database connections, and configuration in the global scope so warm invocations reuse them.
- Make handlers **idempotent** - retries are guaranteed to happen eventually, so use an idempotency key and a conditional write.

**Performance**

- Tune memory: more memory means more CPU, often reducing both duration and total cost.
- Use provisioned concurrency for latency-critical paths, or accept cold starts elsewhere.
- Prefer lightweight runtimes and ahead-of-time compiled languages when startup latency is critical.
- Avoid function-calls-function chains; orchestrate with Step Functions or events instead.

**Reliability**

- Configure dead-letter queues or failure destinations for asynchronous invocations.
- Set reserved concurrency to protect downstream systems (a relational database will not survive 3,000 concurrent Lambdas).
- Handle partial batch failures explicitly when consuming from SQS or Kinesis.

**Security**

- One IAM role per function, scoped to exactly the resources it touches.
- Secrets from Secrets Manager or Parameter Store, cached in the execution environment, never in environment variables in plaintext.
- Validate all event input; events from a queue are still untrusted data.

**Operations**

- Structured JSON logs with a correlation ID, distributed tracing, and alarms on errors, throttles, and duration percentiles.
- Deploy with IaC (SAM, CDK, Serverless Framework, Terraform) and use aliases with weighted routing for canary releases.

## Interview tips

- Connection limits to relational databases is the classic serverless failure - mention reserved concurrency or RDS Proxy.
- Idempotency is non-negotiable and interviewers listen for it.
- Global-scope initialisation is the single easiest performance win; it is a good concrete detail.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Serverless Architecture](./README.md) · [All topics](../README.md)
