---
title: "What DevOps interview questions does Oracle ask?"
id: 361
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - oracle
  - kubernetes
  - docker
  - api-gateway-and-service-mesh
  - container-orchestration-advanced
  - infrastructure-as-code
  - linux-administration
  - network-security
---

# What DevOps interview questions does Oracle ask?

## Questions

### Round set 1 — Kubernetes objects and Docker (8 YOE)

- **What is the purpose of init containers in Kubernetes?**
- **What is the difference between a StatefulSet and a Deployment?**
- **What is the difference between a ConfigMap and a Secret?**
- **What is a PodDisruptionBudget?**
- **Explain all the components in a `deployment.yaml`.**
- **When you try to deploy a Pod and it throws an error, how do you investigate?**
- **How do you deploy a Pod onto a specific node?**
- **Walk me through all the steps of a multi-stage Docker image build.**
- **What layers do you get in Docker while building?**
- **Write a cron expression to schedule a job in Linux.**
- **If the Terraform state file is corrupted, how do you fix it?**
- **Explain the Terraform `lifecycle` block — `create_before_destroy` and the destroy behaviour.**

### Round set 2 — Kubernetes access, Istio, and runtimes (7 YOE)

- **How do you give a user access to a single namespace in a Kubernetes cluster?**
- **What is an Ingress, and why are you using Istio?**
- **What is traffic mirroring in Istio?**
- **What are the Service types, and what does each one do?**
- **What is a CustomResourceDefinition?**
- **Which Kubernetes resources do you know?**
- **What is the role of the container runtime, which runtime do you use, and why?**
- **What is a reverse proxy?**
- **Explain a three-tier architecture.**

## Example

```text
Oracle — DevOps Engineer, two reported rounds (21 questions)

  SET 1  Objects + Docker (8 YOE)     12   init containers, StatefulSet vs
                                           Deployment, ConfigMap vs Secret,
                                           PDB, deployment.yaml field by field,
                                           Pod error triage, node pinning,
                                           multi-stage build, layers, cron,
                                           corrupted state, lifecycle block

  SET 2  Access + Istio (7 YOE)        9   namespace-scoped access, Ingress vs
                                           Istio, traffic mirroring, Service
                                           types, CRDs, resource inventory,
                                           container runtime choice, reverse
                                           proxy, three-tier

ORACLE ASKS "EXPLAIN ALL THE COMPONENTS"
  Twice — for deployment.yaml and for multi-stage builds. These are
  completeness questions: the mark is for covering every field or stage
  without prompting, so rehearse them as a structured walkthrough.
```

## Interview tips

- Traffic mirroring is the most Istio-specific question here and it has a precise definition: also called shadowing, it sends a _copy_ of live production traffic to a second version of a service while the real response still comes from the primary — the mirrored responses are discarded. It is configured in a `VirtualService` with a `mirror` destination and `mirrorPercentage`. Then give the reason it exists: you get real production traffic patterns against a new version with zero user risk, which a canary cannot offer because a canary's failures are user-visible. Add the caveat that earns the point: mirrored requests still hit downstream systems, so writes get duplicated unless the shadow environment has its own datastore. See [what Istio is](../container-orchestration-advanced/what-is-istio.md).
- "What is an Ingress and why are you using Istio?" is asking you to justify the extra complexity, so do not describe them as the same thing. An Ingress does layer-7 host and path routing plus TLS termination at the cluster edge, and that is all. Istio adds service-to-service concerns: mutual TLS between every workload, retries, timeouts, circuit breaking and outlier detection without touching application code, fine-grained traffic splitting for canaries and mirroring, and per-hop telemetry. Say the honest cost — a sidecar per Pod, added latency, and real operational complexity — and that you would only adopt it when you actually need mTLS everywhere or traffic-shaping the Ingress cannot express. That trade-off is what an 8-year interviewer is listening for.
- The `deployment.yaml` walkthrough should be delivered as a structured tour rather than a list: `apiVersion` and `kind`; `metadata` with name, namespace, labels, and annotations; then `spec` — `replicas`, the `selector.matchLabels` that must match the template, `strategy` with `rollingUpdate` `maxSurge` and `maxUnavailable`, `minReadySeconds`, and `revisionHistoryLimit`; then `spec.template` holding the Pod spec — labels, containers with image, ports, `env` and `envFrom`, `resources` requests and limits, probes, `volumeMounts`; and Pod-level fields such as `volumes`, `serviceAccountName`, `securityContext`, `nodeSelector`, `affinity`, `tolerations`, and `terminationGracePeriodSeconds`. Call out that the selector must match the template labels, because a mismatch is rejected. See [main components of Kubernetes architecture](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md).
- Init containers should be answered with purpose plus semantics: they run to completion, in order, _before_ any application container starts, sharing the Pod's volumes and network — so they are used to wait for a dependency, run a schema migration, fetch configuration or secrets, or set file permissions. The semantics that matter: if one fails the Pod restarts according to its `restartPolicy`, and they can carry tools you deliberately keep out of the slim runtime image. Contrast with sidecars, which run _alongside_ the application for its whole life. See [what a Pod is](../kubernetes/what-is-a-pod-in-kubernetes.md).
- ConfigMap versus Secret has a blunt answer worth giving plainly: functionally they are near-identical key-value objects, and a Secret is only base64-_encoded_, not encrypted. What differs is intent and handling — Secrets are not printed by default, can be encrypted at rest in etcd if you enable it, and should be locked down with RBAC. Say that for anything genuinely sensitive you would use an external store surfaced through the External Secrets Operator or the CSI driver, and that a secret mounted as a file can be updated on rotation while one injected as an environment variable cannot. See [managing secrets in CI/CD pipelines](../devsecops/how-do-you-manage-secrets-in-ci-cd-pipelines.md).
- The PodDisruptionBudget question is transcribed as "distribution" but means disruption. Define it as a constraint on _voluntary_ disruptions — `minAvailable` or `maxUnavailable` limiting how many replicas a drain or upgrade may take down at once — with no effect whatsoever when a node crashes. Add the failure mode: a PDB requiring 100% availability blocks node drains indefinitely, which is how cluster upgrades get stuck.
- Namespace-scoped user access is a two-part answer and the second part is where people slip. Create a Role in that namespace with the verbs and resources needed, then a RoleBinding in the same namespace binding the user, group, or service account to it. The detail worth adding: a RoleBinding can reference a _ClusterRole_ — so binding the built-in `edit` or `view` ClusterRole via a namespaced RoleBinding grants those permissions in that namespace only, which is the idiomatic way to do this. Finish with `kubectl auth can-i --as <user> -n <ns>` to verify. See [how RBAC works in Kubernetes](../kubernetes/how-does-rbac-work-in-kubernetes.md).
- The container runtime question wants the CRI story: the kubelet talks to a runtime over the Container Runtime Interface, the runtime pulls images and manages container lifecycles, and it delegates to a low-level runtime such as `runc` to create the namespaces and cgroups. Say `containerd` is what you use and why — it is the default on managed clusters, lighter than Docker Engine, and Docker's own runtime underneath — and note that dockershim was removed in Kubernetes 1.24, which is the follow-up. See [container runtime interface](../container-orchestration-advanced/what-is-container-runtime-interface-cri.md) and [Docker architecture](../docker/explain-docker-architecture.md).
- Corrupted Terraform state has an ordered recovery path: restore the previous object version from the versioned backend — which is exactly why versioning is mandatory — or fall back to `terraform.tfstate.backup`; inspect with `terraform state pull` and repair the JSON offline if the damage is small, then `terraform state push`; and if none of that works, rebuild by importing resources until `plan` is empty. Say what you would not do: apply against broken state, which recreates live infrastructure. See [recovering a lost or corrupted Terraform state file](../infrastructure-as-code/how-do-you-recover-a-lost-or-corrupted-terraform-state-file.md).
- On `lifecycle`, cover the four arguments and be precise about `create_before_destroy`: it inverts the default order so the replacement is created before the original is destroyed, which is how you replace a resource with no gap — and note that it propagates to dependencies, which can surprise you. Then `prevent_destroy` as a guard, `ignore_changes` for externally mutated fields, and `replace_triggered_by`.
- Service types should each come with a use case: ClusterIP for internal-only and the default; NodePort exposing a port in the 30000-32767 range on every node; LoadBalancer having the cloud provision a real load balancer; ExternalName aliasing an external DNS name; and headless (`clusterIP: None`) for direct per-Pod addressing, which is what StatefulSets use. See [what a Service is in Kubernetes](../kubernetes/what-is-a-service-in-kubernetes.md).
- For the cron expression, give the five fields in order — minute, hour, day of month, month, day of week — with a worked example such as `0 2 * * *` for 02:00 daily, and mention that a Kubernetes `CronJob` uses the same syntax plus `concurrencyPolicy` and `startingDeadlineSeconds`. Say that `systemd` timers are the modern alternative on a host because they log to the journal and handle missed runs. See [basic Linux commands](../linux-administration/what-are-the-basic-linux-commands-every-devops-engineer-should-know.md).
- "Which Kubernetes resources do you know?" is a breadth question, so group them rather than listing at random — workloads, networking, configuration, storage, access control, and operations — and then name the ones you have actually authored. Grouping reads as understanding; a flat list reads as recall.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)
- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
