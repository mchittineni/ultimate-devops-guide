---
title: "How do you roll out breaking platform changes safely?"
id: 229
category: "Platform Engineering"
difficulty: "Advanced"
tags:
  - devops
  - platform-engineering
  - interview-questions
---

# How do you roll out breaking platform changes safely?

**Short answer:** Treat the platform interface as a versioned public API: ship the new version alongside the old, announce a deprecation with a dated removal, provide automated migration (a codemod or bot-raised pull requests), track consumer migration progress, and only then remove the old path. For changes you cannot version - a Kubernetes upgrade, a base-image bump - stage them across environments and cohorts with a tested rollback.

## Detail

**Version anything consumers depend on:** templates, CRD API versions, pipeline contracts, CLI flags, base images, Helm chart values, and the shape of injected configuration. Semantic versioning plus a published support window ("N-1 supported for 6 months") turns a surprise into a schedule.

**Migrate for people, do not ask them to.** The difference between a migration that finishes and one that stalls at 60% is whether the platform team wrote the automation: a codemod or `sed`-level script, a bot opening a pull request per repository with the change applied and CI green, and a dashboard showing who is left. Asking 40 teams to each spend an afternoon rewriting the same YAML guarantees a long tail - and the long tail is what blocks the removal.

**Cohort the rollout.** Platform team's own services first, then volunteers, then a friendly cohort, then everyone, with a defined bake time and pass criteria between stages. This is progressive delivery applied to infrastructure changes, and the pass criteria should be explicit - error rates, deploy success rate, support ticket volume.

**Communicate on a schedule, in the channels people read.** Announcement with rationale and a dated timeline; automated warnings in CI output and CLI when a deprecated path is used ("this will fail after 2026-11-01, see MIGRATION.md"); reminders at fixed intervals; and a final notice. In-tool warnings outperform announcements, because they arrive when the developer is actually touching the thing.

**Know which changes cannot be versioned** - Kubernetes minor upgrades, cluster-wide policy tightening, network changes - and handle them with environment staging (dev → staging → prod), canary clusters or node pools, a tested rollback plan, and, for policy, audit mode before enforcement so you see the blast radius before it bites.

**Have an escape hatch and a deadline.** Extensions should be possible but explicit: a named owner, a stated reason, a new date, and visible in a report. Indefinite exceptions mean you now maintain both paths forever, which is how platform teams end up with no capacity for new work.

**Measure and learn from each migration:** how long it took, how many teams needed help, what the automation missed. That data is what makes the next migration cheaper, and it is a strong thing to be able to talk about in an interview.

## Example

```text
Migration plan: platform.acme.com/v1beta1 -> v1  (42 consumers)

T-90d  v1 shipped alongside v1beta1; both reconciled; docs updated
       migration guide + `acme migrate v1` codemod published
T-90d  CI emits a warning on every v1beta1 use, naming the removal date
T-75d  platform team's own 6 services migrated (dogfood; 2 codemod bugs fixed)
T-60d  bot opens PRs for all 42 repos with the change applied and CI passing
       dashboard published: migrated / open PR / not started, by team
T-30d  15 remaining; direct outreach; pairing offered; 3 extensions granted
       (named owner, reason, new date, listed publicly)
T-7d   final notice; 2 remaining, both with approved extensions to T+30d
T-0    v1beta1 reconciliation disabled for everyone else; v1beta1 CRD removed T+30d
T+30d  retrospective: 89% migrated by bot PR alone; codemod missed nested values

Rollback plan at every stage: re-enable v1beta1 reconciliation (kept for 30 days).
```

## Interview tips

- "Version it, automate the migration, cohort the rollout, then remove" is the whole answer in one line.
- The bot-raised pull request with CI already green is the detail that shows you have actually finished a migration.
- Expect: "what about changes you cannot version, like a Kubernetes upgrade?" - staged environments, canary node pools, audit-before-enforce for policy, tested rollback.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you structure Terraform code for multiple environments and providers?]] (`#422`): [How do you structure Terraform code for multiple environments and providers?](../infrastructure-as-code/how-do-you-structure-terraform-code-for-multiple-environments-and-providers.md)
- [[How do you write and structure a reusable Terraform module?]] (`#463`): [How do you write and structure a reusable Terraform module?](../infrastructure-as-code/how-do-you-write-and-structure-a-reusable-terraform-module.md)
- [[What is Infrastructure as Code?]] (`#26`): [What is Infrastructure as Code?](../infrastructure-as-code/what-is-infrastructure-as-code.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Platform Engineering](./README.md) · [All topics](../README.md)
