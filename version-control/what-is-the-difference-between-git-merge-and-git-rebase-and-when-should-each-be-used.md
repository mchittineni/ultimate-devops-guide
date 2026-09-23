---
title: "What is the difference between Git Merge and Git Rebase and when should each be used?"
id: 577
category: "Version Control"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - git
  - merge
  - rebase
  - history
quiz:
  stem: "Why does the 'Golden Rule of Rebasing' advise against rebasing commits that have already been pushed to a shared branch?"
  options:
    - "Rebasing deletes all automated test configurations"
    - "Rebasing rewrites commit SHA hashes, causing the branch history to diverge and breaking collaboration for other teammates"
    - "Git repositories cannot store rebased code in remote cloud hosts"
    - "Rebasing requires continuous internet connectivity"
  answer: 2
  explanation: "Rebasing creates brand new commits with new cryptographic hashes. If teammates have based their work on the original commits, rewriting shared history creates severe synchronization conflicts."
---

# What is the difference between Git Merge and Git Rebase and when should each be used?

**Short answer:** Git Merge joins two branches together by creating a new merge commit that preserves exact historical timestamps and branching topology; Git Rebase replays feature branch commits one by one onto the tip of the target branch, creating a clean, linear commit history.

## Detail

The decision between merge and rebase shapes team collaboration:

### Git Merge

```text
      C1---C2 (feature)
     /       \
A---B---------M (main)
```

- **Pros**: Non-destructive; commit hashes and branch topology are preserved exactly as they occurred.
- **Cons**: Cluttered commit history filled with noisy 'Merge branch main into feature' commits.

### Git Rebase

```text
A---B---C1'---C2' (main & feature linear)
```

- **Pros**: Clean, linear git history. Makes `git bisect` and code audits effortless.
- **Cons**: Rewrites commit history (alters commit hashes).

### The Golden Rule of Rebasing

**Never rebase commits that have been pushed to a public or shared branch.** Rebasing rewrites commit SHAs; teammates working on the same branch will have their history diverge, leading to painful merge reconciliation.

Rebasing your _own_ feature branch before review is fine and common - update it with `git pull --rebase` or `git rebase origin/main`, then publish with `git push --force-with-lease`, which refuses to overwrite the remote if someone else pushed in the meantime.

### Trade-offs, and the middle ground

- Rebasing resolves conflicts **per replayed commit**, so a long branch may make you resolve the same area repeatedly (`rerere` helps); a merge resolves once.
- A rebased commit was never tested in its new position - intermediate commits may not build, which undermines the "clean history helps bisect" argument unless CI tests each commit.
- **Squash-and-merge** on the forge gives `main` one linear commit per PR without anyone rewriting shared history, at the cost of losing the individual commits on `main`. Most teams pick one of: squash-merge, rebase-merge, or merge commits - and enforce it in the repository settings.

## Example

```bash
# Merge: preserve topology, one merge commit
git switch main
git merge --no-ff feature/payments

# Rebase: replay your local feature commits onto the latest main, then publish safely
git switch feature/payments
git fetch origin
git rebase origin/main              # resolve conflicts, then: git rebase --continue
git push --force-with-lease         # only ever on a branch you own

# Tidy before review: squash fixups interactively (local, unpublished commits only)
git rebase -i origin/main

# Undo a rebase that went wrong
git reset --hard ORIG_HEAD
```

## Interview tips

- Define both by what they do to history: merge adds a commit with two parents; rebase creates new commits with new SHAs.
- State the golden rule and its practical form: rebase your own branch freely, never a shared one; publish with `--force-with-lease`.
- Give the trade-offs, not a preference: linear history versus true topology, repeated conflict resolution, untested intermediate commits.
- Mention squash-and-merge as what many teams actually use, and `ORIG_HEAD` / the reflog as the recovery path.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between trunk-based development and GitFlow in modern continuous delivery?]] (`#537`): [What is the difference between trunk-based development and GitFlow in modern continuous delivery?](../cicd/what-is-the-difference-between-trunk-based-development-and-gitflow-in-modern-continuous-delivery.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Version Control](./README.md) · [All topics](../README.md)
