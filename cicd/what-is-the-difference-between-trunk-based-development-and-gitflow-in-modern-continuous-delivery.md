---
title: "What is the difference between trunk-based development and GitFlow in modern continuous delivery?"
id: 537
category: "CI/CD"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - cicd
  - git
  - gitflow
  - trunk-based
quiz:
  stem: "How do developers using Trunk-Based Development prevent incomplete features from impacting production users if code is merged daily?"
  options:
    - "By commenting out unfinished source code before merging"
    - "By wrapping unfinished features in Feature Flags (feature toggles) keeping them disabled in production"
    - "By storing unfinished commits on unshared local USB drives"
    - "By disabling CI/CD pipelines during active development"
  answer: 2
  explanation: "Feature flags decouple deployment from release, allowing unfinished code to be merged continuously to trunk without exposing the functionality to end users until ready."
---

# What is the difference between trunk-based development and GitFlow in modern continuous delivery?

**Short answer:** Trunk-based development involves all developers merging short-lived feature branches into a single shared branch (trunk) multiple times daily, while GitFlow uses long-lived branches (develop, release, hotfix) with infrequent, high-conflict batch releases.

## Detail

DORA research identifies Trunk-Based Development as a key predictor of elite software delivery performance.

### Comparison

| Feature           | Trunk-Based Development                                 | GitFlow                                       |
| ----------------- | ------------------------------------------------------- | --------------------------------------------- |
| Main Branch       | Single branch (`main` / `trunk`)                        | Dual core branches (`master` + `develop`)     |
| Branch Lifespan   | Hours to at most 1–2 days                               | Days, weeks, or months                        |
| Release Mechanism | Deploys directly from trunk or lightweight release tags | Dedicated `release/*` and `hotfix/*` branches |
| Merge Overhead    | Frequent small merges; trivial conflicts                | Infrequent large merges; complex merge hell   |
| Feature Gating    | Feature flags / progressive delivery                    | Unmerged long-lived branches                  |

Trunk-based development prevents 'merge hell' because branches never diverge far from trunk. Large features are decoupled from deployment using **Feature Flags** (Dark Launching).

### When GitFlow still fits

GitFlow was designed for software shipped as discrete, versioned releases where several versions are supported at once - installed products, mobile apps with store review, embedded firmware. Its author added a note to the original post in 2020 recommending a simpler flow (such as GitHub flow) for continuously delivered web software. The trade-off in trunk-based development is that it demands discipline and tooling: a fast, trusted CI suite on every merge, feature flags (and the cleanup of stale flags), and review that keeps pace with small, frequent PRs. Without those, merging to trunk daily just breaks trunk daily.

## Example

```bash
# Trunk-based: a branch that lives hours, not weeks
git switch -c feat/saml-login origin/main
git commit -am "feat: add SAML login behind flag saml_login"   # code ships dark
git push -u origin feat/saml-login                              # PR, CI, review, merge today

# GitFlow: long-lived develop plus a release branch per version
git switch -c release/2.4.0 develop
git commit -am "chore: bump version to 2.4.0"
git switch main && git merge --no-ff release/2.4.0 && git tag v2.4.0
git switch develop && git merge --no-ff release/2.4.0            # merge back, resolve drift
```

## Interview tips

- Define both by branch lifetime and integration frequency, not by branch names.
- Tie trunk-based development to DORA: it is one of the technical capabilities DORA links to higher deployment frequency and shorter lead time.
- Explain how unfinished work is hidden on trunk (feature flags, branch by abstraction), and mention flag debt as the cost.
- Say when GitFlow is still reasonable - multiple supported release versions, app-store or firmware release cycles - rather than dismissing it.
- Likely follow-up: "how do you handle a hotfix in trunk-based development?" - fix on trunk and cherry-pick onto a short-lived release branch or tag, or roll forward.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#511`): [What is the difference between Continuous Delivery and Continuous Deployment?](../core-devops-concepts/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)
- [[How do you manage build artefacts with Nexus or Artifactory?]] (`#460`): [How do you manage build artefacts with Nexus or Artifactory?](../devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md)
- [[How do you rotate secrets without downtime?]] (`#429`): [How do you rotate secrets without downtime?](../devsecops/how-do-you-rotate-secrets-without-downtime.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
