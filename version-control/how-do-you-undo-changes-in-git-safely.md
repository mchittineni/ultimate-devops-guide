---
title: "How do you undo changes in Git safely?"
id: 264
category: "Version Control"
difficulty: "Intermediate"
tags:
  - devops
  - version-control
  - interview-questions
---

# How do you undo changes in Git safely?

**Short answer:** Match the tool to whether the commit is shared. `git revert` creates a new commit that inverts a previous one and is the **only** safe choice on a pushed branch. `git reset` moves the branch pointer and is for local history you have not shared. `git restore` discards working-tree or staged changes without touching commits. And `git reflog` is the safety net that makes almost any mistake recoverable.

## Detail

**The decision is always the same question: has anyone else pulled this?**

| Situation                                         | Command                       |
| ------------------------------------------------- | ----------------------------- |
| Bad commit already pushed to `main`               | `git revert <sha>`            |
| Last few commits are local only, keep the changes | `git reset --soft HEAD~2`     |
| Local commits, discard the changes entirely       | `git reset --hard HEAD~2`     |
| Unstage a file, keep edits                        | `git restore --staged <file>` |
| Throw away uncommitted edits to a file            | `git restore <file>`          |
| Wrong branch, wrong message, nothing pushed       | `git commit --amend`          |

**`git reset` and its three modes** - the distinction interviewers probe:

- `--soft` moves the branch pointer only. Your changes stay staged, ready to recommit. Use it to squash the last few commits into one.
- `--mixed` (the default) moves the pointer and unstages. Changes remain in the working tree.
- `--hard` moves the pointer, unstages, **and** overwrites the working tree. This is the only destructive one, and it discards uncommitted work irreversibly - the reflog can recover commits, not edits you never committed.

**`git revert` is forward-only.** It computes the inverse diff and commits it, so the original commit remains in history and everyone's clone stays consistent. This is why it is the correct answer for production: a bad deploy is rolled back by _adding_ a commit, not by pretending the bad one never existed. Reverting a merge commit needs `-m 1` to say which parent is the mainline - a common follow-up question.

**`git restore` and `git switch` exist because `git checkout` did too much.** `checkout` both changed branches and discarded file changes, which made accidents easy. Modern Git splits them: `switch` for branches, `restore` for file contents. Use them.

**`git clean` handles untracked files,** which `reset --hard` does not touch. Always dry-run first: `git clean -nd`, then `git clean -fd`. Running `-fdx` also removes ignored files - including `.env` files and `node_modules`.

**`git reflog` is the undo for the undo.** Git records every position `HEAD` has held for roughly 90 days, including commits orphaned by a `reset --hard`, a bad rebase, or a deleted branch. If you can find it in the reflog, you can get it back. This is the single most valuable git command to know, and the reason destructive-looking operations on committed work are usually recoverable.

**Removing a secret that was committed is a different problem.** Reverting or amending does not remove the blob from history - it is still reachable from earlier commits, and if it was pushed, it is in every clone and in the hosting provider's cache. You must rewrite history (`git filter-repo`, or BFG Repo-Cleaner), force-push, have everyone re-clone, and - most importantly - **rotate the credential**, because you must assume it is compromised. Rotation is the real fix; history rewriting is cleanup.

## Example

```bash
# Pushed a bad commit to main - revert, never reset
git revert 9f2c1ab
git push origin main

# Reverting a merge commit: -m 1 keeps the first parent as mainline
git revert -m 1 4d5e6f7

# Squash the last 3 local commits into one (nothing pushed)
git reset --soft HEAD~3
git commit -m "feat: add checkout flow"

# Fix the message or add a forgotten file to the last commit
git add forgotten-file.ts
git commit --amend --no-edit

# Unstage without losing edits
git restore --staged src/app.ts

# Discard local edits to one file (irreversible - not in any commit)
git restore src/app.ts

# Remove untracked files - dry run first, always
git clean -nd
git clean -fd

# Recover from a bad reset or rebase
git reflog                     # find the SHA before the mistake
git reset --hard HEAD@{3}
```

## Interview tips

- Open with the deciding question - "is it pushed?" - then give revert for shared, reset for local. That framing is what they are listening for.
- Be able to state the three reset modes and what each touches: pointer, index, working tree.
- `git revert` on a merge commit needs `-m 1`. It is a favourite follow-up because it catches people who have only reverted simple commits.
- Name `git reflog` unprompted. "How would you recover from a `reset --hard`?" is a common trap, and the answer is not "you can't."
- Prefer `git restore`/`git switch` over `git checkout` in your answer - it shows you have kept up since Git 2.23.
- On committed secrets, lead with **rotate the credential**. Candidates who only describe `filter-repo` miss the actual security response.

---

[⬅ Back to Version Control](./README.md) · [All topics](../README.md)
