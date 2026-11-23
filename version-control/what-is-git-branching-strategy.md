---
title: "What is Git Branching Strategy?"
id: 47
category: "Version Control"
difficulty: "Intermediate"
tags:
  - devops
  - version-control
  - interview-questions
---

# What is Git Branching Strategy?

**Short answer:** A branching strategy is the team's agreement on how branches are created, merged, and released - the main options being trunk-based development, GitHub Flow, Git Flow, and release branching, chosen to match release cadence and risk.

## Detail

**Trunk-based development.** Everyone commits to `main` (or via very short-lived branches merged within a day). Incomplete work hides behind feature flags. This is the model that makes CI genuine and is strongly associated with elite DORA performance. It requires good tests and flag discipline.

**GitHub Flow.** A branch per change, a pull request for review, merge to `main`, deploy. Simple, well suited to web services with continuous deployment. Effectively trunk-based if branches stay short.

**Git Flow.** Long-lived `main` and `develop`, plus `feature/*`, `release/*`, and `hotfix/*` branches. Designed for versioned software with scheduled releases and multiple supported versions. Heavy for continuous delivery - the author himself now suggests it is overkill for web apps.

**Release branching.** `main` plus a `release/x.y` branch per version, with fixes cherry-picked back. Standard for software shipped to customers who upgrade at their own pace.

**Choosing:** how often do you release, do you support multiple versions in the field, and how good is your test automation? Continuous deployment of a SaaS product → trunk-based. Quarterly on-premises releases with three supported versions → release branching.

Whatever the model, the practices that matter more than the diagram are: short-lived branches, small pull requests, protected `main` with required checks, and a linear, readable history.

**Hotfixes: the procedure every model needs.** A bug found after release is where a branching strategy is actually tested. The safe sequence is the same whichever model you use:

1. **Mitigate first.** Roll back to the previous version or flip the feature-flag kill switch. That buys time, so the code fix does not have to be rushed.
2. **Branch from what is actually running**, meaning the release tag (`v1.8.0`) or the release branch, not a `main` that already holds two weeks of unreleased work. With pure trunk-based development and continuous deployment, `main` _is_ what is running, so you fix forward on `main`.
3. **Minimal fix plus a regression test.** Review can be expedited, but the change still goes through the same CI pipeline, scans, and single build as any other change.
4. **Tag a patch version** (`v1.8.1`) and deploy it through the normal promotion path, ideally as a short canary.
5. **Bring the fix back** to `main` (and any other supported release branches) by merge or `git cherry-pick -x`, so the next release does not bring the bug back.

## Example

```bash
# Trunk-based / GitHub Flow: one short-lived branch per change
git switch -c fix/login-timeout origin/main
git commit -am "fix: raise login timeout to 30s"
git push -u origin fix/login-timeout
gh pr create --fill                       # review + required checks, then squash-merge today

# Release branching: cut once, patch by cherry-picking fixes from main
git switch -c release/2.4 v2.4.0
git cherry-pick -x 9f2c1ab                # -x records the original commit in the message
git tag -a v2.4.1 -m "2.4.1" && git push origin release/2.4 v2.4.1

# Hotfix: branch from the released tag, not from a main that has moved on
git switch -c hotfix/1.8.1 v1.8.0
git commit -am "fix: correct refund rounding (+ regression test)"
git push -u origin hotfix/1.8.1          # PR, full CI, expedited review
git tag -a v1.8.1 -m "1.8.1" && git push origin v1.8.1
git switch main && git cherry-pick -x hotfix/1.8.1   # so the next release does not regress
```

## Interview tips

- The strongest answer explains the _criteria_ for choosing, not just the diagrams.
- Long-lived branches are the real enemy - name merge hell and delayed integration feedback.
- Feature flags are what let trunk-based development work with unfinished features.
- Expect "a bug is found right after a release, now what?". A weak answer is "fix it on `main` and redeploy", which ships every unreleased change along with the fix. Walk through mitigate, branch from the tag, patch version, same pipeline, and merge back.

**Telling it as a STAR story** (an adaptable example)

- **Situation:** After releasing v1.8.0 of a payments API, a rounding bug hit a small share of refunds, and `main` already held two weeks of unreleased features.
- **Task:** Get a fix to production fast without shipping the unreleased work.
- **Action:** Turned off the new refund path with its feature flag to stop the damage, branched `hotfix/1.8.1` from the `v1.8.0` tag, wrote a failing test and a minimal fix, ran the full CI pipeline with an expedited review, tagged `v1.8.1`, promoted it through staging to a prod canary, then cherry-picked it into `main` with `-x`.
- **Result:** The fix was live about 90 minutes after detection with no unreleased code leaking, and the postmortem added a property-based test for currency rounding.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
- [[How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?]] (`#402`): [How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?](../cicd/how-do-you-troubleshoot-a-jenkins-pipeline-that-never-starts-or-hangs-in-the-queue.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Version Control](./README.md) · [All topics](../README.md)
