---
title: "How Does Google Cloud Shared VPC Enable Network Centralization Across Projects?"
id: 745
category: "GCP Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - gcp-engineering
  - shared-vpc
  - networking
  - governance
quiz:
  stem: "In a Google Cloud Shared VPC architecture, what is the role of the 'Host Project'?"
  options:
    - "It hosts the primary web application domain names for public end users."
    - "It centrally contains and manages the shared VPC network, subnets, routes, and firewall rules used by attached service projects."
    - "It generates daily PDF invoices for Google Workspace accounts."
    - "It replaces the Google Cloud Organization node."
  answer: 2
  explanation: "The Host Project holds the centrally managed Shared VPC network, subnets, and routing policies, allowing attached Service Projects to deploy workloads into those subnets with centralized network administration."
---

# How Does Google Cloud Shared VPC Enable Network Centralization Across Projects?

**Short answer:** Google Cloud Shared VPC allows an organization to connect resources from multiple service projects to a single centrally managed VPC network in a host project, enabling network administrators to enforce unified routing, firewall rules, and security policies while delegating compute administration.

## Detail

### The Architectural Challenge of Multi-Project GCP

In Google Cloud, the **Project** is the primary boundary for identity, quotas, billing, and resource management. If every development team creates its own VPC inside its project, connecting them requires complex VPC Network Peering meshes or VPN gateways, leading to IP fragmentation and fragmented firewall auditing.

### How Shared VPC Works

Shared VPC leverages the unique nature of Google Cloud's **global VPC** (a single VPC network that spans all GCP regions worldwide).

1. **Host Project**:
   - Contains the shared VPC network, subnets, cloud routers, NAT gateways, and firewall rules.
   - Administered centrally by the Network / SecOps team.
2. **Service Projects**:
   - Application projects owned by individual development or product teams (e.g., Billing Service, Frontend App).
   - Attached to the Host Project by a Shared VPC Admin.
3. **Subnet Delegation via IAM**:
   - Central network admins grant service project teams the `compute.networkUser` role on **specific subnets only**.
   - Developers can launch GKE clusters, Cloud Run, or Compute Engine VMs within their project, but attach their network interfaces directly to the centrally managed subnets.

```text
                  [Host Project (Central Network & Security)]
                   Shared VPC Network (Global)
                   ├─ Subnet us-central1 (10.1.0.0/24)
                   └─ Subnet europe-west1 (10.2.0.0/24)
                            │                   │
             ┌──────────────┘                   └──────────────┐
             ▼                                                 ▼
[Service Project A: Billing Team]            [Service Project B: Analytics Team]
 GKE Cluster (us-central1)                    Compute VMs (europe-west1)
```

### Architectural Benefits

- **Separation of Duties**: Network engineers manage IP spaces, interconnects, and firewalls; application teams manage workloads without needing network admin privileges.
- **Cross-Service Private Communication**: VMs and pods in Service Project A can communicate with services in Service Project B over internal RFC 1918 IPs without traversing the public internet or configuring VPC peering.
- **Centralized Egress & Inspection**: Interconnects (Dedicated Interconnect, Cloud VPN) and central firewalls in the Host Project serve all projects.

### Real-World Production Scenario

A financial enterprise on GCP maintains 40 distinct development teams across 40 GCP projects. To enforce strict compliance, the central network team creates a Host Project with a Shared VPC. They assign each team a dedicated subnet. All teams communicate privately over internal IPs, while the central team owns egress (Cloud NAT, plus Secure Web Proxy or a firewall appliance for inspection), hierarchical firewall policies, and the Interconnect to on-premises.

## Example

```bash
# Enable the host project and attach a service project (requires Shared VPC Admin at org/folder)
gcloud compute shared-vpc enable net-hub-prod
gcloud compute shared-vpc associated-projects add payments-prod --host-project=net-hub-prod

# Delegate one subnet only to the payments team
gcloud compute networks subnets add-iam-policy-binding sn-payments-euw1 \
  --project=net-hub-prod --region=europe-west1 \
  --member="group:payments-devs@acme.com" \
  --role="roles/compute.networkUser"

# A VM in the service project using the host project's subnet
gcloud compute instances create api-1 --project=payments-prod --zone=europe-west1-b \
  --subnet=projects/net-hub-prod/regions/europe-west1/subnetworks/sn-payments-euw1 --no-address
```

## Interview tips

- Explain the distinction between the Host Project (owns network/subnets) and Service Projects (own compute/workloads).
- Contrast Shared VPC (centralized network governance) with VPC Peering (connecting separate independent networks).
- Highlight that Shared VPC is an organization-level feature requiring both projects to belong to the same Google Cloud Organization, and that a service project can attach to only one host project.
- Know the trade-offs: the host project becomes a shared blast radius and a quota bottleneck, and the network team becomes a dependency for every new subnet; GKE in a service project needs secondary ranges and extra permissions for its service agents in the host project.
- Mention the alternatives for larger estates: multiple host projects (per environment), and Network Connectivity Center as a hub for connecting VPCs.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are Cloud Egress fees and how do you architect networks to minimize them?]] (`#547`): [What are Cloud Egress fees and how do you architect networks to minimize them?](../cloud-platforms/what-are-cloud-egress-fees-and-how-do-you-architect-networks-to-minimize-them.md)
- [[What is the Container Network Interface (CNI) and how do overlay and routed CNI plugins differ?]] (`#528`): [What is the Container Network Interface (CNI) and how do overlay and routed CNI plugins differ?](../kubernetes/what-is-the-container-network-interface-cni-and-how-do-overlay-and-routed-cni-plugins-differ.md)
- [[What is the difference between Service types ClusterIP, NodePort, LoadBalancer, and ExternalName?]] (`#531`): [What is the difference between Service types ClusterIP, NodePort, LoadBalancer, and ExternalName?](../kubernetes/what-is-the-difference-between-service-types-clusterip-nodeport-loadbalancer-and-externalname.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to GCP Engineering](./README.md) · [All topics](../README.md)
