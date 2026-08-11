---
title: "What is Azure Kubernetes Service (AKS)?"
id: 202
category: "Azure Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - azure-engineering
  - interview-questions
---

# What is Azure Kubernetes Service (AKS)?

**Short answer:** AKS is managed Kubernetes on Azure: Microsoft runs and upgrades the control plane (free on the standard tier, with a paid tier for an uptime SLA), while you own the node pools, networking model, and workloads. Its distinguishing features are deep Entra ID integration for cluster RBAC, workload identity for pod-level Azure access, and node pools that can mix Spot, on-demand, and Windows nodes.

## Detail

**Control plane and tiers.** The Free tier has no SLA; the Standard tier adds a financially backed uptime SLA and higher node limits; the Premium tier adds long-term support for a Kubernetes version. Node pools are yours: a `System` pool for platform components and `User` pools for workloads, so a noisy application cannot starve CoreDNS or the metrics server.

**Workload identity is the important integration.** A Kubernetes service account is federated to an Entra managed identity, so a Pod obtains Azure tokens with no secret in the cluster. This replaced the deprecated pod-managed-identity (aad-pod-identity) approach, and it is the answer to "how does your Pod read from Key Vault?" - combined with the Secrets Store CSI driver to project secrets as files.

**Networking model is a decision you cannot change later.** Azure CNI gives Pods real VNet IPs (routable, but consumes address space fast); Azure CNI Overlay gives Pods addresses from a separate overlay CIDR and conserves VNet space; kubenet is legacy. Choose the network policy engine at creation too - Cilium (Azure CNI powered by Cilium) is the current default recommendation and brings eBPF dataplane and network policy in one.

**Cluster RBAC via Entra.** Enable Entra integration with Azure RBAC for Kubernetes authorisation, so `kubectl` access is granted through Azure role assignments and covered by Conditional Access and PIM - rather than by distributing a cluster admin kubeconfig, which is the pattern auditors object to. Disable local accounts to make it enforceable.

**Upgrades are the recurring operational cost.** Kubernetes minor versions leave AKS support roughly every 12 months, so plan two to three upgrades a year: control plane first, then node pools (surge upgrade with `maxSurge`), with pod disruption budgets and `topologySpreadConstraints` in place so the drain does not cause an outage. Auto-upgrade channels plus planned maintenance windows automate the routine part.

**Scaling.** Cluster autoscaler per node pool, KEDA for event-driven workload scaling (queue length, custom metrics), and Virtual Nodes/ACI for burst capacity. Node autoprovisioning (the Karpenter-based provider) is the newer option for right-sized nodes without predefined pools.

## Example

```bash
# Cluster with overlay networking, Cilium, Entra RBAC, and workload identity
az aks create \
  --resource-group rg-platform-prod-weu \
  --name aks-prod-weu \
  --tier standard \
  --network-plugin azure \
  --network-plugin-mode overlay \
  --network-dataplane cilium \
  --pod-cidr 172.16.0.0/16 \
  --enable-aad --enable-azure-rbac --disable-local-accounts \
  --enable-oidc-issuer --enable-workload-identity \
  --enable-cluster-autoscaler --min-count 3 --max-count 20 \
  --node-os-upgrade-channel NodeImage \
  --auto-upgrade-channel patch \
  --zones 1 2 3
```

```yaml
# Pod gets Azure tokens with no secret: SA annotated, Pod labelled
apiVersion: v1
kind: ServiceAccount
metadata:
  name: checkout
  annotations:
    azure.workload.identity/client-id: 8f3c1b2a-1111-2222-3333-444455556666
---
apiVersion: apps/v1
kind: Deployment
metadata: { name: checkout }
spec:
  selector: { matchLabels: { app: checkout } }
  template:
    metadata:
      labels:
        app: checkout
        azure.workload.identity/use: "true"
    spec:
      serviceAccountName: checkout
      containers: [{ name: api, image: acme.azurecr.io/checkout@sha256:1f4b }]
```

## Interview tips

- Workload identity (not the deprecated pod identity) is the detail that dates your knowledge correctly.
- Say that the network plugin choice is immutable and explain the IP-exhaustion trade-off.
- Expect: "how do you handle upgrades?" - surge upgrades, PDBs, maintenance windows, and the roughly-annual version cadence.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is Cloud Computing?]] (`#21`): [What is Cloud Computing?](../cloud-platforms/what-is-cloud-computing.md)
- [[What is Azure?]] (`#23`): [What is Azure?](../cloud-platforms/what-is-azure.md)
- [[What is Google Cloud Platform (GCP)?]] (`#24`): [What is Google Cloud Platform (GCP)?](../cloud-platforms/what-is-google-cloud-platform-gcp.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Azure Engineering](./README.md) · [All topics](../README.md)
