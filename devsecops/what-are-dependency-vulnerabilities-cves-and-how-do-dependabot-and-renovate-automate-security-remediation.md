---
title: "What are dependency vulnerabilities (CVEs) and how do Dependabot and Renovate automate security remediation?"
id: 708
category: "DevSecOps"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - devsecops
  - cve
  - dependabot
  - renovate
  - dependencies
quiz:
  stem: "How do automated dependency tools (like Dependabot and Renovate) reduce Mean Time to Remediate (MTTR) for critical CVE disclosures?"
  options:
    - "By rewriting application source code into Rust"
    - "By automatically generating pull requests with updated package versions and running CI test suites without waiting for manual developer audits"
    - "By deleting all third-party libraries permanently"
    - "By changing the application's domain name"
  answer: 2
  explanation: "Automated dependency tools detect CVE alerts instantly and open pull requests bumping the vulnerable package version, allowing teams to review and merge patches rapidly."
---

# What are dependency vulnerabilities (CVEs) and how do Dependabot and Renovate automate security remediation?

**Short answer:** CVEs are publicly cataloged software flaws; automated dependency bots (Dependabot, Renovate) monitor package lockfiles, detect vulnerable libraries, and automatically open pull requests with patched versions and changelog summaries.

## Detail

Industry audits routinely find that most of the code in a modern service - often 70-90% - is open-source third-party dependencies (`npm`, `pip`, `maven`, `cargo`). Manually auditing dependencies for security patches is impossible.

### How Automated Dependency Remediators Operate

1. **Cataloging**: Scans repository package manifests (`package-lock.json`, `go.mod`, `pom.xml`).
2. **Vulnerability Matching**: Checks resolved versions against advisory databases (the GitHub Advisory Database, OSV, and the NVD).
3. **Automated PR Generation**: When an advisory is published - for example CVE-2021-3749, a ReDoS in `axios` up to `0.21.1`:
   - Dependabot/Renovate creates a branch and updates `axios` to the first fixed version (`0.21.2`), including the lock file.
   - Automatically opens a Pull Request detailing the CVE severity score (CVSS), release notes, and breaking changes.
4. **CI Integration**: If automated CI tests pass on the PR, teams can configure **automated merging** for minor and patch security updates, eliminating manual toil.

## Example

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended"],
  "minimumReleaseAge": "3 days",
  "vulnerabilityAlerts": { "labels": ["security"], "minimumReleaseAge": null },
  "packageRules": [
    {
      "matchUpdateTypes": ["patch", "minor"],
      "matchCurrentVersion": "!/^0/",
      "automerge": true
    }
  ]
}
```

```yaml
# .github/dependabot.yml - the GitHub-native equivalent
version: 2
updates:
  - package-ecosystem: npm
    directory: /
    schedule: { interval: weekly }
    groups:
      minor-and-patch:
        update-types: [minor, patch]
```

## Interview tips

- Distinguish the two jobs: **security updates** (triggered by an advisory, should be fast) versus **version updates** (routine freshness, can be batched). Both Dependabot and Renovate support both; Renovate is more configurable and works across GitHub, GitLab, Bitbucket, and Azure DevOps.
- Auto-merge is only as safe as your test suite. Limit it to patch/minor updates of stable (1.x+) packages with green CI, and keep majors for human review.
- Mention a release-age delay (`minimumReleaseAge` in Renovate, a cooldown in Dependabot) for routine updates: malicious package versions are usually caught and yanked within days, so not adopting a release in its first hours is cheap protection against compromised publishes. Security fixes bypass the delay.
- Prioritise with exploitability data, not raw CVSS: CISA KEV and EPSS tell you which of the 200 open PRs actually matter this week.
- Know the gap: these bots only see declared dependencies in manifests and lock files - vendored code, base image packages, and binaries need SCA or image scanning as well.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevSecOps](./README.md) · [All topics](../README.md)
