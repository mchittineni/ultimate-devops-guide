---
title: "What is progressive delivery and how does it differ from traditional deployment strategies?"
id: 509
category: "Core DevOps Concepts"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - core-devops-concepts
  - progressive-delivery
  - canary
  - feature-flags
  - deployment
quiz:
  stem: "How does progressive delivery decouple software deployment from software release?"
  options:
    - "By compiling code directly on the host machine before distribution"
    - "By installing code into production while controlling user exposure through traffic routing and feature flags"
    - "By requiring all deployments to execute exclusively during off-peak weekend hours"
    - "By storing compiled binaries on client machines rather than web servers"
  answer: 2
  explanation: "Deployment installs the binary/container onto production infrastructure, while release exposes the functionality to users via feature gates and traffic shaping."
---

# What is progressive delivery and how does it differ from traditional deployment strategies?

**Short answer:** Progressive delivery extends continuous delivery by decoupling deployment (installing code in production) from release (exposing features to users), controlling blast radius through canary rollouts, traffic shifting, and feature flags based on real-time telemetry.

## Detail

In traditional deployment strategies (like rolling updates or a plain blue/green cut-over), all users receive new code as soon as instances pass readiness probes. **Progressive delivery** acknowledges that readiness probes only verify startup, not runtime correctness under live load.

### Core Techniques of Progressive Delivery

1. **Canary Analysis with Automated Metric Verification**: Routing 2% of traffic to a new version, monitoring latency (p99) and error rate against baseline over 15 minutes, then incrementally promoting to 10%, 25%, 50%, and 100%.
2. **Feature Flags**: Shipping code disabled behind boolean flags or user segment evaluations, enabling immediate rollback without redeploying containers.
3. **Automated Rollback on Error Budget Burn**: If synthetic or real user error rate breaches an SLI during a canary step, the rollout aborts immediately.
4. **Traffic Shifting**: weighted routing through a service mesh, an ingress/gateway controller, or Gateway API `HTTPRoute` weights, with controllers such as Argo Rollouts or Flagger driving the steps.

**Trade-offs.** Canary analysis needs enough traffic for the comparison to be statistically meaningful - a service with ten requests a minute cannot judge a 2% canary in 15 minutes. It also needs good metrics, versions that can run side by side (backward-compatible APIs and schemas), and flag hygiene, since stale flags become their own source of bugs.

## Example

The analysis half of an Argo Rollouts canary: the rollout aborts and returns traffic to stable if the success rate drops below 99% twice.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  args:
    - name: service
  metrics:
    - name: success-rate
      interval: 1m
      count: 10
      failureLimit: 2
      successCondition: result[0] >= 0.99
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            sum(rate(http_requests_total{service="{{args.service}}",code!~"5.."}[2m]))
            / sum(rate(http_requests_total{service="{{args.service}}"}[2m]))
```

## Interview tips

- Decoupling deployment from release.
- Traffic shaping (e.g., using service mesh or ingress) combined with telemetry analysis.
- Automated canary rollback based on business and system metrics.
- Limits: traffic volume for statistical confidence, and schema compatibility between versions.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)
- [[What are Jenkins Pipelines?]] (`#18`): [What are Jenkins Pipelines?](../cicd/what-are-jenkins-pipelines.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Core DevOps Concepts](./README.md) · [All topics](../README.md)
