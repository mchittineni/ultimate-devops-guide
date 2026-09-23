---
title: "How Do You Manage Secrets in GCP with Google Cloud Secret Manager and Automatic Rotation?"
id: 748
category: "GCP Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - gcp-engineering
  - secret-manager
  - secrets-rotation
  - cloud-functions
quiz:
  stem: "In Google Cloud Secret Manager, how is automated secret rotation typically triggered and executed?"
  options:
    - "Secret Manager automatically SSHs into all running Compute Engine VMs to edit config files."
    - "Secret Manager publishes a rotation event to a configured Cloud Pub/Sub topic, which triggers a Cloud Function or Cloud Run service to generate and apply the new credential."
    - "Rotating secrets requires opening a manual support ticket with Google Cloud technical engineers."
    - "Secret Manager deletes the entire GCP project if a password is older than 90 days."
  answer: 2
  explanation: "When a rotation schedule matures, Secret Manager sends a notification to a Pub/Sub topic. A subscriber (such as a Cloud Function) consumes the message, provisions the new credential in the target system, and creates the new secret version."
---

# How Do You Manage Secrets in GCP with Google Cloud Secret Manager and Automatic Rotation?

**Short answer:** Google Cloud Secret Manager provides secure, centralized storage for API keys, passwords, and certificates with versioning and IAM access controls. Secret Manager does not rotate anything itself: it publishes a `SECRET_ROTATE` notification to Pub/Sub on schedule, and your handler (typically a Cloud Run service or Cloud Run function) creates the new credential in the target system, adds a new secret version, and disables the old one after a grace period.

## Detail

### Modern Secrets Management in Google Cloud

Hardcoding credentials in source code or relying on unencrypted environment variables creates severe security vulnerabilities.

Google Cloud Secret Manager is a fully managed store with native integration into Cloud IAM, Cloud Audit Logs, Cloud KMS (customer-managed encryption keys), Cloud Run (secrets as env vars or mounted volumes), and GKE (the Secret Manager add-on, based on the Secrets Store CSI driver).

### Core Features of Secret Manager

- **Replication and location**: global secrets use an automatic replication policy (Google chooses locations) or a user-managed policy listing specific regions; **regional secrets** keep the payload in a single region for strict data-residency requirements.
- **Versioning**: Secrets are versioned (e.g., `projects/123/secrets/db-pass/versions/1`). Deployments can target the `latest` alias or pin specific immutable versions.
- **Granular IAM**: Access is governed by Cloud IAM roles such as `roles/secretmanager.secretAccessor` (read payload) and `roles/secretmanager.admin` (manage secret).

### Automated Secrets Rotation Architecture

1. **Configure Rotation Schedule**: Set an automatic rotation period on the secret (e.g., every 30 days) and designate a **Pub/Sub topic**.
2. **Rotation Trigger**: At `next_rotation_time`, Secret Manager publishes a message with the attribute `eventType=SECRET_ROTATE` to the topic. The Secret Manager service agent needs `roles/pubsub.publisher` on that topic.
3. **Rotation Handler (Cloud Run service or Cloud Run function)**:
   - Generates a new random password or API key.
   - Updates the target system (e.g., executes `ALTER USER` on Cloud SQL).
   - Writes the new credential as a new version in Secret Manager via `AddSecretVersion`.
   - Tests connectivity using the new version.
   - Disables or destroys the previous secret version after a designated grace period.

```text
[Secret Manager: Rotation Due (30d)]
                 │
                 ▼ (Pub/Sub Event)
        [Cloud Pub/Sub Topic]
                 │
                 ▼
      [Rotation handler (Cloud Run)]
     ┌───────────┴───────────┐
     ▼                       ▼
[Update Cloud SQL Password] [Create New Version in Secret Manager]
```

### Real-World Production Scenario

A financial reporting service connects to an external banking SFTP server using an API token that expires every 90 days. Engineers configure a 60-day rotation schedule on the secret. When Secret Manager emits the rotation event to Pub/Sub, the rotation handler automatically requests a new token from the bank API, writes version 2 to Secret Manager, and verifies the connection without any manual intervention.

## Example

```bash
# Topic for rotation notifications; the Secret Manager service agent must be able to publish
gcloud pubsub topics create secret-rotation
gcloud pubsub topics add-iam-policy-binding secret-rotation \
  --member="serviceAccount:service-PROJECT_NUMBER@gcp-sa-secretmanager.iam.gserviceaccount.com" \
  --role="roles/pubsub.publisher"

# Secret with a 30-day rotation schedule
gcloud secrets create db-pass \
  --replication-policy=automatic \
  --topics=projects/PROJECT_ID/topics/secret-rotation \
  --rotation-period=2592000s \
  --next-rotation-time="2026-10-01T00:00:00Z"

# The handler adds a new version; least-privilege read access on this one secret only
printf '%s' "$NEW_PASSWORD" | gcloud secrets versions add db-pass --data-file=-
gcloud secrets add-iam-policy-binding db-pass \
  --member="serviceAccount:api@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## Interview tips

- Explain that Secret Manager supports versioning, allowing applications to roll back to previous secret versions if a rotation causes issues.
- Describe the automated rotation pipeline using Pub/Sub and a Cloud Run handler, and stress that you write the rotation logic - Secret Manager only schedules the notification.
- Pin versions in production rather than always reading `latest`, or ensure consumers re-read on failure; a rotated secret cached forever in memory is the classic outage.
- Mention dual-credential rotation (two valid users or keys overlapping) for zero-downtime changes.
- Highlight the principle of least privilege: workloads should only hold `roles/secretmanager.secretAccessor` on the specific secret, not at the project level.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Cloud Computing?]] (`#21`): [What is Cloud Computing?](../cloud-platforms/what-is-cloud-computing.md)
- [[What is Azure?]] (`#23`): [What is Azure?](../cloud-platforms/what-is-azure.md)
- [[What is Google Cloud Platform (GCP)?]] (`#24`): [What is Google Cloud Platform (GCP)?](../cloud-platforms/what-is-google-cloud-platform-gcp.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to GCP Engineering](./README.md) · [All topics](../README.md)
