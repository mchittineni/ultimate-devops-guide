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

**Short answer:** Terraform is HashiCorp's open-source infrastructure-as-code tool that provisions resources across any provider with a declarative language (HCL), tracking what it manages in a state file and showing a reviewable plan before applying changes.

## Detail

**How it works.** You write `.tf` files; `terraform init` downloads providers; `terraform plan` compares desired configuration with state and real infrastructure and prints the diff; `terraform apply` executes it via provider APIs, in dependency order derived from a resource graph.

**State** is the crux. `terraform.tfstate` maps configuration to real resource IDs. In a team it must live in a remote backend (S3 with DynamoDB locking, Terraform Cloud, GCS) so it is shared, locked during apply, and versioned. State contains sensitive values, so it must be encrypted and access-controlled.

**Modules** package reusable groups of resources with inputs and outputs - the unit of abstraction that keeps large estates manageable.

**Workspaces and directories** separate environments; most teams prefer separate state per environment with a shared module, rather than workspaces, for blast-radius reasons.

Key commands: `init`, `fmt`, `validate`, `plan`, `apply`, `destroy`, `state list/mv/rm`, `import`.

## Example

```hcl
terraform {
  required_version = "~> 1.9"
  required_providers { aws = { source = "hashicorp/aws", version = "~> 5.60" } }
  backend "s3" {
    bucket         = "acme-tfstate"
    key            = "prod/network/terraform.tfstate"
    region         = "eu-west-1"
    dynamodb_table = "tf-locks"       # prevents concurrent applies
    encrypt        = true
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.13.0"

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

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
