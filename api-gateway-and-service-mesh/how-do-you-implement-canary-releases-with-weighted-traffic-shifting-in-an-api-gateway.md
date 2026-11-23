---
title: "How do you implement Canary Releases with weighted traffic shifting in an API Gateway?"
id: 620
category: "API Gateway and Service Mesh"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - canary
  - traffic-shifting
  - api-gateway
  - progressive-delivery
quiz:
  stem: "Why is L7 API Gateway traffic shifting superior to native Kubernetes RollingUpdate deployments for canary testing?"
  options:
    - "Kubernetes rolling updates cannot run in the cloud"
    - "L7 gateways allow routing precise percentages of traffic (e.g. 1%) regardless of how many pod replicas exist, while rolling updates couple traffic to replica count"
    - "Rolling updates require purchasing third-party enterprise licenses"
    - "L7 gateways automatically rewrite application code"
  answer: 2
  explanation: "In standard Kubernetes, achieving 1% traffic to a canary requires running 99 stable pods and 1 canary pod. L7 gateways route fractional traffic weights across arbitrary replica sizes."
---

# How do you implement Canary Releases with weighted traffic shifting in an API Gateway?

**Short answer:** Run the new version beside the stable one and let the gateway split requests by **weight** (for example 95/5) at layer 7, so the canary's traffic share is independent of how many replicas each version has. A controller such as Argo Rollouts or Flagger then moves the weights step by step - 1%, 5%, 25%, 50%, 100% - evaluating error rate and latency at each step and resetting the weight to 0 if the canary misbehaves. The limits: weights are statistical (a low-traffic service may never produce a meaningful sample), and both versions must work against the same database schema.

## Detail

**Why the gateway rather than replica counts.** A plain Kubernetes Service balances across Pods, so traffic share follows replica count: 1% needs 99 stable Pods and 1 canary Pod. L7 weighted routing decouples the two - one canary Pod can take exactly 2% of requests.

**Mechanisms by platform**

- **Kubernetes Gateway API** - `HTTPRoute` `backendRefs` with `weight` values; supported by Envoy Gateway, Istio, Cilium, NGINX Gateway Fabric, Kong, and cloud gateway controllers. This is the portable choice now that Ingress-NGINX's canary annotations belong to a controller that has been retired.
- **Service mesh** - Istio `VirtualService` weights or Gateway API routes applied to mesh traffic, which also covers east-west calls.
- **Managed gateways** - AWS API Gateway stage canary settings, Lambda alias weights, ALB weighted target groups, Azure Front Door and Application Gateway backend weights.

**Why not just a rolling update?** A Kubernetes rolling update with good readiness probes is already zero-downtime - but it is not low-risk. It replaces every Pod, so once it finishes every user is on the new version, and a bug that passes readiness checks reaches everyone. A canary limits the blast radius to a small, measured share of traffic and gives you an automatic way back.

**How the split actually happens on AWS (EKS + ALB).** A frequent follow-up is "how does Argo CD talk to AWS?" - and the answer is that it does not. Argo CD only syncs the Rollout, Services and Ingress from Git into the cluster. Argo Rollouts, configured with `trafficRouting.alb`, creates the canary Pods and writes the stable/canary weights into an action annotation on the Ingress. The **AWS Load Balancer Controller**, running in the cluster with its own IAM role (IRSA or EKS Pod Identity), watches that Ingress and calls the AWS API to set **weighted target groups** on the ALB. The split is per request at the ALB, so it is exact regardless of Pod counts. When a step fails analysis, Rollouts sets the canary weight back to 0 and the controller reconciles the ALB again.

**Beyond random weights.** Header- or cookie-based matches (`x-canary: true`, internal users, a specific tenant) let you expose the canary deliberately before any random traffic, and **session affinity** keeps a user on one version so they do not flip between UIs mid-session.

**Automating the analysis.** Argo Rollouts and Flagger own the weight: they update the route, query Prometheus (or Datadog, CloudWatch) for success rate and p99 latency, and promote or abort. The analysis should compare the canary with the stable version over the same window, include a warm-up, and require enough requests per step to be meaningful.

**Constraints to plan for:** database changes must be backward-compatible (expand/contract), because both versions run concurrently; asynchronous consumers (queue workers) are not routed by the gateway and need their own canary mechanism; and caches or CDNs in front can hide the split.

## Example

```yaml
# Gateway API: 95% stable, 5% canary; internal testers always get the canary
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: catalog
  namespace: shop
spec:
  parentRefs:
    - name: public-gateway
      namespace: infra
  hostnames: ["api.example.com"]
  rules:
    - matches:
        - path: { type: PathPrefix, value: /catalog }
          headers: [{ name: x-canary, value: "true" }]
      backendRefs:
        - { name: catalog-v2, port: 80 }
    - matches:
        - path: { type: PathPrefix, value: /catalog }
      backendRefs:
        - { name: catalog-v1, port: 80, weight: 95 }
        - { name: catalog-v2, port: 80, weight: 5 }
```

```yaml
# Argo Rollouts drives the same route: steps, pauses, and automatic abort
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata: { name: catalog, namespace: shop }
spec:
  strategy:
    canary:
      stableService: catalog-v1
      canaryService: catalog-v2
      trafficRouting:
        plugins:
          argoproj-labs/gatewayAPI: { httpRoute: catalog, namespace: shop }
      steps:
        - setWeight: 5
        - analysis: { templates: [{ templateName: success-rate }] }
        - setWeight: 25
        - pause: { duration: 10m }
        - setWeight: 50
        - pause: { duration: 10m }
  # selector, template, and replicas as in a Deployment - omitted
```

```yaml
# EKS + ALB variant: Argo Rollouts writes the weights, the AWS Load Balancer Controller applies them
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata: { name: catalog, namespace: shop }
spec:
  strategy:
    canary:
      stableService: catalog-stable
      canaryService: catalog-canary
      trafficRouting:
        alb:
          ingress: catalog # Rollouts adds alb.ingress.kubernetes.io/actions.catalog-stable with the weights
          servicePort: 80
      steps:
        - setWeight: 10
        - pause: { duration: 10m }
  # selector, template, and replicas omitted
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: catalog
  namespace: shop
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
spec:
  ingressClassName: alb
  rules:
    - http:
        paths:
          - path: /catalog
            pathType: Prefix
            backend:
              service:
                name: catalog-stable
                port: { name: use-annotation } # route via the weighted action annotation
```

## Interview tips

- Say why the gateway matters: weights decouple traffic share from replica count.
- Asked "rolling update or canary?", agree that a rolling update is already zero-downtime, then explain that it exposes every user once it completes, while a canary limits the blast radius.
- On AWS, be precise about who does what: Argo CD syncs manifests and never calls AWS; Argo Rollouts writes weights onto the Ingress; the AWS Load Balancer Controller turns them into ALB weighted target groups. Saying "Argo CD configures the ALB" is the common mistake.
- Name Gateway API `HTTPRoute` weights as the portable mechanism, and a controller (Argo Rollouts, Flagger) as what moves them and decides.
- Mention header-based routing for a dark launch before random traffic, and session affinity for user-facing canaries.
- Raise the constraints unprompted: backward-compatible schema changes, queue consumers outside the gateway, and low-traffic services where the statistics never settle.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is progressive delivery and how does it differ from traditional deployment strategies?]] (`#509`): [What is progressive delivery and how does it differ from traditional deployment strategies?](../core-devops-concepts/what-is-progressive-delivery-and-how-does-it-differ-from-traditional-deployment-strategies.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)
- [[What are Jenkins Pipelines?]] (`#18`): [What are Jenkins Pipelines?](../cicd/what-are-jenkins-pipelines.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to API Gateway and Service Mesh](./README.md) · [All topics](../README.md)
