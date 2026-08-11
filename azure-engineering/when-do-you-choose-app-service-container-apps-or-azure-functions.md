---
title: "When do you choose App Service, Container Apps, or Azure Functions?"
id: 206
category: "Azure Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - azure-engineering
  - interview-questions
---

# When do you choose App Service, Container Apps, or Azure Functions?

**Short answer:** App Service for long-running web applications and APIs that want a simple PaaS with slots and easy custom domains; Container Apps for containerised microservices that need Kubernetes-style scaling (including scale to zero via KEDA) without operating a cluster; Functions for event-driven, short-lived work with rich trigger bindings. AKS only when you genuinely need the Kubernetes API and have a team to run it.

## Detail

| Service        | Unit                 | Scale to zero                       | Best for                                  | Main limitation                        |
| -------------- | -------------------- | ----------------------------------- | ----------------------------------------- | -------------------------------------- |
| App Service    | web app / plan       | no (except Consumption-style tiers) | classic web apps, APIs, easy slots        | less container-native, plan-based cost |
| Container Apps | container + revision | yes                                 | microservices, event consumers, jobs      | no direct Kubernetes API access        |
| Functions      | function app         | yes                                 | event handlers, glue, scheduled work      | execution duration limits, cold starts |
| AKS            | cluster              | node-level                          | complex platforms, operators, portability | you operate and upgrade it             |

**App Service earns its place with slots.** Deployment slots give you a warmed staging instance and an atomic swap, which is the simplest blue/green in Azure. It also handles TLS certificates, custom domains, authentication (Easy Auth), and VNet integration with minimal work. The cost model is the plan - you pay for reserved instances whether or not traffic arrives.

**Container Apps is managed Kubernetes without the cluster.** It runs on AKS internally and exposes Dapr, KEDA-based scaling on queue length or custom metrics, revisions with traffic splitting for canaries, and scale to zero. Choose it when your service is a container, your scaling signal is an event source, and nobody wants to own cluster upgrades. Its constraint is exactly that: you cannot install operators or touch the Kubernetes API.

**Functions and the plan question.** The Consumption plan scales to zero and bills per execution but suffers cold starts and has an execution timeout; Premium keeps warm instances with VNet integration and no practical timeout; the Flex Consumption plan is the newer option combining per-execution billing with VNet support and better cold-start behaviour. For latency-sensitive synchronous APIs, Consumption cold starts are usually disqualifying.

**Cost reasoning.** Steady, predictable traffic favours reserved capacity (App Service plan, or AKS nodes with reservations). Spiky or intermittent traffic favours scale-to-zero (Container Apps, Functions). The comparison is per-workload, not global - most real estates mix all three, and the platform team's job is to make each path well-paved rather than to pick one winner.

**Migration paths matter for the recommendation.** A container running on Container Apps can move to AKS later with the same image and similar manifests; a Functions app with deep binding usage is harder to relocate. If long-term portability is a stated requirement, that argues for containers early - but do not pay Kubernetes' operational cost for a portability need nobody has scheduled.

## Example

```bash
# Container Apps: HTTP autoscaling with scale to zero and a canary revision split
az containerapp create \
  --name checkout --resource-group rg-checkout-prod-weu \
  --environment cae-prod-weu \
  --image acme.azurecr.io/checkout@sha256:1f4b \
  --ingress external --target-port 8080 \
  --min-replicas 0 --max-replicas 30 \
  --scale-rule-name http-rule --scale-rule-type http \
  --scale-rule-http-concurrency 50 \
  --user-assigned "$UAMI_ID" # workload identity, no secrets

# Shift 10% of traffic to the new revision, then ramp
az containerapp ingress traffic set --name checkout --resource-group rg-checkout-prod-weu \
  --revision-weight checkout--rev12=90 checkout--rev13=10
```

## Interview tips

- Answer with the decision criteria - event-driven versus long-running, scale-to-zero need, and whether you need the Kubernetes API.
- Naming KEDA behind Container Apps and Flex Consumption for Functions shows current knowledge.
- Expect: "why not AKS for everything?" - operational cost, upgrade treadmill, and no business value unless you need the API.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is Cloud Computing?]] (`#21`): [What is Cloud Computing?](../cloud-platforms/what-is-cloud-computing.md)
- [[What is Azure?]] (`#23`): [What is Azure?](../cloud-platforms/what-is-azure.md)
- [[What is Google Cloud Platform (GCP)?]] (`#24`): [What is Google Cloud Platform (GCP)?](../cloud-platforms/what-is-google-cloud-platform-gcp.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Azure Engineering](./README.md) · [All topics](../README.md)
