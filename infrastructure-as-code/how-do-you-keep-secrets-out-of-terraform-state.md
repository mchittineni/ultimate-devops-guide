---
title: "How do you keep secrets out of Terraform state?"
id: 759
category: "Infrastructure as Code"
difficulty: "Advanced"
tags:
  - devops
  - infrastructure-as-code
  - interview-questions
  - terraform
  - secrets
  - devsecops
quiz:
  stem: "A Terraform configuration reads a database password with `data \"aws_secretsmanager_secret_version\"` and passes it to `aws_db_instance.password`, marking the variable `sensitive = true`. Where does the password end up?"
  options:
    - "Nowhere - `sensitive = true` prevents it from being stored"
    - "Only in the CLI output, which is redacted"
    - "In plaintext in the state file (and in any saved plan), because both the data source result and the resource attribute are persisted; `sensitive` only redacts display"
    - "Only in AWS Secrets Manager"
  answer: 3
  explanation: "`sensitive` hides values in plan and apply output but does not change what is written to state. Data source results and regular resource arguments are persisted. Ephemeral resources and write-only arguments (Terraform 1.10/1.11+, OpenTofu 1.11+) or provider-managed secrets avoid persisting the value."
---

# How do you keep secrets out of Terraform state?

**Short answer:** First, know that `sensitive = true` does **not** keep anything out of state - it only redacts CLI output. Anything Terraform reads through a data source or sets as a normal resource argument is written to state (and to saved plan files) in plaintext. To actually keep a secret out: let the **provider or platform generate and hold it** (for example RDS `manage_master_user_password`, which keeps the password in Secrets Manager), use **ephemeral resources** to fetch or generate values that exist only during the run (Terraform 1.10+, OpenTofu 1.11+), and pass them into **write-only arguments** (`password_wo`, `secret_string_wo`, Terraform 1.11+), which the provider uses but never persists. Then protect the state you still have: encrypted, versioned, tightly scoped backend, or OpenTofu's client-side state encryption.

## Detail

### Why secrets end up in state

State is Terraform's record of every attribute it manages, so it can diff the next plan. If a password is an argument of `aws_db_instance`, it is in state. If you read it with `data "aws_secretsmanager_secret_version"`, the data source result is in state too - moving the secret to a secret manager and then reading it back with a data source only moved the problem. Saved plans (`terraform plan -out`) contain the same values, which matters when CI uploads them as artefacts.

### The options, strongest first

| Technique                            | How it works                                                                                                 | Limits                                                                  |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------- |
| **Platform-managed secret**          | The service generates and stores the credential (RDS/Aurora `manage_master_user_password`, managed identity) | Only where the provider offers it; consumers read it from the platform  |
| **Ephemeral resource**               | `ephemeral "..."` block fetches or generates a value during plan/apply; never written to state or plan       | Can only be referenced from ephemeral contexts and write-only arguments |
| **Write-only argument**              | `*_wo` arguments accept a value the provider sends to the API but does not store                             | Terraform cannot detect drift; bump `*_wo_version` to rotate            |
| **Generate outside Terraform**       | A secret manager or pipeline creates the value; the application reads it at run time                         | Terraform no longer manages the secret's lifecycle                      |
| **State encryption (OpenTofu 1.7+)** | The CLI encrypts state and plan files before they reach the backend                                          | Secret is still in state, just encrypted with a key you control         |
| **Backend hardening (always)**       | SSE-KMS, versioning, least-privilege IAM, access logging, no humans with read                                | Anyone with backend read access still sees plaintext                    |

### Ephemeral values in practice

- **Ephemeral resources** (`ephemeral "random_password"`, `ephemeral "aws_secretsmanager_secret_version"`, Vault and Kubernetes equivalents) are opened during the run and closed afterwards. They are referenced as `ephemeral.<type>.<name>.<attr>`.
- **Ephemeral variables and outputs** (`ephemeral = true`) let you pass a secret into a module or root without persisting it - useful for a token injected by CI.
- **Write-only arguments** are the bridge back to real resources: `aws_db_instance.password_wo`, `aws_secretsmanager_secret_version.secret_string_wo`. Because Terraform keeps no copy, it cannot see whether the value changed, so each has a companion `*_wo_version` you increment to trigger an update - rotation becomes an explicit, reviewable change.
- **Provider support varies.** Check that your provider version exposes the ephemeral resource or `_wo` argument you need; older providers do not.

### The rest of the hygiene

Keep secrets out of `.tfvars` in Git (inject `TF_VAR_*` from the CI secret store), avoid `output` blocks for secrets (or mark them ephemeral), restrict who can run `terraform state pull`, treat saved plan artefacts as secrets with short retention, and scan state buckets' access logs. If a secret has been in state, assume everyone with backend read access has seen it: rotate it after you remove it.

## Example

```hcl
# A database whose password never lands in state or a saved plan (Terraform 1.11+)
ephemeral "random_password" "db" {
  length  = 32
  special = false
}

resource "aws_secretsmanager_secret" "db" {
  name = "prod/orders/db-master"
}

resource "aws_secretsmanager_secret_version" "db" {
  secret_id                = aws_secretsmanager_secret.db.id
  secret_string_wo         = ephemeral.random_password.db.result # sent to the API, not stored
  secret_string_wo_version = 1                                   # bump to rotate
}

resource "aws_db_instance" "orders" {
  identifier          = "orders-prod"
  engine              = "postgres"
  instance_class      = "db.m7g.large"
  allocated_storage   = 100
  username            = "app_admin"
  password_wo         = ephemeral.random_password.db.result # write-only: no copy in state
  password_wo_version = 1
  skip_final_snapshot = false
}

# Simpler where available: let RDS own the secret entirely
# manage_master_user_password = true   (password lives only in Secrets Manager)
```

```bash
# Prove it: the value must not appear in state or in the plan JSON
terraform plan -out=tfplan
terraform show -json tfplan | jq '.resource_changes[]
  | select(.type=="aws_db_instance") | .change.after.password_wo'   # null
terraform apply tfplan
terraform state pull | jq '.resources[] | select(.type=="aws_db_instance")
  | .instances[0].attributes | {password, password_wo}'           # both null
```

## Interview tips

- Open by correcting the common belief: `sensitive = true` redacts output; it does not keep values out of state. Then say data sources persist what they read, so "we read it from Secrets Manager" is not a fix on its own.
- Rank the options: platform-managed secrets, then ephemeral resources plus write-only arguments, then generating secrets outside Terraform - and always a hardened backend underneath.
- Explain the write-only trade-off precisely: no drift detection, so rotation is an explicit `*_wo_version` bump.
- Mention saved plan files as a second leak path that CI artefact retention often ignores.
- Name OpenTofu's client-side state encryption as the answer when the secret must stay in state.
- Close with incident thinking: if a secret was in state, rotate it. See [how Terraform state is protected in team environments](./how-does-terraform-state-management-work-and-how-do-you-protect-state-files-in-team-environments.md), [running Terraform through CI/CD](./how-do-you-run-terraform-through-a-ci-cd-pipeline.md), and [Terraform versus OpenTofu](./what-is-the-difference-between-terraform-and-opentofu.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you structure an Ansible role and share it through Galaxy?]] (`#468`): [How do you structure an Ansible role and share it through Galaxy?](../configuration-management/how-do-you-structure-an-ansible-role-and-share-it-through-galaxy.md)
- [[How do you handle secrets in Ansible with Vault?]] (`#470`): [How do you handle secrets in Ansible with Vault?](../configuration-management/how-do-you-handle-secrets-in-ansible-with-vault.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
