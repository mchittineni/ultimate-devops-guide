---
title: "How do you manage Terraform state safely in a team?"
id: 261
category: "Infrastructure as Code"
difficulty: "Intermediate"
tags:
  - devops
  - infrastructure-as-code
  - interview-questions
---

# How do you manage Terraform state safely in a team?

**Short answer:** Put state in a remote backend with versioning and encryption, enable state locking so two engineers cannot apply at once, split state by environment and blast radius rather than keeping one giant file, and treat the state file as a secret - it stores resource attributes in plaintext, including some passwords.

## Detail

**What state is for.** Terraform's state file maps the resources in your configuration to the real objects in the provider, and caches their attributes. Without it, Terraform cannot tell "create a new instance" from "this instance already exists" - names alone are not identity, since most cloud resources have provider-generated IDs. State is also what makes `plan` fast: it diffs against the cached attributes rather than reading every resource.

**Local state is single-player.** It lives in `terraform.tfstate` next to your code, is not shared, is not locked, and is trivially lost with the laptop. The first thing any team does is move it.

**Remote backends and locking:**

| Backend             | Locking mechanism                                                              |
| ------------------- | ------------------------------------------------------------------------------ |
| S3                  | Native S3 lockfile (`use_lockfile = true`); older setups used a DynamoDB table |
| Azure Blob          | Native blob leases                                                             |
| GCS                 | Native object locking                                                          |
| Terraform/HCP Cloud | Managed, with run queueing and audit history                                   |

Locking is what prevents the classic corruption case: two engineers run `apply` simultaneously, both read the same state, both write, and the second write silently discards the first one's resources. With a lock the second run blocks and prints who holds it.

> On AWS, S3 now supports native state locking via `use_lockfile = true`, so a separate DynamoDB table is no longer required for new configurations. Plenty of existing code still uses DynamoDB - know both, and be ready to say the separate table is legacy.

**Enable versioning on the bucket.** This is the cheapest insurance in all of Terraform: a corrupted or truncated state is a matter of restoring the previous object version. Turn on server-side encryption too, and block public access.

**State contains secrets.** RDS passwords, generated keys, and any sensitive variable that ends up as a resource attribute are stored in plaintext in the state, whatever `sensitive = true` does to console output. That means encryption at rest, tight IAM on the bucket, and never committing state to Git.

**Split state deliberately.** One state file for the whole estate means every `plan` is slow, every apply risks unrelated resources, and one lock blocks the whole company. Split by environment (dev/stage/prod - always separate) and by rate of change and blast radius: networking and IAM in one state, the Kubernetes platform in another, applications in a third. Consume outputs across states with `terraform_remote_state` or, better, by looking resources up with data sources so the coupling stays loose.

**Workspaces are not environments.** `terraform workspace` gives multiple state files against one backend and one configuration. That is fine for short-lived, identical copies (per-PR preview stacks), but a poor fit for dev/stage/prod, which drift apart in size and configuration and should not share a backend or credentials. Use separate directories or a tool like Terragrunt with per-environment `.tfvars`.

**Drift.** State records what Terraform last saw; someone clicking in the console changes reality without changing state. `terraform plan` detects the difference because it refreshes against the provider before diffing. The durable fixes are: run `plan` on a schedule and alert on non-empty output, remove human write access to production, and adopt changes made by hand with `terraform import` rather than reverting them blindly.

**`terraform state` is a real toolkit,** not just a file. `list`, `show`, `mv` (rename a resource without destroying it), `rm` (forget a resource without deleting it), and `pull`/`push` for surgery. `terraform state mv` is the answer to "how do you refactor modules without downtime" - though `moved` blocks in configuration are the safer, reviewable, version-controlled way to do the same thing.

## Example

```hcl
# backend.tf - remote state with native S3 locking and versioning
terraform {
  required_version = "~> 1.9"

  backend "s3" {
    bucket       = "acme-tfstate-prod"
    key          = "platform/network/terraform.tfstate" # one key per state split
    region       = "eu-west-1"
    encrypt      = true
    use_lockfile = true  # native S3 locking; replaces the old DynamoDB table
    kms_key_id   = "arn:aws:kms:eu-west-1:123456789012:key/abc-123"
  }
}
```

```hcl
# Refactoring without destroying: declare the move, review it in the PR.
moved {
  from = aws_instance.web
  to   = module.web.aws_instance.this
}
```

```bash
# Inspect
terraform state list
terraform state show aws_db_instance.main

# Rename in place - no destroy/create
terraform state mv aws_instance.web module.web.aws_instance.this

# Stop managing a resource without deleting it in the cloud
terraform state rm aws_s3_bucket.legacy

# Adopt something created by hand
terraform import aws_s3_bucket.legacy acme-legacy-assets

# Detect drift in CI, fail the job if anything changed outside Terraform
terraform plan -detailed-exitcode   # exit 0 = no changes, 2 = drift, 1 = error
```

## Interview tips

- Define what state is _for_ before describing where to put it - identity mapping and attribute caching. Candidates who only say "it tracks resources" get probed further.
- Remote backend + locking + versioning + encryption is the four-part answer. Say all four.
- "Two engineers apply at the same time - what happens?" With locking, the second blocks. Without it, the state is corrupted and resources are orphaned.
- Be current on locking: native S3 lockfiles have replaced the DynamoDB table for new configurations, but plenty of production code still uses DynamoDB.
- Flag that state holds secrets in plaintext. It is a compliance point interviewers use to separate readers from operators.
- On workspaces, do not say you use them for dev/stage/prod. Say why: separate directories and backends give real credential and blast-radius isolation.
- `terraform plan -detailed-exitcode` in a scheduled job is a concrete, quotable drift-detection answer.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you structure an Ansible role and share it through Galaxy?]] (`#468`): [How do you structure an Ansible role and share it through Galaxy?](../configuration-management/how-do-you-structure-an-ansible-role-and-share-it-through-galaxy.md)
- [[What is Configuration Management?]] (`#51`): [What is Configuration Management?](../configuration-management/what-is-configuration-management.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
