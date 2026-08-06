---
title: "What is Function as a Service (FaaS)?"
id: 110
category: "Serverless Architecture"
difficulty: "Beginner"
tags:
  - devops
  - serverless-architecture
  - interview-questions
---

# What is Function as a Service (FaaS)?

**Short answer:** FaaS is the compute model at the heart of serverless: you deploy individual functions that the platform executes in response to events, scaling each independently and billing only for execution time.

## Detail

**How it differs from neighbouring models**

|                     | FaaS                | Serverless containers  | PaaS              | IaaS              |
| ------------------- | ------------------- | ---------------------- | ----------------- | ----------------- |
| Unit of deployment  | A function          | A container image      | An application    | A virtual machine |
| Scales to zero      | Yes                 | Usually                | Rarely            | No                |
| Billing granularity | Per ms of execution | Per request/CPU-second | Per instance-hour | Per instance-hour |
| Startup concern     | Cold start          | Cold start             | Warm              | Always on         |
| State               | Stateless           | Stateless              | Can be stateful   | Anything          |

**Implementations:** AWS Lambda, Azure Functions, Google Cloud Functions, Cloudflare Workers (V8 isolates, near-zero cold start), and self-hosted options such as Knative and OpenFaaS on Kubernetes.

**The programming model.** A function receives an event and a context, does one thing, and returns. It is stateless between invocations, subject to execution time and memory limits, and must tolerate being run concurrently many times over and being retried.

**Where FaaS fits best:** event processing (a file lands, a message arrives), scheduled jobs, webhook receivers, lightweight APIs with variable traffic, glue between managed services, and stream processing.

**Where it does not:** long-running computation, workloads needing persistent connections (though WebSocket support exists via gateways), consistently high throughput where reserved compute is cheaper, and applications with heavyweight runtimes where cold start dominates.

## Interview tips

- Position FaaS as a subset of serverless — serverless also covers databases, queues, and containers.
- Cloudflare Workers' isolate model is a good example of how cold starts are being engineered away.
- Knative or OpenFaaS is the answer if asked about FaaS without vendor lock-in.

---

[⬅ Back to Serverless Architecture](./README.md) · [All topics](../README.md)
