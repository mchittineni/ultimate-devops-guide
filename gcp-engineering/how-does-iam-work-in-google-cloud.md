---
title: "How does IAM work in Google Cloud?"
id: 208
category: "GCP Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - gcp-engineering
  - interview-questions
---

# How does IAM work in Google Cloud?

**Short answer:** You bind a principal (user, group, service account, or federated identity) to a role (a bundle of permissions) at a scope in the hierarchy. Grants are additive and inherited downward; there is no implicit deny at a lower level, though explicit IAM Deny policies exist and are evaluated first. Workload Identity Federation removes the need for service-account keys entirely.

## Detail

**Roles come in three kinds.** Basic (`Owner`, `Editor`, `Viewer`) are legacy, extremely broad, and should not appear in a modern project. Predefined roles are per-service and reasonably scoped - start here. Custom roles are for when a predefined role is still too broad, at the cost of maintaining them as Google adds permissions.

**Grant to groups, at the smallest useful scope.** Bindings on individuals do not survive team changes. Bindings at the organisation node apply everywhere, which is why an `Editor` grant there is effectively production admin. Most real grants belong at the project, or on a single resource (a bucket, a topic, a Cloud Run service) where the API supports resource-level policies.

**Service accounts are identities, and their keys are the problem.** A JSON service-account key is a long-lived credential that has been at the root of many GCP incidents. Prefer: attached service accounts for workloads inside GCP (a VM, a Cloud Run service, a GKE Pod), Workload Identity for GKE Pods, and Workload Identity Federation for anything outside GCP (GitHub Actions, AWS workloads, on-premises). Enforce it with the `disableServiceAccountKeyCreation` org policy so the insecure path is unavailable rather than merely discouraged.

**Impersonation instead of keys for humans and automation.** `--impersonate-service-account` mints a short-lived token, requiring `roles/iam.serviceAccountTokenCreator` on the target. This keeps an audit trail of _which human_ acted as the service account - much better than a shared key in a secrets manager.

**Conditions and Deny policies for finer control.** IAM Conditions add constraints on request attributes (resource name prefix, time of day, `request.time` expiry) - for example, temporary elevated access that expires automatically. IAM Deny policies block permissions regardless of grants and evaluate before allows, which is the equivalent of an AWS SCP-style guardrail.

**Verify with tooling, not assumption.** Policy Troubleshooter explains why a specific principal can or cannot do something; Policy Analyzer answers "who can access this resource?"; Recommender proposes role reductions based on 90 days of observed usage. Those recommendations are the fastest route from `Editor` sprawl to least privilege.

## Example

```bash
# Workload Identity Federation: GitHub Actions with no service-account key
gcloud iam workload-identity-pools create github --location=global \
  --display-name="GitHub Actions"

gcloud iam workload-identity-pools providers create-oidc github-oidc \
  --location=global --workload-identity-pool=github \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='acme/checkout'"

# Only the main branch of that repo may impersonate the deployer service account
gcloud iam service-accounts add-iam-policy-binding deployer@payments-prod.iam.gserviceaccount.com \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/$PN/locations/global/workloadIdentityPools/github/attribute.repository/acme/checkout"
```

```bash
# Time-bounded elevated access via an IAM condition
gcloud projects add-iam-policy-binding payments-prod \
  --member="group:oncall-payments@acme.com" \
  --role="roles/cloudsql.admin" \
  --condition='expression=request.time < timestamp("2026-08-10T00:00:00Z"),title=incident-4471'
```

## Interview tips

- "Additive grants, inherited downward, no implicit deny below" is the model to state first.
- Service-account keys are the trap: say you disable their creation by org policy and use federation or impersonation.
- Expect: "how would you prove least privilege?" - IAM Recommender over 90 days of usage, plus Policy Analyzer.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is Google Cloud Platform (GCP)?]] (`#24`): [What is Google Cloud Platform (GCP)?](../cloud-platforms/what-is-google-cloud-platform-gcp.md)
- [[How do you connect an on-premises network to the cloud?]] (`#216`): [How do you connect an on-premises network to the cloud?](../cloud-engineering/how-do-you-connect-an-on-premises-network-to-the-cloud.md)
- [[How do you design least-privilege identity in the cloud?]] (`#217`): [How do you design least-privilege identity in the cloud?](../cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to GCP Engineering](./README.md) · [All topics](../README.md)
