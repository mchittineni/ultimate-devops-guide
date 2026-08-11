---
title: "How do you keep dependencies up to date without breaking the build?"
id: 401
category: "CI/CD"
difficulty: "Intermediate"
tags:
  - devops
  - cicd
  - interview-questions
  - devsecops
  - version-control
---

# How do you keep dependencies up to date without breaking the build?

**Short answer:** Automate the upgrade into small, continuous, reviewable pull requests rather than a quarterly "upgrade everything" project. Concretely: **pin exact versions with a committed lockfile** so builds are reproducible, run a bot (Renovate or Dependabot) that opens one pull request per dependency on a schedule, let CI prove each one, **group and auto-merge low-risk updates** (patches, dev tooling, lockfile-only) while requiring human review for majors, and hold the line with a **deprecation and SCA gate** so nothing rots silently. Big-bang upgrades break builds; small continuous ones do not.

## Detail

### Why builds break on dependencies at all

Three distinct failures get conflated:

1. **Non-reproducibility** - a floating range (`^1.4.0`, `~=2.1`, `latest`) resolved differently today than yesterday, so the build changed without a commit. Fix by committing a lockfile and installing with the frozen flag (`npm ci`, `pnpm install --frozen-lockfile`, `pip-sync`, `poetry install`, `go mod tidy` + committed `go.sum`, `mvn -B` with fixed parent versions). Pin base images by tag _and_ digest, and pin CI actions by commit SHA.
2. **A breaking change on upgrade** - the new version genuinely changed behaviour. Fix with small increments and a real test suite; that is what the pull-request-per-dependency model buys you.
3. **Rot** - a dependency was removed from the registry, the API it calls was decommissioned, or the transitive tree pulls something that no longer builds on the current toolchain. This is what "the build failed and nobody changed anything" usually means, and it is caused by _not_ upgrading.

### The mechanism

- **A bot on a schedule.** Renovate or Dependabot, running off-peak, one pull request per dependency with the changelog in the description. Cap open pull requests (say ten) so the queue stays reviewable.
- **Grouping by risk.** Group dev dependencies, linters, and type definitions into a single weekly pull request. Group monorepo-published families (all `@aws-sdk/*`, all Spring modules) so they move together - split families are a common cause of breakage. Keep runtime majors separate and individual.
- **Auto-merge the boring ones.** Patch and minor updates for dev tooling, plus lockfile-only refreshes, can merge automatically when CI is green. This is only safe if the suite is trustworthy - which is why flakiness is a prerequisite, not a separate concern. See [how do you deal with flaky tests in a CI pipeline](./how-do-you-deal-with-flaky-tests-in-a-ci-pipeline.md).
- **A cooldown on brand-new releases.** Renovate's `minimumReleaseAge` (a few days) avoids both the yanked release and, more importantly, the compromised-package window that supply-chain attacks depend on.
- **Majors get a human and a plan.** Read the migration guide, do it in its own branch, run the integration suite, and expect application changes. If a major blocks on a large refactor, ticket it with an owner rather than leaving a stale pull request open for six months.

### The gates that stop silent rot

- **Fail the build on known-vulnerable dependencies** with an SCA scanner, but prioritise on exploitability and reachability rather than raw CVE count, or the gate gets ignored. See [how do you prioritise vulnerabilities without blocking delivery](../devsecops/how-do-you-prioritise-vulnerabilities-without-blocking-delivery.md).
- **Track deprecation warnings** as build output you actually read. A warning today is a broken build after the next major.
- **Generate an SBOM** per build so you can answer "are we affected?" in minutes rather than days when the next Log4Shell lands. See [what is a software bill of materials](../devsecops/what-is-a-software-bill-of-materials-sbom.md).
- **Keep the toolchain itself declared and current** (`.tool-versions`, `.nvmrc`, base image digests) - language runtimes reaching end of life are the upgrade people postpone longest and regret most.

### When a bot pull request fails CI

Read it as information, not noise. Triage in this order: is the failure in the dependency's own behaviour (a genuine breaking change - read the changelog), in a transitive peer conflict (resolve or pin the peer), in your own test making an assumption about internals (fix the test), or is it flaky (fix the flake). Closing bot pull requests unread is how a codebase arrives at a 200-version-behind framework and an unavoidable six-week upgrade project.

## Example

```json5
// renovate.json - continuous small upgrades, grouped by risk
{
  extends: ["config:recommended"],
  schedule: ["after 9pm on sunday"],
  prConcurrentLimit: 10,
  minimumReleaseAge: "3 days", // avoids yanked and freshly-compromised releases
  lockFileMaintenance: { enabled: true, automerge: true },
  packageRules: [
    {
      matchDepTypes: ["devDependencies"],
      matchUpdateTypes: ["patch", "minor"],
      groupName: "dev tooling",
      automerge: true,
    },
    { matchPackagePatterns: ["^@aws-sdk/"], groupName: "aws sdk" },
    { matchUpdateTypes: ["major"], automerge: false, labels: ["major-upgrade"] },
    { matchPackageNames: ["node"], matchUpdateTypes: ["major"], enabled: false },
  ],
}
```

```bash
# Find out how bad it is before automating anything
npm outdated                      # or: pip list --outdated, mvn versions:display-dependency-updates
npm audit --omit=dev              # known vulnerabilities in the runtime tree
npx depcheck                      # dependencies you can simply delete - the cheapest upgrade

# Prove the upgrade, do not hope for it
npm ci && npm test                # frozen lockfile: exactly what CI will install
```

## Interview tips

- Frame it as "small and continuous beats big and periodic", and say why: a one-dependency pull request has an obvious culprit when CI fails, whereas a 200-dependency upgrade has none.
- Distinguish _pinning_ from _not upgrading_. Pinning makes builds reproducible; refusing to upgrade makes them rot. Candidates often conflate the two.
- Name the auto-merge boundary explicitly (dev tooling patches yes, runtime majors no) - it shows you have run this rather than read about it.
- Mention the release cooldown and its security rationale. It is a detail that lands well with security-minded interviewers.
- Point out that auto-merge requires a trustworthy test suite, so flaky tests are a blocker for this whole strategy.
- Close on the deleted dependency: the fastest way to fix a vulnerable or broken dependency is often to remove it. `depcheck` and a hard look at the tree beat any upgrade.
- Tie it to security posture with SBOM plus SCA, and to [what is the difference between SAST, DAST, IAST, and SCA](../devsecops/what-is-the-difference-between-sast-dast-iast-and-sca.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you rotate secrets without downtime?]] (`#429`): [How do you rotate secrets without downtime?](../devsecops/how-do-you-rotate-secrets-without-downtime.md)
- [[How do you troubleshoot a GitOps pipeline that will not sync?]] (`#428`): [How do you troubleshoot a GitOps pipeline that will not sync?](../devops-tools-and-automation/how-do-you-troubleshoot-a-gitops-pipeline-that-will-not-sync.md)
- [[How do you manage build artefacts with Nexus or Artifactory?]] (`#460`): [How do you manage build artefacts with Nexus or Artifactory?](../devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
