---
title: "How do you authenticate to AWS without long-lived access keys?"
id: 477
category: "AWS Engineering"
difficulty: "Advanced"
tags:
  - devops
  - aws-engineering
  - interview-questions
  - devsecops
  - cicd
---

# How do you authenticate to AWS without long-lived access keys?

**Short answer:** Every identity type has a keyless mechanism, and they are all `sts:AssumeRole` with a different trust anchor. **Humans** federate through IAM Identity Center (or an external IdP with SAML/OIDC) and get short-lived credentials for a permission set - no IAM users, no keys. **EC2** uses an **instance profile**; **ECS tasks** a task role; **Lambda** an execution role - the SDK picks credentials up from the metadata service or the container credentials endpoint automatically. **Kubernetes Pods on EKS** use **IRSA or EKS Pod Identity**, so a service account maps to an IAM role via OIDC. **CI/CD systems** use **OIDC workload identity federation**: GitHub Actions, GitLab, or Azure DevOps presents a signed token, and a role's trust policy exchanges it for a session - constrained to a specific repository and ref. **Other clouds or on-premises workloads** use `AssumeRoleWithWebIdentity` against their own OIDC issuer, or IAM Roles Anywhere with an X.509 certificate. The unifying sentence: an access key is a password that never expires and can be copied; a role session is a time-boxed credential bound to a verifiable identity, so the goal is that **no `AKIA...` key exists anywhere**.

## Detail

### The mechanisms, by identity type

| Identity                         | Mechanism                                                                                                                   | Trust anchor                                     |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| Engineer at a laptop             | IAM Identity Center / SAML or OIDC federation → permission set                                                              | The IdP's assertion + MFA                        |
| EC2 instance                     | Instance profile → role                                                                                                     | The instance's signed identity document (IMDSv2) |
| ECS / Fargate task               | Task role                                                                                                                   | The ECS agent's credential endpoint              |
| Lambda                           | Execution role                                                                                                              | The service                                      |
| EKS Pod                          | **IRSA** (service-account token via the cluster's OIDC provider) or **EKS Pod Identity** (an agent, no annotation plumbing) | The cluster's OIDC issuer                        |
| GitHub Actions / GitLab CI       | `AssumeRoleWithWebIdentity` against the CI provider's OIDC issuer                                                           | The CI system's signed JWT                       |
| Another AWS account              | Cross-account `AssumeRole` with an ExternalId                                                                               | The trusting account's policy                    |
| On-premises server / other cloud | **IAM Roles Anywhere** (X.509 from your CA) or OIDC federation                                                              | Your PKI or OIDC issuer                          |
| Third-party SaaS                 | Cross-account role with `sts:ExternalId`                                                                                    | Contractual + the ExternalId secret              |

All of them yield temporary credentials (access key + secret + **session token**) with an expiry. The presence of a session token is how you can tell at a glance that a credential is temporary.

### CI/CD with OIDC - the one to get exactly right

This is now the most-asked version of the question, usually phrased as _"IAM user versus a GitHub OIDC role versus a Terraform Cloud role - which is more secure and when do you use each?"_

```text
GitHub Actions job (permissions: id-token: write)
   │  requests a signed JWT from GitHub's OIDC provider
   │     iss = https://token.actions.githubusercontent.com
   │     sub = repo:acme/api:ref:refs/heads/main      <- the identity that matters
   ▼
sts:AssumeRoleWithWebIdentity  → role's trust policy validates iss, aud, and sub
   ▼
temporary credentials, ~1 hour, no secret ever stored in the repository
```

The critical detail is the **`sub` condition**. A trust policy with `"token.actions.githubusercontent.com:sub": "repo:acme/*:*"` means _any workflow in any of your repositories, on any branch, including a fork PR that can trigger a workflow_ can assume that role. Constrain it to the exact repository **and** ref or environment:

- `repo:acme/api:ref:refs/heads/main` - only the main branch.
- `repo:acme/api:environment:production` - only jobs targeting the protected environment, which is stronger because environments carry required reviewers.
- Always pin `aud` (`sts.amazonaws.com`) and the OIDC provider's thumbprint/issuer.

Then split roles by stage: a **read-only** role for `terraform plan` on pull requests and a **write** role only for the apply job in a protected environment. A hostile pull request can trigger a plan; it must not be able to mutate anything.

### Cross-account access and the `ExternalId`

Two accounts, one role: account B's role trusts a principal in account A (`arn:aws:iam::A:role/app`), and the caller does `sts:AssumeRole`. That is the answer to "account A has an EC2 instance, account B holds tokens the instance must read": give the instance a role, let B's role trust that role, and have the application assume it - no keys copied between accounts. For **third parties**, add `sts:ExternalId` - a secret the third party supplies and your trust policy requires - which prevents the confused-deputy problem where another of the vendor's customers tricks them into using their access on your account.

Also worth naming: **resource-based policies** sometimes remove the need to assume anything. An S3 bucket policy or a KMS key policy can grant a principal in another account direct access, which is simpler than role chaining for single-resource sharing. Choosing between "assume a role" and "grant on the resource" is a real design decision, and the VPC-side counterpart (endpoints, PrivateLink) is a different axis entirely - a permissions grant does not create a network path.

### IRSA versus EKS Pod Identity

Both give a Pod an IAM role. **IRSA** works by the cluster's OIDC provider: annotate a service account with a role ARN, the Pod gets a projected service-account token, and the SDK exchanges it via `AssumeRoleWithWebIdentity`. It works on any Kubernetes cluster with an OIDC issuer, including self-managed and non-EKS. **EKS Pod Identity** is newer and simpler: an agent on the node vends credentials, associations are made through the EKS API rather than trust-policy editing, and it avoids the annotation-plus-trust-policy round trip and the cross-account trust complexity. Either way, the point is the same: **no key in a Secret**, and the identity is the workload rather than the node. Do not fall back to the node's instance profile - that gives every Pod on the node the same permissions.

### Killing the keys you already have

An honest answer includes the migration:

1. **Inventory**: Credential Report and Access Advisor - find every IAM user with an access key, when it was last used, and for what services.
2. **Alert on creation**: an SCP denying `iam:CreateAccessKey` (with a break-glass exception), plus a Config rule and an EventBridge alarm.
3. **Rotate then replace**: for each key, identify the workload and move it to the right mechanism (instance profile, IRSA, OIDC), then deactivate the key, wait, and delete it. Deactivate first - it is instantly reversible; deletion is not.
4. **Detect leaks**: GitHub secret scanning push protection, `gitleaks`/`trufflehog` in CI, and GuardDuty findings for credentials used from an unexpected location.
5. **IMDSv2 required** on every instance (`http_tokens = required`) - IMDSv1's simple GET is what SSRF attacks use to steal instance role credentials. This is a specific, high-value hardening step people forget.
6. **Compromise response**: if a key leaks, deactivate it immediately, review CloudTrail for what it did, rotate anything it could have read, and only then work out how it escaped. For a compromised **instance**, isolate it with a deny-all security group and snapshot it for forensics before terminating - do not terminate first.

### Making it usable for engineers

The reason people create access keys is that the alternative was inconvenient. Fix that: `aws sso login` with a named profile per account/role in `~/.aws/config`, `credential_process` for tools that cannot do SSO, and `aws sts get-caller-identity` as the habit for "which identity am I?" Once assuming a role is one command, keys stop appearing.

## Example

```hcl
# GitHub Actions OIDC: read-only for plan, write only from the protected environment
data "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
}

resource "aws_iam_role" "gha_plan" {
  name = "gha-api-plan-readonly"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Federated = data.aws_iam_openid_connect_provider.github.arn }
      Action    = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = { "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com" }
        StringLike   = {
          # scoped to ONE repository; pull requests may plan, nothing more
          "token.actions.githubusercontent.com:sub" = "repo:acme/api:*"
        }
      }
    }]
  })
}

resource "aws_iam_role" "gha_apply" {
  name = "gha-api-apply"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Federated = data.aws_iam_openid_connect_provider.github.arn }
      Action    = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          # exact: only jobs in the protected "production" environment
          "token.actions.githubusercontent.com:sub" = "repo:acme/api:environment:production"
        }
      }
    }]
  })
}
```

```yaml
# The consumer side: no secrets in the repository at all
permissions: { contents: read, id-token: write } # id-token is what enables OIDC
steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::111122223333:role/gha-api-apply
      aws-region: eu-west-1
      role-session-name: gha-${{ github.run_id }} # traceable in CloudTrail
  - run: aws sts get-caller-identity
```

```yaml
# EKS: the Pod, not the node, holds the identity (IRSA)
apiVersion: v1
kind: ServiceAccount
metadata:
  name: payments
  namespace: prod
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::111122223333:role/payments-irsa
---
apiVersion: apps/v1
kind: Deployment
metadata: { name: payments, namespace: prod }
spec:
  template:
    spec:
      serviceAccountName: payments # SDK finds credentials automatically; no Secret
      containers:
        - name: app
          image: registry.example.com/payments:1.9.0
```

```hcl
# Cross-account, and a third party with ExternalId (confused-deputy protection)
resource "aws_iam_role" "read_tokens" {
  name = "read-tokens"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      { Effect = "Allow", Action = "sts:AssumeRole",
        Principal = { AWS = "arn:aws:iam::111122223333:role/app-instance" } },
      { Effect = "Allow", Action = "sts:AssumeRole",
        Principal = { AWS = "arn:aws:iam::999988887777:root" },   # the vendor
        Condition = { StringEquals = { "sts:ExternalId" = var.vendor_external_id } } }
    ]
  })
}

# Require IMDSv2 so SSRF cannot lift instance credentials
resource "aws_instance" "app" {
  # ...
  metadata_options {
    http_tokens                 = "required" # IMDSv2 only
    http_put_response_hop_limit = 1          # containers cannot reach it via a hop
  }
}
```

```bash
# Find and kill the keys you already have
aws iam generate-credential-report >/dev/null && \
aws iam get-credential-report --query Content --output text | base64 -d \
  | awk -F, 'NR==1 || ($9=="true")' | cut -d, -f1,9,10,11   # users with active keys

aws iam deactivate-access-key --user-name legacy-ci --access-key-id AKIAIOSFODNN7EXAMPLE
# ...verify nothing broke, then:
aws iam delete-access-key --user-name legacy-ci --access-key-id AKIAIOSFODNN7EXAMPLE

# Which identity am I right now? (temporary creds always carry a session token)
aws sts get-caller-identity
aws configure list | grep token
```

## Interview tips

- Open with the unifying idea: every mechanism is `AssumeRole` with a different trust anchor, and the goal is that no `AKIA...` key exists anywhere. Then enumerate by identity type - human, EC2, ECS, Lambda, EKS Pod, CI, cross-account, on-premises.
- For the CI question, name OIDC federation and immediately give the **`sub` constraint**. Saying "`repo:acme/*:*` is not a constraint - scope it to the repository and ref or environment" is the single highest-signal sentence in this answer.
- Add the read-only-plan versus write-apply role split. It shows you have thought about hostile pull requests, not just about removing keys.
- Explain the difference between IRSA and EKS Pod Identity, and say why you never fall back to the node's instance profile (every Pod on the node inherits it).
- For cross-account, describe the trust-policy direction correctly (the target account's role trusts the source principal) and bring up `ExternalId` with the confused-deputy explanation for third parties.
- Note that a resource-based policy can sometimes replace role assumption entirely, and that a permissions grant is not a network path - the VPC-side answer (endpoints, PrivateLink) is a separate axis. Interviewers often ask both halves.
- Volunteer **IMDSv2 required** as hardening, and explain the SSRF attack it blocks. It is specific, it is real, and few candidates raise it.
- Cover the migration honestly: credential report, SCP denying `iam:CreateAccessKey`, deactivate-before-delete, secret scanning, and GuardDuty for credentials used from unexpected locations. Then say why keys appear in the first place - the keyless path was inconvenient - and fix that with `aws sso login` profiles. See [how does AWS IAM evaluate a request](./how-does-aws-iam-evaluate-a-request.md), [securing Pod access to AWS resources with EKS Pod Identity or IRSA](./how-do-you-secure-pod-access-to-aws-resources-using-eks-pod-identity-or-irsa.md), [designing least-privilege identity in the cloud](../cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md), and [running Terraform through a CI/CD pipeline](../infrastructure-as-code/how-do-you-run-terraform-through-a-ci-cd-pipeline.md).

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
