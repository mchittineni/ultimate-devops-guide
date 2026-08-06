---
title: "What are Security Best Practices in DevOps?"
id: 40
category: "Security and Compliance"
difficulty: "Intermediate"
tags:
  - devops
  - security-and-compliance
  - interview-questions
---

# What are Security Best Practices in DevOps?

**Short answer:** Automate security into the pipeline, eliminate long-lived secrets, apply least privilege everywhere, keep dependencies and images patched, and make production observable enough to detect and respond to compromise quickly.

## Detail

**Secrets management.** No secrets in code, images, or CI configuration. Use a secrets manager (Vault, AWS Secrets Manager, Azure Key Vault) or OIDC federation so pipelines assume short-lived roles instead of holding static keys. Scan every commit for leaked credentials, and rotate anything exposed immediately.

**Identity and access.** Least privilege for humans and workloads. MFA on all human access. Short-lived, auditable elevation instead of standing admin. Regular access reviews.

**Supply chain.** Pin dependencies with lock files, scan them continuously, generate SBOMs, sign artifacts, and verify signatures at deploy time. Restrict which registries and actions/plugins your pipelines may use.

**Pipeline security.** Treat CI as production: it holds deployment credentials. Protect branches, require reviews, use ephemeral runners, and scope tokens narrowly (`permissions:` in GitHub Actions).

**Infrastructure.** Encrypt in transit and at rest, segment networks, default-deny, and scan IaC before apply.

**Runtime.** Immutable deployments, non-root containers, runtime detection, centralised audit logs in an account the workload cannot write to.

**Process.** Threat model new designs, run an incident response plan you have actually rehearsed, patch on a severity-based SLA, and keep security work in the same backlog as everything else.

## Example

```yaml
# GitHub Actions: no static cloud keys, minimum token scope
permissions:
  contents: read
  id-token: write # OIDC only

steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789012:role/gha-deploy
      aws-region: eu-west-1 # short-lived credentials, no secrets stored
```

## Interview tips

- Lead with secrets and identity — they are the source of most real breaches.
- "Treat CI/CD as production infrastructure" is a strong, senior-sounding point.
- Pair every practice with how you would verify it is actually in place.

---

[⬅ Back to Security and Compliance](./README.md) · [All topics](../README.md)
