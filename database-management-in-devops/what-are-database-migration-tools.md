---
title: "What are Database Migration Tools?"
id: 113
category: "Database Management in DevOps"
difficulty: "Intermediate"
tags:
  - devops
  - database-management-in-devops
  - interview-questions
---

# What are Database Migration Tools?

**Short answer:** Flyway and Liquibase for the JVM and general use, Alembic for Python, and framework-native tools (Rails, Django, Entity Framework, Prisma) - all of which apply versioned, tracked schema changes in a repeatable order.

## Detail

| Tool                                 | Ecosystem         | Format               | Notes                                                                                                                          |
| ------------------------------------ | ----------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Flyway**                           | JVM, CLI, Docker  | Plain SQL (and Java) | Simplest model: numbered SQL files plus a schema history table                                                                 |
| **Liquibase**                        | JVM, CLI          | XML, YAML, JSON, SQL | Database-agnostic changelogs, rollback support, preconditions, contexts. Community is FSL-licensed (source-available) from 5.0 |
| **Alembic**                          | Python/SQLAlchemy | Python scripts       | Autogenerate from model diffs; branching and merge support                                                                     |
| **Django / Rails migrations**        | Framework-native  | Python / Ruby DSL    | Tight ORM integration, generated from model changes                                                                            |
| **Entity Framework Core**            | .NET              | C#                   | `dotnet ef migrations` workflow                                                                                                |
| **Prisma Migrate / Atlas**           | Node, polyglot    | Declarative schema   | Modern declarative-to-migration workflow, good CI integration                                                                  |
| **gh-ost / pt-online-schema-change** | MySQL             | N/A                  | Online schema change for very large tables without long locks                                                                  |

**How they work.** Each tool maintains a metadata table recording applied versions with checksums. On run, it compares the scripts on disk with that table and applies what is missing, in a transaction where the engine supports transactional DDL (PostgreSQL does; MySQL largely does not - a critical difference when a migration fails halfway).

**Choosing one:** match your language ecosystem, decide whether you need database-agnostic changelogs (Liquibase) or prefer raw SQL you can read and reason about (Flyway), and check support for your CI/CD flow and for the online-change tooling your database size demands.

**Operationally**, run migrations as a discrete pipeline step (or a Kubernetes Job / Helm `pre-upgrade` hook) with a lock preventing concurrent runs, a timeout, and clear failure handling.

**Licensing is part of the choice now.** Liquibase Community moved from Apache 2.0 to the Functional Source License (FSL, converting to Apache 2.0 after two years) with version 5.0 - fine to run in production, but no longer OSI open source. Flyway's core is open source, while features such as undo migrations and drift reports sit in Redgate's paid editions. Check the current terms before standardising.

**Limitations.** These tools order and record changes; they do not make a change safe. A migration that takes an exclusive lock on a large table is just as dangerous when Flyway runs it, which is why teams add migration linters (Squawk, `atlas migrate lint`) in CI.

## Example

```text
db/migration/
  V1__create_orders.sql
  V2__add_orders_customer_idx.sql
  R__refresh_reporting_views.sql      # repeatable: re-runs whenever its checksum changes
```

```bash
# Flyway in a pipeline step, from the official container image.
docker run --rm -v "$PWD/db/migration:/flyway/sql" \
  -e FLYWAY_URL="jdbc:postgresql://db.internal:5432/app" \
  -e FLYWAY_USER=migrator -e FLYWAY_PASSWORD="$DB_PASSWORD" \
  flyway/flyway:13 -validateMigrationNaming=true validate migrate info
```

## Interview tips

- Transactional DDL differences between PostgreSQL and MySQL is a strong, practical distinction to raise.
- For very large tables, name `gh-ost` or `pt-online-schema-change` - it signals real scale experience.
- Explain where migrations run in the deployment sequence, and how you prevent two pods running them at once.
- Knowing that Liquibase Community is now FSL-licensed shows you track tooling changes, not just features.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Database Management in DevOps](./README.md) · [All topics](../README.md)
