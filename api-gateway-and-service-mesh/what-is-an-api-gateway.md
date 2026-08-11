---
title: "What is an API Gateway?"
id: 76
category: "API Gateway and Service Mesh"
difficulty: "Intermediate"
tags:
  - devops
  - api-gateway-and-service-mesh
  - interview-questions
---

# What is an API Gateway?

**Short answer:** An API gateway is a single entry point for client traffic that routes requests to backend services while handling cross-cutting concerns - authentication, rate limiting, TLS termination, caching, and observability - in one place.

## Detail

Without a gateway, every client must know every service's address, and every service must implement authentication, throttling, and logging itself. The gateway centralises that.

**Responsibilities**

- **Routing** - path, host, header, or method-based dispatch to backends, with load balancing across instances.
- **Authentication and authorisation** - validate JWTs or API keys, integrate with OAuth 2.0/OIDC, and pass verified identity downstream.
- **Rate limiting and quotas** - per client, per key, per plan.
- **TLS termination** and certificate management.
- **Request/response transformation** - protocol translation (REST to gRPC), header manipulation, response aggregation.
- **Caching** of idempotent responses.
- **Resilience** - timeouts, retries, and circuit breaking towards backends.
- **Observability** - one consistent place for access logs, metrics, and trace initiation.

**Gateway vs mesh vs load balancer.** A load balancer distributes traffic. A gateway handles _north-south_ traffic (client to system) with API-level features. A service mesh handles _east-west_ traffic (service to service). Many architectures use all three.

**Common implementations:** Kong, NGINX, Envoy-based gateways, AWS API Gateway, Azure API Management, Apigee, and Kubernetes Gateway API implementations.

**Watch out for:** making the gateway a single point of failure (deploy it redundantly), and pushing business logic into it, which recreates the enterprise service bus problem.

## Interview tips

- North-south versus east-west is the distinction that answers "gateway or mesh?" cleanly.
- Backend-for-frontend is a good pattern to mention - a tailored gateway per client type.
- Warn against business logic in the gateway; it shows architectural judgement.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to API Gateway and Service Mesh](./README.md) · [All topics](../README.md)
