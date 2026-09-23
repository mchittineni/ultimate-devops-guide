---
title: "DevSecOps"
category: "DevSecOps"
tags:
  - devops
  - devsecops
  - index
---

# DevSecOps

Security built into the delivery pipeline: scanning layers, SBOMs and supply-chain provenance, image signing, secretless pipelines, and vulnerability triage that does not stall delivery.

**19 questions** · 🟢 Beginner: 3 · 🟡 Intermediate: 11 · 🔴 Advanced: 5

## Questions

| #   | Question                                                                                                                                                                                                                                         | Difficulty      |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------- |
| 161 | [What does a DevSecOps pipeline look like end to end?](./what-does-a-devsecops-pipeline-look-like-end-to-end.md)                                                                                                                                 | 🟡 Intermediate |
| 162 | [What is the difference between SAST, DAST, IAST, and SCA?](./what-is-the-difference-between-sast-dast-iast-and-sca.md)                                                                                                                          | 🟡 Intermediate |
| 163 | [What is a Software Bill of Materials (SBOM)?](./what-is-a-software-bill-of-materials-sbom.md)                                                                                                                                                   | 🟡 Intermediate |
| 164 | [What is SLSA and how do you secure the software supply chain?](./what-is-slsa-and-how-do-you-secure-the-software-supply-chain.md)                                                                                                               | 🔴 Advanced     |
| 165 | [How do you sign and verify container images?](./how-do-you-sign-and-verify-container-images.md)                                                                                                                                                 | 🟡 Intermediate |
| 166 | [How do you manage secrets in CI/CD pipelines?](./how-do-you-manage-secrets-in-ci-cd-pipelines.md)                                                                                                                                               | 🟡 Intermediate |
| 167 | [How do you scan Infrastructure as Code before it is applied?](./how-do-you-scan-infrastructure-as-code-before-it-is-applied.md)                                                                                                                 | 🟡 Intermediate |
| 168 | [How do you prioritise vulnerabilities without blocking delivery?](./how-do-you-prioritise-vulnerabilities-without-blocking-delivery.md)                                                                                                         | 🔴 Advanced     |
| 244 | [How do you enforce Kubernetes admission control with Kyverno or OPA Gatekeeper?](./how-do-you-enforce-kubernetes-admission-control-with-kyverno-or-opa-gatekeeper.md)                                                                           | 🟡 Intermediate |
| 290 | [What does shift left security mean?](./what-does-shift-left-security-mean.md)                                                                                                                                                                   | 🟢 Beginner     |
| 429 | [How do you rotate secrets without downtime?](./how-do-you-rotate-secrets-without-downtime.md)                                                                                                                                                   | 🔴 Advanced     |
| 504 | [How do you manage Kubernetes secrets in a GitOps workflow?](./how-do-you-manage-kubernetes-secrets-in-a-gitops-workflow.md)                                                                                                                     | 🔴 Advanced     |
| 705 | [How do you integrate automated secret scanning into pre-commit and CI pipelines to prevent credential leaks?](./how-do-you-integrate-automated-secret-scanning-into-pre-commit-and-ci-pipelines-to-prevent-credential-leaks.md)                 | 🟢 Beginner     |
| 706 | [What is Container Image Signing with Sigstore and Cosign and how is it verified by Kubernetes admission controllers?](./what-is-container-image-signing-with-sigstore-and-cosign-and-how-is-it-verified-by-kubernetes-admission-controllers.md) | 🟡 Intermediate |
| 707 | [What is Policy as Code and how do OPA Gatekeeper and Kyverno enforce cluster governance?](./what-is-policy-as-code-and-how-do-opa-gatekeeper-and-kyverno-enforce-cluster-governance.md)                                                         | 🟡 Intermediate |
| 708 | [What are dependency vulnerabilities (CVEs) and how do Dependabot and Renovate automate security remediation?](./what-are-dependency-vulnerabilities-cves-and-how-do-dependabot-and-renovate-automate-security-remediation.md)                   | 🟢 Beginner     |
| 709 | [What is DAST (Dynamic Application Security Testing) and how is OWASP ZAP integrated into CI/CD pipelines?](./what-is-dast-dynamic-application-security-testing-and-how-is-owasp-zap-integrated-into-ci-cd-pipelines.md)                         | 🟡 Intermediate |
| 710 | [What are Threat Modeling frameworks (STRIDE, PASTA) and how do they embed security into early sprint design?](./what-are-threat-modeling-frameworks-stride-pasta-and-how-do-they-embed-security-into-early-sprint-design.md)                    | 🟡 Intermediate |
| 711 | [What is Runtime Application Self-Protection (RASP) and how does it differ from a perimeter WAF?](./what-is-runtime-application-self-protection-rasp-and-how-does-it-differ-from-a-perimeter-waf.md)                                             | 🔴 Advanced     |

## What interviewers probe here

- Which gates block a build, and how you handle the existing backlog.
- SBOM, provenance, and signature verification that fails closed.
- Ranking vulnerabilities by exploitability and exposure, not CVSS alone.

---

[⬅ Back to all topics](../README.md)
