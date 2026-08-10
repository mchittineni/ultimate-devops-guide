---
title: "What is the difference between git fetch, git pull, and git clone?"
id: 499
category: "Version Control"
difficulty: "Beginner"
tags:
  - devops
  - version-control
  - interview-questions
---

# What is the difference between git fetch, git pull, and git clone?

**Short answer:** **`git clone`** creates a new local repository from a remote: it copies the object database, sets up the `origin` remote, creates remote-tracking branches, and checks out the default branch. You do it once. **`git fetch`** downloads new objects and updates **remote-tracking branches** (`origin/main`) **without touching your working tree or your local branches** - it is always safe, because nothing you have is changed or merged. **`git pull`** is `fetch` followed immediately by an integration step in your current branch - `merge` by default, or `rebase` with `--rebase` - so it _does_ change your working tree and can produce conflicts. The practical habit that follows: **`fetch` then look, then integrate deliberately**. `git fetch && git log --oneline HEAD..origin/main` tells you exactly what is about to arrive before you decide whether to merge or rebase, which is why experienced engineers pull far less often than they fetch.

## Detail

### What each command actually does

```text
git clone <url>
   └─ init a repo + add remote "origin" + fetch everything
      + create origin/* tracking branches + checkout the default branch

git fetch origin
   └─ download new objects (commits, trees, blobs, tags)
   └─ move origin/main, origin/feature-x, ...
   └─ your main, your working tree, your index: UNTOUCHED

git pull origin main   ==   git fetch origin  +  git merge origin/main
git pull --rebase      ==   git fetch origin  +  git rebase origin/main
```

|                                              | `clone`                | `fetch`    | `pull`                              |
| -------------------------------------------- | ---------------------- | ---------- | ----------------------------------- |
| Creates a repository                         | Yes                    | No         | No                                  |
| Downloads objects                            | Yes                    | Yes        | Yes                                 |
| Updates remote-tracking refs (`origin/main`) | Yes                    | Yes        | Yes                                 |
| Moves your local branch                      | Yes (initial checkout) | **No**     | **Yes**                             |
| Touches the working tree                     | Yes                    | **No**     | **Yes**                             |
| Can cause a conflict                         | No                     | **No**     | **Yes**                             |
| Safe to run any time                         | N/A                    | **Always** | Not while you have messy local work |
| How often                                    | Once                   | Constantly | Deliberately                        |

The key mental model: your repository holds **two** views of every remote branch - the remote-tracking ref `origin/main` (Git's cached copy of what the server had at last fetch) and your local `main`. `fetch` only updates the first; `pull` updates the first and then tries to move the second onto it.

### Why prefer fetch-then-integrate

- **You see what is coming.** `git log --oneline --graph HEAD..origin/main` and `git diff HEAD...origin/main` before integrating. A pull that surprises you with 40 commits and a conflict in the middle of your own work is avoidable.
- **You choose merge or rebase per situation**, rather than accepting whatever the default is.
- **It never breaks a dirty working tree.** `pull` on uncommitted changes either refuses or leaves you mid-conflict; `fetch` is inert.
- **In scripts and CI it is the correct primitive.** A pipeline should `fetch` and then check out an explicit ref, not `pull` into whatever state the workspace happens to be in.

### `pull --rebase` versus `pull --merge`

`git pull` (merge) creates a **merge commit** when both sides have moved, producing the "Merge branch 'main' of ..." commits that clutter history. `git pull --rebase` replays your local commits on top of the fetched work, giving a linear history and no merge commit - at the cost of rewriting your local commit hashes (fine, because they are not published yet).

The usual team convention: **rebase for your own unpushed work, merge for integrating shared branches.** Set it once so nobody has to remember:

```bash
git config --global pull.rebase true          # pull always rebases
git config --global pull.ff only             # or: refuse to pull unless it fast-forwards
git config --global rebase.autoStash true     # stash/unstash local changes around a rebase
```

`pull.ff only` is worth knowing: it makes `git pull` fail rather than create a surprise merge, forcing you to decide explicitly. Many teams adopt it after one too many accidental merge commits. See [git merge, rebase, and cherry-pick](./what-is-the-difference-between-git-merge-rebase-and-cherry-pick.md).

### `clone` options that matter in CI

Cloning a large repository is often the slowest step in a pipeline, and there are three levers:

- **`--depth 1`** (shallow) - only the latest commit. Fast, but breaks anything needing history: `git describe`, `git blame`, SonarQube's new-code detection, and diffing against a base branch. Deepen later with `--unshallow` if needed.
- **`--filter=blob:none`** (partial/blobless clone) - all commits and trees, blobs fetched on demand. Usually the better CI default: history-aware operations work, and the download is a fraction of the size.
- **`--single-branch`**, **`--no-tags`**, and **`--sparse`** with a sparse-checkout for monorepos where a job needs one directory.

Also: `git clone --bare` (no working tree - what a server holds) and `--mirror` (a bare clone including all refs and configured to mirror), which is the correct tool for migrating a repository between hosts with full history. That is the answer to "how do you move a repo from GitHub to GitLab preserving history?" - `git clone --mirror`, then `git push --mirror` to the new remote, then update the developers' remotes.

### Related commands people mix in

- **`git remote -v`** and `git remote show origin` - which URLs you are actually talking to, and which local branches track what.
- **`git fetch --prune`** (or `fetch.prune=true`) - delete remote-tracking refs for branches that no longer exist on the server. Without it, `origin/*` accumulates dead branches forever, which is the source of "why does this branch still show up?"
- **`git fetch --all --tags`** - all remotes and tags. Tags are not fetched by default in every configuration, which is why a CI job sometimes cannot find the tag it was triggered by.
- **`git pull` versus `git clone`**: only asked to check that you know clone creates the repository and pull updates an existing one.
- **`git push`** is the mirror image of pull: it uploads your commits and moves the remote branch. `--force-with-lease` instead of `--force` is the safe version, because it refuses if someone else has pushed since your last fetch.

### The recurring interview follow-ups

- _"You have a local clone, you changed one file, and you want that change on the remote - which commands in order?"_ → `git status`, `git add <file>`, `git commit -m "..."`, `git fetch origin`, `git rebase origin/main` (or pull --rebase), then `git push origin HEAD` - or on a protected branch, push a feature branch and open a pull request. Mentioning that `main` is usually protected, so the answer is a PR rather than a direct push, is the mature version.
- _"How do you check the difference between two commits?"_ → `git diff a1b2c3 d4e5f6` for content, `--stat` for a summary, `git log a1b2c3..d4e5f6 --oneline` for the commits between them. Note the two-dot versus three-dot distinction: `A..B` is commits reachable from B but not A; `A...B` in `diff` compares B against the merge base, which is what you want when reviewing a branch.
- _"How do you extract all commits from the last three days?"_ → `git log --since="3 days ago" --pretty=format:'%h %an %ad %s' --date=short`, adding `--author` or `-- <path>` to narrow it.

## Example

```bash
# The habit: fetch, inspect, then decide
git fetch --prune origin
git log --oneline --graph --decorate HEAD..origin/main    # what is about to arrive
git diff --stat HEAD...origin/main                        # three dots: vs the merge base
git status -sb                                            # ## main...origin/main [behind 12]

# Now integrate deliberately
git rebase origin/main        # linear history for my unpushed work
# ...or, when integrating a long-lived shared branch:
git merge --no-ff origin/main
```

```bash
# Push one changed file, the way it actually happens on a protected branch
git switch -c fix/timeout-config
git add config/timeouts.yaml
git commit -m "fix(api): raise upstream timeout to 30s"
git fetch origin && git rebase origin/main    # rebase before pushing: no merge commit
git push -u origin HEAD                        # then open a pull request
# direct push to main only if it is unprotected:
#   git push origin main   (and --force-with-lease, never --force, if history was rewritten)
```

```bash
# Set the defaults once, so the team stops arguing about it
git config --global pull.rebase true
git config --global fetch.prune true
git config --global rebase.autoStash true
git config --global push.default simple
git config --global push.autoSetupRemote true

# What am I tracking, and against what?
git remote -v
git branch -vv                                 # local branches and their upstreams
```

```bash
# CI clones: pick the right trade-off
git clone --filter=blob:none --single-branch --branch main "$REPO"   # good default
git clone --depth 1 "$REPO"                    # fastest, but breaks history-aware tooling
git fetch --unshallow                          # recover history if a tool needs it
git fetch origin main --depth 50                # enough history to diff against the base

# Migrate a repository between hosts, preserving everything
git clone --mirror https://github.com/acme/api.git
cd api.git && git push --mirror git@gitlab.example.com:acme/api.git
```

```bash
# Diffs, ranges, and history questions
git diff a1b2c3 d4e5f6 --stat
git log a1b2c3..d4e5f6 --oneline
git log --since="3 days ago" --pretty=format:'%h %an %ad %s' --date=short
git log --since="3 days ago" --author="alice" -- services/api/
```

## Interview tips

- Lead with the one-line distinction and the consequence: `fetch` updates remote-tracking refs only and is always safe; `pull` is `fetch` plus an integration step, so it changes your working tree and can conflict; `clone` creates the repository in the first place.
- Explain the two-refs model - `origin/main` is Git's cached copy of the server, your `main` is yours - because that is what makes the difference obvious rather than memorised.
- Recommend fetch-then-inspect-then-integrate, and show the command you would actually run (`git log HEAD..origin/main`). That is the answer of someone who has been burned by a surprise pull.
- Know that `pull --rebase` avoids the merge commit and that `pull.ff only` makes an unexpected merge fail loudly. Mentioning the config settings you would standardise across a team is a strong signal.
- For the "changed one file, get it to the remote" sequence, give the commands in order **and** note that `main` is normally protected, so the real answer ends in a pull request rather than a push.
- Have the CI clone trade-offs ready: `--depth 1` is fastest but breaks `git describe`, `blame`, and SonarQube new-code detection; `--filter=blob:none` is usually the better default. This is a genuinely useful, rarely-mentioned detail.
- Know `--mirror` for host-to-host migration with full history, and `fetch --prune` for the dead-remote-branch problem.
- Distinguish `A..B` from `A...B` when asked about diffing two commits or reviewing a branch, and use `--force-with-lease` rather than `--force` if force-pushing comes up. See [what is Git](./what-is-git.md), [git merge, rebase, and cherry-pick](./what-is-the-difference-between-git-merge-rebase-and-cherry-pick.md), [how do you undo changes in Git safely](./how-do-you-undo-changes-in-git-safely.md), and [recovering from a bad Git history rewrite](./how-do-you-recover-from-a-bad-git-history-rewrite.md).

---

[⬅ Back to Version Control](./README.md) · [All topics](../README.md)
