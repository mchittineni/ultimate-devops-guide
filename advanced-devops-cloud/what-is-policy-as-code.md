---
title: "What is Policy as Code?"
id: 143
category: "Advanced DevOps & Cloud"
difficulty: "Advanced"
tags:
  - devops
  - advanced-devops-cloud
  - interview-questions
---

# What is Policy as Code?

**Short answer:** Policy as code expresses governance rules — security, compliance, cost, and operational standards — as executable code that is version-controlled, tested, and enforced automatically in pipelines and at runtime.

## Detail

**Why.** Written policies in a wiki are advisory, unevenly applied, and unverifiable. Policy as code makes rules deterministic, reviewable, and enforced at the moment of change, with the reason returned to the engineer immediately.

**Where policies are enforced** — layered, because each catches what the others miss:

- **Pre-commit / IDE** — instant feedback while writing.
- **Pull request** — `conftest`, `checkov`, `tfsec` evaluating Terraform plans and manifests. Fast feedback, but bypassable.
- **Admission control** — OPA Gatekeeper or Kyverno rejecting non-compliant resources at the Kubernetes API server. Not bypassable.
- **Cloud runtime** — AWS Config rules, Azure Policy, or SCPs that detect and sometimes remediate drift in live resources.

**Tools:** Open Policy Agent with the Rego language (general-purpose, works across Kubernetes, Terraform, CI, and application authorisation), Kyverno (Kubernetes-native YAML policies, easier for Kubernetes-only use, and can mutate as well as validate), Sentinel (HashiCorp), and Cloud Custodian for cloud resource policies with remediation.

**Good practice:** treat policies like any other code — unit tests for each rule, a repository with review, staged rollout from audit mode to enforcement, and clear violation messages that tell the engineer exactly how to fix the problem. A policy that says "denied by policy 47" wastes everyone's time.

## Example

```yaml
# Kyverno: require resource limits, and report before enforcing
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: require-resource-limits }
spec:
  validationFailureAction: Audit # switch to Enforce after review
  rules:
    - name: check-limits
      match: { any: [{ resources: { kinds: [Pod] } }] }
      validate:
        message: "Every container must set CPU and memory limits."
        pattern:
          spec:
            containers:
              - resources:
                  limits: { memory: "?*", cpu: "?*" }
```

## Interview tips

- Audit mode before enforcement is the rollout practice that avoids breaking every team at once.
- Layering CI checks with admission control — fast feedback plus real enforcement — is the architecture point.
- Emphasise actionable violation messages; it is what determines whether engineers accept the system.

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
