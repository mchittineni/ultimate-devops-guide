---
title: "How Does Google Cloud Binary Authorization Prevent Unauthorized Container Deployments?"
id: 749
category: "GCP Engineering"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - gcp-engineering
  - binary-authorization
  - supply-chain
  - gke
quiz:
  stem: "How does Google Cloud Binary Authorization determine whether a container image is permitted to deploy onto a GKE cluster?"
  options:
    - "It decompiles the container binary to inspect the source code comments."
    - "It verifies whether the image's cryptographic SHA256 digest has valid digital signatures (attestations) created by authorized CI/CD pipeline attestors."
    - "It checks if the image filename ends with the extension '.approved'."
    - "It allows deployments only if they are initiated by the Google account root user."
  answer: 2
  explanation: "Binary Authorization verifies cryptographic attestations attached to the container image's SHA256 digest. If required signatures (e.g., from security scanners or build agents) are missing, the admission controller rejects the deployment."
---

# How Does Google Cloud Binary Authorization Prevent Unauthorized Container Deployments?

**Short answer:** Google Cloud Binary Authorization is a deploy-time security gate for GKE and Cloud Run that verifies cryptographic signatures (attestations) on container images, ensuring only images that have passed approved CI/CD security stages (vulnerability scanning, QA tests) can be deployed.

## Detail

### Securing the Software Supply Chain (SLSA Compliance)

In modern DevSecOps pipelines, preventing malicious or vulnerable code from reaching production requires strict deploy-time policy enforcement. Simply trusting image repository names is insufficient.

**Google Cloud Binary Authorization** enforces strict cryptographic provenance before a container is permitted to run.

### Core Architectural Concepts

1. **Policy**: An organization-wide or project-level policy defining rules for container admission (e.g., 'Disallow all images unless attested by QA and Security').
2. **Attestor**: A named verification authority backed by a Container Analysis note and one or more public keys (PKIX keys, typically in Cloud KMS, or PGP).
3. **Attestation**: A signed cryptographic statement created during the CI/CD pipeline certifying that a specific container image digest (SHA-256) has passed a specific validation step (e.g., Snyk scan completed with zero critical vulnerabilities).
4. **Enforcement**: GKE evaluates the policy at Pod admission (the enforcer is built into the cluster when Binary Authorization is enabled) and Cloud Run evaluates it at deploy time. Images referenced by tag cannot be matched to an attestation, so pipelines deploy by digest.
5. **Continuous validation (GKE)**: check-based platform policies re-evaluate running Pods against checks such as image freshness, trusted directories, Sigstore signatures, SLSA provenance, and vulnerability thresholds, logging violations for images that were admitted earlier but have since become non-compliant.

```text
[Developer Git Push]
         │
         ▼
[Cloud Build CI Pipeline]
 ├─ 1. Build Container Image & Compute SHA256
 ├─ 2. Run Artifact Analysis vulnerability scan
 └─ 3. IF Passed: Sign digest using KMS Key ──► Creates Attestation
         │
         ▼
[GKE Admission Controller (Binary Authorization)]
 ├─ Inspects Pod Deployment Request
 ├─ Checks required Attestations from Security Attestor
 ├── Valid Signature Found? ──► ALLOW: Pod Launches
 └── Missing Signature?     ──► DENY : Deployment Rejected!
```

### Break-Glass Capability

In emergency production outages, engineers may need to bypass Binary Authorization to deploy an emergency hotfix.

- Binary Authorization provides an auditable **break-glass** mechanism: annotating the Pod with `alpha.image-policy.k8s.io/break-glass: "true"` bypasses enforcement.
- The deployment proceeds, but generates a critical audit log event in Cloud Audit Logs to trigger immediate SecOps investigation.

### Real-World Production Scenario

A developer attempts to manually deploy an untested container image directly from their laptop to a production GKE cluster using `kubectl run`. The GKE Admission Controller queries Binary Authorization, detects that the image digest lacks a cryptographic attestation from the official Cloud Build vulnerability pipeline, and blocks the pod from starting.

## Example

```yaml
# policy.yaml - require the build attestor for everything except Google-managed system images
globalPolicyEvaluationMode: ENABLE
defaultAdmissionRule:
  evaluationMode: REQUIRE_ATTESTATION
  enforcementMode: ENFORCED_BLOCK_AND_AUDIT_LOG
  requireAttestationsBy:
    - projects/PROJECT_ID/attestors/built-by-cloud-build
name: projects/PROJECT_ID/policy
```

```bash
gcloud container binauthz policy import policy.yaml
gcloud container clusters update prod --location=europe-west1 \
  --binauthz-evaluation-mode=PROJECT_SINGLETON_POLICY_ENFORCE

# In CI, after the scan passes: attest the image digest (never a tag)
gcloud container binauthz attestations sign-and-create \
  --artifact-url="europe-docker.pkg.dev/PROJECT_ID/apps/checkout@sha256:${DIGEST}" \
  --attestor=built-by-cloud-build --attestor-project=PROJECT_ID \
  --keyversion=projects/PROJECT_ID/locations/global/keyRings/binauthz/cryptoKeys/attestor/cryptoKeyVersions/1
```

## Interview tips

- Explain that Binary Authorization operates as a Kubernetes Admission Controller intercepting deployment requests.
- Emphasize that attestations are bound to the immutable container image SHA256 digest, not mutable tags like `:latest`.
- Mention the break-glass capability for emergency incident response, which allows deployments while alerting security teams - and that you must actually alert on it.
- Trade-offs: every deploy path (including Helm charts, third-party images, and system add-ons) needs an allowlist pattern or attestation, so rollouts start in dry-run mode; attestation proves the pipeline ran, not that the image is safe.
- Compare with the open-source equivalent: Sigstore/cosign signatures verified by an admission policy engine (Kyverno or Sigstore policy-controller).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Cloud Computing?]] (`#21`): [What is Cloud Computing?](../cloud-platforms/what-is-cloud-computing.md)
- [[What is AWS (Amazon Web Services)?]] (`#22`): [What is AWS (Amazon Web Services)?](../cloud-platforms/what-is-aws-amazon-web-services.md)
- [[What is Google Cloud Platform (GCP)?]] (`#24`): [What is Google Cloud Platform (GCP)?](../cloud-platforms/what-is-google-cloud-platform-gcp.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to GCP Engineering](./README.md) · [All topics](../README.md)
