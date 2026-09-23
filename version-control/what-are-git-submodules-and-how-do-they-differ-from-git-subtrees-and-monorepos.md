---
title: "What are Git submodules and how do they differ from Git subtrees and monorepos?"
id: 581
category: "Version Control"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - git
  - submodules
  - monorepo
  - architecture
quiz:
  stem: "Why do software engineering teams frequently experience CI/CD pipeline failures when first integrating Git submodules?"
  options:
    - "Git submodules cannot store binary files"
    - "Standard `git clone` does not fetch submodule contents by default unless explicitly configured with `--recursive` or `git submodule update --init`"
    - "Submodules only function on macOS development machines"
    - "CI runners block network traffic to all submodules"
  answer: 2
  explanation: "By default, cloning a repository containing submodules only checks out empty directories. Pipelines must run `git submodule update --init --recursive` to fetch submodule contents."
---

# What are Git submodules and how do they differ from Git subtrees and monorepos?

**Short answer:** Submodules point to a specific commit SHA of an external repository without embedding its history; Subtrees embed the entire external repository history directly into a subdirectory of the host project; Monorepos place all shared code in a single unified repository.

## Detail

Sharing code across repositories involves distinct architectural trade-offs:

| Strategy           | Mechanism                                                                                                                                         | Pros                                                                      | Cons                                                                                                                                     |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **Git Submodules** | Records the submodule's URL and path in `.gitmodules`, and pins an exact commit as a special "gitlink" entry (mode `160000`) in the parent's tree | Keeps main repo small; clear dependency boundaries                        | Requires `git submodule update --init`; easy to detach HEAD; painful CI cloning                                                          |
| **Git Subtrees**   | Merges the foreign repository's content (full history, or squashed with `--squash`) into a subfolder of the host                                  | Clones like a standard repo; no submodule initialization friction         | Pollutes host history with foreign commits unless squashed; pushing changes back upstream (`git subtree push/split`) is slow and awkward |
| **Monorepo**       | Single repository containing all libraries and services                                                                                           | Atomic cross-service refactoring; single CI pipeline; zero version desync | Repository size balloons; requires specialized build tools (Bazel, Nx, Turborepo)                                                        |

In modern cloud-native engineering, organizations overwhelmingly favor **Monorepos** or language package managers (`npm`, `pip`, `go modules`) over Git submodules due to developer friction with submodules.

Submodules still fit when you genuinely need to pin an exact revision of a separately owned repository that is not published as a package - vendored firmware, a shared schema repository, a large asset repository. The trade-off is that every consumer has to remember `--recurse-submodules`, and updating the pin is an explicit two-repository change.

## Example

```bash
# Add a submodule: .gitmodules gets url/path, the parent tree gets a pinned commit
git submodule add https://github.com/acme/proto.git vendor/proto
git ls-tree HEAD vendor/proto        # 160000 commit 3f9c...  vendor/proto  <- the pin

# Clone correctly (what CI must do)
git clone --recurse-submodules https://github.com/acme/app.git
# or, in an existing clone:
git submodule update --init --recursive

# Move the pin to a newer commit, deliberately
git -C vendor/proto fetch && git -C vendor/proto switch --detach v2.3.0
git add vendor/proto && git commit -m "chore: bump proto to v2.3.0"

# Subtree alternative: copy the content in, squashed, no special clone step
git subtree add --prefix=vendor/proto https://github.com/acme/proto.git v2.3.0 --squash
```

In GitHub Actions, `actions/checkout` needs `with: { submodules: recursive }` (plus a token that can read private submodules), which is the usual cause of CI failures.

## Interview tips

- Explain the mechanism: a submodule is a pinned commit (a gitlink) plus a URL, not a copy of the code.
- Name the classic failures: empty directories after clone, detached HEAD inside the submodule, forgetting to commit the updated pin.
- Contrast subtree (content copied in, simple to clone, awkward to push back) and monorepo (atomic changes, needs build tooling at scale).
- Prefer published packages for shared libraries when versioning semantics matter.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between trunk-based development and GitFlow in modern continuous delivery?]] (`#537`): [What is the difference between trunk-based development and GitFlow in modern continuous delivery?](../cicd/what-is-the-difference-between-trunk-based-development-and-gitflow-in-modern-continuous-delivery.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Version Control](./README.md) · [All topics](../README.md)
