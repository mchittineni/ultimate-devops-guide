---
title: "What is High Availability?"
id: 57
category: "Scalability and High Availability"
difficulty: "Beginner"
tags:
  - devops
  - scalability-and-high-availability
  - interview-questions
---

# What is High Availability?

**Short answer:** High availability is designing a system to remain operational despite component failures, by removing single points of failure, adding redundancy, and detecting and routing around failures automatically.

## Detail

**Availability targets** and what they permit per year:

| Target                 | Downtime/year | Downtime/month |
| ---------------------- | ------------- | -------------- |
| 99%                    | 3.65 days     | 7.2 hours      |
| 99.9% ("three nines")  | 8.77 hours    | 43.8 minutes   |
| 99.95%                 | 4.38 hours    | 21.9 minutes   |
| 99.99% ("four nines")  | 52.6 minutes  | 4.4 minutes    |
| 99.999% ("five nines") | 5.26 minutes  | 26 seconds     |

Each nine costs materially more. The right target comes from what the business loses per minute of downtime, not from ambition.

**Techniques**

- **Redundancy** - N+1 or N+2 instances, across availability zones. Active-active (all serving) or active-passive (standby ready).
- **Load balancing with health checks** - unhealthy instances are removed from rotation automatically.
- **Failover** - automatic promotion of a replica when a primary fails; database managed services do this in tens of seconds.
- **Graceful degradation** - shed non-essential features rather than failing entirely (serve cached content, disable recommendations).
- **Resilience patterns** - timeouts, retries with exponential backoff and jitter, circuit breakers, bulkheads.
- **No single points of failure** - including in the "boring" layers: DNS, certificates, the deployment pipeline, and the monitoring system itself.

**HA is not DR.** High availability handles component failure within an environment, typically automatically and in seconds. Disaster recovery handles the loss of an entire site or region, typically with a documented procedure and a much longer RTO.

**Availability multiplies down a serial chain.** A request that passes through three components at 99.9% each is at best about 99.7% available, so redundancy has to exist at every hop, not just the web tier.

## Example

```yaml
# Kubernetes: spread replicas across zones and keep a floor during voluntary disruptions.
apiVersion: apps/v1
kind: Deployment
metadata: { name: api }
spec:
  replicas: 6
  selector: { matchLabels: { app: api } }
  template:
    metadata: { labels: { app: api } }
    spec:
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone # survive the loss of one AZ
          whenUnsatisfiable: DoNotSchedule
          labelSelector: { matchLabels: { app: api } }
      containers:
        - name: api
          image: registry.example.com/api:1.8.2
          readinessProbe: { httpGet: { path: /readyz, port: 8080 }, periodSeconds: 5 }
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: api }
spec:
  minAvailable: 4 # node drains and upgrades never take more than 2 away
  selector: { matchLabels: { app: api } }
```

## Interview tips

- Know the nines table well enough to reason about it out loud.
- Always mention that dependencies (DNS, certs, third-party APIs) are part of your availability.
- Distinguish HA from DR clearly - it is a frequently tested distinction.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[What are the core capabilities measured by DORA metrics and why do they correlate with high performance?]] (`#512`): [What are the core capabilities measured by DORA metrics and why do they correlate with high performance?](../core-devops-concepts/what-are-the-core-capabilities-measured-by-dora-metrics-and-why-do-they-correlate-with-high-performance.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scalability and High Availability](./README.md) · [All topics](../README.md)
