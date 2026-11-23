---
title: "What are labels and selectors in Kubernetes, and where are they used?"
id: 791
category: "Kubernetes"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - kubernetes
  - labels
  - selectors
  - services
quiz:
  stem: "You need to change the `spec.selector` of an existing `apps/v1` Deployment. What happens?"
  options:
    - "The Deployment updates and adopts matching Pods automatically"
    - "The API server rejects the change because the selector is immutable, so you create a new Deployment instead"
    - "The selector changes, but only for Pods created after the update"
    - "Kubernetes converts the selector into an annotation"
  answer: 2
  explanation: "In apps/v1 a Deployment's spec.selector is immutable after creation and must match the Pod template labels. Changing it means creating a new Deployment and moving traffic before deleting the old one."
---

# What are labels and selectors in Kubernetes, and where are they used?

**Short answer:** **Labels** are key/value pairs attached to any Kubernetes object, such as `app.kubernetes.io/name: web` or `env: prod`. **Selectors** are queries over those labels. They are how loosely coupled objects find each other: a Deployment's ReplicaSet owns the Pods its selector matches, a Service sends traffic to the Pods its selector matches, and NetworkPolicies, PodDisruptionBudgets, and node scheduling rules all pick their targets the same way. Labels identify things; **annotations** hold non-identifying metadata and cannot be selected on.

## Detail

**Labels.** Any object can carry them: Pods, Nodes, Services, PVCs, Namespaces. A key may have an optional DNS prefix (`app.kubernetes.io/name`, `team`), and both the name part and the value are limited to 63 characters. The project recommends a common set: `app.kubernetes.io/name`, `instance`, `version`, `component`, `part-of`, and `managed-by`. Organisations usually add their own, such as `team` and `env`, for ownership and cost reporting.

**Two kinds of selector.**

- **Equality-based** - `app=web`, `env!=dev`. In YAML this is `matchLabels`, a plain map where every pair must match.
- **Set-based** - `env in (prod,staging)`, `tier notin (cache)`, `team` (the key exists), `!canary` (the key does not exist). In YAML this is `matchExpressions` with the operators `In`, `NotIn`, `Exists`, and `DoesNotExist`.

Services support only the equality form (`spec.selector` is a map). Deployments, ReplicaSets, StatefulSets, Jobs, PDBs, and NetworkPolicies accept both.

**Where selectors are used.**

| Consumer                                           | What it selects                                             |
| -------------------------------------------------- | ----------------------------------------------------------- |
| Deployment, ReplicaSet, StatefulSet                | The Pods it owns and counts towards `replicas`              |
| Service                                            | The Pods that become its endpoints                          |
| NetworkPolicy (`podSelector`, `namespaceSelector`) | Which Pods the policy applies to, and allowed peers         |
| PodDisruptionBudget                                | Which Pods the budget protects                              |
| `nodeSelector`, node affinity                      | Nodes, by node labels such as `topology.kubernetes.io/zone` |
| Pod affinity, anti-affinity, topology spread       | Other Pods to place near or away from                       |
| `kubectl get -l`, `kubectl delete -l`              | Ad hoc queries and bulk operations                          |

**Rules that cause real incidents.**

- A Deployment's `spec.selector` must match its Pod template labels and is **immutable** in `apps/v1`. Changing the selector means a new Deployment.
- Selectors that **overlap** between two controllers or two Services cause surprises. Two Deployments whose Pods share `app: web` will both be picked up by a Service that selects only `app: web`, which is how canary Pods leak into stable traffic.
- Changing a running Pod's labels takes it out of its ReplicaSet (which creates a replacement) and out of any Service. This is useful for quarantining a misbehaving Pod for debugging while traffic moves elsewhere.
- Labels are not a place for large or frequently changing data; that belongs in annotations.

## Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: web-stable }
spec:
  replicas: 3
  selector:
    matchLabels: { app.kubernetes.io/name: web, track: stable } # immutable after creation
  template:
    metadata:
      labels: { app.kubernetes.io/name: web, track: stable, team: storefront }
    spec:
      containers:
        - { name: web, image: nginx:1.27 }
---
apiVersion: v1
kind: Service
metadata: { name: web }
spec:
  selector: { app.kubernetes.io/name: web, track: stable } # canary Pods (track: canary) are excluded
  ports: [{ port: 80, targetPort: 80 }]
```

```bash
kubectl get pods -l 'app.kubernetes.io/name=web,track in (stable,canary)' --show-labels
kubectl get pods -L team,track                                   # labels as columns
kubectl get endpointslices -l kubernetes.io/service-name=web     # which Pod IPs the Service picked
kubectl label pod web-stable-5d8c7-abcde track=quarantine --overwrite   # pull one Pod out of the Service
```

## Interview tips

- The usual answer is "labels tag Pods and selectors in Deployments and Services find them." Widen it: any object can be labelled, and NetworkPolicies, PDBs, node scheduling, and topology spread all rely on selectors.
- Name both selector types and note that a Service only supports the equality form.
- Mention that a Deployment's selector is immutable, and that overlapping selectors are a classic cause of traffic going to the wrong Pods.
- Separate labels (identifying, selectable) from annotations (tool configuration, checksums, descriptions).
- A good follow-up answer: relabelling a Pod to remove it from a Service is a quick way to keep a broken Pod for debugging.

**Telling it as a STAR story** (an adaptable example)

- **Situation:** During a canary release, the stable Service started sending a share of traffic to canary Pods, because both Deployments labelled their Pods only `app: web`.
- **Task:** Stop the leak and introduce labelling that kept selectors predictable.
- **Action:** `kubectl get endpointslices -l kubernetes.io/service-name=web` showed canary IPs behind the stable Service. Because a Deployment selector is immutable, I created a new stable Deployment whose Pods carried `track: stable`, waited for it to be Ready, added `track: stable` to the Service selector, and only then removed the old Deployment. Canary Pods got `track: canary`. I then put a standard label set (`app.kubernetes.io/*`, `team`, `env`) into our Helm library chart and added an admission policy that requires it.
- **Result:** Canaries stayed isolated in later releases, and the consistent `team` label let us report cluster cost per team.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[Why does a container image that works locally fail on Kubernetes or ECS?]] (`#793`): [Why does a container image that works locally fail on Kubernetes or ECS?](../docker/why-does-a-container-image-that-works-locally-fail-on-kubernetes-or-ecs.md)
- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)
- [[How do you troubleshoot a failed Helm release?]] (`#412`): [How do you troubleshoot a failed Helm release?](../container-orchestration-advanced/how-do-you-troubleshoot-a-failed-helm-release.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
