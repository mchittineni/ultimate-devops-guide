---
title: "How Do You Implement AWS IAM Permission Boundaries and Service Control Policies (SCPs)?"
id: 730
category: "AWS Engineering"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - aws-engineering
  - iam
  - scps
  - governance
quiz:
  stem: "How do Service Control Policies (SCPs) differ from IAM Identity-based policies in AWS Organizations?"
  options:
    - "SCPs grant permissions directly to users, whereas identity-based policies only apply to EC2 instances."
    - "SCPs define the maximum allowed permissions for entire accounts or OUs and do not grant permissions on their own, whereas identity-based policies grant specific permissions to principals."
    - "SCPs only apply to billing and invoice generation."
    - "Identity-based policies override explicit Deny statements in SCPs."
  answer: 2
  explanation: "SCPs act as organizational guardrails that set the outer limit of allowable permissions across accounts; they never grant permissions on their own and an identity policy is still required to perform actions."
---

# How Do You Implement AWS IAM Permission Boundaries and Service Control Policies (SCPs)?

**Short answer:** SCPs set the maximum permissible boundaries at the AWS Organization or OU level across entire accounts. Permission Boundaries delegate admin rights to developers safely by setting maximum permissions an IAM entity can grant to itself or others, preventing privilege escalation.

## Detail

### IAM Authorization Logic at Scale

In enterprise AWS deployments, granting developers the ability to create IAM roles and policies is necessary for CI/CD and serverless velocity, but risks privilege escalation (e.g., an engineer creating a role with `AdministratorAccess`).

AWS provides multi-layered guardrails: **Service Control Policies (SCPs)** and **IAM Permission Boundaries**.

### Service Control Policies (SCPs)

- Applied at the AWS Organizations Root, Organizational Unit (OU), or Account level.
- Act as **guardrails**: they define the maximum permissions that any principal (including the member account's `root` user) can exercise within an account. They do **not** apply to the management account or to service-linked roles.
- **Do not grant permissions**: an explicit identity-based policy is still required.
- Common use cases: preventing disabling of CloudTrail, blocking unapproved AWS regions, or enforcing that S3 buckets cannot be made public.
- **Resource control policies (RCPs)** are the resource-side counterpart: they cap what any principal - including ones outside your organization - can do to resources in your accounts (for example, S3 or KMS access only from your organization).

### IAM Permission Boundaries

- Applied directly to individual IAM users or roles.
- Defines the **maximum allowable permissions** that an identity-based policy can grant to that specific principal.
- **Privilege Escalation Prevention**: Allows delegating role creation to developers by enforcing a condition that any new role created by the developer must also have the Permission Boundary attached.

```text
       [AWS Organization Root]
                 │
           [SCP Boundary] ◄── Deny unapproved regions, protect CloudTrail
                 │
       [AWS Account Principal]
                 │
     [Permission Boundary] ◄── Maximum permissions developer role can hold
                 │
   [Identity-Based Policy] ◄── Actual permissions requested (e.g., S3, DynamoDB)
                 │
                 ▼
       EFFECTIVE PERMISSION = Intersection of (SCP ∩ Boundary ∩ Identity Policy)
```

### Delegation Pattern with Permission Boundaries

To safely allow developers to create IAM roles in Terraform:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:AttachRolePolicy"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "iam:PermissionsBoundary": "arn:aws:iam::123456789012:policy/DeveloperBoundary"
        }
      }
    }
  ]
}
```

If the developer attempts to create a role without attaching `DeveloperBoundary`, the request is denied. A complete delegation also denies `iam:DeleteRolePermissionsBoundary`, denies `iam:PutRolePermissionsBoundary` with any other policy, denies edits to the `DeveloperBoundary` policy itself (`iam:CreatePolicyVersion`, `iam:DeletePolicy`), and scopes `iam:PassRole` - otherwise the boundary can simply be removed or rewritten.

### Real-World Production Scenario

A platform engineering team wants developers to provision AWS Lambda execution roles via Terraform without opening tickets. They create a Permission Boundary restricting access to S3, DynamoDB, and CloudWatch Logs. Developers are granted `iam:CreateRole` only on the condition that their new roles attach this boundary. If a developer attempts to attach `AdministratorAccess`, the boundary clips the permissions automatically.

## Example

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyBoundaryRemovalOrSwap",
      "Effect": "Deny",
      "Action": ["iam:DeleteRolePermissionsBoundary", "iam:PutRolePermissionsBoundary"],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "iam:PermissionsBoundary": "arn:aws:iam::123456789012:policy/DeveloperBoundary"
        }
      }
    },
    {
      "Sid": "DenyEditingTheBoundaryItself",
      "Effect": "Deny",
      "Action": ["iam:CreatePolicyVersion", "iam:DeletePolicy", "iam:DeletePolicyVersion", "iam:SetDefaultPolicyVersion"],
      "Resource": "arn:aws:iam::123456789012:policy/DeveloperBoundary"
    }
  ]
}
```

```bash
# Verify the effective result instead of reasoning about it
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:role/dev-created-lambda-role \
  --action-names s3:GetObject iam:CreateUser \
  --query 'EvaluationResults[].[EvalActionName,EvalDecision]' --output table
```

## Interview tips

- Explain that effective permission is always the mathematical intersection of the SCP, Permission Boundary, and Identity-based policy.
- Highlight that SCPs affect even the root user of a member account (but not the management account or service-linked roles), whereas Permission Boundaries apply only to IAM users and roles.
- Explain how the delegation can be bypassed if you forget to deny removing or editing the boundary itself.
- Demonstrate how Permission Boundaries enable safe self-service IAM delegation.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does Cloud IAM Role Federation differ from static Service Account keys?]] (`#546`): [How does Cloud IAM Role Federation differ from static Service Account keys?](../cloud-platforms/how-does-cloud-iam-role-federation-differ-from-static-service-account-keys.md)
- [[What is Cloud Computing?]] (`#21`): [What is Cloud Computing?](../cloud-platforms/what-is-cloud-computing.md)
- [[What is AWS (Amazon Web Services)?]] (`#22`): [What is AWS (Amazon Web Services)?](../cloud-platforms/what-is-aws-amazon-web-services.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
