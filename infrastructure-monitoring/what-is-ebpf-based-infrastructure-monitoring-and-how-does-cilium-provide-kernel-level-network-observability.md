---
title: "What is eBPF-based infrastructure monitoring and how does Cilium provide kernel-level network observability?"
id: 689
category: "Infrastructure Monitoring"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - monitoring
  - ebpf
  - cilium
  - hubble
  - networking
quiz:
  stem: "How does Cilium with eBPF achieve L7 HTTP observability and security filtering in Kubernetes without injecting sidecar proxy containers?"
  options:
    - "By running an SSH tunnel inside every container"
    - "By using eBPF in the kernel datapath to transparently redirect selected traffic to a shared per-node Envoy proxy that parses HTTP, instead of injecting a proxy into every Pod"
    - "By modifying the source code of the Linux kernel itself"
    - "By compiling application code into WebAssembly"
  answer: 2
  explanation: "Cilium enforces and observes L3/L4 traffic in eBPF directly; for L7 (HTTP, gRPC, Kafka, DNS) it uses eBPF to redirect only the flows that need it to a node-local Envoy, so no sidecar is injected into application Pods."
---

# What is eBPF-based infrastructure monitoring and how does Cilium provide kernel-level network observability?

**Short answer:** eBPF attaches verified bytecode programs directly to kernel hooks (tracepoints, kprobes, sockets, `tc`/XDP), capturing network flows, TCP drops, and security events with low overhead and without injecting sidecars or modifying application code. Cilium uses eBPF as its Kubernetes networking datapath, and Hubble exposes the resulting flow data.

## Detail

Traditional container network monitoring relied on parsing `/proc` or injecting Envoy sidecars into every pod. Sidecars introduce high CPU/memory tax and cannot see kernel-level socket drops.

### How Cilium and Hubble Use eBPF

Cilium implements pod networking and network policy with in-kernel eBPF programs attached to Linux `tc` (traffic control), socket, and XDP (eXpress Data Path) hooks, and can optionally replace `kube-proxy` entirely:

1. **Kernel-Level Packet Forwarding**: Routes packets directly between veth interfaces and BPF maps in kernel space, bypassing iptables lookup chains.
2. **Deep L3/L4/L7 Observability (Hubble)**:
   - Captures exact TCP retransmission rates, connection resets, and DNS resolution latency without sidecars.
   - L7 visibility: HTTP methods, paths, and status codes (and DNS, gRPC, Kafka) are parsed by a per-node Envoy proxy that eBPF redirects the relevant flows to - sidecar-free, but not purely in-kernel, and it must be enabled per workload via L7 policy or visibility settings.
3. **Runtime Security (Tetragon)**: Cilium's sister project Tetragon uses eBPF to observe and optionally block process executions and file access inside containers (e.g. an NGINX container spawning `/bin/bash` or touching `/etc/shadow`) in the kernel, before the action completes.

**Trade-offs.** eBPF requires a reasonably modern kernel (features vary by version), debugging the datapath needs new skills (`cilium-dbg`, `bpftool`, Hubble), and L7 visibility still costs proxy CPU. Retaining every flow is expensive, so Hubble flow export is usually filtered or aggregated into metrics.

## Example

```bash
cilium hubble enable --ui            # enable Hubble Relay and UI (cilium-cli)
cilium hubble port-forward &         # expose Relay locally for the hubble CLI

# Every dropped packet in a namespace, with the policy verdict and reason
hubble observe --namespace prod --verdict DROPPED --follow

# HTTP 5xx responses seen at L7 (requires L7 visibility for that workload)
hubble observe --namespace prod --protocol http --http-status 5+

# DNS lookups that failed
hubble observe --namespace prod --protocol dns --verdict DROPPED
```

## Interview tips

- eBPF executing sandboxed code directly inside the Linux kernel.
- Bypassing iptables and sidecar proxy resource overhead.
- Cilium and Hubble providing deep L3/L4/L7 flow observability.
- Detecting TCP connection resets, drops, and DNS latency with zero app modifications.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do Docker bridge, host, and macvlan network drivers differ in packet routing and isolation?]] (`#517`): [How do Docker bridge, host, and macvlan network drivers differ in packet routing and isolation?](../docker/how-do-docker-bridge-host-and-macvlan-network-drivers-differ-in-packet-routing-and-isolation.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure Monitoring](./README.md) · [All topics](../README.md)
