---
title: "How do you plan CIDR ranges and subnets?"
id: 490
category: "Network Security"
difficulty: "Intermediate"
tags:
  - devops
  - network-security
  - interview-questions
  - cloud-engineering
  - aws-engineering
---

# How do you plan CIDR ranges and subnets?

**Short answer:** Allocate from the top down and never reuse a range. Pick a large private block for the organisation (say `10.0.0.0/8`), carve a **non-overlapping** block per environment and region, then a VPC/VNet per account from that, then subnets per tier per availability zone. The arithmetic you must be able to do live: a `/n` prefix means the first **n** bits are the network, leaving **32 − n** host bits, so the block holds **2^(32−n)** addresses - `/24` = 256, `/22` = 1,024, `/16` = 65,536, and `/32` is exactly one address (one specific host, which is why security group rules use `10.1.2.3/32`). In AWS and Azure you lose **5 addresses per subnet** to the platform, so a `/24` gives 251 usable. To decide whether an address is inside a block, compare only the network bits: `10.11.7.44` **is** inside `10.11.0.0/16` (first 16 bits `10.11` match), while `10.11.44.76` is **not** inside `10.1.0.0/16` (`10.11` ≠ `10.1`). The rule that matters more than any calculation: **size subnets generously and leave gaps**, because you cannot renumber a production VPC and overlapping ranges are what block peering, Transit Gateway, and VPN years later.

## Detail

### The arithmetic, quickly

| Prefix | Addresses  | Usable in AWS/Azure | Typical use                                 |
| ------ | ---------- | ------------------- | ------------------------------------------- |
| `/32`  | 1          | 1                   | A single host in a rule or route            |
| `/28`  | 16         | 11                  | Tiny subnet (TGW attachment, endpoints)     |
| `/26`  | 64         | 59                  | Data tier, small services                   |
| `/24`  | 256        | 251                 | A conventional subnet                       |
| `/22`  | 1,024      | 1,019               | Kubernetes node subnet with VPC-native pods |
| `/20`  | 4,096      | 4,091               | Large workload subnet                       |
| `/16`  | 65,536     | -                   | One VPC                                     |
| `/8`   | 16,777,216 | -                   | The whole organisation's space              |

Each step of one in the prefix **halves** the size: `/24` → `/25` is two halves of 128. That is the only mental model you need to subdivide on a whiteboard.

**Whether an address is in a block**: convert the boundary. `10.1.0.0/16` covers `10.1.0.0`-`10.1.255.255`; `10.11.0.0/16` covers `10.11.0.0`-`10.11.255.255`. So `10.11.7.44` ∈ `10.11.0.0/16` ✅ and `10.11.44.76` ∉ `10.1.0.0/16` ❌. For non-octet boundaries, work out the block size: a `/12` has 2^(32−12) = 1,048,576 addresses, stepping the second octet in 16s, so `172.16.0.0/12` covers `172.16.0.0`-`172.31.255.255` - which is exactly the RFC 1918 middle range. And when someone hands you `192.90.90.88/12`, the right response is that the prefix and the address are inconsistent as a _network_ (the host bits are non-zero, so it describes a host inside `192.80.0.0/12`) and that `192.90.x.x` is **public** space regardless - only `10/8`, `172.16/12`, and `192.168/16` are private.

The five reserved addresses in a cloud subnet: network address, the router/gateway (first usable), two for platform DNS/other, and broadcast. So never plan on the full 2^(32−n).

### Top-down allocation

```text
10.0.0.0/8                      organisation
├── 10.0.0.0/12   shared services (DNS, CI, egress inspection, transit)
├── 10.16.0.0/12  production
│   ├── 10.16.0.0/16   prod-eu-west-1      <- one VPC
│   │   ├── 10.16.0.0/20    public   (a /22 per AZ)
│   │   ├── 10.16.16.0/20   private  (a /22 per AZ)  <- biggest: pods live here
│   │   ├── 10.16.32.0/22   data     (a /24 per AZ)
│   │   └── 10.16.36.0/24   infra    (a /28 per AZ: TGW attachments, endpoints)
│   └── 10.20.0.0/16   prod-us-east-1
├── 10.32.0.0/12  staging
├── 10.48.0.0/12  development
└── 10.64.0.0/10  RESERVED - do not allocate, you will need it
```

Principles behind that shape:

- **Non-overlapping, globally.** Two VPCs with the same range can never be peered, joined by Transit Gateway, or reached over the same VPN. Every overlap you allow is a future migration.
- **Summarisable.** Because production is one `/12`, a firewall or route entry can say "production" in one line instead of forty.
- **Leave gaps.** Allocate a `/16` per VPC even if you use a `/20` of it today; keep whole `/12`s unallocated. Address space in `10/8` is free, and renumbering is not.
- **Central registry.** AWS **IPAM**, Azure **Virtual Network Manager**/IPAM, or at minimum a Git-tracked allocation file, with allocation as a pull request. The single biggest cause of overlapping CIDRs is two teams self-allocating.
- **Predictability over density.** A scheme people can read (`10.<env><region>.<tier>.0/24`) beats a perfectly packed one nobody can reason about at 3 a.m.

### Sizing subnets: the Kubernetes trap

The most common real-world sizing failure is a VPC-native CNI. With the AWS VPC CNI (or Azure CNI in the non-overlay mode) **every Pod consumes a real subnet address**, and each node reserves a block of addresses in advance for warm ENIs. A `/24` private subnet with 251 usable addresses can therefore run out with only a few dozen nodes and a few hundred Pods, and the symptom is Pods stuck in `ContainerCreating` with a "failed to assign an IP address" event - which looks like a CNI bug and is actually address exhaustion.

Mitigations, roughly in order: **size node subnets at `/22` or larger** per AZ from the start; add a **secondary CIDR** to the VPC (AWS supports adding ranges, including from `100.64.0.0/10` carrier-grade NAT space, and running Pods there while nodes stay in RFC 1918); tune warm-IP settings (`WARM_IP_TARGET`, `MINIMUM_IP_TARGET`) to stop over-reservation; use **prefix delegation** so ENIs get `/28` prefixes instead of individual addresses; or switch to an **overlay** CNI (Calico VXLAN, Cilium, Azure CNI Overlay) so Pod addresses no longer come from the VPC at all. That last option is the clean answer when you are already boxed in.

### Growth: extending versus adding

- **A subnet's CIDR cannot be extended** after creation in AWS or Azure. The answer to "can a subnet's CIDR be extended?" is no - you create an additional subnet in a free range and place new resources there.
- **A VPC/VNet can have additional CIDR blocks added** (AWS secondary CIDRs, additional Azure address spaces), which is the actual escape hatch. New subnets from the new range work normally, and - answering the usual follow-up - instances in the new subnet **can** communicate with the older ones, because all ranges in the VPC are `local` in the route table and only security groups and NACLs can stop them.
- **Can one VPC carry both a `172.` and a `192.168.` range?** Yes - a VPC can have multiple, non-overlapping CIDR blocks from different private ranges, subject to the provider's rules about which ranges may be added to an existing VPC. It works, but it makes summarisation and firewall rules messier, so it is a remedy rather than a design.

### The overlap problem, and its remedies

If two networks that must communicate already overlap: **PrivateLink** (or a private-endpoint equivalent) is the cleanest answer, because it exposes a service without routing between address spaces - overlap becomes irrelevant. Otherwise: a private NAT gateway translating one side, an application-level proxy, or renumbering the smaller side. Say the prevention too - central IPAM and non-overlapping allocation from day one - because the interviewer is usually probing whether you know overlap is a design failure rather than a routine problem.

### How many subnets, and where

- **One subnet per tier per availability zone** - three AZs × (public, private, data) = nine subnets, plus a small infra subnet per AZ. That gives per-AZ failure isolation and per-tier route tables.
- AWS limits a VPC to 200 subnets by default and 5 CIDR blocks (adjustable); Azure allows many subnets per VNet. Both make **the number of AZs** the practical multiplier, not the number of subnets.
- Small dedicated subnets are correct for Transit Gateway attachments, VPC endpoints, Application Gateway (which requires its own subnet), NAT gateways, and Azure Bastion (which requires `AzureBastionSubnet` at `/26` or larger).

## Example

```bash
# The arithmetic, verified rather than guessed
ipcalc -b 10.16.16.0/20
python3 - <<'EOF'
import ipaddress as ip
print(ip.ip_address('10.11.7.44')  in ip.ip_network('10.11.0.0/16'))   # True
print(ip.ip_address('10.11.44.76') in ip.ip_network('10.1.0.0/16'))    # False
print(ip.ip_network('172.16.0.0/12'))                                   # .0.0 - .31.255.255
print(ip.ip_network('10.16.16.0/20').num_addresses)                     # 4096 (4091 usable)
# subdivide a /20 into per-AZ /22s
print([str(s) for s in ip.ip_network('10.16.16.0/20').subnets(new_prefix=22)])
EOF
```

```hcl
# Deterministic, gap-leaving allocation with cidrsubnet()
locals {
  vpc_cidr = "10.16.0.0/16"   # one /16 per VPC, even though we use a fraction today
  azs      = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]

  # tier => [newbits, index offset] -> non-overlapping, readable, and predictable
  tiers = {
    public  = { newbits = 6, offset = 0 }   # /22 each: 10.16.0.0, 10.16.4.0, 10.16.8.0
    private = { newbits = 6, offset = 4 }   # /22 each: bigger, because pods live here
    data    = { newbits = 8, offset = 32 }  # /24 each
    infra   = { newbits = 12, offset = 576 } # /28 each: TGW attachments, endpoints
  }

  subnets = {
    for pair in setproduct(keys(local.tiers), range(length(local.azs))) :
    "${pair[0]}-${local.azs[pair[1]]}" => {
      tier = pair[0]
      az   = local.azs[pair[1]]
      cidr = cidrsubnet(local.vpc_cidr,
                        local.tiers[pair[0]].newbits,
                        local.tiers[pair[0]].offset + pair[1])
    }
  }
}

resource "aws_vpc" "this" { cidr_block = local.vpc_cidr }

# The escape hatch: a secondary CIDR for pods, keeping nodes in RFC 1918
resource "aws_vpc_ipv4_cidr_block_association" "pods" {
  vpc_id     = aws_vpc.this.id
  cidr_block = "100.64.0.0/16"   # CGNAT space: plentiful, never overlaps a partner network
}
```

```bash
# Central allocation, so two teams cannot self-allocate the same range
aws ec2-ipam create-ipam-pool --address-family ipv4 \
  --ipam-scope-id ipam-scope-0abc --locale eu-west-1 \
  --provisioned-cidrs Cidr=10.16.0.0/12
aws ec2 allocate-ipam-pool-cidr --ipam-pool-id ipam-pool-0abc --netmask-length 16

# Am I about to run out of Pod addresses?
kubectl get pods -A -o wide | wc -l
aws ec2 describe-subnets --filters "Name=vpc-id,Values=vpc-0abc" \
  --query 'Subnets[].{cidr:CidrBlock,free:AvailableIpAddressCount,az:AvailabilityZone}' --output table
kubectl get events -A --field-selector reason=FailedCreatePodSandBox | grep -i 'ip address'
```

## Interview tips

- Do the arithmetic out loud and get it right: a `/n` leaves 32−n host bits, so 2^(32−n) addresses, each prefix step halves the block, and cloud subnets lose **5** addresses to the platform. State `/32` as exactly one address and connect it to security group rules.
- Answer the in-block questions by comparing network bits, and say the range explicitly (`10.11.0.0/16` = `10.11.0.0`-`10.11.255.255`). Showing the boundary is more convincing than asserting the answer.
- If handed an inconsistent example like `192.90.90.88/12`, say two things: the host bits are non-zero so it is a host inside `192.80.0.0/12`, and `192.90.x.x` is **public** - only `10/8`, `172.16/12`, and `192.168/16` are private.
- Lead the design answer with **non-overlapping, top-down, summarisable, with gaps left deliberately**, and name central IPAM as the control. Then give the consequence of getting it wrong - you cannot peer, use Transit Gateway, or VPN to an overlapping network, ever.
- Volunteer the Kubernetes address-exhaustion trap, because it is the most common real failure: VPC-native CNIs consume a real address per Pod, a `/24` runs out fast, and the fixes are larger node subnets, a secondary CIDR (including `100.64.0.0/10`), prefix delegation, warm-IP tuning, or an overlay CNI.
- Answer the extension questions precisely: a **subnet** CIDR cannot be extended, a **VPC** can have additional CIDR blocks, and new subnets from a new block communicate with the old ones because every VPC range is `local` in the route table.
- Confirm that one VPC can hold both `172.` and `192.168.` blocks, while noting it complicates summarisation - so treat it as a remedy, not a plan.
- For an existing overlap, lead with PrivateLink (no routing between address spaces, so overlap is irrelevant) and mention private NAT or renumbering as the alternatives. See [designing a production-ready VPC on AWS](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md), [connecting many VPCs](../aws-engineering/how-do-you-connect-many-vpcs-peering-transit-gateway-or-privatelink.md), [what is network segmentation](./what-is-network-segmentation.md), and [how does Pod networking and service discovery work in Kubernetes](../kubernetes/how-does-pod-networking-and-service-discovery-work-in-kubernetes.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot Docker networking between containers?]] (`#415`): [How do you troubleshoot Docker networking between containers?](../docker/how-do-you-troubleshoot-docker-networking-between-containers.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Network Security](./README.md) · [All topics](../README.md)
