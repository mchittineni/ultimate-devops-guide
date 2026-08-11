---
title: "What is the difference between git merge, rebase, and cherry-pick?"
id: 263
category: "Version Control"
difficulty: "Intermediate"
tags:
  - devops
  - version-control
  - interview-questions
---

# What is the difference between git merge, rebase, and cherry-pick?

**Short answer:** `merge` joins two branches with a new commit that has two parents, preserving history exactly as it happened. `rebase` replays your commits on top of another branch, creating new commits with new hashes and a linear history. `cherry-pick` copies one specific commit onto the current branch. The rule that governs all three: **never rewrite history that other people have already pulled.**

## Detail

**Merge** creates a merge commit with two parents (unless the merge is a fast-forward, where the branch simply moves up). History is truthful: you can see that a branch existed, when it started, and when it landed. The cost is noise - a busy repository accumulates merge commits, and `git log` becomes hard to read.

**Rebase** takes each of your commits, computes its diff, and re-applies it on top of the new base. The result looks as though you started your work from the latest `main`. The commits are **new objects with new SHAs** - the originals still exist in the reflog but are no longer on your branch. That is the entire risk: if you rebase commits someone else has based work on, their history and yours have diverged even though the changes look identical, and the next `pull` produces duplicate commits and confusing conflicts.

|                                             | Merge                     | Rebase                               |
| ------------------------------------------- | ------------------------- | ------------------------------------ |
| History                                     | Preserved, non-linear     | Rewritten, linear                    |
| Commit hashes                               | Unchanged                 | All new                              |
| Conflict resolution                         | Once, in the merge commit | Potentially once per commit replayed |
| Safe on shared branches                     | Yes                       | **No**                               |
| Traceability of "when did this branch land" | Explicit                  | Lost                                 |

**The practical convention** most teams settle on: rebase your _local_ feature branch onto `main` to keep it current (`git pull --rebase`), then merge it into `main` via a pull request. You get a clean linear feature history and an explicit record of integration. Squash-merging is the third option - the whole branch becomes one commit on `main`, which suits trunk-based development and makes reverts trivial, at the cost of losing intermediate commits.

**Cherry-pick** applies the _change_ introduced by a commit onto your current branch as a new commit. The classic use is a hotfix: a bug is fixed on `main` and the same fix must reach `release/2.4` without dragging along everything else on `main`. Use `-x` so the new commit message records the original SHA - future archaeologists will thank you. Cherry-picking the same change into two branches that later merge produces a duplicate-change conflict, so treat it as a targeted tool, not a workflow.

**Related distinctions interviewers pair with this:**

- **`git fetch` vs `git pull`** - `fetch` downloads refs and objects and changes nothing in your working tree; `pull` is `fetch` plus `merge` (or `rebase` with `--rebase`). Fetch when you want to look before you leap.
- **`git stash` / `git stash pop`** - park uncommitted work to switch context, then reapply it. `pop` applies and drops; `apply` keeps the stash entry.
- **Tags** - a named pointer to a commit, used for releases. Annotated tags (`-a`) are real objects with an author, date, and message, and can be signed; lightweight tags are just a ref. Use annotated tags for anything you ship.
- **`--force-with-lease` vs `--force`** - after a rebase you must force-push. `--force` overwrites the remote unconditionally, silently discarding a colleague's commits if they pushed while you were rebasing. `--force-with-lease` refuses unless the remote is still where you last saw it. **Always use `--force-with-lease`.**

## Example

```bash
# Keep a feature branch current without a merge commit
git switch feature/checkout
git fetch origin
git rebase origin/main
# resolve conflicts per replayed commit, then:
git rebase --continue          # or --abort to bail out entirely
git push --force-with-lease    # required: the SHAs changed

# Interactive rebase: clean up before review
git rebase -i origin/main      # squash fixups, reword messages, drop commits

# Backport one fix to a release branch, recording where it came from
git switch release/2.4
git cherry-pick -x 9f2c1ab
git push origin release/2.4

# Make rebase the default for pulls (avoids accidental merge commits)
git config --global pull.rebase true

# Look before merging
git fetch origin
git log --oneline HEAD..origin/main   # what is about to arrive
```

## Interview tips

- Lead with the structural difference - merge adds a commit with two parents, rebase rewrites commits with new SHAs - then give the golden rule about shared branches.
- "Rebase or merge?" is not a trick question with one answer. Say what your team does and why: rebase locally to stay current, merge (or squash-merge) via PR to integrate.
- Volunteering `--force-with-lease` over `--force` is a strong, cheap signal that you have worked on a shared repository.
- `git fetch` vs `git pull` appears in almost every git round. One sentence: fetch updates refs, pull fetches and integrates.
- For cherry-pick, give the concrete use case (hotfix backport) rather than the definition, and mention `-x`.
- If asked "how do you undo a rebase that went wrong" - `git reflog` then `git reset --hard HEAD@{n}`. Knowing the reflog exists is what makes rebasing safe.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?]] (`#402`): [How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?](../cicd/how-do-you-troubleshoot-a-jenkins-pipeline-that-never-starts-or-hangs-in-the-queue.md)
- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)
- [[How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?]] (`#455`): [How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?](../cicd/how-do-you-trigger-a-pipeline-webhooks-polling-schedules-and-upstream-jobs.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Version Control](./README.md) · [All topics](../README.md)
