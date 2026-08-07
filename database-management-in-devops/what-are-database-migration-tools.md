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

| Tool                                 | Ecosystem         | Format               | Notes                                                                   |
| ------------------------------------ | ----------------- | -------------------- | ----------------------------------------------------------------------- |
| **Flyway**                           | JVM, CLI, Docker  | Plain SQL (and Java) | Simplest model: numbered SQL files plus a schema history table          |
| **Liquibase**                        | JVM, CLI          | XML, YAML, JSON, SQL | Database-agnostic changelogs, rollback support, preconditions, contexts |
| **Alembic**                          | Python/SQLAlchemy | Python scripts       | Autogenerate from model diffs; branching and merge support              |
| **Django / Rails migrations**        | Framework-native  | Python / Ruby DSL    | Tight ORM integration, generated from model changes                     |
| **Entity Framework Core**            | .NET              | C#                   | `dotnet ef migrations` workflow                                         |
| **Prisma Migrate / Atlas**           | Node, polyglot    | Declarative schema   | Modern declarative-to-migration workflow, good CI integration           |
| **gh-ost / pt-online-schema-change** | MySQL             | N/A                  | Online schema change for very large tables without long locks           |

**How they work.** Each tool maintains a metadata table recording applied versions with checksums. On run, it compares the scripts on disk with that table and applies what is missing, in a transaction where the engine supports transactional DDL (PostgreSQL does; MySQL largely does not - a critical difference when a migration fails halfway).

**Choosing one:** match your language ecosystem, decide whether you need database-agnostic changelogs (Liquibase) or prefer raw SQL you can read and reason about (Flyway), and check support for your CI/CD flow and for the online-change tooling your database size demands.

**Operationally**, run migrations as a discrete pipeline step (or a Kubernetes Job / Helm `pre-upgrade` hook) with a lock preventing concurrent runs, a timeout, and clear failure handling.

## Interview tips

- Transactional DDL differences between PostgreSQL and MySQL is a strong, practical distinction to raise.
- For very large tables, name `gh-ost` or `pt-online-schema-change` - it signals real scale experience.
- Explain where migrations run in the deployment sequence, and how you prevent two pods running them at once.

---

[⬅ Back to Database Management in DevOps](./README.md) · [All topics](../README.md)
