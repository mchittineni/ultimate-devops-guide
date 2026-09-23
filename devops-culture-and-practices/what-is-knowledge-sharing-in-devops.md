---
title: "What is Knowledge Sharing in DevOps?"
id: 129
category: "DevOps Culture and Practices"
difficulty: "Beginner"
tags:
  - devops
  - devops-culture-and-practices
  - interview-questions
---

# What is Knowledge Sharing in DevOps?

**Short answer:** Knowledge sharing is the deliberate practice of spreading operational and technical understanding across a team - through documentation, runbooks, pairing, reviews, and internal talks - so capability does not depend on specific individuals.

## Detail

**Why it matters operationally.** Concentrated knowledge is a reliability risk. If one person understands the deployment pipeline, every incident during their holiday takes longer, on-call is unfair, and the organisation cannot scale.

**Mechanisms that work**

- **Documentation as part of done.** Architecture decision records (ADRs) capturing _why_ a choice was made, runbooks for operational tasks, and READMEs kept next to the code so they are updated with it.
- **Runbooks linked from alerts** - the most immediately valuable documentation in any organisation.
- **Pair and mob programming** - high-bandwidth transfer, particularly effective for onboarding and for spreading knowledge of a gnarly subsystem.
- **Code review as teaching** - comments that explain reasoning rather than just requesting changes.
- **Post-mortems published openly** - one team's incident is every team's lesson.
- **Internal tech talks, brown bags, and demo days.**
- **Shadowing on-call** before carrying the pager.
- **Communities of practice** - a guild across teams for a shared concern such as Kubernetes or observability.

**What blocks it:** no time allocated, documentation that is stale and therefore distrusted, tools nobody can search, and a reward system that values being indispensable.

**Practical tests:** could a new joiner deploy to production on day three by following the docs? If your most senior engineer disappeared for a month, what breaks? Answering those honestly usually produces the backlog.

## Example

An architecture decision record (Michael Nygard's format), stored next to the code in `docs/adr/`:

```markdown
# ADR 0007: Use PgBouncer in transaction mode for the orders database

- Status: Accepted
- Date: 2026-09-10

## Context
Scaling the orders API to 40 pods pushed PostgreSQL past max_connections during deploys.

## Decision
Put PgBouncer in transaction-pooling mode between the pods and the database.

## Consequences
- Server connections capped at 60 regardless of pod count.
- Session features (SET, advisory locks, session-level prepared statements) are unavailable;
  the ORM is configured accordingly.
```

## Interview tips

- ADRs are a strong, specific practice to name - capturing _why_, not just what.
- "Documentation is part of done" only works if it is reviewed in the same pull request; say that.
- The bus-factor question is a memorable way to frame the risk.
- Trade-off: documentation has a maintenance cost; a small set of trusted, owned documents (runbooks linked from alerts, ADRs) beats a large wiki nobody updates.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you deal with flaky tests in a CI pipeline?]] (`#398`): [How do you deal with flaky tests in a CI pipeline?](../cicd/how-do-you-deal-with-flaky-tests-in-a-ci-pipeline.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Culture and Practices](./README.md) · [All topics](../README.md)
