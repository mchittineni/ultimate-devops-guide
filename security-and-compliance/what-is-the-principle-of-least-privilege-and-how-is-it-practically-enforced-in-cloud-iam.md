---
title: "What is the Principle of Least Privilege and how is it practically enforced in cloud IAM?"
id: 563
category: "Security and Compliance"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - security
  - iam
  - least-privilege
  - compliance
quiz:
  stem: "Which IAM policy statement demonstrates proper enforcement of the Principle of Least Privilege for an app reading objects from a single S3 bucket?"
  options:
    - "`Action: s3:*, Resource: *`"
    - "`Action: s3:GetObject, Resource: arn:aws:s3:::app-data-prod/*`"
    - "`Action: *, Resource: arn:aws:s3:::app-data-prod/*`"
    - "`Action: s3:GetObject, Resource: *`"
  answer: 2
  explanation: "Option 2 restricts the action to the single read operation (`s3:GetObject`) and scopes the target resource strictly to the specific bucket ARN."
---

# What is the Principle of Least Privilege and how is it practically enforced in cloud IAM?

**Short answer:** The Principle of Least Privilege dictates that every identity (user, service, pod) must be granted only the minimum permissions necessary to perform its specific task and for the minimum duration required.

## Detail

Over-privileged identities (e.g. granting `AdministratorAccess` or `*:*` to an application role) turn minor remote code execution vulnerabilities into full corporate account takeovers.

### Practical Enforcement Strategies

1. **Avoid Wildcards**: Do not use `*` in actions or resources where the service lets you scope them. Instead of `Action: s3:*`, specify `Action: ["s3:GetObject", "s3:PutObject"]`. (Some actions, such as many `List*`/`Describe*` calls, only support `Resource: "*"` - constrain those with conditions instead.)
2. **Scope to Explicit Resource ARNs**: Instead of `Resource: "*"`, restrict to `Resource: "arn:aws:s3:::my-company-invoice-bucket/*"`.
3. **Permission Boundaries & Service Control Policies (SCPs)**: Set hard guardrails - a permissions boundary caps what a delegated role can grant, and SCPs (plus resource control policies) cap what any principal in an account can do, whatever its own policies say.
4. **Conditions and Short-Lived Access**: Restrict by `aws:SourceVpce`, `aws:PrincipalOrgID`, tags (ABAC), or time; replace standing admin with just-in-time elevation (IAM Identity Center, Entra PIM) and give workloads role-based identity (instance roles, EKS Pod Identity, workload identity federation) instead of access keys.
5. **Access Analysis and Right-Sizing**: IAM Access Analyzer's unused-access findings, last-accessed data, and CloudTrail-based policy generation (Azure and GCP have equivalents such as the IAM recommender) show permissions granted but never used; review and prune them on a schedule. Full automation is risky - rarely used but essential permissions (disaster recovery, quarterly jobs) look unused too.

## Example

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadWriteInvoicesOnly",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::my-company-invoice-bucket/invoices/*",
      "Condition": {
        "StringEquals": { "aws:PrincipalOrgID": "o-exampleorgid" },
        "Bool": { "aws:SecureTransport": "true" }
      }
    }
  ]
}
```

```bash
# Find what is granted but unused, then generate a policy from observed activity
aws accessanalyzer list-findings-v2 --analyzer-arn "$UNUSED_ACCESS_ANALYZER_ARN" \
  --filter '{"findingType": {"eq": ["UnusedPermission"]}}'
aws iam generate-service-last-accessed-details --arn arn:aws:iam::123456789012:role/invoice-api
```

## Interview tips

- Define it with both dimensions: minimum **permissions** and minimum **duration** - standing access is itself excess privilege.
- Show the layered enforcement model: identity policies grant, while permissions boundaries, SCPs/RCPs, and resource policies cap; an explicit deny anywhere wins.
- Explain how you get there in practice: start from a generated or observed policy, scope resources and add conditions, then use unused-access findings to prune - least privilege is iterative, not a one-time design.
- Prefer roles and federation over users and keys: SSO with just-in-time elevation for people, and workload identity for services, so there are no long-lived credentials to over-scope.
- Name the trade-off: overly tight policies break deployments and slow teams, so provide well-scoped templates and a fast request path rather than letting teams fall back to `*`.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DAST (Dynamic Application Security Testing) and how is OWASP ZAP integrated into CI/CD pipelines?]] (`#709`): [What is DAST (Dynamic Application Security Testing) and how is OWASP ZAP integrated into CI/CD pipelines?](../devsecops/what-is-dast-dynamic-application-security-testing-and-how-is-owasp-zap-integrated-into-ci-cd-pipelines.md)
- [[What are Threat Modeling frameworks (STRIDE, PASTA) and how do they embed security into early sprint design?]] (`#710`): [What are Threat Modeling frameworks (STRIDE, PASTA) and how do they embed security into early sprint design?](../devsecops/what-are-threat-modeling-frameworks-stride-pasta-and-how-do-they-embed-security-into-early-sprint-design.md)
- [[What are Web Application Firewalls (WAF) and how do they mitigate OWASP Top 10 vulnerabilities?]] (`#669`): [What are Web Application Firewalls (WAF) and how do they mitigate OWASP Top 10 vulnerabilities?](../network-security/what-are-web-application-firewalls-waf-and-how-do-they-mitigate-owasp-top-10-vulnerabilities.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Security and Compliance](./README.md) · [All topics](../README.md)
