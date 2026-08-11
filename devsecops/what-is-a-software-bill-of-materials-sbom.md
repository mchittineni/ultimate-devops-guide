---
title: "What is a Software Bill of Materials (SBOM)?"
id: 163
category: "DevSecOps"
difficulty: "Intermediate"
tags:
  - devops
  - devsecops
  - interview-questions
---

# What is a Software Bill of Materials (SBOM)?

**Short answer:** An SBOM is a machine-readable inventory of every component in a build - direct and transitive dependencies, versions, and licenses - emitted in a standard format (SPDX or CycloneDX). Its value is answering "are we affected?" in minutes when the next Log4Shell lands, instead of grepping repositories for a week.

## Detail

**Two formats matter.** SPDX (license-and-compliance heritage; SPDX 2.2.1 is ISO/IEC 5962:2021, and SPDX 3.0 added a profile-based model with Security, Build, AI, and Dataset profiles) and CycloneDX (OWASP, security heritage, richer VEX support; standardised as ECMA-424 and now covering CBOM for cryptography and AI/ML-BOM alongside plain SBOM). Both are accepted by US federal guidance; pick one, generate it consistently, and convert when a customer demands the other. Be ready for the follow-up that you will meet SPDX 2.2.1, 2.3, and 3.x in the wild and they are not capability-equivalent.

**Generate at build time, from the build.** An SBOM produced by scanning source manifests misses what the base image contributes; one produced by scanning the final artifact captures the OS packages too. The reliable pattern is generating from the built image and attaching it to the image in the registry as an attestation, so the SBOM travels with the digest it describes.

**Store it keyed by artifact digest, not by tag.** Tags move. `sha256:…` is the only identifier that lets you say later, precisely, which bill of materials describes the thing running in production.

**VEX is the missing half.** An SBOM says "we contain library X 2.14". A VEX (Vulnerability Exploitability eXchange) document says "CVE-2021-44228 does not affect us because the vulnerable class is not on the classpath". Without VEX, every customer scan of your SBOM regenerates the same false positives and you answer them by hand.

**Where it becomes an obligation.** US Executive Order 14028 and the resulting NIST guidance pushed SBOMs into federal procurement; the EU Cyber Resilience Act carries comparable expectations for products sold into the EU, on a concrete clock: it entered into force in December 2024, the vulnerability and incident reporting obligations apply from **11 September 2026**, and the full requirements from **11 December 2027**. If you sell software to enterprises or governments, customers will ask.

## Example

```bash
# Generate a CycloneDX SBOM from the built image and attach it as an attestation
syft registry:ghcr.io/acme/api@sha256:1f4b... -o cyclonedx-json > sbom.json

cosign attest --predicate sbom.json --type cyclonedx \
  ghcr.io/acme/api@sha256:1f4b...

# Later: "are we affected by this CVE?" - answered from the stored SBOM, no rebuild
grype sbom:sbom.json --fail-on high
```

## Interview tips

- Lead with the incident-response use case; "compliance asked for it" is the weaker answer.
- Naming VEX, and digest-keyed storage, separates people who have generated SBOMs from people who have used them.
- Expect: "who consumes it?" - your own vulnerability management, plus customers' procurement and their scanners.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you harden a container image and a Dockerfile?]] (`#441`): [How do you harden a container image and a Dockerfile?](../docker/how-do-you-harden-a-container-image-and-a-dockerfile.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
- [[How do you integrate SonarQube and quality gates into a pipeline?]] (`#458`): [How do you integrate SonarQube and quality gates into a pipeline?](../cicd/how-do-you-integrate-sonarqube-and-quality-gates-into-a-pipeline.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevSecOps](./README.md) · [All topics](../README.md)
