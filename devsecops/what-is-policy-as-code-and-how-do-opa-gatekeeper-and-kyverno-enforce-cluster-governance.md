---
title: "What is Policy as Code and how do OPA Gatekeeper and Kyverno enforce cluster governance?"
id: 707
category: "DevSecOps"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - devsecops
  - policy-as-code
  - opa
  - kyverno
  - governance
quiz:
  stem: "What is the primary operational advantage of Kyverno over OPA Gatekeeper for Kubernetes platform teams?"
  options:
    - "Kyverno runs without a Kubernetes cluster"
    - "Kyverno policies are written in native Kubernetes YAML rather than requiring engineers to learn the complex Rego programming language"
    - "Kyverno eliminates the need for container images"
    - "Kyverno only functions on Windows nodes"
  answer: 2
  explanation: "Kyverno uses standard Kubernetes YAML patterns, allowing teams to author validation, mutation, and generation rules without learning OPA's specialized Rego language."
---

# What is Policy as Code and how do OPA Gatekeeper and Kyverno enforce cluster governance?

**Short answer:** Policy as Code treats security and operational guardrails as version-controlled code; OPA Gatekeeper (using Rego) and Kyverno (using native YAML) enforce rules at admission time to reject non-compliant resources (e.g. running as root, missing CPU limits, pulling from untrusted registries).

## Detail

Telling developers 'please do not run containers as root' in a PDF wiki does not work. Policy as Code turns guidelines into automated, non-bypassable guardrails:

### OPA Gatekeeper vs Kyverno

| Feature        | OPA Gatekeeper                                                            | Kyverno                                                                        |
| -------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Language       | **Rego** (Declarative query language)                                     | **Native Kubernetes YAML**                                                     |
| Learning Curve | High (requires learning Rego)                                             | Low (anyone who knows Kubernetes YAML can author policies)                     |
| Mutation       | Supported via mutation webhooks                                           | Excellent native mutation and resource generation                              |
| Ecosystem      | OPA/Rego is general-purpose: Terraform plans (Conftest), Envoy, APIs, K8s | Kubernetes-first; the Kyverno CLI and JSON policies can also check files in CI |

### Kyverno Policy Example (Reject Root Containers)

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-root-user
spec:
  rules:
    - name: check-runasnonroot
      match:
        any:
          - resources:
              kinds: ["Pod"]
      validate:
        failureAction: Enforce # per-rule since Kyverno 1.13; spec.validationFailureAction is deprecated
        message: "Running as root is forbidden. Set securityContext.runAsNonRoot: true"
        pattern:
          spec:
            securityContext:
              runAsNonRoot: true
```

## Example

The same rule in Gatekeeper is two objects - a `ConstraintTemplate` holding the Rego, and a `Constraint` applying it:

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequirenonroot
spec:
  crd:
    spec:
      names:
        kind: K8sRequireNonRoot
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequirenonroot

        violation[{"msg": msg}] {
          not input.review.object.spec.securityContext.runAsNonRoot
          msg := "Pod must set spec.securityContext.runAsNonRoot: true"
        }
---
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequireNonRoot
metadata:
  name: pods-must-run-as-non-root
spec:
  enforcementAction: dryrun # audit first; switch to deny once violations are cleaned up
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
```

```bash
# Shift the same policies left: test manifests in CI before they reach the cluster
kyverno apply ./policies/ --resource ./k8s/deployment.yaml
```

## Interview tips

- Frame policy as code by its properties: versioned, reviewed, tested, and enforced automatically - the same lifecycle as application code.
- Enforce in more than one place: CI (fast feedback via `kyverno apply`/`kyverno test` or Conftest), admission (the real gate), and background audit (catches resources that existed before the policy).
- Roll out in audit/dry-run mode first and read the reports; flipping straight to enforce is how you block a production rollout at 2 a.m.
- Mention the built-in option: **ValidatingAdmissionPolicy** (CEL, GA since Kubernetes 1.30) handles simple validations in-process without a webhook, and both Kyverno and Gatekeeper can generate or use it. Webhook engines remain the choice for mutation, generation, image verification, and complex logic.
- Trade-off to name: webhooks add latency and a failure mode - decide `failurePolicy` deliberately and exclude system namespaces so a policy-engine outage cannot stop the control plane healing itself.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you integrate SonarQube and quality gates into a pipeline?]] (`#458`): [How do you integrate SonarQube and quality gates into a pipeline?](../cicd/how-do-you-integrate-sonarqube-and-quality-gates-into-a-pipeline.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevSecOps](./README.md) · [All topics](../README.md)
