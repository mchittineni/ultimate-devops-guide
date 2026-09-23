---
title: "How Do AWS Transit Gateway and VPC Peering Compare for Enterprise Interconnectivity?"
id: 729
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - aws-engineering
  - networking
  - transit-gateway
  - vpc-peering
quiz:
  stem: "What is the primary architectural limitation of AWS VPC Peering when attempting to scale connections across dozens of VPCs?"
  options:
    - "VPC Peering forces all traffic to route across the public internet."
    - "VPC Peering does not support transitive routing, requiring a complex point-to-point mesh where every pair of VPCs must have an individual connection."
    - "VPC Peering caps network throughput at 10 Mbps per connection."
    - "VPC Peering can only connect VPCs located in different AWS geographic regions."
  answer: 2
  explanation: "VPC Peering does not allow transitive routing (VPC A cannot talk to VPC C via VPC B). Connecting $N$ VPCs requires a full mesh of $N(N-1)/2$ separate peering connections and complex route table updates."
---

# How Do AWS Transit Gateway and VPC Peering Compare for Enterprise Interconnectivity?

**Short answer:** VPC Peering creates point-to-point connections with lowest latency and zero hourly cost, but does not support transitive routing and becomes unmanageable at scale (a full mesh grows as N²). AWS Transit Gateway acts as a central cloud router supporting transitive routing, VPNs, and Direct Connect across thousands of VPCs.

## Detail

### The Evolution of Cloud Networking Topology

As organizations scale into multi-account and multi-VPC architectures (AWS Control Tower, Landing Zones), connecting VPCs efficiently is a fundamental architectural decision.

### VPC Peering: Low Latency Point-to-Point

VPC Peering connects two VPCs using AWS private network infrastructure.

- **Transitive Routing**: **Not supported**. If VPC A is peered to VPC B, and VPC B is peered to VPC C, VPC A **cannot** communicate with VPC C through VPC B.
- **Mesh Complexity**: Connecting N VPCs requires N(N-1)/2 peering connections. Connecting 10 VPCs requires 45 peering connections; 100 VPCs requires 4,950 peering connections.
- **Cost**: No hourly charge; only standard data transfer fees (traffic within the same AZ over peering is free; cross-AZ and cross-region traffic is charged).
- **Performance**: Maximum bandwidth with no packet processing bottleneck or added hop latency.

### AWS Transit Gateway (TGW): Central Hub-and-Spoke

Transit Gateway acts as a regional managed virtual router.

- **Transitive Routing**: **Fully supported**. VPCs, on-premises VPNs, and AWS Direct Connect attach to the TGW and route through central route tables.
- **Scale**: Supports up to 5,000 attachments per gateway across multiple AWS accounts via AWS Resource Access Manager (RAM).
- **Network Segmentation**: Supports multiple route tables to isolate environments (e.g., Prod VPCs cannot reach Dev VPCs, but both reach Shared Services).
- **Cost**: Incurs an hourly charge per attachment plus a data processing fee per GB routed through the gateway.
- **Limitations**: TGW is regional (cross-region needs TGW peering, which does not propagate routes dynamically), adds a hop, and its per-GB fee makes it expensive for very chatty VPC pairs - which is why a common hybrid keeps direct peering for the heaviest pair alongside a TGW backbone. For very large multi-region estates, Cloud WAN manages TGW-style segmentation globally.

```text
VPC Peering (Full Mesh Complexity)      Transit Gateway (Hub and Spoke)

    [VPC A] ────── [VPC B]                   [VPC A]       [VPC B]
       │    ╲    ╱    │                         │             │
       │      ╳       │                         ▼             ▼
       │    ╱    ╲    │                    ┌───────────────────────┐
    [VPC C] ────── [VPC D]                 │ AWS Transit Gateway   │
                                           └───────────────────────┘
                                                ▲             ▲
                                                │             │
                                             [VPC C]     [On-Premises]
```

### Architectural Comparison

| Feature                 | VPC Peering                                    | AWS Transit Gateway                          |
| :---------------------- | :--------------------------------------------- | :------------------------------------------- |
| **Topology**            | 1-to-1 Point-to-point mesh                     | Hub-and-spoke router                         |
| **Transitive Routing**  | No                                             | Yes                                          |
| **Max Connections**     | Limited routing table limits                   | Up to 5,000 attachments                      |
| **Hybrid Connectivity** | Cannot peer Direct Connect/VPN directly        | Directly attaches Direct Connect & VPN       |
| **Hourly Cost**         | $0.00 / hour                                   | Hourly fee per attachment + processing fee   |
| **Best Used For**       | High-throughput, latency-critical 1-to-1 pairs | Enterprise multi-account, multi-VPC networks |

### Real-World Production Scenario

An enterprise migrates from 3 VPCs to 60 VPCs across 20 AWS accounts under AWS Organizations. Managing over 1,700 peering connections and individual routing tables becomes untenable. The network team deploys an AWS Transit Gateway shared via AWS RAM, creating a central hub that reduces route management to three centralized route tables (Production, Non-Production, and Shared Services).

## Example

```hcl
# One TGW in the network account, shared to the organization with RAM
resource "aws_ec2_transit_gateway" "hub" {
  description                     = "org-hub"
  default_route_table_association = "disable" # explicit route tables = segmentation
  default_route_table_propagation = "disable"
}

resource "aws_ram_resource_share" "tgw" {
  name                      = "tgw-hub"
  allow_external_principals = false
}

resource "aws_ram_resource_association" "tgw" {
  resource_arn       = aws_ec2_transit_gateway.hub.arn
  resource_share_arn = aws_ram_resource_share.tgw.arn
}

resource "aws_ram_principal_association" "org" {
  principal          = "arn:aws:organizations::111122223333:organization/o-abc123"
  resource_share_arn = aws_ram_resource_share.tgw.arn
}

# Direct peering kept for the one chatty pair, to avoid TGW per-GB processing
resource "aws_vpc_peering_connection" "analytics_to_lake" {
  vpc_id      = aws_vpc.analytics.id
  peer_vpc_id = aws_vpc.datalake.id
  auto_accept = true # same account and region
}
```

## Interview tips

- State clearly that VPC Peering is non-transitive (A-B and B-C does not allow A-C).
- Explain the mathematical complexity of full-mesh peering: N(N-1)/2.
- Highlight the cost trade-off: VPC peering has no hourly or data processing fee, making it cheaper for high-throughput single-pair traffic.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are Cloud Egress fees and how do you architect networks to minimize them?]] (`#547`): [What are Cloud Egress fees and how do you architect networks to minimize them?](../cloud-platforms/what-are-cloud-egress-fees-and-how-do-you-architect-networks-to-minimize-them.md)
- [[How does CoreDNS resolve services in Kubernetes and how do you troubleshoot DNS latency bottlenecks?]] (`#527`): [How does CoreDNS resolve services in Kubernetes and how do you troubleshoot DNS latency bottlenecks?](../kubernetes/how-does-coredns-resolve-services-in-kubernetes-and-how-do-you-troubleshoot-dns-latency-bottlenecks.md)
- [[How does the Kubernetes Gateway API evolve beyond standard Ingress resources?]] (`#520`): [How does the Kubernetes Gateway API evolve beyond standard Ingress resources?](../kubernetes/how-does-the-kubernetes-gateway-api-evolve-beyond-standard-ingress-resources.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
