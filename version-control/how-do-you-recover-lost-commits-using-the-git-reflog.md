---
title: "How do you recover lost commits using the Git Reflog?"
id: 579
category: "Version Control"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - git
  - reflog
  - troubleshooting
  - recovery
quiz:
  stem: "An engineer accidentally runs `git reset --hard HEAD~1` and loses an unpushed commit. Which command allows them to find the lost commit hash?"
  options:
    - "`git remote -v`"
    - "`git reflog`"
    - "`git status`"
    - "`git push --force`"
  answer: 2
  explanation: "`git reflog` logs every historical movement of the `HEAD` pointer, allowing recovery of orphaned commits that are no longer reachable from branch tips."
---

# How do you recover lost commits using the Git Reflog?

**Short answer:** `git reflog` records every update to `HEAD` in the local repository (checkouts, resets, commits, rebases); you recover accidentally deleted commits by identifying the commit SHA before the destructive action and branching from or resetting to it.

## Detail

When you accidentally run `git reset --hard HEAD~3` or delete a branch with `git branch -D`, Git does not delete the commits from disk immediately. They become dangling commits.

### Recovery Workflow

1. **Inspect Local Reflog**:

   ```bash
   git reflog
   ```

   Output:

   ```text
   7a8b9c0 (HEAD -> main) HEAD@{0}: reset: moving to HEAD~3
   1e2f3a4 HEAD@{1}: commit: add payment integration
   ```

2. **Identify the Lost Commit**: `1e2f3a4` is the state right before the bad reset (`HEAD@{1}`).
3. **Restore into a Safe Branch**:

   ```bash
   git branch recovered-work 1e2f3a4
   ```

   Or force restore main:

   ```bash
   git reset --hard 1e2f3a4
   ```

Dangling commits remain recoverable for a while, not forever: by default reflog entries for commits still reachable from a branch expire after 90 days (`gc.reflogExpire`), entries for unreachable commits after 30 days (`gc.reflogExpireUnreachable`), and once no reflog entry protects an object, `git gc` prunes it after a further grace period (`gc.pruneExpire`, two weeks). Recover promptly.

### What the reflog cannot do

- It is **local to one clone** and never pushed - a colleague's reflog cannot help you, and a fresh clone has an empty one (forges keep their own audit of force-pushes instead).
- It records **ref movements**, not file edits: uncommitted changes lost to `reset --hard` or `restore` are not in it. (Staged content may survive as dangling blobs findable with `git fsck --lost-found`.)
- Each branch has its own reflog (`git reflog show feature/x`) as well as `HEAD`'s; a deleted branch's own reflog is deleted with it, but `HEAD`'s reflog usually still shows the commits you had checked out.

## Example

```bash
# Simulate the accident, then recover
git log --oneline -3
# 1e2f3a4 add payment integration
# 9c8d7e6 add cart
# 7a8b9c0 initial checkout
git reset --hard HEAD~2                 # oops: two commits gone from the branch

git reflog -5
# 7a8b9c0 (HEAD -> main) HEAD@{0}: reset: moving to HEAD~2
# 1e2f3a4 HEAD@{1}: commit: add payment integration

git branch recovered-work HEAD@{1}      # safe: recover into a new branch first
git log --oneline recovered-work -2     # confirm, then merge or reset main to it

# Deleted branch? Find its last tip in HEAD's reflog
git reflog | grep 'checkout: moving from feature/payments'
```

## Interview tips

- Explain the mechanism: commits are not deleted by `reset` or `branch -D`, only unreferenced; the reflog remembers where refs used to point.
- Recover into a new branch first, then decide - it is non-destructive and easy to verify.
- Know the limits: local only, expiry and `gc`, and no record of uncommitted edits.
- Mention `ORIG_HEAD` for undoing the last reset, merge, or rebase, and `git fsck --lost-found` when the reflog has expired.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between trunk-based development and GitFlow in modern continuous delivery?]] (`#537`): [What is the difference between trunk-based development and GitFlow in modern continuous delivery?](../cicd/what-is-the-difference-between-trunk-based-development-and-gitflow-in-modern-continuous-delivery.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Version Control](./README.md) · [All topics](../README.md)
