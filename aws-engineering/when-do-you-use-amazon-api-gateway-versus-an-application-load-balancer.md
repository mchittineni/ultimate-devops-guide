---
title: "When do you use Amazon API Gateway versus an Application Load Balancer?"
id: 798
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - aws-engineering
  - api-gateway
  - load-balancing
  - serverless
quiz:
  stem: "Which requirement most clearly points to Amazon API Gateway (REST API) rather than an Application Load Balancer?"
  options:
    - "TLS termination with an ACM certificate"
    - "Attaching AWS WAF managed rules"
    - "Per-client API keys with usage plans that enforce throttling and monthly quotas"
    - "Routing requests to different target groups by URL path"
  answer: 3
  explanation: "ALBs also terminate TLS with ACM certificates, integrate with AWS WAF, and route by path and host. Per-client API keys, usage plans, quotas and per-client throttling are API-management features that API Gateway REST APIs provide and ALB does not."
---

# When do you use Amazon API Gateway versus an Application Load Balancer?

**Short answer:** Use **API Gateway** when you need **API management**: per-client API keys, usage plans and quotas, request validation and transformation, caching, authorizers (IAM, Cognito, JWT, Lambda), and pay-per-request pricing that suits spiky or low-volume serverless APIs. Use an **ALB** when you need a **load balancer**: steady high-volume HTTP traffic to containers or EC2, long-lived connections and WebSockets at scale, gRPC, and predictable hourly-plus-capacity pricing that becomes far cheaper than per-request pricing at sustained volume. TLS, WAF, path routing, Lambda targets and basic OIDC authentication exist on **both**, so they are not the deciding factors.

## Detail

### What each one actually is

- **API Gateway** is a managed API front door. It comes in three flavours: **REST APIs** (the full feature set - API keys, usage plans, request validation, mapping templates, caching, WAF, private APIs), **HTTP APIs** (cheaper and lower latency, JWT authorizers and CORS built in, but no usage plans, caching or direct WAF association) and **WebSocket APIs**. It scales to zero cost when idle and has no servers or load-balancer capacity to manage.
- **ALB** is a Layer 7 load balancer that runs continuously in your VPC subnets. It routes on host, path, headers, query strings and source IP to target groups of instances, IPs, containers or Lambda functions, with weighted target groups for canaries. On EKS the AWS Load Balancer Controller creates it from an Ingress.

### The real differentiators

| Need                                                | API Gateway                                                 | ALB                                      |
| --------------------------------------------------- | ----------------------------------------------------------- | ---------------------------------------- |
| Per-client API keys, usage plans, quotas            | Yes (REST)                                                  | No                                       |
| Per-client throttling                               | Yes (stage, method and usage-plan limits)                   | Only via WAF rate-based rules            |
| Request validation, payload transformation, caching | Yes (REST)                                                  | No                                       |
| Authentication                                      | IAM, Cognito, JWT, Lambda authorizers                       | OIDC or Cognito login on HTTPS listeners |
| Pricing                                             | Per request (plus caching and data transfer)                | Hourly plus capacity units               |
| Timeouts and payloads                               | Integration timeout historically 29 s; payload limit ~10 MB | Idle timeout configurable up to 4000 s   |
| Long-lived and streaming connections                | WebSocket APIs, billed per message and connection-minute    | Native WebSockets and gRPC               |
| Targets                                             | Lambda, HTTP endpoints, AWS services, private VPC resources | Instances, IPs, containers, Lambda       |

**Cost crossover.** API Gateway costs nothing when idle and charges per million requests; an ALB has a fixed hourly charge plus load balancer capacity units. A low-volume or bursty API is cheaper on API Gateway; a service doing thousands of requests per second all day is usually much cheaper behind an ALB. Do the arithmetic with current regional prices rather than guessing.

**Limits matter.** The 29-second integration timeout (raisable for some REST API types through a quota request) and the payload limit rule API Gateway out for large uploads and slow synchronous calls - use presigned S3 URLs or asynchronous patterns instead. Lambda behind an ALB has a smaller payload limit (1 MB), which surprises teams moving from API Gateway.

### Using both

They are not mutually exclusive. A common pattern is API Gateway as the public, managed edge for partners (keys, quotas, validation) with a **private integration** through a **VPC link** to internal services behind a load balancer, while internal or high-volume first-party traffic goes straight to the ALB. On Kubernetes, many teams now get API-management features from a gateway inside the cluster (Gateway API implementations, or a dedicated API gateway product) and use an ALB or NLB in front of it.

### Security - both are strong

Both get **Shield Standard** automatically, both terminate TLS with ACM certificates, and both can use **AWS WAF** (REST APIs and ALB directly; HTTP APIs need CloudFront in front for WAF). "API Gateway is more secure" is not a reason on its own; the reason is the API-specific controls - keys, quotas, validation and authorizers.

## Example

```bash
# API Gateway: an HTTP API in front of a Lambda function (quick create)
aws apigatewayv2 create-api --name orders-api --protocol-type HTTP \
  --target arn:aws:lambda:eu-west-1:111122223333:function:orders

# API Gateway REST API: a partner usage plan with throttling and a monthly quota
aws apigateway create-usage-plan --name partner-basic \
  --throttle burstLimit=20,rateLimit=10 \
  --quota limit=100000,period=MONTH \
  --api-stages apiId=a1b2c3d4e5,stage=prod
```

```hcl
# ALB: path-based routing to a container service, the high-volume default
resource "aws_lb_listener_rule" "orders" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 20

  condition {
    path_pattern { values = ["/orders/*"] }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.orders.arn
  }
}
```

## Interview tips

- Frame the answer as "API management versus load balancing", then give two or three features only API Gateway has (usage plans and keys, request validation, caching, authorizers) and two reasons to pick ALB (cost at sustained volume, long timeouts and connections).
- A common answer is "API Gateway when you need authentication, TLS or DDoS protection; ALB for simple internal routing". TLS, WAF, OIDC authentication and Shield Standard are available on ALB too - correct that and move to the real differentiators.
- Know the REST versus HTTP API split: HTTP APIs are cheaper but lack usage plans, caching and direct WAF association.
- Mention the integration timeout and payload limits; they decide real designs more often than features do.
- Offer the combined pattern - API Gateway for external partners, private integration to services behind a load balancer - and the cost crossover reasoning. See [what is an API gateway](../api-gateway-and-service-mesh/what-is-an-api-gateway.md), [layer 4 versus layer 7 load balancers](../scalability-and-high-availability/what-is-the-difference-between-a-layer-4-and-a-layer-7-load-balancer.md), and [how Auto Scaling groups and load balancers work together](./how-do-auto-scaling-groups-and-load-balancers-work-together-on-aws.md).

**Telling it as a STAR story** (an adaptable example)

- **Situation:** A team exposed every API through API Gateway by default, including an internal service doing several thousand requests per second around the clock, and the per-request bill had become one of the largest line items.
- **Task:** Cut cost without losing the controls partners relied on.
- **Action:** Compared per-request pricing with ALB hourly and capacity-unit pricing at the measured traffic, moved the internal high-volume service behind an ALB with path routing and WAF, and kept API Gateway REST APIs only for the partner-facing endpoints that used API keys, usage plans and request validation, integrated privately with the internal services.
- **Result:** The monthly bill for that traffic dropped substantially, partners saw no change, and the team adopted a written rule of thumb for choosing between the two.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?]] (`#407`): [How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-waiting-for-a-persistentvolumeclaim.md)
- [[What are the different types of cloud services?]] (`#25`): [What are the different types of cloud services?](../cloud-platforms/what-are-the-different-types-of-cloud-services.md)
- [[How does Cloud IAM Role Federation differ from static Service Account keys?]] (`#546`): [How does Cloud IAM Role Federation differ from static Service Account keys?](../cloud-platforms/how-does-cloud-iam-role-federation-differ-from-static-service-account-keys.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
