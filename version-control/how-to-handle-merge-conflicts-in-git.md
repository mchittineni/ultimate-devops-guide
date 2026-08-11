---
title: "How to handle merge conflicts in Git?"
id: 50
category: "Version Control"
difficulty: "Beginner"
tags:
  - devops
  - version-control
  - interview-questions
---

# How to handle merge conflicts in Git?

**Short answer:** Fetch the latest target branch, merge or rebase, inspect each conflicted file, resolve by choosing or combining the changes, remove the markers, run the tests, then `git add` and complete the merge or `git rebase --continue`.

## Detail

A conflict occurs when two branches change the same lines, or when one deletes a file the other modified. Git marks the region and stops.

**The workflow**

```bash
git fetch origin
git rebase origin/main          # or: git merge origin/main

git status                      # lists "both modified" files
git diff --name-only --diff-filter=U

# edit each file, or use a merge tool
git mergetool

git add path/to/resolved.js
git rebase --continue           # or: git commit   (for a merge)
```

**Reading the markers**

```text
<<<<<<< HEAD
const timeout = 30;          # the branch you are on (during merge)
=======
const timeout = 60;          # the incoming change
>>>>>>> feature/timeouts
```

Note that during a _rebase_ the sides are inverted relative to a merge - `HEAD` is the upstream branch. This trips people up constantly.

**Useful tools**

- `git checkout --ours <file>` / `--theirs <file>` when one side wins wholesale.
- `git merge --abort` / `git rebase --abort` to get back to safety.
- `git config rerere.enabled true` - Git remembers how you resolved a conflict and replays it, which is a large win during long rebases.
- `git log --merge -p <file>` to see the commits from both sides that touched the file.

**Prevention beats cure:** short-lived branches, frequent integration, small pull requests, agreed code formatting (so whitespace never conflicts), and avoiding wide refactors during a busy period.

## Interview tips

- Always mention running the tests after resolving - a syntactically clean resolution can still be semantically wrong.
- `rerere` is a detail that signals real day-to-day Git experience.
- Frame prevention as the primary answer; conflict resolution is a symptom of long-lived branches.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)
- [[How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?]] (`#402`): [How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?](../cicd/how-do-you-troubleshoot-a-jenkins-pipeline-that-never-starts-or-hangs-in-the-queue.md)
- [[How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?]] (`#455`): [How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?](../cicd/how-do-you-trigger-a-pipeline-webhooks-polling-schedules-and-upstream-jobs.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Version Control](./README.md) · [All topics](../README.md)
