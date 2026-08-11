---
title: "How do you manage secrets in CI/CD pipelines?"
id: 166
category: "DevSecOps"
difficulty: "Intermediate"
tags:
  - devops
  - devsecops
  - interview-questions
---

# How do you manage secrets in CI/CD pipelines?

**Short answer:** Eliminate long-lived secrets first: have the pipeline exchange its OIDC identity token for short-lived cloud credentials, so there is nothing static to steal. For secrets that genuinely must exist, keep them in a secrets manager, inject them at run time as environment variables or files, scope them per environment, and audit every read.

## Detail

**The hierarchy, best to worst:**

1. **Workload identity federation** - CI presents an OIDC token; AWS/Azure/GCP returns credentials valid for minutes. No stored secret.
2. **Dynamic secrets** - Vault generates a database credential per job with a short lease and revokes it after.
3. **Secrets manager with pinned scope** - a stored value fetched at run time, scoped to one environment and one pipeline.
4. **CI platform secret variables** - acceptable, but shared broadly and easy to expose to forks.
5. **Committed to the repository, plaintext in the log** - the incident you will be asked about.

**Fork pull requests are the classic leak.** A workflow triggered by a fork must not receive secrets. In GitHub Actions, `pull_request` withholds them by default and `pull_request_target` does not - the latter combined with checking out the fork's code is a well-known privilege-escalation pattern. Split the pipeline: untrusted code runs without credentials; anything needing secrets runs after review, from the trusted branch.

**Assume the log is public.** Mask values, never `echo` them, avoid `set -x` around them, and remember that a secret passed as a command-line argument appears in process listings. Multi-line secrets and base64 blobs often defeat automatic masking.

**Rotation is a design requirement, not a task.** If rotating a credential requires editing 14 pipelines, it will not happen. Reference secrets by path from a single source of truth (External Secrets Operator syncing into Kubernetes, or a Vault agent) so rotation happens in one place.

**Detect what leaks anyway.** `gitleaks`/`trufflehog` in pre-commit and in CI on full history, plus provider-side secret scanning with automatic revocation. And treat any exposed secret as compromised: rotate it, do not just delete the commit.

## Example

```yaml
# GitHub Actions → AWS with no stored keys at all
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write # required to mint the OIDC token
      contents: read
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::111122223333:role/deploy-prod
          aws-region: eu-west-1
          role-duration-seconds: 900
      - run: aws sts get-caller-identity
```

```hcl
# The trust policy limits which repository and ref may assume the role
condition {
  test     = "StringLike"
  variable = "token.actions.githubusercontent.com:sub"
  values   = ["repo:acme/api:ref:refs/heads/main"]
}
```

## Interview tips

- Lead with "remove the secret entirely via OIDC federation" - it reframes the question and is what modern teams do.
- The `sub` condition pinning repo and ref is the detail that proves you have configured this rather than read about it.
- Expect the fork/`pull_request_target` question, and "what do you do after a leak?" - rotate first, forensics second.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you harden a container image and a Dockerfile?]] (`#441`): [How do you harden a container image and a Dockerfile?](../docker/how-do-you-harden-a-container-image-and-a-dockerfile.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevSecOps](./README.md) · [All topics](../README.md)
