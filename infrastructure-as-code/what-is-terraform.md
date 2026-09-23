---
title: "What is Terraform?"
id: 27
category: "Infrastructure as Code"
difficulty: "Beginner"
tags:
  - devops
  - infrastructure-as-code
  - interview-questions
---

# What is Terraform?

**Short answer:** Terraform is HashiCorp's infrastructure-as-code tool that provisions resources across any provider with a declarative language (HCL), tracking what it manages in a state file and showing a reviewable plan before applying changes. Since August 2023 it is source-available under the Business Source Licence rather than open source (HashiCorp is now part of IBM); **OpenTofu**, the Linux Foundation fork of Terraform 1.5, is the MPL-licensed, largely drop-in alternative.

## Detail

**How it works.** You write `.tf` files; `terraform init` downloads providers; `terraform plan` compares desired configuration with state and real infrastructure and prints the diff; `terraform apply` executes it via provider APIs, in dependency order derived from a resource graph.

**State** is the crux. `terraform.tfstate` maps configuration to real resource IDs. In a team it must live in a remote backend (S3 with native lockfile locking, HCP Terraform, Azure Blob, GCS) so it is shared, locked during apply, and versioned. State contains sensitive values, so it must be encrypted and access-controlled.

**Modules** package reusable groups of resources with inputs and outputs - the unit of abstraction that keeps large estates manageable.

**Workspaces and directories** separate environments; most teams prefer separate state per environment with a shared module, rather than workspaces, for blast-radius reasons.

Key commands: `init`, `fmt`, `validate`, `plan`, `apply`, `destroy`, `test`, `state list/mv/rm`, `import` - plus the declarative `import`, `moved`, and `removed` blocks that have largely replaced ad-hoc state surgery.

**Trade-offs:** state is a sensitive single point of truth that must be protected; there is no rollback, so a failed apply is fixed forward; provider quality varies; and the licence change matters to vendors building competing products (not to most end users), which is why some organisations standardised on OpenTofu.

## Example

```hcl
terraform {
  required_version = "~> 1.9"
  required_providers { aws = { source = "hashicorp/aws", version = "~> 6.0" } }
  backend "s3" {
    bucket       = "acme-tfstate"
    key          = "prod/network/terraform.tfstate"
    region       = "eu-west-1"
    use_lockfile = true # S3-native locking prevents concurrent applies
    encrypt      = true
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "6.7.3"

  name            = "prod"
  cidr            = "10.0.0.0/16"
  azs             = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  enable_nat_gateway = true
}
```

## Interview tips

- State management is the single most-asked Terraform question: remote backend, locking, encryption, never committed to Git.
- Know `terraform import` and `state mv` for adopting existing infrastructure and refactoring modules.
- Pin provider and module versions; unpinned versions cause surprise diffs.
- Be accurate on licensing: Terraform is BSL-licensed since 1.6; OpenTofu is the open-source fork. Interviewers increasingly ask which one you would choose and why.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you structure an Ansible role and share it through Galaxy?]] (`#468`): [How do you structure an Ansible role and share it through Galaxy?](../configuration-management/how-do-you-structure-an-ansible-role-and-share-it-through-galaxy.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[What is Configuration Management?]] (`#51`): [What is Configuration Management?](../configuration-management/what-is-configuration-management.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
