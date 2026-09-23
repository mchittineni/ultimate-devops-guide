---
title: "How do you architect an end-to-end production DevOps project on GCP?"
id: 251
category: "GCP Engineering"
difficulty: "Advanced"
tags:
  - devops
  - gcp-engineering
  - interview-questions
---

# How do you architect an end-to-end production DevOps project on GCP?

**Short answer:** Architect an end-to-end production DevOps project on GCP by building a Global VPC with Shared VPC networks, running GKE Autopilot with Workload Identity Federation (keyless IAM), provisioning Cloud SQL / Cloud Spanner via Terraform, automating pipelines with Cloud Build / GitHub Actions via Workload Identity, and monitoring with Google Cloud Observability (formerly the Cloud Operations suite).

## Detail

Google Cloud Platform's architecture differs fundamentally from other clouds due to its global network SDN backbone, keyless identity model, and managed GKE Autopilot capabilities:

### 1. Global Networking & VPC Architecture

- **Global VPC:** GCP VPCs are global resources spanning all GCP regions naturally.
- **Shared VPC Topology:** Host Project manages shared network subnets, Cloud NAT, and firewall policies, while Service Projects deploy isolated application workloads and their load balancers (with Cloud Armor security policies attached to the backend services).
- **Private Google Access & VPC Service Controls:** Ensures GKE pods and Compute instances communicate with Google APIs (Cloud Storage, BigQuery) over internal Google private IP addresses, surrounded by VPC Service Controls perimeter boundaries.

### 2. Compute & Keyless IAM (GKE Autopilot + Workload Identity)

- **GKE Autopilot:** Production-ready managed Kubernetes where Google manages node provisioning, OS patching, control plane scaling, and security hardening automatically.
- **Workload Identity Federation for GKE:** Kubernetes ServiceAccounts are IAM principals in their own right (`principal://...svc.id.goog/...`), so you grant roles to them directly - or map them to a Google service account where a tool needs one - without generating JSON key files.
- **Cloud SQL / Spanner Database:** Highly available relational data storage configured with Private IP only and Cloud SQL Auth Proxy for secure encrypted access.

### 3. CI/CD & Observability Infrastructure

- **Cloud Build / GitHub Actions:** Authenticated via GCP Workload Identity Federation pools for keyless build execution.
- **Artifact Registry:** Secure storage for container images and Helm charts (OCI), with vulnerability scanning via Artifact Analysis. Container Registry (`gcr.io`) is shut down; `gcr.io` paths are served by Artifact Registry.
- **Google Cloud Observability:** Managed Service for Prometheus, Cloud Logging, and Cloud Trace, fed by OpenTelemetry.

**Trade-offs.** Autopilot and managed services trade control for less toil - no node SSH, per-request pricing, and provider-specific APIs. The global VPC simplifies multi-region routing but makes firewall and route mistakes global, so hierarchical firewall policies and change review on the host project matter.

## Example

**1. GCP Global Production Architecture Diagram:**

```mermaid
graph TD
    User[Global Traffic] --> CloudArmor[Cloud Armor WAF & Global Load Balancer]
    subgraph HostProject["Host Project (Shared VPC Network)"]
        CloudArmor
        SubnetUS[Subnet us-central1]
        SubnetEU[Subnet europe-west1]
    end
    subgraph ServiceProject["Service Project (Application Workloads)"]
        GKE[GKE Autopilot Cluster]
        CloudSQL[Cloud SQL Database - Private IP]
        SecretMgr[Secret Manager]
    end
    CloudArmor --> GKE
    GKE --> CloudSQL
    GKE --> SecretMgr
    GKE --> WorkloadID[Workload Identity Federation]
```

**2. Terraform GCP GKE Autopilot & Workload Identity Module (`main.tf`):**

```hcl
resource "google_compute_network" "custom_vpc" {
  name                    = "prod-global-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "prod_subnet" {
  name          = "prod-us-central1-subnet"
  ip_cidr_range = "10.2.0.0/16"
  region        = "us-central1"
  network       = google_compute_network.custom_vpc.id

  secondary_ip_range {
    range_name    = "pod-ranges"
    ip_cidr_range = "10.100.0.0/16"
  }
  secondary_ip_range {
    range_name    = "service-ranges"
    ip_cidr_range = "10.200.0.0/20"
  }

  private_ip_google_access = true
}

resource "google_container_cluster" "primary" {
  name     = "prod-gke-autopilot"
  location = "us-central1"

  enable_autopilot = true
  network          = google_compute_network.custom_vpc.name
  subnetwork       = google_compute_subnetwork.prod_subnet.name

  ip_allocation_policy {
    cluster_secondary_range_name  = "pod-ranges"
    services_secondary_range_name = "service-ranges"
  }

  # Autopilot enables Workload Identity Federation for GKE automatically
  # (pool: <project-id>.svc.id.goog), so no workload_identity_config block is needed.

  deletion_protection = true
}
```

## Interview tips

- Contrast **GCP Global VPC** with AWS/Azure regional VPCs: GCP subnets exist across multiple regions within the same VPC, simplifying multi-region mesh networking.
- Highlight **GCP Workload Identity Federation**: explain why downloading JSON service account keys is anti-pattern on GCP and how Workload Identity exchanges short-lived tokens.
- Emphasize **GKE Autopilot**: explain how Autopilot shifts node management, OS upgrades, and bin-packing responsibilities to Google SREs while enforcing strict security defaults out of the box.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Cloud Computing?]] (`#21`): [What is Cloud Computing?](../cloud-platforms/what-is-cloud-computing.md)
- [[What is AWS (Amazon Web Services)?]] (`#22`): [What is AWS (Amazon Web Services)?](../cloud-platforms/what-is-aws-amazon-web-services.md)
- [[What is Azure?]] (`#23`): [What is Azure?](../cloud-platforms/what-is-azure.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to GCP Engineering](./README.md) · [All topics](../README.md)
