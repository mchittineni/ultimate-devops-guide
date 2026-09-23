---
title: "What is the difference between Terraform dynamic blocks and count/for_each loops?"
id: 551
category: "Infrastructure as Code"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - iac
  - terraform
  - hcl
  - loops
quiz:
  stem: "Why is using `for_each` with a map or set preferred over `count` with a list when creating multiple cloud resources in Terraform?"
  options:
    - "Terraform prohibits the use of `count` in production code"
    - "Removing an item from the middle of a `count` list shifts all subsequent array indices, forcing unnecessary resource destruction and recreation"
    - "`count` can only create up to three resources simultaneously"
    - "`for_each` compiles faster than `count`"
  answer: 2
  explanation: "`count` identifies resources by numeric index (`aws_instance.web[1]`). Removing item 0 shifts item 1 into index 0, forcing Terraform to modify or recreate all subsequent resources. `for_each` binds by static key."
---

# What is the difference between Terraform dynamic blocks and count/for_each loops?

**Short answer:** `count` and `for_each` loop over top-level resources or modules to instantiate multiple instances, while `dynamic` blocks loop inside a single resource to generate repeatable nested configuration blocks (like ingress rules).

## Detail

Understanding where iteration occurs in HCL:

### 1. `count` vs `for_each` (Top-Level Resources)

- **`count`**: Index-based (`[0]`, `[1]`). Deleting an item from the middle of the input list causes Terraform to shift array indices, destroying and recreating all subsequent resources!
- **`for_each`**: Key-based (`["us-east"]`, `["eu-west"]`). Deleting a key only deletes that exact resource; other resources remain untouched. Always prefer `for_each` over `count` for resources.

### 2. `dynamic` Blocks (Nested Configs Inside Resources)

You cannot use `for_each` directly on nested attributes like `ingress` in a security group:

```hcl
resource "aws_security_group" "web" {
  name   = "web-sg"
  vpc_id = var.vpc_id

  dynamic "ingress" {
    for_each = var.allowed_ports
    content {
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
}
```

The iterator is named after the block (`ingress.value`, `ingress.key`) unless you set `iterator = rule`. `dynamic` can generate nested blocks of a resource, data source, provider, or provisioner, but not meta-argument blocks such as `lifecycle`.

### Trade-offs

`dynamic` blocks make configuration compact but plans harder to read, and nested blocks are often stored as sets, so changing one rule can show the whole block set as replaced in the diff. Where the provider offers a standalone resource for the nested thing, prefer it: for AWS security groups the current recommendation is `aws_vpc_security_group_ingress_rule` / `egress_rule` resources with `for_each`, which give each rule its own address, clean diffs, and no conflicts between inline and standalone rules.

## Example

```hcl
variable "ingress_rules" {
  type = map(object({ port = number, cidr = string }))
  default = {
    https = { port = 443, cidr = "0.0.0.0/0" }
    ssh   = { port = 22, cidr = "10.0.0.0/8" }
  }
}

resource "aws_security_group" "web" {
  name   = "web-sg"
  vpc_id = var.vpc_id
}

# for_each at resource level: one addressable rule per key
resource "aws_vpc_security_group_ingress_rule" "web" {
  for_each          = var.ingress_rules
  security_group_id = aws_security_group.web.id
  ip_protocol       = "tcp"
  from_port         = each.value.port
  to_port           = each.value.port
  cidr_ipv4         = each.value.cidr
  description       = each.key
}
```

## Interview tips

- State the scope difference crisply: `count`/`for_each` multiply resources or modules; `dynamic` multiplies nested blocks inside one resource.
- Explain the `count` index-shift hazard and why `for_each` keys are stable identity.
- Say that `dynamic` blocks should be used sparingly because they hurt readability, and that a standalone resource with `for_each` is often better (security group rules are the canonical case).
- Know the iterator name defaults to the block label and can be renamed with `iterator`.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between mutable and immutable infrastructure in modern deployment patterns?]] (`#586`): [What is the difference between mutable and immutable infrastructure in modern deployment patterns?](../configuration-management/what-is-the-difference-between-mutable-and-immutable-infrastructure-in-modern-deployment-patterns.md)
- [[What is Configuration Management?]] (`#51`): [What is Configuration Management?](../configuration-management/what-is-configuration-management.md)
- [[What is Puppet?]] (`#52`): [What is Puppet?](../configuration-management/what-is-puppet.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
