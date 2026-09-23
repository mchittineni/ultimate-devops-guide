---
title: "What is DAST (Dynamic Application Security Testing) and how is OWASP ZAP integrated into CI/CD pipelines?"
id: 709
category: "DevSecOps"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - devsecops
  - dast
  - owasp-zap
  - security
  - testing
quiz:
  stem: "What is the primary operational distinction between SAST (Static AST) and DAST (Dynamic AST)?"
  options:
    - "SAST is only used for databases, while DAST is used for mobile apps"
    - "SAST analyzes source code without executing it, whereas DAST attacks a live, running application over the network to test exploitability"
    - "DAST cannot run inside CI/CD pipelines"
    - "SAST runs exclusively on Linux servers"
  answer: 2
  explanation: "SAST analyzes raw code files for theoretical patterns. DAST interacts with the live running application over HTTP, validating whether vulnerabilities can be actively exploited in a deployed state."
---

# What is DAST (Dynamic Application Security Testing) and how is OWASP ZAP integrated into CI/CD pipelines?

**Short answer:** DAST tests a running application from the outside by executing simulated hacker attacks (SQLi, XSS, header misconfigurations); OWASP ZAP runs inside ephemeral CI containers to scan staging environments and fail pipelines if high-risk vulnerabilities are found.

## Detail

While SAST inspects static source code, it cannot verify whether a vulnerability is actually exploitable in a running environment with real web servers and proxies.

### Running OWASP ZAP in a CI/CD Pipeline

```yaml
# GitHub Actions snippet
- name: Run OWASP ZAP Baseline Scan
  uses: zaproxy/action-baseline@v0.15.0
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    target: "https://staging.my-app.internal"
    rules_file_name: ".zap/rules.tsv"
    fail_action: true
```

### Scan Modes

1. **Baseline Scan**: Fast (< 5 min) non-intrusive scan checking passive rules (missing security headers, clickjacking protection, insecure cookies, information leaks) - it spiders the app and inspects responses without sending attack payloads.
2. **Full Active Scan**: Active penetration testing sending malicious payloads into forms, query parameters, and API routes to uncover SQL injection and authenticated XSS.
3. **API Scan**: Ingests an OpenAPI / Swagger JSON spec to systematically fuzz all REST endpoints.

## Example

```text
10038  WARN  (Content Security Policy Header Not Set)
10021  FAIL  (X-Content-Type-Options Header Missing)
10096  IGNORE  (Timestamp Disclosure - Unix)
```

The `.zap/rules.tsv` file above (columns separated by tabs in the real file) tunes the baseline scan: `FAIL` rules break the build, `WARN` rules only report, `IGNORE` suppresses known noise. The same scan runs outside GitHub Actions with the ZAP container:

```bash
docker run --rm -v "$PWD:/zap/wrk:rw" -t ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t https://staging.my-app.internal -c rules.tsv -r zap-report.html
```

## Interview tips

- Position DAST correctly: black-box testing of the deployed application, so it finds runtime and configuration issues (headers, cookies, TLS, auth flaws, reflected injection) that SAST cannot see - but it gives no line numbers and only tests what it can reach.
- Run the passive **baseline** scan on every deployment to an ephemeral or staging environment, and the **active/full** or **API** scan nightly or pre-release - never actively scan production without explicit approval.
- Authentication is the make-or-break: without a login context or token, the crawler only tests the login page. The API scan with an OpenAPI spec is usually the highest-value mode for microservices.
- Manage noise with a checked-in rules file and fail only on agreed high-risk alerts, otherwise teams disable the job.
- Know the naming: ZAP left OWASP in 2023 and is now "ZAP by Checkmarx", so current docs and images use `zaproxy` names (`ghcr.io/zaproxy/zaproxy`, `zaproxy/zap-stable`) - the old `owasp/zap2docker-*` images are deprecated.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Shift-Left and how is it practically implemented across the SDLC?]] (`#510`): [What is Shift-Left and how is it practically implemented across the SDLC?](../core-devops-concepts/what-is-shift-left-and-how-is-it-practically-implemented-across-the-sdlc.md)
- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevSecOps](./README.md) · [All topics](../README.md)
