---
title: "What are Pod Security Standards and how does Pod Security Admission enforce them?"
id: 753
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - kubernetes
  - interview-questions
  - devsecops
quiz:
  stem: "A namespace is labelled `pod-security.kubernetes.io/enforce: restricted`. What happens to an existing Deployment whose Pods run as root?"
  options:
    - "Its running Pods are evicted immediately"
    - "Running Pods keep running, but new Pods it tries to create are rejected at admission"
    - "The Deployment object itself is deleted"
    - "Nothing, because Pod Security Admission only audits"
  answer: 2
  explanation: "Pod Security Admission evaluates Pods when they are created or updated. Existing Pods are not touched, but the ReplicaSet's next Pod creation (scale-up, rollout, node drain) is denied - which is why you roll out with warn and audit modes first."
---

# What are Pod Security Standards and how does Pod Security Admission enforce them?

**Short answer:** The **Pod Security Standards** are three Kubernetes-defined policy levels for Pod `securityContext` and host access: **`privileged`** (no restrictions), **`baseline`** (blocks known privilege escalations such as `privileged: true`, `hostNetwork`, `hostPID`, `hostPath`, and added dangerous capabilities), and **`restricted`** (baseline plus hardening: must run as non-root, `allowPrivilegeEscalation: false`, drop `ALL` capabilities, a `RuntimeDefault` or `Localhost` seccomp profile). **Pod Security Admission** is the built-in admission controller (GA since 1.25, replacing PodSecurityPolicy, which was removed in 1.25) that applies a level per namespace through labels, in three modes: `enforce` rejects violating Pods, `warn` returns a warning to the client, and `audit` writes an audit annotation. It is simple and always available, but it is namespace-granular with no per-workload exceptions, so finer policy still needs Kyverno, Gatekeeper, or `ValidatingAdmissionPolicy`.

## Detail

### The three levels

| Level        | Intended for                                   | Examples of what it forbids                                                                                                                                                                                                                                             |
| ------------ | ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `privileged` | System and infrastructure workloads (CNI, CSI) | Nothing                                                                                                                                                                                                                                                                 |
| `baseline`   | Ordinary apps, minimal friction                | `privileged`, host namespaces, `hostPath`, `hostPort`, adding capabilities beyond a safe set, unsafe sysctls, `Unconfined` AppArmor/seccomp                                                                                                                             |
| `restricted` | Security-sensitive or multi-tenant namespaces  | Everything in baseline, plus root (`runAsNonRoot` required), privilege escalation, any capability except `NET_BIND_SERVICE`, missing seccomp profile, volume types other than the safe list (no `hostPath`, but PVC, `emptyDir`, ConfigMap, Secret, projected are fine) |

### How Pod Security Admission applies them

Labels on the namespace choose the level per mode, optionally pinned to a policy version:

```text
pod-security.kubernetes.io/enforce: restricted
pod-security.kubernetes.io/enforce-version: v1.36   # or "latest"
pod-security.kubernetes.io/warn: restricted
pod-security.kubernetes.io/audit: restricted
```

- **Pods are checked on create and update.** Existing Pods are never evicted, which makes the failure mode subtle: tightening a label breaks the workload later, the next time its controller creates a Pod.
- **Workload objects get warnings, not rejections.** A Deployment that would produce violating Pods is accepted with a `warn` message; the ReplicaSet's Pod creation is what fails, visible as `FailedCreate` events on the ReplicaSet.
- **Version pinning** (`enforce-version`) stops a cluster upgrade from silently tightening a level when the standard gains a new check.
- **Cluster-wide defaults and exemptions** live in the API server's `AdmissionConfiguration` for the `PodSecurity` plugin: default levels for unlabelled namespaces, and exemptions by username, RuntimeClass, or namespace (typically `kube-system`). There are no per-Pod or per-container exemptions.
- A dry-run tells you the impact before you enforce: `kubectl label --dry-run=server --overwrite ns <ns> pod-security.kubernetes.io/enforce=restricted` lists every existing Pod that would violate it.

### PSA versus a policy engine

| Need                                                           | PSA | Kyverno / Gatekeeper / ValidatingAdmissionPolicy |
| -------------------------------------------------------------- | --- | ------------------------------------------------ |
| Baseline security for every namespace, zero install            | Yes | Possible, more work                              |
| Per-workload exceptions ("this one DaemonSet needs NET_ADMIN") | No  | Yes                                              |
| Non-security rules (approved registries, required labels)      | No  | Yes                                              |
| Mutation (inject a default `securityContext`)                  | No  | Kyverno, MutatingAdmissionPolicy                 |
| Image signature verification                                   | No  | Kyverno, Sigstore policy-controller              |

The common production setup is both: PSA `restricted` (or `baseline`) as the floor on every application namespace, and a policy engine for everything PSA cannot express.

## Example

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: payments
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: v1.36
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted
---
# A Pod that passes `restricted`
apiVersion: v1
kind: Pod
metadata: { name: api, namespace: payments }
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    seccompProfile: { type: RuntimeDefault }
  containers:
    - name: api
      image: registry.example.com/api:1.9.0
      securityContext:
        allowPrivilegeEscalation: false
        capabilities: { drop: ["ALL"] }
```

```bash
# What would break if I enforced restricted here? (no change is made)
kubectl label --dry-run=server --overwrite ns payments pod-security.kubernetes.io/enforce=restricted
# Warning: existing pods in namespace "payments" violate the new PodSecurity enforce level "restricted:latest"
# Warning: legacy-worker-6c9f: allowPrivilegeEscalation != false, runAsNonRoot != true

# Why did my Deployment stop creating Pods?
kubectl get events -n payments --field-selector reason=FailedCreate
# ... violates PodSecurity "restricted:v1.36": runAsNonRoot != true
```

## Interview tips

- Name the three levels and one concrete rule each - baseline blocks `privileged` and host namespaces, restricted adds non-root, no escalation, dropped capabilities, and seccomp.
- Explain the three modes and the rollout order: `warn` and `audit` first, a server-side dry-run, then `enforce`.
- Point out that PSA checks Pods, not Deployments, and never evicts running Pods - so a tightened label shows up later as `FailedCreate` on a ReplicaSet.
- Know the history: PodSecurityPolicy was removed in 1.25 and PSA is its built-in replacement.
- Be balanced about limits: namespace-level only, no per-workload exceptions, no mutation, so pair it with Kyverno, Gatekeeper, or CEL admission policies. See [why should you avoid running containers as root](../docker/why-should-you-avoid-running-containers-as-the-root-user-and-how-do-you-enforce-non-root-execution.md), [mutating and validating admission webhooks](./what-is-the-difference-between-mutating-and-validating-admission-webhooks-in-kubernetes.md), and [running a multi-tenant cluster](../container-orchestration-advanced/how-do-you-run-a-multi-tenant-kubernetes-cluster.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do you run a multi-tenant Kubernetes cluster?]] (`#453`): [How do you run a multi-tenant Kubernetes cluster?](../container-orchestration-advanced/how-do-you-run-a-multi-tenant-kubernetes-cluster.md)
- [[What are Custom Resource Definitions (CRDs) and how do Custom Operators extend the Kubernetes API?]] (`#623`): [What are Custom Resource Definitions (CRDs) and how do Custom Operators extend the Kubernetes API?](../container-orchestration-advanced/what-are-custom-resource-definitions-crds-and-how-do-custom-operators-extend-the-kubernetes-api.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
