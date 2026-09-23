---
title: "How does OpenID Connect (OIDC) eliminate long-lived cloud credentials in CI/CD pipelines?"
id: 533
category: "CI/CD"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - cicd
  - oidc
  - security
  - iam
  - aws
quiz:
  stem: "How does OIDC authentication verify that a deployment request originates from the `main` branch of an approved repository?"
  options:
    - "The developer enters an SMS verification code during the pipeline execution"
    - "The cloud provider validates the cryptographic signature of the OIDC JWT and matches claims like `sub` against its IAM trust policy"
    - "The CI system stores the cloud provider's master root password"
    - "OIDC requires an open SSH port on the target cloud virtual machines"
  answer: 2
  explanation: "The CI provider mints a signed JWT containing claims identifying the repository, branch, and actor. The cloud provider validates the signature and ensures claims match the IAM role trust policy."
---

# How does OpenID Connect (OIDC) eliminate long-lived cloud credentials in CI/CD pipelines?

**Short answer:** OIDC allows CI runners to exchange a short-lived cryptographically signed JSON Web Token (JWT) directly for temporary cloud IAM credentials, eliminating the need to store static, long-lived access keys in CI secret stores.

## Detail

Static cloud credentials (like `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`) stored in GitHub Actions or GitLab secrets are frequently leaked via compromised dependencies, misconfigured build logs, or malicious pull requests.

### The OIDC Exchange Workflow

```text
1. CI Job starts -> Requests OIDC token from CI Provider (e.g. GitHub token service)
2. CI Provider issues signed JWT containing claims (sub: repo:org/repo:ref:refs/heads/main, aud: sts.amazonaws.com)
3. CI Runner presents JWT to Cloud STS (AssumeRoleWithWebIdentity)
4. Cloud IAM verifies JWT against CI Provider's OIDC discovery endpoint (.well-known/openid-configuration)
5. Cloud IAM evaluates trust policy (checks repo name and branch) -> Issues temporary credentials (1 hour by default)
```

The security gain comes from three properties: there is **no stored secret** to leak, the token is **short-lived** (minutes for the JWT, typically an hour for the cloud session), and the trust decision is made on **verifiable claims** - repository, branch or tag, environment, workflow - rather than on possession of a key. The same pattern works with Azure (workload identity federation on an Entra ID app registration or managed identity), Google Cloud (Workload Identity Federation), HashiCorp Vault (JWT auth), and GitLab CI (`id_tokens:`).

### Where it goes wrong

- **Over-broad trust conditions.** A `sub` condition of `repo:my-org/*` (or a missing `sub` condition entirely) lets any repository in the organisation - or on some providers, anyone - assume the role. Match the exact repository and ref, or better an environment.
- **Claim format surprises.** When a job uses a GitHub `environment:`, the `sub` claim becomes `repo:org/repo:environment:prod` instead of the `ref:` form, so a trust policy written for the branch stops matching.
- **Role permissions are still the blast radius.** OIDC removes the long-lived key, not the need for a least-privilege role per pipeline purpose (plan vs apply, deploy vs read).

## Example

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com" },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:my-org/my-app:environment:production"
        }
      }
    }
  ]
}
```

```yaml
# .github/workflows/deploy.yml - no AWS keys anywhere
name: deploy
on:
  push:
    branches: [main]
permissions:
  id-token: write # allows the job to request the OIDC JWT
  contents: read
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production # sub claim becomes repo:my-org/my-app:environment:production
    steps:
      - uses: aws-actions/configure-aws-credentials@v6
        with:
          role-to-assume: arn:aws:iam::123456789012:role/my-app-deploy
          aws-region: eu-west-1
      - run: aws sts get-caller-identity # proves the federated session works
```

## Interview tips

- Walk the exchange in order: job requests a JWT, cloud STS validates its signature against the issuer's published keys, trust policy checks the claims, short-lived credentials come back.
- Emphasise that the trust policy _is_ the security boundary; name the `sub` and `aud` conditions and the wildcard mistake.
- Mention the `environment:` form of the `sub` claim - it is the most common reason a working OIDC setup breaks after someone adds an approval gate.
- Be honest about limits: a compromised workflow on an allowed branch can still assume the role during the job, so pair OIDC with branch protection, environment reviewers, and least-privilege roles.
- Likely follow-up: "what about Azure or GCP?" - the same federation model under different names (Entra ID workload identity federation, GCP Workload Identity Federation).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#511`): [What is the difference between Continuous Delivery and Continuous Deployment?](../core-devops-concepts/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)
- [[What do you need to know about Maven as a DevOps engineer?]] (`#461`): [What do you need to know about Maven as a DevOps engineer?](../devops-tools-and-automation/what-do-you-need-to-know-about-maven-as-a-devops-engineer.md)
- [[What is HashiCorp Vault and how does dynamic secret generation eliminate static credentials?]] (`#631`): [What is HashiCorp Vault and how does dynamic secret generation eliminate static credentials?](../devops-tools-and-automation/what-is-hashicorp-vault-and-how-does-dynamic-secret-generation-eliminate-static-credentials.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
