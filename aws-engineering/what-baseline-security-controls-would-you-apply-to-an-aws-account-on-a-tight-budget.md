---
title: "What baseline security controls would you apply to an AWS account on a tight budget?"
id: 796
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - aws-engineering
  - security
  - iam
  - guardrails
quiz:
  stem: "A cost-conscious customer says they cannot afford Shield or WAF. Which statement about their baseline is accurate?"
  options:
    - "Without paying for Shield Advanced they have no DDoS protection at all"
    - "Shield Standard is already applied to every account at no extra cost, and most of the highest-value baseline controls (root MFA, Block Public Access, default EBS encryption, IMDSv2, SCPs) are free settings"
    - "Security groups and network ACLs alone are a sufficient security baseline"
    - "CloudTrail must be bought as an add-on before any API activity is recorded"
  answer: 2
  explanation: "Shield Standard protects every AWS customer automatically. The cheapest, highest-return controls are account settings and identity hygiene, not paid services; network rules matter but cover only one of several layers. CloudTrail event history records management events for 90 days at no cost."
---

# What baseline security controls would you apply to an AWS account on a tight budget?

**Short answer:** Most of the baseline is free settings, not paid products. Lock down the **root user** (MFA, no access keys), move people to **IAM Identity Center** with least-privilege permission sets and workloads to **roles** with no long-lived keys, turn on account-wide **S3 Block Public Access**, **default EBS encryption** and **IMDSv2 by default**, keep a **CloudTrail** trail to a locked-down bucket, restrict network exposure with tight **security groups** and SSM Session Manager instead of open SSH, and enforce it all with **SCPs** and Terraform-only changes. Then spend the small budget where detection pays most: **GuardDuty**, **IAM Access Analyzer** and budget alerts. Shield Standard is already on for everyone.

## Detail

A good answer is organised by layer, because security groups and NACLs alone cover only the network - and most real AWS breaches start with identity (leaked keys, over-broad roles) or data exposure (public buckets, snapshots), not an open port.

### 1. Identity - free and the highest return

- **Root user**: hardware or passkey MFA, no access keys, used only for the handful of tasks that need it. In an AWS Organization, centrally managed root access lets you remove root credentials from member accounts altogether.
- **People**: IAM Identity Center with permission sets per job function, short-lived credentials, MFA, and no IAM users for humans.
- **Workloads**: instance profiles, EKS Pod Identity or IRSA, and **OIDC federation** for CI (GitHub Actions, GitLab) so no access keys live in pipeline secrets.
- **Least privilege**: start from AWS managed job-function policies if you must, then tighten using IAM Access Analyzer's policy generation from CloudTrail activity.

### 2. Account-wide defaults - one command each

- **S3 Block Public Access** at the account level (new buckets already block public access by default, but the account setting also covers existing buckets).
- **Default EBS encryption** per region, so no unencrypted volume or snapshot can be created by accident. S3 already encrypts new objects with SSE-S3 by default.
- **IMDSv2 required** as the account default for new instances, which blocks the classic SSRF-to-credentials path.
- **Block public sharing** of EBS snapshots and AMIs (account-level settings).

### 3. Network - small, precise, and no inbound admin ports

- Security groups referencing other security groups, not CIDR ranges, and never `0.0.0.0/0` on SSH, RDP or database ports.
- **SSM Session Manager** (no inbound port, every session logged) instead of a bastion with port 22 open.
- Workloads in private subnets behind a load balancer; gateway endpoints for S3 and DynamoDB are free and remove internet paths.
- **NACLs** are stateless and coarse: useful as a subnet-level backstop (for example to block a known-bad range), not as the main control, and a frequent source of broken return traffic.

### 4. Logging and detection - where the money goes

- **CloudTrail**: event history shows 90 days of management events for free; create one multi-region (ideally organisation-wide) trail to a separate, versioned, access-restricted bucket for durable evidence. The first copy of management events in a trail is not charged; you pay for S3 storage.
- **GuardDuty**: paid, but priced on usage and usually small for a modest account, with a free trial to size it. It is the single best value detective control.
- **IAM Access Analyzer** external-access findings are free and flag buckets, roles and keys shared outside the account.
- **Trusted Advisor** core security checks are free on every support plan.
- **AWS Budgets** alerts catch both waste and the classic sign of compromise - a crypto-mining bill spike.
- Add **AWS Config** and **Security Hub** when the budget allows; both charge per evaluation or check, so scope them to what you will actually act on.

### 5. Guardrails and change control

- **SCPs** (free with AWS Organizations): deny leaving the organisation, deny disabling CloudTrail or GuardDuty, deny regions you do not use, deny creating IAM users with access keys.
- All changes through **Terraform** in a reviewed pipeline, with console access read-only for most people. That turns drift and manual mistakes into code review.

**On the "can't afford Shield or WAF" premise.** Shield Standard protects every account at no cost against common network and transport-layer attacks. WAF is priced per web ACL, rule and request, so a small ruleset on one load balancer is often cheaper than people assume - worth costing before ruling it out.

## Example

```bash
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)

# Root user: MFA on, no access keys? (both should print 1 and 0)
aws iam get-account-summary --query 'SummaryMap.[AccountMFAEnabled,AccountAccessKeysPresent]'

# Account-wide defaults (EBS encryption and IMDS defaults are per region)
aws s3control put-public-access-block --account-id "$ACCOUNT" \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
aws ec2 enable-ebs-encryption-by-default
aws ec2 modify-instance-metadata-defaults --http-tokens required --http-put-response-hop-limit 2
aws ec2 enable-snapshot-block-public-access --state block-all-sharing

# Cheap detection
aws guardduty create-detector --enable
aws accessanalyzer create-analyzer --analyzer-name account-external --type ACCOUNT
```

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ProtectAuditTrail",
      "Effect": "Deny",
      "Action": ["cloudtrail:StopLogging", "cloudtrail:DeleteTrail", "guardduty:DeleteDetector", "organizations:LeaveOrganization"],
      "Resource": "*"
    },
    {
      "Sid": "NoLongLivedKeys",
      "Effect": "Deny",
      "Action": "iam:CreateAccessKey",
      "Resource": "*"
    }
  ]
}
```

## Interview tips

- Structure the answer by layer - identity, account defaults, network, detection, guardrails - and say why identity comes first.
- A common answer is "least-privilege security groups, NACLs, IAM policies and Terraform-only changes". That is a good start but misses root protection, long-lived keys, public data exposure, logging and detection; name those gaps yourself.
- Correct the premise politely: Shield Standard is free and automatic, and WAF is cheaper than many assume.
- Expect follow-ups: "How do CI pipelines authenticate without keys?" (OIDC to an IAM role), "How do you get into a private instance?" (Session Manager), "What would you buy first with a small budget?" (GuardDuty).
- Be honest about NACLs: stateless, so return traffic on ephemeral ports must be allowed, and they rarely add much over well-designed security groups. See [security groups versus network ACLs](./what-is-the-difference-between-a-security-group-and-a-network-acl.md), [authenticating to AWS without long-lived access keys](./how-do-you-authenticate-to-aws-without-long-lived-access-keys.md), and [permission boundaries and SCPs](./how-do-you-implement-aws-iam-permission-boundaries-and-service-control-policies-scps.md).

**Telling it as a STAR story** (an adaptable example)

- **Situation:** A small product company ran everything in one AWS account with shared IAM users, SSH open to the internet, and no security budget beyond "a few hundred dollars a month".
- **Task:** Raise the baseline quickly without buying premium security services.
- **Action:** Locked down root with MFA and removed its keys, moved engineers to IAM Identity Center permission sets and CI to OIDC roles, deleted the IAM users' keys, and replaced port 22 with Session Manager. Applied account-wide Block Public Access, default EBS encryption and IMDSv2 through Terraform, added an organisation CloudTrail and SCPs protecting it, and enabled GuardDuty and Access Analyzer with findings routed to the team channel.
- **Result:** The account had no long-lived human credentials and no inbound admin ports within a month, and the detection layer cost a small fraction of the budget; the first GuardDuty finding caught a leaked test credential being used from an unknown network.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does Cloud IAM Role Federation differ from static Service Account keys?]] (`#546`): [How does Cloud IAM Role Federation differ from static Service Account keys?](../cloud-platforms/how-does-cloud-iam-role-federation-differ-from-static-service-account-keys.md)
- [[How does the Cloud Shared Responsibility Model divide security obligations between IaaS, PaaS, and SaaS?]] (`#543`): [How does the Cloud Shared Responsibility Model divide security obligations between IaaS, PaaS, and SaaS?](../cloud-platforms/how-does-the-cloud-shared-responsibility-model-divide-security-obligations-between-iaas-paas-and-saas.md)
- [[What Kubernetes production best practices do you follow for reliability, security, and cost?]] (`#790`): [What Kubernetes production best practices do you follow for reliability, security, and cost?](../kubernetes/what-kubernetes-production-best-practices-do-you-follow-for-reliability-security-and-cost.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
