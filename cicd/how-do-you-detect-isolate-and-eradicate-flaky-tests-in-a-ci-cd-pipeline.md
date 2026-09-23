---
title: "How do you detect, isolate, and eradicate flaky tests in a CI/CD pipeline?"
id: 536
category: "CI/CD"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - cicd
  - testing
  - flaky-tests
  - reliability
quiz:
  stem: "Why is blindly adding `retry: 3` to failing CI test steps considered an anti-pattern when addressing flaky tests?"
  options:
    - "It causes git merge conflicts automatically"
    - "It masks underlying race conditions and non-deterministic bugs, causing pipeline run times to balloon and real regressions to slip through"
    - "Test runners crash if configured with retries"
    - "Retries violate ISO-27001 compliance standards"
  answer: 2
  explanation: "Blind retries mask real bugs, quadruple build times, and fail to fix the root cause (such as race conditions or state pollution), eventually failing when the flakiness rate increases."
---

# How do you detect, isolate, and eradicate flaky tests in a CI/CD pipeline?

**Short answer:** Flaky tests (tests that non-deterministically pass or fail on the same code commit) are managed by test quarantine suites, randomized test execution ordering, concurrency isolation, and alerting on failure patterns.

## Detail

Flaky tests destroy developer trust in CI: developers ignore failures, hit "re-run" until it passes, and ship real bugs to production.

### Detection

A test is flaky when it both passes and fails on the **same commit**. The only reliable way to see that is data: publish structured results (JUnit XML) for every run, including retries, and compute a per-test flake rate over a rolling window on the default branch. Most CI platforms and test-analytics tools (GitLab's test reports, Buildkite Test Engine, Datadog/Trunk flaky-test tracking, or a simple warehouse query) will do this for you. A nightly job that re-runs the suite several times on an unchanged commit surfaces flakes that normal traffic has not hit yet.

### Root causes of test flakiness

1. **Race conditions and timeouts**: hard-coded `sleep(5)` instead of polling for a condition (`waitForSelector`, Gomega's `Eventually`, Awaitility).
2. **Order dependence**: test B passes only if test A ran beforehand and created database rows.
3. **Shared state**: tests sharing static variables, database tables, temp files, or fixed network ports.
4. **Time and environment**: tests reading the real clock, timezone, locale, or random seed.
5. **External dependencies**: real network calls to third-party APIs, DNS, or package registries.

### Remediation strategy

- **Shuffle test order**: run tests in random order in CI (pytest-randomly, which shuffles automatically once installed, `go test -shuffle=on`, RSpec `--order random`, JUnit 5 `MethodOrderer.Random`) and log the seed so a failing order can be replayed.
- **Automated quarantine**: a test that fails intermittently is moved to a non-blocking quarantine suite and assigned as a bug ticket with an owner and a deadline. Cap the quarantine list, or it becomes a graveyard of tests nobody runs.
- **Retry with metrics**: a single retry at a genuinely unreliable boundary may keep the pipeline moving, but every pass-on-retry must be recorded as a flake event, otherwise the signal that drives fixes disappears.
- **Fix, then return to the gate**: inject clocks, isolate data per test, allocate ports dynamically, and stub external calls; a quarantined test only goes back into the blocking suite after it survives a repeat-run check.

The trade-off: quarantine and retries buy back pipeline trust at the cost of temporarily reduced coverage. That is acceptable only while the debt is visible and owned.

## Example

```bash
# Detect: run the same commit repeatedly and in random order (pytest-repeat + pytest-randomly)
pip install pytest-repeat pytest-randomly
pytest tests/checkout --count=20 -x --junitxml=repeat.xml  # pytest-randomly shuffles by default once installed
# a failure prints "Using --randomly-seed=1234"; replay that exact order:
pytest tests/checkout --randomly-seed=1234

# Isolate: mark the offender and exclude it from the blocking job
#   @pytest.mark.quarantine  # ENG-812, owner @alice, remove by 2026-10-15
pytest -m "not quarantine"            # blocking gate
pytest -m quarantine || true          # non-blocking, results still published

# Go equivalent: shuffle and repeat
go test ./... -shuffle=on -count=10
```

## Interview tips

- Define flakiness precisely: pass and fail on the same commit. That definition is what makes it measurable.
- Lead with detection from data (per-test flake rate across runs), not anecdotes - it is what lets you prioritise.
- Know that the shuffle flag differs per runner; note that `-p no:randomly` _disables_ pytest-randomly, a common mistake in pipelines.
- Say that retries are a tourniquet, not a cure, and must be reported as flakes. Blind `retry: 3` masks real race conditions.
- Quarantine needs an owner, a deadline, and a cap; be willing to delete a test nobody will fix.
- Likely follow-up: "how do you stop new flaky tests getting in?" - repeat-run new or changed tests before merge, and shuffle nightly.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#511`): [What is the difference between Continuous Delivery and Continuous Deployment?](../core-devops-concepts/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)
- [[How do you manage build artefacts with Nexus or Artifactory?]] (`#460`): [How do you manage build artefacts with Nexus or Artifactory?](../devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md)
- [[What is DAST (Dynamic Application Security Testing) and how is OWASP ZAP integrated into CI/CD pipelines?]] (`#709`): [What is DAST (Dynamic Application Security Testing) and how is OWASP ZAP integrated into CI/CD pipelines?](../devsecops/what-is-dast-dynamic-application-security-testing-and-how-is-owasp-zap-integrated-into-ci-cd-pipelines.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
