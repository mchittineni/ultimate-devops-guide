---
title: "What is Cloud Run and when do you choose it?"
id: 211
category: "GCP Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - gcp-engineering
  - interview-questions
---

# What is Cloud Run and when do you choose it?

**Short answer:** Cloud Run runs stateless containers that listen on a port, scaling automatically from zero to many instances and billing per request-time resource usage. Choose it when the workload is a container, traffic is variable or spiky, and you do not need the Kubernetes API - it delivers most of what a small service needs from GKE without any cluster to operate.

## Detail

**The contract is simple.** Your container listens on `$PORT`, is stateless, and tolerates being started and stopped at any time. Cloud Run gives you concurrency per instance (default up to 80 simultaneous requests, unlike single-concurrency FaaS models), request timeouts up to an hour, HTTP/2 and gRPC, WebSockets, and traffic splitting between revisions for canary releases.

**Services versus Jobs.** Cloud Run _services_ respond to requests or events; Cloud Run _jobs_ run to completion with parallel task arrays - the right home for batch work that used to be a Kubernetes Job. Both share the same container contract and IAM model.

**Scale to zero, and its price.** A cold start pays image pull and application initialisation. Mitigations: minimum instances (paid, keeps warm capacity), startup CPU boost, lean images, and lazy initialisation. For latency-sensitive user-facing APIs, set minimum instances rather than accepting cold starts - the cost is usually small relative to the engineering effort of the alternative.

**Concurrency is the tuning dial that decides your bill.** Higher concurrency means fewer instances for the same traffic and lower cost, but shared memory and CPU per request. Concurrency of 1 makes reasoning simple and cost high. Load-test to find the point where p99 latency degrades, then set concurrency slightly below it.

**Networking and access.** Direct VPC egress (or a Serverless VPC Access connector) lets a service reach private resources such as Cloud SQL or an internal API; ingress can be restricted to internal traffic or a load balancer; IAM `run.invoker` controls who may call it, and service-to-service authentication uses ID tokens rather than shared secrets. Combined with a global external load balancer, you get Cloud CDN, Cloud Armor, and multi-region routing in front of it.

**Where Cloud Run is the wrong choice:** long-lived stateful processes, workloads needing sidecars beyond what Cloud Run supports (multi-container services exist but are constrained), anything requiring the Kubernetes API or operators, GPU-heavy training jobs (inference on GPUs is supported), and services that must maintain in-memory session state across requests without an external store.

**Versus Cloud Functions.** Cloud Functions (2nd gen) is built on Cloud Run - same infrastructure, with a source-based deployment and function signature. If you want a container and full control, use Cloud Run directly; if you want to deploy a single handler from source with event bindings, functions are the convenience layer.

## Example

```bash
# Deploy with an explicit digest, private ingress, VPC egress, and a canary split
gcloud run deploy checkout \
  --image=europe-docker.pkg.dev/payments-prod/apps/checkout@sha256:1f4b \
  --region=europe-west1 \
  --service-account=checkout@payments-prod.iam.gserviceaccount.com \
  --concurrency=60 --cpu=1 --memory=512Mi \
  --min-instances=2 --max-instances=100 \
  --ingress=internal-and-cloud-load-balancing \
  --network=vpc-prod --subnet=sn-prod-euw1 --vpc-egress=private-ranges-only \
  --no-allow-unauthenticated \
  --no-traffic --tag=canary

# Send 10% of traffic to the canary revision, then promote
gcloud run services update-traffic checkout --region=europe-west1 \
  --to-tags=canary=10
```

## Interview tips

- Concurrency per instance is the feature that distinguishes Cloud Run from classic FaaS - mention it early.
- Cold starts plus minimum instances is the expected follow-up; give the trade-off in cost terms.
- Expect: "Cloud Run or GKE?" - Cloud Run unless you need the Kubernetes API, operators, or host-level access.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is Cloud Computing?]] (`#21`): [What is Cloud Computing?](../cloud-platforms/what-is-cloud-computing.md)
- [[What is AWS (Amazon Web Services)?]] (`#22`): [What is AWS (Amazon Web Services)?](../cloud-platforms/what-is-aws-amazon-web-services.md)
- [[What is Azure?]] (`#23`): [What is Azure?](../cloud-platforms/what-is-azure.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to GCP Engineering](./README.md) · [All topics](../README.md)
