---
title: "What are Event-Driven architectures with EventBridge, SQS, and SNS and how do they decouple serverless systems?"
id: 659
category: "Serverless Architecture"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - serverless
  - eventbridge
  - sqs
  - sns
  - event-driven
quiz:
  stem: "Which AWS service is best suited for routing events based on complex JSON payload attributes (e.g. `department == 'finance' AND amount > 10000`) across SaaS applications and microservices?"
  options:
    - "Amazon SQS Standard"
    - "Amazon EventBridge"
    - "Amazon DynamoDB Streams"
    - "AWS Direct Connect"
  answer: 2
  explanation: "Amazon EventBridge is an enterprise event bus featuring advanced JSON content-based filtering rules, schema registries, and native integrations with third-party SaaS providers."
---

# What are Event-Driven architectures with EventBridge, SQS, and SNS and how do they decouple serverless systems?

**Short answer:** They are three different AWS primitives. **SQS** is a durable queue: messages wait until a consumer processes and deletes them, which buffers load and isolates a slow or failed consumer. **SNS** is push-based pub/sub: one publish fans out to many subscribers (SQS queues, Lambda, HTTP endpoints, email/SMS), with attribute- or payload-based filtering. **EventBridge** is an event bus with rich content-based rules, many AWS and SaaS event sources, schema discovery, archive and replay, and scheduling. They decouple producers from consumers in time (the consumer can be down), in scale (the queue absorbs spikes), and in knowledge (the producer does not know who listens) - at the price of eventual consistency and at-least-once delivery that every consumer must handle.

## Detail

| Feature      | Amazon SQS                                                         | Amazon SNS                                                 | Amazon EventBridge                                                        |
| ------------ | ------------------------------------------------------------------ | ---------------------------------------------------------- | ------------------------------------------------------------------------- |
| Model        | Queue: one consumer group competes for each message                | Topic: pushes a copy to every subscriber                   | Bus: rules match events and send them to targets                          |
| Delivery     | Consumers poll (Lambda polls for you via an event source mapping)  | Push, with retries per protocol                            | Push to up to five targets per rule, with retries and DLQs                |
| Retention    | Up to 14 days until processed                                      | None: a message goes to current subscribers or is lost     | None by default; optional archive for replay                              |
| Filtering    | None on the queue (Lambda event source mapping filters exist)      | Subscription filter policies on attributes or message body | Event patterns on any field: prefix, numeric ranges, exists, anything-but |
| Ordering     | Standard: best-effort; FIFO: ordered per message group             | Standard, or FIFO topics feeding FIFO queues               | No ordering guarantee                                                     |
| Throughput   | Very high (standard); FIFO lower, higher with high-throughput mode | Very high                                                  | High, but quota-bound per account and region                              |
| Typical role | Buffer and work queue in front of a consumer                       | Fast fan-out of the same message to many consumers         | Routing domain events between services, accounts, and SaaS                |

**Patterns that combine them**

- **Fan-out with isolation (SNS → SQS per consumer).** Billing, shipping, and analytics each get their own queue; if billing is down, its messages wait while the others proceed. Each queue has its own DLQ and retry policy.
- **Event bus between domains (EventBridge).** Services publish domain events (`OrderPlaced`) to a bus; each consuming team owns a rule matching what it needs, targeting its own queue or function. Cross-account buses support multi-account estates.
- **Queue in front of a constrained resource.** SQS with a capped consumer concurrency protects a database or third-party API from bursts.
- **Pipes.** EventBridge Pipes connect a source (SQS, Kinesis, DynamoDB Streams) to a target with filtering and enrichment, replacing glue Lambdas.

**What every consumer must handle:** duplicates (idempotency keys), out-of-order arrival (except FIFO), poison messages (DLQs with alarms and a redrive process), and schema evolution (versioned events; EventBridge schema registry can generate bindings). Trace context must be propagated in message attributes, or traces break at every hop.

## Example

```yaml
# SAM: EventBridge rule routes large finance orders to a dedicated queue and consumer
Resources:
  LargeOrderRule:
    Type: AWS::Events::Rule
    Properties:
      EventBusName: orders-bus
      EventPattern:
        source: [shop.orders]
        detail-type: [OrderPlaced]
        detail:
          department: [finance]
          amount: [{ numeric: [">", 10000] }]
      Targets:
        - Id: large-orders-queue
          Arn: !GetAtt LargeOrdersQueue.Arn
  LargeOrdersQueue:
    Type: AWS::SQS::Queue
    Properties:
      VisibilityTimeout: 180
      RedrivePolicy: { deadLetterTargetArn: !GetAtt LargeOrdersDLQ.Arn, maxReceiveCount: 5 }
  LargeOrdersDLQ:
    Type: AWS::SQS::Queue
  LargeOrdersQueuePolicy: # allow the rule to send to the queue
    Type: AWS::SQS::QueuePolicy
    Properties:
      Queues: [!Ref LargeOrdersQueue]
      PolicyDocument:
        Statement:
          - Effect: Allow
            Principal: { Service: events.amazonaws.com }
            Action: sqs:SendMessage
            Resource: !GetAtt LargeOrdersQueue.Arn
            Condition: { ArnEquals: { aws:SourceArn: !GetAtt LargeOrderRule.Arn } }
  ReviewFunction:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: python3.13
      Handler: review.handler
      Events:
        Queue:
          Type: SQS
          Properties:
            Queue: !GetAtt LargeOrdersQueue.Arn
            ScalingConfig: { MaximumConcurrency: 5 } # protect the downstream system
            FunctionResponseTypes: [ReportBatchItemFailures]
```

## Interview tips

- Classify them first: queue (SQS), push fan-out (SNS), content-routed bus (EventBridge).
- Describe SNS-to-SQS fan-out and say why a queue per consumer isolates failures.
- Correct a common mistake: SNS filter policies can match the message body, not only attributes.
- Name what decoupling costs - duplicates, ordering, poison messages, schema evolution - and the controls for each.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[How do you use Jenkins shared libraries?]] (`#268`): [How do you use Jenkins shared libraries?](../cicd/how-do-you-use-jenkins-shared-libraries.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Serverless Architecture](./README.md) · [All topics](../README.md)
