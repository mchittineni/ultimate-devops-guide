---
title: "How do you recover a lost or corrupted Terraform state file?"
id: 262
category: "Infrastructure as Code"
difficulty: "Advanced"
tags:
  - devops
  - infrastructure-as-code
  - interview-questions
---

# How do you recover a lost or corrupted Terraform state file?

**Short answer:** Stop before you run anything. In order of preference: restore the previous object version from the versioned backend bucket, restore from the `.terraform.tfstate.backup` file Terraform writes on every apply, or - if no copy exists anywhere - rebuild the state by importing every real resource back into a fresh state file. Never run `terraform apply` against empty state, because Terraform will interpret existing infrastructure as absent and try to create duplicates.

## Detail

**Why this question gets asked so often:** it separates people who have used Terraform from people who have operated it. The interviewer is testing whether you understand that state is a _record_, not the infrastructure - losing it destroys nothing, but it does make Terraform blind.

**What actually happens with no state.** `terraform plan` shows every resource as "to be created". Applying that either creates a parallel copy of your entire estate, or fails partway on name conflicts (S3 bucket names, IAM role names, RDS identifiers) leaving a half-built mess. This is the single most expensive Terraform mistake, and the reason the first move is always to stop.

**Recovery ladder, in order:**

1. **Backend object versioning.** If the bucket has versioning enabled - which is why it is non-negotiable - list previous versions and restore the last good one. This is a two-minute fix and covers deletion, truncation, and corruption alike.
2. **`terraform.tfstate.backup`.** Terraform writes the previous state next to the current one on every write, including when using some remote backends locally. If someone deleted the state on a workstation, the backup is often still there.
3. **Terraform/HCP Cloud state history.** Managed backends keep every state version with the run that produced it, and let you roll back through the UI or API.
4. **A colleague's or CI runner's cached copy.** `.terraform/` directories on a build agent may still hold a recent pull.
5. **Rebuild by import.** The last resort, described below.

**Rebuilding by import.** With the configuration still in Git, you re-associate each real resource with its address:

- **`import` blocks (Terraform 1.5+) are the modern way.** They are declarative, reviewable in a pull request, and `terraform plan` shows exactly what will be adopted before you commit to it - unlike the old `terraform import` CLI command, which mutated state immediately with no dry run.
- Generate scaffolding with `terraform plan -generate-config-out=`, which writes HCL for imported resources you do not have configuration for.
- Work outward from the dependency graph: networking and IAM first, then data stores, then compute.
- After each batch, run `plan` and expect it to be **empty**. A non-empty plan means the imported attributes do not match the configuration - fix the config to match reality, do not apply.

This is slow and manual for a large estate, which is the point: it is the argument for versioned buckets that you make to the interviewer.

**Corruption rather than deletion.** Symptoms are a JSON parse error, a resource present twice, or a state whose `serial` went backwards after a concurrent write. Restore from a version first. If you must repair by hand: `terraform state pull > repair.json`, edit, then `terraform state push repair.json`. Never hand-edit the remote object in place, and never lower the `serial` - Terraform uses it to detect stale writes.

**Stuck locks are a different failure** that people confuse with corruption. If a run is killed mid-apply, the lock persists and every subsequent run blocks. `terraform force-unlock <LOCK_ID>` clears it - but only after you have confirmed no apply is genuinely still running, because force-unlocking a live apply is how you get the concurrent-write corruption you were trying to avoid.

**Partial apply.** A crash halfway through an apply leaves some resources created and recorded, others created and _not_ recorded. Terraform usually writes state before exiting; if it did not, the unrecorded resources are orphans - find them by tag and either import or delete them.

## Example

```bash
# 1. FIRST: stop anyone else from applying. Then diagnose - never apply blind.
terraform state list   # errors or empty output confirms the problem

# 2. Restore a previous version from S3 (versioning enabled)
aws s3api list-object-versions \
  --bucket acme-tfstate-prod \
  --prefix platform/network/terraform.tfstate \
  --query 'Versions[?IsLatest==`false`].[VersionId,LastModified]' --output table

aws s3api get-object \
  --bucket acme-tfstate-prod \
  --key platform/network/terraform.tfstate \
  --version-id 3HL4kqtJlcpXroDTDmJ+rmSpXd3dIbrHY+MTRCxf3vjVBH40Nr8X8gdRQBpUMLUo \
  restored.tfstate

terraform state push restored.tfstate
terraform plan   # MUST be empty before you trust it
```

```hcl
# 3. No backup anywhere: rebuild declaratively with import blocks.
import {
  to = aws_s3_bucket.assets
  id = "acme-prod-assets"
}

import {
  to = aws_instance.web
  id = "i-0abc123def4567890"
}
```

```bash
# Dry-run the adoption, then apply. Plan shows imports, not creates.
terraform plan
terraform apply

# Generate HCL for resources you have no configuration for
terraform plan -generate-config-out=generated.tf

# Stuck lock after a killed run - confirm nothing is applying first
terraform force-unlock 1a2b3c4d-5e6f-7890-abcd-ef1234567890
```

## Interview tips

- The first sentence should be "stop - do not run `apply`." Interviewers are checking for the reflex, and everything else follows from it.
- Explain the consequence precisely: empty state makes Terraform plan a full recreate, and unique-name collisions turn that into a half-applied mess.
- Give the ladder in order - bucket versioning, `.tfstate.backup`, managed state history, then import - rather than jumping straight to import.
- Prefer `import` blocks over the `terraform import` command and say why: reviewable in a PR, and `plan` dry-runs the adoption.
- "Plan must be empty afterwards" is the verification step most candidates omit.
- Close by turning it into prevention: versioned encrypted bucket, locking, split state, and no local state in production. That reframes a recovery question as a design answer.
- Do not confuse a stuck lock with corruption. Knowing `force-unlock` - and that using it on a live apply causes the corruption - is a good senior signal.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you structure an Ansible role and share it through Galaxy?]] (`#468`): [How do you structure an Ansible role and share it through Galaxy?](../configuration-management/how-do-you-structure-an-ansible-role-and-share-it-through-galaxy.md)
- [[What is Configuration Management?]] (`#51`): [What is Configuration Management?](../configuration-management/what-is-configuration-management.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
