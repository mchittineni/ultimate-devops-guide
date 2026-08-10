---
title: "How do you structure Terraform code for multiple environments and providers?"
id: 422
category: "Infrastructure as Code"
difficulty: "Advanced"
tags:
  - devops
  - infrastructure-as-code
  - interview-questions
  - cloud-engineering
  - platform-engineering
  - version-control
---

# How do you structure Terraform code for multiple environments and providers?

**Short answer:** Use **one directory (and one state file) per environment**, each composing versioned **modules**, with variables supplying the differences. Prefer that over workspaces for environments: a directory per environment gives you separate state, separate backends, separate credentials, and a readable diff between staging and production - workspaces share one configuration and one backend, which makes blast radius and per-environment drift harder to control. Split state by **blast radius and change frequency** (network, data, platform, applications) and wire them together with remote-state data sources or explicitly published outputs. For multiple providers, use **aliased provider blocks** passed explicitly into modules, and keep cloud-specific logic inside per-cloud modules behind a common interface rather than one module with `if aws / if azure` branching.

## Detail

### Layout: directory per environment, composing modules

```text
infra/
  modules/                     # reusable, versioned, no provider/backend blocks
    network/  eks/  rds/  app-service/
  live/
    prod/
      network/    { main.tf backend.tf terraform.tfvars }   # one state each
      platform/
      apps/
    staging/  { ...same shape, smaller numbers }
    dev/
```

Why this beats a single root with workspaces:

- **State isolation.** A mistake in dev cannot corrupt production state, and `terraform apply` in one environment physically cannot touch another.
- **Different credentials and backends** per environment, which is what least privilege requires.
- **A readable diff.** `diff -r live/staging live/prod` shows exactly how production differs - the most useful review artefact you can have.
- **Independent versions.** Staging can adopt module v2.1 while production stays on v2.0. Workspaces force one configuration for all.

Use **workspaces** where they fit well: many near-identical, short-lived instances of the same thing - ephemeral pull-request environments, per-tenant stacks, per-region replicas of one identical stack.

### Module design

- **Modules take variables and return outputs; they do not declare `provider` or `backend` blocks.** A module with its own provider configuration cannot be reused with a different account or region.
- **Version them.** Reference by Git tag or registry version (`source = "git::...?ref=v2.1.0"`), so an upgrade is a deliberate, reviewable change rather than "whatever `main` says today". Pin the Terraform and provider versions too, and commit the `.terraform.lock.hcl`.
- **Keep them shallow.** Two levels of nesting is usually the practical limit before debugging becomes archaeology. Prefer composition in the environment root over deep module trees.
- **Right-size the interface.** A module with 60 variables is a leaky abstraction; a module with 3 is inflexible. Expose what genuinely varies and hard-code your organisation's opinions - that opinionation is the point of an internal module.

### Splitting state

Split by blast radius and change cadence:

| Layer          | Contents                                 | Changes   | Why separate                                          |
| -------------- | ---------------------------------------- | --------- | ----------------------------------------------------- |
| **foundation** | accounts, IAM baseline, DNS zones        | rarely    | Catastrophic if damaged; different approvers          |
| **network**    | VPC, subnets, peering, transit           | rarely    | Long-lived, referenced by everything                  |
| **data**       | RDS, caches, buckets                     | sometimes | Stateful; a mistake here loses data, not just uptime  |
| **platform**   | Kubernetes cluster, node groups, add-ons | weekly    | Frequent, and should not require touching the network |
| **apps**       | app-specific resources                   | daily     | Fast, low-risk changes with a small plan              |

Smaller states mean faster plans, smaller blast radius, and fewer lock conflicts. The cost is wiring: use `terraform_remote_state` data sources, or - better for decoupling - publish stable identifiers to SSM Parameter Store / Azure App Configuration and read those, so consumers do not need read access to another layer's whole state. See [how do you manage Terraform state safely in a team](./how-do-you-manage-terraform-state-safely-in-a-team.md).

### Multiple providers and multiple clouds

- **Aliases for multiple instances of one provider** - regions, accounts, or a second subscription:

  ```hcl
  provider "aws" { alias = "eu", region = "eu-west-1" }
  provider "aws" { alias = "us", region = "us-east-1" }
  module "edge" { source = "./modules/cdn", providers = { aws = aws.us } }
  ```

  Pass providers into modules explicitly with the `providers` argument. Cross-account work uses `assume_role` per provider block rather than long-lived keys.

- **Genuinely multi-cloud**: do not write one module that branches on cloud. Write `modules/aws/kubernetes` and `modules/azure/kubernetes` with a deliberately similar variable interface, and compose them in the environment root. The abstraction that survives is at the _interface_ level, not inside the resources - because the resources have no common shape. Keep provider credentials out of the code (environment variables, OIDC federation from CI, or a workload identity), and be honest that a single state containing two clouds means one provider outage blocks changes to both. See [what are the real trade-offs of multi-cloud](../cloud-engineering/what-are-the-real-trade-offs-of-multi-cloud.md).

### Variables, secrets, and the pipeline

Per-environment `terraform.tfvars` committed to Git for non-secret values; secrets from a secret manager or CI-injected environment variables, never in `.tfvars` and never in state you have not encrypted. In CI: `fmt -check`, `validate`, `tflint`, a security scan (`tfsec`/Checkov), then `plan -out=tfplan` on the pull request with the plan posted as a comment, and `apply tfplan` after approval so what is applied is provably what was reviewed. Protect production with a separate approval and separate credentials. See [how do you scan Infrastructure as Code before it is applied](../devsecops/how-do-you-scan-infrastructure-as-code-before-it-is-applied.md).

## Example

```hcl
# live/prod/platform/main.tf - a thin composition root: modules + variables, nothing clever
terraform {
  required_version = "~> 1.9"
  required_providers { aws = { source = "hashicorp/aws", version = "~> 5.60" } }

  backend "s3" {                                   # one state per environment per layer
    bucket       = "acme-tfstate-prod"
    key          = "prod/platform/terraform.tfstate"
    region       = "eu-west-1"
    use_lockfile = true                            # S3-native locking
    encrypt      = true
  }
}

provider "aws" {
  region = var.region
  assume_role { role_arn = var.deploy_role_arn }   # no static credentials
  default_tags { tags = { env = var.environment, owner = var.owner, managed_by = "terraform" } }
}

provider "aws" {                                   # aliased: a second region for DR
  alias  = "dr"
  region = var.dr_region
  assume_role { role_arn = var.deploy_role_arn }
}

# Read the network layer's outputs instead of duplicating them
data "terraform_remote_state" "network" {
  backend = "s3"
  config  = { bucket = "acme-tfstate-prod", key = "prod/network/terraform.tfstate", region = "eu-west-1" }
}

module "eks" {
  source  = "git::https://github.com/acme/tf-modules.git//eks?ref=v2.1.0"  # pinned
  cluster_name = "prod"
  vpc_id       = data.terraform_remote_state.network.outputs.vpc_id
  subnet_ids   = data.terraform_remote_state.network.outputs.private_subnet_ids
  node_groups  = var.node_groups                   # the per-environment difference
}

module "eks_dr" {
  source    = "git::https://github.com/acme/tf-modules.git//eks?ref=v2.1.0"
  providers = { aws = aws.dr }                     # same module, other region
  cluster_name = "prod-dr"
  vpc_id       = data.terraform_remote_state.network.outputs.dr_vpc_id
  subnet_ids   = data.terraform_remote_state.network.outputs.dr_private_subnet_ids
  node_groups  = var.dr_node_groups
}
```

```text
# live/prod/platform/terraform.tfvars vs staging - the diff IS the documentation
  prod                                   staging
  region        = "eu-west-1"            region        = "eu-west-1"
  node_groups   = { general = {          node_groups   = { general = {
      min = 6, max = 60,                     min = 1, max = 6,
      instance_types = ["m6i.xlarge"] } }    instance_types = ["t3.large"] } }
  deploy_role_arn = ".../tf-prod"        deploy_role_arn = ".../tf-staging"
```

## Interview tips

- Answer with a concrete layout and then justify it. "Directory per environment composing versioned modules" plus the four reasons (state isolation, credentials, readable diff, independent versions) is a complete answer.
- Have a firm, reasoned position on workspaces: not for environments, good for many identical short-lived stacks. Interviewers ask this specifically because the HashiCorp tutorial suggests workspaces and production practice has moved on.
- Say that modules must not contain `provider` or `backend` blocks, and explain why - it is the constraint that makes reuse possible.
- Splitting state by blast radius and change frequency is the senior answer; name the layers and the trade-off (faster plans and smaller blast radius, at the cost of wiring between them).
- For cross-state wiring, mention both `terraform_remote_state` and publishing to a parameter store, and prefer the latter for decoupling and least privilege.
- For multi-provider, show aliased providers passed with the `providers` argument, and reject one module branching on cloud - per-cloud modules with a similar interface is the pattern that survives.
- Mention pinning: Terraform version, provider versions, module tags, and a committed lock file. Then `plan -out` reviewed and `apply` of that exact plan.
- Close on the diff between environment variable files being your best drift documentation - it is a practical detail that shows you have operated this, not just designed it.

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
