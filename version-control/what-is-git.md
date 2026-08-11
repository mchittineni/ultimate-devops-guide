---
title: "What is Git?"
id: 46
category: "Version Control"
difficulty: "Beginner"
tags:
  - devops
  - version-control
  - interview-questions
---

# What is Git?

**Short answer:** Git is a distributed version control system that records project history as a graph of immutable commits, giving every clone the full history and enabling cheap branching, offline work, and safe collaboration.

## Detail

**Distributed** means each clone is a complete repository, not a working copy. You can commit, branch, diff, and inspect history with no network. A "central" repository is a convention, not a technical requirement.

**The object model** is what makes Git predictable. A commit points to a tree (a snapshot of the directory), to its parents, and carries author, timestamp, and message. Every object is addressed by the SHA of its content, so history is tamper-evident - changing anything changes every subsequent hash. Branches are just movable pointers to commits, which is why branching is instant.

**The three areas:** working directory → staging area (index) → repository. `git add` moves changes to the index, `git commit` writes them to history.

Everyday commands:

```bash
git clone <url>
git switch -c feature/x        # create and switch branch
git add -p                     # stage hunks interactively
git commit -m "..."
git fetch && git rebase origin/main
git push -u origin feature/x
git log --oneline --graph --decorate
```

Recovery commands worth knowing cold: `git reflog` (find any commit you "lost"), `git revert` (safe undo on shared branches), `git reset --hard` (dangerous, local only), `git cherry-pick`, `git bisect` (binary search for the commit that broke something), `git stash`.

## Interview tips

- The SHA-addressed object graph and "branches are pointers" are the answers that show real understanding.
- `revert` versus `reset`: revert makes a new commit and is safe on shared history; reset rewrites and is not.
- `git reflog` is the answer to "I destroyed my work" - almost nothing is truly lost for 90 days.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)
- [[How do you troubleshoot a GitOps pipeline that will not sync?]] (`#428`): [How do you troubleshoot a GitOps pipeline that will not sync?](../devops-tools-and-automation/how-do-you-troubleshoot-a-gitops-pipeline-that-will-not-sync.md)
- [[How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?]] (`#402`): [How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?](../cicd/how-do-you-troubleshoot-a-jenkins-pipeline-that-never-starts-or-hangs-in-the-queue.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Version Control](./README.md) · [All topics](../README.md)
