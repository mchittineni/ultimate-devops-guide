---
title: "How do you run Terraform through a CI/CD pipeline?"
id: 466
category: "Infrastructure as Code"
difficulty: "Advanced"
tags:
  - devops
  - infrastructure-as-code
  - interview-questions
  - cicd
  - devsecops
---

# How do you run Terraform through a CI/CD pipeline?

**Short answer:** Nobody should be running `apply` from a laptop against production. The pipeline shape that works: on a **pull request**, run `fmt -check`, `validate`, security scanning (Checkov/tfsec/tflint), a policy check, and `terraform plan -out=tfplan` - then post the plan as a PR comment and **save the plan as an artefact**. On **merge to main**, an environment-gated job downloads that same plan and runs `terraform apply tfplan`, so what executes is exactly what was reviewed. Authentication is **OIDC federation** to short-lived cloud credentials, never a stored access key. State lives in a remote backend with **locking** (S3 with native locking or DynamoDB, Azure blob leases, GCS, Terraform Cloud) and is **separated per environment**, so a dev apply cannot touch production. The environment progression is dev → staging → prod using the **same code** with different variable files, each with its own state and its own approval.

## Detail

### The two-stage plan/apply flow, and why the saved plan matters

```text
Pull request
  ├── terraform fmt -check -recursive          fast, deterministic
  ├── terraform init -backend=false            no state access needed to validate
  ├── terraform validate
  ├── tflint / checkov / tfsec                 security + provider correctness
  ├── terraform init  (real backend, read-only creds if possible)
  ├── terraform plan -out=tfplan -lock=false   plan does not need the lock
  ├── conftest / OPA / Sentinel against the JSON plan
  └── post the plan to the PR + upload tfplan as an artefact

Merge to main  (environment-protected job, requires approval for prod)
  ├── download tfplan
  ├── terraform apply tfplan                   exactly the reviewed change
  └── publish outputs / notify
```

If you re-plan at apply time instead of applying the saved plan, someone can merge a second change (or reality can drift) between review and execution, and you apply something nobody approved. The saved plan closes that gap. Its trade-off: a stale plan will be rejected if state moved on, which is correct behaviour - re-run the pipeline.

Note the flags: `plan` does not need the state lock (`-lock=false` is safe and avoids blocking colleagues), `apply` absolutely does. And `-input=false -no-color` on every command so the job never hangs on a prompt and the logs stay readable.

### Credentials: OIDC, not keys

Long-lived cloud keys in CI are the single biggest risk in an IaC pipeline - they sit in a variable store, they never expire, and they usually have administrator rights. Replace them with workload identity federation: the CI system presents a signed OIDC token, the cloud exchanges it for a short-lived role session.

- **AWS**: an IAM role with a trust policy on `token.actions.githubusercontent.com` (or your GitLab/Azure DevOps issuer), constrained by `sub` to a **specific repository and ref/environment**. `repo:acme/*:*` is not a constraint.
- **Azure**: a federated credential on an app registration or user-assigned managed identity, scoped to the repository and environment.
- **GCP**: Workload Identity Federation with an attribute condition on the repository.

Give the plan stage a **read-only** role and the apply stage the write role. That one split means a malicious pull request cannot mutate infrastructure even though it triggers a plan.

For secrets _inside_ Terraform (database passwords, API keys), pull them at runtime from the secret manager via a data source or environment variables (`TF_VAR_db_password`), never commit `.tfvars` containing them, and remember **state contains them in plaintext** - so the state bucket needs encryption, versioning, tight IAM, and access logging. That is the honest answer to "do you commit `tfvars`?": non-secret values yes, secrets never, and secret values in state are why the backend is a sensitive asset.

### State layout and locking

- **One state per environment per component.** `prod/network`, `prod/eks`, `prod/data`, and the same for staging - separated by lifecycle and blast radius. A single monolithic state makes every plan slow and every apply risky.
- **Locking is mandatory** for concurrent teams. Two people applying the same state simultaneously corrupts it; the backend lock is what prevents that, and `terraform force-unlock` is only for a confirmed-dead apply.
- **Serialise applies per state in CI**: a concurrency group keyed on the state path with `cancel-in-progress: false`, so pipelines queue rather than collide. This is the CI-level answer to the locking question and it is the part candidates forget.
- Cross-state references via `terraform_remote_state` (read-only, coupling) or, better, by publishing outputs to SSM/Key Vault and reading them as data sources - looser coupling and no permission on another team's state.

### Policy and security gates

- **`tflint`** with the provider ruleset for provider-specific errors a plan would only reveal at apply.
- **`checkov` / `tfsec` / `trivy config`** for misconfiguration - unencrypted volumes, public buckets, `0.0.0.0/0` ingress. Gate on severity, allow documented exceptions inline so the gate stays credible.
- **Policy as code on the plan JSON**: `terraform show -json tfplan | conftest test -` (or Sentinel in Terraform Cloud). This is stronger than scanning code, because it evaluates the _actual_ proposed change: "no resource may be deleted in prod without the `approved-destroy` label", "every resource must carry a cost-centre tag", "no security group may open 22 to the world".
- **Drift detection** as a scheduled job: `terraform plan -detailed-exitcode` on every state (exit 2 = drift) and alert on it. Otherwise the console changes people make quietly accumulate until an unrelated apply reverts them at the worst moment.

### Where the pipeline runs

- **Hosted runners** are fine when the provider APIs are public.
- **Self-hosted runners** are needed when the API endpoints are private (a private EKS endpoint, a database inside a VPC, an on-premises provider). Make them ephemeral, in the target network, and least-privileged. Never attach them to a public repository.
- **Terraform Cloud / Spacelift / Atlantis / env0** give you plan/apply orchestration, run queues, state, policy, and an approval UI out of the box. Atlantis is the classic PR-comment workflow (`atlantis plan`, `atlantis apply`) and is worth naming as the "we built this ourselves" alternative.

### Failure handling

There is no rollback. A failed apply leaves partial resources recorded in state, so you **fix forward** - correct the code and apply again. Design for it: idempotent configuration, `create_before_destroy` on anything replacement-prone, and small blast radius per state so a partial failure is bounded. If an apply is interrupted, expect a held lock and a possibly stale state; verify with `plan` before doing anything else, and only `force-unlock` after confirming no run is alive. See [recovering a lost or corrupted Terraform state file](./how-do-you-recover-a-lost-or-corrupted-terraform-state-file.md).

### Making it fast

A slow plan is usually a huge state (every refresh queries every resource), a distant backend, or an artificially serialised graph. Split state, cache the provider plugin directory between runs (`TF_PLUGIN_CACHE_DIR`), use `-refresh=false` where you know state is fresh, and only plan the components a change actually touches - path filters or a tool such as Terragrunt/Terramate that understands your stack layout. That is the answer to "the Terraform pipeline takes 25 minutes".

## Example

```yaml
# GitHub Actions: plan on PR with read-only OIDC, apply the SAVED plan on merge
name: terraform
on:
  pull_request: { paths: ["infra/**"] }
  push: { branches: [main], paths: ["infra/**"] }

permissions: { contents: read } # elevated per job only

concurrency: # serialise applies against the same state
  group: tf-prod-network
  cancel-in-progress: false

jobs:
  plan:
    runs-on: ubuntu-24.04
    permissions: { contents: read, id-token: write, pull-requests: write }
    defaults: { run: { working-directory: infra/envs/prod } }
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with: { terraform_version: 1.9.8 }
      - run: terraform fmt -check -recursive
      - run: terraform init -backend=false && terraform validate
      - uses: aws-actions/configure-aws-credentials@v4
        with: # READ-ONLY role for planning
          role-to-assume: arn:aws:iam::111122223333:role/tf-plan-readonly
          aws-region: eu-west-1
      - run: terraform init -input=false
      - run: terraform plan -out=tfplan -input=false -lock=false -no-color
      - run: terraform show -json tfplan > tfplan.json
      - run: conftest test --policy ../../policy tfplan.json # policy on the real change
      - uses: bridgecrewio/checkov-action@master
        with: { directory: infra, framework: terraform, soft_fail: false }
      - uses: actions/upload-artifact@v4
        with: { name: tfplan, path: infra/envs/prod/tfplan, retention-days: 5 }
      - if: github.event_name == 'pull_request'
        run: gh pr comment "$PR" --body "$(terraform show -no-color tfplan | head -300)"
        env: { GH_TOKEN: "${{ github.token }}", PR: "${{ github.event.number }}" }

  apply:
    if: github.ref == 'refs/heads/main'
    needs: plan
    runs-on: ubuntu-24.04
    environment: production # required reviewers gate this job
    permissions: { contents: read, id-token: write }
    defaults: { run: { working-directory: infra/envs/prod } }
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with: { terraform_version: 1.9.8 }
      - uses: aws-actions/configure-aws-credentials@v4
        with: # WRITE role, only here
          role-to-assume: arn:aws:iam::111122223333:role/tf-apply
          aws-region: eu-west-1
      - uses: actions/download-artifact@v4
        with: { name: tfplan, path: infra/envs/prod }
      - run: terraform init -input=false
      - run: terraform apply -input=false -no-color tfplan # the reviewed plan, verbatim
```

```hcl
# Backend and provider: state per environment per component, locked and encrypted
terraform {
  required_version = "~> 1.9"
  backend "s3" {
    bucket       = "acme-tfstate-prod"
    key          = "prod/network/terraform.tfstate" # one state per component
    region       = "eu-west-1"
    encrypt      = true
    use_lockfile = true # S3 native locking (or dynamodb_table = "tf-locks")
  }
}
provider "aws" {
  region = var.region
  assume_role { role_arn = var.pipeline_role_arn } # no static keys anywhere
  default_tags { tags = { ManagedBy = "terraform", Repo = "acme/infra", Env = var.environment } }
}
```

```rego
# policy/plan.rego - deny surprises in the actual proposed change
package main

deny[msg] {
  rc := input.resource_changes[_]
  rc.change.actions[_] == "delete"
  not rc.change.after
  startswith(rc.address, "aws_db_instance")
  msg := sprintf("refusing to delete a database: %s", [rc.address])
}

deny[msg] {
  rc := input.resource_changes[_]
  rc.type == "aws_security_group_rule"
  rc.change.after.cidr_blocks[_] == "0.0.0.0/0"
  rc.change.after.to_port == 22
  msg := sprintf("SSH open to the world: %s", [rc.address])
}
```

```bash
# Scheduled drift detection: exit code 2 means "reality has moved"
terraform plan -detailed-exitcode -refresh-only -lock=false -no-color
case $? in
  0) echo "no drift" ;;
  2) echo "DRIFT DETECTED"; terraform show -no-color; exit 1 ;;
  *) echo "plan failed"; exit 1 ;;
esac
```

## Interview tips

- Lead with the two-stage flow and the saved plan: plan on the PR, apply **that artefact** on merge. Then explain why - re-planning at apply time means executing something nobody reviewed. That detail is the single strongest thing you can say here.
- Say OIDC federation immediately, and add the two refinements: trust policies constrained to repository and ref, and a **read-only role for plan, write role for apply**. The read/write split is what stops a hostile PR from mutating infrastructure.
- Describe state layout as one state per environment per component, justified by blast radius and plan speed, and mention CI-level serialisation (a concurrency group per state) alongside backend locking.
- Answer the `tfvars` question honestly: non-secret values in version control, secrets from the secret manager at runtime, and note that **state stores secrets in plaintext**, so the backend needs encryption, versioning, and tight IAM.
- Distinguish scanning code (Checkov/tfsec) from policy on the **plan JSON** (Conftest/OPA/Sentinel), and give an example rule such as "no database deletions without an explicit approval label". Evaluating the real change is a level above linting files.
- Bring up scheduled drift detection with `-detailed-exitcode` unprompted; it is how you stop console changes accumulating silently.
- Be clear there is no rollback - fix forward, keep blast radius small, expect a held lock after an interrupted apply and verify with `plan` before force-unlocking.
- If the pipeline is slow, diagnose it: state size, backend distance, plugin cache, and planning only the components a change touches. Name Atlantis, Terraform Cloud, or Spacelift as ready-made options. See [managing Terraform state safely in a team](./how-do-you-manage-terraform-state-safely-in-a-team.md), [structuring Terraform code for multiple environments and providers](./how-do-you-structure-terraform-code-for-multiple-environments-and-providers.md), [scanning IaC before it is applied](../devsecops/how-do-you-scan-infrastructure-as-code-before-it-is-applied.md), and [authenticating to AWS without long-lived access keys](../aws-engineering/how-do-you-authenticate-to-aws-without-long-lived-access-keys.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
- [[How do you integrate SonarQube and quality gates into a pipeline?]] (`#458`): [How do you integrate SonarQube and quality gates into a pipeline?](../cicd/how-do-you-integrate-sonarqube-and-quality-gates-into-a-pipeline.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
