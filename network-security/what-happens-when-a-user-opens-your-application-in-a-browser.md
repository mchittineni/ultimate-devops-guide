---
title: "What happens when a user opens your application in a browser?"
id: 270
category: "Network Security"
difficulty: "Intermediate"
tags:
  - devops
  - network-security
  - interview-questions
---

# What happens when a user opens your application in a browser?

**Short answer:** DNS resolves the hostname to an IP, the browser opens a TCP connection (or QUIC for HTTP/3) and completes a TLS handshake, the HTTP request travels through CDN, load balancer, and ingress to a Pod or instance, the application responds, and the browser renders it. The reason interviewers ask is that every layer is a place things break - and your answer maps directly onto how you would debug a real outage.

## Detail

**1. DNS resolution.** The browser checks its own cache, then the OS cache, then asks the configured resolver. If nothing is cached, the resolver walks root → TLD → authoritative nameserver. The record type matters: `A`/`AAAA` for an IP, `CNAME` for an alias, and on AWS an `ALIAS` record which resolves like a CNAME but works at the zone apex. TTL determines how long a change takes to propagate - which is why DNS-based failover is measured in minutes, not seconds, and why you lower TTL _before_ a planned cutover.

**2. TCP connection (three-way handshake).** `SYN` → `SYN-ACK` → `ACK`, one round trip before any data. Geographic distance is unavoidable latency here, which is the entire argument for a CDN or edge presence. HTTP/3 replaces TCP with QUIC over UDP and folds the transport and TLS handshakes together.

**3. TLS handshake.** The client offers cipher suites and a key share; the server picks one and returns its certificate chain. The client validates the chain to a trusted root, checks expiry, hostname (SAN), and revocation, then both derive a session key. TLS 1.3 completes in one round trip, and zero with session resumption. Modern browsers negotiate a post-quantum hybrid key exchange (`X25519MLKEM768`) by default. SNI is what lets one IP serve many certificates - it is sent in the clear, which is how a load balancer knows which certificate to present.

**4. Edge and CDN.** If a CDN is in front, it may serve the response from cache and never contact your origin at all. Cache hit ratio, cache keys, and `Cache-Control` headers live here; so do WAF rules, bot filtering, and DDoS absorption.

**5. Load balancing.** A layer 7 load balancer terminates TLS, parses the request, matches it against host and path rules, and forwards to a healthy target - adding `X-Forwarded-For` so the backend can still see the client IP. Unhealthy targets are excluded by health checks.

**6. Inside the cluster.** An ingress controller or Gateway routes to a Service; the Service resolves through EndpointSlices to a Pod IP; `kube-proxy` (iptables/IPVS) or a CNI's eBPF datapath does the actual forwarding. A Pod that fails its readiness probe is not in the EndpointSlice, so it receives nothing. NetworkPolicies may drop the packet here.

**7. The application, and everything behind it.** The request hits your handler, which likely calls a database, a cache, and two other services. Connection pool exhaustion, N+1 queries, and slow downstream dependencies show up as latency at this layer. Distributed tracing exists precisely to attribute time across these hops.

**8. The response and rendering.** Status code, headers, body. Security headers are set here or at the edge: `Strict-Transport-Security`, `Content-Security-Policy`, `X-Content-Type-Options`, and cookie flags (`HttpOnly`, `Secure`, `SameSite`).

**Turning this into a debugging method.** The value of the walkthrough is that a symptom points at a layer:

| Symptom                     | Likely layer                                                                                   |
| --------------------------- | ---------------------------------------------------------------------------------------------- |
| `NXDOMAIN`, or the wrong IP | DNS - record, TTL, or split-horizon                                                            |
| Connection times out        | Security group / NACL / firewall / routing                                                     |
| Connection refused          | Nothing listening, or the wrong port                                                           |
| Certificate error           | Expiry, wrong SAN, incomplete chain, SNI mismatch                                              |
| 502 / 503                   | No healthy backends - readiness probes or crashed Pods                                         |
| **504**                     | Backend accepted the request but did not answer in time - slow query, deadlock, exhausted pool |
| Slow but correct            | Application, database, or downstream latency; check traces                                     |
| Intermittent failure        | One bad replica, or a partial network partition                                                |

Note the 502-versus-504 distinction: **502 means the backend gave a bad or no response; 504 means it never responded in time.** That is a frequent follow-up, because it changes where you look first.

## Example

```bash
# 1. DNS - what does it resolve to, and from where?
dig +short api.acme.com
dig +trace api.acme.com          # full delegation path when propagation is suspect
dig @8.8.8.8 api.acme.com        # rule out a stale local resolver

# 2. TCP - is the port even reachable?
nc -vz api.acme.com 443
mtr -rw api.acme.com             # where in the path do packets stop?

# 3. TLS - certificate, chain, and expiry
openssl s_client -connect api.acme.com:443 -servername api.acme.com </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates -ext subjectAltName

# 4. HTTP - full timing breakdown, layer by layer
curl -sS -o /dev/null -w \
  'dns=%{time_namelookup}s tcp=%{time_connect}s tls=%{time_appconnect}s ttfb=%{time_starttransfer}s total=%{time_total}s code=%{http_code}\n' \
  https://api.acme.com/healthz

# 5. Inside the cluster - are there any healthy backends at all?
kubectl get endpointslices -l kubernetes.io/service-name=api
kubectl describe ingress api
kubectl logs -l app=api --tail=100 --since=10m
```

## Interview tips

- Structure the answer as numbered layers and keep moving. Interviewers are testing breadth and structure, not depth on any one hop.
- Finish by converting it into a debugging method - "and this is how I isolate an outage" - because that is the real reason they asked.
- The `curl -w` timing breakdown is a strong, concrete detail: it tells you in one command whether the problem is DNS, TCP, TLS, or the application.
- Know 502 versus 504 cold. It is the most common follow-up.
- Mention TTL and lowering it before a planned DNS cutover; it shows you have done a migration rather than read about one.
- If the role is security-leaning, expect the branch into TLS specifics - handshake steps, SNI, certificate chain validation, and HSTS.
- If it is Kubernetes-leaning, expect the branch into Service → EndpointSlice → Pod and why a failing readiness probe produces a 503.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot Docker networking between containers?]] (`#415`): [How do you troubleshoot Docker networking between containers?](../docker/how-do-you-troubleshoot-docker-networking-between-containers.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Network Security](./README.md) · [All topics](../README.md)
