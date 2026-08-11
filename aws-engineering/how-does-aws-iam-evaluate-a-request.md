---
title: "How does AWS IAM evaluate a request?"
id: 192
category: "AWS Engineering"
difficulty: "Advanced"
tags:
  - devops
  - aws-engineering
  - interview-questions
---

# How does AWS IAM evaluate a request?

**Short answer:** Deny by default; an explicit `Deny` anywhere wins; otherwise the request needs an `Allow` and must survive every applicable boundary - Organizations SCPs, the identity policy, any resource policy, permission boundaries, and session policies. Cross-account access is the special case: it requires an `Allow` on both sides.

## Detail

**Evaluation order, simplified but accurate enough to explain:**

1. Collect all applicable policies: SCPs (and resource control policies), identity-based policies, resource-based policies, permission boundaries, session policies.
2. If any explicit `Deny` matches - decision is deny, immediately.
3. SCPs must allow the action (they only filter; they never grant).
4. Then an `Allow` must exist in an identity policy or a resource policy. Permission boundaries and session policies act as intersections: they cap what the identity policy can grant.
5. Otherwise: implicit deny.

**The mental model is intersection, not union.** Adding a policy can only ever grant within what the surrounding boundaries already permit. This is why an administrator with `AdministratorAccess` still cannot act if an SCP denies the action - a fact that surprises people during incidents.

**Cross-account needs both sides.** For account B's role to read a bucket in account A, account A's bucket policy must allow the principal _and_ account B's identity policy must allow the action. One side alone is insufficient. This symmetry is the most commonly missed detail in interviews.

**Roles over users, always.** Human access via identity-centre federation with short-lived sessions; workload access via instance profiles, EKS IAM Roles for Service Accounts (or EKS Pod Identity), or OIDC federation from CI. Long-lived access keys are the root cause of a large share of cloud incidents; if one must exist, scope it narrowly and rotate it automatically.

**Conditions are where real least privilege lives.** `aws:PrincipalOrgID` to keep resources internal, `aws:SourceIp` or `aws:SourceVpce` for network constraints, `aws:RequestTag`/`aws:ResourceTag` for tag-based access control, `sts:ExternalId` for third-party roles, and `aws:PrincipalTag` for attribute-based access. Wildcard actions with no conditions are what audits flag first.

**Verify, do not assume.** The IAM policy simulator, `aws iam get-context-keys-for-custom-policy`, Access Analyzer (which flags resources reachable from outside the org and generates least-privilege policies from CloudTrail), and last-accessed data are the tools that turn policy debates into evidence.

## Example

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadOnlyOwnTeamData",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": ["arn:aws:s3:::acme-data", "arn:aws:s3:::acme-data/*"],
      "Condition": {
        "StringEquals": { "s3:ExistingObjectTag/team": "${aws:PrincipalTag/team}" }
      }
    },
    {
      "Sid": "DenyOutsideOrgAndUnencrypted",
      "Effect": "Deny",
      "Action": "s3:*",
      "Resource": "arn:aws:s3:::acme-data/*",
      "Condition": {
        "StringNotEquals": { "aws:PrincipalOrgID": "o-abc123" },
        "Bool": { "aws:SecureTransport": "false" }
      }
    }
  ]
}
```

## Interview tips

- "Explicit deny wins, SCPs filter but never grant, cross-account needs both sides" covers most of what is being probed.
- Describe boundaries as an intersection - it explains permission boundaries and session policies in one sentence.
- Expect: "how would you prove this role is least privilege?" - Access Analyzer policy generation from CloudTrail, plus last-accessed data.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?]] (`#407`): [How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-waiting-for-a-persistentvolumeclaim.md)
- [[How does networking differ across AWS, Azure, and GCP?]] (`#282`): [How does networking differ across AWS, Azure, and GCP?](../cloud-platforms/how-does-networking-differ-across-aws-azure-and-gcp.md)
- [[What is a cloud landing zone?]] (`#215`): [What is a cloud landing zone?](../cloud-engineering/what-is-a-cloud-landing-zone.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
