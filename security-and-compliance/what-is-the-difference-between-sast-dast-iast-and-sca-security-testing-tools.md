---
title: "What is the difference between SAST, DAST, IAST, and SCA security testing tools?"
id: 565
category: "Security and Compliance"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - security
  - sast
  - dast
  - sca
  - devsecops
quiz:
  stem: "Which security testing tool scans third-party open-source libraries and package lockfiles (like `package-lock.json`) for known public CVEs?"
  options:
    - "Static Application Security Testing (SAST)"
    - "Software Composition Analysis (SCA)"
    - "Dynamic Application Security Testing (DAST)"
    - "Web Application Firewall (WAF)"
  answer: 2
  explanation: "SCA tools (like Snyk and Trivy) specifically inventory open-source dependencies and match them against vulnerability databases (like the NVD) to flag known CVEs and license risks."
---

# What is the difference between SAST, DAST, IAST, and SCA security testing tools?

**Short answer:** SAST analyzes static source code without running it; DAST attacks running applications externally via simulated exploits; SCA scans open-source third-party dependencies for known CVEs and license risks; IAST instruments the runtime from inside to verify vulnerabilities as code executes.

## Detail

Modern AppSec relies on layered application security testing across the SDLC:

| Tool Category                                                           | How it Works                         | When it Runs           | Strengths                                                                                | Weaknesses                                                                           |
| ----------------------------------------------------------------------- | ------------------------------------ | ---------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| **SAST** (Static Application Security Testing - SonarQube, Semgrep)     | Scans raw source code / AST          | Pre-commit / Early CI  | Finds code-level flaws (SQL injection, hardcoded secrets, buffer overflows)              | High false positive rate; cannot see runtime config                                  |
| **SCA** (Software Composition Analysis - Snyk, Trivy, Dependabot)       | Analyzes package lockfiles           | CI / PR build          | Identifies vulnerable third-party dependencies (CVEs) and license violations             | Noisy unless the tool offers reachability analysis; says nothing about your own code |
| **DAST** (Dynamic Application Security Testing - OWASP ZAP, Burp Suite) | Black-box HTTP penetration testing   | Staging / Running App  | Findings are demonstrated against the running app, so false positives are relatively low | Slow; only covers what it can reach; cannot pinpoint file and line                   |
| **IAST** (Interactive AST - Contrast Assess, Seeker)                    | Agent inside the application runtime | Integration tests / QA | Combines SAST line precision with DAST runtime verification                              | Requires dedicated test traffic and runtime language agent                           |

## Example

```bash
# SAST on the diff only (fast PR feedback)
semgrep scan --config p/owasp-top-ten --baseline-commit "$(git merge-base origin/main HEAD)" --error

# SCA on the lock file, failing only on fixable high/critical findings
trivy fs --scanners vuln --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 .

# DAST passive baseline against a deployed staging environment
docker run --rm -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t https://staging.example.com
```

## Interview tips

- Anchor each on what it needs and when it runs: SAST needs source (every PR), SCA needs manifests or lock files (every PR and continuously), DAST needs a running app (staging), IAST needs an agent plus test traffic (integration/QA).
- Match them to bug classes: SAST for code patterns, SCA for known-vulnerable components (Log4Shell was an SCA problem), DAST for runtime and configuration issues, IAST for confirming exploitable paths with a stack trace.
- The operational problem is noise, not coverage: scan diffs, gate on new high-severity findings, use reachability or exploitability data, and require a reason for suppressions.
- None of them finds business-logic or authorisation flaws reliably - that remains threat modelling, code review, and manual penetration testing.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DAST (Dynamic Application Security Testing) and how is OWASP ZAP integrated into CI/CD pipelines?]] (`#709`): [What is DAST (Dynamic Application Security Testing) and how is OWASP ZAP integrated into CI/CD pipelines?](../devsecops/what-is-dast-dynamic-application-security-testing-and-how-is-owasp-zap-integrated-into-ci-cd-pipelines.md)
- [[What are Threat Modeling frameworks (STRIDE, PASTA) and how do they embed security into early sprint design?]] (`#710`): [What are Threat Modeling frameworks (STRIDE, PASTA) and how do they embed security into early sprint design?](../devsecops/what-are-threat-modeling-frameworks-stride-pasta-and-how-do-they-embed-security-into-early-sprint-design.md)
- [[What is Runtime Application Self-Protection (RASP) and how does it differ from a perimeter WAF?]] (`#711`): [What is Runtime Application Self-Protection (RASP) and how does it differ from a perimeter WAF?](../devsecops/what-is-runtime-application-self-protection-rasp-and-how-does-it-differ-from-a-perimeter-waf.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Security and Compliance](./README.md) · [All topics](../README.md)
