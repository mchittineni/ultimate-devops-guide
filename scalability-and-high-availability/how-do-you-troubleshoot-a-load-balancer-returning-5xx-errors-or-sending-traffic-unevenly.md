---
title: "How do you troubleshoot a load balancer returning 5xx errors or sending traffic unevenly?"
id: 419
category: "Scalability and High Availability"
difficulty: "Advanced"
tags:
  - devops
  - scalability-and-high-availability
  - interview-questions
  - network-security
  - incident-management
  - api-gateway-and-service-mesh
---

# How do you troubleshoot a load balancer returning 5xx errors or sending traffic unevenly?

**Short answer:** First establish **who generated the error** - the load balancer or the backend - because the fix is entirely different, and every cloud load balancer gives you this in its metrics and access logs (`HTTPCode_ELB_5XX` versus `HTTPCode_Target_5XX` on AWS, `elb_status_code` versus `target_status_code` per request). Then decode the code: **503 = no healthy targets** (health checks, deregistration, or scaling), **502 = the backend answered badly** (crash, malformed response, protocol or TLS mismatch, or a keep-alive timeout shorter than the load balancer's idle timeout), **504 = the backend was too slow** (timeout tuning or genuine saturation), **500 from the load balancer itself** = configuration. For uneven traffic, the usual causes are **sticky sessions**, **long-lived connections with connection-based balancing**, **cross-zone balancing disabled**, or **DNS-level caching** pinning clients to one node.

## Detail

### Step 1: attribute the error

Enable and read the access log. One line per request tells you the client, the target chosen, the load-balancer status, the target status, and the three timing fields (request, target, response). That is usually the whole investigation:

- `elb_status_code 502`, `target_status_code -` → the backend never returned a valid response.
- `elb_status_code 503`, `target -` → no healthy target was available to pick.
- `elb_status_code 504` with `target_processing_time` at exactly your idle timeout → the backend exceeded the timeout.
- Both codes 500 → the application genuinely returned 500 and the load balancer faithfully passed it on. Stop looking at the load balancer.

### Step 2: decode by status code

**503 - no healthy targets.** Check the target group health, then _why_ targets are failing the health check. Recurring causes: the health-check path requires authentication or hits a dependency and so fails when the dependency is slow (health checks should be shallow - liveness, not a full dependency check); the health-check port or protocol is wrong; the security group does not allow the load balancer's subnet to reach the target port; the check is too aggressive for a slow-starting application (raise the healthy threshold, or use a slow-start/warm-up period); or the targets are genuinely all unhealthy because of a bad deploy. Also check whether a scaling event deregistered too many at once, and whether deregistration delay (connection draining) is long enough for in-flight requests.

**502 - bad gateway.** The backend accepted the connection and then failed: it crashed mid-request, returned a malformed or oversized header, spoke HTTPS while the target group expects HTTP (or vice versa), presented an untrusted certificate on an HTTPS target group, or - the subtle one - **closed a keep-alive connection the load balancer still believed was open**. That last case is the classic intermittent 502: your application's keep-alive timeout must be **longer** than the load balancer's idle timeout (AWS ALB defaults to 60 s, so set the application to 65-75 s), or you will see a small, unexplained, permanent 502 rate.

**504 - gateway timeout.** Either the load balancer's idle timeout is shorter than a legitimately slow endpoint (raise it deliberately for that route, or make the endpoint asynchronous) or the backend is saturated - queueing, connection-pool exhaustion, or a slow dependency. Check target response time percentiles and target queue depth rather than averages. See [how do you troubleshoot a database that is slow or timing out under load](../database-management-in-devops/how-do-you-troubleshoot-a-database-that-is-slow-or-timing-out-under-load.md).

**Capacity of the load balancer itself.** A very sudden spike can outpace an ALB/NLB's scaling; on AWS the tell is a rise in `SurgeQueueLength`/rejected connections or `HTTPCode_ELB_5XX` with healthy targets. Pre-warm or use an architecture that absorbs bursts (CloudFront in front, or scheduled scaling before a known event).

### Step 3: uneven distribution

Even distribution is not the default in as many cases as people assume:

- **Sticky sessions** pin a client to one target for the cookie's lifetime, so a few heavy clients create hot targets. Remove stickiness by externalising session state (Redis or a database) - the durable fix.
- **Long-lived connections with connection-level balancing.** A layer 4 balancer distributes _connections_, not requests, so gRPC, HTTP/2, and WebSocket clients that open one connection and multiplex thousands of requests will hammer whichever target they landed on. The fix is a layer 7 balancer, request-level load balancing (a service mesh or a client-side load balancer), or periodic connection recycling (`max_connection_age`). See [what is the difference between a layer 4 and a layer 7 load balancer](./what-is-the-difference-between-a-layer-4-and-a-layer-7-load-balancer.md).
- **Cross-zone load balancing disabled** (the default for NLB and for Kubernetes `externalTrafficPolicy: Local`). With 2 targets in one zone and 8 in another, each zone still receives ~50% of traffic, so the two targets are overloaded. Enable cross-zone balancing, or keep the target count balanced per zone.
- **DNS-level and client caching.** Clients that resolve the load balancer's DNS once and cache the IP (some JVM defaults, or a proxy with a long TTL cache) pin themselves to one load-balancer node.
- **Algorithm mismatch.** Round-robin is unfair when request cost varies wildly; least-outstanding-requests handles heterogeneous work far better. And uneven **target capacity** - a mixed instance-type target group - looks like an algorithm bug but is a placement bug.
- **Keep-alive plus round-robin** is a real subtlety: connections are balanced, and if some connections are far busier than others, the request distribution is not.

### After the incident

Fix the configuration, then remove the class: shallow health checks that do not cascade dependency failures, keep-alive timeouts ordered correctly (application > load balancer), deregistration delay matched to your longest request, cross-zone balancing on, load-balancer configuration managed in Terraform so a manual change cannot cause the next outage (and so the revert is a `git revert`), and dashboards that separate load-balancer 5xx from target 5xx as first-class metrics. Alert on the ratio, not the count. See [how do you run a major incident as incident commander](../incident-management/how-do-you-run-a-major-incident-as-incident-commander.md) and [how do you design a system to degrade gracefully under overload](./how-do-you-design-a-system-to-degrade-gracefully-under-overload.md).

## Example

```text
ALB access log - one line answers "who generated the error?"

https 2026-08-10T09:14:02 app/prod-alb/2f1 203.0.113.9:54233 10.0.3.17:8080
  0.001 0.061 -1  502 -   "GET https://shop.example.com/api/cart HTTP/2.0"
        ^      ^   ^   ^
        |      |   |   target_status_code "-"  -> backend returned nothing valid
        |      |   elb_status_code 502
        |      response_processing_time -1     -> connection closed before response
        target_processing_time 0.061           -> backend was FAST, so not overload

Diagnosis: keep-alive race. App keep-alive 5s < ALB idle timeout 60s, so the ALB
reuses a connection the app has already closed. Fix: app keep-alive 75s > ALB 60s.
502 rate 0.4% -> 0.00%.
```

```bash
# Who is generating the 5xx - the load balancer or the targets?
aws cloudwatch get-metric-statistics --namespace AWS/ApplicationELB \
  --metric-name HTTPCode_ELB_5XX_Count --period 60 --statistics Sum \
  --dimensions Name=LoadBalancer,Value=app/prod-alb/2f1 --start-time ... --end-time ...
# repeat with HTTPCode_Target_5XX_Count - the two together localise the fault

# Why are targets unhealthy? The reason string is explicit.
aws elbv2 describe-target-health --target-group-arn "$TG" \
  --query 'TargetHealthDescriptions[?TargetHealth.State!=`healthy`].[Target.Id,TargetHealth.State,TargetHealth.Reason,TargetHealth.Description]' --output table
# i-0abc  unhealthy  Target.Timeout  "Request timed out"        <- slow or wrong path
# i-0def  unhealthy  Target.FailedHealthChecks                   <- app returning non-200

# Is the health check path even reachable and cheap? Test it as the LB does.
curl -s -o /dev/null -w '%{http_code} %{time_total}s\n' http://10.0.3.17:8080/healthz

# Uneven traffic: is it stickiness, zone imbalance, or connection-level balancing?
aws elbv2 describe-target-group-attributes --target-group-arn "$TG" \
  --query 'Attributes[?contains(Key,`stickiness`)||contains(Key,`cross_zone`)||contains(Key,`deregistration`)]'
```

```hcl
# The settings that prevent most of the above - managed as code, not by hand
resource "aws_lb" "prod" {
  idle_timeout                     = 60    # app keep-alive MUST exceed this
  enable_cross_zone_load_balancing = true  # off by default on NLB: causes zone skew
  access_logs { bucket = aws_s3_bucket.lb_logs.id, enabled = true }  # non-negotiable
}

resource "aws_lb_target_group" "api" {
  port                 = 8080
  protocol             = "HTTP"
  deregistration_delay = 45                # >= longest in-flight request
  slow_start           = 30                # ramp traffic into cold targets

  health_check {
    path                = "/healthz"       # shallow: no DB, no downstream calls
    healthy_threshold   = 2
    unhealthy_threshold = 3                # not 2 - avoid flapping on one blip
    timeout             = 3
    interval            = 10
    matcher             = "200"
  }
  stickiness { enabled = false, type = "lb_cookie" }  # externalise session state
}
```

## Interview tips

- The first move is attribution: load-balancer 5xx versus target 5xx. Say that you would read the access log and the two separate metrics before touching anything.
- Have the code mapping fluent - 503 no healthy targets, 502 bad backend response, 504 too slow, and know that a 500 with a matching target status is simply the application's own error.
- The keep-alive ordering rule (application keep-alive > load-balancer idle timeout) is the single best detail to volunteer. It explains a persistent low-rate 502 that teams often live with for years.
- Say that health checks must be shallow. A health check that calls the database converts a slow dependency into "all targets unhealthy" and a total outage - a genuinely instructive failure.
- For uneven traffic, give the four causes with mechanisms: stickiness, connection-level balancing with multiplexed protocols (gRPC/HTTP/2), cross-zone balancing off, and client-side DNS caching.
- Mention `deregistration_delay` and `slow_start` as the deploy-time settings that stop rolling deployments producing 5xx blips.
- Close on prevention: load-balancer configuration in Terraform, access logs always on, dashboards that split the two 5xx families, and alerting on ratio rather than count.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you troubleshoot Docker networking between containers?]] (`#415`): [How do you troubleshoot Docker networking between containers?](../docker/how-do-you-troubleshoot-docker-networking-between-containers.md)
- [[How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?]] (`#402`): [How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?](../cicd/how-do-you-troubleshoot-a-jenkins-pipeline-that-never-starts-or-hangs-in-the-queue.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scalability and High Availability](./README.md) · [All topics](../README.md)
