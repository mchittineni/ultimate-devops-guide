---
title: "What is Compliance as Code?"
id: 39
category: "Security and Compliance"
difficulty: "Advanced"
tags:
  - devops
  - security-and-compliance
  - interview-questions
---

# What is Compliance as Code?

**Short answer:** Compliance as Code expresses regulatory and internal control requirements as executable policies that are enforced automatically in pipelines and at runtime, producing continuous evidence instead of periodic manual audits.

## Detail

Traditional compliance is a point-in-time exercise: screenshots, spreadsheets, and an auditor's sample. Between audits, drift goes undetected. Compliance as Code turns each control into a test that runs constantly.

**How it is implemented:**

- **Policy engines** - Open Policy Agent with Rego, or Kyverno for Kubernetes-native YAML policies. Policies evaluate resource definitions and return allow/deny with a reason.
- **Pipeline gates** - `conftest` or `checkov` evaluate Terraform plans and Kubernetes manifests before anything is applied. A non-compliant change fails the pull request.
- **Admission control** - the cluster rejects non-compliant workloads at the API server, so the control holds even for changes that bypass CI.
- **Continuous cloud posture checks** - AWS Config rules, Azure Policy, or Cloud Custodian evaluate live resources and can auto-remediate.
- **Evidence generation** - every policy evaluation is logged, giving auditors a continuous, queryable record mapped to control IDs (SOC 2 CC6.1, PCI DSS v4.0.1 Req 3.5.1, and so on). Cite the current numbering - v3.2.1 retired in March 2024 and v4.x renumbered heavily, so the old "PCI-DSS 3.4" style reference dates an answer immediately.

The cultural benefit is that requirements stop being a PDF nobody reads: they become failing tests with a clear message telling the engineer exactly what to change.

## Example

```rego
package kubernetes.admission

deny[msg] {
  input.request.kind.kind == "Pod"
  c := input.request.object.spec.containers[_]
  not c.securityContext.runAsNonRoot
  msg := sprintf("SOC2 CC6.1: container '%s' must set runAsNonRoot", [c.name])
}
```

```bash
conftest test terraform-plan.json --policy policy/   # gate in CI
```

## Interview tips

- Map policies to named control IDs - that is what makes it _compliance_ rather than just linting.
- Explain defence in depth: the same rule in CI (fast feedback) and admission control (enforcement).
- Note that auto-remediation needs care; start in audit mode, measure, then enforce.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you manage TLS certificates in production?]] (`#491`): [How do you manage TLS certificates in production?](../network-security/how-do-you-manage-tls-certificates-in-production.md)
- [[What does a DevSecOps pipeline look like end to end?]] (`#161`): [What does a DevSecOps pipeline look like end to end?](../devsecops/what-does-a-devsecops-pipeline-look-like-end-to-end.md)
- [[What is the difference between SAST, DAST, IAST, and SCA?]] (`#162`): [What is the difference between SAST, DAST, IAST, and SCA?](../devsecops/what-is-the-difference-between-sast-dast-iast-and-sca.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Security and Compliance](./README.md) · [All topics](../README.md)
