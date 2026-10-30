---
title: "How do AWS Lambda, Google Cloud Run, and Azure Functions compare for serverless workloads?"
id: 776
category: "Serverless Architecture"
difficulty: "Intermediate"
tags:
  - devops
  - serverless-architecture
  - interview-questions
  - aws-lambda
  - cloud-run
  - azure-functions
---

# How do AWS Lambda, Google Cloud Run, and Azure Functions compare for serverless workloads?

**Short answer:** All three scale to zero and bill for usage. They differ in the **unit you deploy** and the **concurrency model**. **Lambda** runs functions (zip or container image) with one request per execution environment, a 15-minute cap, and the deepest event-source integration on AWS. **Cloud Run** runs any container that listens on a port, serves many concurrent requests per instance (default 80), allows requests of up to 60 minutes, and has jobs for batch work of up to 7 days. **Azure Functions** on the **Flex Consumption** plan runs functions with triggers and bindings, configurable per-instance concurrency, VNet integration, and optional always-ready instances. Pick by workload shape and by the ecosystem you are already in, not by benchmark headlines.

## Detail

| Dimension           | AWS Lambda                                                                    | Google Cloud Run (services)                                             | Azure Functions (Flex Consumption)                                                 |
| ------------------- | ----------------------------------------------------------------------------- | ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Deployable unit     | Function: zip (250 MB unzipped) or container image (10 GB)                    | Any OCI container listening on `$PORT`                                  | Function app: code plus triggers and bindings (Linux)                              |
| Concurrency         | 1 request per environment (Managed Instances are the exception)               | Many per instance: default 80, configurable up to 1,000                 | Configurable per-instance concurrency for HTTP; per-trigger for others             |
| Max duration        | 15 minutes                                                                    | 60 minutes per request; jobs up to 168 hours per task                   | Default 30 minutes, configurable; HTTP responses limited by the front end (~230 s) |
| Size                | Up to 10 GB memory, CPU proportional (~6 vCPU)                                | Up to 32 GiB and 8 vCPU per instance; GPUs available                    | Instance sizes of 512 MB, 2 GB, or 4 GB                                            |
| Cold-start controls | Provisioned concurrency, SnapStart                                            | Minimum instances, startup CPU boost                                    | Always-ready instances                                                             |
| Billing             | Requests + GB-seconds (init included)                                         | vCPU-seconds + GiB-seconds (request-based or instance-based) + requests | Execution time and memory, plus always-ready baseline                              |
| Event integration   | Native event source mappings (SQS, Kinesis, DynamoDB, Kafka), EventBridge, S3 | Eventarc, Pub/Sub push, Cloud Scheduler, Cloud Tasks                    | Triggers and bindings (Service Bus, Event Hubs, Storage, Cosmos DB)                |
| Orchestration       | Step Functions, Lambda durable functions                                      | Workflows                                                               | Durable Functions                                                                  |
| Portability         | AWS-specific handler and event shapes                                         | Plain container: also runs on Knative or Kubernetes                     | Functions host is open source and runs in containers                               |

**What the concurrency model changes.** With one request per environment, Lambda isolates requests well and keeps code simple, but 500 concurrent requests need 500 environments, 500 cold starts during a burst, and potentially 500 database connections. Cloud Run and Flex Consumption can serve those requests from a handful of instances, which helps I/O-bound APIs a lot. The cost is that your code must be safe for concurrent use, one slow request competes with others for the same CPU, and a memory leak hits many requests at once.

**Where each tends to win**

- **Lambda** - glue and event processing inside AWS (S3, SQS, DynamoDB Streams, EventBridge), with fine-grained IAM per function and the richest failure handling (destinations, partial batch responses, bisecting stream batches).
- **Cloud Run** - HTTP APIs and web apps that already ship as containers, long requests, WebSockets and gRPC streaming, and teams that want to keep a path to Kubernetes. Cloud Run functions (formerly Cloud Functions) are built on the same platform.
- **Azure Functions** - Microsoft-centric estates where triggers and bindings to Service Bus, Event Hubs, and Cosmos DB remove boilerplate, and Durable Functions covers long-running orchestration in code.

**Plan and runtime churn to know.** Azure's older Linux Consumption plan retires on 30 September 2028 and Flex Consumption is the replacement. Google renamed Cloud Functions to Cloud Run functions. AWS added Lambda Managed Instances (functions on EC2 capacity you choose) and durable functions. Check the current limits page before quoting a number in a design review.

**Trade-offs common to all three.** Account or project quotas, not the platform, usually cap you first. Cold starts depend mostly on your package and init code. And at steady high utilisation, reserved containers or VMs are cheaper on every provider.

## Example

```bash
# Cloud Run: concurrency, warm floor, and cold-start help are deploy-time flags.
gcloud run deploy orders-api --image=europe-docker.pkg.dev/acme/apps/orders:1.4.2 \
  --region=europe-west1 --concurrency=80 --min-instances=1 --max-instances=50 \
  --cpu-boost --timeout=300

# Azure Functions Flex Consumption: instance size, scale ceiling, always-ready baseline.
az functionapp create --resource-group rg-orders --name fn-orders-weu \
  --storage-account stordersweu --flex-consumption-location westeurope \
  --runtime python --runtime-version 3.12 --instance-memory 2048
az functionapp scale config set --resource-group rg-orders --name fn-orders-weu \
  --maximum-instance-count 100
az functionapp scale config always-ready set --resource-group rg-orders --name fn-orders-weu \
  --settings http=2

# Lambda: the equivalent warm floor is provisioned concurrency on an alias.
aws lambda put-provisioned-concurrency-config --function-name orders-api \
  --qualifier live --provisioned-concurrent-executions 5
```

## Interview tips

- Lead with the concurrency model - one request per environment versus many per instance - and explain what it changes for cold starts, connection counts, and code safety.
- Quote the limits that drive design: Lambda's 15 minutes, Cloud Run's 60-minute requests and 7-day jobs, and the Azure HTTP response ceiling even when function timeouts are longer.
- Map each platform's warm-capacity control: provisioned concurrency or SnapStart, minimum instances or CPU boost, always-ready instances.
- Show current knowledge: Flex Consumption replacing Linux Consumption, Cloud Run functions, Lambda Managed Instances.
- Close with judgement: choose the platform your events and identity already live on, and move steady, heavy workloads to containers or VMs.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Serverless Architecture](./README.md) · [All topics](../README.md)
