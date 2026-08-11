---
title: "What DevOps interview questions does Sony ask?"
id: 380
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - sony
  - kubernetes
  - infrastructure-as-code
  - site-reliability-engineering
  - incident-management
  - cicd
  - api-gateway-and-service-mesh
  - devops-tools-and-automation
  - cloud-cost-optimization
---

# What DevOps interview questions does Sony ask?

## Questions

**Incident response and judgement**

- **How would you respond to a production outage during peak hours?**
- **How do you decide between rolling back and applying a hotfix when a production issue occurs?**
- **What steps do you take when your monitoring says the system is healthy but users are still complaining?**
- **How do you start troubleshooting when a Kubernetes cluster feels slow?**
- **How would you investigate a sudden threefold increase in the AWS bill?**

**Alerting and reliability**

- **How do you design alerting so that you avoid noisy or false alerts and prevent alert fatigue?**

**Deployment and delivery**

- **How do you guarantee zero-downtime deployments in Kubernetes?**
- **How do you stop broken code from reaching production?**
- **How would you shorten a CI/CD pipeline that currently takes 45 minutes?**
- **How do you secure your Jenkins pipelines?**
- **I want Jenkins to run a pipeline only once N commits have been pushed. How would you do that?**
- **What vulnerability reports do you get out of your SonarQube?**

**Resilience and multi-region design**

- **How would you design a system to survive one AWS region going down?**
- **How would you design a Kubernetes cluster that must survive a full availability-zone failure with no data loss, while running stateful workloads at scale — covering storage, networking, controllers, quorum, and recovery?**
- **What is your approach to disaster recovery for stateful applications running in containers?**

**Kubernetes internals and platform design**

- **Explain the complete request flow when using the Gateway API with multiple GatewayClasses across regions. How do you prevent split-brain routing?**
- **How do you debug intermittent Pod restarts when the liveness probe passes and readiness passes, but the Pod is still killed by the node?**
- **What happens internally when etcd latency spikes above 500 ms? How does it affect the scheduler, the controllers, and the API server?**
- **Design a multi-tenant Kubernetes platform where teams cannot affect each other's resource usage, network traffic, or upgrade cycles.**
- **How would you implement zero-trust networking inside Kubernetes without using a service mesh?**
- **Describe a real production incident where a misconfigured HPA caused cascading failure. How would you redesign autoscaling to avoid it?**
- **Why does a container sometimes exit immediately even though the application works perfectly in local testing? Give three real production causes.**
- **How would you design container images for very fast cold starts in serverless or autoscaled Kubernetes environments?**

**Terraform at scale**

- **How would you safely refactor a Terraform monorepo with hundreds of state files into a module-based architecture without downtime?**
- **Explain how Terraform builds its dependency graph internally. How can circular dependencies still appear in real projects?**
- **How would you manage Terraform when multiple teams deploy into the same AWS account but must not overwrite each other's resources?**
- **Describe a production failure caused by `terraform apply`. What guardrails would you implement to prevent it permanently?**
- **If I want to start an EC2 instance once CPU hits 80%, what Terraform code would you write — and it should also copy the image from S3.**

**GitOps at scale**

- **How do you design GitOps for more than a thousand clusters, with environment drift detection, emergency hotfixes, and controlled manual overrides?**

## Example

```text
Sony — DevOps Engineer, reported round
29 questions — almost entirely open-ended design and diagnosis

  K8s internals / platform    8   Gateway API across regions + split-brain,
                                  node kills a Pod whose probes pass, etcd
                                  latency >500ms, multi-tenant platform,
                                  zero-trust without a mesh, HPA cascade,
                                  container exits immediately, cold starts
  Terraform at scale          5   refactor hundreds of state files, dependency
                                  graph internals + circular deps, many teams
                                  one account, a failure caused by apply
  Incident response           5   peak-hour outage, rollback vs hotfix,
                                  healthy metrics but unhappy users,
                                  slow cluster, 3x bill spike
  Deployment and delivery     6   zero downtime, block broken code, 45-min
                                  pipeline, Jenkins security, N-commit trigger,
                                  SonarQube reports
  Resilience / multi-region   3   survive a region loss, AZ failure with
                                  stateful workloads, container DR
  Alerting                    1   avoid noise and fatigue
  GitOps at scale             1   1000+ clusters

THE HARDEST ROUND IN THIS COLLECTION
  There is not a single definition question. Every item is "design this",
  "debug this", or "describe a real failure". Several are explicitly staff-level
  — 1000+ clusters, hundreds of state files, etcd latency internals.
```

## Interview tips

- The "probes pass but the node kills the Pod" question is the sharpest in the round and it has a specific answer: if liveness and readiness are both passing, the kill is not coming from the probes — it is coming from the **kubelet's eviction manager or the kernel OOM killer**. The three causes to name are memory pressure on the node causing eviction of Pods exceeding their requests (BestEffort and Burstable first), the container exceeding its own memory limit and being `OOMKilled` with exit code 137, and node-pressure eviction from disk or inode exhaustion. Say how you would confirm it: `kubectl describe pod` shows `Evicted` with a reason, `kubectl get events` shows the eviction, `dmesg` on the node shows the OOM kill, and the exit code distinguishes them. Add that a Guaranteed QoS Pod — requests equal to limits — is evicted last, which is the design fix.
- The etcd-latency question is a genuine internals question and worth preparing precisely. etcd is the only datastore, and every write goes through raft consensus requiring a quorum fsync — so latency above 500 ms means write requests to the API server slow or time out. Consequences to name: the API server's watch and write paths degrade, so `kubectl` becomes slow and mutating calls fail; leader election leases begin to expire, so controllers and the scheduler lose leadership and stop reconciling; the scheduler cannot bind Pods, so scheduling stalls; kubelet status updates fail, so nodes flip to `NotReady` and trigger spurious Pod evictions; and etcd may trigger leader elections of its own, compounding it. Say that existing Pods keep serving traffic throughout — the dataplane is unaffected — and that the usual causes are slow disks (etcd needs low-latency fsync, so it wants dedicated SSD), a large database from unrotated events or too many objects, or network latency between members. See [main components of Kubernetes architecture](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md).
- "Container exits immediately but works locally — give three causes" wants exactly three concrete ones, so pick the real production classics: PID 1 has nothing to keep it alive, because the image's `CMD` runs a foreground process locally but the container's command starts a daemon that backgrounds itself and exits; a missing environment variable, config file, or mounted secret that exists on your laptop but not in the cluster, so the process fails at startup; and a platform or permission mismatch — an `arm64` image on `amd64` nodes, or a non-root `securityContext` where the process cannot write a path it expects. Add exit-code triage as the method: 0 means it completed and `restartPolicy` is wrong, 1 is an application error, 137 is `OOMKilled`, 126 or 127 mean the entrypoint is not executable or not found. See [troubleshooting a Pod stuck in Pending or CrashLoopBackOff](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md).
- Zero-trust in Kubernetes _without_ a service mesh is a constraint question and there is a real answer: default-deny NetworkPolicies in every namespace so nothing talks to anything unless allowed; workload identity through bound service-account tokens and OIDC rather than network position; application-layer mTLS or TLS terminated by the workloads themselves, with certificates issued by cert-manager and short-lived; authorisation at the API layer via JWT validation; admission control enforcing non-root, no host namespaces, and signed images; and encryption in transit provided by the CNI where available — Cilium can do transparent WireGuard or IPsec encryption without a sidecar. Naming Cilium's transparent encryption is the detail that answers the constraint properly. See [zero-trust security](../network-security/what-is-zero-trust-security.md) and [network segmentation](../network-security/what-is-network-segmentation.md).
- The HPA cascade question wants a real mechanism, and the classic story is worth having ready: an HPA scaling on CPU against a backend whose slowness was caused by a saturated database — so scaling up added connections, which made the database slower, which raised latency and CPU further, which scaled up again until connections were exhausted and everything failed. The redesign: scale on a signal that reflects work rather than symptom — queue depth or requests per replica rather than CPU — cap `maxReplicas` well below what the data tier can serve, put a connection pooler such as RDS Proxy or PgBouncer in front, add circuit breakers and load shedding so the service degrades rather than amplifying, and set a stabilisation window to stop thrashing. Say that autoscaling a stateless tier in front of a bottlenecked dependency makes the outage worse, which is the whole insight. See [designing a system to degrade gracefully under overload](../scalability-and-high-availability/how-do-you-design-a-system-to-degrade-gracefully-under-overload.md).
- The AZ-failure-with-stateful-workloads question is a full design answer, so structure it by the five things they listed. Storage: zonal block volumes cannot follow a Pod across zones, so either use a replicated storage layer or let the _application_ replicate — three StatefulSet replicas, one per zone, each with its own zonal volume, and `WaitForFirstConsumer` binding so the volume is created where the Pod is scheduled. Networking: subnets and load balancers in all three zones, and topology spread constraints so replicas never co-locate. Controllers: a control plane across three zones, and PodDisruptionBudgets tuned so voluntary disruption cannot break quorum. Quorum: an odd member count so losing one zone leaves a majority — which is why three zones rather than two is the requirement, since a two-zone split has no majority. Recovery: automated re-replication when the zone returns, plus backups because replication is not backup. The quorum-needs-three-zones point is the crux. See [StatefulSets](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md) and [designing for multi-region resilience](../cloud-engineering/how-do-you-design-for-multi-region-resilience.md).
- The Gateway API split-brain question is current and specific. Walk the flow: a `GatewayClass` names a controller implementation, a `Gateway` is a concrete listener provisioned by that controller, `HTTPRoute` objects attach to it and may be owned by different namespaces via `ReferenceGrant`, and the controller programs the dataplane. Then the split-brain risk: if two regional Gateways both accept the same hostname and global DNS resolves to both, writes can land in either region with no coordination. Prevention: one authoritative region per hostname or tenant, health-checked failover rather than active-active DNS for anything stateful, a single source of truth for routing config reconciled by GitOps so the regions cannot diverge, and — where you truly need active-active — a data layer designed for it with conflict resolution. Say that split-brain is a data problem that routing exposes, not a routing problem.
- Multi-tenant Kubernetes design should map each of the three isolation dimensions they named onto a mechanism: resource usage via namespace-per-tenant with `ResourceQuota` and `LimitRange`, plus Guaranteed QoS and priority classes so one tenant cannot starve another, and node pools with taints for hard separation; network traffic via default-deny NetworkPolicies and, where required, separate ingress per tenant; upgrade cycles via separate clusters or node pools per tenant, since a shared control plane means a shared upgrade — say that if tenants genuinely need independent upgrade cadence, cluster-per-tenant is the honest answer and virtual clusters are the middle ground. Add RBAC scoped per namespace, admission policy, and per-tenant cost attribution by label.
- The Terraform monorepo refactor wants a safe migration path: never move resources by deleting and recreating. Use `moved` blocks — or `terraform state mv` — so refactoring into modules is a state operation with no infrastructure change, verify with a plan that shows _no_ changes as the acceptance test, migrate one stack at a time behind a review, and keep state backends versioned so you can roll back a bad state write. Say the guiding rule: an empty plan proves the refactor was behaviour-preserving. For the dependency-graph half, say Terraform builds a DAG from explicit references and `depends_on`, walks it in order, and parallelises independent nodes — and that circular dependencies appear in real projects through security groups referencing each other, IAM roles and policies that reference one another, or two modules each consuming the other's output; the fix is to break the cycle with a standalone rule resource or restructure the module boundary. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- The many-teams-one-account question is about ownership boundaries: separate state per team and per component so no two pipelines write the same state, IAM roles scoped by resource tag or naming prefix so a team physically cannot modify another's resources, a naming and tagging standard enforced by policy, and ideally separate accounts per team with the shared account reserved for genuinely shared infrastructure. Say that state locking prevents concurrent writes but does nothing about a team applying over resources it does not own — permissions are what prevent that.
- The `terraform apply` failure question is an invitation to be honest about a real incident, and the guardrails are what is being graded: plan reviewed on the pull request and applied from the saved plan file so what was reviewed is what runs, apply only from CI with no local applies, `prevent_destroy` on stateful resources, required approval on any plan showing deletions, policy-as-code scanning the plan with OPA or Sentinel, and deletion protection enabled at the provider level. Naming "apply the saved plan file" is the strongest single guardrail.
- The 1000-cluster GitOps question wants a structure, not a tool name: an ApplicationSet with a cluster generator so clusters are enrolled by label rather than defined one by one, a repository layout with a shared base plus per-environment and per-region overlays so there is one source of truth, automated sync with self-heal in lower environments and approval-gated sync in production, progressive rollouts so a bad change reaches a wave of clusters rather than all of them, drift detection surfaced as `OutOfSync` status with alerting, and a documented break-glass path for emergency hotfixes — a direct commit to a hotfix branch with automatic reconciliation afterwards, so the override is recorded rather than hidden. Say that the hard part is not deployment but _knowing_ which of a thousand clusters is drifting. See [GitOps](../devops-tools-and-automation/what-is-gitops.md) and [Argo CD](../devops-tools-and-automation/what-is-argocd.md).
- "Healthy metrics but users complaining" is a classic SRE question and the answer is that you are measuring the wrong thing. Your metrics are infrastructure-level while the user experience is a journey — so check real user monitoring and synthetic probes on the critical path, look at percentiles rather than averages because p99 pain is invisible in a mean, segment by region, tenant, device, and API version because an aggregate hides a broken cohort, and verify the monitoring itself is not stale or scraping a healthy-but-unused replica. Then say the fix: define SLIs from user journeys rather than from CPU. See [service level indicators](../site-reliability-engineering/what-are-service-level-indicators-slis.md).
- Rollback versus hotfix has a decision rule worth stating plainly: roll back by default, because it is the fastest path to a known-good state and diagnosis can happen afterwards. Hotfix only when rollback is impossible or unsafe — a database migration that cannot be reversed, a security fix that must go forward, or data already written in the new format. Say that you mitigate first and diagnose second, and that a hotfix under pressure carries a much higher risk of a second incident. See [running a major incident as incident commander](../incident-management/how-do-you-run-a-major-incident-as-incident-commander.md).
- Alert design should be answered with principles and a mechanism: alert on user-facing symptoms and SLO burn rate rather than causes; every page must be actionable, or people stop reading them; use severity tiers so only customer-impacting issues page and everything else becomes a ticket or a dashboard; group and deduplicate related alerts; suppress during known maintenance; and delete any alert nobody has ever acted on. Name multi-window multi-burn-rate alerting as the concrete technique. See [designing alerts that page a human](../site-reliability-engineering/how-do-you-design-alerts-that-page-a-human.md) and [error budgets](../site-reliability-engineering/what-is-error-budget.md).
- The Jenkins N-commits trigger is a small practical question: there is no built-in "after N commits" trigger, so you either poll on a schedule and let the build accumulate several commits, or use a webhook plus a script that counts commits since the last successful build and exits early below the threshold, or gate on a changeset condition in the pipeline. Say plainly that batching builds is usually the wrong instinct — it delays feedback and makes bisecting a failure harder — and that the legitimate use case is an expensive job such as a nightly integration suite. Being willing to challenge the requirement is the better answer.
- For the EC2-at-80%-CPU Terraform question, correct the framing: Terraform is declarative and does not react to metrics at runtime. The right implementation is a CloudWatch alarm on `CPUUtilization` at 80% triggering an Auto Scaling policy — all of which you _define_ in Terraform — with the "copy the image from S3" part handled by `user_data` or a baked AMI rather than by Terraform at scale-out time. Saying "Terraform declares the alarm and the scaling policy; the cloud does the reacting" is the answer. See [auto-scaling](../scalability-and-high-availability/what-is-auto-scaling.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
