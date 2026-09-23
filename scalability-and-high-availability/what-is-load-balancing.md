---
title: "What is Load Balancing?"
id: 58
category: "Scalability and High Availability"
difficulty: "Beginner"
tags:
  - devops
  - scalability-and-high-availability
  - interview-questions
---

# What is Load Balancing?

**Short answer:** Load balancing distributes incoming traffic across multiple backend instances, improving throughput and availability by routing only to healthy targets and removing failed ones automatically.

## Detail

**Layer 4 vs Layer 7.** L4 balancers (AWS NLB, IPVS) forward TCP/UDP based on IP and port - extremely fast, protocol-agnostic, but blind to content. L7 balancers (ALB, NGINX, HAProxy, Envoy) understand HTTP, enabling path- and header-based routing, TLS termination, retries, and request-level observability, at slightly higher latency.

**Algorithms**

- **Round robin** - simple rotation; fine when requests are uniform.
- **Weighted round robin** - for heterogeneous backend sizes.
- **Least connections** - sends to the least busy backend; better for long-lived or variable requests.
- **Least response time** - factors in latency.
- **IP hash / consistent hashing** - same client to the same backend, important for cache locality; consistent hashing minimises reshuffling when the pool changes.
- **Random with two choices** - surprisingly effective and cheap at scale.

**Health checks** are the mechanism that turns a load balancer into an availability tool: active probes (periodic requests to `/healthz`) and passive checks (observing real request failures). A check that returns 200 unconditionally proves little, but one that calls a shared dependency (the database) is worse: when that dependency slows, every instance fails at once and the balancer removes the whole pool. Check what is local to the instance - the process is up, warmed, and able to serve - and handle dependency failure with timeouts and degradation instead.

**Other responsibilities** commonly handled at this layer: TLS termination, HTTP/2 and gRPC support, sticky sessions (avoid if you can - they undermine even distribution), connection draining during deploys, rate limiting, and WAF integration.

**Global load balancing** uses DNS or anycast to route users to the nearest healthy region.

## Example

```nginx
upstream api {
    least_conn;
    server 10.0.1.10:8080 max_fails=3 fail_timeout=30s;
    server 10.0.1.11:8080 max_fails=3 fail_timeout=30s;
    server 10.0.1.12:8080 backup;
    keepalive 32;
}

server {
    listen 443 ssl;
    http2 on;                      # nginx >= 1.25.1; "listen ... http2" is deprecated
    ssl_certificate     /etc/nginx/tls/api.crt;
    ssl_certificate_key /etc/nginx/tls/api.key;

    location / {
        proxy_http_version 1.1;    # needed for upstream keepalive
        proxy_set_header Connection "";
        proxy_pass http://api;
        proxy_next_upstream error timeout http_502 http_503;
        proxy_connect_timeout 2s;
        proxy_read_timeout 10s;
    }
}
```

## Interview tips

- The L4/L7 distinction is asked almost every time - have a one-line answer plus an example of each.
- Deep versus shallow health checks is a great detail to raise unprompted - and know why a health check that calls the database can take out the whole pool.
- Connection draining during deployments is what turns load balancing into zero-downtime deployment.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is progressive delivery and how does it differ from traditional deployment strategies?]] (`#509`): [What is progressive delivery and how does it differ from traditional deployment strategies?](../core-devops-concepts/what-is-progressive-delivery-and-how-does-it-differ-from-traditional-deployment-strategies.md)
- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)
- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scalability and High Availability](./README.md) · [All topics](../README.md)
