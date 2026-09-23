---
title: "How Do You Set SLIs and SLOs for Event-Driven and Streaming Architectures?"
id: 723
category: "SLO Engineering"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - slo-engineering
  - streaming
  - event-driven
  - kafka
quiz:
  stem: "Why are synthetic canary events frequently injected into streaming and event-driven data pipelines for SLI monitoring?"
  options:
    - "To clean up old data records from disk partitions."
    - "To measure end-to-end delivery freshness and detect pipeline stalls even when genuine user event volume is low or intermittent."
    - "To force Kafka consumer groups to rebalance every minute."
    - "To bypass TLS encryption checks across internal broker clusters."
  answer: 2
  explanation: "If user traffic drops, passive metrics might show zero errors despite a broken or deadlocked pipeline. Synthetic canary events ensure continuous, proactive measurement of end-to-end propagation latency regardless of user volume."
---

# How Do You Set SLIs and SLOs for Event-Driven and Streaming Architectures?

**Short answer:** Event-driven and streaming SLIs measure data freshness (end-to-end event delivery latency), consumer processing lag, message loss/durability (completeness), and pipeline throughput, using time-windowed quantiles rather than simple HTTP status code checks.

## Detail

### Challenges of Measuring Streaming Systems

Unlike synchronous request-response APIs, streaming and event-driven architectures (Apache Kafka, Apache Flink, AWS Kinesis, RabbitMQ) process continuous, unbounded streams of records. Users do not wait for immediate HTTP status codes; instead, downstream consumers rely on event order, completeness, and low end-to-end propagation lag.

### Key SLI Dimensions for Streaming

1. **Freshness / End-to-End Latency SLI**:
   - The time elapsed between when an event is initially generated at the producer and when it is successfully processed and emitted by the stream processor.
   - SLI: $99\%$ of processed events have an end-to-end latency $\le 2.0\text{ seconds}$.
2. **Consumer Lag SLI (Backlog Delay)**:
   - Measures the difference between the latest offset written to the topic partition and the committed offset of the consumer group.
   - Expressed in time: $\text{Lag Time} = \text{Current Time} - \text{Timestamp of Oldest Uncommitted Event}$.
   - SLI: Consumer lag time $\le 30\text{ seconds}$ across $99.9\%$ of 1-minute windows.
3. **Data Completeness & Loss SLI**:
   - Verifies that zero messages are dropped or corrupted during transit or dead-letter routing.
   - SLI: $\frac{\text{Events Successfully Ingested}}{\text{Events Produced}} \ge 99.99\%$ per day (a 100% target leaves no budget and cannot be measured reliably anyway).
4. **Throughput / Processing Continuity SLI**:
   - Detects stalled stream topologies where consumer processes are alive but deadlocked or in crash loops.
   - SLI: Stream processor produces output records at $\ge 95\%$ of expected historical baseline for each 5-minute window.

```text
[Producer: Event Created (T0)]
            │
            ▼
[Kafka Topic Partition] (Records Offset N)
            │
            ▼
[Flink / Kafka Streams Worker (T1)]
            │
  Processing Latency = T1 - T0
  Consumer Lag = Current Wall Clock - Event Timestamp
```

### Implementing SLI Probers

Because passive consumer telemetry may be silent during low-volume periods, engineering teams deploy **synthetic heartbeat events** (canary records) published once every 10 seconds. The prober measures the exact transit time through all stream stages to evaluate pipeline health continuously.

### Real-World Production Scenario

A financial fraud detection engine consumes a Kafka topic handling 50,000 credit card authorizations per second. During a network rebalance, consumer lag spikes. An SLI tracks the 99th percentile end-to-end latency of authorization events. Because the threshold of 500ms is breached for more than 2 minutes, an alert triggers autoscaling of the consumer group before transactions begin timing out at retail points of sale.

## Example

```python
# Synthetic heartbeat producer: one canary event every 10 s carrying its creation time.
# The pipeline's sink records now - created_at for records with canary=true as the freshness SLI.
import json, time
from confluent_kafka import Producer

p = Producer({"bootstrap.servers": "kafka:9092", "acks": "all", "enable.idempotence": True})
while True:
    p.produce("card-authorizations", key="canary",
              value=json.dumps({"canary": True, "created_at": time.time()}))
    p.poll(0)
    time.sleep(10)
```

```promql
# Freshness SLO: fraction of 1-minute windows where canary end-to-end latency stayed under 2 s
avg_over_time((max(pipeline_canary_e2e_latency_seconds) < bool 2)[28d:1m])
```

## Interview tips

- Explain consumer lag in terms of time rather than just raw offset count, as offset count significance varies based on message size and processing complexity.
- Mention synthetic canary events as a vital tool for verifying streaming pipeline health during off-peak periods.
- Discuss how watermark delays and out-of-order event handling in Apache Flink impact latency calculations.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What is progressive delivery and how does it differ from traditional deployment strategies?]] (`#509`): [What is progressive delivery and how does it differ from traditional deployment strategies?](../core-devops-concepts/what-is-progressive-delivery-and-how-does-it-differ-from-traditional-deployment-strategies.md)
- [[What is Shift-Left and how is it practically implemented across the SDLC?]] (`#510`): [What is Shift-Left and how is it practically implemented across the SDLC?](../core-devops-concepts/what-is-shift-left-and-how-is-it-practically-implemented-across-the-sdlc.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SLO Engineering](./README.md) · [All topics](../README.md)
