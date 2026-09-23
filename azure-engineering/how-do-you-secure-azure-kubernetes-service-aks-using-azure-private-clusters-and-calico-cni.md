---
title: "How Do You Secure Azure Kubernetes Service (AKS) Using Azure Private Clusters and Calico CNI?"
id: 739
category: "Azure Engineering"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - azure-engineering
  - aks
  - calico
  - kubernetes-security
quiz:
  stem: "In an Azure Kubernetes Service (AKS) Private Cluster, how is the Kubernetes API server exposed to administrators?"
  options:
    - "Through a public IPv4 address with an open internet firewall rule."
    - "Through an Azure Private Endpoint with an internal private IP accessible only via connected VNets, Bastion, or ExpressRoute."
    - "Through an unauthenticated HTTP proxy hosted on GitHub."
    - "Via a public AWS Route 53 global nameserver."
  answer: 2
  explanation: "In an AKS Private Cluster, the API server has no public IP; it uses an Azure Private Endpoint backed by Private Link, making it reachable only within private virtual networks or via ExpressRoute/VPN."
---

# How Do You Secure Azure Kubernetes Service (AKS) Using Azure Private Clusters and Calico CNI?

**Short answer:** An AKS Private Cluster ensures the Kubernetes API server has no public IP and is accessible only through private endpoints within a VNet or peered network. Calico CNI complements this by enforcing fine-grained east-west network security policies between pods.

**Short answer:** A **private cluster** removes the public endpoint from the AKS API server: `kubectl` reaches it through a private endpoint in your VNet (or, with API Server VNet Integration, an internal IP in a delegated subnet), resolved through a private DNS zone. **Calico** is one of AKS's network policy engines and enforces Kubernetes `NetworkPolicy` (and Calico's own richer policies) for east-west traffic between Pods. Together they close the two biggest exposures - a publicly reachable control plane and a flat Pod network - at the cost of harder access for CI and operators. For new clusters, Azure CNI powered by Cilium is now Microsoft's recommended policy engine; Calico remains supported.

## Detail

### 1. AKS Private Clusters (Control Plane Isolation)

- A standard cluster's API server has a public FQDN (optionally restricted with authorized IP ranges).
- A **private cluster** exposes the API server through **Azure Private Link**: a private endpoint in the cluster's VNet, with a private DNS zone (`privatelink.<region>.azmk8s.io`) resolving the FQDN to its private IP.
- **API Server VNet Integration** is the alternative model: the API server is projected into a delegated subnet in your VNet and reached via an internal load balancer, without a private endpoint - and it can be switched between public and private access.
- `kubectl` access then needs a network path: a jump box or Azure Bastion in the VNet, a peered VNet, ExpressRoute/VPN from on-premises, or `az aks command invoke` for ad-hoc commands without network access. Hub-and-spoke designs must link the private DNS zone to the hub (or use a custom DNS zone) so resolution works from wherever operators and pipelines run.
- CI/CD then needs **self-hosted agents** inside the network; Microsoft-hosted agents cannot reach a private API server.

### 2. Network Policy: Calico or Cilium

By default, Kubernetes Pods can talk to any other Pod in any namespace. Network policy establishes default-deny and explicit allows.

- **Engines on AKS**: Calico (open source, with Azure CNI or CNI Overlay), Azure CNI powered by Cilium (eBPF, recommended for new clusters), and Azure Network Policy Manager (being retired - plan a migration). The engine is chosen at cluster creation.
- **Standard `NetworkPolicy`** works on all of them and is the portable choice. **Calico's own policies** (`projectcalico.org/v3`, applied with `calicoctl` or the Calico API server) add global policies, explicit deny rules, ordering, and host endpoint protection. Layer 7 (HTTP-aware) rules need a service mesh or a commercial Calico edition; they are not part of the open-source policy engine.
- Remember DNS: a default-deny egress policy must allow Pods to reach CoreDNS on port 53, or everything breaks in confusing ways.

```text
[On-Premises / Bastion]
         │ (ExpressRoute / VNet Peering)
         ▼
[Private DNS Zone] ──► [AKS API Server (private endpoint IP)]
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
        [Pod A (Frontend)]             [Pod B (Backend)]
                 │                             ▲
                 └──► NetworkPolicy ───────────┘
                      (TCP 8080 from frontend only)
```

**Trade-offs.** Private clusters complicate operations (DNS, agents, access for support engineers) and do not protect workloads - only the API endpoint. Network policies are only as good as their default-deny baseline and need testing; a missing egress allow for DNS or the metadata endpoint is a common self-inflicted outage.

### Real-World Production Scenario

A healthcare provider deploys an EHR service on AKS as a private cluster, with the private DNS zone linked to the hub VNet so operators on ExpressRoute and self-hosted pipeline agents can reach the API server. Each namespace gets a default-deny policy, and the database tier accepts connections on port 5432 only from the backend API Pods.

## Example

```bash
# Private cluster with Azure CNI Overlay, Calico network policy, Entra RBAC, and workload identity
az aks create -g rg-aks-prod -n aks-ehr-prod \
  --enable-private-cluster \
  --network-plugin azure --network-plugin-mode overlay \
  --network-policy calico \
  --vnet-subnet-id "$AKS_SUBNET_ID" \
  --enable-aad --enable-azure-rbac --disable-local-accounts \
  --enable-oidc-issuer --enable-workload-identity \
  --zones 1 2 3

# Ad-hoc access without a network path to the private API server
az aks command invoke -g rg-aks-prod -n aks-ehr-prod --command "kubectl get pods -n production"
```

```yaml
# Default-deny for the namespace, then an explicit allow (standard NetworkPolicy, enforced by Calico)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: production
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-from-backend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: postgres
  policyTypes: [Ingress]
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: backend
      ports:
        - protocol: TCP
          port: 5432
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: production
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
          podSelector:
            matchLabels:
              k8s-app: kube-dns
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```

## Interview tips

- Explain how administrators and pipelines reach a private cluster: Bastion or jump box, peering or ExpressRoute/VPN, self-hosted agents, or `az aks command invoke`.
- Mention the private DNS zone and hub linking as the usual failure point.
- Clarify roles: Azure CNI (or Overlay) provides Pod networking; Calico or Cilium enforces policy on top.
- Say that Cilium is the recommended engine for new clusters and Azure Network Policy Manager is being retired, while Calico remains supported.
- Start from default-deny and remember the DNS egress allow - that detail shows hands-on experience.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Cloud Computing?]] (`#21`): [What is Cloud Computing?](../cloud-platforms/what-is-cloud-computing.md)
- [[What is Azure?]] (`#23`): [What is Azure?](../cloud-platforms/what-is-azure.md)
- [[What is Google Cloud Platform (GCP)?]] (`#24`): [What is Google Cloud Platform (GCP)?](../cloud-platforms/what-is-google-cloud-platform-gcp.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Azure Engineering](./README.md) · [All topics](../README.md)
