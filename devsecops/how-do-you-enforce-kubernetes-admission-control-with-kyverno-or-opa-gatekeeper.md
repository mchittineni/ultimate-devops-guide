---
title: "How do you enforce Kubernetes admission control with Kyverno or OPA Gatekeeper?"
id: 244
category: "DevSecOps"
difficulty: "Intermediate"
tags:
  - devops
  - devsecops
  - interview-questions
---

# How do you enforce Kubernetes admission control with Kyverno or OPA Gatekeeper?

**Short answer:** Enforce Kubernetes security admission control by deploying dynamic Admission Webhooks via Kyverno or OPA Gatekeeper to validate, mutate, or block non-compliant resource manifests (such as enforcing non-root container users, mandatory resource requests/limits, disallowing privileged containers, and requiring trusted image registry signatures).

## Detail

Admission Controllers act as gatekeepers before Kubernetes objects are persisted into `etcd`. Policy as Code (PaC) tools validate or mutate requests at admission time:

### 1. Kyverno vs OPA Gatekeeper

- **Kyverno:** Kubernetes-native policy engine written specifically for Kubernetes. Policies are declared as standard YAML Custom Resources (`ClusterPolicy`) without requiring a learning curve for a new query language.
- **OPA Gatekeeper:** Uses Open Policy Agent and **Rego** declarative policy language. Highly extensible across microservices, CI/CD, and multi-cloud infrastructure, but requires writing Rego policies and constraint templates.

### 2. Core Policy Enforcement Scenarios

- **Disallowing Privileged Containers:** Block any Pod requesting `securityContext.privileged: true` or host network/PID namespaces.
- **Enforcing Non-Root Execution:** Mutate or validate container specifications to enforce `runAsNonRoot: true` and `readOnlyRootFilesystem: true`.
- **Mandatory Tags & Labels:** Require all Namespaces and Deployments to include `owner`, `cost-center`, and `environment` labels.
- **Allowed Container Registries:** Block pulling container images from unauthorized public registries (e.g. allow only `123456789012.dkr.ecr.us-east-1.amazonaws.com/*`).

### 3. Policy Execution Modes: Audit vs Enforce

- **Audit Mode (`validate.failureAction: Audit`):** Log policy violations to PolicyReports, metrics, and events without blocking deployment pipelines. Used when introducing new policies to production clusters to measure impact.
- **Enforce Mode (`validate.failureAction: Enforce`):** Reject non-compliant `kubectl apply` requests immediately with an explicit error message.
- **Set it per rule, not per policy.** Kyverno 1.13 deprecated the policy-wide `spec.validationFailureAction` (and `spec.validationFailureActionOverrides`) in favour of `spec.rules[].validate.failureAction` and `.failureActionOverrides`, and the old fields are scheduled for removal. Per-rule control is also what you want operationally: a new rule can ship in Audit alongside rules already enforcing in the same policy.

## Example

Kyverno ClusterPolicy blocking privileged containers and requiring non-root execution:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-privileged-and-require-non-root
spec:
  background: true
  rules:
    - name: check-privileged-containers
      match:
        any:
          - resources:
              kinds:
                - Pod
      validate:
        failureAction: Enforce # per-rule since Kyverno 1.13; spec.validationFailureAction is deprecated
        message: "Privileged containers are disallowed in this cluster!"
        pattern:
          spec:
            containers:
              - =(securityContext):
                  =(privileged): false
    - name: check-run-as-non-root
      match:
        any:
          - resources:
              kinds:
                - Pod
      validate:
        failureAction: Enforce
        message: "Containers must run as non-root (securityContext.runAsNonRoot must be true)."
        pattern:
          spec:
            securityContext:
              runAsNonRoot: true
```

OPA Gatekeeper Constraint enforcing allowed container image registries:

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sAllowedRepos
metadata:
  name: prod-allowed-repos
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
  parameters:
    repos:
      - "123456789012.dkr.ecr.us-east-1.amazonaws.com/"
      - "ghcr.io/my-org/"
```

## Interview tips

- Compare **Kyverno** (YAML-native, easier K8s adoption) with **OPA Gatekeeper** (Rego language, cross-system policy engine beyond Kubernetes).
- Always mention starting new policies in **Audit mode** before moving to **Enforce mode** to prevent accidental pipeline downtime.
- Explain admission controller mechanics: `ValidatingWebhookConfiguration` (blocks or allows) runs after `MutatingWebhookConfiguration` (modifies requests defaults).

---

[⬅ Back to DevSecOps](./README.md) · [All topics](../README.md)
