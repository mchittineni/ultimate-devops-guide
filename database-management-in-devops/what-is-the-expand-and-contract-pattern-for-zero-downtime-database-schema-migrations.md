---
title: "What is the Expand and Contract pattern for zero-downtime database schema migrations?"
id: 662
category: "Database Management in DevOps"
difficulty: "Intermediate"
tags:
  - devops
  - database-management-in-devops
  - interview-questions
  - databases
  - zero-downtime
  - expand-contract
  - migrations
quiz:
  stem: "Why must breaking database schema changes (like renaming a column) follow the Expand and Contract pattern during rolling updates?"
  options:
    - "Because SQL syntax prohibits renaming columns"
    - "Because during rolling updates, old and new application versions run concurrently; direct column renames break running older instances instantly"
    - "To reduce database licensing fees"
    - "Because Kubernetes does not support relational databases"
  answer: 2
  explanation: "During rolling updates, older pods expecting the old column name run alongside newer pods expecting the new column name. The Expand and Contract pattern maintains backward compatibility."
---

# What is the Expand and Contract pattern for zero-downtime database schema migrations?

**Short answer:** The Expand and Contract (Parallel Change) pattern safely rolls out breaking schema changes across three distinct deployment phases (Expand, Migrate/Dual-Write, Contract), ensuring that older and newer application versions can run concurrently without downtime.

## Detail

If you rename a column directly (`ALTER TABLE users RENAME COLUMN phone TO mobile;`), every running application instance that still references `phone` starts failing immediately - and during a rolling deploy, some instances always do. Rolling back the code then fails too, because the old code expects `phone`.

### The phases

**Phase 1: Expand (additive, non-breaking)**

- Add the new column alongside the old one: `ALTER TABLE users ADD COLUMN mobile varchar(20);` - nullable, no volatile default, so it is a fast metadata change.
- Deploy app version v2: it still reads `phone` but **writes to both** `phone` and `mobile`. (A database trigger can do the dual write instead, which also covers writers you do not control.)

**Phase 2: Backfill and switch reads**

- Copy historical data from `phone` to `mobile` in small, throttled, restartable batches - one giant `UPDATE` locks rows, bloats the WAL, and lags replicas.
- Verify the columns match, then deploy v3: it reads `mobile`. Keep writing both for one release so a rollback to v2 still sees correct data.

**Phase 3: Contract (cleanup)**

- Deploy v4, which writes only `mobile`.
- Once no running version references `phone` - and query logs or `pg_stat_statements` confirm it - drop it in a later release: `ALTER TABLE users DROP COLUMN phone;`
- Add any constraints (for example `NOT NULL`) with the online-safe forms (`NOT VALID` then `VALIDATE`).

**The invariant.** At every step, the schema is compatible with both the currently deployed version and the one being rolled out, so any single deploy can be rolled back. A migration and the code that depends on it never ship in the same release.

**Trade-offs.** The change takes three or four releases instead of one, dual-write code and triggers add complexity and must actually be removed, the backfill needs care on large tables, and data can diverge if one write path forgets to dual-write. The contract step is also the one point of no return - take a backup or snapshot before dropping data.

## Example

```sql
-- Phase 1 (expand): additive, safe while old code runs.
ALTER TABLE users ADD COLUMN mobile varchar(20);

-- Phase 2 (backfill): batched and restartable; rerun until it updates 0 rows.
UPDATE users SET mobile = phone
WHERE id IN (
  SELECT id FROM users
  WHERE mobile IS NULL AND phone IS NOT NULL
  ORDER BY id LIMIT 5000
);

-- Verify before switching reads.
SELECT count(*) FROM users WHERE mobile IS DISTINCT FROM phone;  -- expect 0

-- Phase 3 (contract): a later release, once nothing references phone.
ALTER TABLE users DROP COLUMN phone;
```

## Interview tips

- Start with why a direct rename fails: old and new code run together during a rolling deploy, and rollback must keep working.
- Walk through expand, backfill and switch, contract - and state the invariant that each step is compatible with the versions on either side.
- Insist on batched backfills and a verification query before switching reads.
- Mention the trade-offs: more releases, dual-write complexity, and cleanup debt if the contract phase never happens.
- Tie it to deployment strategies: expand/contract is what makes rolling, blue/green, and canary deploys safe when the schema changes.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Database Management in DevOps](./README.md) · [All topics](../README.md)
