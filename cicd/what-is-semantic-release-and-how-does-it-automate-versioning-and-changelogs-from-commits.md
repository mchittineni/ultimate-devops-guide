---
title: "What is Semantic Release and how does it automate versioning and changelogs from commits?"
id: 540
category: "CI/CD"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - cicd
  - versioning
  - semver
  - automation
quiz:
  stem: "In a repository configured with Semantic Release, what type of version bump is triggered by a commit containing `BREAKING CHANGE:` in its footer?"
  options:
    - "Patch version bump (e.g. 1.2.3 to 1.2.4)"
    - "Major version bump (e.g. 1.2.3 to 2.0.0)"
    - "Minor version bump (e.g. 1.2.3 to 1.3.0)"
    - "No version bump; the pipeline pauses for manual review"
  answer: 2
  explanation: "Under the Conventional Commits specification, a `BREAKING CHANGE:` footer or `feat!:` prefix signifies backward-incompatible changes, triggering an automated Major version increment."
---

# What is Semantic Release and how does it automate versioning and changelogs from commits?

**Short answer:** Semantic Release analyzes structured Conventional Commits (`feat:`, `fix:`, `feat!:`) on the main branch to automatically calculate the next SemVer version number, generate release notes, and publish packages without human intervention.

## Detail

Manual release versioning is prone to errors, forgotten changelogs, and team arguments about whether a release is minor or patch.

### Conventional Commit Conventions to SemVer Mapping

| Commit Format                                                | SemVer Impact                          | Example                                 |
| ------------------------------------------------------------ | -------------------------------------- | --------------------------------------- |
| `fix: resolve db connection pool leak`                       | **Patch** release (`1.0.0` -> `1.0.1`) | Bug fixes, internal performance patches |
| `feat: add saml authentication support`                      | **Minor** release (`1.0.0` -> `1.1.0`) | New backward-compatible feature         |
| `feat!: drop support for python 3.8` (or `BREAKING CHANGE:`) | **Major** release (`1.0.0` -> `2.0.0`) | Incompatible API changes                |

### The Automated Pipeline

1. Developer merges PR to `main` with Conventional Commits.
2. Semantic Release checks git history since the last release tag.
3. Automatically increments version, generates release notes, tags the commit (`v1.2.0`), creates a GitHub/GitLab release, and publishes to package registries. Committing a `CHANGELOG.md` and bumped `package.json` back to the repository is optional and needs the `@semantic-release/changelog` and `@semantic-release/git` plugins; many teams skip it, because pushing commits from CI back to a protected `main` needs a bypass token.

### How it decides

Each plugin implements a lifecycle step: `commit-analyzer` reads commits since the last release tag and picks the highest bump (any breaking change -> major, else any `feat` -> minor, else any `fix`/`perf` -> patch; `docs`, `chore`, `ci` release nothing); `release-notes-generator` writes the notes; `npm`, `github`, or `gitlab` plugins publish. The last release tag is the state, so the job needs the full Git history and tags (`fetch-depth: 0`).

### Trade-offs

- It only works if commit messages are disciplined; enforce Conventional Commits with commitlint in a hook and in CI (or squash-merge with a validated PR title).
- Fully automatic releases on every merge suit libraries and continuously delivered services; products that batch releases often prefer **release-please**, which opens a release PR you merge when ready.
- Current semantic-release versions require a recent Node.js LTS in CI, even for non-JavaScript projects.

## Example

```json
{
  "branches": ["main", { "name": "next", "prerelease": true }],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/npm",
    "@semantic-release/github"
  ]
}
```

```yaml
# .github/workflows/release.yml
name: release
on:
  push:
    branches: [main, next]
permissions:
  contents: write # create tags and releases
  issues: write # comment on released issues
  pull-requests: write
  id-token: write # npm provenance via OIDC
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0 # the last release tag is the state
      - uses: actions/setup-node@v7
        with:
          node-version: 24
      - run: npm ci
      - run: npx semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## Interview tips

- Map commit types to bumps precisely, including that `docs:`/`chore:` produce no release and that `!` or a `BREAKING CHANGE:` footer forces a major.
- Explain the mechanism: the last Git tag is the version state, which is why shallow clones break it.
- Say where it fails: sloppy commit messages. Pair it with commitlint or validated squash-merge titles.
- Contrast with release-please (release PR, human decides when) - interviewers like hearing when you would _not_ release on every merge.
- Know the edge: semantic-release starts at `1.0.0` and does not model `0.x` development versions; use a prerelease branch (`next`, `beta`) for pre-stable work.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#511`): [What is the difference between Continuous Delivery and Continuous Deployment?](../core-devops-concepts/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)
- [[What do you need to know about Maven as a DevOps engineer?]] (`#461`): [What do you need to know about Maven as a DevOps engineer?](../devops-tools-and-automation/what-do-you-need-to-know-about-maven-as-a-devops-engineer.md)
- [[What is Packer and how does it automate immutable golden machine image generation across clouds?]] (`#632`): [What is Packer and how does it automate immutable golden machine image generation across clouds?](../devops-tools-and-automation/what-is-packer-and-how-does-it-automate-immutable-golden-machine-image-generation-across-clouds.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
