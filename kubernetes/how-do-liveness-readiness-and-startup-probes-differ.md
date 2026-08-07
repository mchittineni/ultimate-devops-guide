---
title: "How do liveness, readiness, and startup probes differ?"
id: 255
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - kubernetes
  - interview-questions
---

# How do liveness, readiness, and startup probes differ?

**Short answer:** A **readiness** probe decides whether a Pod receives traffic, a **liveness** probe decides whether the kubelet restarts the container, and a **startup** probe suspends the other two until a slow-booting application has finished starting. They answer three different questions, and conflating them causes outages.

## Detail

| Probe            | Question it answers              | Failure consequence                                |
| ---------------- | -------------------------------- | -------------------------------------------------- |
| `startupProbe`   | Has the app finished booting?    | Container killed; liveness/readiness stay paused   |
| `readinessProbe` | Should this Pod get traffic now? | Pod removed from Service endpoints - not restarted |
| `livenessProbe`  | Is this container wedged?        | Container restarted                                |

**The classic interview scenario: liveness passing, readiness failing.** The container keeps running and is _not_ restarted, but it is pulled out of the Service's EndpointSlice, so it stops receiving requests. If every replica is in that state, the Service has zero endpoints and clients get connection failures - the Deployment looks healthy in `kubectl get pods` while the app is entirely down. This is the correct behaviour: readiness is how a Pod says "not me right now" while it warms a cache, reconnects to a database, or drains.

**Three probe mechanisms:** `httpGet` (any 2xx/3xx is a pass), `tcpSocket` (can the port be opened?), and `exec` (a command exiting 0). There is also `grpc` for services implementing the gRPC health-checking protocol. Prefer `httpGet` against a dedicated endpoint you control.

**Why the startup probe exists.** Before it, slow starters forced you to set a long `initialDelaySeconds` on the liveness probe, which meant a genuinely hung container also went undetected for that long. A startup probe with a generous `failureThreshold × periodSeconds` budget lets you keep the liveness probe aggressive after boot.

**The most common production mistake** is pointing the liveness probe at an endpoint that checks downstream dependencies. When the database blips, every replica fails liveness, every container restarts simultaneously, and a recoverable dependency outage becomes a self-inflicted total outage. **Liveness must only test the process itself.** Dependency health belongs in the readiness probe, if anywhere.

**Tuning matters.** `periodSeconds × failureThreshold` is your detection window. Too tight and a GC pause or a slow request restarts a healthy container; too loose and a wedged pod serves errors for minutes. `terminationGracePeriodSeconds` interacts with this: a readiness probe that starts failing on `SIGTERM`, plus a `preStop` sleep, is what gives the load balancer time to stop sending new connections before the process exits.

## Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  template:
    spec:
      containers:
        - name: api
          image: ghcr.io/acme/api:1.4.0
          ports: [{ containerPort: 8080 }]

          # Boot budget: 30 x 5s = 150s before liveness/readiness begin.
          startupProbe:
            httpGet: { path: /healthz, port: 8080 }
            periodSeconds: 5
            failureThreshold: 30

          # Process-only check. No database, no downstream calls.
          livenessProbe:
            httpGet: { path: /healthz, port: 8080 }
            periodSeconds: 10
            failureThreshold: 3

          # May check dependencies - failing here removes traffic, not the Pod.
          readinessProbe:
            httpGet: { path: /readyz, port: 8080 }
            periodSeconds: 5
            failureThreshold: 2

          lifecycle:
            preStop:
              exec:
                command: ["sleep", "10"] # let endpoints propagate before exit
      terminationGracePeriodSeconds: 30
```

```bash
# What the probe actually returned, and why the container restarted
kubectl describe pod api-7d9f... | grep -A5 -i "liveness\|readiness\|Last State"
kubectl get endpointslices -l kubernetes.io/service-name=api   # who is receiving traffic
```

## Interview tips

- Lead with the one-line distinction: readiness controls **traffic**, liveness controls **restarts**.
- "Liveness passes but readiness fails - what happens?" is the single most common follow-up. The Pod runs, gets no traffic, and is never restarted.
- Volunteering the anti-pattern - liveness probes that check the database - marks you as someone who has actually operated this.
- Mention `preStop` plus readiness-on-`SIGTERM` when asked about zero-downtime rollouts; probes and graceful shutdown are the same conversation.

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
