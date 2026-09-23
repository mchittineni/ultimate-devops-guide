---
title: "What is Database Schema Migration as Code and how do tools like Flyway and Liquibase automate rollouts?"
id: 661
category: "Database Management in DevOps"
difficulty: "Beginner"
tags:
  - devops
  - database-management-in-devops
  - interview-questions
  - databases
  - migrations
  - flyway
  - liquibase
  - cicd
quiz:
  stem: "What action does Flyway take if a developer modifies the contents of an old migration file (e.g. `V1__init.sql`) that has already been applied to the production database?"
  options:
    - "It drops all database tables automatically"
    - "It fails the deployment immediately due to a checksum mismatch in `flyway_schema_history`"
    - "It silently ignores the modification and continues"
    - "It converts the database into SQLite"
  answer: 2
  explanation: "Flyway stores a checksum of every applied migration script. If a historical script is altered, Flyway detects a checksum mismatch and halts to prevent schema corruption."
---

# What is Database Schema Migration as Code and how do tools like Flyway and Liquibase automate rollouts?

**Short answer:** Schema Migration as Code treats database DDL changes as versioned, immutable SQL scripts committed to Git; tools like Flyway track executed migrations via a schema version table (`flyway_schema_history`) and automatically apply new migrations sequentially during CI/CD.

## Detail

Manual schema changes - someone running ad-hoc `ALTER TABLE` statements from a GUI - cause drift between environments, forgotten steps, and releases that work in staging but fail in production. Migration as code makes every schema change a versioned, reviewed file that the pipeline applies identically everywhere.

### How Flyway works

1. Migrations are files with strict version prefixes, applied in order:
   - `V1__create_users_table.sql`
   - `V2__add_email_index.sql`
   - `V3__add_phone_number_column.sql`
   - `R__refresh_views.sql` - a _repeatable_ migration, re-applied whenever its checksum changes.
2. Flyway creates a history table in the target database, `flyway_schema_history`, recording each applied version, its checksum (a CRC32 of the file), who ran it, when, and whether it succeeded.
3. On `migrate`, it compares the files on disk with the history table and runs only the pending ones, in version order. Each migration runs in its own transaction where the database supports transactional DDL (PostgreSQL, SQL Server); on MySQL, DDL auto-commits, so a failed migration can leave a partial change that must be fixed by hand.
4. On `validate` (run by default before `migrate`), if an already-applied file has changed, Flyway reports a **checksum mismatch** and stops. The fix is a new migration, never an edit; `flyway repair` exists to realign the history table after a deliberate, reviewed correction.

### How Liquibase differs

Liquibase organises changes as **changesets** (identified by `id` + `author` + file) in a changelog written in SQL, XML, YAML, or JSON. It records them in `DATABASECHANGELOG`, takes a lock in `DATABASECHANGELOGLOCK` so two runners cannot apply changes concurrently, and supports preconditions, contexts/labels for environment-specific changes, and declared rollbacks. Its abstract change types (`addColumn`, `createIndex`) can target multiple database engines. Note that Liquibase Community 5.0 moved to the source-available Functional Source License.

### In the pipeline

- Run `validate` in CI against an ephemeral database, and ideally lint migrations for dangerous operations.
- Apply migrations as a **separate, gated step before** the application rollout (a pipeline stage or Kubernetes Job), not from application startup across many replicas.
- Keep every migration backward compatible with the running version of the code, using expand/contract for breaking changes.

**Limitations.** A migration tool tracks _what_ ran, not _whether it is safe_: it will happily run a statement that locks a 500 GB table. Down migrations are optional and often untested, so many teams treat migrations as forward-only and fix mistakes with a new migration.

## Example

```bash
# CI: fail fast on edited or misnamed migrations, then apply to a disposable database.
flyway -url="jdbc:postgresql://localhost:5432/ci" -user=ci -password="$CI_DB_PASSWORD" \
  -locations=filesystem:db/migration validate migrate info

# What an edited, already-applied file looks like:
# ERROR: Validate failed: Migrations have failed validation
# Migration checksum mismatch for migration version 1
# -> Applied to database : 1432098215
# -> Resolved locally    : -1911431077
```

```yaml
# Liquibase: the same idea as a YAML changelog with an explicit rollback.
databaseChangeLog:
  - changeSet:
      id: 3-add-phone-number
      author: platform-team
      changes:
        - addColumn:
            tableName: users
            columns:
              - column: { name: phone_number, type: varchar(20) }
      rollback:
        - dropColumn: { tableName: users, columnName: phone_number }
```

## Interview tips

- Describe the mechanism: versioned files, a history table in the target database, pending migrations applied in order.
- Explain the checksum check and the rule it enforces - never edit an applied migration, add a new one.
- Know the transactional-DDL difference: PostgreSQL rolls back a failed migration, MySQL can leave it half-applied.
- Contrast Flyway (plain SQL, simple) with Liquibase (changesets, preconditions, rollbacks, multi-engine), and mention the Liquibase licence change.
- Say migrations run as a gated step before rollout and must stay backward compatible with the running code.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#511`): [What is the difference between Continuous Delivery and Continuous Deployment?](../core-devops-concepts/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Database Management in DevOps](./README.md) · [All topics](../README.md)
