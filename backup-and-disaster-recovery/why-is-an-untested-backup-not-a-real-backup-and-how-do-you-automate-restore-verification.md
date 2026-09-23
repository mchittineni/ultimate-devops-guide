---
title: "Why is an untested backup not a real backup and how do you automate restore verification?"
id: 599
category: "Backup and Disaster Recovery"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - backup-and-disaster-recovery
  - backup
  - testing
  - automation
  - disaster-recovery
quiz:
  stem: "Why do mature engineering teams run automated daily restore pipelines into sandbox environments instead of relying on backup success logs?"
  options:
    - "Cloud providers require daily restores to maintain snapshot licenses"
    - "To prove that backup images can actually boot, decrypt, and serve application queries without discovering silent corruption during a real disaster"
    - "Because snapshots are deleted automatically if not restored within 24 hours"
    - "To accelerate database write throughput"
  answer: 2
  explanation: "A successful backup log only proves data was written to disk. Automated restore testing guarantees that snapshots can be decrypted, mounted, and queried successfully."
---

# Why is an untested backup not a real backup and how do you automate restore verification?

**Short answer:** Backups frequently fail during real disasters due to silent corruption, missing decryption keys, or unrecorded schema dependencies; automated restore verification periodically spins up ephemeral infrastructure from backups, executes synthetic queries, and destroys the test environment.

## Detail

The classic DevOps axiom: **Nobody cares about backups; people only care about restores.**

### Common Reasons Restores Fail

1. **Silent Snapshot Corruption**: Cloud snapshot API reported success, but the underlying disk blocks are unreadable.
2. **Missing Encryption Keys**: The backup is encrypted with a KMS key that was disabled, scheduled for deletion, or never shared with the recovery account. (Automatic KMS key rotation is not the problem - old key material is retained - but a deleted key makes every backup encrypted with it unrecoverable.)
3. **Application Incompatibility**: The restored database lacks required external secrets, networking routes, or compatible extensions.

### Automated Restore Testing Pipeline

```text
Cron Trigger -> Provision Ephemeral Sandbox DB -> Restore Latest Snapshot -> Run Synthetic Health Queries -> Emit Metric -> Destroy Sandbox
```

- A daily CI/CD pipeline triggers an automated restore into an isolated sandbox VPC.
- The pipeline connects to the restored database, checks record counts, executes basic CRUD tests, and confirms data integrity.
- If the restore succeeds, it emits a heartbeat metric (`backup_restore_verified{status="ok"}`).
- If it fails, on-call engineers are paged immediately before an actual production disaster strikes.

## Example

AWS Backup has restore testing built in: a plan that restores the latest recovery point on a schedule, then deletes it.

```bash
aws backup create-restore-testing-plan --restore-testing-plan '{
  "RestoreTestingPlanName": "nightly_rds_restore",
  "ScheduleExpression": "cron(0 3 * * ? *)",
  "RecoveryPointSelection": {
    "Algorithm": "LATEST_WITHIN_WINDOW",
    "RecoveryPointTypes": ["SNAPSHOT"],
    "IncludeVaults": ["*"],
    "SelectionWindowDays": 1
  }
}'
# Then attach a selection (create-restore-testing-selection) for the RDS resources,
# and add a validation Lambda that runs your SQL assertions against the restored copy.
```

## Interview tips

- 'Nobody wants backups; they want restores.'
- Silent failures: deleted or unshared KMS keys, corrupted WALs, unmountable filesystems.
- Automated ephemeral restore verification in CI/CD sandbox environments.
- Synthetic database assertions to verify data integrity.
- Record restore duration as your measured RTO and the newest row's timestamp as your measured RPO.
- Trade-off: full nightly restores of multi-terabyte databases cost real money and time, so rotate which systems get a full restore and run cheaper integrity checks on the rest.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Shift-Left and how is it practically implemented across the SDLC?]] (`#510`): [What is Shift-Left and how is it practically implemented across the SDLC?](../core-devops-concepts/what-is-shift-left-and-how-is-it-practically-implemented-across-the-sdlc.md)
- [[How do you detect, isolate, and eradicate flaky tests in a CI/CD pipeline?]] (`#536`): [How do you detect, isolate, and eradicate flaky tests in a CI/CD pipeline?](../cicd/how-do-you-detect-isolate-and-eradicate-flaky-tests-in-a-ci-cd-pipeline.md)
- [[What is Semantic Release and how does it automate versioning and changelogs from commits?]] (`#540`): [What is Semantic Release and how does it automate versioning and changelogs from commits?](../cicd/what-is-semantic-release-and-how-does-it-automate-versioning-and-changelogs-from-commits.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Backup and Disaster Recovery](./README.md) · [All topics](../README.md)
