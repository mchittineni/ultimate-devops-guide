---
title: "What is the difference between a layer 4 and a layer 7 load balancer?"
id: 269
category: "Scalability and High Availability"
difficulty: "Intermediate"
tags:
  - devops
  - scalability-and-high-availability
  - interview-questions
---

# What is the difference between a layer 4 and a layer 7 load balancer?

**Short answer:** A layer 4 load balancer forwards TCP/UDP connections based only on IP and port - it never reads the payload, so it is fast, protocol-agnostic, and cheap. A layer 7 load balancer terminates the connection, parses the HTTP request, and can route on host, path, header, or cookie, at the cost of latency and CPU. On AWS that maps to NLB versus ALB; the same split exists on every cloud.

## Detail

**Layer 4 - the transport layer.** The balancer sees a connection, picks a backend, and forwards packets. It cannot see the URL because it never decrypts or parses anything. Consequences:

- Extremely low latency and very high throughput; handles millions of connections.
- Works for **any** TCP or UDP protocol - databases, MQTT, gRPC streaming, game servers, SMTP.
- Can preserve the client's source IP directly, which simplifies allow-listing.
- Cannot do path-based routing, header-based routing, or per-request retries.
- Health checks are shallow: "does the port accept a connection?", not "does `/healthz` return 200?"

**Layer 7 - the application layer.** The balancer terminates TLS, reads the HTTP request, and makes a decision per _request_ rather than per _connection_. That unlocks:

- Host and path routing (`api.acme.com/v2/*` to one target group, `/static/*` to another).
- Header, cookie, and query-string matching - the basis for canary releases and A/B tests.
- Weighted traffic splitting for blue/green and canary deployments.
- Request-level retries, timeouts, redirects, and rewrites.
- Deep health checks against a real endpoint.
- WAF integration and authentication at the edge (OIDC, mTLS termination).
- Response compression and HTTP/2 or HTTP/3 termination in front of HTTP/1.1 backends.

Because it terminates the connection, the backend sees the balancer's IP - the original client IP arrives in `X-Forwarded-For` or the PROXY protocol, and forgetting that breaks rate limiting and audit logs.

|                   | Layer 4                               | Layer 7                                    |
| ----------------- | ------------------------------------- | ------------------------------------------ |
| Decision unit     | Connection                            | Request                                    |
| Sees payload      | No                                    | Yes                                        |
| Protocols         | Any TCP/UDP                           | HTTP/HTTPS, gRPC, WebSocket                |
| TLS               | Passthrough or termination            | Termination (usually)                      |
| Latency           | Lowest                                | Higher (parsing + termination)             |
| Routing           | IP + port                             | Host, path, header, cookie, weight         |
| Client IP         | Preserved                             | Via `X-Forwarded-For`                      |
| AWS / Azure / GCP | NLB / Load Balancer / Passthrough NLB | ALB / Application Gateway / Application LB |

**Choosing between them.** Use layer 7 for anything HTTP - it is the default for web traffic and everything a microservice architecture needs. Use layer 4 when the protocol is not HTTP, when you need the absolute lowest latency, when you need true TLS passthrough for end-to-end encryption or client-certificate authentication at the application, or when you need a static IP. A common production pattern is both: an NLB with a static IP fronting an NGINX or Envoy ingress layer that does the layer 7 work.

**Algorithms** differ by layer too. Layer 4 typically uses round robin or a 5-tuple hash (which naturally gives connection affinity). Layer 7 can use least outstanding requests - usually the better choice, because it accounts for slow backends that round robin keeps feeding.

**Where Kubernetes fits.** `kube-proxy` and a `LoadBalancer` Service are effectively layer 4. An Ingress controller or a Gateway API implementation is layer 7 running inside the cluster. A service mesh sidecar is a per-Pod layer 7 proxy. Knowing which layer each abstraction operates at is what lets you answer "why can I not do path routing with a Service?"

## Example

```hcl
# Layer 7: ALB routing by path, with a weighted canary.
resource "aws_lb" "app" {
  name               = "app-alb"
  load_balancer_type = "application" # layer 7
  subnets            = var.public_subnet_ids
}

resource "aws_lb_listener_rule" "api_v2" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 10

  condition {
    path_pattern { values = ["/v2/*"] } # impossible at layer 4
  }

  action {
    type = "forward"
    forward {
      target_group { arn = aws_lb_target_group.stable.arn, weight = 90 }
      target_group { arn = aws_lb_target_group.canary.arn, weight = 10 }
    }
  }
}

# Deep health check - a real endpoint, not just an open port.
resource "aws_lb_target_group" "stable" {
  port     = 8080
  protocol = "HTTP"
  vpc_id   = var.vpc_id

  health_check {
    path                = "/healthz"
    matcher             = "200"
    interval            = 15
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }
}
```

```hcl
# Layer 4: NLB for a non-HTTP protocol, with a static IP and TLS passthrough.
resource "aws_lb" "mqtt" {
  name               = "mqtt-nlb"
  load_balancer_type = "network" # layer 4
  subnets            = var.public_subnet_ids
}

resource "aws_lb_listener" "mqtt" {
  load_balancer_arn = aws_lb.mqtt.arn
  port              = 8883
  protocol          = "TCP" # passthrough - the broker terminates TLS itself
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.mqtt.arn
  }
}
```

## Interview tips

- The one-line distinction: **layer 4 routes connections on IP and port; layer 7 routes requests on their content.** Everything else follows from that.
- Give the concrete capability layer 4 cannot provide - path-based routing - rather than saying "it is less flexible."
- Name the cloud equivalents. "NLB versus ALB" is often how the question is actually phrased.
- Volunteering `X-Forwarded-For` shows operational experience: at layer 7 the backend loses the real client IP unless you handle it.
- Know the legitimate reasons to pick layer 4 in 2026: non-HTTP protocols, static IPs, true TLS passthrough, and lowest latency. "Layer 7 is always better" is the wrong answer.
- Expect a follow-up connecting this to Kubernetes: a `LoadBalancer` Service is layer 4, an Ingress or Gateway is layer 7.
- Least-outstanding-requests over round robin is a good detail if algorithms come up - round robin keeps feeding a slow backend.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scalability and High Availability](./README.md) · [All topics](../README.md)
