---
title: "What is Database Version Control?"
id: 112
category: "Database Management in DevOps"
difficulty: "Intermediate"
tags:
  - devops
  - database-management-in-devops
  - interview-questions
---

# What is Database Version Control?

**Short answer:** Database version control means keeping schema definitions and change scripts in the same repository as the application, versioned and reviewed, so any environment can be built to a known schema version reproducibly.

## Detail

**Two approaches**

- **Migration-based (imperative).** A numbered sequence of change scripts (`V1__init.sql`, `V2__add_orders.sql`). The tool tracks which have been applied in a metadata table and runs the missing ones in order. Explicit, auditable, and the dominant approach - Flyway, Liquibase, Alembic, Rails migrations.
- **State-based (declarative).** You maintain the desired schema definition; the tool computes the diff against the target database and generates the change script. Convenient for development, but generated scripts need review before production - an automated diff will happily generate a destructive statement.

Many teams use both: declarative for authoring, with the generated migration committed and reviewed.

**What good practice requires**

- Migrations are **immutable once merged** - never edit an applied script; write a new one. Editing breaks the checksum and diverges environments.
- Scripts are **idempotent or guarded** where possible, and every one is tested by running it against a copy of production-shaped data.
- **Rollback plans** exist, whether as a down script or a documented forward-fix. In practice, forward-fix is safer for data-destructive changes.
- **Reference data** (lookup tables, feature configuration) is versioned too.
- The **same scripts run in every environment**, in the same order, through the same automation.

## Example

```sql
-- migrations/V13__add_order_status.sql
ALTER TABLE orders ADD COLUMN status varchar(20);
UPDATE orders SET status = 'complete' WHERE status IS NULL;   -- backfill in batches for large tables
```

```bash
flyway -url=jdbc:postgresql://db/app -locations=filesystem:migrations info
flyway migrate     # runs only what has not been applied, records checksums
```

## Interview tips

- "Never edit an applied migration" is the rule that reveals whether you have lived with this.
- Explain the migration-versus-state trade-off; naming both approaches shows breadth.
- Point out that reviewing generated diffs is mandatory - tools generate `DROP` statements cheerfully.

---

[⬅ Back to Database Management in DevOps](./README.md) · [All topics](../README.md)
