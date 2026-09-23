---
title: "What are SLSA (Supply-chain Levels for Software Artifacts) frameworks and how do they verify build integrity?"
id: 539
category: "CI/CD"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - cicd
  - slsa
  - supply-chain
  - security
  - provenance
quiz:
  stem: "What is the primary function of a signed SLSA build provenance attestation?"
  options:
    - "It serves as a software license key verifying enterprise billing"
    - "It provides tamper-evident cryptographic proof detailing which source repository, commit, and build environment generated the binary"
    - "It converts container images into virtual machine snapshots"
    - "It encrypts the application source code so developers cannot read it"
  answer: 2
  explanation: "Provenance attestations cryptographically link the compiled artifact to its exact source repository, commit hash, and build system, proving the artifact was not modified or replaced post-build."
---

# What are SLSA (Supply-chain Levels for Software Artifacts) frameworks and how do they verify build integrity?

**Short answer:** SLSA is an industry security framework that prevents software tampering through verifiable build provenance, ensuring that code running in production was built by a trusted build service from an authentic source repository without intermediary tampering.

## Detail

SLSA (pronounced "salsa") is an OpenSSF specification. Since v1.0 it is organised into **tracks**, each with its own levels; the current version, **v1.2** (November 2025), has a **Build track** and a **Source track**. (The older v0.1 draft had a single ladder up to Level 4; that numbering is obsolete.)

**Build track** - how trustworthy the provenance of an artefact is:

| Level    | Requirement                                                                                                                          | What it defends against                             |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------- |
| Build L0 | Nothing                                                                                                                              | -                                                   |
| Build L1 | Provenance exists, describing how the artefact was built (can be unsigned)                                                           | Mistakes; gives you an inventory                    |
| Build L2 | Built on a **hosted build platform** that generates and **signs** the provenance itself                                              | Tampering after the build; forged provenance        |
| Build L3 | **Hardened** build platform: runs are isolated from one another and the signing material is inaccessible to user-defined build steps | A compromised build step forging its own provenance |

**Source track** (L1-L4) covers the other half: the source is in version control, its history is protected (no force-pushes over released commits), and at the top levels changes need two-party review - with the source system issuing its own verifiable attestations.

### How provenance verification works

1. **Build execution**: the build platform runs the build in an isolated, ephemeral runner.
2. **Attestation generation**: the platform (not the build script) generates an in-toto attestation with a SLSA provenance predicate recording:
   - Source repository URI and exact commit SHA.
   - The builder identity, the build definition (workflow file), and external parameters.
   - Resolved dependencies and the cryptographic digest of the output artefact.
3. **Cryptographic signing (Sigstore)**: the attestation is signed keylessly - Fulcio issues a short-lived certificate bound to the workflow's OIDC identity, and the signature is recorded in the Rekor transparency log so it can be audited later.
4. **Verification at the point of use**: before deployment, a verifier (`gh attestation verify`, `slsa-verifier`, `cosign verify-attestation`, or a Kubernetes admission policy in Kyverno or Sigstore policy-controller) checks the signature, then checks the **claims**: expected source repository, expected builder, expected branch or tag.

The limitation to state: SLSA provenance proves _where and how_ an artefact was built, not that the source code is safe. A malicious commit built on a perfect Build L3 platform yields perfectly valid provenance - which is why the Source track, code review, and dependency scanning still matter.

## Example

```yaml
# GitHub Actions: build, then have the platform sign SLSA provenance for the digest
name: release
on:
  push:
    tags: ["v*"]
permissions:
  contents: read
  packages: write
  id-token: write # Sigstore keyless signing
  attestations: write # store the attestation
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: docker/login-action@v4
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: push
        uses: docker/build-push-action@v7
        with:
          push: true
          tags: ghcr.io/acme/api:${{ github.ref_name }}
      - uses: actions/attest-build-provenance@v4
        with:
          subject-name: ghcr.io/acme/api
          subject-digest: ${{ steps.push.outputs.digest }}
          push-to-registry: true
```

```bash
# Verify before deploying: signature valid AND built by the expected repository
gh attestation verify oci://ghcr.io/acme/api:v1.4.0 --repo acme/api
```

## Interview tips

- Use the current vocabulary: tracks and levels (Build L1-L3, Source L1-L4 in v1.2). Quoting "SLSA Level 4" signals an out-of-date mental model.
- Explain the step up from L2 to L3 precisely: at L3 the build steps cannot reach the signing key, so a compromised build cannot forge its own provenance.
- Separate signing from verification: provenance only helps if something checks the claims (repository, builder, ref) at deploy or admission time.
- Name the limit - provenance does not make malicious source safe - and connect it to code review, the Source track, and SBOM/SCA.
- Likely follow-up: "how is this different from an SBOM?" - an SBOM lists what is inside the artefact; provenance attests how and from what source it was built.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Shift-Left and how is it practically implemented across the SDLC?]] (`#510`): [What is Shift-Left and how is it practically implemented across the SDLC?](../core-devops-concepts/what-is-shift-left-and-how-is-it-practically-implemented-across-the-sdlc.md)
- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#511`): [What is the difference between Continuous Delivery and Continuous Deployment?](../core-devops-concepts/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)
- [[How do you manage build artefacts with Nexus or Artifactory?]] (`#460`): [How do you manage build artefacts with Nexus or Artifactory?](../devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
