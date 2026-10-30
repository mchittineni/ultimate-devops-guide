---
title: "How do you import existing cloud infrastructure into Terraform?"
id: 235
category: "Infrastructure as Code"
difficulty: "Intermediate"
tags:
  - devops
  - infrastructure-as-code
  - interview-questions
---

# How do you import existing cloud infrastructure into Terraform?

**Short answer:** Import existing cloud resources into Terraform state using `terraform import <address> <id>` or declarative `import {}` blocks in Terraform 1.5+, writing matching resource configuration blocks, and running `terraform plan` to ensure zero drift.

## Detail

In production environments, resources are often created manually via the AWS Console or Cloud Portal before being brought under Terraform management. Bringing pre-existing resources into IaC requires binding the cloud resource ID to a Terraform state address.

### Modern Declarative Import (`import {}` blocks - Terraform 1.5+)

Terraform 1.5 introduced top-level `import` blocks, making imports version-controlled, plan-driven, and reproducible.

1. **Define the import block:** Specify the target resource `to` address and the existing cloud `id`.
2. **Generate configuration:** Use `terraform plan -generate-config-out=generated.tf` to auto-generate HCL code for the imported resources.
3. **Refine and apply:** Review `generated.tf`, clean up auto-generated attributes, run `terraform plan` to verify zero changes required, and execute `terraform apply`. The import happens in the apply, so it goes through the same review and locking as any other change.
4. **Scale it:** since Terraform 1.7 (and OpenTofu), `import` blocks accept `for_each`, so a map of IDs can adopt many resources at once. Remove the blocks after the apply, or leave them - they are no-ops once the resource is in state.
5. **Discover what to import:** Terraform 1.14+ adds `terraform query`, which runs `list` blocks from `*.tfquery.hcl` files against the provider to find unmanaged resources (by tag, say), and `terraform query -generate-config-out=found.tf` writes the matching `import` and `resource` blocks. It only works for resource types whose provider implements list resources, so coverage is still growing. Since 1.12, `import` blocks can also take an `identity` object instead of a provider-specific `id` string for providers that support resource identity.

### CLI Command Import (`terraform import`)

The legacy CLI approach modifies remote state directly:

1. **Write skeleton HCL:** Write the `resource "aws_s3_bucket" "my_bucket" {}` block in `.tf`.
2. **Run CLI import:** Run `terraform import aws_s3_bucket.my_bucket bucket-name-12345`.
3. **Reconcile configuration:** Fill in missing arguments until `terraform plan` returns **No changes. Your infrastructure matches the configuration.**

## Example

Declarative import using Terraform 1.5+ `import` block:

```hcl
# main.tf

# 1. Declare the import mapping
import {
  to = aws_security_group.web_sg
  id = "sg-0123456789abcdef0"
}

# 2. Write matching resource definition
resource "aws_security_group" "web_sg" {
  name        = "web-production-sg"
  description = "Security group for production web servers"
  vpc_id      = "vpc-0a1b2c3d4e5f67890"

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

Import command workflow:

```bash
# Import blocks WITHOUT a resource block yet? Generate a draft (the file must not exist)
terraform plan -generate-config-out=imports.tf

# Review the plan: it should say "1 to import, 0 to add, 0 to change, 0 to destroy"
terraform plan
terraform apply                 # the import happens here, under the state lock

# Confirm the resource is now in state, then prove zero drift
terraform state list
terraform plan                  # "No changes."
```

## Interview tips

- Highlight that `terraform import` (CLI method) only modifies the state file (`terraform.tfstate`) and does **not** generate HCL code automatically unless using `import {}` blocks in Terraform 1.5+.
- Explain how to handle resource dependencies (import parent resources like VPCs/subnets first before importing EC2 instances or security group rules).
- Mention state safety: backup remote state or perform imports in a dedicated workspace/branch before committing changes.
- Be honest about the limits: generated config is verbose, sometimes includes conflicting or computed arguments that must be removed, and cannot express intent (variables, modules). Treat it as a starting draft. For bulk discovery, tools such as `aztfexport` (Azure) or cloud-specific exporters produce import blocks at scale.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you structure an Ansible role and share it through Galaxy?]] (`#468`): [How do you structure an Ansible role and share it through Galaxy?](../configuration-management/how-do-you-structure-an-ansible-role-and-share-it-through-galaxy.md)
- [[What is Configuration Management?]] (`#51`): [What is Configuration Management?](../configuration-management/what-is-configuration-management.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
