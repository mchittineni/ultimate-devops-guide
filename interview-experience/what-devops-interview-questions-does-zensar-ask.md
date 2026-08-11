---
title: "What DevOps interview questions does Zensar ask?"
id: 394
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - zensar
  - azure-engineering
  - kubernetes
  - cicd
  - docker
  - network-security
  - cloud-cost-optimization
  - backup-and-disaster-recovery
---

# What DevOps interview questions does Zensar ask?

## Questions

**Azure DevOps pipelines**

- **What is a service connection, and what is a connection string?**
- **What types of pipeline do you use, and how many types are there?**
- **What is a variable in a pipeline?**
- **Can you run multiple jobs in parallel from a single pipeline? How?**
- **What is an agent?**

**Azure platform**

- **How do you set alerts in Azure Monitor — the steps and configuration you would do?**
- **What are the types of VNet peering?**
- **How do you create an app registration?**
- **For cost optimisation, should you use Azure Application Gateway or a network gateway?**

**Kubernetes**

- **What is the difference between a ReplicaSet and a Deployment?**
- **What is the difference between a stateless and a stateful application?**
- **How are ConfigMaps and Secrets used in Kubernetes?**
- **If the control plane goes down, what happens to the worker nodes?**
- **What is etcd and what is it used for?**
- **If two Pods are in different namespaces, how do you let them communicate securely?**
- **What is an Ingress?**
- **Why do you need Kubernetes if Docker volumes already exist?**

**Docker and resilience**

- **What is Docker networking?**
- **What is disaster recovery?**

## Example

```text
Zensar — DevOps Engineer (6+ YOE), reported round
19 questions

  Kubernetes                  8   ReplicaSet vs Deployment, stateless vs
                                  stateful, ConfigMaps + Secrets, control
                                  plane down, etcd, cross-namespace secure
                                  comms, Ingress, "why K8s if Docker volumes
                                  exist"
  Azure DevOps pipelines      5   service connection vs connection string,
                                  pipeline types, variables, parallel jobs,
                                  agents
  Azure platform              4   Azure Monitor alerts, VNet peering types,
                                  app registration, App Gateway vs network
                                  gateway on cost
  Docker and resilience       2   Docker networking, disaster recovery

THE ONE ODD QUESTION
  "Why do you need Kubernetes if Docker volumes exist?" compares two things
  that solve different problems. The candidate noted the framing was unclear —
  answering it by naming the category error is the correct move.
```

## Interview tips

- "Why Kubernetes if Docker volumes exist?" compares a storage feature with an orchestrator, so name that mismatch politely and then answer the question behind it. A Docker volume solves **persistence for one container on one host**. Kubernetes solves everything around that: scheduling across many hosts, self-healing when a container or node dies, rolling updates and rollback, horizontal scaling, service discovery and load balancing, and declarative desired state that a controller continuously reconciles. On storage specifically, Kubernetes adds the layer Docker volumes lack — PersistentVolumes and PVCs with dynamic provisioning via a StorageClass, access modes, and a CSI interface so a volume can follow a Pod to another node. Say the sentence that resolves it: a Docker volume keeps data alive when a container restarts on **the same machine**; Kubernetes keeps the _application_ alive when the machine itself disappears. See [what container orchestration is and why you need it](../container-orchestration-advanced/what-is-container-orchestration-and-why-do-you-need-it.md).
- "If the control plane goes down, what happens to the worker nodes?" has a precise two-part answer that many candidates get half right. Existing Pods **keep running and keep serving traffic**, because the kubelet manages its containers independently and kube-proxy's routing rules are already programmed on each node. What you lose is everything the control plane does: no `kubectl`, no new scheduling, no self-healing, no rescheduling if a node dies, no scaling, and no Service or ConfigMap updates propagating. Say both halves, and add that node status updates stop, so after the monitor grace period nodes may appear `NotReady` — but the dataplane is unaffected throughout. That distinction between control plane and dataplane is the whole point. See [main components of Kubernetes architecture](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md).
- The cross-namespace secure-communication question wants layers, because "namespaces do not isolate network traffic by default" is the key fact. Reachability first: Pods in different namespaces can already talk, addressed as `service.namespace.svc.cluster.local`. Then _secure_: a **NetworkPolicy** in the destination namespace with a `namespaceSelector` allowing only the specific source namespace, on top of a default-deny baseline — noting that policies do nothing unless the CNI enforces them. Then identity and encryption: mutual TLS so the caller is authenticated rather than merely permitted, either through a service mesh or application-level TLS with short-lived certificates from cert-manager; plus RBAC scoped per namespace, and separate service accounts so the workload identity is distinct. Say that network policy answers "who can reach me" and mTLS answers "who are you" — you need both. See [network segmentation](../network-security/what-is-network-segmentation.md) and [zero-trust security](../network-security/what-is-zero-trust-security.md).
- The service connection versus connection string question is an Azure DevOps specific with a clean answer: a **service connection** is a first-class Azure DevOps object holding the credentials and configuration a pipeline needs to reach an external system — an Azure subscription, a container registry, a Kubernetes cluster — scoped and permissioned at project level, and ideally using **workload identity federation** so there is no stored service-principal secret to rotate. A **connection string** is just a configuration value your application uses to reach a database or storage account, and it belongs in Key Vault referenced through a variable group, not in the pipeline YAML. Say that framing: one is how the _pipeline_ authenticates, the other is how the _application_ does — and neither should be a plain-text secret in a repository.
- Application Gateway versus "network gateway" on cost needs the comparison made explicit before you answer, because the products differ in kind. Application Gateway is a **layer 7** regional load balancer with WAF, path and host routing, and TLS termination, billed hourly plus capacity units. Azure Load Balancer is the **layer 4** product and is significantly cheaper (the basic tier historically free, standard billed on rules and data). NAT Gateway and VPN Gateway are outbound and connectivity products entirely. So the cost-optimal answer is: if you only need layer-4 distribution, a Load Balancer is much cheaper; pay for Application Gateway when you actually need layer-7 routing or the WAF — and if you need global edge distribution and caching, Front Door may replace both. Say that the real cost mistake is running an Application Gateway per application instead of one with host-based routing.
- ReplicaSet versus Deployment should be answered with why you never author the former: a ReplicaSet maintains a stable number of Pod replicas matching its selector; a Deployment is a higher-level controller that _manages_ ReplicaSets on your behalf, creating a new one per revision — which is what gives you rolling updates with `maxSurge` and `maxUnavailable`, revision history, and `kubectl rollout undo`. Say that the template hash in the ReplicaSet name is the revision identity, and that is exactly the mechanism rollback relies on.
- Stateless versus stateful should end in a design consequence rather than a definition: a stateless application holds no data locally, so any replica can serve any request and Pods are disposable — which is what makes horizontal scaling, rolling updates, and self-healing straightforward. A stateful application has identity and durable data, so it needs a StatefulSet with stable ordinal names, per-replica PersistentVolumeClaims, a headless Service for peer discovery, and ordered updates. Add the practical point: a "stateless" application still _has_ state — it just lives in a database, cache, or object store, which is precisely why externalising session data to Redis is the first step in making something scalable. See [StatefulSets](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md).
- ConfigMaps and Secrets deserve the honest caveat: both are key-value objects consumed as environment variables or mounted files, ConfigMaps for non-sensitive configuration and Secrets for sensitive values — but a Secret is only **base64-encoded**, not encrypted, so you must enable encryption at rest for etcd and restrict access with RBAC. Then the operational detail that shows real use: a **mounted** ConfigMap or Secret updates in place when the object changes, while one injected as an **environment variable** does not — it is fixed for the container's lifetime, so a rotation needs a rolling restart. Say that this is why external secret stores surfaced through the CSI driver or External Secrets Operator are preferred for anything that rotates. See [managing secrets in CI/CD pipelines](../devsecops/how-do-you-manage-secrets-in-ci-cd-pipelines.md).
- etcd should be described by its properties rather than as "the database": a distributed, strongly consistent key-value store using the raft consensus protocol, holding the entire cluster state — every object, its spec and status. The details worth adding: only the API server talks to it, quorum requires a majority so member counts are odd and a three-member cluster survives one loss, every write needs a quorum fsync which is why etcd demands low-latency disks, and it exposes a **watch** API that is what lets controllers react to change rather than poll. Then the operational consequence: etcd is what you back up, and losing it without a snapshot means losing the cluster's state — though not the running workloads.
- VNet peering types has a specific answer: **regional** peering between VNets in the same region and **global** peering across regions, both giving private, non-transitive connectivity over the Microsoft backbone with no gateway required. The two facts that matter are that peering is **not transitive** — so a hub-and-spoke topology needs a firewall, route server, or user-defined routes in the hub to let spokes reach each other — and that address spaces **must not overlap**. Mention Virtual WAN as the managed answer at larger scale.
- Azure Monitor alerts should be answered as the steps they asked for: choose the scope (the resource, resource group, or subscription), select a signal — a platform metric, a log query in Log Analytics, an activity-log event, or the resource health signal — set the condition with an aggregation, threshold, evaluation frequency, and lookback window (or a **dynamic** threshold, which is the anomaly-detection option), attach an **action group** defining who is notified and what runs (email, SMS, webhook, Logic App, Automation runbook, or an ITSM connector), and set severity plus suppression rules. Then volunteer the gap that always comes up: **memory and disk on a VM are not default platform metrics** — they are guest-OS level and need the Azure Monitor agent with a data collection rule. Saying that unprompted is the strongest part of the answer. See [monitoring in DevOps](../monitoring-and-logging/what-is-monitoring-in-devops.md).
- App registration is an Entra ID question: registering an application creates an application object and a **service principal** in the tenant, giving you a client ID, optional client secret or certificate, redirect URIs, and API permissions — used so an application or pipeline can authenticate as itself. Say the improvement in the same breath: prefer a **managed identity** where the workload runs in Azure, because there is no credential to store or rotate, and prefer workload identity federation over a client secret for external systems such as GitHub Actions. See [least-privilege identity in the cloud](../cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md).
- The parallel-jobs question has an exact Azure DevOps answer: jobs within a stage run **in parallel by default** unless you add `dependsOn`, so the way to serialise is to add dependencies, and the way to parallelise is to remove them. Add the two constructs that matter: a **matrix** strategy to fan one job out across combinations, and `maxParallel` to cap concurrency — plus the practical limit that parallelism is bounded by your purchased parallel jobs or the number of self-hosted agents available. For pipeline types, say YAML (the current recommendation, versioned with the code) versus classic build and release pipelines (UI-configured, not versioned), and note that classic release pipelines are where deployment groups and stage-level approvals lived, while YAML uses environments with approvals and checks. For variables: pipeline-level, stage-level, and job-level scopes, runtime parameters, variable groups in the Library (optionally linked to Key Vault), secret variables that are masked, and output variables passed between stages — and that approvals attach to the **environment**, not the YAML. An agent is the compute that runs a job, either Microsoft-hosted (clean ephemeral VM, no private-network access) or self-hosted (your machine, private access and caching, but you patch it and state persists between jobs).
- Docker networking should list the drivers with their purpose and then name the default: `bridge` is the default for standalone containers, giving a private internal network with NAT for egress and published ports for ingress; `host` removes network isolation for performance at the cost of port conflicts; `none` disables networking; `overlay` spans hosts for Swarm; `macvlan` gives the container its own MAC address on the LAN. Then the detail that shows real use: the **default** bridge provides no DNS-based service discovery, whereas a **user-defined** bridge does — which is why containers on a user-defined network resolve each other by name and why Compose creates its own network. See [Docker network types](../docker/what-are-docker-network-types-bridge-host-overlay-macvlan.md).
- Disaster recovery should lead with the two numbers and then a named tier: RPO is tolerable data loss, RTO is tolerable time to recover, and the patterns are backup-and-restore, pilot light, warm standby, and active-active in ascending cost and descending RTO. Then the three points that make the answer credible: replication is **not** backup, because a deletion replicates too — so you need an immutable copy; traffic redirection needs health-checked DNS or a global load balancer; and an untested plan does not count, so a restore rehearsal is the only proof. On Azure specifically, name Site Recovery, geo-redundant storage, paired regions, and Traffic Manager or Front Door. See [disaster recovery](../scalability-and-high-availability/what-is-disaster-recovery.md).
- Ingress should be defined as an API object that routes external HTTP and HTTPS traffic to Services by host and path, with TLS termination — plus the crucial point that the object does nothing without an **ingress controller** running in the cluster to implement it, selected via `ingressClassName`. Add that the Gateway API is its successor, since the community ingress-nginx project is now maintenance-only. See [exposing an application in Kubernetes](../kubernetes/how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[How do you scale CI/CD across many services and teams?]] (`#459`): [How do you scale CI/CD across many services and teams?](../cicd/how-do-you-scale-ci-cd-across-many-services-and-teams.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
