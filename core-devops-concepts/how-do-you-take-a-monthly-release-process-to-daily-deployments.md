---
title: "How do you take a monthly release process to daily deployments?"
id: 285
category: "Core DevOps Concepts"
difficulty: "Advanced"
tags:
  - devops
  - core-devops-concepts
  - interview-questions
---

# How do you take a monthly release process to daily deployments?

**Short answer:** Attack batch size and the confidence gap together. Make releases smaller and more frequent only as fast as you can make them _safe_: automated tests that people trust, a one-command reversible deploy, decoupling of deploy from release via feature flags, and observability good enough to detect a bad change in minutes. The sequence is measure → automate the tests → shrink the batch → decouple release from deploy → remove the manual gate. Skipping to the last step is how organisations get a monthly outage cadence instead.

## Detail

**Start by measuring, because you will need the evidence.** Baseline the four DORA metrics - deployment frequency, lead time for changes, change failure rate, and time to restore - plus the thing nobody measures: how many _hours of human toil_ a release consumes. A monthly release usually hides a two-day change-advisory process, a manual regression pass, and a war room. Those costs are your argument.

**Understand why the batch is monthly.** It is almost never "we like monthly". It is one of: manual regression testing that takes a week, a release process that requires six people in a room, a database migration process that is risky, an environment that cannot be reproduced, an approval board that meets monthly, or a rollback story that is "restore from backup". Each has a different fix, so diagnose before prescribing.

**The sequence that works:**

1. **Make the pipeline the only path to production.** No manual steps, no engineer with SSH access doing the deploy. Even if it still runs monthly, one automated path is the foundation for everything else. Build once, promote the same artifact through environments.
2. **Buy trust with tests.** The blocker to frequency is almost always that nobody believes the test suite. Invest in a fast, reliable core: unit tests, contract tests between services, and a thin layer of end-to-end tests on the critical paths. Ruthlessly delete or quarantine flaky tests - a suite people re-run until it passes provides zero signal.
3. **Make rollback boring.** Until reverting takes one command and under five minutes, nobody will consent to deploying often. Immutable artifacts, backward-compatible database migrations (expand/contract: add the new column, dual-write, backfill, switch reads, drop the old column - never in one release), and a rehearsed rollback path.
4. **Shrink the batch.** Trunk-based development or short-lived branches, merged daily. Batch size is the single biggest driver of change failure rate: a release containing three changes is diagnosable, a release containing 300 is not. This step is cultural as much as technical.
5. **Decouple deploy from release.** Feature flags let code reach production dark and be enabled later, per cohort. Once deploying is no longer the same event as launching, deploy frequency stops being a business risk conversation and becomes an engineering practice.
6. **Deploy progressively.** Canary or blue/green with automated analysis: route 5% of traffic, compare error rate and latency against baseline, promote or roll back automatically. This is what converts "we deploy daily" from a claim into a safe default.
7. **Replace the manual gate with evidence.** Change-advisory boards exist because nobody could prove a change was safe. Give the auditors what they actually need - who changed what, which tests passed, who approved the pull request, and the automated rollback record - as pipeline artifacts. This is where a compliance-heavy organisation gets unblocked, and it is often the hardest conversation.

**Expect these obstacles.** Long-lived branches and merge pain; database changes treated as a separate release train; shared staging environments that queue teams behind each other; a QA team whose role is defined by the manual gate; and on-call engineers who reasonably fear more change. The response to the last one is data: smaller changes reduce failure rate, and time-to-restore improves because the change set is small enough to read.

**What success looks like at each stage** - and it is genuinely incremental: monthly → biweekly → weekly is usually pure test and rollback automation; weekly → daily needs trunk-based development and flags; daily → on-merge needs progressive delivery and no manual gate. Publishing the metrics per team makes the improvement visible and keeps the momentum.

## Example

```yaml
# Expand/contract migration: three releases, each independently revertible.
# Release 1 - expand. Additive only, old code still works.
- ALTER TABLE users ADD COLUMN email_normalised text;
- CREATE INDEX CONCURRENTLY idx_users_email_norm ON users (email_normalised);
# App writes both columns, reads the old one.

# Release 2 - migrate. Backfill in batches, then flip reads behind a flag.
- UPDATE users SET email_normalised = lower(email) WHERE email_normalised IS NULL LIMIT 10000;
# Flag `read_normalised_email` enabled per cohort; old column still populated.

# Release 3 - contract. Only after the flag is 100% and soaked.
- ALTER TABLE users DROP COLUMN email;
```

```yaml
# Progressive delivery with automated analysis - the gate that replaces the human one.
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: api
spec:
  strategy:
    canary:
      steps:
        - setWeight: 5
        - pause: { duration: 5m }
        - analysis:
            templates: [{ templateName: error-rate-and-latency }]
        - setWeight: 25
        - pause: { duration: 10m }
        - setWeight: 100
  # A failed analysis aborts and shifts traffic back automatically.
```

```bash
# The metrics that make the case, measured before and after.
# deployment frequency, lead time, change failure rate, time to restore
git log --since='90 days ago' --grep='^deploy' --oneline | wc -l
gh pr list --state merged --limit 200 --json mergedAt,createdAt \
  | jq '[.[] | (.mergedAt|fromdate) - (.createdAt|fromdate)] | add/length/3600' # lead time hrs
```

## Interview tips

- Lead with batch size and the confidence gap. Frequency is an outcome of safety, not a target you set independently.
- Give the sequence in order and justify why rollback and tests come before frequency. Candidates who start at "we enabled continuous deployment" get taken apart.
- The expand/contract migration pattern is the highest-value concrete detail in this answer. Have it ready with the three releases named.
- Separate deploy from release explicitly via feature flags. It is the idea that makes daily deployment politically possible.
- Address the change-advisory board directly: replace the manual gate with pipeline evidence rather than arguing it away. This shows you have worked in a regulated environment.
- Acknowledge the human side - QA role changes, on-call fear - and answer it with data rather than enthusiasm.

---

[⬅ Back to Core DevOps Concepts](./README.md) · [All topics](../README.md)
