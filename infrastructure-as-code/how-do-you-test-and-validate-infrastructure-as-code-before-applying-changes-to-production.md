---
title: "How do you test and validate Infrastructure as Code before applying changes to production?"
id: 552
category: "Infrastructure as Code"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - iac
  - terraform
  - testing
  - opa
  - tflint
quiz:
  stem: "Which tool in the IaC testing workflow validates organizational policy compliance (such as requiring cost center tags and restricting cloud regions) before deployment?"
  options:
    - "Terraform fmt"
    - "Open Policy Agent (OPA) / Conftest"
    - "Docker Compose"
    - "Prometheus Alertmanager"
  answer: 2
  explanation: "Open Policy Agent (OPA) and Conftest allow security and platform teams to author Policy as Code assertions over Terraform JSON plans before infrastructure is provisioned."
---

# How do you test and validate Infrastructure as Code before applying changes to production?

**Short answer:** Testing IaC involves a pyramid of automated checks: static syntax and linting (`tflint`), security and policy scanning (`trivy`, `checkov`, OPA/Conftest), native unit testing (`terraform test`), and ephemeral end-to-end integration testing.

## Detail

Treating infrastructure as software requires testing before `terraform apply`:

### The IaC Testing Pyramid

1. **Linting & Formatting (Pre-commit/CI)**:
   - `terraform fmt -check` (style consistency).
   - `tflint` (catches invalid cloud provider configurations, like invalid EC2 instance types, before running plan).
2. **Security & Policy-as-Code (Static Analysis)**:
   - `checkov` / `trivy config` (Trivy absorbed tfsec, which is no longer developed): Scans for security antipatterns (e.g., S3 buckets without encryption, open `0.0.0.0/0` SSH security groups).
   - **Open Policy Agent (OPA) / Conftest**: Enforces organizational guardrails (e.g., mandatory cost tags, allowed AWS regions).
3. **Speculative Planning**:
   - `terraform plan -detailed-exitcode` in PR to inspect proposed diffs, and policy (OPA/Conftest, Sentinel) evaluated against `terraform show -json` of that plan - the only check that sees the real change, including replacements and deletions.
4. **Unit tests with `terraform test` (Terraform 1.6+, `tofu test` in OpenTofu)**:
   - `.tftest.hcl` files run `plan` or `apply` and assert on the result. With `command = plan` and `mock_provider` (1.7+) they run in seconds with no cloud credentials - good for validating variable validation, naming, and conditional logic.
5. **Integration Testing (`terraform test` with `command = apply`, or Terratest)**:
   - Spawns real ephemeral infrastructure in a sandbox account, validates HTTP/health endpoints, and runs `terraform destroy`.

### Trade-offs

Each layer up the pyramid is slower, more expensive, and more realistic. Static scanners and mocked tests cannot see provider-side behaviour (API validation, eventual consistency, quota limits); real-apply tests can, but cost money, take minutes to tens of minutes, and leave orphaned resources if teardown fails - so run them in a dedicated account with a nuke/cleanup job, typically on module changes rather than on every commit.

## Example

```hcl
# tests/naming.tftest.hcl - fast unit test: plan only, mocked provider, no credentials
mock_provider "aws" {}

variables {
  name = "payments"
  cidr = "10.20.0.0/16"
  azs  = ["eu-west-1a", "eu-west-1b"]
}

run "vpc_is_named_and_tagged" {
  command = plan

  assert {
    condition     = aws_vpc.this.tags["Name"] == "payments"
    error_message = "VPC Name tag must equal var.name"
  }
}

run "rejects_bad_names" {
  command = plan
  variables {
    name = "Payments_Prod"
  }
  expect_failures = [var.name] # the validation block must reject this
}
```

```bash
# The pipeline, cheapest first
terraform fmt -check -recursive
terraform init -backend=false && terraform validate
tflint --recursive
checkov -d . --framework terraform         # or: trivy config .
terraform test                             # unit tests above, seconds
terraform plan -out=tfplan && terraform show -json tfplan > tfplan.json
conftest test tfplan.json --policy policy/ # organisational guardrails on the real change
```

## Interview tips

- Present it as a pyramid with cost and speed trade-offs, and say which layers run on every PR (fmt, validate, lint, scan, mocked tests, plan + policy) versus less often (real-apply integration tests).
- Distinguish scanning the code from evaluating policy on the plan JSON - only the plan shows replacements and deletions.
- Know the native framework: `.tftest.hcl`, `run` blocks, `command = plan` vs `apply`, `expect_failures`, and `mock_provider`.
- Name the limit of static checks: they cannot catch what the cloud API will reject or how it behaves at runtime.
- Likely follow-up: "how do you stop integration tests leaving resources behind?" - a dedicated sandbox account, unique name prefixes per run, and a scheduled cleanup job.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between mutable and immutable infrastructure in modern deployment patterns?]] (`#586`): [What is the difference between mutable and immutable infrastructure in modern deployment patterns?](../configuration-management/what-is-the-difference-between-mutable-and-immutable-infrastructure-in-modern-deployment-patterns.md)
- [[How do you test Ansible roles using Molecule and testinfra in CI/CD pipelines?]] (`#588`): [How do you test Ansible roles using Molecule and testinfra in CI/CD pipelines?](../configuration-management/how-do-you-test-ansible-roles-using-molecule-and-testinfra-in-ci-cd-pipelines.md)
- [[How do you detect, isolate, and eradicate flaky tests in a CI/CD pipeline?]] (`#536`): [How do you detect, isolate, and eradicate flaky tests in a CI/CD pipeline?](../cicd/how-do-you-detect-isolate-and-eradicate-flaky-tests-in-a-ci-cd-pipeline.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
