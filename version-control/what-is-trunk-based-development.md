---
title: "What is Trunk Based Development?"
id: 49
category: "Version Control"
difficulty: "Intermediate"
tags:
  - devops
  - version-control
  - interview-questions
---

# What is Trunk Based Development?

**Short answer:** Trunk-based development is a branching model where all developers integrate into a single shared branch at least daily, using very short-lived branches or direct commits, with unfinished work hidden behind feature flags.

## Detail

The premise: integration pain grows superlinearly with branch age, so keep branches under a day old. There is exactly one long-lived branch, and it is always releasable.

**What makes it work**

- **Feature flags** - merge incomplete code that is switched off, so "not done" never justifies a long branch.
- **Branch by abstraction** - for large refactors, introduce an abstraction layer, migrate implementations behind it incrementally, then remove the old path.
- **Strong CI** - every commit builds and tests in minutes; a red trunk is fixed immediately.
- **Small, reviewable changes** - pull requests measured in tens of lines, reviewed within hours.
- **Release branches only if needed** - cut from trunk at release time, fixes cherry-picked forward.

**Why it matters:** the DORA research consistently identifies trunk-based development as a predictor of elite delivery performance - fewer than three active branches, branches under a day old, and no code freezes.

**The objection** - "our code will be unstable" - is answered by test automation and flags, not by longer branches. Long branches do not make code stable; they defer the discovery of instability.

## Example

```javascript
// Ship the code disabled, enable it independently of deploy
if (flags.isEnabled("new-checkout", { userId })) {
  return newCheckout(cart);
}
return legacyCheckout(cart);
```

## Interview tips

- Link it explicitly to CI: you cannot claim continuous integration with week-old branches.
- Flag lifecycle management - removing stale flags - is the practical downside; mention it.
- Contrast with Git Flow in one sentence to show you know both and choose deliberately.

---

[⬅ Back to Version Control](./README.md) · [All topics](../README.md)
