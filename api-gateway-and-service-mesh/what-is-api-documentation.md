---
title: "What is API Documentation?"
id: 80
category: "API Gateway and Service Mesh"
difficulty: "Beginner"
tags:
  - devops
  - api-gateway-and-service-mesh
  - interview-questions
---

# What is API Documentation?

**Short answer:** API documentation describes how to use an API - endpoints, parameters, schemas, authentication, errors, and examples - and is most valuable when generated from a machine-readable specification such as OpenAPI so it cannot drift from the implementation.

## Detail

**Specification-driven.** OpenAPI (REST), AsyncAPI (event-driven), and Protocol Buffers (gRPC) define the contract in a machine-readable format. From one spec you get rendered documentation, client SDKs, server stubs, mock servers, request validation, and contract tests. That reuse is why spec-first is the modern default.

**What complete documentation includes**

- Every endpoint with method, path, parameters, and request/response schemas.
- **Authentication** - how to obtain and present credentials, with a working example.
- **Error responses** - status codes, error body shape, and what the client should do about each.
- **Rate limits** and pagination conventions.
- **Working examples** - copy-pasteable `curl` commands with realistic values.
- **Versioning and deprecation policy** - how changes are communicated and how long old versions live.
- **Changelog.**

**Keeping it honest.** Documentation drifts the moment it is written by hand separately from the code. Defences: generate the spec from code annotations or generate code from the spec; validate live requests against the schema in CI; run contract tests (Pact, Schemathesis) that fail the build when implementation and spec diverge; and publish the docs automatically from the pipeline.

**Beyond reference docs**, good API programmes include a getting-started guide, common workflow tutorials, and an interactive console - reference documentation alone rarely gets a developer to their first successful call.

## Example

```yaml
openapi: 3.1.0
info: { title: Orders API, version: 1.2.0 }
paths:
  /orders/{orderId}:
    get:
      summary: Retrieve an order
      security: [{ bearerAuth: [] }]
      parameters:
        - { name: orderId, in: path, required: true, schema: { type: string } }
      responses:
        "200":
          {
            description: Order found,
            content:
              {
                application/json:
                  { schema: { $ref: "#/components/schemas/Order" } },
              },
          }
        "404": { description: Not found }
        "429": { description: Rate limit exceeded }
```

## Interview tips

- Spec-first with generated artifacts is the answer that shows engineering maturity.
- Contract testing in CI is how you prove docs and implementation agree - mention it.
- Note that error documentation is the most commonly missing and most needed section.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to API Gateway and Service Mesh](./README.md) · [All topics](../README.md)
