---
title: "What do the common HTTP status codes mean, and how do you debug a 502, 503, or 504?"
id: 507
category: "API Gateway and Service Mesh"
difficulty: "Intermediate"
tags:
  - devops
  - api-gateway-and-service-mesh
  - interview-questions
  - network-security
  - incident-management
---

# What do the common HTTP status codes mean, and how do you debug a 502, 503, or 504?

**Short answer:** The class tells you **whose fault it is**: `2xx` success, `3xx` redirection, **`4xx` the client's request is wrong**, **`5xx` the server failed**. The ones you will actually debug are the 5xx family from a proxy, and they are distinguishable: **502 Bad Gateway** means the proxy reached the backend and got an invalid or empty response (the backend crashed, closed the connection, spoke the wrong protocol, or returned malformed headers); **503 Service Unavailable** means the proxy had **no healthy backend to send to** (all targets failing health checks, no endpoints, the pool is empty, or a rate limiter or circuit breaker is shedding load); **504 Gateway Timeout** means the backend accepted the request but did not respond within the proxy's timeout. So the diagnostic shortcut is: **502 = the backend answered badly, 503 = nothing to answer, 504 = answered too slowly.** Then the debugging order is always the same - reproduce with `curl -v`, read the proxy's access log for the upstream status and timing fields, check backend health and endpoints, then look at the backend's own logs and timeouts.

## Detail

### The codes worth knowing, and what each one usually means operationally

| Code                          | Meaning                                                    | What it usually indicates in production                                                                                                                                        |
| ----------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `200` / `201` / `204`         | OK / Created / No Content                                  | -                                                                                                                                                                              |
| `301` / `302` / `307` / `308` | Moved permanently / found / temporary / permanent redirect | An HTTP→HTTPS redirect loop is the classic bug: the load balancer terminates TLS and the app still thinks it is on HTTP, so it redirects forever. Fix with `X-Forwarded-Proto` |
| `304 Not Modified`            | Cache validation succeeded                                 | Normal and desirable                                                                                                                                                           |
| `400 Bad Request`             | Malformed request                                          | Often a WAF or proxy rejecting a bad header, or a body too large                                                                                                               |
| `401 Unauthorized`            | **Not authenticated**                                      | Missing or invalid credentials/token                                                                                                                                           |
| `403 Forbidden`               | **Authenticated but not permitted**                        | Authorisation, a WAF rule, an S3 bucket policy, or IP allowlisting. `401` = who are you; `403` = I know who you are and no                                                     |
| `404 Not Found`               | No route matched                                           | A path-routing rule that matches nothing, a missing ingress rule, or the app's own router. Note a proxy can emit 404 before the backend is ever consulted                      |
| `405` / `415` / `422`         | Method / media type / semantics                            | API contract mismatches                                                                                                                                                        |
| `413`                         | Payload too large                                          | Proxy body-size limit (`client_max_body_size`, ALB limits)                                                                                                                     |
| `429 Too Many Requests`       | Rate limited                                               | Your limiter, or an upstream API limiting **you**. Should carry `Retry-After`                                                                                                  |
| `499`                         | Client closed the request (nginx-specific)                 | The client gave up before the backend answered - usually a symptom of slowness, not a cause                                                                                    |
| `500 Internal Server Error`   | The **application** threw                                  | An unhandled exception. The stack trace is in the app's logs, not the proxy's                                                                                                  |
| **`502 Bad Gateway`**         | Invalid response from upstream                             | Backend crashed mid-request, closed the connection, wrong protocol (HTTP sent to an HTTPS port), or an untrusted certificate on the backend leg                                |
| **`503 Service Unavailable`** | No healthy upstream                                        | All targets unhealthy, zero endpoints, an empty target group, maintenance mode, or deliberate load shedding                                                                    |
| **`504 Gateway Timeout`**     | Upstream too slow                                          | The backend is slow or hung; the proxy's timeout is shorter than the backend's work                                                                                            |
| `501 Not Implemented`         | Method not supported by the server                         | Rare; usually a proxy or a minimal server rejecting a method such as `PATCH`                                                                                                   |
| `507` / `508`                 | Insufficient storage / loop detected                       | Rare, WebDAV-era                                                                                                                                                               |

The `401` versus `403` distinction and the `502`/`503`/`504` split are the two things interviewers reliably test, because both reveal whether you understand the layers or are guessing.

### Debugging in order - and it is the same order every time

**1. Reproduce and see the full exchange.**

```bash
curl -sS -o /dev/null -D - -w '\ncode=%{http_code} dns=%{time_namelookup} tcp=%{time_connect} \
tls=%{time_appconnect} ttfb=%{time_starttransfer} total=%{time_total}\n' https://api.example.com/orders
```

The timing breakdown tells you immediately whether the delay is DNS, TCP, TLS, or the backend thinking. If `ttfb` is close to the proxy's timeout, you are looking at a 504 cause.

**2. Read the proxy's access log with the upstream fields.** This is the step that answers the question, and most teams have not configured the fields. You want the **upstream status**, **upstream response time**, and **which upstream** was tried:

- nginx: `$upstream_status $upstream_addr $upstream_response_time $request_time`.
- ALB access logs: `target_status_code`, `elb_status_code`, `target_processing_time`, and the `-` in `target_status_code` meaning the target never responded.
- Envoy/Istio: `%RESPONSE_CODE% %RESPONSE_FLAGS%` - and the response flags are gold (`UH` no healthy upstream, `UF` upstream connection failure, `UT` upstream timeout, `URX` retry limit exceeded, `NR` no route).

An `elb_status_code` of 502 with `target_status_code` of `-` proves the backend never returned a valid response; a 504 with a `target_processing_time` equal to your idle timeout proves it was too slow.

**3. Check whether there is a healthy backend at all.** For 503 this is nearly always the answer:

```bash
aws elbv2 describe-target-health --target-group-arn "$TG" \
  --query 'TargetHealthDescriptions[].[Target.Id,TargetHealth.State,TargetHealth.Reason]' --output table
kubectl get endpointslice -l kubernetes.io/service-name=payments -o wide   # empty? that is your 503
kubectl get pods -l app=payments -o wide                                    # Ready, or just Running?
```

In Kubernetes, "no endpoints" comes from a **selector mismatch** or a **failing readiness probe** - and the second is the more common. A Pod that is `Running` but not `Ready` is deliberately removed from the Service, which is correct behaviour producing a 503.

**4. Then look at the backend.** For 500 and 502 the cause is in the application's logs: an unhandled exception, an OOM kill mid-request (exit 137), a worker crash, or a connection reset. For 504, look at what the request is waiting on - a slow query, an exhausted connection pool, a downstream API with no timeout of its own.

### The specific causes, by code

**502 Bad Gateway**

- Backend process crashed or restarted mid-request (check for `OOMKilled`, exit 137, or a rolling deploy at that moment).
- **Protocol mismatch**: the proxy speaks HTTP to a port expecting HTTPS, or HTTP/2 to a backend that only does HTTP/1.1.
- **Certificate not trusted** on the backend leg when using end-to-end TLS.
- Response headers too large for the proxy's buffer (a common one with big JWTs in headers - raise `proxy_buffer_size`).
- **Keep-alive mismatch**: the backend's idle timeout is _shorter_ than the proxy's, so the proxy reuses a connection the backend has already closed. Always make the backend's keep-alive timeout **longer** than the load balancer's idle timeout - this is a genuinely common and hard-to-spot 502 source.

**503 Service Unavailable**

- All targets failing health checks - check the health-check **path, port, host header, and expected status code**, because a probe hitting `/` when the app serves `/healthz`, or expecting 200 when the app returns 302, marks a perfectly healthy backend as down.
- Zero endpoints: selector mismatch, readiness failing, or the Deployment scaled to zero.
- **Health check grace period shorter than startup time**, so instances or Pods are killed before they can pass - a replacement loop that presents as intermittent 503s.
- Deliberate shedding: rate limiting, a circuit breaker, an Envoy `UH`/overflow, or `maxSurge`/`maxUnavailable` leaving too little capacity mid-rollout.
- A missing route or listener rule (in some proxies this surfaces as 503 rather than 404).

**504 Gateway Timeout**

- The backend is slow: an unindexed query, a lock, a saturated thread or connection pool, or a synchronous call to a slow third party.
- **Timeout ladder inverted**: the client's timeout is shorter than the proxy's, which is shorter than the backend's, so somebody always gives up first and retries pile on. The rule is that timeouts should **decrease** as you go deeper - and each layer's timeout must be shorter than its caller's.
- No timeout at all on an outbound call, so one hung dependency consumes every worker.
- Long-running requests that should not be synchronous at all - the fix is a 202 plus a job and a status endpoint, not a bigger timeout.

### The related debugging questions

**"The deployment succeeded but the application returns 404"** - the Pods are fine and the routing is wrong. Check the ingress host and path rules, whether the path is rewritten (the backend may expect `/` where the ingress forwards `/api/`), the Service port versus `targetPort`, and the application's own base path. A 404 from the proxy versus a 404 from the app are different problems: the response headers (`Server`, or a proxy-specific header) tell you which one answered.

**"403 for external users, 200 for internal"** - something is deciding based on origin: a WAF rule or geo-block, an IP allowlist on the load balancer or bucket policy, an internal-only auth path (a header injected by the internal proxy), a CDN origin-restriction header, or split-horizon DNS sending the two groups to different endpoints. Compare the two requests header by header; the difference is the cause.

**"Clients report 504s intermittently"** - intermittent means capacity or a specific slow path, not a total failure. Correlate the 504s with p99 latency, pool saturation, GC pauses, and a specific endpoint or tenant; a single slow query on one code path will produce exactly this.

### What to do while you are debugging

Mitigate before you have the root cause: shift traffic away from the failing version, scale out if it is a capacity problem, raise the timeout **temporarily** if that stops user-visible errors while you fix the slow query, and shed load with 429 plus `Retry-After` rather than letting everything time out. Retries need care - retrying a 504 amplifies load on an already-slow backend, so retries must be bounded, jittered, and only on idempotent requests, with a circuit breaker so a struggling dependency is not hammered.

## Example

```bash
# 1. See the whole exchange and where the time goes
curl -sS -o /dev/null -D - -w '\ncode=%{http_code} tcp=%{time_connect} tls=%{time_appconnect} \
ttfb=%{time_starttransfer} total=%{time_total}\n' -H 'Host: api.example.com' \
  https://api.example.com/orders/123

# 502? bypass the proxy and hit the backend directly - does IT answer correctly?
kubectl run probe --rm -it --image=nicolaka/netshoot -- \
  curl -sS -m 5 -o /dev/null -w '%{http_code}\n' http://payments.prod.svc.cluster.local:8080/healthz
```

```nginx
# 2. Log the upstream fields, or you are debugging blind
log_format upstream '$remote_addr "$request" status=$status '
                    'upstream=$upstream_addr up_status=$upstream_status '
                    'up_time=$upstream_response_time req_time=$request_time '
                    'proto=$http_x_forwarded_proto';
access_log /var/log/nginx/access.log upstream;

# and the two settings that cause 502s
proxy_buffer_size   16k;    # big JWT headers overflow the default buffer
proxy_buffers       8 16k;
keepalive_timeout   75s;    # MUST be longer than the load balancer's idle timeout
proxy_read_timeout  30s;    # shorter than the client's timeout, longer than p99
```

```bash
# 3. 503: is there anything healthy to route to?
kubectl get endpointslice -l kubernetes.io/service-name=payments -o yaml | grep -A3 addresses
kubectl get pods -l app=payments -o custom-columns=\
'NAME:.metadata.name,READY:.status.containerStatuses[*].ready,RESTARTS:.status.containerStatuses[*].restartCount'
kubectl describe pod -l app=payments | grep -A5 'Readiness\|Liveness'   # probe path/port right?

aws elbv2 describe-target-health --target-group-arn "$TG" \
  --query 'TargetHealthDescriptions[].[Target.Id,TargetHealth.State,TargetHealth.Reason,
           TargetHealth.Description]' --output table
```

```bash
# 4. Istio/Envoy response flags name the cause outright
kubectl logs -n istio-system deploy/istio-ingressgateway --tail=200 \
  | grep -E '"(502|503|504)"' | awk '{print $2, $12}' | sort | uniq -c
#  UH  = no healthy upstream        -> 503, check endpoints and readiness
#  UF  = upstream connection failure -> 502, backend refused or reset
#  UT  = upstream timeout            -> 504, backend too slow
#  URX = retry limit exceeded        -> retries amplifying the problem
#  NR  = no route configured         -> routing, not the backend

# ALB access logs in Athena: elb_status_code vs target_status_code is the whole answer
#   SELECT elb_status_code, target_status_code, count(*) AS n,
#          approx_percentile(target_processing_time, 0.99) AS p99
#   FROM alb_logs WHERE time > '2026-08-10T00:00:00Z'
#   GROUP BY 1,2 ORDER BY n DESC;
#   target_status_code = '-'  ->  the target never returned a valid response (502/504)
```

```text
The timeout ladder - get this wrong and you generate your own 504s

  client                 30s   ─┐
    CDN / edge           25s    │  each layer's timeout must be SHORTER
      load balancer      20s    │  than its caller's, so the innermost
        app server       15s    │  layer fails first and the error is
          DB query        5s   ─┘  attributable rather than a mystery
          outbound API    3s + 2 bounded, jittered retries + circuit breaker

  Inverted ladders produce: retry storms, phantom 504s at the edge while the
  backend is still working, and duplicate side effects from non-idempotent retries.
```

## Interview tips

- Lead with the class semantics - `4xx` is the client's fault, `5xx` is the server's - then give the three-way split that answers the real question: **502 the backend answered badly, 503 nothing to answer, 504 answered too slowly**. That single sentence is the most useful thing you can say here.
- Distinguish `401` from `403` precisely: not authenticated versus authenticated but not permitted. It is asked constantly and often fumbled.
- Give a fixed debugging order and stick to it: reproduce with `curl -v` and the timing breakdown, read the proxy log's **upstream** fields, check backend health and endpoints, then the application's own logs.
- Name the fields that actually resolve it - nginx's `$upstream_status`/`$upstream_response_time`, the ALB's `target_status_code` being `-`, and Envoy's `UH`/`UF`/`UT` response flags. Knowing the flags is a strong differentiator.
- For 503 in Kubernetes, go straight to endpoints and readiness: a `Running` but not `Ready` Pod is removed from the Service by design, and a health check probing the wrong path or expecting the wrong status marks healthy backends down.
- Volunteer the **keep-alive mismatch** 502 cause - the backend closing idle connections sooner than the load balancer reuses them - because it is common, subtle, and almost nobody mentions it.
- Draw the **timeout ladder** and state the rule that timeouts decrease with depth. Then add that retrying a 504 amplifies load, so retries must be bounded, jittered, idempotent-only, and paired with a circuit breaker.
- For "deployment succeeded but I get a 404", say it is routing rather than the workload - ingress host/path rules, path rewriting, `targetPort`, and the app's base path - and note that you can tell a proxy 404 from an application 404 by the response headers. See [what is an API gateway](./what-is-an-api-gateway.md), [debugging a Kubernetes Ingress that is not routing traffic](../kubernetes/how-do-you-debug-a-kubernetes-ingress-that-is-not-routing-traffic.md), [troubleshooting a load balancer returning 5xx errors](../scalability-and-high-availability/how-do-you-troubleshoot-a-load-balancer-returning-5xx-errors-or-sending-traffic-unevenly.md), [troubleshooting high latency in a microservices architecture](../cloud-native-architecture/how-do-you-troubleshoot-high-latency-in-a-microservices-architecture.md), and [a Service that has no endpoints](../kubernetes/how-do-you-troubleshoot-a-kubernetes-service-that-has-no-endpoints.md).

---

[⬅ Back to API Gateway and Service Mesh](./README.md) · [All topics](../README.md)
