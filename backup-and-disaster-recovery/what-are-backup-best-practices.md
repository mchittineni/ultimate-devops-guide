---
title: "What are backup best practices?"
id: 65
category: "Backup and Disaster Recovery"
difficulty: "Beginner"
tags:
  - devops
  - backup-and-disaster-recovery
  - interview-questions
---

# What are backup best practices?

**Short answer:** Automate backups, follow 3-2-1-1-0, encrypt everything, keep an immutable copy in a separate account, monitor every job, and - above all - test restores on a schedule.

## Detail

**Coverage.** Inventory what actually needs backing up: databases, object storage, configuration and secrets, infrastructure code, CI/CD definitions, and SaaS data (source control, ticketing, identity). Cloud-managed does not mean backed up - the shared responsibility model puts your data on you.

**Automation and monitoring.** Backups run on a schedule with no human involvement, and every job reports success or failure to your monitoring system. Alert on _absence_ of a successful backup, not just on explicit failures - a job that never ran produces no error.

**The 3-2-1-1-0 rule.** Three copies, two media types, one off-site, one immutable/offline, zero restore errors.

**Security.** Encrypt in transit and at rest with keys you control. Store backups in a separate account or subscription with distinct credentials and MFA-protected delete. Enable object lock so backups cannot be deleted before their retention expires - this is the primary ransomware defence.

**Retention and cost.** Match retention to legal and business need (a common shape: 30 days daily, 12 months monthly, 7 years annual for regulated data), with lifecycle rules moving older sets to archival storage.

**Verification.** Checksums on write, periodic automated restore tests into an isolated environment, and a documented restore runbook with measured timings. Record how long the last real restore took - that number is your true RTO.

**Documentation.** Which systems, what schedule, where stored, who owns it, and the exact restore procedure. Keep it accessible when your primary systems are down.

## Example

```bash
# Immutable, encrypted, lifecycle-managed backup target
aws s3api put-object-lock-configuration --bucket acme-backups \
  --object-lock-configuration '{"ObjectLockEnabled":"Enabled",
    "Rule":{"DefaultRetention":{"Mode":"COMPLIANCE","Days":35}}}'

# Alert when no successful backup in 26 hours (Prometheus)
# time() - backup_last_success_timestamp_seconds > 26 * 3600
```

## Interview tips

- "Alert on the absence of success" is a subtle, senior point about monitoring backups.
- Immutability plus a separate account is the ransomware answer.
- Close on restore testing with a real number - it is the most credible thing you can say about backups.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Backup and Disaster Recovery](./README.md) · [All topics](../README.md)
