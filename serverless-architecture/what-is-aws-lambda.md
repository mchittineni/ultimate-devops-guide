---
title: "What is AWS Lambda?"
id: 107
category: "Serverless Architecture"
difficulty: "Beginner"
tags:
  - devops
  - serverless-architecture
  - interview-questions
---

# What is AWS Lambda?

**Short answer:** AWS Lambda is Amazon's function-as-a-service platform. You upload code as a zip or container image, configure memory and a trigger, and AWS runs it on demand - scaling automatically and billing per millisecond of execution.

## Detail

**Execution model.** An event invokes a handler function. Lambda provisions an execution environment (a Firecracker microVM), runs the initialisation code, then the handler. The environment is reused for subsequent invocations while warm, which is why global-scope initialisation - database clients, SDK objects - should sit outside the handler.

**Configuration that matters**

- **Memory** (128 MB to 10 GB) also determines CPU allocation proportionally. Increasing memory often _reduces_ cost by finishing faster - worth measuring with a tuning tool.
- **Timeout** - up to 15 minutes.
- **Concurrency** - reserved concurrency guarantees capacity and caps blast radius; provisioned concurrency keeps environments warm to eliminate cold starts.
- **Layers** for shared dependencies, and container images up to 10 GB for large runtimes.
- **VPC attachment** for private resources (now with much-improved cold-start behaviour via Hyperplane ENIs).

**Common triggers:** API Gateway or Function URLs (HTTP), SQS and Kinesis (streams), S3 events, EventBridge (schedules and events), DynamoDB Streams, and Step Functions.

**Operational practices:** structured JSON logging to CloudWatch, tracing with X-Ray or OpenTelemetry, a dead-letter queue or on-failure destination for failed asynchronous invocations, idempotent handlers (retries happen), and least-privilege IAM per function.

## Example

```python
import json, os, boto3

# Initialised once per execution environment, reused across invocations
table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])

def handler(event, context):
    for record in event["Records"]:                 # SQS batch
        body = json.loads(record["body"])
        table.put_item(Item={"id": body["id"], "payload": body})  # idempotent write
    return {"statusCode": 200}
```

## Interview tips

- Initialising clients outside the handler is the most common practical optimisation - mention it.
- Memory tuning affecting CPU (and therefore cost) surprises people; it is a strong detail.
- Idempotency, DLQs, and retry behaviour show you have run Lambda in production, not just deployed a demo.

---

[⬅ Back to Serverless Architecture](./README.md) · [All topics](../README.md)
