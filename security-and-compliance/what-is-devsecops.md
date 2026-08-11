---
title: "What is DevSecOps?"
id: 36
category: "Security and Compliance"
difficulty: "Beginner"
tags:
  - devops
  - security-and-compliance
  - interview-questions
---

# What is DevSecOps?

**Short answer:** DevSecOps integrates security into every stage of the delivery pipeline rather than bolting it on at the end - making security a shared responsibility of the whole team, automated and continuous.

## Detail

The traditional model put a security review just before release, where findings were expensive to fix and delayed launches. DevSecOps shifts security **left** (earlier in development) and **right** (continuous verification in production).

Where controls sit in the lifecycle:

- **Plan** - threat modelling, abuse cases, security requirements in the story.
- **Code** - secure coding standards, IDE linters, pre-commit secret scanning, peer review.
- **Build** - SAST (static analysis), SCA (dependency CVE scanning), license checks, SBOM generation, image signing.
- **Test** - DAST (dynamic scanning against a running app), API fuzzing, IaC policy scanning.
- **Release** - signed artifacts, provenance attestations, admission control that rejects unsigned or vulnerable images.
- **Operate** - runtime detection, vulnerability rescanning of deployed images, WAF, audit logging.
- **Monitor** - anomaly detection, alerting, incident response, and feedback into the backlog.

Two cultural points make it work: security findings become normal backlog items with owners and SLAs, not a separate spreadsheet; and gates must be tuned so that only high-confidence, high-severity findings break the build - otherwise teams route around them.

## Example

```yaml
# Security stage that fails the build only on genuine high-severity findings
security:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Secret scan
      uses: gitleaks/gitleaks-action@v2
    - name: Dependency + image scan
      run: trivy image --severity HIGH,CRITICAL --exit-code 1 --ignore-unfixed app:${{ github.sha }}
    - name: IaC policy scan
      run: checkov -d infra/ --compact --quiet
    - name: Generate SBOM
      run: syft app:${{ github.sha }} -o cyclonedx-json > sbom.json
```

## Interview tips

- `--ignore-unfixed` and severity thresholds show you have run these tools in anger, not just installed them.
- Name the acronyms accurately: SAST, DAST, SCA, IAST, SBOM.
- The cultural answer matters as much as the tooling: security champions in each team, and blameless handling of vulnerabilities.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you rotate secrets without downtime?]] (`#429`): [How do you rotate secrets without downtime?](../devsecops/how-do-you-rotate-secrets-without-downtime.md)
- [[How do you manage TLS certificates in production?]] (`#491`): [How do you manage TLS certificates in production?](../network-security/how-do-you-manage-tls-certificates-in-production.md)
- [[What does a DevSecOps pipeline look like end to end?]] (`#161`): [What does a DevSecOps pipeline look like end to end?](../devsecops/what-does-a-devsecops-pipeline-look-like-end-to-end.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Security and Compliance](./README.md) · [All topics](../README.md)
