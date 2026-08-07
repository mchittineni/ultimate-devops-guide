---
title: "How do you connect an on-premises network to the cloud?"
id: 216
category: "Cloud Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - cloud-engineering
  - interview-questions
---

# How do you connect an on-premises network to the cloud?

**Short answer:** Either an IPsec VPN over the internet — quick, cheap, bandwidth-limited by the internet path — or a dedicated private circuit (AWS Direct Connect, Azure ExpressRoute, Google Cloud Interconnect) for consistent latency, higher throughput, and lower egress rates. Production designs usually run a dedicated circuit with a VPN as automatic backup, with BGP handling failover.

## Detail

| Option            | Set-up time  | Bandwidth                 | Latency             | Typical use                               |
| ----------------- | ------------ | ------------------------- | ------------------- | ----------------------------------------- |
| Site-to-site VPN  | hours        | up to ~1–5 Gbps aggregate | variable (internet) | dev, small offices, backup path           |
| Dedicated circuit | weeks–months | 1–100 Gbps                | consistent          | production, migrations, latency-sensitive |
| SD-WAN / partner  | days–weeks   | flexible                  | good                | many branch sites                         |

**Redundancy is the design requirement.** A single circuit is a single point of failure with a multi-week repair time — the standard is two circuits at different physical locations and, ideally, different providers, plus a VPN as a tertiary path. Provider SLAs on private circuits are usually contingent on having redundant connections, which is a detail worth knowing.

**BGP is how failover works.** Advertise routes with AS-path prepending or MED to prefer the circuit and fall back to VPN; accept a summarised set of on-premises prefixes; and respect route limits (each provider caps advertised prefixes per session). Watch for asymmetric routing, where traffic leaves via one path and returns via another and stateful firewalls drop it — this is the most common hybrid connectivity bug.

**Address planning must come first.** Overlapping RFC 1918 ranges between on-premises and cloud is the mistake that forces NAT and haunts the estate for years. Reserve non-overlapping ranges per cloud, per region, and per environment before the first VPC exists, and keep a single authoritative IPAM record.

**DNS resolution both ways.** Cloud workloads must resolve on-premises names and vice versa: conditional forwarders on-premises pointing at cloud resolvers (Route 53 Resolver inbound endpoints, Azure DNS Private Resolver, Cloud DNS forwarding zones) and outbound rules pointing at on-premises DNS. Hybrid DNS failure looks exactly like a network problem and consumes hours of debugging, so test it explicitly.

**Egress cost is the quiet driver.** Data leaving the cloud over the internet is expensive; over a dedicated circuit it is markedly cheaper. For workloads that continuously send data back to a data centre, circuit costs can be lower than internet egress alone — that calculation, done honestly, often justifies the circuit on its own.

**Encryption.** A dedicated circuit is private but not encrypted; if your compliance regime requires encryption in transit, run IPsec or MACsec over it, or terminate TLS end to end at the application layer. Interviewers like this question because "it is a private link" is a common and incomplete answer.

## Example

```text
Production hybrid topology

  On-premises DC-A ──┬── Direct Connect / ExpressRoute #1 ──┐
                     │                                       ├── Cloud hub network
  On-premises DC-B ──┴── Direct Connect / ExpressRoute #2 ──┤    (transit gateway /
                                                            │     virtual WAN / NCC)
                        IPsec VPN (tertiary, BGP backup) ────┘

BGP: prefer circuits (lower MED), VPN advertised with AS-path prepend x3
Address plan: on-prem 172.16.0.0/12 · cloud 10.40.0.0/12 · no overlap ever
DNS: on-prem conditional forwarder -> cloud inbound resolver
     cloud outbound rules -> on-prem DNS for corp.acme.internal
Encryption: MACsec on the circuits; TLS end to end regardless
Test quarterly: fail circuit #1, confirm convergence and no asymmetric drops
```

## Interview tips

- Give the VPN-versus-dedicated trade-off, then say production uses both with BGP failover.
- Non-overlapping address planning and hybrid DNS are the two failures that cause the most real pain — mention both.
- Expect: "is a dedicated circuit encrypted?" — no; add IPsec/MACsec or rely on application-layer TLS.

---

[⬅ Back to Cloud Engineering](./README.md) · [All topics](../README.md)
