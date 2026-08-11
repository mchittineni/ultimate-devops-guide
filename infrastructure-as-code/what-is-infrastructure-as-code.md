---
title: "What is Infrastructure as Code?"
id: 26
category: "Infrastructure as Code"
difficulty: "Beginner"
tags:
  - devops
  - infrastructure-as-code
  - interview-questions
---

# What is Infrastructure as Code?

**Short answer:** Infrastructure as Code is the practice of defining infrastructure in machine-readable files that are version-controlled, reviewed, and applied automatically - so environments are reproducible rather than hand-built.

## Detail

IaC replaces console clicking and runbook typing with declarative definitions committed to Git. That single change brings the whole software engineering toolkit to infrastructure: code review, history, blame, branching, testing, and rollback.

Benefits in practice:

- **Reproducibility** - staging and production come from the same code with different variables, so "it works in staging" means something.
- **Auditability** - every change is a commit with an author, a reason, and a reviewer.
- **Speed and scale** - a new environment or region is a parameter change, not a project.
- **Disaster recovery** - rebuild is `apply`, not archaeology.
- **Drift detection** - `plan` shows where reality diverged from intent.

**Declarative vs imperative:** declarative tools (Terraform, CloudFormation, Bicep, Pulumi) describe the desired end state and compute the diff; imperative scripts describe the steps. Declarative wins because it is idempotent - applying it twice changes nothing the second time.

**Immutable vs mutable:** the mature pattern is to replace rather than modify - build a new image or new resource and swap traffic, instead of patching in place. This eliminates configuration drift entirely.

## Example

```hcl
resource "aws_s3_bucket" "artifacts" {
  bucket = "${var.project}-artifacts-${var.environment}"
  tags   = local.common_tags
}

resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_public_access_block" "artifacts" {
  bucket                  = aws_s3_bucket.artifacts.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

## Interview tips

- Say "declarative and idempotent" early - it is the conceptual heart.
- The best answer includes testing IaC: `plan` review in pull requests, `tflint`/`checkov` policy scanning, and `terratest` for modules.
- Know how you would handle drift caused by an emergency manual change: import or re-apply, then fix the process.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you structure an Ansible role and share it through Galaxy?]] (`#468`): [How do you structure an Ansible role and share it through Galaxy?](../configuration-management/how-do-you-structure-an-ansible-role-and-share-it-through-galaxy.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[What is Configuration Management?]] (`#51`): [What is Configuration Management?](../configuration-management/what-is-configuration-management.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
