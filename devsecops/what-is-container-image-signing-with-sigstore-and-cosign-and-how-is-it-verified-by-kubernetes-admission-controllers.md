---
title: "What is Container Image Signing with Sigstore and Cosign and how is it verified by Kubernetes admission controllers?"
id: 706
category: "DevSecOps"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - devsecops
  - sigstore
  - cosign
  - supply-chain
  - admission-controller
quiz:
  stem: "How does keyless signing with Sigstore/Cosign eliminate the burden of managing long-lived private signing keys?"
  options:
    - "It uses unencrypted plain text passwords"
    - "It exchanges short-lived OIDC tokens (from GitHub/GitLab) for temporary X.509 certificates and logs signatures to an immutable public transparency ledger (Rekor)"
    - "It stores private keys in public DNS records"
    - "It runs only on local hardware without internet"
  answer: 2
  explanation: "Keyless signing leverages workload identity (OIDC) to issue short-lived certificates valid for minutes, recording signatures in a transparency log without managing private key files."
---

# What is Container Image Signing with Sigstore and Cosign and how is it verified by Kubernetes admission controllers?

**Short answer:** Sigstore/Cosign cryptographically signs container images during CI/CD using short-lived OpenID Connect certificates; Kubernetes admission controllers (Kyverno, Sigstore policy-controller, or Gatekeeper via the Ratify external data provider) verify this signature and the signer's identity before allowing the image to run, blocking untrusted or tampered images.

## Detail

Without image signing, anyone with write access to your container registry can overwrite the `my-app:v1.2` tag with a malicious cryptocurrency miner or backdoor.

### The Keyless Signing Workflow with Cosign

```text
1. CI Runner (GitHub Actions) builds container image: my-app@sha256:abcd...
2. Cosign requests an ephemeral certificate from Fulcio (Sigstore CA) using GitHub OIDC token.
3. Cosign signs the image digest using an ephemeral key pair.
4. The signature and public certificate are published to Rekor (an immutable transparency log).
5. The signature is stored in the registry next to the image (as an OCI artifact referencing the digest).
```

### Kubernetes Admission Enforcement (Kyverno)

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signatures
spec:
  webhookTimeoutSeconds: 30
  rules:
    - name: verify-signature
      match:
        any:
          - resources:
              kinds: ["Pod"]
      verifyImages:
        - imageReferences: ["ghcr.io/my-org/*"]
          failureAction: Enforce # per-rule since Kyverno 1.13; spec.validationFailureAction is deprecated
          mutateDigest: true # rewrite the tag to the verified digest
          attestors:
            - entries:
                - keyless:
                    issuer: "https://token.actions.githubusercontent.com"
                    subject: "https://github.com/my-org/my-app/.github/workflows/*@refs/heads/main"
```

If an unauthorized image is deployed, the admission controller **blocks pod creation immediately**.

## Example

```bash
# In CI (GitHub Actions job with `permissions: id-token: write`): keyless sign by digest
DIGEST=$(crane digest ghcr.io/my-org/my-app:"$GITHUB_SHA")
cosign sign --yes ghcr.io/my-org/my-app@"$DIGEST"

# Verify exactly what the admission policy will check: issuer AND identity
cosign verify ghcr.io/my-org/my-app@"$DIGEST" \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  --certificate-identity-regexp '^https://github.com/my-org/my-app/\.github/workflows/.+@refs/heads/main$'
```

## Interview tips

- Say "sign and verify the digest, not the tag" - tags are mutable, and a signature over a tag proves nothing about what is running.
- Explain keyless precisely: Fulcio issues a certificate valid for about ten minutes that binds an ephemeral key to the CI workload's OIDC identity; the Rekor transparency log entry proves the signature was made while the certificate was valid, so there is no long-lived private key to steal or rotate.
- Verification must pin the **identity** (issuer plus subject/workflow), not just "has a signature" - anyone can sign an image with their own identity.
- Name the enforcement options: Kyverno `verifyImages`, Sigstore policy-controller, or Gatekeeper with an external data provider (for example Ratify). Kyverno also mutates the tag to the verified digest.
- Trade-offs: a hard dependency on the registry and Sigstore at admission time (plan for `failurePolicy`, caching, or a private Sigstore instance), and third-party images that are unsigned - mirror, scan, and re-sign them internally.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
- [[How do you secure CI/CD runners against supply-chain attacks and untrusted pull requests?]] (`#538`): [How do you secure CI/CD runners against supply-chain attacks and untrusted pull requests?](../cicd/how-do-you-secure-ci-cd-runners-against-supply-chain-attacks-and-untrusted-pull-requests.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevSecOps](./README.md) · [All topics](../README.md)
