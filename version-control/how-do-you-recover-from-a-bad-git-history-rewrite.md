---
title: "How do you recover from a bad Git history rewrite?"
id: 305
category: "Version Control"
difficulty: "Advanced"
tags:
  - devops
  - version-control
  - interview-questions
---

# How do you recover from a bad Git history rewrite?

**Short answer:** Stop writing to the repository, then recover from a copy of the old object graph - almost always the **reflog** on any clone that still has it, or a `git fsck --lost-found` walk of dangling commits. The rule that makes this survivable: Git does not delete commits on a rewrite, it just stops referencing them, so as long as garbage collection has not run and _some_ clone still points at the old objects, you can restore the branch to its previous commit. Then fix the cause - protect the branch, ban force-push to shared branches, and require `--force-with-lease` where force-push is legitimate.

## Detail

**First: freeze.** Lock the branch or the repository so nothing else pushes on top of the damage, and tell the team to stop pulling - a `git pull` after a bad rewrite rewrites their local branches too and destroys the copies you are about to need. Then ask _who has the old history_: someone who has not fetched since the rewrite is holding a complete backup in their clone, and that is usually the fastest path to recovery.

**Find the pre-rewrite commit.** In order of ease:

1. **Reflog.** `git reflog show main` (or `git reflog` for `HEAD`) lists every position the ref has held locally, with the reason. `main@{1}` is where it was before the last move. Reflogs are per-clone and local, so check the machine of the person who did the rewrite _and_ anyone who had fetched previously. On a self-hosted server, the bare repo may also have reflogs enabled.
2. **Dangling objects.** `git fsck --full --no-reflogs --unreachable --lost-found` lists unreachable commits; `git log --graph <sha>` lets you identify the right one. This works even when a reflog entry has expired, as long as `git gc` has not pruned the objects.
3. **The forge.** GitHub, GitLab, and Bitbucket all record ref updates: GitHub's events API and the "Activity" view show force-pushes with before/after SHAs, and a pull request page keeps the old commit SHAs in its timeline even when the branch no longer points at them. GitLab and Bitbucket have similar audit data. An SHA from any of these is enough - the objects usually still exist server-side.
4. **CI logs.** Every pipeline run records the commit SHA it built. That is a free, durable record of the history that existed.
5. **A backup or mirror.** `git clone --mirror` backups, or the forge's own backup/restore support - the slowest option, and the one you use when the objects really are gone.

**Restore.** Once you have the SHA, reset the branch and push it back. On a shared branch, prefer restoring it to the exact previous SHA rather than trying to merge - reconstructing by hand is how people lose the second half of the work. If commits legitimately landed _after_ the bad rewrite, cherry-pick them onto the restored branch rather than discarding them.

**The specific cases, because they differ:**

- **Force-pushed over other people's commits.** The lost commits are the ones in the old head that are not in the new one: `git log --oneline <new>..<old>`. Restore the old head, then replay any legitimate new work.
- **A bad rebase or interactive rebase.** `ORIG_HEAD` is set to the pre-rebase position, so `git reset --hard ORIG_HEAD` is usually the entire fix. `git rebase --abort` works if you are still mid-rebase.
- **A branch deleted.** The reflog for `HEAD` still shows it (`git reflog | grep <branch>`); recreate with `git branch <name> <sha>`.
- **`git reset --hard` losing uncommitted work.** Uncommitted changes are genuinely gone - unless they were staged, in which case `git fsck --lost-found` will find the dangling blobs. This is the one case where Git cannot usually help you, and it is worth saying so.
- **`filter-branch` / `filter-repo` run on the wrong scope.** Every SHA changed, so every clone and every open pull request is now inconsistent. Restore from a mirror, then redo the filter correctly on a fresh clone, and coordinate a single cutover with the team.

**Then prevent it.** Recovery is a skill; not needing it is a configuration:

- **Branch protection** on `main` and release branches: no force-push, no deletion, required reviews and status checks. This alone removes the most common cause.
- **`--force-with-lease` instead of `--force`** for the legitimate case of updating your own feature branch - it refuses the push if the remote moved since you last fetched, which is precisely the accident you are trying to avoid. Set `push.useForceIfIncludes` and make it a team habit.
- **Extend the safety net**: raise `gc.reflogExpire` and `gc.reflogExpireUnreachable` so the reflog is a longer-lived backup, and keep a scheduled `git clone --mirror` of important repositories somewhere outside the forge.
- **Never rewrite published history** on a shared branch. If you must (a leaked secret, a huge file), do it as an announced, coordinated event with a mirror taken first - and remember that rewriting to remove a secret does not un-leak it: rotate the credential, because the old objects may persist in forks, caches, and clones.

## Example

```bash
# 0. Freeze. Lock the branch in the forge, tell the team to stop pulling.
gh api -X PUT repos/acme/app/branches/main/protection/enforce_admins   # or the UI

# 1. Reflog: the fastest recovery, on any clone that has not fetched since.
git reflog show main
# 8f2a1c9 main@{0}: update by push          <- the bad rewrite
# a91b3de main@{1}: fast-forward            <- what we want
git log --oneline a91b3de..8f2a1c9   # what the rewrite added
git log --oneline 8f2a1c9..a91b3de   # what it destroyed - the important list

# 2. No reflog entry? Walk the dangling objects.
git fsck --full --no-reflogs --unreachable --lost-found | grep commit
git log --graph --oneline <candidate-sha> | head -20   # identify the right one

# 3. Or get the SHA from the forge's record of the force-push.
gh api repos/acme/app/events --jq \
  '.[] | select(.type=="PushEvent" and .payload.forced==true)
       | {ref: .payload.ref, before: .payload.before, head: .payload.head, at: .created_at}'

# 4. Restore the branch to its previous state.
git checkout main
git reset --hard a91b3de
git push --force-with-lease origin main    # lease, so you cannot repeat the mistake

# 5. Replay anything legitimate that landed after the rewrite.
git cherry-pick 8f2a1c9^..8f2a1c9
```

```bash
# The common single-command fixes, worth knowing cold.
git reset --hard ORIG_HEAD      # undo a bad rebase / merge / pull
git rebase --abort              # still mid-rebase
git branch recovered <sha>      # resurrect a deleted branch from the HEAD reflog
git reflog | grep -i 'feature/payments'
git stash list                  # people forget their work may be here
```

```bash
# Prevention: configuration, not discipline.
gh api -X PUT repos/acme/app/branches/main/protection --input - <<'JSON'
{ "required_status_checks": {"strict": true, "contexts": ["ci"]},
  "enforce_admins": true,
  "required_pull_request_reviews": {"required_approving_review_count": 1},
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false }
JSON

git config --global alias.pushf 'push --force-with-lease'   # make the safe way the easy way
git config --global gc.reflogExpire '180 days'
git config --global gc.reflogExpireUnreachable '90 days'

# An off-forge backup, because the forge is a single point of failure too.
git clone --mirror git@github.com:acme/app.git && \
  (cd app.git && git remote add backup s3://... && git push --mirror backup)
```

## Interview tips

- Say "freeze first" before any recovery command. Letting the team keep pulling destroys the copies you need, and most candidates skip straight to `git reflog`.
- Explain the underlying fact: a rewrite does not delete commits, it just unreferences them - which is why reflog and `fsck` work at all. That mechanism is what is being tested.
- Know that reflogs are per-clone and local, so the recovery may live on a colleague's laptop or in CI logs. It is a detail that shows real experience.
- `git reset --hard ORIG_HEAD` for a bad rebase is the single most useful command in this area. Have it ready.
- Be honest about the one unrecoverable case: uncommitted, unstaged work after `git reset --hard` is gone.
- `--force-with-lease` over `--force` is the prevention answer interviewers want, along with branch protection.
- Add that rewriting history to remove a secret does not un-leak it - rotate the credential. That is the security-aware answer and it consistently scores well.

---

[⬅ Back to Version Control](./README.md) · [All topics](../README.md)
