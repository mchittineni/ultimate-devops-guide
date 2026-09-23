---
title: "What are AWS Direct Connect and Azure ExpressRoute and when are dedicated hybrid connections necessary?"
id: 695
category: "Cloud Migration"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - cloud-migration
  - networking
  - direct-connect
  - expressroute
  - hybrid
quiz:
  stem: "What is the primary financial advantage of using AWS Direct Connect instead of an internet-based IPSec VPN for massive daily data transfers?"
  options:
    - "Direct Connect eliminates all server CPU costs"
    - "AWS charges significantly lower per-gigabyte data egress rates over Direct Connect compared to standard public internet data transfer"
    - "Direct Connect provides free unlimited S3 storage"
    - "Direct Connect eliminates the need for network routers"
  answer: 2
  explanation: "In addition to high bandwidth and predictable latency, cloud providers offer heavily discounted per-GB egress rates over dedicated interconnects like Direct Connect."
---

# What are AWS Direct Connect and Azure ExpressRoute and when are dedicated hybrid connections necessary?

**Short answer:** AWS Direct Connect and Azure ExpressRoute are private, dedicated connections between your network and the cloud provider's backbone - usually via a cross-connect in a colocation facility or through a connectivity partner - that bypass the public internet for predictable latency, high bandwidth (up to 100 Gbps per port, with 400 Gbps Direct Connect ports in some locations), and lower data-transfer-out rates.

## Detail

An IPsec VPN over the internet is quick to set up and encrypted, but it inherits the internet's variability (jitter, packet loss, congestion at peering points) and has per-tunnel throughput limits - historically 1.25 Gbps per AWS Site-to-Site VPN tunnel, raised to 5 Gbps for large-bandwidth tunnels in late 2025, with ECMP across tunnels for more.

### How dedicated interconnects work

- **Physical path**: a fibre cross-connect in a colocation facility (Equinix, Digital Realty, and others) from your router to the provider's edge router, or a **hosted connection** of 50 Mbps-25 Gbps through a partner if you are not in the building.
- **Logical path**: BGP sessions over VLANs. Direct Connect uses **virtual interfaces** - private (to a VPC via a virtual private gateway or Direct Connect gateway), transit (to Transit Gateways), and public (to AWS public endpoints). ExpressRoute uses **private peering** (to VNets) and **Microsoft peering** (to Microsoft 365 and public services).
- **Scale-out**: a Direct Connect gateway or ExpressRoute Global Reach connects many regions or on-prem sites over the same circuits.

### When a dedicated connection is justified

1. **Large or continuous data movement**: a 100 TB migration takes about 9 days at a sustained 1 Gbps but under a day at 10 Gbps; continuous replication and backup traffic benefit even more.
2. **Latency-sensitive hybrid architectures**: systems that stay on-premises (mainframes, factory systems) calling cloud services need low, _predictable_ latency - a few milliseconds within a metro, bounded by distance, not "sub-millisecond" across a country.
3. **Data transfer cost**: data transferred out of AWS over Direct Connect is billed at a much lower per-GB rate than internet egress, which pays for the port at sustained volumes. Check current pricing for your location; the saving depends on volume and region.
4. **Compliance and routing control**: traffic stays off the public internet and on known paths.

### Common misconceptions and trade-offs

- **Private is not encrypted.** Direct Connect and ExpressRoute do not encrypt traffic by default. Use MACsec on supported dedicated ports (10/100/400 Gbps), or run IPsec over the circuit, or rely on TLS end to end.
- **One circuit is a single point of failure.** Resilient designs use two connections at two separate locations (AWS's "maximum resiliency" model uses two per location across two locations), with a VPN as a lower-cost backup path.
- **Lead time**: ordering ports and cross-connects takes weeks; a VPN gets a migration started while the circuit is provisioned.
- **Fixed cost**: port-hours are charged whether or not you use the bandwidth, so low-volume sites are often better served by VPN.

## Example

```hcl
# Direct Connect: a private virtual interface over an existing dedicated connection,
# terminating on a Direct Connect gateway so several VPCs/regions can use it.
resource "aws_dx_gateway" "hybrid" {
  name            = "hybrid-dxgw"
  amazon_side_asn = "64512"
}

resource "aws_dx_private_virtual_interface" "primary" {
  connection_id    = var.dx_connection_id_site_a # a second one uses the connection at site B
  name             = "vif-primary-site-a"
  vlan             = 101
  address_family   = "ipv4"
  bgp_asn          = 65010 # on-premises router ASN
  dx_gateway_id    = aws_dx_gateway.hybrid.id
  mtu              = 9001 # jumbo frames for bulk transfer
}

resource "aws_dx_gateway_association" "prod_vpc" {
  dx_gateway_id         = aws_dx_gateway.hybrid.id
  associated_gateway_id = aws_vpn_gateway.prod.id
  allowed_prefixes      = ["10.20.0.0/16"]
}
```

## Interview tips

- Explain what it is physically (cross-connect or hosted connection) and logically (BGP over VLANs, virtual interfaces or peerings).
- Justify it with numbers: transfer time at a given bandwidth, latency predictability, and data-transfer-out savings at volume.
- Correct the two common misconceptions: private is not encrypted (use MACsec or IPsec), and one circuit is not resilient.
- Mention VPN as the fast-start and backup path, and that VPN tunnel limits have risen (5 Gbps tunnels on AWS).
- Close with the cost trade-off: fixed port charges and weeks of lead time versus a VPN's flexibility.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do Docker bridge, host, and macvlan network drivers differ in packet routing and isolation?]] (`#517`): [How do Docker bridge, host, and macvlan network drivers differ in packet routing and isolation?](../docker/how-do-docker-bridge-host-and-macvlan-network-drivers-differ-in-packet-routing-and-isolation.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Migration](./README.md) · [All topics](../README.md)
