---
title: "What is the Strangler Fig pattern and how is it used to safely decommission monolithic applications?"
id: 606
category: "Cloud Native Architecture"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - architecture
  - refactoring
  - strangler-fig
  - microservices
quiz:
  stem: "What is the core strategic principle behind the Strangler Fig architecture pattern for legacy migration?"
  options:
    - "Halting all feature development for two years to execute a clean-slate rewrite"
    - "Placing an API gateway in front of the monolith to incrementally divert traffic to new microservices one bounded context at a time"
    - "Converting all relational databases into flat CSV files"
    - "Running legacy code inside WebAssembly sandbox modules"
  answer: 2
  explanation: "The Strangler Fig pattern uses a facade (API Gateway) to route specific API endpoints to new microservices while the legacy monolith continues handling the remainder, enabling incremental risk-free migration."
---

# What is the Strangler Fig pattern and how is it used to safely decommission monolithic applications?

**Short answer:** Named by Martin Fowler after vines that grow around a host tree until they replace it, the Strangler Fig pattern replaces a legacy system one capability at a time. You put an interception layer - a reverse proxy, API gateway, or event router - in front of the monolith, build a new service for one slice, redirect that slice's traffic to it, and repeat until nothing routes to the monolith and it can be switched off. It avoids the risk of a big-bang rewrite, at the cost of running old and new side by side for a long time and solving data ownership for every slice.

## Detail

**The loop**

1. **Intercept.** Route all traffic through a facade you control (NGINX, Envoy, a cloud API gateway, or Gateway API routes). Initially everything goes to the monolith, so this step changes nothing for users.
2. **Pick a slice.** Choose a bounded context with clear edges and real value - often something that changes frequently or needs different scaling - rather than the most tangled core.
3. **Build and shadow.** Implement the new service; where possible, mirror traffic or compare outputs against the monolith before users depend on it.
4. **Redirect gradually.** Shift the route by percentage or by user segment, with a fast route-back if metrics degrade.
5. **Remove the dead code** from the monolith, so it genuinely shrinks.
6. **Repeat**, then decommission the monolith and its infrastructure.

**Data is the hard part.** The new service usually needs data the monolith owns. Options, roughly in order of preference: the new service becomes the owner and the monolith reads through its API; changes are synchronised with change data capture from the monolith's database while ownership transfers; or, temporarily, both read the same database - acceptable only as a short, explicit stage because it keeps the coupling you are trying to remove.

**Related techniques**

- **Branch by abstraction** - inside the monolith, put an interface in front of the code being replaced, so calls can be switched to the new implementation (or a client for the new service) behind a flag.
- **Event interception** - for asynchronous flows, route messages or publish domain events from the monolith so new services can react without HTTP routing.
- **Anti-corruption layer** - translate between the legacy model and the new service's model so the old design does not leak into the new code.

**Why teams stall.** The facade and the first two services are easy; the remaining 30% of the monolith is the tangled core, and without an explicit decommissioning plan and budget the organisation ends up running both systems indefinitely. Track the share of traffic and code still served by the monolith as a visible metric.

## Example

```nginx
# The facade: new service owns /payments; everything else still goes to the monolith.
upstream monolith  { server legacy-app.internal:8080; }
upstream payments  { server payments-svc.internal:8080; }

split_clients "${remote_addr}${http_user_agent}" $payments_backend {
    20%   payments;   # ramp the new service: 20% of clients today
    *     monolith;
}

server {
    listen 443 ssl;
    server_name shop.example.com;
    ssl_certificate     /etc/nginx/tls/shop.crt;
    ssl_certificate_key /etc/nginx/tls/shop.key;

    location /api/v1/payments/ { proxy_pass http://$payments_backend; }
    location /                 { proxy_pass http://monolith; }   # shrinking over time
}
```

## Interview tips

- Describe the loop - intercept, extract one slice, redirect gradually, delete the old code, repeat - and stress that the facade comes first and changes nothing.
- Spend time on data ownership; that is where strangler migrations actually succeed or fail.
- Mention branch by abstraction and an anti-corruption layer as companions to the routing change.
- Warn about the long tail: without a decommission plan, you run two systems forever.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Native Architecture](./README.md) · [All topics](../README.md)
