---
title: "What is the difference between Orchestration and Choreography in microservice event-driven architectures?"
id: 603
category: "Cloud Native Architecture"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - microservices
  - event-driven
  - orchestration
  - choreography
  - saga
quiz:
  stem: "Which business scenario is better suited to centralized Orchestration (e.g. AWS Step Functions) rather than decentralized Choreography?"
  options:
    - "Sending real-time telemetry metrics to five independent dashboards"
    - "A multi-step financial checkout transaction requiring strict compensation rollbacks (Saga) if any intermediate step fails"
    - "Broadcasting weather updates to millions of mobile phones"
    - "Stateless image thumbnail generation"
  answer: 2
  explanation: "Multi-step transactional workflows with compensation logic (like payment and inventory sagas) benefit heavily from orchestration, where the central state machine can coordinate rollbacks reliably."
---

# What is the difference between Orchestration and Choreography in microservice event-driven architectures?

**Short answer:** In **orchestration**, one component - a workflow engine such as Temporal, AWS Step Functions, or Camunda - owns the process: it calls or commands each service in turn, records durable state, and handles timeouts, retries, and compensations. In **choreography**, there is no conductor: each service reacts to events on a broker (`OrderPlaced` → payments charges → `PaymentCaptured` → shipping dispatches) and emits its own. Orchestration makes the flow explicit and observable at the cost of a central dependency; choreography maximises decoupling at the cost of a flow that exists only implicitly across many services.

## Detail

**Choreography**

- Producers publish facts; consumers decide what to do. Adding a new reaction (analytics, loyalty points) needs no change to existing services.
- Works well for short flows and fan-out notifications.
- Problems grow with length: nobody owns the end-to-end process, "where is order 1042 stuck?" needs distributed tracing across services, compensation logic is spread everywhere, and cyclic dependencies between events can appear. Event contracts become the coupling.

**Orchestration**

- The workflow definition is the single place that shows the process, its state per instance, and its failure handling.
- Durable execution engines persist every step, so a crash mid-flow resumes where it left off; long waits (hours or days for a human approval) are cheap.
- Costs: the orchestrator is a critical dependency to run (or buy) and scale; services can become passive "task executors" if the orchestrator absorbs business logic that belongs in them; and the workflow team can become a bottleneck.

**Comparison**

| Concern            | Orchestration                                                                | Choreography                                         |
| ------------------ | ---------------------------------------------------------------------------- | ---------------------------------------------------- |
| Process visibility | Explicit, per-instance state                                                 | Implicit; reconstructed from traces and events       |
| Coupling           | Orchestrator knows every participant                                         | Participants know only event contracts               |
| Failure handling   | Central retries, timeouts, compensation                                      | Each service handles its own; harder to reason about |
| Adding a step      | Change the workflow                                                          | Add a subscriber                                     |
| Best for           | Multi-step transactions, sagas, long-running and human-in-the-loop processes | Notifications, fan-out, simple reactive flows        |

**Mixing them is normal.** A common shape is orchestration inside a bounded context (the checkout saga) and choreography between contexts (checkout publishes `OrderCompleted`, which other domains react to).

## Example

```json
{
  "Comment": "Orchestrated checkout saga (AWS Step Functions, JSONata query language)",
  "QueryLanguage": "JSONata",
  "StartAt": "ReserveInventory",
  "States": {
    "ReserveInventory": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Arguments": { "FunctionName": "reserve-inventory", "Payload": "{% $states.input %}" },
      "Output": "{% $states.input %}",
      "Retry": [{ "ErrorEquals": ["States.TaskFailed"], "MaxAttempts": 3, "BackoffRate": 2 }],
      "Next": "ChargePayment"
    },
    "ChargePayment": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Arguments": { "FunctionName": "charge-payment", "Payload": "{% $states.input %}" },
      "Output": "{% $states.input %}",
      "Catch": [{ "ErrorEquals": ["States.ALL"], "Output": "{% $states.input %}", "Next": "ReleaseInventory" }],
      "Next": "PublishOrderCompleted"
    },
    "ReleaseInventory": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Arguments": { "FunctionName": "release-inventory", "Payload": "{% $states.input %}" },
      "Next": "Failed"
    },
    "PublishOrderCompleted": {
      "Type": "Task",
      "Comment": "Hand-off to choreography: other domains react to this event",
      "Resource": "arn:aws:states:::events:putEvents",
      "Arguments": {
        "Entries": [{ "Source": "shop.checkout", "DetailType": "OrderCompleted", "Detail": "{% $states.input %}" }]
      },
      "End": true
    },
    "Failed": { "Type": "Fail", "Error": "CheckoutFailed" }
  }
}
```

## Interview tips

- Define both by who owns the process: a conductor with durable state, or services reacting to events.
- Give the trade-off honestly: visibility and central failure handling versus decoupling and easy extension.
- Recommend orchestration for sagas and long-running flows, choreography for fan-out, and a mix across bounded contexts.
- Mention that choreographed systems need strong tracing and event-contract governance to stay debuggable.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between a declarative and a scripted Jenkins pipeline?]] (`#454`): [What is the difference between a declarative and a scripted Jenkins pipeline?](../cicd/what-is-the-difference-between-a-declarative-and-a-scripted-jenkins-pipeline.md)
- [[What is the difference between Docker Image and Docker Container?]] (`#7`): [What is the difference between Docker Image and Docker Container?](../docker/what-is-the-difference-between-docker-image-and-docker-container.md)
- [[What is the difference between a bind mount and a volume in Docker?]] (`#440`): [What is the difference between a bind mount and a volume in Docker?](../docker/what-is-the-difference-between-a-bind-mount-and-a-volume-in-docker.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Native Architecture](./README.md) · [All topics](../README.md)
