---
title: "How do you monitor and debug a serverless application?"
id: 423
category: "Serverless Architecture"
difficulty: "Intermediate"
tags:
  - devops
  - serverless-architecture
  - interview-questions
  - monitoring-and-logging
  - aws-engineering
  - infrastructure-monitoring
---

# How do you monitor and debug a serverless application?

**Short answer:** You cannot SSH into a function, so observability has to be designed in rather than added later. Instrument three layers: **the platform metrics** (invocations, errors, duration, throttles, concurrency, and - critically - dead-letter and destination failures), **structured JSON logs with a correlation ID** propagated across every hop, and **distributed tracing** (X-Ray, or OpenTelemetry to your own backend) because a serverless request is a chain of managed services rather than one process. Then alert on the things unique to this model: **throttles** (`Throttles > 0` means requests were rejected, not slow), **async retry exhaustion and DLQ depth** (silent data loss otherwise), **iterator age** for stream consumers, and **p99 duration approaching the configured timeout**. The recurring debugging traps are asynchronous invocations failing invisibly, cold starts distorting latency percentiles, and downstream connection limits.

## Detail

### The metrics that matter, and what each one really tells you

| Metric                            | Meaning                                                    | Alert on                                                          |
| --------------------------------- | ---------------------------------------------------------- | ----------------------------------------------------------------- |
| `Errors` / `Invocations`          | Handler raised or timed out                                | Error rate against an SLO, not an absolute count                  |
| `Throttles`                       | Rejected - concurrency limit or account quota hit          | Any sustained non-zero. This is capacity, not code                |
| `Duration` p50 / p99 / max        | Execution time excluding queue time                        | p99 within ~70% of the timeout, so you see it before it fails     |
| `ConcurrentExecutions`            | Simultaneous instances                                     | Approaching the reserved or account limit                         |
| `DeadLetterErrors` / DLQ depth    | Async events that failed every retry                       | Any message. This is silent data loss                             |
| `IteratorAge` (streams)           | How stale the record being processed is                    | Growing trend - the consumer is falling behind and will lose data |
| `ProvisionedConcurrencySpillover` | Traffic beyond warm capacity, so cold starts are happening | Non-zero when latency matters                                     |
| Init duration (from logs/traces)  | Cold-start cost                                            | Track separately; do not let it hide inside p99                   |

The two most valuable are **`Throttles`** and **DLQ depth**, precisely because neither looks like an error in the application's own logs.

### Logging: structured, correlated, and sampled

- **Emit JSON**, one object per event, with the request ID, a business correlation ID, the function name and version, and the cold-start flag. Text logs are useless at this volume because you can only find anything by querying fields.
- **Propagate a correlation ID across every hop** - API Gateway → function → queue message attribute → next function → database. Without it, a single user journey through six services cannot be reassembled. This is the single highest-value practice in serverless debugging.
- **Never log the payload blindly** - serverless makes it trivially easy to log PII and card data into an unbounded log store.
- **Control cost.** Log volume is a real line item: set retention (7-30 days for verbose logs, longer for audit), sample debug logs, and consider export to cheap storage for analysis. See [how do you design a logging pipeline that stays affordable at scale](../monitoring-and-logging/how-do-you-design-a-logging-pipeline-that-stays-affordable-at-scale.md).

### Tracing is not optional here

In a serverless architecture the "system" is API Gateway plus five functions plus a queue plus DynamoDB, and no single log stream shows the whole request. Enable X-Ray (or an OpenTelemetry-based collector) with **subsegments around every downstream call**, so a trace shows where the 900 ms actually went - and, importantly, shows the cold-start init segment separately. OpenTelemetry via a Lambda layer is the portable choice; the vendor tools (Datadog, New Relic, Lumigo) add serverless-specific views such as automatic dependency mapping and cold-start analysis. See [what is tracing in observability](../advanced-devops-cloud/what-is-tracing-in-observability.md).

### The failure modes that catch teams out

- **Asynchronous invocations fail silently.** An event-driven function (S3 event, EventBridge rule, SNS) retries a couple of times and then discards the event unless you configured a DLQ or an on-failure destination. Every async function needs one, plus an alarm on it. Most "we lost some events" incidents are this.
- **Stream consumers block on a poison record.** Kinesis and DynamoDB Streams retry the same batch until it succeeds or expires, so one bad record stalls the shard and `IteratorAge` climbs. Configure `BisectBatchOnFunctionError`, `MaximumRetryAttempts`, and a failure destination.
- **Throttling looks like an outage with no errors in the code.** Reserved concurrency limits one function; the account limit is shared, so a runaway batch function can throttle the customer-facing API. Reserve concurrency for critical paths deliberately.
- **Downstream connection exhaustion.** A function scaling to 1,000 concurrent instances opens 1,000 database connections. Use RDS Proxy or a data API, and keep clients initialised outside the handler so they are reused across warm invocations.
- **Cold starts distort everything.** Report cold and warm latency separately; use provisioned concurrency for user-facing paths where it matters, keep packages small, and avoid heavyweight initialisation.
- **Timeouts hide the real error.** A function killed at its timeout logs a truncated message with no stack. Set the timeout deliberately (not the default 3 s, not a lazy 15 min), and implement an internal deadline so the handler fails cleanly and logs context before the platform kills it.
- **Retries mean duplicates.** At-least-once delivery is the norm, so handlers must be idempotent - which is a design requirement, not an operational one. See [how do you design a serverless system for production](./how-do-you-design-a-serverless-system-for-production.md).

### Debugging locally and in production

Reproduce with the real event shape (SAM CLI `generate-event`, or a saved production event body) rather than a hand-written test object - most bugs are in the event parsing. Use short-lived debug logging switched by an environment variable or parameter, replay failed events from the DLQ after fixing the code, and lean on function versions and aliases so you can compare behaviour between two deployed versions rather than guessing.

## Example

```python
# Structured logging + correlation ID + clients outside the handler + a deadline
import json, logging, os, time, uuid, boto3

log = logging.getLogger()
log.setLevel(os.getenv("LOG_LEVEL", "INFO"))
ddb = boto3.resource("dynamodb")                 # reused across warm invocations
table = ddb.Table(os.environ["TABLE"])
COLD_START = True

def handler(event, context):
    global COLD_START
    cold, COLD_START = COLD_START, False
    # accept an upstream correlation id, or start one - then pass it on everywhere
    corr = (event.get("headers") or {}).get("x-correlation-id") or str(uuid.uuid4())
    ctx = {"correlation_id": corr, "request_id": context.aws_request_id,
           "function": context.function_name, "cold_start": cold}

    log.info(json.dumps({**ctx, "event": "start", "route": event.get("rawPath")}))
    try:
        # internal deadline: fail cleanly with context BEFORE the platform kills us
        deadline = time.time() + (context.get_remaining_time_in_millis() / 1000) - 1.0
        result = do_work(event, deadline, ctx)
        log.info(json.dumps({**ctx, "event": "ok", "items": len(result)}))
        return {"statusCode": 200,
                "headers": {"x-correlation-id": corr},      # propagate downstream
                "body": json.dumps(result)}
    except Exception as e:
        # log the failure with context - never rely on the truncated timeout message
        log.exception(json.dumps({**ctx, "event": "error", "error": type(e).__name__}))
        raise                                                # let it count as an Error
```

```yaml
# Every async function needs a failure destination and an alarm on it
Resources:
  ProcessOrder:
    Type: AWS::Serverless::Function
    Properties:
      Timeout: 20 # deliberate: not the 3s default, not a lazy 900
      MemorySize: 1024
      ReservedConcurrentExecutions: 50 # protects the database and other functions
      Tracing: Active # X-Ray on
      EventInvokeConfig:
        MaximumRetryAttempts: 2
        DestinationConfig:
          OnFailure: { Destination: !GetAtt FailedOrdersQueue.Arn } # or events vanish

  DlqNotEmptyAlarm: # the alarm that catches silent data loss
    Type: AWS::CloudWatch::Alarm
    Properties:
      Namespace: AWS/SQS
      MetricName: ApproximateNumberOfMessagesVisible
      Dimensions: [{ Name: QueueName, Value: !GetAtt FailedOrdersQueue.QueueName }]
      Statistic: Maximum
      Period: 60
      Threshold: 0
      ComparisonOperator: GreaterThanThreshold
      EvaluationPeriods: 1
```

```text
CloudWatch Logs Insights - the query you actually run during an incident
  fields @timestamp, correlation_id, function, cold_start, error
  | filter correlation_id = "9f2c8b1d-..."        # one user journey, all functions
  | sort @timestamp asc

  # and the one that finds the real latency story
  filter @type = "REPORT"
  | stats count(*), pct(@duration, 50), pct(@duration, 99), max(@duration),
          count(@initDuration) as cold_starts by bin(5m)
```

## Interview tips

- Open with the constraint: no host to log into, so observability is a design decision. Then name the three layers - platform metrics, structured logs, traces.
- `Throttles` is the metric that separates people who have run serverless from people who have read about it. Explain that throttled requests are rejected, and that account-level concurrency is shared so one function can starve another.
- Asynchronous invocations failing silently into nothing is the best war story here. Say that every async function needs a DLQ or on-failure destination **and an alarm on it**, because otherwise the failure mode is data loss with a green dashboard.
- Correlation IDs propagated through queues and events - state it explicitly, because it is the thing that makes multi-function debugging possible at all.
- Mention `IteratorAge` and poison-pill handling for stream consumers (`BisectBatchOnFunctionError`), which is a level of detail interviewers rarely hear.
- Report cold and warm latency separately, and give provisioned concurrency as the fix _when latency matters_ rather than as a default.
- Bring up the downstream connection-limit problem (1,000 concurrent functions, 1,000 database connections) and RDS Proxy plus clients initialised outside the handler.
- Close on cost: log retention and sampling, because serverless observability bills can exceed the compute bill and that is a real engineering decision.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Serverless Architecture](./README.md) · [All topics](../README.md)
