---
title: "What does a DevSecOps pipeline look like end to end?"
id: 161
category: "DevSecOps"
difficulty: "Intermediate"
tags:
  - devops
  - devsecops
  - interview-questions
---

# What does a DevSecOps pipeline look like end to end?

**Short answer:** Security controls sit at every stage rather than in a final review gate: secret scanning and linting pre-commit, SAST and dependency scanning on pull request, image and IaC scanning at build, signing and admission control at deploy, and runtime detection in production. Each gate has an owner, a severity threshold that fails the build, and a documented exception path.

## Detail

**The stages and what runs in each:**

| Stage        | Controls                                                             | Fails the build on               |
| ------------ | -------------------------------------------------------------------- | -------------------------------- |
| Pre-commit   | secret detection (`gitleaks`), format/lint                           | any credential match             |
| Pull request | SAST, SCA/dependency review, IaC scan, license check                 | new high/critical, license deny  |
| Build        | image vulnerability scan, SBOM generation, provenance attestation    | critical with a fix available    |
| Pre-deploy   | signature verification, policy admission (OPA/Kyverno), config drift | unsigned or non-compliant object |
| Runtime      | behavioural detection, CSPM, audit logging                           | n/a — alerts, not gates          |

**Fail the build on new findings, not total findings.** A gate that fails on the existing backlog gets disabled within a week. Compare against a baseline: block what this change introduces, and burn the backlog down on a separate track with its own SLA per severity.

**Every gate needs an exception path.** A time-boxed, approved, expiring waiver recorded in the repository (not a Slack message) is the difference between a control teams respect and one they route around. Waivers without expiry dates become permanent.

**Shift left, but do not shift alone.** Developers get findings in the pull request with a fix suggestion; the security team owns the rules, the thresholds, and the triage of anything the developer cannot resolve. Tooling that only reports into a security dashboard has not shifted left at all.

## Example

```yaml
# .github/workflows/security.yml — PR-time gates, failing only on new criticals
name: security
on: [pull_request]
permissions:
  contents: read
  security-events: write
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 } # gitleaks needs history
      - name: Secret scan
        uses: gitleaks/gitleaks-action@v2
      - name: Dependency review (blocks new vulnerable deps)
        uses: actions/dependency-review-action@v4
        with: { fail-on-severity: high }
      - name: IaC scan
        run: |
          docker run --rm -v "$PWD:/src" aquasec/trivy:0.55.0 \
            config /src --severity HIGH,CRITICAL --exit-code 1
```

## Interview tips

- Name the gates in order and say which ones block. "Security is everyone's responsibility" without a pipeline is not an answer.
- The baseline/new-findings distinction and expiring waivers are the two details that show you have run this in a real team.
- Expect the follow-up: "what do you do when the critical has no fix?" — compensating control, documented risk acceptance, and a tracked ticket.

---

[⬅ Back to DevSecOps](./README.md) · [All topics](../README.md)
