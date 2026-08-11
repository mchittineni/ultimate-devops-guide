---
title: "How do you use Git hooks for automated linting, testing, and commit validation?"
id: 254
category: "Version Control"
difficulty: "Beginner"
tags:
  - devops
  - version-control
  - interview-questions
---

# How do you use Git hooks for automated linting, testing, and commit validation?

**Short answer:** Use Git hooks (custom scripts executed automatically on Git events like `pre-commit`, `commit-msg`, and `pre-push`) to shift security and quality checks left by automatically formatting code, running linters, enforcing Conventional Commits formatting, and scanning for leaked credentials before code reaches remote repositories.

## Detail

Git hooks are event-driven shell scripts located in `.git/hooks/` that execute automatically during Git lifecycle events:

### 1. Client-Side vs Server-Side Git Hooks

- **Client-Side Hooks:** Executed on developer workstations before commits or pushes.
  - `pre-commit`: Runs linters (ESLint, Flake8), code formatters (Prettier, Black), and secret scanners (`gitleaks`). Aborts commit if checks fail.
  - `commit-msg`: Validates commit message formatting (e.g., Conventional Commits: `feat:`, `fix:`, `docs:`).
  - `pre-push`: Runs fast unit test suites prior to pushing to remote origin.
- **Server-Side Hooks:** Executed on Git remote servers (GitHub Enterprise, GitLab, Bitbucket) before accepting pushes.
  - `pre-receive`: Evaluates pushed commits and rejects branch updates if corporate policies are violated.

### 2. Standardizing Hooks with `pre-commit` Framework & Husky

Git hooks inside `.git/hooks/` are not committed to version control by default. To share hooks across engineering teams:

- **Python `pre-commit` Framework:** Uses `.pre-commit-config.yaml` to pull version-controlled hook plugins, installing hooks automatically during `git init`.
- **Husky (Node.js ecosystem):** Configures client hooks inside `.husky/` directory tracked in Git.

## Example

**1. Shared Python `pre-commit` configuration file (`.pre-commit-config.yaml`):**

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=500']

  - repo: https://github.com/psf/black
    rev: 24.2.0
    hooks:
      - id: black

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v3.1.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args: [feat, fix, chore, docs, style, refactor, perf, test]
```

**2. Executable bash shell script for `pre-commit` hook (`.git/hooks/pre-commit`):

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "Running pre-commit quality checks..."

# Run code formatter check
if ! npx prettier --check "src/**/*.{js,ts,json,md}"; then
    echo "Code formatting errors found! Run 'npx prettier --write .' to fix."
    exit 1
fi

# Run secret scanning
if command -v gitleaks &> /dev/null; then
    gitleaks protect --staged --verbose
fi

echo "Pre-commit checks passed successfully!"
```

## Interview tips

- Highlight why manual `.git/hooks/` scripts fail in team settings: `.git/` folder is ignored by version control. Frameworks like `pre-commit` or `husky` solve this by storing configuration in root project files.
- Mention `git commit --no-verify`: developers can bypass client-side hooks; therefore, server-side CI/CD pipeline checks are still mandatory as a final enforcement gate.
- Connect Git hooks to DevSecOps: running `gitleaks` or `trufflehog` in a `pre-commit` hook prevents secrets from ever entering `.git` history on developer machines.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?]] (`#455`): [How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?](../cicd/how-do-you-trigger-a-pipeline-webhooks-polling-schedules-and-upstream-jobs.md)
- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)
- [[How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?]] (`#402`): [How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?](../cicd/how-do-you-troubleshoot-a-jenkins-pipeline-that-never-starts-or-hangs-in-the-queue.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Version Control](./README.md) · [All topics](../README.md)
