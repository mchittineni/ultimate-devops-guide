---
title: "What is Fault Injection testing and how is it executed via a Service Mesh?"
id: 621
category: "API Gateway and Service Mesh"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - service-mesh
  - chaos-engineering
  - fault-injection
  - envoy
quiz:
  stem: "What is the primary benefit of performing Chaos Engineering fault injection at the Service Mesh proxy layer rather than modifying application code?"
  options:
    - "Fault injection causes permanent database corruption"
    - "It allows testing resilience against timeouts and 5xx errors across any programming language without polluting production application source code"
    - "Service mesh fault injection can only be run on local developer laptops"
    - "It guarantees 100% server uptime"
  answer: 2
  explanation: "Because the service mesh sidecar intercepts network traffic, engineers can inject latency and HTTP failures transparently into any service, regardless of language or framework."
---

# What is Fault Injection testing and how is it executed via a Service Mesh?

**Short answer:** Fault injection deliberately adds latency or returns errors on real calls to test whether callers handle a slow or failing dependency - timeouts, retries, circuit breakers, fallbacks - before a real outage tests it for you. A service mesh does this in the proxy (Istio's `VirtualService` `fault` block, or Envoy's fault filter), so no application code changes and the fault can be scoped to a percentage of requests, a header, or a single caller. It exercises the network path only: it cannot simulate a crashed Pod, a full disk, or a slow database query inside the service.

## Detail

**The two fault types**

- **Delay** - hold a percentage of requests for a fixed time (for example 5 s on 10%). Tests timeouts, deadline propagation, thread and connection-pool exhaustion, and whether the caller's timeout is shorter than its own caller's.
- **Abort** - fail a percentage of requests immediately with an HTTP status (500, 503) or a gRPC status. Tests fallbacks, retry behaviour (and retry storms), and circuit breakers.

**How it is applied.** The mesh programs the fault into the client-side proxy for traffic to the target host - with a sidecar, the caller's sidecar; in Istio ambient mode, the destination's waypoint (L7 features need a waypoint). Because the proxy generates the fault, the application sees an ordinary slow or failed response.

**Scoping keeps it safe**

- Match on a header (`x-chaos: true`), a source workload label, or a path so only test traffic is affected.
- Start in staging, then in production with a small percentage and a clear hypothesis ("with 5 s delay on 10% of inventory calls, checkout p99 stays under 2 s and error rate under 0.5%").
- Have an abort switch - deleting or reverting the resource removes the fault within seconds - and watch SLO dashboards throughout.

**Gotchas**

- In Istio, fault injection cannot be combined with `retries` or `timeout` settings on the same route; put the fault on a dedicated route (for example matched by a header) or test the caller's own timeout behaviour instead.
- Retries configured elsewhere can mask aborts, so you learn about your retry policy rather than your fallback.
- The Kubernetes Gateway API has no standard fault-injection filter; you use implementation-specific extensions or the mesh's native API.
- For failures the proxy cannot express (killed Pods, node loss, DNS, resource pressure), use a chaos tool such as Chaos Mesh, LitmusChaos, or AWS FIS.

## Example

```yaml
# Delay 10% and abort 5% of calls to inventory - but only for requests marked as chaos tests
apiVersion: networking.istio.io/v1
kind: VirtualService
metadata:
  name: inventory
  namespace: prod
spec:
  hosts: [inventory.prod.svc.cluster.local]
  http:
    - name: chaos
      match:
        - headers: { x-chaos: { exact: "true" } }
      fault:
        delay:
          percentage: { value: 10.0 }
          fixedDelay: 5s
        abort:
          percentage: { value: 5.0 }
          httpStatus: 503
      route:
        - destination: { host: inventory.prod.svc.cluster.local }
    - name: default # normal traffic keeps its timeout and retries
      timeout: 2s
      retries: { attempts: 2, perTryTimeout: 1s, retryOn: "5xx,reset" }
      route:
        - destination: { host: inventory.prod.svc.cluster.local }
```

```bash
# Drive test traffic through the faulty route (checkout must propagate x-chaos downstream)
for i in $(seq 1 100); do
  curl -s -o /dev/null -w '%{http_code} %{time_total}\n' -H 'x-chaos: true' \
    http://checkout.prod.svc.cluster.local/api/cart
done | sort | uniq -c
kubectl delete virtualservice inventory -n prod   # abort switch (or re-apply without the chaos route)
```

## Interview tips

- Tie fault injection to a hypothesis about a specific resilience mechanism (timeout, fallback, circuit breaker); injecting faults without one is just breaking things.
- Explain that the proxy generates the fault, so it works for any language with no code changes - and say what it cannot simulate.
- Mention scoping by header or source and ramping from staging to a small production percentage with an abort path.
- Knowing that Istio will not combine faults with retries or timeouts on the same route is a detail that shows hands-on use.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#20`): [What is the difference between Continuous Delivery and Continuous Deployment?](../cicd/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to API Gateway and Service Mesh](./README.md) · [All topics](../README.md)
