---
title: "What is the difference between Service Discovery mechanisms in Kubernetes vs HashiCorp Consul?"
id: 704
category: "Advanced DevOps & Cloud"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - service-discovery
  - consul
  - kubernetes
  - dns
  - networking
quiz:
  stem: "In what environment is HashiCorp Consul strongly preferred over native Kubernetes CoreDNS for service discovery?"
  options:
    - "In a standalone single-node minikube development setup"
    - "In heterogeneous hybrid environments where services running on legacy on-premise VMs must discover and communicate with microservices running in cloud Kubernetes clusters"
    - "Consul can only be used with Windows 95"
    - "Consul only supports static IP addresses"
  answer: 2
  explanation: "Kubernetes DNS only knows about pods inside its own cluster. Consul operates across heterogeneous infrastructure, unifying VMs, bare metal, and multiple cloud clusters into a single catalog."
---

# What is the difference between Service Discovery mechanisms in Kubernetes vs HashiCorp Consul?

**Short answer:** Kubernetes discovery is built in and cluster-scoped: a `Service` gets a stable virtual IP and a CoreDNS name (`svc.namespace.svc.cluster.local`), EndpointSlices track ready Pods, and kube-proxy (or an eBPF data plane such as Cilium) load-balances to them. Consul is an external service catalogue that spans VMs, bare metal, Nomad, and multiple Kubernetes clusters and datacentres, with its own health checks, DNS and HTTP interfaces, and an optional service mesh. Choose Kubernetes-native when everything lives in one cluster; Consul (or a multi-cluster mesh) when discovery must cross platforms and sites - at the cost of operating another stateful system, now under HashiCorp's Business Source Licence.

## Detail

**Kubernetes-native**

- The API server is the registry: a Service selects Pods by label, and the EndpointSlice controller publishes only **Ready** endpoints (readiness probes are the health check).
- CoreDNS answers `A`/`AAAA` records for the ClusterIP (or Pod IPs for headless Services) and `SRV` records for named ports.
- kube-proxy programs iptables, IPVS, or nftables rules; eBPF data planes replace it entirely.
- **Scope:** one cluster. Cross-cluster needs the Multi-Cluster Services API (`clusterset.local`), a mesh, or external DNS. A VM outside the cluster cannot register itself.

**Consul**

- A Raft-replicated server cluster holds the catalogue; services register through agents on VMs, or - on Kubernetes - via the catalog sync / Consul dataplane integration, which uses Kubernetes health instead of per-node client agents.
- **Health checks** run close to the service (HTTP, TCP, gRPC, script, TTL); failing instances drop out of DNS (`web.service.consul`) and HTTP API answers.
- **Multi-datacentre** by design: WAN federation or cluster peering lets `web.service.dc2.consul` resolve across sites, and prepared queries can fail over to another datacentre automatically.
- **Consul service mesh** adds Envoy-based mTLS and intentions (service-to-service authorisation), the part of Consul most often compared with Istio.
- It also offers a KV store, which is why older stacks use it for configuration.

**Comparison**

| Dimension    | Kubernetes Service + CoreDNS    | Consul                                                     |
| ------------ | ------------------------------- | ---------------------------------------------------------- |
| Scope        | Single cluster                  | Many clusters, VMs, bare metal, datacentres                |
| Registration | Automatic from Pod labels       | Agents / sync / API registration                           |
| Health       | Readiness probes on the kubelet | Consul checks, or Kubernetes readiness when synced         |
| Operations   | Nothing extra                   | A Raft cluster to run, back up, upgrade, and secure (ACLs) |
| Licence      | Apache 2.0                      | BSL 1.1 since 2023 (HashiCorp is now part of IBM)          |

## Example

```bash
# Kubernetes: what the cluster thinks "payments" is
kubectl get svc payments -n prod
kubectl get endpointslice -n prod -l kubernetes.io/service-name=payments
kubectl run -it --rm dns --image=busybox:1.36 -- nslookup payments.prod.svc.cluster.local

# Consul: the same service seen from any datacentre, healthy instances only
dig @127.0.0.1 -p 8600 payments.service.consul SRV
dig @127.0.0.1 -p 8600 payments.service.dc2.consul
curl -s "http://127.0.0.1:8500/v1/health/service/payments?passing" | jq '.[].Service.Address'
```

## Interview tips

- Start from scope: Kubernetes discovery is cluster-local and zero-effort; Consul is multi-platform and multi-datacentre but is another system to operate.
- Say that in Kubernetes the readiness probe _is_ the health check for discovery - unready Pods are removed from EndpointSlices.
- Mention the Multi-Cluster Services API and multi-cluster meshes as the Kubernetes-native alternatives before reaching for Consul.
- Note the licence change (BSL) as a procurement factor, without overstating it - it restricts competing hosted offerings, not ordinary internal use.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[What are ephemeral preview environments and how do you manage their lifecycle and cleanup?]] (`#535`): [What are ephemeral preview environments and how do you manage their lifecycle and cleanup?](../cicd/what-are-ephemeral-preview-environments-and-how-do-you-manage-their-lifecycle-and-cleanup.md)
- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
