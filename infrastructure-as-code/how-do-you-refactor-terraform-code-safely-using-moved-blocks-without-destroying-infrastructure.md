---
title: "How do you refactor Terraform code safely using moved blocks without destroying infrastructure?"
id: 550
category: "Infrastructure as Code"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - iac
  - terraform
  - refactoring
  - state
quiz:
  stem: "What is the primary benefit of using a Terraform `moved` block when refactoring resource names in code?"
  options:
    - "It automatically migrates virtual machines across physical cloud data centers"
    - "It updates the internal state address mapping without destroying and recreating the live cloud resource"
    - "It encrypts the Terraform code using AES-GCM"
    - "It bypasses the need to run `terraform plan`"
  answer: 2
  explanation: "Without `moved`, renaming a resource looks like a deletion of the old name and creation of a new one. `moved` blocks inform Terraform of the address change, avoiding recreation."
---

# How do you refactor Terraform code safely using moved blocks without destroying infrastructure?

**Short answer:** Terraform `moved` blocks declare that a resource or module has been renamed or relocated in code, instructing Terraform to update its internal state mapping automatically during `plan` and `apply` rather than destroying and recreating the live resource.

## Detail

Historically, renaming a resource in code (`aws_instance.server` -> `aws_instance.web`) caused Terraform to plan a destructive **Destroy and Recreate** action, or required engineers to coordinate error-prone CLI commands (`terraform state mv`).

### The `moved` Block Solution (Terraform 1.1+)

```hcl
# Old resource was: resource "aws_security_group" "web"
# New resource is in a module:
module "security" {
  source = "./modules/security"
}

# Declaratively update state:
moved {
  from = aws_security_group.web
  to   = module.security.aws_security_group.web
}
```

### Key Advantages

- **Declarative & Version-Controlled**: State moves are committed in Git alongside the refactored code.
- **Team Safe**: Every team member and CI pipeline applies the rename safely on their next run without manual CLI intervention.
- **Zero Downtime**: `terraform plan` confirms that 0 resources will be added or destroyed, only state addresses updated.

### What `moved` covers, and what it does not

- Renaming a resource, moving it into or out of a module, renaming a module call, and switching between `count` and `for_each` (`from = aws_instance.web[0]`, `to = aws_instance.web["a"]`).
- Since Terraform 1.8, moving between **resource types** where the provider supports it (for example `null_resource` to `terraform_data`).
- It cannot move resources **between state files** - that still needs `terraform state mv -state-out`, or an `import` block in the new state plus a `removed` block in the old one.
- The companion **`removed` block** (Terraform 1.7+) is the declarative way to stop managing a resource without destroying it (`lifecycle { destroy = false }`), replacing ad-hoc `terraform state rm`.

The limitation: in a shared module, a `moved` block must stay until every consumer has applied the new version, or those who upgrade late will see a destroy/create. Module authors keep them as a permanent part of the module's history.

## Example

```hcl
# Switch a count-based resource to for_each without replacing the instances
variable "web_names" {
  default = ["a", "b"]
}

resource "aws_instance" "web" {
  for_each      = toset(var.web_names)
  ami           = "ami-0123456789abcdef0"
  instance_type = "t3.micro"
  tags          = { Name = "web-${each.key}" }
}

moved {
  from = aws_instance.web[0]
  to   = aws_instance.web["a"]
}

moved {
  from = aws_instance.web[1]
  to   = aws_instance.web["b"]
}

# Stop managing a legacy bucket without deleting it
removed {
  from = aws_s3_bucket.legacy
  lifecycle {
    destroy = false
  }
}
```

```bash
terraform plan
# aws_instance.web[0] has moved to aws_instance.web["a"]
# aws_instance.web[1] has moved to aws_instance.web["b"]
# Plan: 0 to add, 0 to change, 0 to destroy.
```

## Interview tips

- Explain the mechanism: Terraform identifies resources by address, so a rename looks like delete-plus-create; `moved` tells it the old address and the new one are the same object.
- Show you know the common case - `count` to `for_each` - not just a rename.
- Say what `moved` cannot do (cross-state moves) and name the tools that can (`state mv`, or `import` + `removed`).
- Mention `removed` blocks as the declarative replacement for `terraform state rm`.
- Always finish with verification: the plan must show moves and `0 to destroy` before anyone applies.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between mutable and immutable infrastructure in modern deployment patterns?]] (`#586`): [What is the difference between mutable and immutable infrastructure in modern deployment patterns?](../configuration-management/what-is-the-difference-between-mutable-and-immutable-infrastructure-in-modern-deployment-patterns.md)
- [[What is Configuration Management?]] (`#51`): [What is Configuration Management?](../configuration-management/what-is-configuration-management.md)
- [[What is Puppet?]] (`#52`): [What is Puppet?](../configuration-management/what-is-puppet.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
