---
title: "How do you connect many VPCs — peering, Transit Gateway, or PrivateLink?"
id: 475
category: "AWS Engineering"
difficulty: "Advanced"
tags:
  - devops
  - aws-engineering
  - interview-questions
  - network-security
  - cloud-engineering
---

# How do you connect many VPCs — peering, Transit Gateway, or PrivateLink?

**Short answer:** Choose by topology and scale. **VPC peering** is a one-to-one, non-transitive link: cheap (no hourly charge), lowest latency, but it needs a peering connection and route-table entries **per pair**, so N VPCs need N(N-1)/2 connections - unmanageable past a handful. **Transit Gateway** is a regional hub-and-spoke router: each VPC attaches once, routing is centralised in TGW route tables, it is transitive, and it also terminates Direct Connect and site-to-site VPN - so it becomes the backbone for a multi-account estate. It costs per attachment-hour plus per GB. **PrivateLink** is not really "connecting VPCs" at all: it exposes **one service** (behind an NLB) to consumers who create interface endpoints, one-directional, and - crucially - **immune to overlapping CIDRs** because no routing between the address spaces happens. That last property is the answer to the classic scenario: two VPCs must communicate, their CIDRs overlap, and Transit Gateway is not permitted - use PrivateLink.

## Detail

### The comparison

|                     | VPC peering                               | Transit Gateway                                   | PrivateLink                            |
| ------------------- | ----------------------------------------- | ------------------------------------------------- | -------------------------------------- |
| Topology            | Point-to-point mesh                       | Hub and spoke                                     | Service exposure (provider → consumer) |
| Transitive routing  | **No** - A↔B and B↔C does not give A↔C    | **Yes**                                           | N/A - no routing at all                |
| Scale               | N(N-1)/2 connections                      | One attachment per VPC                            | One endpoint per consumer per service  |
| Overlapping CIDRs   | **Not allowed**                           | **Not allowed**                                   | **Fine**                               |
| Cross-region        | Yes (inter-region peering)                | Yes (TGW peering)                                 | Yes, with some service limits          |
| Cross-account       | Yes                                       | Yes (via RAM sharing)                             | Yes - designed for it                  |
| Terminates DX / VPN | No                                        | **Yes**                                           | No                                     |
| Bandwidth           | No aggregate limit; instance limits apply | 50 Gbps per attachment (burst)                    | NLB limits                             |
| Hourly cost         | **None** (data transfer only)             | Per attachment + per GB                           | Per endpoint per AZ + per GB           |
| Segmentation        | Per-pair only                             | Multiple TGW route tables = network domains       | Per-service by policy                  |
| Exposure            | The whole VPC's routable space            | The whole attached space, subject to route tables | **Exactly one service, one port**      |

### Non-transitivity, the fact everything else follows from

Peering does not forward traffic on behalf of a third party. So a hub-and-spoke built from peering connections does not work: spoke A cannot reach spoke C through hub B, and you cannot route to the internet, a NAT gateway, or a VPC endpoint in the peer VPC either. This is why organisations that start with peering hit a wall at roughly five to ten VPCs and migrate to Transit Gateway. Say the arithmetic - 10 VPCs is 45 peering connections and 45 sets of route-table entries to maintain - because that number makes the argument for you.

### Transit Gateway, and the part that gets asked

Attach each VPC once, then routing is decided in **TGW route tables**, which is where segmentation lives. The frequently-asked question - _"having connected several VPCs through a Transit Gateway, how do you block traffic from A to B and from B to C?"_ - is answered with **multiple TGW route tables**, not with security groups:

```text
TGW route table "prod"    <- prod VPC association;  routes to shared services only
TGW route table "dev"     <- dev VPC association;   routes to shared services only
TGW route table "shared"  <- shared VPC;            routes to prod AND dev

Result: prod ↔ shared  ✅     dev ↔ shared  ✅     prod ↔ dev  ❌ (no route exists)
```

Because each attachment is _associated_ with exactly one route table but can _propagate_ its routes into several, you build network domains that cannot talk to each other by omission rather than by denial. That is the cleanest form of segmentation AWS offers.

Then the other half of the question people miss: **each VPC's own subnet route tables need an entry** sending the other VPCs' CIDRs (or a summary like `10.0.0.0/8`) to the TGW attachment. Without that, TGW routing is configured and nothing flows. You do **not** add a CIDR per VPC to the TGW attachment - the attachment is per-VPC and picks up subnets you nominate; the CIDR work is in the route tables.

Operational notes worth having: put the attachment ENI in a small dedicated subnet per AZ in each VPC, attach in every AZ you want traffic in (traffic to an AZ with no attachment traverses another AZ and incurs charges), enable **appliance mode** when traffic must be inspected by a stateful firewall so flows stay symmetric, and remember TGW is regional - cross-region needs TGW peering.

### PrivateLink: exposure, not connectivity

The mental shift: with peering or TGW you join two networks and then restrict with security groups; with PrivateLink you never join the networks - the consumer gets an ENI in _their_ VPC that fronts _your_ NLB. Consequences:

- **Overlapping CIDRs are irrelevant.** There is no route between the address spaces, so `10.0.0.0/16` on both sides is fine. This is the reason it solves the overlap scenario, and the reason it is often the right answer for SaaS and cross-organisation integration.
- **One-directional.** The consumer initiates; the provider cannot reach back. That is a security feature, and a limitation if you need two-way traffic (you would create a second endpoint service in the other direction).
- **Minimal blast radius.** You expose one NLB listener, not a routable network. Compare that with a peering connection, which exposes everything your route tables and security groups permit.
- **Scales to many consumers** without any address-space coordination - which is why AWS's own services use it.

### The other options, for completeness

- **Overlapping CIDRs with peering/TGW**: strictly you can work around it with private NAT gateways translating one side's addresses, but it is complex and fragile. Prefer PrivateLink, or renumber the VPC if you own both sides - and prevent the problem by allocating non-overlapping CIDRs centrally (IPAM) from day one.
- **VPN over the internet between VPCs**: works, adds encryption and complexity, occasionally used for cross-cloud (AWS VPC ↔ another provider's VPC, which is how you would answer "connect an AWS VPC to a VPC in IBM Cloud" - site-to-site IPsec VPN, or a partner interconnect through Direct Connect and their equivalent).
- **Cloud WAN** for very large global estates - TGW-like segmentation managed centrally across regions.
- **A shared-services VPC** pattern: put the things everyone needs (AD, DNS resolvers, CI runners, monitoring, egress inspection) in one VPC attached to the hub, so spokes need routes to one place rather than to each other.

### Cost, which is often the deciding factor

Peering has **no hourly charge** - you pay data transfer only, and intra-AZ peering traffic in the same region is free in many cases. Transit Gateway charges **per attachment per hour** plus per GB processed, so a 40-VPC estate has a meaningful fixed monthly cost before any traffic. That produces a genuinely common hybrid: TGW as the backbone for general connectivity, plus **direct peering for the two chattiest VPC pairs** to bypass the per-GB charge. Being able to say that shows you have designed for a bill, not just a diagram.

## Example

```hcl
# Transit Gateway with segmentation: prod and dev can each reach shared, not each other
resource "aws_ec2_transit_gateway" "hub" {
  description                     = "acme-hub"
  default_route_table_association = "disable" # we manage associations explicitly
  default_route_table_propagation = "disable"
  dns_support                     = "enable"
}

resource "aws_ec2_transit_gateway_vpc_attachment" "prod" {
  transit_gateway_id = aws_ec2_transit_gateway.hub.id
  vpc_id             = aws_vpc.prod.id
  subnet_ids         = [for s in aws_subnet.prod_tgw : s.id] # one small subnet per AZ
  appliance_mode_support = "disable"
}

resource "aws_ec2_transit_gateway_route_table" "prod" { transit_gateway_id = aws_ec2_transit_gateway.hub.id }
resource "aws_ec2_transit_gateway_route_table" "shared" { transit_gateway_id = aws_ec2_transit_gateway.hub.id }

# prod is associated with the prod table...
resource "aws_ec2_transit_gateway_route_table_association" "prod" {
  transit_gateway_attachment_id  = aws_ec2_transit_gateway_vpc_attachment.prod.id
  transit_gateway_route_table_id = aws_ec2_transit_gateway_route_table.prod.id
}
# ...and propagates its routes only into the shared table
resource "aws_ec2_transit_gateway_route_table_propagation" "prod_to_shared" {
  transit_gateway_attachment_id  = aws_ec2_transit_gateway_vpc_attachment.prod.id
  transit_gateway_route_table_id = aws_ec2_transit_gateway_route_table.shared.id
}
# prod's table gets a route ONLY to shared -> prod↔dev is impossible by omission

# The half people forget: the VPC's own subnets need a route to the TGW
resource "aws_route" "prod_to_hub" {
  for_each               = aws_route_table.prod_private
  route_table_id         = each.value.id
  destination_cidr_block = "10.0.0.0/8"
  transit_gateway_id     = aws_ec2_transit_gateway.hub.id
}
```

```hcl
# PrivateLink: expose one service, overlapping CIDRs irrelevant, one-directional
resource "aws_vpc_endpoint_service" "payments" {   # provider side
  acceptance_required        = true
  network_load_balancer_arns = [aws_lb.payments_nlb.arn]
  allowed_principals         = ["arn:aws:iam::444455556666:root"] # who may connect
  supported_ip_address_types = ["ipv4"]
}

resource "aws_vpc_endpoint" "payments" {           # consumer side, in THEIR VPC
  vpc_id              = aws_vpc.consumer.id        # CIDR may be identical to the provider's
  service_name        = aws_vpc_endpoint_service.payments.service_name
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [for s in aws_subnet.consumer_private : s.id]
  security_group_ids  = [aws_security_group.consumer_app.id]
  private_dns_enabled = false                      # or use a custom private hosted zone
}
```

```bash
# Peering does not scale: the arithmetic that decides the design
python3 -c 'n=10; print(f"{n} VPCs -> {n*(n-1)//2} peering connections")'   # 45

# Diagnose "TGW is attached but nothing flows" - check BOTH layers
aws ec2 search-transit-gateway-routes --transit-gateway-route-table-id tgw-rtb-0abc \
  --filters "Name=state,Values=active" --query 'Routes[].[DestinationCidrBlock,Type]' --output table
aws ec2 describe-route-tables --route-table-ids rtb-0abc \
  --query 'RouteTables[0].Routes[?TransitGatewayId!=`null`]'   # the VPC-side route

# Reachability Analyzer names the exact blocking component across TGW hops
aws ec2 create-network-insights-path --source i-0abc --destination i-0def \
  --protocol tcp --destination-port 443
```

## Interview tips

- Answer with a decision, not a list: peering for a couple of VPCs, Transit Gateway once you have more than a handful or need Direct Connect/VPN termination, PrivateLink when you want to expose a service rather than join networks.
- Lead the peering explanation with **non-transitivity** and the N(N-1)/2 arithmetic. Saying "10 VPCs is 45 connections" makes the scaling argument instantly.
- For the segmentation question, answer with **multiple TGW route tables** and explain association versus propagation - blocking by omission rather than by deny rules. That is the expected senior answer.
- Volunteer the step people forget: each VPC's own subnet route tables need a route to the TGW attachment. And correct the premise of "do you configure the attachment with a CIDR per VPC?" - the attachment is per VPC and per subnet; the CIDRs live in route tables.
- Have the overlapping-CIDR answer ready and lead with **PrivateLink**, explaining _why_ it works - no routing between address spaces, so overlap is irrelevant - then mention private NAT as the ugly alternative and central IPAM as the prevention.
- Describe PrivateLink's other two properties: one-directional, and exposes exactly one NLB listener rather than a routable network. Frame it as blast-radius reduction.
- Mention cost as a design input: peering has no hourly charge, TGW charges per attachment-hour plus per GB, and a hybrid (TGW backbone plus direct peering for the two chattiest pairs) is a legitimate optimisation.
- Add appliance mode for stateful inspection and per-AZ attachments for cost and latency - both are details only practitioners mention. See [what are VPC endpoints](./what-are-vpc-endpoints-and-when-do-you-use-a-gateway-versus-an-interface-endpoint.md), [structuring a multi-account AWS organisation](./how-do-you-structure-a-multi-account-aws-organisation.md), [connecting an on-premises network to the cloud](../cloud-engineering/how-do-you-connect-an-on-premises-network-to-the-cloud.md), and [designing a production-ready VPC](./how-do-you-design-a-production-ready-vpc-on-aws.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you connect an on-premises network to the cloud?]] (`#216`): [How do you connect an on-premises network to the cloud?](../cloud-engineering/how-do-you-connect-an-on-premises-network-to-the-cloud.md)
- [[How do you manage DNS and global traffic routing?]] (`#220`): [How do you manage DNS and global traffic routing?](../cloud-engineering/how-do-you-manage-dns-and-global-traffic-routing.md)
- [[How do you troubleshoot a DNS problem in production?]] (`#435`): [How do you troubleshoot a DNS problem in production?](../cloud-engineering/how-do-you-troubleshoot-a-dns-problem-in-production.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
