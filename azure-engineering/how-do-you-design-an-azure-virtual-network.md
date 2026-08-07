---
title: "How do you design an Azure virtual network?"
id: 201
category: "Azure Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - azure-engineering
  - interview-questions
---

# How do you design an Azure virtual network?

**Short answer:** A hub-and-spoke topology: a hub VNet holding shared egress (Azure Firewall or NVA), private DNS, and hybrid connectivity (ExpressRoute or VPN gateway), with per-workload spoke VNets peered to it. Subnets are segmented by tier and protected by network security groups, private endpoints replace public service access, and default outbound internet access is explicitly replaced with a NAT gateway or firewall.

## Detail

**Hub and spoke, and why peering shapes the design.** VNet peering is not transitive: two spokes peered to the same hub cannot reach each other unless you route through a network virtual appliance in the hub (user-defined routes) or connect them directly. Azure Virtual WAN automates this for large estates. Deciding early whether spoke-to-spoke traffic must be inspected determines whether you need Firewall in the hub at all.

**Subnets and NSGs.** Subnets are per-tier (web, app, data), each with an NSG whose rules should reference application security groups or service tags (`Sql`, `AzureMonitor`, `Internet`) rather than raw CIDRs - service tags are maintained by Microsoft and survive IP changes. Some services require dedicated, delegated subnets (Azure Firewall, Bastion, gateway subnets, App Service integration), each with naming and minimum-size requirements, so leave room.

**Private endpoints are the main security decision.** By default PaaS services (Storage, SQL, Key Vault) have public endpoints. A private endpoint gives the service a private IP inside your VNet; combined with `publicNetworkAccess = Disabled` on the resource, this removes the internet path entirely. The catch is DNS: the resource's public FQDN must resolve to the private IP, which requires linked private DNS zones - misconfigured private DNS is the single most common cause of "the private endpoint does not work".

**Outbound internet access is changing.** Implicit outbound access for new VMs is being retired, so egress must be explicit: NAT gateway (simple, scalable SNAT), a load balancer's outbound rules, or routing through Azure Firewall for inspection and FQDN filtering. NAT gateway also solves SNAT port exhaustion, which is a real failure mode for chatty outbound workloads.

**Address planning.** Non-overlapping RFC 1918 space across hubs, spokes, and on-premises, sized for growth - and for AKS, sized for the networking model you choose (Azure CNI consumes a VNet IP per Pod; overlay modes conserve address space). Azure reserves five addresses per subnet, so a /29 is smaller than it looks.

**Observability.** VNet flow logs with Traffic Analytics, NSG rule hit counts, Connection Monitor for hybrid paths, and Network Watcher's next-hop and effective-rules tools - which are the fastest way to answer "why can this VM not reach that endpoint?" during an incident.

## Example

```bicep
// Spoke VNet with tiered subnets, service-tag NSG rule, and a NAT gateway for egress
param location string = resourceGroup().location

resource natPip 'Microsoft.Network/publicIPAddresses@2023-11-01' = {
  name: 'pip-nat-spoke'
  location: location
  sku: { name: 'Standard' }
  properties: { publicIPAllocationMethod: 'Static' }
}

resource nat 'Microsoft.Network/natGateways@2023-11-01' = {
  name: 'nat-spoke'
  location: location
  sku: { name: 'Standard' }
  properties: {
    idleTimeoutInMinutes: 4
    publicIpAddresses: [{ id: natPip.id }]
  }
}

resource nsgApp 'Microsoft.Network/networkSecurityGroups@2023-11-01' = {
  name: 'nsg-app'
  location: location
  properties: {
    securityRules: [
      {
        name: 'allow-sql-outbound'
        properties: {
          priority: 100
          direction: 'Outbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: 'VirtualNetwork'
          destinationAddressPrefix: 'Sql' // service tag, not a CIDR
          destinationPortRange: '1433'
        }
      }
    ]
  }
}

resource vnet 'Microsoft.Network/virtualNetworks@2023-11-01' = {
  name: 'vnet-payments-prod-weu'
  location: location
  properties: {
    addressSpace: { addressPrefixes: ['10.60.0.0/16'] }
    subnets: [
      {
        name: 'snet-app'
        properties: {
          addressPrefix: '10.60.16.0/20'
          networkSecurityGroup: { id: nsgApp.id }
          natGateway: { id: nat.id }
        }
      }
      {
        name: 'snet-data' // private endpoints only, no egress
        properties: { addressPrefix: '10.60.48.0/24' }
      }
    ]
  }
}
```

## Interview tips

- Say "peering is not transitive" unprompted; it is the Azure networking fact interviewers check for.
- Private endpoints plus linked private DNS zones - and naming DNS as the usual failure - signals hands-on experience.
- Expect: "how does traffic leave?" - explicit NAT gateway or Firewall, and mention SNAT port exhaustion.

---

[⬅ Back to Azure Engineering](./README.md) · [All topics](../README.md)
