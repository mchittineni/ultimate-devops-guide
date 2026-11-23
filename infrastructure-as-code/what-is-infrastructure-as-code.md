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

**Declarative vs imperative:** declarative tools (Terraform/OpenTofu, CloudFormation, Bicep) describe the desired end state and compute the diff; imperative scripts describe the steps. Pulumi and the AWS CDK sit in between - you write a general-purpose language, but it produces a declarative desired-state model that an engine diffs. Declarative wins for provisioning because it is idempotent - applying it twice changes nothing the second time.

**The costs:** IaC is only authoritative if nobody changes things by hand, so it needs access controls and drift detection; state (for tools that keep it) becomes a sensitive, critical asset; and a bad change now applies everywhere at machine speed, which is why plan review, policy checks, and small blast-radius state splits matter.

**"It is one-off and will not change for five years - why codify it?"** This objection comes up often, and the default answer is still to codify it, because the value of IaC is not only in frequent changes. Infrastructure that rarely changes is exactly what gets forgotten: in five years nobody remembers why a VPN endpoint or a set of IAM roles exists, who owns it, or whether it can be removed, and the people who knew the console clicks have moved on. Code in Git gives you documentation of what exists and why, review and audit, an exact rebuild for disaster recovery or a second region, drift detection with `terraform plan -refresh-only`, and a clean decommission (`destroy`) at the end. It is still a cost/benefit call, not dogma: a truly throwaway resource with tags and a ticket can be acceptable. And if something was built by hand, it can be adopted later with an `import` block (Terraform 1.5+), using `terraform plan -generate-config-out=generated.tf` to draft the configuration.

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

```hcl
# Adopting a customer gateway someone created in the console (Terraform 1.5+)
import {
  to = aws_customer_gateway.partner
  id = "cgw-0abc1234def567890"
}
```

```bash
terraform plan -generate-config-out=generated.tf   # drafts the resource block to review and tidy
terraform plan -refresh-only                       # later: has anyone changed it by hand?
```

## Interview tips

- Say "declarative and idempotent" early - it is the conceptual heart.
- The best answer includes testing IaC: `plan` review in pull requests, `tflint`/`checkov` policy scanning, and `terratest` for modules.
- Know how you would handle drift caused by an emergency manual change: import or re-apply, then fix the process.
- If asked whether long-lived, rarely changed infrastructure is worth codifying, avoid both extremes. Do not dismiss it as "just click it", and do not answer with dogma. Give the reasons (documentation, DR rebuild, audit, drift detection, clean removal) and mention adopting hand-built resources with `import` blocks.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you structure an Ansible role and share it through Galaxy?]] (`#468`): [How do you structure an Ansible role and share it through Galaxy?](../configuration-management/how-do-you-structure-an-ansible-role-and-share-it-through-galaxy.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[What is Configuration Management?]] (`#51`): [What is Configuration Management?](../configuration-management/what-is-configuration-management.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
