---
title: "How does networking differ across AWS, Azure, and GCP?"
id: 282
category: "Cloud Platforms"
difficulty: "Advanced"
tags:
  - devops
  - cloud-platforms
  - interview-questions
---

# How does networking differ across AWS, Azure, and GCP?

**Short answer:** The vocabulary rhymes but the topology does not. **AWS** VPCs are regional with per-AZ subnets and per-resource security groups. **Azure** VNets are regional with subnet-level NSGs, and its identity-and-network model leans on resource groups and service endpoints / private endpoints. **GCP** VPCs are **global** - one VPC spans every region, with regional subnets and firewall rules attached to network tags or service accounts. That single difference reshapes multi-region design: on GCP a global VPC needs no peering between regions, while on AWS and Azure cross-region always means peering or a transit hub.

## Detail

**Scope of the virtual network.**

| Concept                | AWS                               | Azure                                  | GCP                                            |
| ---------------------- | --------------------------------- | -------------------------------------- | ---------------------------------------------- |
| Network object         | VPC (**regional**)                | VNet (**regional**)                    | VPC (**global**)                               |
| Subnet scope           | One AZ                            | Spans zones within the region          | Regional (spans zones)                         |
| Per-instance firewall  | Security group (stateful)         | NSG (subnet or NIC), ASGs for grouping | VPC firewall rules by tag / service account    |
| Subnet-level ACL       | Network ACL (stateless)           | NSG at subnet                          | Hierarchical firewall policies                 |
| Cross-network          | VPC peering, Transit Gateway      | VNet peering, Virtual WAN              | VPC peering, Network Connectivity Center       |
| Private access to PaaS | VPC endpoints / PrivateLink       | Service endpoints, Private Endpoint    | Private Service Connect, Private Google Access |
| Hybrid                 | Direct Connect, Site-to-Site VPN  | ExpressRoute, VPN Gateway              | Cloud Interconnect, Cloud VPN                  |
| Managed egress         | NAT Gateway (per-AZ, per-AZ cost) | NAT Gateway (regional)                 | Cloud NAT (regional, no per-AZ instance)       |
| L7 global entry        | CloudFront + ALB                  | Front Door + App Gateway               | Global external Application Load Balancer      |

**Where the models genuinely diverge, not just in naming:**

- **Global VPC (GCP).** Subnets in `us-central1` and `europe-west1` sit in one VPC with private RFC1918 reachability and no peering. Design consequence: fewer moving parts for multi-region, but a single blast radius for firewall and routing mistakes, and hierarchical firewall policies at the folder/org level become the control you actually manage.
- **Load balancer anycast (GCP).** GCP's global load balancer is a single anycast IP fronting backends in many regions. AWS and Azure achieve global entry by layering a CDN/edge service (CloudFront, Front Door) in front of regional load balancers, which means an extra tier and extra config.
- **Firewall attachment model.** AWS security groups are referenceable objects - a rule can allow "traffic from security group X", which is effectively identity-based microsegmentation. GCP firewall rules can target **service accounts**, which is even closer to identity. Azure NSGs are CIDR/tag-based with Application Security Groups as the grouping mechanism; the mental model is closer to a traditional firewall.
- **NAT and egress economics.** AWS NAT Gateways are per-AZ resources you pay for hourly _and_ per GB, and cross-AZ traffic to a NAT in another zone is an easy accidental cost. Cloud NAT on GCP is a regional configuration with no per-zone instances. Egress pricing differs enough between providers to change architecture decisions for data-heavy workloads.
- **Private connectivity to managed services.** AWS PrivateLink, Azure Private Endpoint, and GCP Private Service Connect solve the same problem, but the DNS integration differs materially - Azure requires private DNS zones linked to the VNet, and forgetting that link is the single most common "it resolves to a public IP" failure.
- **IP address planning.** Azure reserves five addresses per subnet; AWS reserves five; GCP reserves four. More importantly, secondary IP ranges (alias IPs) on GCP are how GKE assigns Pod addresses, so a GKE cluster consumes far more address space than the node count suggests. Undersized CIDR blocks are the mistake that forces a rebuild.

**Practical multi-cloud consequence.** Overlapping RFC1918 ranges across providers make interconnection painful, so allocate non-overlapping CIDR space per provider _and_ per region from day one, from a single registry. Transit-hub designs (Transit Gateway, Virtual WAN, Network Connectivity Center) are the right pattern once you exceed a handful of peerings, because full-mesh peering scales quadratically and peering is non-transitive on all three providers.

## Example

```hcl
# AWS: regional VPC, subnets pinned to AZs, security group referencing another SG.
resource "aws_vpc" "main" { cidr_block = "10.10.0.0/16" }

resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.10.1.0/24"
  availability_zone = "eu-west-1a" # subnets are per-AZ on AWS
}

resource "aws_security_group_rule" "db_from_app" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  security_group_id        = aws_security_group.db.id
  source_security_group_id = aws_security_group.app.id # identity, not CIDR
}
```

```hcl
# GCP: one global VPC, regional subnets, no peering needed between regions.
resource "google_compute_network" "main" {
  name                    = "main"
  auto_create_subnetworks = false # global network, explicit subnets
}

resource "google_compute_subnetwork" "us" {
  name          = "us"
  network       = google_compute_network.main.id
  region        = "us-central1"
  ip_cidr_range = "10.20.0.0/20"
  secondary_ip_range { # GKE Pods live here - size it generously
    range_name    = "pods"
    ip_cidr_range = "10.60.0.0/14"
  }
}

resource "google_compute_firewall" "db_from_app" {
  name                    = "db-from-app"
  network                 = google_compute_network.main.id
  direction               = "INGRESS"
  source_service_accounts = ["app@project.iam.gserviceaccount.com"] # identity-based
  target_service_accounts = ["db@project.iam.gserviceaccount.com"]
  allow { protocol = "tcp" ports = ["5432"] }
}
```

```bash
# The classic Azure private-endpoint failure: the DNS zone is not linked to the VNet.
az network private-dns link vnet list \
  --resource-group net-rg --zone-name privatelink.database.windows.net -o table
nslookup mydb.database.windows.net   # must return a 10.x address, not a public one
```

## Interview tips

- Lead with the one structural difference - GCP's VPC is global, AWS and Azure VNets/VPCs are regional. Everything else follows from it.
- Map the vocabulary quickly (VPC/VNet, SG/NSG, Direct Connect/ExpressRoute/Interconnect) and then move to where the models actually differ. Vocabulary alone is table stakes.
- Know that security groups and GCP firewall rules can reference identities (SGs, service accounts) while NSGs are CIDR/tag-based. That is real microsegmentation design.
- Mention peering is non-transitive on all three, and that transit hubs exist because full-mesh peering scales quadratically.
- Have the private-endpoint DNS trap ready - it is the most common practical failure and shows hands-on time.
- Bring up CIDR planning and GKE secondary ranges. Address exhaustion forcing a cluster rebuild is a story interviewers recognise immediately.

---

[⬅ Back to Cloud Platforms](./README.md) · [All topics](../README.md)
