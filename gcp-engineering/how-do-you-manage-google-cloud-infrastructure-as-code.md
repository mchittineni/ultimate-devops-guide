---
title: "How do you manage Google Cloud infrastructure as code?"
id: 213
category: "GCP Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - gcp-engineering
  - interview-questions
---

# How do you manage Google Cloud infrastructure as code?

**Short answer:** Terraform (or OpenTofu) is the mainstream choice, usually with Google's Cloud Foundation Toolkit modules, state in a versioned GCS bucket, and plans gated in CI. Config Connector is the Kubernetes-native alternative when you want to manage Google resources as custom resources reconciled inside GKE. Deployment Manager is deprecated - say so if it comes up.

## Detail

**Terraform with a GCS backend.** GCS supports object versioning and native state locking, so the backend is simple: one bucket, versioning on, per-environment prefixes so a broken plan cannot touch another environment. Blast radius is controlled by splitting state - foundation (org policies, folders, projects), networking, and per-workload - rather than one monolithic state file that takes 20 minutes to plan.

**Use the Cloud Foundation Toolkit for the boring parts.** Google-maintained modules cover project factory, networking, GKE, Cloud SQL, and log export, and encode the practices you would otherwise rediscover. A platform team wraps them in internal modules with organisation defaults (labels, regions, KMS keys) - the golden-path pattern.

**Authenticate without keys.** Terraform running in CI should use Workload Identity Federation to impersonate a deployer service account, not a downloaded JSON key. Combine with the `disableServiceAccountKeyCreation` org policy so nobody can create the insecure alternative.

**Config Connector for Kubernetes-native reconciliation.** Google resources become CRDs (`SQLInstance`, `PubSubTopic`, `StorageBucket`) reconciled continuously by a controller in GKE, so drift is corrected automatically and application teams request infrastructure with the same manifests and GitOps flow as their workloads. It suits platforms already fully invested in Kubernetes; the cost is running the controller, weaker preview than `terraform plan`, and uneven resource coverage.

**Policy gates over the plan.** Run `terraform plan -json` through Conftest/OPA or Policy Library constraints in the pull request: mandatory labels, approved regions, no public IPs, no `Editor` bindings, encryption keys required. Org policies still enforce the same intent at the API as the non-bypassable boundary - the pipeline exists for fast feedback, not as the security control.

**Project factory and bootstrapping.** Creating projects requires elevated permissions, so a bootstrap project holds the deployer identity and the state bucket, and everything else is created by pipeline. That answers the chicken-and-egg question interviewers like to ask about how the first resources get created.

## Example

```hcl
terraform {
  required_version = "~> 1.9"
  backend "gcs" {
    bucket = "acme-tfstate-prod"
    prefix = "payments/networking"
  }
  required_providers {
    google = { source = "hashicorp/google", version = "~> 6.8" }
  }
}

# CI impersonates the deployer SA via Workload Identity Federation - no keys
provider "google" {
  project                     = var.project_id
  region                      = "europe-west1"
  impersonate_service_account = "deployer@payments-prod.iam.gserviceaccount.com"
}

module "vpc" {
  source  = "terraform-google-modules/network/google"
  version = "~> 9.3"

  project_id   = var.project_id
  network_name = "vpc-prod"

  subnets = [{
    subnet_name           = "sn-prod-euw1"
    subnet_ip             = "10.70.0.0/20"
    subnet_region         = "europe-west1"
    subnet_private_access = true
    subnet_flow_logs      = true
  }]

  secondary_ranges = {
    sn-prod-euw1 = [
      { range_name = "pods", ip_cidr_range = "10.71.0.0/16" },
      { range_name = "services", ip_cidr_range = "10.72.0.0/20" },
    ]
  }
}
```

## Interview tips

- Say Deployment Manager is deprecated and name Terraform plus Config Connector as the live options.
- State splitting (foundation / network / workload) is the answer to "how do you keep plans safe and fast?".
- Expect: "how does Terraform authenticate?" - Workload Identity Federation and impersonation, never a JSON key.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is Cloud Computing?]] (`#21`): [What is Cloud Computing?](../cloud-platforms/what-is-cloud-computing.md)
- [[What is Azure?]] (`#23`): [What is Azure?](../cloud-platforms/what-is-azure.md)
- [[What is Google Cloud Platform (GCP)?]] (`#24`): [What is Google Cloud Platform (GCP)?](../cloud-platforms/what-is-google-cloud-platform-gcp.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to GCP Engineering](./README.md) · [All topics](../README.md)
