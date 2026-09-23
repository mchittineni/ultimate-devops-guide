---
title: "What is Traffic Shadowing (Mirroring) and how is it used for zero-risk production testing?"
id: 619
category: "API Gateway and Service Mesh"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - traffic-shadowing
  - mirroring
  - envoy
  - testing
  - canary
quiz:
  stem: "What critical precaution must engineering teams take when enabling Traffic Shadowing to a new version of a payment service?"
  options:
    - "Disabling all database read operations"
    - "Mocking or disabling external payment gateway calls in the candidate service to prevent real customers from being charged twice"
    - "Converting all HTTPS traffic to plain text HTTP"
    - "Ensuring the candidate service runs in the same container as the production service"
  answer: 2
  explanation: "Because traffic shadowing replays real production payloads, if the new service connects to real third-party APIs (like Stripe), it will execute duplicate credit card charges unless external calls are mocked."
---

# What is Traffic Shadowing (Mirroring) and how is it used for zero-risk production testing?

**Short answer:** Traffic shadowing copies live requests to a candidate version of a service while the stable version keeps answering the user. The proxy (Envoy via Istio, the Gateway API `RequestMirror` filter, NGINX `mirror`) sends the copy fire-and-forget and discards the candidate's response, so you see how new code behaves on real payloads and real load without users seeing its output. It is low-risk rather than zero-risk: any side effect the candidate performs - database writes, payments, emails, messages - happens for real, and the mirrored load hits shared dependencies.

## Detail

**What it is good for**

- Validating a rewrite or a new engine against real request shapes and edge cases that synthetic tests never contain.
- Measuring latency, CPU, memory, and error rate under production traffic before any user depends on it.
- Comparing responses: with a diffing tool (or by logging both responses keyed by request ID) you can check the candidate produces the same answers - a technique Twitter's Diffy popularised.

**How the proxy does it.** For each request selected by the mirror percentage, the proxy sends a copy to the mirror destination and does not wait for it. Envoy appends `-shadow` to the `Host`/`:authority` header of the copy, which lets the candidate (and its logs) recognise mirrored traffic. The candidate's response and errors are dropped; the user only ever sees the primary's response.

**The hazards, which are the real interview content**

- **Side effects are duplicated.** A candidate that charges cards, sends email, publishes events, or writes to the shared database will do it twice. Point it at stubs or sandboxes for external calls, a separate or isolated datastore, and disable publishing - or shadow only idempotent, read-only endpoints.
- **Shared dependencies get extra load.** Mirroring 100% of traffic to a candidate that uses the same database roughly doubles that database's read load; start with a few percent.
- **Resource cost on the proxy.** Request bodies are buffered to be copied, which costs memory for large uploads.
- **Not every protocol mirrors well** - streaming, WebSockets, and long-polling are awkward; asynchronous consumers need their own replay approach (for example consuming a copy of the topic).
- **Data protection** - mirrored requests carry real personal data into a less mature environment, which must meet the same controls.

**Shadowing versus canary.** Shadowing tests without any user seeing the new version's output; a canary exposes a small share of users to it. Shadow first to catch correctness and performance problems, then canary to validate real user outcomes.

## Example

```yaml
# Istio: all traffic served by v1; 20% copied to v2, whose responses are discarded
apiVersion: networking.istio.io/v1
kind: VirtualService
metadata: { name: payments, namespace: prod }
spec:
  hosts: [payments.prod.svc.cluster.local]
  http:
    - route:
        - destination: { host: payments.prod.svc.cluster.local, subset: v1 }
          weight: 100
      mirror: { host: payments.prod.svc.cluster.local, subset: v2 }
      mirrorPercentage: { value: 20.0 }
```

```yaml
# Gateway API equivalent: RequestMirror filter (percent support is newer - check your implementation)
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata: { name: payments, namespace: prod }
spec:
  parentRefs: [{ name: public-gateway, namespace: infra }]
  rules:
    - backendRefs: [{ name: payments-v1, port: 80 }]
      filters:
        - type: RequestMirror
          requestMirror:
            backendRef: { name: payments-v2, port: 80 }
            percent: 20
```

## Interview tips

- Say clearly that the user only ever receives the stable version's response, and that the copy is fire-and-forget.
- Lead the risks with duplicated side effects - payments, email, events, writes to shared data - and how you neutralise them.
- Mention load on shared dependencies and starting with a small mirror percentage.
- Position shadowing before a canary: it checks correctness and performance; the canary checks real user impact.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is progressive delivery and how does it differ from traditional deployment strategies?]] (`#509`): [What is progressive delivery and how does it differ from traditional deployment strategies?](../core-devops-concepts/what-is-progressive-delivery-and-how-does-it-differ-from-traditional-deployment-strategies.md)
- [[What is Shift-Left and how is it practically implemented across the SDLC?]] (`#510`): [What is Shift-Left and how is it practically implemented across the SDLC?](../core-devops-concepts/what-is-shift-left-and-how-is-it-practically-implemented-across-the-sdlc.md)
- [[How do you detect, isolate, and eradicate flaky tests in a CI/CD pipeline?]] (`#536`): [How do you detect, isolate, and eradicate flaky tests in a CI/CD pipeline?](../cicd/how-do-you-detect-isolate-and-eradicate-flaky-tests-in-a-ci-cd-pipeline.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to API Gateway and Service Mesh](./README.md) · [All topics](../README.md)
