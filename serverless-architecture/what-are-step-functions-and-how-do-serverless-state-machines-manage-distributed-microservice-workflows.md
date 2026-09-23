---
title: "What are Step Functions and how do serverless state machines manage distributed microservice workflows?"
id: 658
category: "Serverless Architecture"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - serverless
  - step-functions
  - workflows
  - aws
  - orchestration
quiz:
  stem: "Which AWS Step Functions workflow type is designed for processing high-volume event streams (like IoT telemetry) running for under 5 minutes with at-least-once execution?"
  options:
    - "Standard Workflows"
    - "Express Workflows"
    - "Batch Workflows"
    - "Singleton Workflows"
  answer: 2
  explanation: "Express Workflows are built for high-throughput, short-duration event processing workloads up to 5 minutes, offering significant cost savings over Standard Workflows."
---

# What are Step Functions and how do serverless state machines manage distributed microservice workflows?

**Short answer:** AWS Step Functions is a managed workflow orchestrator. You describe a process as a state machine in Amazon States Language (JSON or YAML) - tasks, choices, parallel branches, maps, waits - and the service runs each execution, persisting its state between steps and applying declarative **retries**, **catches**, and **timeouts**. Tasks can call Lambda, ECS, or more than 200 AWS services directly through SDK integrations, often with no Lambda at all. **Standard** workflows run for up to a year with exactly-once step execution and full history; **Express** workflows run for up to five minutes at high volume and lower cost with at-least-once (asynchronous) semantics. The trade-off is lock-in to ASL and per-transition pricing that punishes chatty, fine-grained steps.

## Detail

**Why not chain Lambdas.** When function A invokes B which invokes C, A pays for waiting, timeouts nest, retries multiply, and nobody can see where an order is stuck. A state machine makes the flow explicit, stores state durably, and handles failure declaratively.

**Building blocks**

- **Task** - do work: invoke Lambda, run an ECS task, call DynamoDB/SQS/SNS/EventBridge/Bedrock via service or SDK integrations. `.sync` waits for a job to finish; `.waitForTaskToken` pauses until an external system (or a human approval) calls back.
- **Choice, Parallel, Map** - branching, concurrent branches, and iteration. **Distributed Map** fans out to up to 10,000 parallel child executions over items in S3 - large-scale batch processing without a cluster.
- **Wait** - pause for a duration or until a timestamp, free while waiting in Standard workflows.
- **Retry / Catch** - per-state retry policies (`IntervalSeconds`, `MaxAttempts`, `BackoffRate`, `MaxDelaySeconds`, `JitterStrategy`) and catchers that route errors to compensation or notification states - the natural way to implement a saga.
- **Data handling** - JSONata (`QueryLanguage: JSONata`, added in 2024) and workflow variables simplify passing and transforming data; the older JSONPath fields (`InputPath`, `ResultPath`, `Parameters`) remain supported.

**Standard versus Express**

| Aspect       | Standard                                            | Express                                                   |
| ------------ | --------------------------------------------------- | --------------------------------------------------------- |
| Max duration | 1 year                                              | 5 minutes                                                 |
| Semantics    | Exactly-once step execution                         | At-least-once (async) or at-most-once (sync)              |
| Pricing      | Per state transition                                | Per request and duration/memory                           |
| History      | Full execution history in the console/API           | Sent to CloudWatch Logs                                   |
| Suits        | Order processing, sagas, human approvals, long jobs | High-volume event processing, IoT ingestion, API backends |

**Trade-offs:** state transitions cost money in Standard workflows (design coarser steps), state input and output are capped at 256 KiB (a hard quota - unlike Lambda async, SQS and EventBridge, which moved to 1 MB in 2025-26 - so pass S3 references for anything large), ASL definitions can become large and hard to test (use the TestState API and local testing tools), and the workflow logic is AWS-specific. Code-first durable-execution alternatives include Temporal and, within Lambda, Lambda durable functions.

## Example

```json
{
  "Comment": "Order workflow: retry transient failures with jitter, compensate on payment failure",
  "StartAt": "ReserveStock",
  "States": {
    "ReserveStock": {
      "Type": "Task",
      "Resource": "arn:aws:states:::dynamodb:updateItem",
      "Parameters": {
        "TableName": "inventory",
        "Key": { "sku": { "S.$": "$.sku" } },
        "UpdateExpression": "SET reserved = reserved + :q",
        "ConditionExpression": "stock - reserved >= :q",
        "ExpressionAttributeValues": { ":q": { "N.$": "States.Format('{}', $.qty)" } }
      },
      "ResultPath": null,
      "Next": "ChargePayment"
    },
    "ChargePayment": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": { "FunctionName": "charge-payment", "Payload.$": "$" },
      "ResultPath": "$.payment",
      "Retry": [
        {
          "ErrorEquals": ["Lambda.TooManyRequestsException", "States.Timeout"],
          "IntervalSeconds": 2,
          "MaxAttempts": 3,
          "BackoffRate": 2.0,
          "JitterStrategy": "FULL"
        }
      ],
      "Catch": [{ "ErrorEquals": ["States.ALL"], "ResultPath": "$.error", "Next": "ReleaseStock" }],
      "End": true
    },
    "ReleaseStock": {
      "Type": "Task",
      "Resource": "arn:aws:states:::dynamodb:updateItem",
      "Parameters": {
        "TableName": "inventory",
        "Key": { "sku": { "S.$": "$.sku" } },
        "UpdateExpression": "SET reserved = reserved - :q",
        "ExpressionAttributeValues": { ":q": { "N.$": "States.Format('{}', $.qty)" } }
      },
      "Next": "OrderFailed"
    },
    "OrderFailed": { "Type": "Fail", "Error": "PaymentFailed" }
  }
}
```

## Interview tips

- Explain the problem it solves - brittle Lambda-to-Lambda chains with no durable state or visibility - before listing features.
- Know Standard versus Express precisely: duration, execution semantics, pricing, and where history lives.
- Mention direct service integrations (no "glue" Lambda), `.waitForTaskToken` for human or external steps, and Distributed Map for large fan-out.
- Show you know the costs: per-transition pricing, the payload-size quota, and ASL lock-in.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does OpenID Connect (OIDC) eliminate long-lived cloud credentials in CI/CD pipelines?]] (`#533`): [How does OpenID Connect (OIDC) eliminate long-lived cloud credentials in CI/CD pipelines?](../cicd/how-does-openid-connect-oidc-eliminate-long-lived-cloud-credentials-in-ci-cd-pipelines.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[How do you take a monthly release process to daily deployments?]] (`#285`): [How do you take a monthly release process to daily deployments?](../core-devops-concepts/how-do-you-take-a-monthly-release-process-to-daily-deployments.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Serverless Architecture](./README.md) · [All topics](../README.md)
