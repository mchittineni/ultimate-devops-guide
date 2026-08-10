---
title: "How do you deal with flaky tests in a CI pipeline?"
id: 398
category: "CI/CD"
difficulty: "Intermediate"
tags:
  - devops
  - cicd
  - interview-questions
  - devops-culture-and-practices
  - devops-metrics-and-kpis
---

# How do you deal with flaky tests in a CI pipeline?

**Short answer:** Treat flakiness as a defect with an owner, not as background noise. **Measure it** (per-test pass rate across runs, so flakes are visible rather than anecdotal), **quarantine** the worst offenders out of the blocking suite immediately so the pipeline is trustworthy again, **fix the root cause** - almost always time, shared state, ordering, or an unstubbed network call - and only then return the test to the gate. Blanket `retry: 3` is not a fix: it hides real intermittent bugs and doubles your pipeline time.

## Detail

### Why flakiness is a delivery problem, not a test problem

A suite that fails 1 in 10 runs for no reason trains the team to click "re-run" without reading the failure. Once that habit exists, a genuine regression is re-run past the gate too. Flakiness destroys the only thing a test suite provides - a trusted verdict - and its cost compounds: developers wait for re-runs, deploys queue, and change failure rate rises because nobody believes red any more.

### 1. Make it measurable

Store test results as structured output (JUnit XML or equivalent) for every run, including retries, and build a per-test flake rate: _failures on unchanged code / total runs_. Rank by (flake rate x how often the test runs). This turns "the tests are flaky" into "these six tests cost us 40 developer-hours a month", which is what gets fixing prioritised. Track the pipeline's own pass rate on `main` as a headline reliability metric.

### 2. Quarantine fast, with a deadline

Move a proven flaky test out of the blocking suite into a non-blocking job on the same run. Two rules keep quarantine from becoming a graveyard: every quarantined test gets a ticket with an owner and a date, and the quarantine list is reviewed in the team's regular cadence with a hard cap (say ten tests). A test that is neither fixed nor deleted by the deadline gets deleted - an untrusted test that nobody will fix has negative value.

### 3. Diagnose the actual cause

Flakiness has a short list of causes, and each has a real fix:

- **Time and timing** - `sleep`-based waits, tests that assume "now" or a fixed duration, timezone or DST edges. Fix by waiting on a condition with a timeout, and by injecting a clock rather than reading the system one.
- **Shared mutable state** - a database row, a Redis key, a temp file, a global singleton left dirty by an earlier test. Fix with per-test isolation: unique fixture data, transactional rollback, or a fresh schema/namespace per worker.
- **Order dependence** - the test only passes after another test seeds something. Prove it by shuffling the order deliberately in CI (`--random`, `-shuffle=on`) so hidden coupling fails loudly and early.
- **Concurrency and resource contention** - parallel workers colliding on a fixed port, an in-memory cache, or CPU starvation causing timeouts. Fix by allocating ports dynamically and sizing workers to the runner.
- **Real asynchrony** - eventual consistency, message queues, retries. Poll for the expected end state with a generous timeout instead of asserting immediately.
- **External dependencies** - a third-party API, DNS, a package registry. Stub at the boundary for unit and integration tests; keep genuine external calls to a small, separately reported end-to-end suite.
- **UI/browser races** - assert on application state and stable test IDs, not on animation timing or CSS selectors.

### 4. Use retries deliberately, and never silently

Retries are legitimate for a genuinely unreliable boundary (a network call in an end-to-end suite), but they must be **narrow, capped at one, and reported**. Any test that passes only on retry is recorded as a flake, not as a pass - otherwise the metric that drives fixes disappears. Retrying the whole job rather than the failed test is the worst version: it multiplies cost and erases the signal.

### 5. Prevent regression

Require new tests to survive a repeat-run check (`--count=10` or the framework equivalent) before merge, run the suite in shuffled order nightly, keep an eye on the slowest tests (slow tests are disproportionately flaky), and make "no new quarantine entries" part of the definition of done. See [how do you deal with a slow pipeline](./how-do-you-speed-up-a-slow-ci-cd-pipeline.md) - the two problems share a root in tests that do too much.

## Example

```text
Flake report - main branch, last 200 runs (retries counted as flakes)

  test                                      runs  flake%  cause            action
  checkout/payment_timeout_test             200    18.0%  sleep(2) wait    fixed: poll
  orders/list_pagination_test               200     9.5%  shared fixture   fixed: per-test row
  search/reindex_e2e_test                    40     7.5%  eventual index   retry(1), reported
  auth/session_expiry_test                  200     6.0%  system clock     fixed: injected clock
  ui/checkout_button_test                   200     4.5%  animation race   quarantined -> ENG-812
  ------------------------------------------------------------------------------
  pipeline pass rate on main: 71% -> 97% after the first three fixes
```

```yaml
# Quarantine as a non-blocking job, with the list under review - not a silent skip
jobs:
  test:
    steps:
      - run: pytest -m "not quarantine" -p no:randomly --junitxml=results.xml
  test-quarantine:
    continue-on-error: true # visible, reported, does not gate the merge
    steps:
      - run: pytest -m quarantine --junitxml=quarantine.xml
  new-test-stability:
    steps:
      # a new or changed test must pass 10 consecutive runs before it can gate
      - run: pytest --count=10 $(git diff --name-only origin/main -- 'tests/**')
```

## Interview tips

- Open with the cost, not the mechanics: flaky tests destroy trust in the suite, and an untrusted suite lets real regressions through. That is the reason this question is asked.
- Say explicitly that blanket retries are not a fix, then concede the one legitimate use - a narrow, capped, _reported_ retry at an unreliable boundary. The nuance reads as experience.
- Name the causes as a checklist (time, shared state, order, concurrency, asynchrony, external calls). Interviewers can tell the difference between someone who has debugged these and someone listing generalities.
- Mention deliberate test shuffling as the trick that surfaces order dependence, and repeat-runs on new tests as the guard against reintroduction.
- Quarantine with an owner, a date, and a cap - and be willing to say you would delete a test nobody will fix. That decisiveness is often the point of the question.
- Tie it to the metric: pipeline pass rate on `main` and change failure rate. See [what is change failure rate](../devops-metrics-and-kpis/what-is-change-failure-rate.md) and [what is blameless culture](../devops-culture-and-practices/what-is-blameless-culture.md) for the cultural half of the answer.

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
