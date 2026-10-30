---
title: "What is the difference between Terraform and OpenTofu?"
id: 758
category: "Infrastructure as Code"
difficulty: "Intermediate"
tags:
  - devops
  - infrastructure-as-code
  - interview-questions
  - terraform
  - opentofu
quiz:
  stem: "Why did the OpenTofu project fork Terraform in 2023?"
  options:
    - "Terraform stopped supporting the AWS provider"
    - "HashiCorp relicensed Terraform from the open-source MPL 2.0 to the source-available Business Source License (BSL) starting with 1.6"
    - "Terraform removed support for remote state backends"
    - "OpenTofu wanted to replace HCL with YAML"
  answer: 2
  explanation: "In August 2023 HashiCorp moved Terraform to the BSL 1.1. OpenTofu forked the last MPL-licensed code (Terraform 1.5.x) and is now maintained under the Linux Foundation and CNCF with an open governance model, staying largely compatible with Terraform configurations, providers, and state."
---

# What is the difference between Terraform and OpenTofu?

**Short answer:** OpenTofu is the open-source fork of Terraform, created after HashiCorp relicensed Terraform from MPL 2.0 to the source-available Business Source License (BSL) in August 2023. It forked from Terraform 1.5, is governed by the Linux Foundation and CNCF, and remains largely drop-in compatible: the same HCL, the same providers, the same state format, with `tofu` replacing `terraform` on the command line. The two have since diverged in features - OpenTofu shipped client-side state encryption and early variable evaluation first, Terraform has HCP Terraform integrations such as Stacks and `terraform query` - so "which one?" is now a decision about licensing, governance, and specific features rather than a rename.

## Detail

### What is the same

- **Language and workflow.** HCL, modules, `init`/`plan`/`apply`, `import`/`moved`/`removed` blocks, `for_each`, `terraform test` (`tofu test`) - an engineer moves between them without retraining.
- **Providers.** Both use the same provider plugin protocol. OpenTofu resolves providers through its own registry (`registry.opentofu.org`), which mirrors the public providers, so `hashicorp/aws` works unchanged.
- **State.** The state file format is shared, so OpenTofu can take over an existing Terraform state in S3, Azure Blob, GCS, and the other standard backends. Migration is usually `tofu init` in the existing working directory, a `tofu plan` that must show no changes, and a switch in CI. Two caveats: the official migration guides are per Terraform source version (state written by a much newer Terraform may need a version-matched path), and state held in HCP Terraform has to be moved to another backend first.

### Where they differ

| Area                 | Terraform                                                                   | OpenTofu                                                                                  |
| -------------------- | --------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Licence              | BSL 1.1 (source-available) since 1.6; HashiCorp is part of IBM              | MPL 2.0 (open source)                                                                     |
| Governance           | Single vendor                                                               | Linux Foundation / CNCF project, public RFC process                                       |
| State encryption     | Not in the CLI; rely on backend encryption (S3 SSE-KMS, HCP Terraform)      | Native client-side encryption of state and plan files (1.7+), with KMS or passphrase keys |
| Early evaluation     | Backend and module `source` blocks cannot use variables                     | Variables and locals usable in `backend`, module `source`/`version` (1.8+)                |
| Provider iteration   | `for_each` on modules and resources, not on provider blocks                 | `for_each` on provider configurations (1.9+) - one aliased provider per region from a map |
| Targeting            | `-target`                                                                   | `-target` plus `-exclude` (1.9+)                                                          |
| Secrets in state     | Ephemeral resources and write-only arguments (1.10/1.11)                    | Ephemeral resources and write-only attributes (1.11)                                      |
| Platform features    | HCP Terraform: Stacks, `terraform query` / list resources (1.14+), Sentinel | Uses third-party platforms (Spacelift, env0, Scalr, Harness) and OPA                      |
| Registry and modules | `registry.terraform.io`                                                     | `registry.opentofu.org`, plus OCI registries as provider/module sources (1.10+)           |

The practical consequence of divergence: a configuration that uses a feature exclusive to one tool stops being portable. OpenTofu also accepts `.tofu` files, which override a same-named `.tf` file, so a module can carry OpenTofu-only syntax without breaking Terraform users.

### How to choose

- **Licence exposure.** The BSL restricts offering Terraform as a competing hosted product; it does not stop an end user running Terraform for their own infrastructure. Most companies are not affected legally - but vendors, platform teams building an internal "Terraform as a service", and organisations with strict open-source policies often are, and choose OpenTofu.
- **Platform coupling.** If you rely on HCP Terraform (run tasks, Sentinel, Stacks, private registry), Terraform is the path of least resistance. If you use Spacelift, env0, Atlantis, or plain CI, either works.
- **Features you need.** State encryption without a SaaS backend and variables in backend configuration are concrete reasons to pick OpenTofu; Stacks and `terraform query` are concrete reasons to stay.
- **Ecosystem tools.** Terragrunt, tflint, Checkov, Trivy, and Infracost support both; check anything in-house that shells out to the `terraform` binary.

### Migration pitfalls

Pin one tool per state and enforce it in CI - mixing binaries against the same state is how you end up with state written by a newer version that the other tool refuses to read. Migrate from the newest version both tools support, read the OpenTofu migration guide for your source version, and treat it like any other upgrade: a no-change plan in each environment before the switch, and a rollback path (the previous state version in the versioned bucket).

## Example

```bash
# Migrate one working directory from Terraform to OpenTofu
terraform version                 # note the version; follow the matching migration guide
terraform plan -detailed-exitcode # 0 = clean starting point; never migrate with pending changes

tofu init                         # same backend block, providers fetched from registry.opentofu.org
tofu plan -detailed-exitcode      # must also be 0 - identical view of the world
# then switch CI to `tofu`, and keep the previous state version for rollback
```

```hcl
# OpenTofu-only: client-side state encryption with AWS KMS (1.7+)
terraform {
  encryption {
    key_provider "aws_kms" "main" {
      kms_key_id = "alias/tofu-state"
      region     = "eu-west-1"
      key_spec   = "AES_256"
    }
    method "aes_gcm" "main" {
      keys = key_provider.aws_kms.main
    }
    state {
      method = method.aes_gcm.main
    }
    plan {
      method = method.aes_gcm.main # saved plans contain secrets too
    }
  }
}
```

## Interview tips

- Start with the history in one sentence - BSL relicensing in August 2023, fork of 1.5, now under the Linux Foundation/CNCF - then say what is the same (HCL, providers, state) before what differs.
- Be accurate about the licence: the BSL limits competing commercial offerings, not ordinary internal use. Overstating it reads as tribal; understating it ignores real vendor and policy constraints.
- Name two concrete divergences each way: OpenTofu's state encryption and early variable evaluation; Terraform's HCP Stacks and `terraform query`.
- Give a migration plan with a verification step: no-change plan before and after, one tool pinned per state, rollback via the versioned state bucket.
- Likely follow-up: "would you migrate an existing estate?" - only with a reason (licence policy, a needed feature, platform choice); otherwise the migration is risk with no payoff. See [what is Terraform](./what-is-terraform.md) and [how Terraform state is protected](./how-does-terraform-state-management-work-and-how-do-you-protect-state-files-in-team-environments.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you structure an Ansible role and share it through Galaxy?]] (`#468`): [How do you structure an Ansible role and share it through Galaxy?](../configuration-management/how-do-you-structure-an-ansible-role-and-share-it-through-galaxy.md)
- [[What is the difference between mutable and immutable infrastructure in modern deployment patterns?]] (`#586`): [What is the difference between mutable and immutable infrastructure in modern deployment patterns?](../configuration-management/what-is-the-difference-between-mutable-and-immutable-infrastructure-in-modern-deployment-patterns.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
