---
title: "What is the Container Network Interface (CNI) and how do overlay and routed CNI plugins differ?"
id: 528
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - kubernetes
  - cni
  - networking
  - overlay
quiz:
  stem: "What is a major trade-off of using a native routed CNI (such as AWS VPC CNI) instead of an overlay CNI (such as VXLAN-based Flannel)?"
  options:
    - "Routed CNIs cannot enforce NetworkPolicies"
    - "Routed CNIs assign VPC subnet IP addresses to every pod, which can rapidly exhaust the VPC's available IP address pool"
    - "Routed CNIs impose a 50-byte packet header overhead on all network traffic"
    - "Overlay CNIs require external hardware routers on each node"
  answer: 2
  explanation: "Native routed CNIs draw Pod IPs directly from the underlying VPC subnet. While this eliminates encapsulation overhead, large clusters can quickly exhaust the VPC CIDR."
---

# What is the Container Network Interface (CNI) and how do overlay and routed CNI plugins differ?

**Short answer:** CNI (Container Network Interface) is a CNCF specification plus a set of plugins: when a Pod sandbox is created, the container runtime calls a CNI plugin binary with the Pod's network namespace, and the plugin creates its interface, assigns an IP, and sets up routes. **Overlay** plugins give Pods addresses from a private cluster range and encapsulate Pod-to-Pod traffic between nodes in VXLAN or Geneve tunnels, so they work on any underlying network but cost MTU and some CPU. **Routed** (flat) plugins make Pod IPs directly routable - from the cloud VPC's own subnets or advertised via BGP - so there is no encapsulation, but Pod addresses consume real network address space and the underlay must know how to reach them.

## Detail

**How the interface works.** The kubelet asks the CRI runtime (containerd or CRI-O) to create a Pod sandbox; the runtime reads the network config from `/etc/cni/net.d/` and executes the plugin binaries from `/opt/cni/bin/` with `ADD` (and later `DEL`, `CHECK`) plus the namespace path. Plugins are chained: a main plugin (Calico, Cilium, AWS VPC CNI, Flannel) typically delegates IP allocation to an IPAM plugin, and helpers like `portmap` or `bandwidth` add features. A node reports `NetworkUnavailable` or `NetworkPluginNotReady` until a valid config exists, which is why a broken CNI DaemonSet makes nodes `NotReady`.

CNI only wires up Pod interfaces. Service load balancing is kube-proxy's job (or the CNI's eBPF replacement), and NetworkPolicy enforcement is an optional extra that some plugins implement and others, such as plain Flannel, do not.

### Overlay versus routed

| Dimension         | Overlay (Flannel VXLAN, Calico VXLAN/IPIP, Cilium tunnel mode)                     | Routed / flat (AWS VPC CNI, Azure CNI, GKE VPC-native, Calico BGP, Cilium native routing) |
| ----------------- | ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Packet path       | Pod packet wrapped in an outer UDP packet (VXLAN on port 4789) between nodes       | Pod packet routed as-is; the VPC route table or BGP knows each node's Pod range or Pod IP |
| MTU               | Around 50 bytes lost to VXLAN over IPv4 (Geneve varies); Pod MTU must be set lower | Full underlay MTU (1500, or 9001 on AWS jumbo frames)                                     |
| CPU               | Encapsulation and decapsulation per packet (often offloaded by modern NICs)        | None for encapsulation                                                                    |
| Address space     | Pod CIDR is independent of the VPC; large clusters do not consume VPC addresses    | Pods consume VPC or routed addresses - IP exhaustion is a real capacity limit             |
| Cloud integration | Pod IPs invisible to VPC security groups and flow logs (they see node IPs)         | Pod IPs visible to VPC tooling; per-Pod security groups possible on some platforms        |
| Underlay needs    | Only node-to-node IP reachability and the tunnel port open                         | Cloud integration or BGP peering with the network fabric                                  |

Cloud providers blur the line with hybrids: **Azure CNI Overlay**, AWS VPC CNI **prefix delegation** and custom networking (Pods in a secondary CIDR), and IPv6 clusters all exist to relieve IP exhaustion while keeping most of the routed model's benefits.

**Choosing.** Routed is the default on managed clouds because it is fastest and integrates with cloud firewalls and flow logs; plan subnet sizes for Pods, not just nodes. Overlay suits on-premises or multi-environment clusters where you do not control the network, or where VPC address space is scarce. eBPF plugins (Cilium, Calico eBPF) can run either way and additionally replace kube-proxy and add richer policy and observability. Weave Net, once a common overlay choice, has been unmaintained since Weaveworks closed in 2024 and should be migrated off.

## Example

```json
{
  "cniVersion": "1.0.0",
  "name": "cbr0",
  "plugins": [
    { "type": "flannel", "delegate": { "hairpinMode": true, "isDefaultGateway": true } },
    { "type": "portmap", "capabilities": { "portMappings": true } }
  ]
}
```

```bash
# Which CNI is installed, and is it healthy on every node?
ls /etc/cni/net.d/ /opt/cni/bin/
kubectl -n kube-system get ds                         # calico-node, cilium, aws-node, kube-flannel...
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"  "}{.spec.podCIDR}{"\n"}{end}'

# Overlay symptom check: small requests work, large ones hang -> MTU
kubectl exec -it netshoot -- ping -M do -s 1472 10.244.3.17   # fails on a VXLAN overlay with 1500 MTU
kubectl exec -it netshoot -- ping -M do -s 1422 10.244.3.17   # fits once the ~50-byte overhead is subtracted
```

## Interview tips

- Explain what CNI actually is: a spec and plugin binaries invoked by the runtime with `ADD`/`DEL` for each Pod sandbox - not a daemon, and not responsible for Services.
- Contrast overlay and routed on four axes: encapsulation, MTU, address space, and cloud visibility.
- Name the routed model's real risk - VPC IP exhaustion - and the mitigations (prefix delegation, secondary CIDRs, overlay modes, IPv6).
- Name the overlay model's classic bug - an MTU mismatch where small packets work and large responses hang.
- Mention that NetworkPolicy depends on the plugin: Flannel alone does not enforce it, Calico and Cilium do.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do Docker bridge, host, and macvlan network drivers differ in packet routing and isolation?]] (`#517`): [How do Docker bridge, host, and macvlan network drivers differ in packet routing and isolation?](../docker/how-do-docker-bridge-host-and-macvlan-network-drivers-differ-in-packet-routing-and-isolation.md)
- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
