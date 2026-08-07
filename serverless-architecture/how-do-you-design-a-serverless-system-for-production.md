---
title: "How do you design a serverless system for production?"
id: 303
category: "Serverless Architecture"
difficulty: "Advanced"
tags:
  - devops
  - serverless-architecture
  - interview-questions
---

# How do you design a serverless system for production?

**Short answer:** Design for the four things that separate a demo from production: **idempotency** (every event source retries and may deliver twice, so every handler must tolerate duplicates), **concurrency and downstream limits** (a Lambda scaling to 1,000 will exhaust a database's connections long before it exhausts itself), **failure handling** (dead-letter queues, retry policy, and partial batch failure), and **cold-start latency** where it is user-facing (provisioned concurrency, smaller packages, or a different compute model). Add per-function least-privilege IAM, distributed tracing, and a per-function cost model, and the architecture holds.

## Detail

**Idempotency is not optional.** Event sources deliver at-least-once: SQS can deliver a message twice, an API client retries, an EventBridge rule can fire twice, and a failed batch is reprocessed. So every handler needs an idempotency key derived from the event (message ID, order ID, or a hash of the payload) and a store to record what has already been processed - conditional writes to DynamoDB with a TTL are the standard pattern. Charging a card twice because a retry was invisible is the canonical serverless production incident.

**Concurrency is the real capacity limit, and it points downstream.** Functions scale horizontally and fast, which means they transmit the traffic spike to whatever is behind them. A function opening one database connection per invocation, scaled to 1,000 concurrent executions, needs 1,000 connections - and RDS will refuse long before that. The controls:

- **Reserved concurrency** as a hard cap per function, so one function cannot consume the account's whole concurrency pool and starve the others.
- **A connection proxy** (RDS Proxy, PgBouncer) so pooled connections are shared rather than per-execution, or a serverless-native data store (DynamoDB, Aurora Serverless with the Data API) that scales with the same shape as the compute.
- **A queue as a shock absorber** between the spiky source and the constrained consumer, with the consumer's concurrency capped to what the downstream can absorb. This is the single most important structural pattern in serverless design.
- **Initialise clients outside the handler** so connections and SDK clients are reused across warm invocations rather than created per request.

**Failure handling, event source by event source.** Retry semantics differ and you must know which you are using: synchronous invocations (API Gateway) do not retry - the client must; asynchronous invocations retry twice with backoff then send to a **dead-letter queue** or on-failure destination; stream sources (Kinesis, DynamoDB Streams) retry the _whole batch_ and will block the shard until the poison record expires unless you configure `BisectBatchOnFunctionError`, `MaximumRetryAttempts`, and an on-failure destination. For SQS batches, implement **partial batch failure** (`ReportBatchItemFailures`) so one bad message does not force reprocessing of the other nine. And build the DLQ redrive path before you need it - a DLQ nobody monitors is just a place data goes to die, so alert on its depth.

**Cold starts, in proportion.** A cold start is the runtime initialisation plus your init code, typically tens to a few hundred milliseconds for interpreted runtimes and much worse for a heavy JVM or a large dependency tree - and it is worst of all for a function inside a VPC with lots of ENI churn (largely mitigated by modern VPC networking, but still a factor). Mitigations in order of preference: shrink the deployment package and lazy-load what the request path does not need; move initialisation out of the handler; use provisioned concurrency or SnapStart for the user-facing tier only; and if the traffic is steady and latency-critical, question whether serverless is the right model at all - a container service may be cheaper and faster. Do not use scheduled "warmer" pings; they are a workaround that does not survive real concurrency.

**Boundaries and limits to design against.** Function timeout (15 minutes on Lambda) and payload size limits mean long or large work needs Step Functions, a queue, or S3 as the transfer medium instead of the event body. Account-level concurrency is a shared quota - request increases before launch, not during. Statelessness means no local disk assumptions beyond `/tmp`, and no in-memory session state.

**Operability, which is where serverless is genuinely harder.** One IAM role per function with only the permissions that function needs (the fine-grained-by-default advantage - do not throw it away with a shared wildcard role). Distributed tracing (X-Ray or OpenTelemetry) is essential because the "stack trace" is now spread across a dozen managed services. Structured JSON logs with a correlation ID propagated through every hop. Alert on the serverless-specific signals: throttles, error rate, DLQ depth, iterator age for streams, and duration approaching the timeout. And keep a per-function cost model - serverless bills per invocation and per GB-second, so a hot function in a loop or an accidental recursive S3 trigger becomes a financial incident within hours. Set a billing alarm and never let a function write to the bucket that triggers it.

## Example

```python
# Idempotency + partial batch failure: the two things every SQS consumer needs.
import json, os, boto3
from botocore.exceptions import ClientError

ddb = boto3.resource("dynamodb")                       # created once, reused when warm
seen = ddb.Table(os.environ["IDEMPOTENCY_TABLE"])

def handler(event, context):
    failures = []
    for record in event["Records"]:
        try:
            body = json.loads(record["body"])
            key = body["order_id"]                      # business key, not the message id
            try:
                seen.put_item(
                    Item={"pk": key, "ttl": int(context.get_remaining_time_in_millis()/1000) + 86400},
                    ConditionExpression="attribute_not_exists(pk)",
                )
            except ClientError as exc:
                if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
                    continue                            # already processed - skip, do not fail
                raise
            process(body)
        except Exception:
            failures.append({"itemIdentifier": record["messageId"]})   # only this one retries
    return {"batchItemFailures": failures}
```

```yaml
# SAM/CloudFormation: the production settings, not the tutorial ones.
Resources:
  OrderProcessor:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: python3.13
      MemorySize: 512 # tune: more memory = more CPU = often cheaper per invocation
      Timeout: 30
      ReservedConcurrentExecutions: 50 # cap: protects the database AND other functions
      Tracing: Active # X-Ray
      Policies: # one narrow role per function
        - DynamoDBCrudPolicy: { TableName: !Ref IdempotencyTable }
        - SQSPollerPolicy: { QueueName: !GetAtt OrderQueue.QueueName }
      Events:
        Orders:
          Type: SQS
          Properties:
            Queue: !GetAtt OrderQueue.Arn
            BatchSize: 10
            MaximumBatchingWindowInSeconds: 5
            FunctionResponseTypes: [ReportBatchItemFailures] # partial batch failure
  OrderQueue:
    Type: AWS::SQS::Queue
    Properties:
      VisibilityTimeout: 180 # >= 6x function timeout
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt OrderDLQ.Arn
        maxReceiveCount: 3 # then the DLQ, which is monitored
```

```yaml
# Alerts that are specific to this model.
- AlarmName: LambdaThrottles
  MetricName: Throttles # you hit a concurrency ceiling
  Threshold: 1
- AlarmName: DLQNotEmpty
  MetricName: ApproximateNumberOfMessagesVisible # data is stuck - always alert
  Threshold: 1
- AlarmName: IteratorAgeHigh
  MetricName: IteratorAge # stream consumer falling behind / poison record
  Threshold: 60000
- AlarmName: DurationNearTimeout
  MetricName: Duration
  ExtendedStatistic: p99
  Threshold: 24000 # 80% of a 30s timeout
```

## Interview tips

- Lead with idempotency and say "every event source is at-least-once". The double-charge scenario makes it concrete immediately.
- The concurrency-exhausts-the-database point is the highest-value architectural insight here. Give the arithmetic: 1,000 concurrent executions × 1 connection each.
- Name reserved concurrency as protecting both the downstream _and_ the other functions sharing the account quota.
- Know the retry semantics per source - sync does not retry, async retries twice then DLQs, streams retry the whole batch and block the shard. Interviewers probe this precisely.
- Mention `ReportBatchItemFailures` for partial batch failure. Few candidates do, and it is a real production detail.
- Be measured about cold starts: mitigate on the user-facing path, and be willing to say a container service is the better choice for steady latency-critical traffic.
- Close on cost and blast radius - per-invocation billing, billing alarms, and never letting a function write to the bucket that triggers it. The recursive-trigger story is a well-known failure.

---

[⬅ Back to Serverless Architecture](./README.md) · [All topics](../README.md)
