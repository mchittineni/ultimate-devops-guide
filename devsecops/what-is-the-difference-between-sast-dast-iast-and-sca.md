---
title: "What is the difference between SAST, DAST, IAST, and SCA?"
id: 162
category: "DevSecOps"
difficulty: "Intermediate"
tags:
  - devops
  - devsecops
  - interview-questions
---

# What is the difference between SAST, DAST, IAST, and SCA?

**Short answer:** SAST reads your source code without running it, DAST attacks the running application from the outside, IAST instruments the running application to observe code paths while it is exercised, and SCA inventories third-party dependencies and matches them against vulnerability databases. They find different classes of bug, so a mature programme runs all four at different points in the pipeline.

## Detail

| Technique | Needs           | Runs at        | Finds                                             | Weakness                             |
| --------- | --------------- | -------------- | ------------------------------------------------- | ------------------------------------ |
| SAST      | source code     | PR / commit    | injection sinks, unsafe crypto, hardcoded secrets | false positives, no runtime context  |
| DAST      | running app     | staging / prod | authn/authz flaws, misconfig, real exploitability | slow, shallow coverage, no line refs |
| IAST      | agent in app    | test execution | exploitable paths with stack traces               | language-specific, runtime overhead  |
| SCA       | manifest / lock | PR + build     | vulnerable and abandoned dependencies, licenses   | says nothing about your own code     |

**SCA finds most of what actually gets exploited.** The majority of an application's code is third-party. Prefer scanners that read the lock file (exact resolved versions) and, better, ones that flag whether the vulnerable function is actually reachable from your code - reachability analysis is what turns 400 findings into the 12 that matter.

**SAST's cost is triage, not licensing.** Tune the ruleset to your stack, suppress with inline annotations that require a reason, and measure the false-positive rate. An untuned scanner teaches developers to ignore security output.

**DAST needs an authenticated crawl.** Unauthenticated scans hit the login page and stop. Give it credentials, a route inventory (an OpenAPI spec is ideal), and a seeded dataset, or it tests almost nothing.

**Where each belongs:** SCA and SAST on every pull request (fast, incremental); IAST attached to the integration test suite; DAST nightly against a staging environment that resembles production; plus periodic manual penetration testing, which is the only one of these that finds business-logic flaws.

## Example

```bash
# SCA on the lock file, failing on fixable highs only
docker run --rm -v "$PWD:/src" aquasec/trivy:0.55.0 fs /src \
  --scanners vuln --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1

# SAST with a tuned ruleset
semgrep --config p/owasp-top-ten --config ./.semgrep/rules \
  --baseline-commit "$(git merge-base origin/main HEAD)" --error
```

## Interview tips

- The clean one-liner is white-box (SAST) versus black-box (DAST) versus grey-box (IAST), with SCA orthogonal to all three.
- Mention `--ignore-unfixed` and reachability analysis - both show you have fought signal-to-noise in practice.
- Common trap: claiming SAST would have caught Log4Shell. That was a dependency issue, so SCA plus an SBOM is the answer.

---

[⬅ Back to DevSecOps](./README.md) · [All topics](../README.md)
