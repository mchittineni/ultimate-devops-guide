---
title: "What is the difference between count and for_each in Terraform?"
id: 464
category: "Infrastructure as Code"
difficulty: "Intermediate"
tags:
  - devops
  - infrastructure-as-code
  - interview-questions
---

# What is the difference between count and for_each in Terraform?

**Short answer:** Both create multiple instances of one resource block, but they **address** those instances differently, and that is the whole difference. `count` produces a **list** indexed by position - `aws_instance.web[0]`, `[1]`, `[2]` - so identity depends on order. `for_each` takes a **map or a set of strings** and produces instances keyed by name - `aws_instance.web["api"]`, `["worker"]` - so identity is stable regardless of order. The consequence that matters in production: remove the middle element from a `count` list and Terraform **shifts every later index down**, so it destroys and recreates resources that should not have changed; remove a key from a `for_each` map and only that one instance is destroyed. So the rule is: **`for_each` by default**, and `count` only for a genuinely positional list of identical things or as a conditional on/off switch (`count = var.enabled ? 1 : 0`).

## Detail

### The index-shifting problem, concretely

This is the interview scenario almost verbatim: _three instances were created from a list of names; you remove the second name and apply - what happens to the three existing instances?_

```text
count = length(["api", "worker", "batch"])          state addresses
  web[0] = api        web[1] = worker    web[2] = batch

remove "worker" from the list  ->  ["api", "batch"]

  web[0] = api      (unchanged)
  web[1] = worker -> batch      ~ or -/+  REPLACED: it is now a different machine
  web[2] = batch                -  DESTROYED

Result: you wanted to delete one instance. Terraform destroys one and
        rebuilds another, because identity was positional.
```

With `for_each` over a map keyed by name, removing `"worker"` destroys exactly `web["worker"]` and leaves `web["api"]` and `web["batch"]` untouched. For anything stateful - a database, a disk, an instance with data - that difference is the difference between a routine change and an incident.

### Side by side

|                                    | `count`                                              | `for_each`                            |
| ---------------------------------- | ---------------------------------------------------- | ------------------------------------- |
| Accepts                            | A number                                             | A map, or a set of strings            |
| Instance address                   | `res[0]`, `res[1]` …                                 | `res["key"]`                          |
| Iterator inside the block          | `count.index`                                        | `each.key`, `each.value`              |
| Stable when the collection changes | **No** - indexes shift                               | **Yes** - keys are identity           |
| Per-instance configuration         | Awkward (index into parallel lists)                  | Natural (`each.value.size`)           |
| Conditional creation               | `count = var.enabled ? 1 : 0` - the idiomatic switch | `for_each = var.enabled ? {...} : {}` |
| Referencing one instance           | By position - fragile                                | By meaningful key                     |
| Works on modules                   | Yes (0.13+)                                          | Yes (0.13+)                           |

Both are **meta-arguments**, along with `provider`, `depends_on`, and `lifecycle` - and you cannot use both `count` and `for_each` on the same block.

### Practical `for_each` rules

- **The keys must be known at plan time.** Deriving keys from an attribute that only exists after apply (an ARN, a generated ID) gives `Invalid for_each argument ... depends on resource attributes that cannot be determined until apply`. Key on inputs you control - names, environment identifiers - and put the computed values in the _value_, not the key.
- **Sets of strings** work directly (`for_each = toset(["a","b"])`, where `each.key == each.value`); lists do **not** - convert with `toset()`, and be aware `toset` deduplicates and discards order.
- **Maps of objects** are the powerful form: one entry per instance with its own settings, which removes the parallel-list anti-pattern entirely.
- **Renaming a key is a destroy/create.** If you need to rename without replacement, use a `moved` block (`moved { from = ... to = ... }`, Terraform 1.1+) or `terraform state mv`.

### When `count` is still right

1. **A conditional resource**: `count = var.create_nat ? 1 : 0`. This is the standard on/off pattern, and the reason you then reference `aws_nat_gateway.this[0].id` (or `one(aws_nat_gateway.this[*].id)` to avoid an index error when it is disabled).
2. **N identical, interchangeable things** where position genuinely does not matter and nothing holds state - "give me 50 identical workers behind an autoscaling group" is better served by the autoscaling group itself, but "create 3 identical subnets from `cidrsubnet(...)` by index" is a legitimate `count` use because the index _is_ the meaning.
3. **Splat expressions** (`aws_instance.web[*].id`) read cleanly on a `count` list; the `for_each` equivalent is `values(aws_instance.web)[*].id` or a `for` expression.

### Related constructs people confuse with these

- **`for` expressions** (`[for x in list : upper(x)]`, `{for k, v in map : k => v.id}`) transform values; they do not create resources. Frequently used to _build_ the map you feed to `for_each`.
- **`dynamic` blocks** repeat a **nested block inside one resource** (security group rules, `setting` blocks), not the resource itself. Use them sparingly - they make plans hard to read.
- **`count` on a module** versus `for_each` on a module - the same trade-off applies, and `for_each` on modules is how you stamp out per-tenant or per-region stacks with stable addresses.
- **`tuple`/`list`/`set`/`map`** as types: a common trick question is "what is the difference between `count` and a tuple?" - `count` is a meta-argument that controls how many instances exist; a tuple is a value type with fixed-length, per-position types. They are unrelated concepts that share the idea of ordering.

### Migrating from `count` to `for_each`

You cannot just swap the meta-argument - the addresses change, so Terraform plans to destroy every indexed instance and create every keyed one. Do it deliberately with `moved` blocks (declarative, reviewable in the plan) or `terraform state mv` per instance, then confirm the plan shows **no changes** before merging. That "the plan must be empty" check is the whole safety mechanism.

## Example

```hcl
# for_each with a map of objects: stable keys AND per-instance settings
variable "services" {
  type = map(object({
    instance_type = string
    az            = string
    monitoring    = optional(bool, true)
  }))
  default = {
    api    = { instance_type = "t3.medium", az = "eu-west-1a" }
    worker = { instance_type = "t3.large", az = "eu-west-1b" }
    batch  = { instance_type = "c6i.xlarge", az = "eu-west-1c", monitoring = false }
  }
}

resource "aws_instance" "svc" {
  for_each      = var.services # keys are identity: api / worker / batch
  ami           = data.aws_ami.al2023.id
  instance_type = each.value.instance_type
  availability_zone = each.value.az
  monitoring    = each.value.monitoring
  tags          = { Name = "svc-${each.key}", Service = each.key }
}

# addressed by name, so removing "worker" touches only aws_instance.svc["worker"]
output "api_private_ip" { value = aws_instance.svc["api"].private_ip }
```

```hcl
# count: the two legitimate uses
resource "aws_nat_gateway" "this" {
  count         = var.single_nat_gateway ? 1 : 0 # 1. conditional on/off
  subnet_id     = aws_subnet.public["public-eu-west-1a"].id
  allocation_id = aws_eip.nat[0].id
}
output "nat_id" { value = one(aws_nat_gateway.this[*].id) } # null when disabled

resource "aws_subnet" "private" {
  count             = length(var.azs) # 2. index IS the meaning
  vpc_id            = aws_vpc.this.id
  availability_zone = var.azs[count.index]
  cidr_block        = cidrsubnet(var.cidr, 4, count.index + 10)
}
```

```hcl
# Building a for_each map from a list, and stamping out modules per key
locals {
  tenants = ["acme", "globex", "initech"]
  # setproduct + for = one stack per tenant per region, stable composite keys
  stacks = {
    for pair in setproduct(local.tenants, ["eu-west-1", "us-east-1"]) :
    "${pair[0]}-${pair[1]}" => { tenant = pair[0], region = pair[1] }
  }
}

module "tenant" {
  for_each = local.stacks # module addresses: module.tenant["acme-eu-west-1"]
  source   = "./modules/tenant-stack"
  tenant   = each.value.tenant
  region   = each.value.region
}
```

```bash
# Migrating count -> for_each without destroying anything
# declarative and reviewable:
cat >> moved.tf <<'EOF'
moved { from = aws_instance.web[0]  to = aws_instance.svc["api"]    }
moved { from = aws_instance.web[1]  to = aws_instance.svc["worker"] }
moved { from = aws_instance.web[2]  to = aws_instance.svc["batch"]  }
EOF
terraform plan     # MUST report "No changes" - that is the safety check

# imperative equivalent, one at a time
terraform state mv 'aws_instance.web[0]' 'aws_instance.svc["api"]'
terraform state list | grep aws_instance   # verify the new addresses
```

## Interview tips

- Lead with addressing, not syntax: `count` gives positional indexes, `for_each` gives named keys, and identity in state follows the address. Everything else is a consequence.
- Walk the index-shift scenario out loud. "Remove the middle item from a `count` list and Terraform replaces every subsequent resource" is the answer they are waiting for, and adding "which is catastrophic if those hold data" shows you have felt it.
- Give the default recommendation plainly - `for_each` unless you have a reason - and then name the two legitimate `count` uses: conditional `? 1 : 0`, and a list where the index genuinely is the meaning.
- Know the plan-time constraint on `for_each` keys and the error it produces. Keying on an attribute that only exists after apply is the most common `for_each` failure, and the fix is to key on inputs and put computed data in the value.
- Mention that lists need `toset()`, that `toset` deduplicates, and that `each.key == each.value` for sets.
- Distinguish `for_each` (creates resources) from `for` expressions (transform values) and `dynamic` blocks (repeat nested blocks). Interviewers often mix these deliberately.
- If asked how to migrate from `count` to `for_each`, name `moved` blocks or `terraform state mv`, and say the plan must show no changes afterwards. That single sentence demonstrates you have done a real migration. See [writing and structuring a reusable Terraform module](./how-do-you-write-and-structure-a-reusable-terraform-module.md), [stopping Terraform from destroying or recreating a resource](./how-do-you-stop-terraform-from-destroying-or-recreating-a-resource.md), and [managing Terraform state safely in a team](./how-do-you-manage-terraform-state-safely-in-a-team.md).

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
