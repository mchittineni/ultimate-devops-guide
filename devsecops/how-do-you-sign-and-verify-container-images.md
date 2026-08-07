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
```

## Interview tips

- Say "sign by digest" unprompted - interviewers listen for the tag-mutability trap.
- Keyless and Rekor transparency logging are the modern answer; explain the key-management problem they remove.
- Be ready for "how do you handle upstream images with no signatures?" - mirror, scan, re-sign, and pin by digest.

---

[⬅ Back to DevSecOps](./README.md) · [All topics](../README.md)
