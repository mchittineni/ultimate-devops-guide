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
3. **Refine and apply:** Review `generated.tf`, clean up auto-generated attributes, run `terraform plan` to verify zero changes required, and execute `terraform apply`.

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
# Validate import plan and auto-generate code if needed
terraform plan -generate-config-out=imports.tf

# Check state list to confirm imported resource
terraform state list

# Verify zero drift after configuration matching
terraform plan
```

## Interview tips

- Highlight that `terraform import` (CLI method) only modifies the state file (`terraform.tfstate`) and does **not** generate HCL code automatically unless using `import {}` blocks in Terraform 1.5+.
- Explain how to handle resource dependencies (import parent resources like VPCs/subnets first before importing EC2 instances or security group rules).
- Mention state safety: backup remote state or perform imports in a dedicated workspace/branch before committing changes.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you structure an Ansible role and share it through Galaxy?]] (`#468`): [How do you structure an Ansible role and share it through Galaxy?](../configuration-management/how-do-you-structure-an-ansible-role-and-share-it-through-galaxy.md)
- [[What is Configuration Management?]] (`#51`): [What is Configuration Management?](../configuration-management/what-is-configuration-management.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
