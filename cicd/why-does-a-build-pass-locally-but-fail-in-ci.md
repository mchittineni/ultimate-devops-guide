---
title: "Why does a build pass locally but fail in CI?"
id: 397
category: "CI/CD"
difficulty: "Intermediate"
tags:
  - devops
  - cicd
  - interview-questions
  - docker
  - configuration-management
---

# Why does a build pass locally but fail in CI?

**Short answer:** Because the two environments differ in something you did not declare. The usual culprits, in the order they occur: **uncommitted or untracked files** on the developer machine, **unpinned dependencies** resolving to different versions, a **different toolchain version** (JDK, Node, Python, compiler), **missing environment variables or credentials**, **filesystem and locale differences** (case sensitivity, path separators, timezone), **missing system packages**, and **test-order or concurrency assumptions** that only break on a clean, parallel runner. The permanent fix is to make the build environment declared and identical - a container image or devcontainer used both locally and in CI - so "works on my machine" stops being possible.

## Detail

### The diagnostic sequence

1. **Read the CI log for the first error, not the last.** A missing dependency at the start often produces fifty misleading failures later.
2. **Check what CI actually checked out.** `git status --porcelain` locally frequently reveals an untracked file the build depends on. A shallow clone, a missing submodule, or missing LFS objects produce the same symptom.
3. **Print the environment in the job.** Tool versions, `env` (masked), working directory, disk, CPU count, locale, timezone. Most "mystery" failures are visible in this one diff against your laptop.
4. **Reproduce CI locally, not the reverse.** Run the exact CI command inside the exact CI image: `docker run --rm -v "$PWD":/src -w /src <ci-image> <the command>`. If it fails there, you have a reproducible bug; if it passes, the difference is in the runner's state or credentials.
5. **Then bisect the difference** - pin one variable at a time (toolchain version, dependency lockfile, env var) until the failure moves.

### The root causes and their permanent fixes

- **Unpinned dependencies.** A range like `^1.4.0` resolves to 1.7.2 on the runner and 1.4.1 in your months-old cache. Commit the lockfile and install with the frozen flag (`npm ci`, `pnpm install --frozen-lockfile`, `pip install -r requirements.txt` from a compiled `requirements.lock`, `mvn -B` with a fixed parent). Do the same for base images: pin by tag _and_ digest.
- **Different toolchain version.** Declare it in the repository (`.nvmrc`, `.tool-versions`, `.python-version`, Gradle toolchains, `pom.xml` release level) and have CI read that file rather than hard-coding a version in the pipeline.
- **Local state you forgot about.** A globally installed CLI, a `~/.npmrc` token, a stale build directory, an already-running database, a hosts-file entry. CI starts clean; that is a feature, and it is telling you the build has undeclared inputs.
- **Missing secrets or configuration.** CI has no `.env`. Fail fast with a clear message when a required variable is absent, and inject values from the secret store rather than the repository. See [how do you prevent and handle secret leaks in CI/CD pipelines](./how-do-you-prevent-and-handle-secret-leaks-in-ci-cd-pipelines.md).
- **Filesystem and platform differences.** macOS is case-insensitive; Linux runners are not, so `import ./Utils` compiles locally and fails in CI. Line endings, file permissions lost through zips, `$TZ` defaulting to UTC and breaking a date test, and a different locale changing sort order all belong to this family.
- **Missing system packages or build tools.** Native extensions need compilers and headers that your laptop acquired years ago. Install them explicitly in the image, not ad hoc in the job.
- **Test-order and concurrency.** A clean database, a parallel test runner, and one CPU instead of ten expose shared-state assumptions. Fixed ports collide; `localhost` services do not exist. This is usually a real bug in the tests. See [how do you deal with flaky tests in a CI pipeline](./how-do-you-deal-with-flaky-tests-in-a-ci-pipeline.md).
- **Resource limits.** A container with 2 GB of memory OOM-kills a bundler that has 32 GB locally, and the log shows only "killed" or exit code 137.

### The structural fix

Run the build inside the same declared image everywhere - a `Dockerfile` or devcontainer that CI uses and developers run through one `make` target. Add a pre-merge job that builds from a **fresh clone in a clean container** so undeclared inputs cannot survive a review. This turns environment drift from a recurring debugging cost into a build-time error.

## Example

```bash
# 1. What does CI see that I do not? Untracked/ignored files the build needs.
git status --porcelain
git clean -ndx            # dry run: what a clean checkout would delete

# 2. Reproduce the CI environment exactly, then run the CI command in it.
docker run --rm -it -v "$PWD":/src -w /src node:20.11.1-bookworm \
  bash -lc 'npm ci && npm test'

# 3. Diff the two environments where the failures usually hide.
node --version; npm --version; echo "$TZ"; locale; nproc; free -m
```

```yaml
# The environment declared in the repository, read by CI - not duplicated in it
# .tool-versions (asdf/mise), consumed by the pipeline step below
# nodejs 20.11.1
# python 3.12.2
# terraform 1.7.5

steps:
  - uses: actions/checkout@v4
    with: { fetch-depth: 0, submodules: recursive, lfs: true }
  - run: |
      test -f .tool-versions || { echo "toolchain not declared"; exit 1; }
      : "${DATABASE_URL:?DATABASE_URL is required - configure it in CI settings}"
  - run: npm ci && npm test    # frozen lockfile: same versions as the developer
```

## Interview tips

- Answer with the principle first: the build has an **undeclared input**, and CI is the clean room that found it. That framing is what interviewers are listening for.
- Give the reproduce-in-the-image step early. Candidates who say "I would add debug logging and re-run the pipeline twenty times" reveal how they actually work.
- Have two concrete war stories ready - case sensitivity on Linux and an unpinned transitive dependency are the two most relatable.
- Mention exit code 137 and OOM as the failure mode that looks like a compiler bug but is a memory limit.
- Say that the answer is _not_ "make CI more like my laptop" but "make both come from one declared image". Reference [what a Dockerfile is](../docker/what-is-dockerfile.md) and [what is configuration management](../configuration-management/what-is-configuration-management.md).
- Add the guardrail: a fresh-clone-in-clean-container job on every pull request, so drift fails at review rather than at release.

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
