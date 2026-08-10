---
title: "How do you promote a release across dev, staging, and production?"
id: 399
category: "CI/CD"
difficulty: "Intermediate"
tags:
  - devops
  - cicd
  - interview-questions
  - devops-tools-and-automation
  - configuration-management
  - security-and-compliance
---

# How do you promote a release across dev, staging, and production?

**Short answer:** Build the artefact **once**, tag it immutably with the Git SHA, and promote that exact digest through environments changing only configuration. Environment differences live outside the artefact - in per-environment values files or parameter stores - and secrets come from a secret manager at deploy time, never from the repository. Each promotion is gated by evidence (tests, smoke checks, soak time), production adds an approval and a change record, and every environment is deployed by the same code path so staging genuinely rehearses production.

## Detail

### The rule that makes promotion safe: one artefact, many configurations

If the deploy stage rebuilds per environment, you have never tested what production runs. So: build one image or package, tag it `app:<git-sha>` (plus a moving `app:staging`/`app:prod` alias for humans), push it to a registry, and have every subsequent environment deploy that digest. Promotion is then a **metadata change** - "this digest is now approved for staging" - not a new build. The same discipline applies to infrastructure: the same Terraform modules or Helm chart version, different variable files.

### Where environment differences belong

- **Non-secret configuration** - per-environment values files (`values-dev.yaml`, `values-prod.yaml`), a `dev.tfvars`/`prod.tfvars` pair, or a parameter store path per environment (`/app/prod/*`). Keep them in version control and reviewed; the diff between two environments should be readable on one screen.
- **Secrets** - fetched at deploy or run time from Vault, AWS Secrets Manager, Azure Key Vault, or the platform's own secret objects, ideally through short-lived OIDC federation so the pipeline holds no long-lived credentials. See [how do you manage secrets in CI/CD pipelines](../devsecops/how-do-you-manage-secrets-in-ci-cd-pipelines.md).
- **Scale and topology** - replica counts, instance sizes, and feature flags differ legitimately. Everything else that differs is drift, and drift is what makes staging a poor rehearsal.

### The gates between environments

Promotion is earned, and each gate should produce evidence you could show an auditor:

1. **Dev** - automatic on every green build of `main`. Post-deploy smoke test; failure rolls back immediately.
2. **Staging** - automatic after dev smoke passes. Run the integration and contract suites here, plus a database migration rehearsal against a production-shaped dataset. Hold for a short soak so error-rate and latency alerts have a chance to fire.
3. **Production** - manual approval by someone who did not author the change (separation of duties), an attached change record, and a deployment window if the organisation requires one. Then a progressive rollout - canary or blue/green - with automatic rollback on error-budget burn rather than on someone watching a dashboard.

### Making it operable

- **Version everything visible.** Record which digest is in which environment, by whom and when. `kubectl get deploy -o jsonpath` or an ArgoCD/Flux application status is the source of truth; a wiki page is not.
- **Prefer GitOps for the promotion step.** Promotion becomes a pull request that changes an image digest in the environment repository, which gives review, audit, and rollback (`git revert`) for free. See [what is GitOps](../devops-tools-and-automation/what-is-gitops.md).
- **Handle stateful changes separately.** Schema migrations must be backward compatible and applied before the code that needs them, or promotion breaks the moment you roll back. See [how do you change a production database schema without downtime](../database-management-in-devops/how-do-you-change-a-production-database-schema-without-downtime.md).
- **Keep environment count honest.** Every long-lived environment costs money and drifts; prefer ephemeral per-pull-request environments for testing and a small number of durable ones for promotion.

## Example

```text
Commit abc1234 on main
  build ......... app:abc1234  (built once, pushed, digest sha256:9f2c...)
  dev ........... deploy digest 9f2c + values-dev.yaml      auto, smoke test 40s
  staging ....... deploy digest 9f2c + values-staging.yaml  auto after dev green
                  integration suite, migration rehearsal, 30m soak
  production .... deploy digest 9f2c + values-prod.yaml     approval: @sre-oncall
                  canary 5% -> 25% -> 100%, auto-rollback on burn rate > 2x
  ------------------------------------------------------------------------
  Never rebuilt. Only the values file and the replica count changed.
```

```yaml
# One chart, one image digest, per-environment values. Promotion = change the digest.
# values-prod.yaml (reviewed in Git; secrets are NOT here)
image:
  repository: registry.example.com/checkout
  digest: sha256:9f2c8b1d... # promoted from staging by PR #4821
replicaCount: 12
resources:
  requests: { cpu: "500m", memory: "1Gi" }
env:
  LOG_LEVEL: info
externalSecrets:
  - name: checkout-db
    remoteRef: /app/prod/db-password # resolved at deploy time from the secret store
```

## Interview tips

- Say "build once, promote the artefact" in the first sentence, and give the reason: rebuilding per environment means production runs something untested. That single line answers most of the question.
- Be concrete about _what_ is allowed to differ between environments - configuration, secrets, scale - and call anything else drift.
- Describe gates as evidence rather than ceremony: smoke test, contract tests, migration rehearsal, soak, then approval by a second person for production.
- Mention rollback as part of promotion, not a separate topic, and note the constraint that database migrations impose on it.
- If the interviewer uses Kubernetes, offer the GitOps version - promotion as a pull request changing an image digest, with `git revert` as the rollback path.
- Have an opinion on environment count. "We had seven long-lived environments and cut to three plus ephemeral PR environments" is a strong, real answer. See [what are deployment strategies](../devops-tools-and-automation/what-are-deployment-strategies.md) and [continuous delivery versus continuous deployment](./what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md).

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
