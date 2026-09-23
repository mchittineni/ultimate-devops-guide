---
title: "What are Git Hooks and how are they used with pre-commit frameworks to enforce quality gates?"
id: 582
category: "Version Control"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - git
  - git-hooks
  - pre-commit
  - automation
quiz:
  stem: "Why can an organization NOT rely solely on local Git `pre-commit` hooks to enforce mandatory security scanning policies?"
  options:
    - "Git hooks cannot run security tools"
    - "Developers can easily bypass client-side hooks using the `--no-verify` flag or forget to install them locally"
    - "Pre-commit hooks only run on Linux servers"
    - "Git hooks require enterprise licenses"
  answer: 2
  explanation: "Client-side hooks are advisory; developers can bypass them using `git commit --no-verify`. Mandatory security controls must always be duplicated in server-side CI pipelines."
---

# What are Git Hooks and how are they used with pre-commit frameworks to enforce quality gates?

**Short answer:** Git hooks are custom shell scripts triggered at key execution points (pre-commit, commit-msg, pre-push); frameworks like `pre-commit` manage multi-language hooks to catch formatting errors, secret leaks, and lint issues before code is committed.

## Detail

Git hooks live in `.git/hooks/` and run locally on developer machines.

### Common Hooks

- **`pre-commit`**: Runs linters, formatters (`black`, `prettier`), and secret scanners (`gitleaks`) before the commit is created. If any check exits non-zero, the commit is aborted.
- **`commit-msg`**: Validates commit message formatting (e.g. enforcing Conventional Commits `feat: ...` or requiring a Jira ticket ID).
- **`pre-push`**: Runs fast unit tests before pushing to the remote.

### The `pre-commit` Framework

Because `.git/hooks/` is not tracked by Git, teams cannot commit hooks directly into source control. The `pre-commit` tool solves this by tracking hooks in a versioned `.pre-commit-config.yaml` file and installing them automatically via `pre-commit install`:

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.1
    hooks:
      - id: gitleaks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: check-yaml
      - id: end-of-file-fixer
```

Pin every `rev` to a tag (or a commit SHA for stronger supply-chain guarantees) and let `pre-commit autoupdate` or Renovate propose bumps - a hook repository is third-party code executing on every developer machine.

### Trade-offs

Client-side hooks are a convenience, not a control: they are optional to install, skippable with `--no-verify`, and slow hooks train people to skip them. So the same checks run again in CI (`pre-commit run --all-files`), and the enforcement point is the server: required status checks, branch protection or rulesets, and secret push protection on the forge.

## Example

```bash
pip install pre-commit
pre-commit install                          # writes .git/hooks/pre-commit
pre-commit install --hook-type commit-msg   # for commit-message hooks
pre-commit run --all-files                  # run everything once, as CI will
pre-commit autoupdate                       # propose newer pinned revs
```

```yaml
# .github/workflows/pre-commit.yml - the enforcement copy of the local hooks
name: pre-commit
on: [pull_request]
jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: "3.13"
      - run: pip install pre-commit && pre-commit run --all-files --show-diff-on-failure
```

## Interview tips

- Name the common hooks and when they fire: `pre-commit`, `commit-msg`, `pre-push` (client), `pre-receive`/`update` (server).
- Explain why `.git/hooks` does not travel with the repository and how frameworks (pre-commit, Husky, lefthook) or `core.hooksPath` fix that.
- Say plainly that hooks are bypassable, so CI and branch protection are the real gate.
- Keep hooks fast and scoped to staged files; mention pinning hook revs as a supply-chain concern.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Semantic Release and how does it automate versioning and changelogs from commits?]] (`#540`): [What is Semantic Release and how does it automate versioning and changelogs from commits?](../cicd/what-is-semantic-release-and-how-does-it-automate-versioning-and-changelogs-from-commits.md)
- [[What is Packer and how does it automate immutable golden machine image generation across clouds?]] (`#632`): [What is Packer and how does it automate immutable golden machine image generation across clouds?](../devops-tools-and-automation/what-is-packer-and-how-does-it-automate-immutable-golden-machine-image-generation-across-clouds.md)
- [[What is the difference between trunk-based development and GitFlow in modern continuous delivery?]] (`#537`): [What is the difference between trunk-based development and GitFlow in modern continuous delivery?](../cicd/what-is-the-difference-between-trunk-based-development-and-gitflow-in-modern-continuous-delivery.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Version Control](./README.md) · [All topics](../README.md)
