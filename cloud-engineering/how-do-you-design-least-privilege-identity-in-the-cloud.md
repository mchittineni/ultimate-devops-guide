---
title: "How do you design least-privilege identity in the cloud?"
id: 217
category: "Cloud Engineering"
difficulty: "Advanced"
tags:
  - devops
  - cloud-engineering
  - interview-questions
---

# How do you design least-privilege identity in the cloud?

**Short answer:** Eliminate long-lived credentials (SSO federation for humans, workload identity federation for machines), grant to groups and roles rather than individuals, scope permissions to the smallest resource boundary that works, make privileged access time-bound and approved, and derive the actual permission set from observed usage rather than from guesswork.

## Detail

**Humans and workloads need different mechanisms.** Humans: identity provider SSO, group-driven role assignment, MFA and device compliance, short-lived sessions, and just-in-time elevation for privileged roles. Workloads: platform-issued identities (instance roles, managed identities, attached service accounts) inside the cloud, and OIDC-based workload identity federation for CI or other clouds. Any long-lived access key is an exception that needs a named owner and an expiry.

**Least privilege is derived, not designed.** Start from a broad-but-bounded role in a non-production environment, capture what the workload actually calls from audit logs over a few weeks, then generate a tight policy from that data - AWS IAM Access Analyzer policy generation, GCP IAM Recommender, and Azure's least-privilege recommendations all do this. Hand-written least privilege is either too tight (breaks at 3am) or, more often, quietly too broad.

**Guardrails above grants.** Organisation-level deny rules (SCPs, Azure Policy deny, GCP org policy and IAM Deny) cap what any grant can achieve, including for administrators. This two-layer model - a permissive-enough grant inside a hard boundary - is more robust than trying to make every individual policy perfect.

**Break-glass access, designed deliberately.** A small number of highly privileged emergency identities, with credentials split and stored offline, MFA, alerting on every use, and a documented review after each use. The failure mode to avoid is the opposite extremes: no break-glass path (so someone weakens the guardrails during an incident) or an unmonitored one.

**Attribute-based access scales better than role explosion.** Tag/label resources with team and environment, and write conditions that compare the principal's attributes to the resource's (`aws:PrincipalTag/team` = `aws:ResourceTag/team`). One policy then serves many teams, instead of one role per team per environment.

**Review continuously, and prove it.** Quarterly access reviews driven by the identity provider, automatic removal on role change and departure, last-used data to retire unused permissions and identities, and alerting on the creation of new long-lived keys, on `iam:*` policy changes, and on root/global-admin use. Auditors want evidence of the review, so make the process produce artefacts.

**The multi-cloud version.** Federate all clouds to one identity provider so joiner/mover/leaver is a single process, and keep per-cloud authorisation native - trying to abstract IAM across providers into one model loses fidelity and creates a second system to secure.

## Example

```text
Access model that survives an audit

Humans
  IdP groups            eng-payments · eng-payments-oncall · platform-admins
  Standing access       read-only in prod, write in dev/staging
  Elevation             PIM / IAM condition with expiry -> write in prod for 4 h,
                        justification + approval + alert to #security
  Session               8 h max, MFA + compliant device required

Workloads
  In-cloud              attached role / managed identity / service account
  CI/CD                 OIDC federation, subject pinned to repo AND branch
  Long-lived keys       denied by org policy; exceptions registered with expiry

Boundaries
  Preventive            org-level deny: regions, public data stores, key creation,
                        disabling audit logs
  Detective             alert on new key, on policy change, on break-glass use

Derivation
  Every role's policy generated from 30-90 days of audit-log usage, reviewed quarterly
```

## Interview tips

- Lead with removing long-lived credentials - it is the change with the largest real-world effect.
- "Derive the policy from audit logs" is the answer that separates practitioners from policy theorists.
- Expect: "what about emergencies?" - a designed, alerted, reviewed break-glass path, not weakening the guardrails.

---

[⬅ Back to Cloud Engineering](./README.md) · [All topics](../README.md)
