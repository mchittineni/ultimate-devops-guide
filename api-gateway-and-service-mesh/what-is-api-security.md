---
title: "What is API Security?"
id: 78
category: "API Gateway and Service Mesh"
difficulty: "Intermediate"
tags:
  - devops
  - api-gateway-and-service-mesh
  - interview-questions
---

# What is API Security?

**Short answer:** API security is protecting APIs against unauthorised access and abuse through strong authentication, fine-grained authorisation, transport encryption, input validation, rate limiting, and monitoring - guided by the OWASP API Security Top 10.

## Detail

**Authentication** - verify who is calling. OAuth 2.0 with OIDC for user-facing APIs, mutual TLS or signed requests for service-to-service, API keys only for low-risk identification (they identify, they do not authenticate a user). Use short-lived tokens and rotate credentials.

**Authorisation** - verify what they may do, on _every_ request and _every_ object. Broken object-level authorisation (BOLA) is API1 on the OWASP API Security Top 10:2023 - the number one item: an endpoint that returns `/orders/{id}` without checking the order belongs to the caller is the most common serious API vulnerability in the wild.

**Transport** - TLS 1.2+ everywhere, HSTS, and no sensitive data in URLs (they land in logs and referrer headers).

**Input validation** - validate against a schema, reject unknown fields, cap payload size and array lengths, and constrain query depth on GraphQL. Never build queries by string concatenation.

**Rate limiting and quotas** - per user and per IP, protecting against both abuse and accidental client loops. Return `429` with `Retry-After`.

**Data exposure** - return only the fields needed. Filtering in the client is not security; the response already contains the data.

**Operational** - audit logging of authentication and authorisation decisions, alerting on anomalous patterns, an inventory of every API (shadow and zombie APIs are a real risk), and security testing in CI.

## Example

```yaml
# Gateway-enforced JWT validation and rate limit
plugins:
  - name: jwt
    config:
      claims_to_verify: [exp, aud]
      key_claim_name: iss
  - name: rate-limiting
    config: { minute: 120, policy: redis, limit_by: consumer }
```

## Interview tips

- Name BOLA/IDOR explicitly and explain the object-level check - it is the highest-signal answer here.
- Distinguish authentication from authorisation cleanly and early.
- Mention API inventory and schema validation; both indicate real-world experience.

---

[⬅ Back to API Gateway and Service Mesh](./README.md) · [All topics](../README.md)
