---
title: "How do you prevent and handle secret leaks in CI/CD pipelines?"
id: 237
category: "CI/CD"
difficulty: "Intermediate"
tags:
  - devops
  - cicd
  - interview-questions
---

# How do you prevent and handle secret leaks in CI/CD pipelines?

**Short answer:** Prevent secret leaks by enforcing pre-commit secret scanners (Gitleaks, TruffleHog), using short-lived OIDC federated credentials, masking secrets in pipeline stdout/stderr, and immediately revoking, rotating, and auditing compromised keys if a leak occurs.

## Detail

Hardcoded credentials (AWS keys, database passwords, API tokens) committed to version control or printed in CI execution logs represent one of the most critical security risks in modern software delivery.

### 1. Shift-Left Prevention (Pre-Commit & Push Hooks)

- **Local Scanning:** Developers use pre-commit hooks running `gitleaks` or `trufflehog` to catch secrets before `git commit`.
- **Repository Branch Protections:** Secret scanning integrated into GitHub/GitLab PR checks blocks merges containing credential entropy patterns.

### 2. Eliminating Long-Lived Static Secrets (OIDC & Vault)

- **OpenID Connect (OIDC):** Instead of storing static `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in GitHub Secrets, use OIDC authentication to exchange short-lived JWT tokens for temporary AWS IAM role credentials.
- **Dynamic Secrets:** Use HashiCorp Vault or AWS Secrets Manager to inject short-lived secrets at runtime rather than storing them in CI variable stores.

### 3. Log Masking & Sanitization

- Ensure CI runner engines automatically mask values defined in secret stores.
- Never run `set -x` or output environment variables (`env`, `printenv`) in build shell scripts without explicitly redacting sensitive values.

### 4. Emergency Incident Response Workflow

If a secret is exposed in a commit or pipeline log:

1. **Revoke & Rotate:** Immediately invalidate the leaked credential in the target system (AWS IAM, DB, API provider).
2. **Audit Logs:** Review CloudTrail / audit logs for any access made using the leaked key between the commit timestamp and revocation.
3. **Purge Git History:** Use `git-filter-repo` or BFG Repo-Cleaner to remove the secret from Git history (simply deleting the file in a new commit leaves the secret accessible in historical commits).

## Example

GitHub Actions workflow using OIDC to authenticate with AWS without static credentials:

```yaml
name: Deploy Infrastructure

on:
  push:
    branches: [main]

permissions:
  id-token: write # Required for requesting the OIDC JWT token
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Configure AWS Credentials via OIDC
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsCI-Role
          aws-region: us-east-1

      - name: Run Terraform Apply
        run: |
          terraform init
          terraform apply -auto-approve
```

Sample `.pre-commit-config.yaml` snippet:

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

## Interview tips

- Always highlight **OIDC (OpenID Connect)** over static API keys — this is what enterprise interviewers expect to hear.
- Explain why running `git rm secret.txt` in a subsequent commit is insufficient: the secret remains in `.git` packfiles and commit history.
- Mention automated key rotation pipelines and immediate audit logging (e.g., CloudTrail events) as part of incident response.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you rotate secrets without downtime?]] (`#429`): [How do you rotate secrets without downtime?](../devsecops/how-do-you-rotate-secrets-without-downtime.md)
- [[What do you need to know about Maven as a DevOps engineer?]] (`#461`): [What do you need to know about Maven as a DevOps engineer?](../devops-tools-and-automation/what-do-you-need-to-know-about-maven-as-a-devops-engineer.md)
- [[How do you troubleshoot a GitOps pipeline that will not sync?]] (`#428`): [How do you troubleshoot a GitOps pipeline that will not sync?](../devops-tools-and-automation/how-do-you-troubleshoot-a-gitops-pipeline-that-will-not-sync.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
