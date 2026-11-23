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
| Runtime      | behavioural detection, CSPM, audit logging                           | n/a - alerts, not gates          |

**Fail the build on new findings, not total findings.** A gate that fails on the existing backlog gets disabled within a week. Compare against a baseline: block what this change introduces, and burn the backlog down on a separate track with its own SLA per severity.

**Every gate needs an exception path.** A time-boxed, approved, expiring waiver recorded in the repository (not a Slack message) is the difference between a control teams respect and one they route around. Waivers without expiry dates become permanent.

**Make the gates impossible to skip.** "Developers should scan locally" is a convenience that saves pipeline minutes, not a control: nobody can prove it ran. A gate only counts if there is no route to production around it:

- **The pipeline checks are required.** Branch protection or a ruleset on `main` lists the scan jobs as required status checks, blocks direct pushes, and applies to admins too, so a pull request cannot merge with a failing or missing scan.
- **Only the pipeline can publish artefacts.** The registry (for example an ECR repository policy plus IAM) allows pushes only from the CI system's OIDC-assumed role, scoped to the protected branch. Developers can pull but not push, so an image built and pushed from a laptop cannot exist.
- **Production admits only what the pipeline produced.** The pipeline signs the image and attaches provenance and scan attestations; admission control in the cluster (Kyverno `verifyImages`, Sigstore policy-controller, or a cloud equivalent) rejects anything unsigned or signed by any identity other than that workflow. This closes the last gap, someone running `kubectl set image` with an unscanned tag.

With those three in place, local scans become what they should be: fast feedback that avoids a failed pipeline run, not the thing standing between a vulnerability and production.

**Shift left, but do not shift alone.** Developers get findings in the pull request with a fix suggestion; the security team owns the rules, the thresholds, and the triage of anything the developer cannot resolve. Tooling that only reports into a security dashboard has not shifted left at all.

## Example

```yaml
# .github/workflows/security.yml - PR-time gates, failing only on new criticals
name: security
on: [pull_request]
permissions:
  contents: read
  security-events: write
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with: { fetch-depth: 0 } # gitleaks needs history
      - name: Secret scan
        uses: gitleaks/gitleaks-action@v3
        env: { GITHUB_TOKEN: "${{ secrets.GITHUB_TOKEN }}" } # needed to scan pull requests
      - name: Dependency review (blocks new vulnerable deps)
        uses: actions/dependency-review-action@v5
        with: { fail-on-severity: high }
      - name: IaC scan
        run: |
          docker run --rm -v "$PWD:/src" aquasec/trivy:0.73.0 \
            config /src --severity HIGH,CRITICAL --exit-code 1
```

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "OnlyCiMayPush",
      "Effect": "Deny",
      "Principal": "*",
      "Action": ["ecr:PutImage", "ecr:InitiateLayerUpload", "ecr:UploadLayerPart", "ecr:CompleteLayerUpload"],
      "Condition": {
        "StringNotEquals": { "aws:PrincipalArn": "arn:aws:iam::111122223333:role/ci-image-publisher" }
      }
    }
  ]
}
```

The ECR repository policy above denies image pushes from every principal except the CI role, which the pipeline assumes through OIDC with a trust policy limited to the protected branch.

## Interview tips

- Name the gates in order and say which ones block. "Security is everyone's responsibility" without a pipeline is not an answer.
- The baseline/new-findings distinction and expiring waivers are the two details that show you have run this in a real team.
- "You can't trust developers to scan locally, so how do you enforce it?" A weak answer stops at "the pipeline scans anyway". The strong one shows there is no way around the pipeline: required status checks, a registry only the CI role can push to, and admission control that admits only images signed by that pipeline.
- Expect the follow-up: "what do you do when the critical has no fix?" - compensating control, documented risk acceptance, and a tracked ticket.
- Treat the security tooling as supply chain too: pin actions and scanner images to a commit SHA or digest (the tags above are for readability). In March 2026 attackers force-pushed most `aquasecurity/trivy-action` tags to a credential stealer - tag-pinned pipelines ran it, SHA-pinned ones did not.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevSecOps](./README.md) · [All topics](../README.md)
