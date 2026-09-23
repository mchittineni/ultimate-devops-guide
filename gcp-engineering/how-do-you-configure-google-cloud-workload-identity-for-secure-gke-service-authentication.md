---
title: "How Do You Configure Google Cloud Workload Identity for Secure GKE Service Authentication?"
id: 746
category: "GCP Engineering"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - gcp-engineering
  - gke
  - workload-identity
  - iam
  - security
quiz:
  stem: "What is the primary security advantage of using GKE Workload Identity over traditional service account keys?"
  options:
    - "It enables pods to access the internet without an egress NAT gateway."
    - "It eliminates the need to generate, store, and rotate long-lived private JSON service account keys by issuing short-lived OAuth tokens directly to mapped Kubernetes ServiceAccounts."
    - "It encrypts all container image layers with AES-512 before pulling."
    - "It bypasses Kubernetes RBAC validation for faster deployment."
  answer: 2
  explanation: "Workload Identity links Kubernetes ServiceAccounts directly to Google ServiceAccounts, generating short-lived tokens dynamically via the GKE metadata server and eliminating the risk of leaked static JSON key files."
---

# How Do You Configure Google Cloud Workload Identity for Secure GKE Service Authentication?

**Short answer:** Workload Identity Federation for GKE (formerly just "Workload Identity") makes each Kubernetes ServiceAccount (KSA) an IAM principal in the cluster's workload identity pool (`PROJECT_ID.svc.id.goog`). You either grant IAM roles to that KSA principal directly, or - the older pattern, still needed for some APIs - let the KSA impersonate a Google service account (GSA). Pods get short-lived access tokens from the GKE metadata server, so there is no JSON key to store, mount, or rotate.

## Detail

### The Hazard of Static Service Account Keys

Historically, when a pod in GKE needed to access GCP resources (e.g., Cloud Storage, BigQuery, Secret Manager), developers exported a private JSON key for a Google Service Account (GSA) and stored it as a Kubernetes Secret.

- Keys are long-lived (valid for years unless manually revoked).
- Keys are frequently leaked into git repositories, container logs, or CI/CD pipelines.
- Node-level service accounts grant overly broad permissions to every pod running on that node.

**Workload Identity** is the recommended best practice for authenticating GKE workloads to Google Cloud services.

### How Workload Identity Functions

With the node pool's metadata mode set to `GKE_METADATA`, a GKE metadata server DaemonSet on each node intercepts Pod calls to the metadata endpoint (`metadata.google.internal` / `169.254.169.254`). It identifies the calling Pod, obtains a signed token for its KSA, exchanges it at Google's Security Token Service for a federated access token, and - if the KSA is configured to impersonate a GSA - exchanges that for the GSA's access token. Client libraries using Application Default Credentials pick this up with no code change.

**Limitations.** Pods using `hostNetwork: true` cannot use it; all clusters in one project share the same pool, so `ns/payments/sa/api` in any cluster of the project is the same principal (keep untrusted clusters in separate projects); and a few Google APIs still do not accept federated principals directly, which is when you fall back to GSA impersonation.

### Configuration Workflow

1. **Enable it on the cluster and node pool** (Autopilot clusters have it on permanently):

   ```bash
   gcloud container clusters update CLUSTER_NAME --location=LOCATION \
       --workload-pool=PROJECT_ID.svc.id.goog
   gcloud container node-pools update POOL_NAME --cluster=CLUSTER_NAME \
       --location=LOCATION --workload-metadata=GKE_METADATA
   ```

2. **Preferred: grant the role directly to the KSA principal** (no GSA needed):

   ```bash
   gcloud storage buckets add-iam-policy-binding gs://acme-reports \
       --role=roles/storage.objectViewer \
       --member="principal://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/PROJECT_ID.svc.id.goog/subject/ns/default/sa/my-ksa"
   ```

3. **Alternative (GSA impersonation) - create the Google Service Account**:

   ```bash
   gcloud iam service-accounts create my-gsa
   gcloud projects add-iam-policy-binding PROJECT_ID \
       --member="serviceAccount:my-gsa@PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/storage.objectViewer"
   ```

4. **Allow the KSA to impersonate the GSA**:

   ```bash
   gcloud iam service-accounts add-iam-policy-binding \
       my-gsa@PROJECT_ID.iam.gserviceaccount.com \
       --role="roles/iam.workloadIdentityUser" \
       --member="serviceAccount:PROJECT_ID.svc.id.goog[default/my-ksa]"
   ```

5. **Annotate the KSA** (only for the impersonation pattern):

   ```yaml
   apiVersion: v1
   kind: ServiceAccount
   metadata:
     name: my-ksa
     namespace: default
     annotations:
       iam.gke.io/gcp-service-account: my-gsa@PROJECT_ID.iam.gserviceaccount.com
   ```

```text
[Pod running under KSA 'my-ksa']
               │
               ▼
[GKE Metadata Server DaemonSet]
               │ (Validates KSA token against PROJECT_ID.svc.id.goog)
               ▼
[Google Cloud IAM Service]
               │ (Issues short-lived OAuth2 Token)
               ▼
[Pod accesses Google Cloud Storage securely]
```

### Real-World Production Scenario

A payments microservice running on GKE needs to write audit logs to BigQuery. Instead of mounting a service account JSON secret into the pod, the DevOps engineer enables Workload Identity Federation for GKE, grants the Pod's Kubernetes ServiceAccount principal the BigQuery Data Editor role on the one dataset it writes to, and allows the Google Cloud SDK inside the container to authenticate automatically via short-lived tokens.

## Example

Verify from inside a Pod that it is using its federated identity rather than the node's service account:

```bash
kubectl run wi-test -n default --rm -it --restart=Never \
  --image=google/cloud-sdk:slim \
  --overrides='{"spec":{"serviceAccountName":"my-ksa"}}' \
  -- bash -c 'curl -s -H "Metadata-Flavor: Google" \
       http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email; echo; \
     gcloud storage ls gs://acme-reports'
# Direct grant: prints PROJECT_ID.svc.id.goog; with impersonation: prints the GSA email
```

## Interview tips

- State clearly: Workload Identity eliminates downloadable, long-lived JSON service account keys.
- Explain that the GKE metadata server intercepts metadata requests to issue short-lived tokens per pod.
- Compare with AWS: EKS Pod Identity (an agent on the node, like the GKE metadata server) and IRSA (projected OIDC token exchanged at STS).
- Know the direct-grant `principal://` form versus the older GSA-annotation form, and when you still need the GSA.
- Mention the shared-pool caveat: the same namespace/KSA name in any cluster of the project is the same identity.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does Cloud IAM Role Federation differ from static Service Account keys?]] (`#546`): [How does Cloud IAM Role Federation differ from static Service Account keys?](../cloud-platforms/how-does-cloud-iam-role-federation-differ-from-static-service-account-keys.md)
- [[How does the Cloud Shared Responsibility Model divide security obligations between IaaS, PaaS, and SaaS?]] (`#543`): [How does the Cloud Shared Responsibility Model divide security obligations between IaaS, PaaS, and SaaS?](../cloud-platforms/how-does-the-cloud-shared-responsibility-model-divide-security-obligations-between-iaas-paas-and-saas.md)
- [[What is the difference between Mutating and Validating Admission Webhooks in Kubernetes?]] (`#524`): [What is the difference between Mutating and Validating Admission Webhooks in Kubernetes?](../kubernetes/what-is-the-difference-between-mutating-and-validating-admission-webhooks-in-kubernetes.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to GCP Engineering](./README.md) · [All topics](../README.md)
