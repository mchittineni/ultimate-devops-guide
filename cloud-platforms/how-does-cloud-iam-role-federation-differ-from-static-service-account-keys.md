---
title: "How does Cloud IAM Role Federation differ from static Service Account keys?"
id: 546
category: "Cloud Platforms"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - cloud
  - iam
  - security
  - federation
quiz:
  stem: "What is the primary operational and security advantage of using Workload Identity Federation instead of downloading a service account JSON private key?"
  options:
    - "Federation makes API requests run twice as fast"
    - "Federation issues short-lived temporary credentials, eliminating static secrets that can be leaked in source code or CI systems"
    - "Federation allows unauthenticated anonymous access to cloud resources"
    - "Static keys can only be used on Windows operating systems"
  answer: 2
  explanation: "Workload Identity Federation eliminates permanent private key files entirely, exchanging ephemeral identity tokens for short-lived credentials that auto-expire."
---

# How does Cloud IAM Role Federation differ from static Service Account keys?

**Short answer:** Federation exchanges a token the workload already has from a trusted identity provider (an OIDC token from GitHub Actions or Kubernetes, a SAML assertion, an AWS or Azure identity) for **short-lived, auto-expiring** cloud credentials via the provider's Security Token Service. A static key - a GCP service account JSON key or an AWS IAM user access key - is a long-lived bearer secret that works from anywhere until someone deletes it. Federation removes the secret to store, rotate, and leak; the price is a trust configuration you must scope tightly.

## Detail

**Why static keys are the problem.** A downloaded key is a bearer credential: whoever holds the file _is_ the identity. Keys end up on laptops, in CI variables, in container images, and in Git history. They are rarely rotated, carry no binding to where they are used, and outlive the workload that needed them. Leaked long-lived credentials are consistently one of the most common initial-access vectors in cloud breaches.

**How federation works.**

1. The workload obtains a signed identity token from an issuer it already trusts - GitHub's OIDC provider, the Kubernetes API server's service-account issuer, Entra ID, Okta.
2. It presents that token to the cloud STS (AWS `AssumeRoleWithWebIdentity`, GCP Security Token Service, Entra ID workload identity federation).
3. The STS verifies the signature against the issuer's published keys (JWKS) and checks the claims - issuer, audience, and subject such as `repo:acme/api:ref:refs/heads/main` or `system:serviceaccount:payments:api`.
4. If the trust policy matches, it returns temporary credentials - on AWS one hour by default for web identity (configurable from 15 minutes up to the role's maximum session duration, at most 12 hours); on GCP, access tokens valid for about an hour.

**The equivalents per provider.**

| Use case             | AWS                                   | GCP                                  | Azure                                          |
| -------------------- | ------------------------------------- | ------------------------------------ | ---------------------------------------------- |
| CI/CD (e.g. GitHub)  | IAM OIDC provider + role trust policy | Workload Identity Federation pool    | Federated credential on app / managed identity |
| Kubernetes pods      | EKS Pod Identity (or IRSA)            | Workload Identity Federation for GKE | Microsoft Entra Workload ID on AKS             |
| Cloud-native compute | Instance profile / execution role     | Attached service account             | Managed identity                               |

**Secure-by-default direction.** GCP organizations created since 2024 enforce the `iam.disableServiceAccountKeyCreation` organization policy by default, and AWS recommends against IAM users for workloads altogether. Treat key creation as an exception that needs a justification and an expiry.

**Trade-offs and limitations.** The trust policy is now the secret: an audience or subject condition that is too broad (for example `repo:acme/*` or no `sub` check at all) lets any repository or branch assume the role. Federation also needs the workload to reach the STS endpoint, and some third-party tools still only accept static keys - in which case store them in a secrets manager, scope them narrowly, and rotate automatically.

## Example

GitHub Actions to AWS with no stored secret - the trust policy pins the audience and the exact repository and branch:

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
          "token.actions.githubusercontent.com:sub": "repo:acme/api:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

```yaml
# .github/workflows/deploy.yml (excerpt)
permissions:
  id-token: write # allow the job to request an OIDC token
  contents: read
steps:
  - uses: aws-actions/configure-aws-credentials@v6 # pin to a full commit SHA in production
    with:
      role-to-assume: arn:aws:iam::123456789012:role/gha-deploy
      aws-region: eu-west-1
  - run: aws sts get-caller-identity # temporary credentials, expire automatically
```

## Interview tips

- Describe the mechanism: token from a trusted issuer, STS verifies signature and claims, returns short-lived credentials. "It uses OIDC" alone is too thin.
- Name the per-provider equivalents: AWS OIDC roles and EKS Pod Identity/IRSA, GCP Workload Identity Federation, Azure federated credentials and Entra Workload ID.
- Stress claim scoping - a missing `sub` condition is the classic misconfiguration that turns federation into an open door.
- Mention the preventive control: block key creation by policy (GCP org policy, AWS SCPs denying `iam:CreateAccessKey`) and alert on any that exist.
- Expected follow-up: "What if a tool only supports static keys?" - secrets manager, least privilege, automated rotation, and detection on usage.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How Do You Configure Google Cloud Workload Identity for Secure GKE Service Authentication?]] (`#746`): [How Do You Configure Google Cloud Workload Identity for Secure GKE Service Authentication?](../gcp-engineering/how-do-you-configure-google-cloud-workload-identity-for-secure-gke-service-authentication.md)
- [[How Does Google Cloud Armor Defend Against DDoS and OWASP Top 10 Web Vulnerabilities?]] (`#747`): [How Does Google Cloud Armor Defend Against DDoS and OWASP Top 10 Web Vulnerabilities?](../gcp-engineering/how-does-google-cloud-armor-defend-against-ddos-and-owasp-top-10-web-vulnerabilities.md)
- [[How Do You Implement VPC Service Controls to Prevent Data Exfiltration in Google Cloud?]] (`#750`): [How Do You Implement VPC Service Controls to Prevent Data Exfiltration in Google Cloud?](../gcp-engineering/how-do-you-implement-vpc-service-controls-to-prevent-data-exfiltration-in-google-cloud.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Platforms](./README.md) · [All topics](../README.md)
