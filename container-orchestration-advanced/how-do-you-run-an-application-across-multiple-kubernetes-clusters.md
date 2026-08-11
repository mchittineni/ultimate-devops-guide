---
title: "How do you run an application across multiple Kubernetes clusters?"
id: 414
category: "Container Orchestration Advanced"
difficulty: "Advanced"
tags:
  - devops
  - container-orchestration-advanced
  - interview-questions
  - kubernetes
  - cloud-engineering
  - scalability-and-high-availability
---

# How do you run an application across multiple Kubernetes clusters?

**Short answer:** Start by naming _why_, because the reason determines the design: availability (survive a cluster or region failure), blast-radius isolation, data residency, tenancy separation, or scale beyond one cluster's practical limits. Then the pattern is almost always the same: **one Git repository as the source of truth** with a GitOps controller fanning out per cluster (ArgoCD ApplicationSets or Flux), **a global traffic layer** in front (DNS with health checks, Anycast, or a global load balancer) to steer users and fail over, **per-cluster stateless workloads** with configuration overlays, and **an explicit decision about data** - because that is the genuinely hard part. Avoid stretching one cluster across regions, and avoid true active/active on a single write-primary database unless you have accepted the latency or the conflict resolution.

## Detail

### Choose the topology from the requirement

| Requirement                          | Topology                                                             | Cost of it                                                        |
| ------------------------------------ | -------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Survive one cluster failing          | Active/passive - warm standby, traffic steered by DNS or a global LB | Idle capacity; drift risk in the standby if it is never exercised |
| Zero-downtime regional failure       | Active/active per region, users pinned by latency routing            | Data replication and conflict handling become your problem        |
| Blast-radius isolation               | Many small clusters, one per environment or tenant group             | N times the platform work, unless it is genuinely automated       |
| Data residency / sovereignty         | Cluster per jurisdiction, no cross-border replication                | Routing must be correct by law, not by convenience                |
| Scale past one cluster               | Sharded clusters behind one entry point                              | Shard placement and rebalancing logic                             |
| Cheaper upgrades and fewer surprises | Immutable clusters - build new, shift traffic, delete old            | Requires everything to be reproducible from Git                   |

**Do not** stretch a single control plane across regions - etcd needs low, stable latency for quorum, and a cross-region cluster converts a network blip into a control-plane outage. Multiple clusters, one per region, is the supported shape.

### Delivering to many clusters

- **GitOps with a fan-out.** One repository holds the manifests; ArgoCD **ApplicationSets** (cluster generator) or Flux Kustomizations render per-cluster variants from overlays. Adding a cluster becomes registering it, not copying a pipeline. See [what is GitOps](../devops-tools-and-automation/what-is-gitops.md) and [what is ArgoCD](../devops-tools-and-automation/what-is-argocd.md).
- **Progressive rollout across clusters, not just across Pods.** Deploy to one cluster, verify SLOs, then the next - a per-cluster canary. This is the main reliability benefit of multi-cluster and the one teams most often forget to use.
- **Configuration by overlay, artefact by digest.** The same image digest everywhere; only region, replica counts, endpoints, and secrets differ.
- **Fleet-level policy.** One place to define baselines - Kyverno or Gatekeeper policies, resource quotas, PSA levels, network defaults - applied to every cluster from the same repository, or drift makes each cluster a separate bespoke problem.

### Traffic and service discovery

- **North-south (users in):** DNS with health checks and latency or geo routing (Route 53, Azure Traffic Manager, Cloud DNS), a global load balancer, or Anycast at the CDN edge. Know the failover time you are actually buying: DNS TTL plus resolver behaviour means minutes, whereas a global load balancer or Anycast fails over in seconds. Say which you need.
- **East-west (service to service across clusters):** either keep calls in-cluster and replicate the whole stack per cluster - much simpler, and usually correct - or connect the clusters explicitly with a multi-cluster mesh (Istio multi-primary, Linkerd multi-cluster, Cilium Cluster Mesh) which gives cross-cluster service discovery, mTLS, and failover at the cost of a shared trust domain and real operational complexity. Cross-cluster synchronous calls also import the inter-region latency into every request, so treat them as a last resort rather than a default.
- **Non-overlapping CIDRs** for Pod and Service networks if the clusters must talk directly - a detail that is painful to retrofit.

### Data: the part that decides the design

Stateless replication is easy; state is where multi-cluster architectures succeed or fail:

- **Single write region, read replicas elsewhere** - simplest correct answer. Writes cross regions (accept the latency), reads are local. Failover is a promotion, with an RPO defined by replication lag.
- **Globally distributed database** (Spanner, CockroachDB, DynamoDB global tables, Aurora Global Database) - buys multi-region writes and brings consistency semantics you must actually understand.
- **Active/active on one primary** - the trap. Two clusters writing to one region's database means half your users pay the round trip and a region failure still takes the write path down.
- **Everything stateful needs a decision**: object storage replication, cache warming, message queues (an event consumed in one cluster must not be reprocessed in another), and cron or singleton jobs, which must run in exactly one cluster - leader election across clusters or a designated primary.

### The operational cost, stated honestly

Multi-cluster multiplies certificates, secrets distribution, upgrade cycles, observability plumbing (metrics and traces must carry a cluster label and roll up centrally), on-call surface, and cost. It is worth it when the requirement is real. When someone wants multi-cluster for "high availability" and a single cluster with three availability zones would meet the SLO, the right answer is to say so - a multi-zone cluster already survives a data-centre failure. See [how do you design for multi-region resilience](../cloud-engineering/how-do-you-design-for-multi-region-resilience.md) and [what are the real trade-offs of multi-cloud](../cloud-engineering/what-are-the-real-trade-offs-of-multi-cloud.md). And the discipline that makes any of this survivable: **exercise the failover regularly**, because an untested standby is a hypothesis, not a capability.

## Example

```yaml
# One definition, every cluster - ArgoCD ApplicationSet with a cluster generator
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata: { name: checkout, namespace: argocd }
spec:
  generators:
    - clusters: # every registered cluster labelled env=prod
        selector:
          matchLabels: { env: prod }
  strategy: # progressive: one wave of clusters at a time
    type: RollingSync
    rollingSync:
      steps:
        - matchExpressions:
            [{ key: region, operator: In, values: [eu-west-1] }] # canary cluster
        - matchExpressions:
            [{ key: region, operator: In, values: [us-east-1, ap-south-1] }]
  template:
    metadata: { name: "checkout-{{name}}" }
    spec:
      project: default
      source:
        repoURL: https://github.com/example/platform.git
        targetRevision: main
        path: "apps/checkout/overlays/{{metadata.labels.region}}" # per-region overlay
      destination: { server: "{{server}}", namespace: prod }
      syncPolicy:
        automated: { prune: true, selfHeal: true }
```

```text
Traffic and data, active/active reads with a single write region

                    users
                      |
        Route 53 latency routing + health checks   (failover: TTL 60s + resolver ~= 2-5 min)
             /                    \
   cluster: eu-west-1        cluster: us-east-1
   checkout (6 pods)         checkout (6 pods)     <- same image digest, different overlay
   reads  -> local replica   reads  -> local replica
   writes -> eu-west-1 primary  <---- cross-region write, ~80ms  (accepted, documented)
   cron/singleton: ENABLED   cron/singleton: disabled  <- exactly one cluster runs it

   Fail over: promote us-east-1 replica, flip the write endpoint, enable cron there.
   RPO = replication lag (measured, alerted).  RTO = promotion + DNS = ~5 min.
   Tested quarterly with a real, announced failover - not a document.
```

## Interview tips

- Ask (or state) the reason first. "Multi-cluster for what - availability, isolation, residency, or scale?" is the strongest possible opening, because each answer implies a different design.
- Say early that you would not stretch one cluster across regions, and why: etcd quorum needs low latency, so a network blip becomes a control-plane outage.
- Lead the delivery answer with GitOps fan-out (ApplicationSets or Flux) and per-cluster progressive rollout. Deploying to one cluster first is the reliability win people forget.
- Be precise about failover time: DNS gives minutes because of TTL and resolver caching; a global load balancer or Anycast gives seconds. Naming that difference is what separates design from vocabulary.
- Push data to the front of the discussion. Single write region with local reads is the answer that is usually right, and "active/active against one primary database" is the trap to call out.
- Mention the singleton problem - cron jobs and leader-elected components must run in exactly one cluster - because it is a real bug people hit in week two.
- Volunteer the honest cost: certificates, secrets, upgrades, observability labelling, on-call, spend. And say that a three-zone single cluster already survives a data-centre failure, so multi-cluster needs a requirement it alone can meet.
- Close on testing the failover regularly. An untested standby has never once worked first time.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
