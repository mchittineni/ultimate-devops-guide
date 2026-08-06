---
title: "What is Continuous Integration?"
id: 3
category: "Core DevOps Concepts"
difficulty: "Beginner"
tags:
  - devops
  - core-devops-concepts
  - interview-questions
---

# What is Continuous Integration?

**Short answer:** Continuous Integration is the practice of merging every developer's work into a shared mainline at least daily, where an automated build and test suite verifies each merge within minutes.

## Detail

CI exists to kill integration pain. When branches live for weeks, merging them is a project in itself. When everyone integrates to `main` daily, conflicts are small and defects surface within minutes of being introduced — while the author still has full context.

The practice has hard requirements that tools alone do not provide:

1. A single shared mainline that everyone merges into frequently.
2. Every commit triggers an automated build plus a fast test suite.
3. The build is fast — ten minutes is a common ceiling, because a slow pipeline gets ignored.
4. A broken build is the team's top priority; nobody builds on top of red.
5. Tests are trustworthy. Flaky tests destroy CI faster than no tests.

Feature flags and branch-by-abstraction let teams integrate incomplete work safely, so "not finished" never becomes a reason to hold a long-lived branch.

## Example

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm test -- --coverage
      - run: npm run build
```

## Interview tips

- If asked "do you do CI?", the real question is how long branches live and how fast the build is.
- Mention trunk-based development as the branching model that makes CI genuine.
- Know what you do about flaky tests — quarantine, retry budgets, and a fix deadline.

---

[⬅ Back to Core DevOps Concepts](./README.md) · [All topics](../README.md)
