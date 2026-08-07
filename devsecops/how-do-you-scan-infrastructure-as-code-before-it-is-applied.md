---
title: "How do you scan Infrastructure as Code before it is applied?"
id: 167
category: "DevSecOps"
difficulty: "Intermediate"
tags:
  - devops
  - devsecops
  - interview-questions
---

# How do you scan Infrastructure as Code before it is applied?

**Short answer:** Run two layers on every pull request: static scanners over the templates (Checkov, `trivy config`, tfsec) for known misconfigurations, and policy-as-code over the Terraform _plan_ (OPA/Conftest, Sentinel) for organisation-specific rules. Plan-based checks are the stronger gate because they see resolved values, modules, and what will actually change.

## Detail

**Template scanning versus plan scanning.** A scanner reading `.tf` files cannot resolve a variable supplied at apply time, so it either guesses or misses. `terraform plan -out` converted to JSON gives you the concrete resource attributes, including values coming from modules and data sources. Use template scanning for fast feedback in the editor and plan scanning as the merge gate.

**What the rules should cover.** Public storage buckets and unrestricted security groups are table stakes. The rules that pay for themselves are organisation-specific: mandatory tags (owner, cost-centre, data-classification), approved regions, encryption with customer-managed keys, no IAM wildcards, no public IPs on database subnets, instance types from an approved list.

**Detect destructive changes, not just insecure ones.** A plan that deletes a database or replaces a stateful resource deserves a distinct, louder gate than a lint warning — for example, requiring a second approval when the plan contains `delete` on any resource of a protected type.

**Close the loop at run time.** Pre-apply scanning cannot catch a console change. Pair it with drift detection and a CSPM/Config-rules layer evaluating live resources against the same policy set — ideally the same Rego, so there is one definition of "compliant".

**Keep the failure actionable.** Output the file, line, rule ID, and remediation. Suppressions live inline (`#checkov:skip=CKV_AWS_18:access logs go to the central account`) with a reason, so reviewers see the justification in the diff.

## Example

```bash
# Fast layer: template scan on every PR
trivy config . --severity HIGH,CRITICAL --exit-code 1

# Strong layer: policy over the resolved plan
terraform plan -out=tf.plan
terraform show -json tf.plan > tf.json
conftest test --policy ./policy tf.json
```

```rego
# policy/tags.rego — every taggable resource must carry an owner
package main

required := {"owner", "cost_center", "data_classification"}

deny contains msg if {
  rc := input.resource_changes[_]
  rc.change.actions[_] in {"create", "update"}
  startswith(rc.type, "aws_")
  tags := object.get(rc.change.after, "tags", {})
  missing := required - {k | some k, _ in tags}
  count(missing) > 0
  msg := sprintf("%s is missing tags: %v", [rc.address, missing])
}
```

## Interview tips

- The plan-versus-template distinction is the point interviewers are probing; lead with it.
- Mention one org-specific rule you have written — it separates "I enabled a scanner" from "I own the guardrails".
- Follow-up to expect: "how do you stop someone changing it in the console?" — drift detection plus the same policy evaluated against live state, and SCPs/Azure Policy denying it outright.

---

[⬅ Back to DevSecOps](./README.md) · [All topics](../README.md)
