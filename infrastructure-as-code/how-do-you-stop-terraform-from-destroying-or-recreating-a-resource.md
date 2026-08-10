---
title: "How do you stop Terraform from destroying or recreating a resource?"
id: 465
category: "Infrastructure as Code"
difficulty: "Advanced"
tags:
  - devops
  - infrastructure-as-code
  - interview-questions
  - devsecops
---

# How do you stop Terraform from destroying or recreating a resource?

**Short answer:** Match the tool to the reason. If an attribute change **forces replacement** and you cannot avoid it, `lifecycle { create_before_destroy = true }` builds the replacement first so there is no gap. If something outside Terraform mutates an attribute and every plan wants to revert it, `lifecycle { ignore_changes = [...] }` tells Terraform to stop caring about that attribute. If the resource must never be deleted by Terraform at all, `lifecycle { prevent_destroy = true }` makes any plan that would destroy it **fail**. If you want to hand a resource over to be managed manually, `terraform state rm` removes it from state and leaves the real resource alone (the modern declarative equivalent for moves is a `removed` block). And if the resource is disappearing from your code because a **module changed shape**, use a `moved` block so Terraform re-addresses it instead of destroy-and-create. On top of all that, the real protections are process: read every `-/+` line in the plan, run `plan` in CI and require review, and use provider-side deletion protection for anything holding data.

## Detail

### First, know _why_ it wants to replace

Read the plan. `-/+ must be replaced` always comes with a `# forces replacement` annotation naming the attribute. Common triggers: renaming an identifier (`identifier`, `name`, `bucket`), changing a subnet or availability zone, changing `user_data` on some instance types, editing an immutable field the cloud API cannot update in place, or a provider upgrade that changed how an attribute is handled. The fix depends entirely on which of these it is - which is why "how do I stop Terraform destroying things?" is really "read the diff first".

### The `lifecycle` block, argument by argument

| Argument                                 | What it does                                              | When to use it                                                                                                                                                   |
| ---------------------------------------- | --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `create_before_destroy = true`           | Creates the replacement **before** destroying the old one | Replacement is unavoidable and downtime is not acceptable. Watch for name/port collisions - two objects exist simultaneously, so unique names must be generated  |
| `prevent_destroy = true`                 | Any plan that would destroy this resource **errors out**  | Databases, state buckets, KMS keys, production data stores                                                                                                       |
| `ignore_changes = [tags, desired_count]` | Terraform stops reconciling those attributes              | Something else legitimately owns the value: an autoscaler adjusting `desired_capacity`, a deployment pipeline updating an image tag, a cloud service adding tags |
| `ignore_changes = all`                   | Ignore every attribute drift                              | Adopted resources you do not fully model yet. Use with discomfort - it hides real drift                                                                          |
| `replace_triggered_by = [...]`           | **Force** replacement when another resource changes       | Rebuild an instance when its launch template or a null_resource trigger changes                                                                                  |
| `precondition` / `postcondition`         | Assert invariants at plan/apply time                      | Fail fast when an AMI is not encrypted, or a CIDR overlaps                                                                                                       |

Two important limitations to state in an interview: **`prevent_destroy` does not stop a human deleting the resource in the console**, and it does not survive removing the resource block from your code - if the block is gone, so is the lifecycle rule, and Terraform will destroy it. `prevent_destroy` also blocks `terraform destroy` for the whole configuration, which is exactly what you want in production and mildly annoying in ephemeral environments (make it a variable, defaulted on for prod).

### Handing a resource over to manual management

The scenario: an integration requires two Terraform-managed resources to be taken out of Terraform's lifecycle and managed by hand, untouched and undestroyed.

```bash
terraform state rm aws_db_instance.legacy      # forget it; the real DB is untouched
# then delete the resource block from the code, or Terraform will plan to CREATE a new one
```

Order matters and both halves are required: remove from state **and** remove from configuration. Do it the other way round (delete the code first, then apply) and Terraform destroys the resource. Terraform 1.7+ adds a declarative form - a `removed` block with `lifecycle { destroy = false }` - which is reviewable in the plan and safer in a pipeline than an imperative state command. Belt and braces: enable the provider's own deletion protection first, so a mistake cannot delete it either way.

### Moving instead of replacing

When you refactor - rename a resource, wrap resources in a module, switch `count` to `for_each` - the **address** changes, and Terraform reads a new address as a new resource. `moved` blocks fix that declaratively:

```hcl
moved {
  from = aws_instance.web
  to   = module.compute.aws_instance.web
}
```

Then `terraform plan` must show **no changes**. That empty plan is the proof the refactor is safe; if it is not empty, stop. `terraform state mv` is the imperative equivalent for one-off work.

### Provider-side protection is stronger than Terraform-side

Terraform-side flags protect you from Terraform. They do nothing about the console, another pipeline, or a different state file. So for anything that matters, layer:

- `deletion_protection = true` on RDS, `enable_deletion_protection` on load balancers, S3 bucket versioning plus MFA delete, KMS key deletion windows, Azure resource locks (`CanNotDelete`), GCP liens.
- `skip_final_snapshot = false` on RDS so an accidental destroy still leaves a snapshot.
- IAM policy denying `Delete*` on production resources for the pipeline role, with a break-glass role for genuine deletions.
- An SCP at the organisation level for the truly critical things.

And the process controls: separate state per environment so a production resource cannot be caught in a dev destroy, a required `plan` review with the destroy count called out, `terraform plan -out` so the apply matches what was reviewed, and a policy check (OPA/Conftest/Sentinel) that fails a plan containing unexpected deletions.

### `-/+` versus `+/-` and the downtime question

`-/+` means destroy then create - a gap. `+/-` (which `create_before_destroy` produces) means create then destroy - no gap, but momentarily two resources. The scenario _"a configuration change caused brief downtime during apply - what happened and how do you prevent it?"_ is answered exactly here: an in-place-looking change actually forced replacement, Terraform destroyed before creating, and the fix is `create_before_destroy` plus, where the resource fronts traffic, ensuring the load balancer or DNS shifts over before the old one goes away.

### Stopping an accidental `terraform destroy`

Frequently asked as its own question. Layers, not one answer: `prevent_destroy` on the critical resources; IAM denying delete actions for the CI role; no `destroy` stage in the production pipeline at all (make it a separate, manually-triggered, approval-gated job); provider deletion protection; and separate state files so blast radius is bounded. Also remove local `terraform destroy` capability from production by not giving humans production credentials - the deploy role belongs to the pipeline.

## Example

```hcl
# 1. Replacement is unavoidable -> create the new one first
resource "aws_launch_template" "app" {
  name_prefix   = "app-" # prefix, not a fixed name: two can coexist briefly
  image_id      = data.aws_ami.al2023.id
  instance_type = var.instance_type

  lifecycle {
    create_before_destroy = true
  }
}

# 2. Something else owns the value -> stop fighting it
resource "aws_autoscaling_group" "app" {
  name             = "app"
  min_size         = 2
  max_size         = 20
  desired_capacity = 4 # the autoscaler changes this constantly

  lifecycle {
    ignore_changes = [desired_capacity, tag] # otherwise every plan reverts scaling
  }
}

resource "aws_ecs_service" "api" {
  name            = "api"
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 3

  lifecycle {
    ignore_changes = [task_definition, desired_count] # the deploy pipeline owns these
  }
}
```

```hcl
# 3. Must never be destroyed by Terraform - and by the provider either
resource "aws_db_instance" "orders" {
  identifier              = "orders-prod"
  engine                  = "postgres"
  instance_class          = var.db_instance_class
  deletion_protection     = true  # provider-side: blocks the API call itself
  skip_final_snapshot     = false # a mistake still leaves a snapshot
  backup_retention_period = 14

  lifecycle {
    prevent_destroy = true # Terraform-side: any destroy plan errors out
    precondition {
      condition     = var.environment != "prod" || var.multi_az
      error_message = "Production databases must be Multi-AZ."
    }
  }
}

# 4. Force replacement deliberately when a dependency changes
resource "aws_instance" "bastion" {
  ami           = data.aws_ami.al2023.id
  instance_type = "t3.micro"

  lifecycle {
    replace_triggered_by = [aws_launch_template.app.latest_version]
  }
}
```

```bash
# 5. Hand a resource to manual management - state first, THEN the code
terraform state rm aws_db_instance.legacy aws_s3_bucket.legacy_exports
# now delete both resource blocks; plan must show no create and no destroy
terraform plan
```

```hcl
# Terraform 1.7+: the reviewable, declarative version of the same thing
removed {
  from = aws_db_instance.legacy
  lifecycle { destroy = false } # forget it, do not delete it
}

# Refactoring without replacement
moved {
  from = aws_instance.web[0]
  to   = module.compute.aws_instance.web["api"]
}
```

```bash
# Guardrail: fail any plan that deletes something unexpected
terraform plan -out=tfplan
terraform show -json tfplan | jq -e '
  [.resource_changes[]
   | select(.change.actions | index("delete"))
   | .address] as $d
  | if ($d | length) > 0 then ($d | @json | halt_error(1)) else empty end
' || { echo "Plan contains deletions - requires explicit approval"; exit 1; }
```

## Interview tips

- Start by refusing the shortcut: read the plan and find the `# forces replacement` attribute, because the right tool depends on why replacement was triggered. That reframing is the senior answer.
- Then give the four `lifecycle` arguments with a real use for each - `create_before_destroy` for zero-gap replacement, `ignore_changes` when another system owns the value, `prevent_destroy` for data stores, `replace_triggered_by` to force a rebuild. Mentioning `precondition`/`postcondition` is a bonus.
- Name the two limits of `prevent_destroy` explicitly: it does not stop a console deletion, and it disappears if you remove the resource block. Those caveats are what interviewers probe.
- Give a concrete `ignore_changes` example that a practitioner would recognise - `desired_capacity` fought over by an autoscaler, or `task_definition` owned by the deploy pipeline. It proves the flag is not theoretical for you.
- For "take resources out of Terraform without destroying them", give the exact order - `state rm` first, then delete the code - and warn that reversing the order destroys them. Mention `removed` blocks as the declarative 1.7+ form.
- Distinguish `-/+` from `+/-` and use it to answer the brief-downtime scenario: an apparently in-place change forced replacement, destroy happened before create, and `create_before_destroy` (plus traffic shifting) is the fix.
- Layer provider-side protection over Terraform-side, and add the process controls: separate state per environment, reviewed saved plans, a policy check that fails unexpected deletions, and no destroy stage in the production pipeline. See [what do terraform init, plan, apply, and refresh actually do](./what-do-terraform-init-plan-apply-and-refresh-actually-do.md), [managing Terraform state safely in a team](./how-do-you-manage-terraform-state-safely-in-a-team.md), [importing existing infrastructure](./how-do-you-import-existing-cloud-infrastructure-into-terraform.md), and [count versus for_each](./what-is-the-difference-between-count-and-for-each-in-terraform.md).

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
