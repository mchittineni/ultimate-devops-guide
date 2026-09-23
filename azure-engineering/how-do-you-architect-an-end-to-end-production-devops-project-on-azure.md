---
title: "How do you architect an end-to-end production DevOps project on Azure?"
id: 250
category: "Azure Engineering"
difficulty: "Advanced"
tags:
  - devops
  - azure-engineering
  - interview-questions
---

# How do you architect an end-to-end production DevOps project on Azure?

**Short answer:** Architect an end-to-end production DevOps project on Azure by provisioning a Hub-and-Spoke Virtual Network topology using Bicep/Terraform, deploying Azure Kubernetes Service (AKS) with Workload Identity and Entra ID RBAC, running Azure SQL Managed Instance over Private Endpoints, automating CI/CD via Azure DevOps Pipelines, and monitoring with Azure Monitor and Log Analytics.

## Detail

Designing an enterprise production environment on Microsoft Azure requires enforcing landing zone principles, strict network isolation, federated identity, and automated Bicep/Terraform deployments:

### 1. Enterprise Network Topology (Hub-and-Spoke VNet)

- **Hub VNet:** Houses centralized shared services, Azure Firewall / Application Gateway with WAF, Azure Bastion, and Azure Private DNS Zones.
- **Spoke VNet:** Hosts application workloads (AKS clusters, App Services) peered to the Hub VNet with forced tunneling through Azure Firewall.
- **Private Link / Endpoints:** All PaaS services (Azure SQL, Key Vault, Container Registry) expose internal IP addresses via Private Endpoints, disabling public endpoint access completely.

### 2. Compute & Security Architecture (AKS + Entra ID)

- **Azure Kubernetes Service (AKS):** Cluster deployed with Azure CNI Overlay networking, User-Assigned Managed Identity, and Entra ID (Azure AD) RBAC integration.
- **Azure Workload Identity:** Replaces legacy pod-managed identity to federate Kubernetes Service Accounts with Entra ID Managed Identities using OpenID Connect (OIDC).
- **Secrets Management:** Azure Key Vault storing certificates and connection strings, mounted into AKS pods via CSIDriver (Secrets Store CSI Driver).

### 3. CI/CD & Compliance Automation

- **Azure DevOps Pipelines / GitHub Actions:** Authenticates to Azure via OIDC Workload Identity Federation (eliminating service principal secret keys).
- **Azure Policy:** Enforces Enterprise Governance (e.g. denying public storage accounts, enforcing mandatory resource tagging, requiring encrypted disks).

**Trade-offs.** Forcing all egress through a hub firewall and all PaaS access through private endpoints gives central inspection and no public data paths, but costs money (Firewall and private endpoints are billed hourly), adds latency, and makes private DNS a critical dependency - a broken zone link takes applications down. Since March 2026 new VNets have no implicit outbound internet access, so egress through the firewall or a NAT gateway must be designed from day one.

## Example

**1. Azure Production Hub-and-Spoke Architecture Diagram:**

```mermaid
graph TD
    User[Internet Traffic] --> AppGW[Azure Application Gateway WAF]
    subgraph HubVNet["Hub Virtual Network"]
        AppGW
        AzFW[Azure Firewall]
        DNS[Azure Private DNS Zones]
    end
    subgraph SpokeVNet["Spoke Virtual Network"]
        AKS[Azure Kubernetes Service - AKS]
        KV[Azure Key Vault Private Endpoint]
        SQL[Azure SQL Database Private Endpoint]
    end
    AppGW --> AKS
    AKS --> KV
    AKS --> SQL
    AKS --> WorkloadID[Azure Workload Identity]
```

**2. Bicep Infrastructure Deployment Module Snippet (`main.bicep`):**

```bicep
param location string = resourceGroup().location
param clusterName string = 'prod-aks-cluster'

resource vnet 'Microsoft.Network/virtualNetworks@2024-05-01' = {
  name: 'spoke-vnet'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        '10.1.0.0/16'
      ]
    }
    subnets: [
      {
        name: 'aks-subnet'
        properties: {
          addressPrefix: '10.1.0.0/22'
        }
      }
    ]
  }
}

resource aksIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-${clusterName}'
  location: location
}

resource aksCluster 'Microsoft.ContainerService/managedClusters@2024-09-01' = {
  name: clusterName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${aksIdentity.id}': {}
    }
  }
  properties: {
    dnsPrefix: 'prodaks'
    aadProfile: {
      managed: true
      enableAzureRBAC: true
    }
    disableLocalAccounts: true
    networkProfile: {
      networkPlugin: 'azure'
      networkPluginMode: 'overlay'
      networkDataplane: 'cilium'
      podCidr: '192.168.0.0/16'
    }
    agentPoolProfiles: [
      {
        name: 'systempool'
        count: 3
        vmSize: 'Standard_D4s_v5'
        mode: 'System'
        vnetSubnetID: vnet.properties.subnets[0].id
        availabilityZones: ['1', '2', '3']
      }
    ]
    oidcIssuerProfile: {
      enabled: true // oidcIssuerProfile sits under properties, not securityProfile
    }
    securityProfile: {
      workloadIdentity: {
        enabled: true
      }
    }
  }
}
```

## Interview tips

- Highlight **Hub-and-Spoke topology**: explain how centralized Azure Firewall in the Hub VNet enforces egress traffic inspection across all Spoke VNets.
- Emphasize **Azure Workload Identity**: explain how it replaces static Azure Service Principal client secrets in CI/CD pipelines and AKS pods with OIDC federated tokens.
- Address PaaS isolation: always mention using **Azure Private Endpoints** and **Azure Private DNS Zones** to secure Azure Key Vault, ACR, and Azure SQL DB from public internet access.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Cloud Computing?]] (`#21`): [What is Cloud Computing?](../cloud-platforms/what-is-cloud-computing.md)
- [[What is AWS (Amazon Web Services)?]] (`#22`): [What is AWS (Amazon Web Services)?](../cloud-platforms/what-is-aws-amazon-web-services.md)
- [[What is Azure?]] (`#23`): [What is Azure?](../cloud-platforms/what-is-azure.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Azure Engineering](./README.md) · [All topics](../README.md)
