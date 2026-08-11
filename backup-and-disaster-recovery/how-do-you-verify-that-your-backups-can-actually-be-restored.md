---
title: "How do you verify that your backups can actually be restored?"
id: 436
category: "Backup and Disaster Recovery"
difficulty: "Intermediate"
tags:
  - devops
  - backup-and-disaster-recovery
  - interview-questions
  - database-management-in-devops
  - site-reliability-engineering
  - scripting-and-automation
---

# How do you verify that your backups can actually be restored?

**Short answer:** Automate the restore, not just the backup. On a schedule, spin up a clean, isolated environment, **restore from the actual backup artefact**, and then run assertions that prove the data is usable: row counts and checksums against expected ranges, referential-integrity checks, the newest record's timestamp (which measures your real RPO), and an application-level smoke test against the restored copy. Record the **restore duration** because that is your real RTO, not the number in the plan. Destroy the environment afterwards, and alert on a failed or skipped verification exactly as you would on a failed backup. The principle to state plainly: a backup that has never been restored is not a backup, it is a hopeful file - and "the backup job reported success" is a statement about the job, not about the data.

## Restoring from the backup artefact matters

The commonest way this goes wrong is testing the wrong thing:

- A **snapshot that exists** but was taken while the database was mid-write and is not crash-consistent.
- A **backup of an empty or partially-populated volume** - the job succeeded, the data was elsewhere.
- **Encrypted backups whose key is unavailable** in the recovery scenario (the key lived only in the account you lost, or the KMS grant was never made cross-account).
- **Logically valid, semantically empty** - the dump has tables and no rows, because the export ran against a replica that had been reset.
- **Restorable but too slow**: 30 hours to rehydrate 8 TB from cold storage, against a 4-hour RTO. That is a failed backup even though it works.
- **Application-incompatible**: the schema in the backup predates a migration and the current code cannot read it.

Only an end-to-end restore that ends with the application working catches all of these.

## Detail

### The automated verification loop

1. **Provision an isolated environment** from Infrastructure as Code - a separate account or project, no route to production, no production credentials. Isolation matters both to prevent accidents and because a restore test that can write to production is a bigger risk than the one it mitigates.
2. **Restore from the artefact you would use in a real incident** - the S3 object, the snapshot, the Velero backup - not from a live replica and not from a hand-made copy.
3. **Measure and record** the wall-clock time of each phase (locate, transfer, restore, recover, validate). This is where the honest RTO comes from.
4. **Assert on the data**, and make the assertions cheap enough to run every time:
   - Row counts per critical table within an expected range (not exact - the data moves).
   - Aggregate checksums or hashes over key columns for a sample of partitions.
   - The maximum timestamp in the newest table - this is your measured **RPO**.
   - Referential integrity and a few business invariants (no orders without a customer; balances sum correctly).
   - For files and object storage: object counts, total bytes, and checksums of a random sample.
5. **Run an application smoke test** against the restored data - start the application pointed at it, log in, load a record, run one read-heavy report. This is the step that catches schema and encoding problems.
6. **Publish the result** as a metric (`backup_verification_success`, `restore_duration_seconds`, `measured_rpo_seconds`) so it is on a dashboard and alertable, then **tear the environment down** so the test costs little.
7. **Alert on absence too.** A verification that silently stopped running looks identical to a passing one until the day you need it - so alert on staleness, not only on failure.

### Verification at different depths and cadences

| Cadence      | Depth                                                                                    | Purpose                                      |
| ------------ | ---------------------------------------------------------------------------------------- | -------------------------------------------- |
| Every backup | Job success, artefact exists, size within expected bounds, integrity check where offered | Catch the trivially broken                   |
| Nightly      | Automated restore of the most critical database to a scratch environment plus assertions | Prove restorability continuously             |
| Monthly      | Restore a full application stack; run smoke tests; record RTO                            | Prove the procedure and the timing           |
| Quarterly    | Full DR game day - unannounced-ish, real failover, humans following the runbook          | Prove people and dependencies, not just data |

The quarterly exercise is where the non-data failures surface: an out-of-date runbook, a DNS change nobody has permission to make, a licence bound to the old environment, a partner IP allow-list, an expired certificate, or a key that only one person can access. Data restores test technology; game days test the organisation. See [how do you execute a Disaster Recovery failover with minimal RTO and RPO](./how-do-you-execute-a-disaster-recovery-failover-with-minimal-rto-and-rpo.md).

### Backup properties that make verification meaningful

- **3-2-1 with immutability**: at least one copy off-site, and one immutable (object lock / retention lock) so ransomware or a compromised account cannot delete it. Test restoring **from the immutable copy**, since that is the one you will need in the worst case.
- **Cross-account, cross-region, and key access.** Verify that the recovery identity can read the backup and use the key. This is the single most common gap in an otherwise sound design.
- **Point-in-time recovery** for databases (continuous WAL/log archiving) rather than only nightly dumps - and verify a PITR to an arbitrary timestamp, not just the latest full backup, because the real scenario is "restore to 14:32, just before the bad migration".
- **Retention that matches the threat.** Silent corruption discovered six weeks later needs a backup older than six weeks, which changes your retention design.
- **Documented, tested runbooks** with the restore commands, and access that does not depend on one person.

See [what are backup best practices](./what-are-backup-best-practices.md) and [what is RPO and RTO](./what-is-rpo-and-rto.md).

## Example

```bash
#!/usr/bin/env bash
# Nightly restore verification. Runs in an isolated account, tears down, emits metrics.
set -Eeuo pipefail
START=$(date +%s)
STACK="verify-$(date +%Y%m%d)"
trap 'terraform -chdir=./verify destroy -auto-approve >/dev/null 2>&1 || true' EXIT

# 1. Isolated environment, no route to production
terraform -chdir=./verify apply -auto-approve -var "stack=$STACK"
HOST=$(terraform -chdir=./verify output -raw db_host)

# 2. Restore from the ARTEFACT - and from the immutable copy, which is the one that matters
LATEST=$(aws s3api list-objects-v2 --bucket acme-backups-locked --prefix prod/pg/ \
  --query 'sort_by(Contents,&LastModified)[-1].Key' --output text)
aws s3 cp "s3://acme-backups-locked/$LATEST" - | pg_restore -h "$HOST" -U postgres -d app --jobs=4
RESTORE_SECS=$(( $(date +%s) - START ))          # this is the real RTO, not the plan's number

# 3. Assertions: is the data USABLE, not merely present?
psql -h "$HOST" -U postgres -d app -v ON_ERROR_STOP=1 <<'SQL'
  -- row counts within an expected band (data moves; exact equality is a false alarm)
  DO $$ DECLARE n bigint; BEGIN
    SELECT count(*) INTO n FROM orders;
    IF n < 4000000 THEN RAISE EXCEPTION 'orders too few: %', n; END IF;
  END $$;
  -- referential integrity and a business invariant
  DO $$ DECLARE bad bigint; BEGIN
    SELECT count(*) INTO bad FROM orders o LEFT JOIN customers c ON c.id=o.customer_id
      WHERE c.id IS NULL;
    IF bad > 0 THEN RAISE EXCEPTION 'orphan orders: %', bad; END IF;
  END $$;
  -- MEASURED RPO: how stale is the newest data in this backup?
  SELECT 'measured_rpo_seconds=' || extract(epoch FROM now() - max(created_at))::int FROM orders;
SQL

# 4. Application-level smoke test - catches schema/encoding problems SQL checks miss
docker run --rm -e "DATABASE_URL=postgres://postgres@$HOST/app" \
  registry.example.com/app:current ./bin/smoke-test --read-only

# 5. Publish results so a SKIPPED run is as visible as a failed one
cat <<EOF | curl -s --data-binary @- "$PUSHGATEWAY/metrics/job/backup_verification"
backup_verification_success 1
restore_duration_seconds $RESTORE_SECS
EOF
```

```yaml
# Alert on failure AND on staleness - a verification that stopped running looks like success
groups:
  - name: backup-verification
    rules:
      - alert: BackupVerificationFailed
        expr: backup_verification_success == 0
        for: 5m
        labels: { severity: page }
        annotations: { runbook: "https://runbooks.example.com/backup-verify" }

      - alert: BackupVerificationStale
        expr: time() - push_time_seconds{job="backup_verification"} > 172800 # 48h
        labels: { severity: page }
        annotations:
          summary: "No backup restore has been verified for 48h - treat backups as unproven"

      - alert: RestoreTimeExceedsRTO
        expr: restore_duration_seconds > 14400 # documented RTO: 4 hours
        labels: { severity: ticket }
        annotations:
          summary: "Measured restore time now exceeds the committed RTO"
```

## Interview tips

- Say the line early: a backup that has never been restored is not a backup. Then add the sharper version - "the backup job succeeded" is a statement about the job, not the data.
- Insist on restoring **from the artefact**, in an isolated environment, on a schedule. Automation is what makes verification real; a manual annual test decays immediately.
- Give concrete assertions rather than "check it worked": row counts in a band, referential integrity, a business invariant, and the newest timestamp as a **measured RPO**. That last one is the detail that impresses.
- Emphasise that restore duration is your real RTO, and that a restore which works but takes 30 hours against a 4-hour RTO is a failed backup.
- The failure modes list is your credibility - crash-inconsistent snapshots, missing encryption keys in the recovery account, empty-but-valid dumps, schema older than the code. Pick two and be specific.
- Mention restoring from the **immutable** copy, and verifying that the recovery identity can read the backup and use the key cross-account. It is the most common real gap.
- Distinguish data verification from a DR game day: the former tests technology, the latter tests runbooks, permissions, DNS, and people. Interviewers want to hear you have done the second.
- Close on alerting for **staleness** as well as failure, because a verification job that quietly stopped is indistinguishable from a passing one until the day it matters. See [what is business continuity planning](./what-is-business-continuity-planning.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)
- [[How do you take a monthly release process to daily deployments?]] (`#285`): [How do you take a monthly release process to daily deployments?](../core-devops-concepts/how-do-you-take-a-monthly-release-process-to-daily-deployments.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Backup and Disaster Recovery](./README.md) · [All topics](../README.md)
