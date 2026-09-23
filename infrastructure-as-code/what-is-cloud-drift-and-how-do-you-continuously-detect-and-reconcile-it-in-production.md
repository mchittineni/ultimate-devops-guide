---
title: "What is Cloud Drift and how do you continuously detect and reconcile it in production?"
id: 555
category: "Infrastructure as Code"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - iac
  - terraform
  - drift
  - gitops
  - reconciliation
quiz:
  stem: "What does an exit code of `2` indicate when running `terraform plan -detailed-exitcode` in an automated drift detection pipeline?"
  options:
    - "Terraform crashed due to a syntax error"
    - "The configuration matches reality exactly with no changes needed"
    - "Drift was detected between the Terraform code and the live infrastructure"
    - "The state file backend is locked by another operator"
  answer: 3
  explanation: "When invoked with `-detailed-exitcode`, 0 means clean with no changes, 1 indicates an error, and 2 indicates that a diff exists (drift detected)."
---

# What is Cloud Drift and how do you continuously detect and reconcile it in production?

**Short answer:** Cloud drift occurs when real-world cloud infrastructure changes out-of-band (via console clicks, emergency scripts, other automation, or provider-side changes) so it no longer matches the IaC definition; it is detected and resolved via scheduled refresh jobs, GitOps reconciliation tools, and read-only console permissions.

## Detail

Drift happens when an engineer modifies a security group in the AWS console at 2 a.m. to fix an incident and forgets to commit the change to Terraform.

### Consequences of Unmanaged Drift

- The next scheduled `terraform apply` overwrites the hotfix, re-introducing the production outage.
- Audits and compliance reports become invalid because source code does not represent reality.

### Continuous Drift Detection & Remediation

1. **Scheduled Speculative Runs**: Configure CI/CD (GitHub Actions, or the built-in drift detection in HCP Terraform, Spacelift, or env0) to run `terraform plan -detailed-exitcode` on a cron schedule (e.g. every night):
   - Exit code 0: No changes.
   - Exit code 2: Drift detected! Triggers a Slack alert or PagerDuty ticket.
2. **GitOps Operators for IaC**: Controllers such as Flux's Tofu Controller (formerly Weave TF-Controller) or Crossplane run continuous reconciliation loops inside a Kubernetes cluster, detecting and optionally auto-reverting out-of-band changes.
3. **Read-Only Console Access**: Prevent drift at the source by revoking write permissions in production consoles, forcing all changes through pull requests, with an audited break-glass role for incidents.
4. **Cloud-side detection**: AWS Config rules, CloudTrail-based alerts on write API calls by humans, or Azure Policy show _who_ changed _what_, which a Terraform plan cannot.

### Reconcile: adopt or revert

Drift is a decision, not just an alert. If the manual change was right (the 2 a.m. hotfix), **adopt** it: update the code to match and confirm with an empty plan (or `terraform apply -refresh-only` for attributes you only need to record). If it was wrong, **revert** it by applying the code. Auto-revert is attractive but dangerous: it can undo an incident fix in the middle of an incident, so most teams alert automatically and revert only for well-understood resource classes.

Note the limit of plan-based detection: Terraform only sees resources it manages. A resource created entirely outside Terraform is invisible to `plan`; finding those needs inventory tooling (AWS Config, Resource Graph, cloud asset inventory) compared against state.

## Example

```yaml
# .github/workflows/drift.yml - nightly drift detection per state
name: drift
on:
  schedule:
    - cron: "17 3 * * *"
permissions:
  contents: read
  id-token: write
jobs:
  plan:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        stack: [prod/network, prod/platform, prod/data]
    defaults:
      run:
        working-directory: live/${{ matrix.stack }}
    steps:
      - uses: actions/checkout@v7
      - uses: hashicorp/setup-terraform@v4
      - uses: aws-actions/configure-aws-credentials@v6
        with:
          role-to-assume: arn:aws:iam::111122223333:role/tf-plan-readonly
          aws-region: eu-west-1
      - run: terraform init -input=false
      - name: Detect drift
        run: |
          set +e
          terraform plan -detailed-exitcode -lock=false -input=false -no-color > plan.txt
          code=$?
          if [ "$code" -eq 2 ]; then echo "::error::Drift detected in ${{ matrix.stack }}"; cat plan.txt; exit 1; fi
          exit "$code"
```

## Interview tips

- Define drift precisely - live infrastructure no longer matches the declared configuration - and name the causes (console changes, other automation, provider-side changes).
- Explain the exit codes: 0 clean, 1 error, 2 changes present.
- Treat reconciliation as a choice: adopt a legitimate change into code, or revert an illegitimate one - and explain why blind auto-revert can undo an incident fix.
- Mention prevention (read-only production access, break-glass roles) as more valuable than detection.
- Note the blind spot: `plan` cannot see unmanaged resources; cloud inventory tools cover that.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between mutable and immutable infrastructure in modern deployment patterns?]] (`#586`): [What is the difference between mutable and immutable infrastructure in modern deployment patterns?](../configuration-management/what-is-the-difference-between-mutable-and-immutable-infrastructure-in-modern-deployment-patterns.md)
- [[What are ephemeral preview environments and how do you manage their lifecycle and cleanup?]] (`#535`): [What are ephemeral preview environments and how do you manage their lifecycle and cleanup?](../cicd/what-are-ephemeral-preview-environments-and-how-do-you-manage-their-lifecycle-and-cleanup.md)
- [[What is Configuration Management?]] (`#51`): [What is Configuration Management?](../configuration-management/what-is-configuration-management.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
