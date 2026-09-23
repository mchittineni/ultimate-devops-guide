---
title: "What is Git Flow?"
id: 48
category: "Version Control"
difficulty: "Intermediate"
tags:
  - devops
  - version-control
  - interview-questions
---

# What is Git Flow?

**Short answer:** Git Flow is a branching model with two permanent branches - `main` (released code) and `develop` (integration) - plus feature, release, and hotfix branches, designed for software with scheduled, versioned releases.

## Detail

**The branches**

- `main` - production; every commit is tagged with a version.
- `develop` - the integration branch where completed features accumulate.
- `feature/*` - branched from `develop`, merged back into `develop`.
- `release/*` - branched from `develop` when feature-complete; only stabilisation fixes land here. Merged into both `main` (tagged) and `develop`.
- `hotfix/*` - branched from `main` for urgent production fixes; merged into `main` and `develop`.

**Where it fits.** Versioned products, on-premises or packaged software, mobile releases going through app-store review, and teams with a formal QA phase and defined release windows.

**Its costs.** Two permanent branches double the merge surface. Feature branches often live for weeks, which delays integration feedback - precisely what CI is meant to prevent. Release stabilisation periods create a "code freeze" culture. For a continuously deployed web service, this ceremony buys very little - which is why Vincent Driessen, who published the model in 2010, added a note in 2020 recommending a simpler flow such as GitHub Flow for continuously delivered software.

```text
main     ──●───────────────●────────────●──  (v1.0)      (v1.1)   (v1.1.1)
            \             /            /
release      \        ●──●            /
              \      /               /
develop  ──●───●────●───────●───────●──
            \       /        \     /
feature      ●─────●          ●───●
```

## Example

```bash
# Feature: branch from develop, merge back with --no-ff to keep the feature visible
git switch -c feature/payments develop
git commit -am "feat: add payments"
git switch develop && git merge --no-ff feature/payments

# Release: stabilise on a release branch, then merge to main (tagged) AND back to develop
git switch -c release/1.1.0 develop
git commit -am "chore: bump version to 1.1.0"
git switch main && git merge --no-ff release/1.1.0 && git tag -a v1.1.0 -m "1.1.0"
git switch develop && git merge --no-ff release/1.1.0

# Hotfix: branch from main, merge to both
git switch -c hotfix/1.1.1 main
git commit -am "fix: null pointer in checkout"
git switch main && git merge --no-ff hotfix/1.1.1 && git tag -a v1.1.1 -m "1.1.1"
git switch develop && git merge --no-ff hotfix/1.1.1
```

The original `git flow` CLI extension (git-flow / git-flow AVH) automates these steps but is no longer actively maintained; plain Git commands like the above are the portable form.

## Interview tips

- Be able to state when it is appropriate - blanket criticism reads as dogma, not judgement.
- The honest summary: excellent for versioned releases, poor for continuous deployment.
- If your team uses it and struggles, the usual fix is shortening feature branches, not changing the diagram.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)
- [[How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?]] (`#455`): [How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?](../cicd/how-do-you-trigger-a-pipeline-webhooks-polling-schedules-and-upstream-jobs.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Version Control](./README.md) · [All topics](../README.md)
