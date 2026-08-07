---
title: "What does shift left security mean?"
id: 290
category: "DevSecOps"
difficulty: "Beginner"
tags:
  - devops
  - devsecops
  - interview-questions
---

# What does shift left security mean?

**Short answer:** Moving security checks earlier - "left" - in the delivery timeline, so problems are found while code is being written rather than in a penetration test weeks after release. In practice it means the IDE, the pull request, and the pipeline each catch a class of issue, with fast automated feedback to the person who wrote the code. It is about **timing and ownership**, not about doing less security later.

## Detail

**Why timing matters so much.** A vulnerability found in the editor costs minutes to fix. The same issue found in a pull request costs an hour. Found in a pre-release security review, it costs a sprint and a difficult conversation about the launch date. Found in production, it costs an incident. The defect is identical; only the position in the timeline changed. Shifting left is an economic argument before it is a security one.

**What moves left, and to where:**

| Stage            | Checks that belong there                                                 | Feedback time |
| ---------------- | ------------------------------------------------------------------------ | ------------- |
| **IDE / commit** | Secret scanning via pre-commit hooks, linters, IaC misconfig hints       | Seconds       |
| **Pull request** | SAST on the diff, dependency scanning (SCA), IaC scanning, policy checks | Minutes       |
| **Build**        | Container image scan, SBOM generation, image signing                     | Minutes       |
| **Pre-deploy**   | Admission policy, config validation, DAST against staging                | Minutes       |
| **Runtime**      | Vulnerability re-scanning, drift and anomaly detection, WAF              | Continuous    |

**The tools by what they look at.** **SAST** reads your source code for insecure patterns. **SCA** checks your dependencies against known-vulnerability databases - and for most applications, this finds the most real risk for the least effort, because most of the code you ship is somebody else's. **Secret scanning** catches credentials before they enter Git history. **IaC scanning** (Checkov, tfsec, Trivy) catches the public S3 bucket or the open security group before it exists. **DAST** attacks a running application. **Container scanning** covers the base image and OS packages you inherited.

**Ownership shifts too, and that is the harder half.** Shift left only works if developers can act on the findings, which means security stops being a gate a separate team operates and starts being feedback the delivery team owns. The security team's job becomes building the checks, setting the policy, and helping with the hard findings - not manually reviewing every release.

**The failure mode: noise.** A scanner turned on at full volume produces hundreds of findings, most of them irrelevant, and teams learn to ignore the whole category. Avoiding that:

- **Fail the build only on what matters** - critical and high severity, with a known exploit path, in code that actually runs. Report the rest without blocking.
- **Scan the diff, not the world**, on pull requests. New issues block; the existing backlog gets a separate, planned effort.
- **Suppress with an expiry and a reason.** A permanent unexplained ignore is how real findings hide.
- **Keep it fast.** A security stage that adds fifteen minutes to every pull request will be routed around within a month.

**What does not move left.** Threat modelling still happens at design time (that is even further left). Penetration testing, red teaming, incident response, and runtime detection remain essential - a container with no known CVEs can still be exploited through business logic. "Shift left" adds early cheap feedback; it does not replace defence in depth.

## Example

```yaml
# Pull request pipeline: fast checks, diff-scoped, blocking only on real risk.
name: security
on: pull_request

jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 } # full history so secret scanning can see the diff

      - name: Secrets (blocking - a leaked credential is always a stop)
        uses: gitleaks/gitleaks-action@v2

      - name: Dependencies (blocking on high/critical with a fix available)
        run: |
          trivy fs --scanners vuln --severity HIGH,CRITICAL \
                   --ignore-unfixed --exit-code 1 .

      - name: Infrastructure as Code
        run: checkov -d infra/ --compact --quiet --soft-fail-on LOW,MEDIUM

      - name: SAST on the changed files only
        run: semgrep ci --config auto   # 'ci' mode diffs against the base branch

      - name: Image scan + SBOM
        run: |
          docker build -t app:$GITHUB_SHA .
          trivy image --severity HIGH,CRITICAL --exit-code 1 app:$GITHUB_SHA
          syft app:$GITHUB_SHA -o spdx-json > sbom.json
```

```yaml
# .pre-commit-config.yaml - the leftmost check, running on the developer's machine.
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks: [{ id: gitleaks }]
  - repo: https://github.com/bridgecrewio/checkov
    rev: 3.2.0
    hooks: [{ id: checkov, args: [--quiet, --compact] }]
```

```yaml
# Suppressions carry a reason and an expiry - never a bare ignore.
# .trivyignore
CVE-2026-12345 exp:2026-10-01 # dev-only dependency, not in the runtime image - ticket SEC-412
```

## Interview tips

- Define it as timing and ownership, then give the cost curve: minutes in the IDE, an hour in a PR, a sprint before release, an incident in production.
- Map each check to the stage where it belongs. A table-shaped answer (IDE, PR, build, pre-deploy, runtime) reads as structured thinking.
- Know what the acronyms actually inspect - SAST source, SCA dependencies, DAST a running app, IaC scanning your Terraform. Mixing them up is the most common junior error here.
- Say that SCA usually finds the most real risk for the least effort, because most shipped code is third-party.
- Volunteer the noise problem and the fixes: diff-scoped scanning, block only on high/critical with a fix, expiring suppressions, keep it fast.
- Close by saying shift left does not remove pen testing, threat modelling, or runtime detection. Claiming it replaces them is the trap.

---

[⬅ Back to DevSecOps](./README.md) · [All topics](../README.md)
