---
title: "How do you version releases with Git tags, and how do you fix a tag that is already pushed?"
id: 799
category: "Version Control"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - version-control
  - git
  - release-management
  - semantic-versioning
quiz:
  stem: "You pushed tag v2.3.0, the release pipeline published artefacts from it, and then you found a bug. What is the recommended fix?"
  options:
    - "Check out the tag, commit the fix on it, and push the tag again"
    - "Merge the fix and release it under a new tag such as v2.3.1, leaving v2.3.0 pointing at the original commit"
    - "Run git tag -f v2.3.0 on the fixed commit and force-push it so everyone gets the fix automatically"
    - "Delete the remote branch the tag was created from so the tag disappears"
  answer: 2
  explanation: "A tag is a named pointer to a commit and cannot be edited. It can be moved with git tag -f and a force push, but clones that already fetched it keep the old commit and published artefacts no longer match the tag. Fixing forward with a new patch version keeps every version reproducible."
---

# How do you version releases with Git tags, and how do you fix a tag that is already pushed?

**Short answer:** Mark each release with an **annotated tag** following semantic versioning (`v1.4.0`), created on the exact commit CI built, pushed explicitly, and used by the release pipeline to name its artefacts. A tag is a ref, a named pointer to one commit, so it cannot be "edited". If a tagged release turns out to be broken, **fix forward**: merge the fix and tag a new patch version (`v1.4.1`). Tags _can_ be moved (`git tag -f` plus a force push) or deleted, but once a tag is published that breaks reproducibility for everyone who fetched it or built from it, so treat published tags as immutable and enforce it with tag protection.

## Detail

### Tags as release identifiers

A tag gives a human-readable name to a commit. There are two kinds:

- **Lightweight tags** are just a ref, with no metadata of their own. Fine for private bookmarks.
- **Annotated tags** are full Git objects with a tagger, date, message, and optionally a signature (`git tag -s`). Use these for releases: `git describe` uses them by default, they record who cut the release and when, and they can be signed and verified.

Most teams pair tags with **semantic versioning**: `MAJOR.MINOR.PATCH`, where a breaking change bumps major, a backwards-compatible feature bumps minor, and a fix bumps patch. The tag is what the pipeline keys on: a `push` of a `v*` tag triggers the release workflow, which builds once and publishes the image, package, and release notes under that version. Tools such as semantic-release or release-please can derive the next version from Conventional Commit messages, so humans do not pick numbers by hand.

Two practical details trip people up:

- **Tags are not pushed by default.** `git push` sends branches; a tag needs `git push origin v1.4.0` (or `--follow-tags`, which pushes annotated tags reachable from the pushed commits).
- **Tag the commit that was tested**, typically the merge commit on `main` or the release branch that CI already built, not whatever is checked out locally.

### "Editing" a tag that is already pushed

You cannot commit "into" a tag. Checking out a tag gives a detached `HEAD`; a new commit there belongs to no branch and the tag still points at the old commit. What you can do:

| Option                    | Commands                                                       | Consequence                                                                                                                                         |
| ------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Fix forward** (default) | merge the fix, `git tag -a v1.4.1`, push                       | Every version stays reproducible; clear audit trail                                                                                                 |
| **Move the tag**          | `git tag -f -a v1.4.0 <sha>`, `git push --force origin v1.4.0` | Clones that already have `v1.4.0` keep the old commit (`git fetch` will not overwrite an existing tag without `--force`); artefacts no longer match |
| **Delete and recreate**   | `git push origin --delete v1.4.0`, then tag and push again     | Same problems as moving, plus a window where the version does not exist                                                                             |

Moving a published tag causes real damage downstream:

- Anyone who built from `v1.4.0` now has a binary that no longer matches the tag's source.
- Immutable registries refuse to republish the version: an ECR repository with tag immutability will not accept a second `1.4.0` image, and package registries such as npm and PyPI never allow a version to be reused.
- Go modules record checksums for each version in a public checksum database, so a moved tag makes builds fail verification.
- Release tooling, changelogs, and lockfiles that reference the version silently point at different code.

Moving or deleting a tag is acceptable only when nobody has consumed it yet, for example a tag pushed by mistake seconds ago with no release run, or one that must be removed because it pointed at a commit containing a leaked secret (and then you rotate the secret too).

### Preventing the problem

- **Protect release tags.** A tag ruleset on GitHub (or protected tags on GitLab) can restrict who may create `v*` tags and block updates and deletions, so a force-push of a release tag is rejected.
- **Only CI cuts releases.** The release job creates and pushes the tag after tests pass, so tags are never created from someone's laptop.
- **Make registries immutable too.** Tag immutability on the image registry means the artefact side cannot drift from the Git side.
- **Release candidates** (`v1.5.0-rc.1`) give QA something to test before the final tag, so fewer bugs are found after the real release.

## Example

```bash
# Cut a release from the commit CI built on main
git switch main && git pull --ff-only
git tag -a v1.4.0 -m "Release 1.4.0" 3f9c2ab
git push origin v1.4.0                      # tags are not pushed by plain `git push`

# A bug is found after release: fix forward, do not touch v1.4.0
git switch -c fix/config-default v1.4.0
git commit -am "fix: correct default timeout"
# ...PR, CI, merge to main (or to the release branch)...
git switch main && git pull --ff-only
git tag -a v1.4.1 -m "Release 1.4.1: fix default timeout"
git push origin v1.4.1

# Inspect what a tag points at
git show --no-patch v1.4.0                  # tagger, date, message, target commit
git describe --tags                         # e.g. v1.4.1-3-g8e1d2c4 on later commits
git ls-remote --tags origin 'v1.4.*'        # what the remote actually has
```

```bash
# Only for a tag that nobody has consumed yet (wrong commit, pushed seconds ago)
git tag -f -a v1.4.0 -m "Release 1.4.0" <correct-sha>
git push --force origin v1.4.0
# Anyone who already fetched it must run: git fetch --tags --force
```

## Interview tips

- Lead with the model: a tag is a pointer to a commit, so it cannot be edited. A common wrong answer is "check out the tag, change the code, and push it again". That creates a detached commit and leaves the tag where it was.
- Show you know both halves: technically a tag can be moved with `git tag -f` and a force push, and deleted with `git push origin --delete`, but best practice is to fix forward with a new patch version. Saying only one half sounds either naive or dogmatic.
- Explain _why_ moving is harmful: existing clones keep the old commit, artefacts and lockfiles no longer match, and immutable registries refuse the duplicate version.
- Mention annotated (ideally signed) tags for releases, and that tags must be pushed explicitly.
- Close with prevention: tag rulesets blocking updates and deletions of `v*`, release tags created only by CI, and registry tag immutability.
- Likely follow-up: "how do you hotfix a release when `main` has moved on?" Branch from the release tag, fix, tag a patch version, and merge the fix back. See [what is Git branching strategy](./what-is-git-branching-strategy.md) and [how Git stores commits and annotated tags](./how-does-git-internally-store-data-using-blobs-trees-commits-and-annotated-tags.md).

**Telling it as a STAR story** (an adaptable example)

- **Situation:** A `v2.3.0` tag triggered the release pipeline, which published an image and a GitHub release, and an hour later QA found a configuration bug.
- **Task:** A developer wanted to "edit the tag" to include the fix; decide how to ship the fix without breaking anything downstream.
- **Action:** Explained that a tag is only a ref: it can be moved with a force push but not edited, and moving it here would break things, because the `2.3.0` image already existed in an immutable registry and other services had pinned it. Merged the fix, created an annotated `v2.3.1` tag, pushed it, and marked the `v2.3.0` release notes as superseded. Then added a tag ruleset blocking updates and deletions of `v*` tags.
- **Result:** The fixed release shipped within 30 minutes with a clean audit trail, and there was never again any doubt about which commit a version referred to.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)
- [[How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?]] (`#455`): [How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?](../cicd/how-do-you-trigger-a-pipeline-webhooks-polling-schedules-and-upstream-jobs.md)
- [[How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?]] (`#402`): [How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?](../cicd/how-do-you-troubleshoot-a-jenkins-pipeline-that-never-starts-or-hangs-in-the-queue.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Version Control](./README.md) · [All topics](../README.md)
