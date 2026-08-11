---
title: "What is Database DevOps?"
id: 111
category: "Database Management in DevOps"
difficulty: "Intermediate"
tags:
  - devops
  - database-management-in-devops
  - interview-questions
---

# What is Database DevOps?

**Short answer:** Database DevOps applies DevOps practices - version control, automated testing, continuous integration, and automated deployment - to database schemas and data, so database changes ship as safely and frequently as application changes.

## Detail

**The problem it solves.** Application code has been automated for years, but database changes often remained manual: a DBA running scripts during a change window. That makes the database the bottleneck and the riskiest part of every release.

**Core practices**

- **Schema as code.** Migration scripts live in the application repository, reviewed like any other change.
- **Migration tooling** - Flyway, Liquibase, Alembic, or a framework's built-in migrations - applies versioned, ordered, tracked changes and records what has run.
- **Automated testing** - migrations run against an ephemeral database in CI, seeded with production-shaped data, including a rollback test.
- **Continuous delivery** - migrations run automatically as part of deployment, not as a separate manual step.
- **Backward compatibility** - every migration must work with both the currently running application version and the new one, because they coexist during a rolling deploy.
- **Observability** - monitor migration duration, lock waits, and replication lag during rollout.

**The expand/contract pattern** is the central technique:

1. **Expand** - add the new column/table, nullable and additive only.
2. **Migrate** - deploy code that writes to both old and new, backfill existing rows in batches.
3. **Switch** - deploy code that reads from the new location.
4. **Contract** - after confidence, remove the old column and the dual-write code.

Each step is independently deployable and reversible. It takes several releases, and that is the point.

## Example

```sql
-- V12__add_email_verified.sql  (expand: additive, no lock, no default rewrite)
ALTER TABLE users ADD COLUMN email_verified boolean;
CREATE INDEX CONCURRENTLY idx_users_email_verified ON users (email_verified);
```

## Interview tips

- Expand/contract is the answer to "how do you change a schema with zero downtime?" - know all four steps.
- Mention that destructive changes (drop column, rename) are never done in the same release as the code change.
- Long-running locks on large tables are the practical danger; `CONCURRENTLY`, batched backfills, and lock timeouts are the mitigations.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Database Management in DevOps](./README.md) · [All topics](../README.md)
