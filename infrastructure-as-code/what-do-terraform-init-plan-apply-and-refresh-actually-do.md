---
title: "What do terraform init, plan, apply, and refresh actually do?"
id: 462
category: "Infrastructure as Code"
difficulty: "Beginner"
tags:
  - devops
  - infrastructure-as-code
  - interview-questions
---

# What do terraform init, plan, apply, and refresh actually do?

**Short answer:** `init` prepares the working directory: it reads the configuration, **downloads the provider plugins** into `.terraform/`, **initialises the backend** and connects to remote state, **installs modules**, and writes or verifies `.terraform.lock.hcl` (the dependency lock file that pins provider versions and checksums). `plan` **refreshes** its picture of reality by reading the real resources, builds a dependency graph, diffs desired configuration against that state, and prints the proposed changes - `+` create, `-` destroy, `~` update in place, `-/+` destroy and recreate, `<=` read a data source. It changes nothing. `apply` does the same work and then executes the graph, walking resources in dependency order and writing the new state. `refresh` is the reconciliation step on its own: it queries the providers and updates state to match reality without touching your infrastructure - and since Terraform 0.15 the standalone `terraform refresh` is deprecated in favour of `terraform apply -refresh-only`, because silently rewriting state is dangerous and you should review the drift first.

## Detail

### `init` - what it really sets up

| Step                   | Effect                                                  | Failure you will see                                                                      |
| ---------------------- | ------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Backend initialisation | Connects to S3/AzureRM/GCS/Terraform Cloud, pulls state | `Backend initialization required`, or a state-migration prompt after changing the backend |
| Provider installation  | Downloads plugins to `.terraform/providers`             | Version constraints unsatisfiable, or a checksum mismatch against the lock file           |
| Module installation    | Copies/clones modules into `.terraform/modules`         | Bad source URL, or a private registry credential problem                                  |
| Lock file              | Creates or verifies `.terraform.lock.hcl`               | `provider ... does not match any of the checksums`                                        |

`init` is **safe and idempotent** - run it as often as you like. Flags worth knowing: `-upgrade` (allow newer provider versions within constraints, and rewrite the lock file), `-reconfigure` (discard backend settings and start fresh), `-migrate-state` (move existing state to a new backend), and `-backend-config=...` for values you keep out of the repository.

**`.terraform.lock.hcl` should be committed.** It pins the exact provider versions and their checksums so every engineer and every CI run uses identical providers, which is what makes a plan reproducible. Add `-platform=` entries when your laptops and CI runners differ in OS/architecture, or CI will fail on a missing hash.

### `plan` - the diff, and how to read it

`plan` runs a refresh first (unless you pass `-refresh=false`), so the diff is against **reality**, not against the last state file. That is why the classic interview scenario works: someone changes an instance type in the console, you run `plan`, and Terraform shows `~ instance_type: "t3.large" -> "t3.medium"` - it intends to **undo** the manual change and bring the resource back to what the code says. That is drift correction, and it is the whole point of declarative IaC.

Symbols:

```text
  + create                     resource will be created
  - destroy                    resource will be deleted
  ~ update in-place            attribute changed, no replacement needed
-/+ destroy and then create    a "ForceNew" attribute changed - EXPECT DOWNTIME
+/- create then destroy        same, but with create_before_destroy set
 <= read (data source)         will be read during apply
```

Always read the `-/+` lines and the `# forces replacement` annotations. A one-word change to a name or a subnet can quietly replace a database.

Use `-out=tfplan` to save the plan and `terraform show -json tfplan` to inspect or policy-check it. A saved plan is also what makes CI safe: the apply executes exactly what was reviewed, with no re-planning between approval and execution.

### `apply`

`apply` builds the same graph and executes it, parallelised across independent resources (default 10, tunable with `-parallelism`) and serialised where dependencies exist. Dependencies come from implicit references (`subnet_id = aws_subnet.a.id`) and, where there is no reference, from explicit `depends_on`.

Realities worth naming:

- **A partial apply is normal on failure.** If resource 7 of 20 fails, the first six are created and recorded in state. Terraform has no transactions and no rollback - you fix forward: correct the configuration and apply again. The resources it already made are in state, so it will not duplicate them.
- **Interrupting an apply** (Ctrl-C, a killed CI job) can leave state stale or the lock held. Hence `force-unlock` exists, and hence you never kill an apply casually.
- **`-auto-approve`** in a pipeline is fine only when the plan was reviewed and saved; approving a fresh plan automatically is how people destroy production.
- **`-target`** is a break-glass tool for a broken graph, not a workflow. Regular use hides drift and creates inconsistent state.

### `refresh`, drift, and `-refresh-only`

`terraform apply -refresh-only` shows you what changed outside Terraform and lets you accept those facts into state without modifying infrastructure. Use it when someone has made manual changes and you want to see the drift explicitly before deciding whether to adopt or revert it. `terraform plan -refresh-only` is the read-only version.

Compare with the two neighbours interviewers pair it with:

| Command               | Reads real infrastructure | Changes infrastructure | Changes state |
| --------------------- | ------------------------- | ---------------------- | ------------- |
| `plan`                | Yes                       | No                     | No            |
| `apply -refresh-only` | Yes                       | No                     | **Yes**       |
| `apply`               | Yes                       | Yes                    | Yes           |
| `destroy`             | Yes                       | Yes (deletes)          | Yes           |

And `terraform destroy` is simply an apply of "everything absent" - which is why `prevent_destroy` and a protected pipeline stage matter.

### The other commands you are expected to know

- **`validate`** - syntax and internal consistency, no provider API calls, no state. Runs offline after `init`. Cheap first CI step.
- **`fmt`** - canonical formatting. `fmt -check -recursive` in CI so style is not a review topic.
- **`show`** - human or JSON view of state or a saved plan.
- **`output`** - read root module outputs, `-json` for scripting.
- **`state list/show/mv/rm/pull/push`** - surgical state operations, covered in the state-management answers.
- **`console`** - an expression REPL against your state; the fastest way to work out what a `for` expression produces.
- **`graph`** - emits the dependency graph, useful when explaining why order surprised you.
- **`TF_LOG=DEBUG`** (or `TRACE`) plus `TF_LOG_PATH` - the answer to "how do you enable debug logs in Terraform?"

### Why an apply takes forever

Asked often. The usual causes: a very large single state file (every refresh queries every resource), slow provider APIs (some cloud resources genuinely take 10-20 minutes - RDS, CloudFront, EKS), a serialised graph created by unnecessary `depends_on`, low parallelism, or a state file in a distant region. Fixes: split the state by lifecycle and blast radius, `-refresh=false` when you know the state is fresh, raise `-parallelism` carefully, remove artificial dependencies, and move data-heavy work out of Terraform. See [structuring Terraform code for multiple environments](./how-do-you-structure-terraform-code-for-multiple-environments-and-providers.md).

## Example

```bash
# The canonical local loop
terraform init -upgrade                 # providers, backend, modules, lock file
terraform fmt -recursive
terraform validate                       # offline: syntax + internal consistency
terraform plan -out=tfplan               # review this; it changes nothing
terraform show -json tfplan | jq '[.resource_changes[]
  | select(.change.actions | index("delete"))
  | {addr: .address, actions: .change.actions}]'    # what will be destroyed?
terraform apply tfplan                   # executes exactly the reviewed plan
```

```text
Reading a plan properly - the two lines that matter

  ~ aws_instance.app
      ~ instance_type = "t3.large" -> "t3.medium"        # in-place, safe
      ~ tags          = { "Env" = "prod" -> "production" }

-/+ aws_db_instance.orders must be replaced
      ~ identifier = "orders" -> "orders-prod"  # forces replacement
      ...
  Plan: 1 to add, 1 to change, 1 to destroy.

  ^ that "1 to destroy" is a production database. This is why nobody
    runs `apply -auto-approve` against an unreviewed plan.
```

```bash
# Someone changed things in the console. See the drift, decide, then act.
terraform plan -refresh-only             # read-only view of reality vs state
terraform apply -refresh-only            # accept reality into state (no infra change)
#   ... or just `terraform apply` to revert the console change back to code

# Debugging and unblocking
TF_LOG=DEBUG TF_LOG_PATH=./tf.log terraform apply
terraform force-unlock 9f2c8b1d-...      # ONLY after confirming no apply is running
terraform state list | wc -l             # a huge number explains a slow refresh
```

## Interview tips

- Give `init` as four things, not one: providers, backend/state, modules, lock file. Most candidates say "it initialises Terraform", which is exactly the non-answer interviewers are testing for.
- Mention `.terraform.lock.hcl` unprompted - what it pins, that it is committed, and that `-upgrade` rewrites it. It is a common follow-up.
- Recite the plan symbols, and emphasise `-/+` with "forces replacement" as the line that causes outages. Then say you read every destroy line before approving.
- For "someone changed a resource in the console, what does `plan` show?", answer that it shows Terraform intending to revert the manual change back to the code, and name that as drift correction. For "what if they ran `apply` without planning?" - it does not error, it plans internally and applies, which is precisely why that habit is dangerous.
- Explain `refresh` as state reconciliation, note that standalone `terraform refresh` is deprecated, and recommend `apply -refresh-only` so drift is reviewed rather than silently absorbed.
- Be clear that there is **no rollback**: a failed apply leaves partial resources recorded in state, and you fix forward. Candidates who claim Terraform rolls back have not had an apply fail.
- Distinguish `validate` (offline, no API calls, no state) from `plan` (talks to providers, needs credentials and state). That pair gets asked directly.
- Know `TF_LOG=DEBUG` for debug output and `-target` as break-glass only. See [what is Terraform](./what-is-terraform.md), [managing Terraform state safely in a team](./how-do-you-manage-terraform-state-safely-in-a-team.md), [what is infrastructure drift](../advanced-devops-cloud/what-is-infrastructure-drift.md), and [stopping Terraform from destroying or recreating a resource](./how-do-you-stop-terraform-from-destroying-or-recreating-a-resource.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you structure an Ansible role and share it through Galaxy?]] (`#468`): [How do you structure an Ansible role and share it through Galaxy?](../configuration-management/how-do-you-structure-an-ansible-role-and-share-it-through-galaxy.md)
- [[What is Puppet?]] (`#52`): [What is Puppet?](../configuration-management/what-is-puppet.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
