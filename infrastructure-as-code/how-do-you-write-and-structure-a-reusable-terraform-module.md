---
title: "How do you write and structure a reusable Terraform module?"
id: 463
category: "Infrastructure as Code"
difficulty: "Intermediate"
tags:
  - devops
  - infrastructure-as-code
  - interview-questions
  - platform-engineering
---

# How do you write and structure a reusable Terraform module?

**Short answer:** A module is just a directory of `.tf` files with a deliberate interface: **`variables.tf`** (inputs, typed, described, validated, with defaults only where a default is genuinely safe), **`main.tf`** (the resources), **`outputs.tf`** (what consumers need - IDs, ARNs, endpoints), plus `versions.tf` for the `required_version` and `required_providers` constraints, a `README.md`, and `examples/`. Every Terraform configuration is already a module - the directory you run `terraform apply` in is the **root module** - and you call another one with a `module` block pointing at a `source` (local path, Git URL, or a registry) with a **version constraint** when the source supports it. The design rules that separate a reusable module from a copied folder: the module owns **one logical piece of infrastructure**, it does **not** declare providers or backends (the root does), it exposes intent rather than every attribute, and it is **versioned with semantic tags** so consumers upgrade deliberately.

## Detail

### Layout and the file conventions

```text
modules/vpc/
├── main.tf         # resources - the actual infrastructure
├── variables.tf    # inputs: type, description, default, validation
├── outputs.tf      # outputs: value, description, sensitive
├── versions.tf     # required_version + required_providers (constraints only)
├── locals.tf       # computed values, naming, tag merging
├── README.md       # generated with terraform-docs; the module's contract
└── examples/
    ├── minimal/    # smallest working invocation
    └── complete/   # every feature on - doubles as your test fixture
```

The file names are convention, not enforcement - Terraform concatenates every `.tf` in the directory - but the convention is what makes a stranger able to read your module. `terraform-docs` generates the inputs/outputs table into the README from the code, so the documentation cannot drift.

### The interface is the design

- **Type your variables** (`string`, `number`, `bool`, `list(string)`, `map(object({...}))`). An untyped variable is a bug waiting to happen, and typed object variables give consumers autocomplete and errors at plan time.
- **Always write `description`.** It ends up in the generated docs and in `terraform console`.
- **`validation` blocks** catch bad input before the provider does, with a message that says what to do: CIDR shape, allowed environment names, minimum sizes.
- **Defaults only where safe.** A default region or a default instance type is convenience; a default that silently creates a public resource is a security incident. Prefer no default and let the plan fail loudly.
- **`sensitive = true`** on secret inputs and outputs so they do not appear in plan output (state still stores them in the clear - say that if asked).
- **Outputs are the contract.** Export IDs, ARNs, names, and endpoints the caller will need; do not export the whole resource object, because that couples consumers to your internals.
- **`nullable = false`** where an explicit null makes no sense, and `optional()` attributes inside object types (with defaults) for backwards-compatible growth.

### Calling and versioning

```hcl
module "vpc" {
  source  = "git::https://github.com/acme/tf-modules.git//modules/vpc?ref=v3.2.0"
  # or:   source = "app.terraform.io/acme/vpc/aws"   with   version = "~> 3.2"
  name    = "prod"
  cidr    = "10.20.0.0/16"
  azs     = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
}
```

**Pin the version.** A Git `ref` tag or a registry `version` constraint means a module change does not silently alter every environment on the next `init`. Upgrading a module version is then a reviewable pull request: bump the constraint, run `terraform init -upgrade`, read the plan, and look for `-/+` replacements before merging. Do that in dev first, then staging, then production - a module upgrade is a change like any other.

Registry-sourced modules support `version`; raw Git sources do not, which is why you pin with `?ref=` there. Local paths (`./modules/vpc`) are unversioned by nature - fine inside one repository, wrong for sharing across teams.

### Provider configuration belongs to the root

A module should declare which providers it **needs** (`required_providers` with version constraints) but not **configure** them. The root module configures providers and passes aliased ones explicitly:

```hcl
provider "aws" { region = "eu-west-1" }
provider "aws" { alias = "us", region = "us-east-1" }

module "cdn" {
  source    = "./modules/cdn"
  providers = { aws = aws.us }     # explicit: CloudFront certs must live in us-east-1
}
```

This is also the answer to the classic multi-region trap: a resource with no explicit provider uses the **default** provider configuration, regardless of how many aliases exist. If you declare three regions and create one instance without `provider = aws.<alias>`, it lands in the default region.

Modules must not declare a `backend` either - state configuration is a root-module concern, one per state.

### Composition, not inheritance

Good module design is layered:

- **Resource modules** - a thin, opinionated wrapper over one thing (a VPC, an RDS instance, an EKS node group). Reusable everywhere.
- **Service or "infrastructure" modules** - compose resource modules into a deployable unit (`payments-service` = ECS service + ALB target group + RDS + secrets + alarms). This is where your organisation's opinions live.
- **Root modules** - one per environment per state, thin: provider config, backend, a few module calls, and environment values.

Avoid the two common failure modes: a **mega-module** with 60 inputs that tries to configure everything (nobody can read the plan, and every change risks everything), and **deep nesting** three or four levels down (debugging becomes archaeology and a small change fans out unpredictably). Two levels of nesting is a healthy ceiling.

Also resist wrapping a resource that has no added value - a module that just passes eight variables to one `aws_s3_bucket` adds indirection and no benefit. Wrap when you are encoding a decision (naming, tagging, encryption on by default, logging wired up), not to avoid typing.

### Iteration, DRY, and the "hundred lines" question

The frequently-asked version is _"you are writing a hundred lines of repetitive Terraform - how do you avoid it?"_ Answer in three layers: **`for_each`/`count`** for repeated resources, **modules** for repeated groups of resources, and **`dynamic` blocks** for repeated nested blocks inside a single resource (security group rules, tags on a launch template). Then add the honest caveat - DRY has a cost, and `dynamic` blocks in particular make plans much harder to read, so use them where the nested block genuinely varies in count, not to save three lines.

### Testing and quality gates

- **`terraform validate` + `fmt -check`** on every module, in CI.
- **`tflint`** with the provider ruleset for provider-specific mistakes; **`checkov`/`tfsec`** for security defaults inside the module (so consumers inherit a safe baseline).
- **`terraform test`** (native, `.tftest.hcl`) or **Terratest** for real apply-and-assert-then-destroy tests against the `examples/` directories. Testing the examples means your documented usage is the thing under test.
- **`terraform-docs` in a pre-commit hook** so the README table matches the variables.
- Publish to a private registry or a tagged Git repository, with a CHANGELOG and semver: patch for fixes, minor for new optional inputs, **major for anything that forces resource replacement or removes an input**.

## Example

```hcl
# modules/vpc/variables.tf - typed, described, validated, safe defaults only
variable "name" {
  type        = string
  description = "Name prefix for all resources; also used in the Name tag."
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,30}$", var.name))
    error_message = "name must be lowercase alphanumeric with hyphens, 2-31 chars."
  }
}

variable "cidr" {
  type        = string
  description = "IPv4 CIDR block for the VPC, /16 to /20."
  validation {
    condition     = can(cidrhost(var.cidr, 0)) && tonumber(split("/", var.cidr)[1]) <= 20
    error_message = "cidr must be a valid IPv4 CIDR of /20 or larger."
  }
}

variable "subnets" {
  description = "Subnet tiers to create per availability zone."
  type = map(object({
    newbits = number
    public  = optional(bool, false) # optional with a default: safe to add later
  }))
  default = {
    public  = { newbits = 4, public = true }
    private = { newbits = 4 }
    data    = { newbits = 6 }
  }
}

variable "tags" {
  type        = map(string)
  description = "Tags merged onto every resource."
  default     = {}
  nullable    = false
}
```

```hcl
# modules/vpc/main.tf - for_each over the interface, consistent naming and tags
locals {
  tags = merge(var.tags, { Module = "vpc", ManagedBy = "terraform" })

  # one subnet per tier per AZ, deterministically addressed
  subnets = {
    for pair in setproduct(keys(var.subnets), range(length(var.azs))) :
    "${pair[0]}-${var.azs[pair[1]]}" => {
      tier   = pair[0]
      az     = var.azs[pair[1]]
      cidr   = cidrsubnet(var.cidr, var.subnets[pair[0]].newbits, pair[1] + index(keys(var.subnets), pair[0]) * length(var.azs))
      public = var.subnets[pair[0]].public
    }
  }
}

resource "aws_vpc" "this" {
  cidr_block           = var.cidr
  enable_dns_hostnames = true
  tags                 = merge(local.tags, { Name = var.name })
}

resource "aws_subnet" "this" {
  for_each                = local.subnets # stable keys, not list indexes
  vpc_id                  = aws_vpc.this.id
  cidr_block              = each.value.cidr
  availability_zone       = each.value.az
  map_public_ip_on_launch = each.value.public
  tags                    = merge(local.tags, { Name = "${var.name}-${each.key}", Tier = each.value.tier })
}
```

```hcl
# modules/vpc/outputs.tf + versions.tf - the contract, and the constraints
output "vpc_id" {
  value       = aws_vpc.this.id
  description = "ID of the created VPC."
}
output "subnet_ids_by_tier" {
  value       = { for tier in keys(var.subnets) : tier => [for k, s in aws_subnet.this : s.id if local.subnets[k].tier == tier] }
  description = "Subnet IDs grouped by tier, for consumers to place resources."
}

terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 5.0, < 6.0" } # constraint, not config
  }
}
```

```bash
# Quality gates for the module itself
terraform fmt -check -recursive && terraform validate
tflint --recursive && checkov -d . --framework terraform
terraform-docs markdown table . > README.md          # docs generated from code
terraform test                                        # runs examples/*.tftest.hcl

# Consuming and upgrading deliberately
terraform init -upgrade && terraform plan   # read the plan for -/+ replacements
```

## Interview tips

- Answer the file question directly and then explain the _why_: `main.tf` for resources, `variables.tf` for the input contract, `outputs.tf` for what consumers need, `versions.tf` for constraints, plus a README and examples. Add that the file split is convention - Terraform reads every `.tf` - which shows you know the difference between a rule and a habit.
- Say "every configuration is a module; the directory you apply in is the root module." It reframes the question and is technically the right starting point.
- Emphasise **version pinning** on module sources (`?ref=v3.2.0` for Git, `version = "~> 3.2"` for a registry) and describe upgrading as a reviewable PR where you read the plan for replacements. That is the answer to "how do you upgrade a module version?"
- Be firm that modules declare `required_providers` but never configure providers or backends, and give the aliased-provider example. It leads straight into the multi-region trap - a resource without an explicit `provider` uses the default configuration.
- Describe the composition layers (resource modules → service modules → thin root modules) and name the two failure modes: the 60-input mega-module and four-deep nesting.
- For "how do you avoid a hundred repetitive lines?", give the three-layer answer - `for_each`, modules, `dynamic` blocks - and caveat that `dynamic` hurts plan readability.
- Prefer `for_each` over `count` in module examples and be ready to say why (stable keys versus index shifting).
- Mention testing and docs generation - `terraform test`/Terratest against `examples/`, `tflint`, `checkov`, `terraform-docs` in a pre-commit hook - and semver where a major version means "this may replace resources". See [structuring Terraform code for multiple environments and providers](./how-do-you-structure-terraform-code-for-multiple-environments-and-providers.md), [count versus for_each](./what-is-the-difference-between-count-and-for-each-in-terraform.md), [what are Terraform providers](./what-are-terraform-providers.md), and [scanning IaC before it is applied](../devsecops/how-do-you-scan-infrastructure-as-code-before-it-is-applied.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you structure an Ansible role and share it through Galaxy?]] (`#468`): [How do you structure an Ansible role and share it through Galaxy?](../configuration-management/how-do-you-structure-an-ansible-role-and-share-it-through-galaxy.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you scale CI/CD across many services and teams?]] (`#459`): [How do you scale CI/CD across many services and teams?](../cicd/how-do-you-scale-ci-cd-across-many-services-and-teams.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
