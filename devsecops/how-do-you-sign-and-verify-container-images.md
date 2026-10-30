---
title: "How do you sign and verify container images?"
id: 165
category: "DevSecOps"
difficulty: "Intermediate"
tags:
  - devops
  - devsecops
  - interview-questions
---

# How do you sign and verify container images?

**Short answer:** Sign the image by digest with Sigstore `cosign` - ideally keyless, exchanging a CI OIDC token for a short-lived certificate so there is no private key to leak - and store the signature alongside the image in the registry. Verify in an admission controller that fails closed, checking the signing identity, not merely that a signature exists.

## Detail

**Keys versus keyless.** A long-lived key pair means key storage, rotation, and a blast radius if it leaks. Keyless signing binds the signature to a workload identity (`repo:acme/api:ref:refs/heads/main` from GitHub's OIDC issuer) and records it in the Rekor transparency log. Keyless is the default recommendation; keys still make sense in air-gapped environments, where you use a KMS-backed key rather than a file.

**Sign the digest, always.** `cosign sign acme/api:latest` resolves the tag, but any policy that verifies by tag is bypassable - the tag can be repointed after verification. Pipelines should carry the `sha256:` digest from build to deploy and sign and verify that.

**Verification must check identity.** "Has a valid signature" is nearly worthless; anyone can sign anything. The policy has to assert _who_ signed: which OIDC issuer, which subject pattern, and for provenance which workflow ref. And it must fail closed - an unreachable transparency log should block deployment, not wave it through.

**What else to attach.** The same mechanism carries attestations: SBOM, SLSA provenance, vulnerability-scan results, even a "passed integration tests" claim. Policy can then require, for example, an SBOM attestation plus a scan attestation less than 7 days old.

**Where the signature lives.** Cosign v3 writes a Sigstore **bundle** (signature, certificate, and transparency-log proof in one object) and stores it as an OCI 1.1 **referrer** of the image digest, falling back to the referrers-tag scheme on registries without the referrers API; older releases used a `sha256-<digest>.sig` tag. Mixed estates matter here: verifiers and admission policies that only look for the old `.sig` tag will report "no signature" for a perfectly signed image, so upgrade the verification side first.

**Enforcing it.** Kyverno `verifyImages` (or its newer `ImageValidatingPolicy`), the Sigstore policy-controller, or Gatekeeper with Ratify check the identity at admission. The main alternative to Sigstore is **Notation** (CNCF Notary Project), which signs with X.509 certificates from your own PKI and suits organisations that want no public transparency log; Ratify and Kyverno verify both.

**Trade-offs.** Verification adds latency and a hard dependency on Sigstore infrastructure (mitigate by mirroring or self-hosting Fulcio/Rekor). Third-party base images usually have no signature you can pin, so most teams mirror them internally and re-sign after scanning.

## Example

```bash
# In CI: keyless sign the digest that was just built and pushed
DIGEST=$(crane digest ghcr.io/acme/api:"$GITHUB_SHA")
cosign sign --yes ghcr.io/acme/api@"$DIGEST"

# Anywhere: verify the signer identity, not just the presence of a signature
cosign verify ghcr.io/acme/api@"$DIGEST" \
  --certificate-identity-regexp '^https://github.com/acme/.+$' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com

# Attestations use the same identity: attach an SBOM, then require it at deploy time
cosign attest --yes --type cyclonedx --predicate sbom.json ghcr.io/acme/api@"$DIGEST"
cosign verify-attestation --type cyclonedx ghcr.io/acme/api@"$DIGEST" \
  --certificate-identity-regexp '^https://github.com/acme/.+$' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com > /dev/null
```

## Interview tips

- Say "sign by digest" unprompted - interviewers listen for the tag-mutability trap.
- Keyless and Rekor transparency logging are the modern answer; explain the key-management problem they remove.
- Be ready for "how do you handle upstream images with no signatures?" - mirror, scan, re-sign, and pin by digest.
- If asked "Sigstore or Notation?": Sigstore keyless for public and CI-native workflows; Notation (or cosign with a KMS key) when signatures must chain to a corporate CA or no public log is acceptable.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
- [[How do you integrate SonarQube and quality gates into a pipeline?]] (`#458`): [How do you integrate SonarQube and quality gates into a pipeline?](../cicd/how-do-you-integrate-sonarqube-and-quality-gates-into-a-pipeline.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevSecOps](./README.md) · [All topics](../README.md)
