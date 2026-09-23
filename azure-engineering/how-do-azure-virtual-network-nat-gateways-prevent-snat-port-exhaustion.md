---
title: "How Do Azure Virtual Network NAT Gateways Prevent SNAT Port Exhaustion?"
id: 740
category: "Azure Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - azure-engineering
  - nat-gateway
  - networking
  - snat
quiz:
  stem: "Why does an Azure VNet NAT Gateway prevent SNAT port exhaustion more effectively than default Azure Load Balancer outbound rules?"
  options:
    - "It disables all outbound TCP handshakes."
    - "It maintains a unified, dynamic pool of up to 64,512 SNAT ports per public IP allocated on-demand, rather than statically pre-allocating fixed port slices per VM."
    - "It forces all external web traffic to use UDP instead of TCP."
    - "It converts all outbound traffic into internal ExpressRoute circuits."
  answer: 2
  explanation: "Standard Load Balancers statically divide ports among VMs, causing busy nodes to run out quickly. NAT Gateway dynamically assigns ports on demand from a shared pool across all subnet instances."
---

# How Do Azure Virtual Network NAT Gateways Prevent SNAT Port Exhaustion?

**Short answer:** Azure Virtual Network NAT Gateway provides high-performance, fully managed outbound internet connectivity with dynamic SNAT port allocation across up to 16 public IP addresses, eliminating the static pre-allocation bottlenecks that cause SNAT port exhaustion on Azure Load Balancers.

**Short answer:** NAT Gateway attaches to subnets and gives all their outbound flows a shared pool of SNAT ports - 64,512 per public IP, up to 16 IPs - allocated **on demand** to whichever VM or Pod needs them. Load Balancer outbound rules and the old implicit default outbound access instead **pre-allocate** a fixed slice of ports per backend instance, so one busy instance can exhaust its slice while ports sit idle elsewhere. NAT Gateway removes that per-instance ceiling; it does not remove the need to reuse connections.

## Detail

### The Root Cause of SNAT Port Exhaustion

When VMs or AKS Pods without public IPs open outbound connections to the internet, Azure translates the private source IP and port to a public IP and port (SNAT). A SNAT port can be reused for different destinations, but each concurrent flow to the **same destination IP and port** needs its own SNAT port.

With Load Balancer outbound rules (the AKS `loadBalancer` outbound type) each backend instance gets a fixed number of ports - by default a small allocation that shrinks as the pool grows, or whatever you set manually. A node opening thousands of connections to one payment API exhausts its allocation: new connections fail or hang, surfacing as intermittent timeouts that look like an upstream problem.

### How NAT Gateway Solves It

1. **Dynamic, shared allocation.** Ports come from a pool shared by every instance in the associated subnets and are allocated per flow as needed, so capacity follows demand instead of instance count.
2. **Capacity.** 64,512 SNAT ports per public IP, up to 16 IPs or prefixes - just over one million ports. The Standard SKU handles up to 50 Gbps; the StandardV2 SKU (GA January 2026) raises that to 100 Gbps and is zone-redundant by default, whereas Standard is zonal.
3. **Precedence.** Once associated with a subnet, NAT Gateway takes over outbound internet traffic from load balancer outbound rules and instance-level public IPs for new outbound flows (inbound through a load balancer or public IP still works).
4. **Timers.** The TCP idle timeout defaults to 4 minutes (configurable up to 120). Ports from closed connections are held briefly before reuse, so connection churn to one destination still consumes ports.

Since 31 March 2026, subnets in new VNets are private by default with no implicit outbound access, so an explicit egress method - NAT Gateway, a firewall, or a load balancer - is now a design requirement rather than a fix applied later.

**Limitations.** A NAT gateway serves subnets in one VNet; the Standard SKU lives in a single zone; it provides outbound only; and it does no inspection or FQDN filtering - for that, route egress through Azure Firewall (which can itself use a NAT gateway for its SNAT). The application-level fix still matters: connection pooling and HTTP keep-alive cut the number of flows by orders of magnitude.

```text
[Private AKS Subnet]
 ├─ Pod 1 ──┐
 ├─ Pod 2 ──┼──► [NAT Gateway] ──► [Up to 16 public IPs / prefixes] ──► [Internet]
 └─ Pod 3 ──┘   (shared, on-demand SNAT pool: 64,512 ports per IP)
```

### Real-World Production Scenario

An e-commerce platform on AKS sees payment gateway timeouts during a sale. SNAT connection metrics on the Standard Load Balancer show failed allocations on the busiest nodes, each limited to its pre-allocated ports. The team associates a NAT gateway with two public IPs (about 129,000 ports shared across all nodes), switches the cluster's outbound type to `userAssignedNATGateway`, and enables HTTP keep-alive in the payment client - timeouts stop, and the port usage metric shows ample headroom.

## Example

```bash
# NAT gateway with a static public IP, attached to the AKS subnet
# (choose the StandardV2 SKU for the NAT gateway and IP where you need zone redundancy)
az network public-ip create -g rg-net -n pip-nat-weu --sku Standard --allocation-method Static
az network nat gateway create -g rg-net -n nat-weu \
  --public-ip-addresses pip-nat-weu --idle-timeout 4
az network vnet subnet update -g rg-net --vnet-name vnet-prod -n snet-aks \
  --nat-gateway nat-weu

# Watch for exhaustion: SNAT connection count and dropped packets per NAT gateway
az monitor metrics list \
  --resource "$(az network nat gateway show -g rg-net -n nat-weu --query id -o tsv)" \
  --metric SNATConnectionCount PacketDropCount --interval PT1M -o table
```

## Interview tips

- Explain the root cause precisely: fixed per-instance pre-allocation (Load Balancer outbound rules, default outbound access) versus a shared on-demand pool (NAT Gateway).
- Give the numbers: 64,512 ports per public IP, up to 16 IPs, and the fact that ports are consumed per destination IP and port.
- Mention that new VNets are private by default since March 2026, so explicit egress is mandatory for new designs.
- Name the application-side fix too - connection pooling and keep-alive - otherwise you are only buying headroom.
- Know the SKU difference: Standard is zonal, StandardV2 is zone-redundant.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are Cloud Egress fees and how do you architect networks to minimize them?]] (`#547`): [What are Cloud Egress fees and how do you architect networks to minimize them?](../cloud-platforms/what-are-cloud-egress-fees-and-how-do-you-architect-networks-to-minimize-them.md)
- [[How does the Kubernetes Gateway API evolve beyond standard Ingress resources?]] (`#520`): [How does the Kubernetes Gateway API evolve beyond standard Ingress resources?](../kubernetes/how-does-the-kubernetes-gateway-api-evolve-beyond-standard-ingress-resources.md)
- [[How does CoreDNS resolve services in Kubernetes and how do you troubleshoot DNS latency bottlenecks?]] (`#527`): [How does CoreDNS resolve services in Kubernetes and how do you troubleshoot DNS latency bottlenecks?](../kubernetes/how-does-coredns-resolve-services-in-kubernetes-and-how-do-you-troubleshoot-dns-latency-bottlenecks.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Azure Engineering](./README.md) · [All topics](../README.md)
