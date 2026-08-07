---
title: "How do you structure a multi-account AWS organisation?"
id: 197
category: "AWS Engineering"
difficulty: "Advanced"
tags:
  - devops
  - aws-engineering
  - interview-questions
---

# How do you structure a multi-account AWS organisation?

**Short answer:** Accounts are the strongest isolation boundary AWS offers, so use one per workload per environment, grouped into organisational units by function, governed by Service Control Policies, with centralised logging, security tooling, and identity in dedicated accounts. Control Tower (or a Landing Zone built on Organizations) provisions and enforces this consistently.

## Detail

**Why accounts, not just VPCs or tags.** An account is a separate blast radius for IAM, service quotas, and billing. A compromised credential, a runaway Lambda, or a quota exhaustion in staging cannot reach production if they are separate accounts. Tags and VPCs do not give you any of those boundaries.

**A conventional OU layout:**

| OU             | Contains                                                                     |
| -------------- | ---------------------------------------------------------------------------- |
| Security       | log archive, audit/security tooling, incident response                       |
| Infrastructure | shared networking (Transit Gateway), shared CI, shared registries            |
| Workloads      | nested per-environment OUs: prod, staging, dev — one account per app per env |
| Sandbox        | time-limited experimentation accounts with hard budget caps                  |
| Suspended      | quarantine OU with a deny-all SCP for compromised accounts                   |

The management (payer) account holds nothing but Organizations, billing, and the automation that provisions accounts — no workloads, tightly restricted access.

**SCPs are guardrails, not permissions.** They filter what any principal in the account may do, including administrators. Typical set: deny leaving the organisation, deny disabling CloudTrail/GuardDuty/Config, deny unapproved regions, deny root user actions, deny deletion of security-tooling roles. Keep them broad and stable — SCPs debugged during an incident are painful because the error messages are indirect.

**Centralise what must be tamper-proof and auditable:** an organisation CloudTrail delivering to an S3 bucket in the log-archive account (which no workload account can write to or delete from), Config aggregation, GuardDuty and Security Hub delegated administration, and a central Access Analyzer. Attackers with account-level admin should still be unable to erase the evidence.

**Networking has two viable shapes.** Centralised: a shared-services VPC with Transit Gateway attachments and inspection egress, which suits regulated environments. Decentralised: per-account VPCs with only the connectivity they need (private endpoints, PrivateLink) and no shared transit, which suits independent teams. Choose based on whether traffic inspection is mandatory.

**Provisioning must be automated.** Account Factory (Control Tower) or Terraform/CDK pipelines that create the account, baseline it (IAM roles, guardrails, logging, budgets, tagging), and register it in the service catalogue. Manually created accounts drift, escape the baseline, and are how organisations end up with untracked spend and unmonitored regions.

**Cost.** Consolidated billing gives volume discounts and lets Reserved Instances and Savings Plans be shared across accounts, while cost allocation tags plus per-account attribution make spend accountable to teams. Budgets and anomaly detection belong in the baseline, not added later.

## Example

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyRegionsOutsideApproved",
      "Effect": "Deny",
      "NotAction": ["iam:*", "sts:*", "organizations:*", "cloudfront:*", "route53:*", "support:*"],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": { "aws:RequestedRegion": ["eu-west-1", "eu-central-1"] }
      }
    },
    {
      "Sid": "ProtectSecurityBaseline",
      "Effect": "Deny",
      "Action": [
        "cloudtrail:StopLogging",
        "cloudtrail:DeleteTrail",
        "guardduty:DeleteDetector",
        "config:DeleteConfigurationRecorder"
      ],
      "Resource": "*"
    },
    {
      "Sid": "DenyLeavingOrg",
      "Effect": "Deny",
      "Action": ["organizations:LeaveOrganization"],
      "Resource": "*"
    }
  ]
}
```

## Interview tips

- Lead with "the account is the blast-radius boundary" — it justifies everything else.
- Naming the log-archive account that workload accounts cannot write to shows you think about an attacker with admin.
- Expect: "how do you stop an engineer spinning up GPUs in an unapproved region?" — a region-deny SCP plus budgets in the account baseline.

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
