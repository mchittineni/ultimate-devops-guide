---
title: "How do Docker bridge, host, and macvlan network drivers differ in packet routing and isolation?"
id: 517
category: "Docker"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - docker
  - networking
  - bridge
  - macvlan
quiz:
  stem: "When running a container with `--network host`, what happens if the containerized app attempts to bind to port 80?"
  options:
    - "Docker automatically remaps port 80 to port 8080 on the host"
    - "The container binds directly to port 80 on the host's network interface and will fail if another host process is using port 80"
    - "Traffic is routed through the default `docker0` bridge via NAT"
    - "The container fails to start because host mode only supports UDP traffic"
  answer: 2
  explanation: "Host networking shares the host network namespace. There is no port translation or isolation; conflicts with host ports will cause port binding errors."
---

# How do Docker bridge, host, and macvlan network drivers differ in packet routing and isolation?

**Short answer:** **Bridge** (the default) gives each container its own network namespace with a veth pair plugged into a Linux bridge on a private subnet; outbound traffic is masqueraded (SNAT) to the host's IP and inbound traffic reaches the container only through published ports, which Docker implements with DNAT firewall rules. **Host** skips the network namespace entirely: the container uses the host's interfaces, IPs, and port space, so there is no NAT, no port mapping, and no network isolation. **Macvlan** gives each container its own MAC address and an IP on the physical LAN through a sub-interface of a host NIC, so it appears as a separate machine on the network, with no NAT - but it needs the network to accept multiple MACs per port, and by default the host itself cannot talk to its macvlan containers.

## Detail

| Driver    | Namespace | Addressing                               | How packets flow                                                                                      | Isolation                                                   | Typical use                                                        |
| --------- | --------- | ---------------------------------------- | ----------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------ |
| `bridge`  | Own       | Private subnet (default `172.17.0.0/16`) | veth → `docker0` or user bridge → host routing; SNAT out, DNAT in for published ports                 | Containers isolated from the LAN except via published ports | Standalone containers, local development, Compose                  |
| `host`    | Host's    | The host's own IPs                       | Straight onto the host stack - no veth, no NAT                                                        | None at the network layer                                   | Maximum throughput or many ports (monitoring agents, some proxies) |
| `macvlan` | Own       | An IP on the physical subnet, unique MAC | Sub-interface of the parent NIC; frames go directly onto the LAN, bypassing the host's bridge and NAT | Separate L2 identity; host-to-container blocked by default  | Legacy apps that must have a LAN IP; network appliances            |

**Bridge details.** User-defined bridges (`docker network create`) are preferred over the default `bridge`: they provide an embedded DNS server at `127.0.0.11` so containers resolve each other by name, and they isolate unrelated stacks from each other. Publishing `-p 8080:80` binds on all host addresses by default - including public ones - so bind to `127.0.0.1:8080:80` for local-only services. Docker programmes these rules with iptables (nftables support arrived experimentally in Docker Engine 29), which is why host firewalls like `ufw` are bypassed by published ports unless you add rules in the `DOCKER-USER` chain.

**Host details.** No port mapping is possible (`-p` is ignored), port conflicts with host processes are real, and the container can reach services bound to the host's `localhost`. It is fast because there is no veth hop or conntrack NAT, but it throws away the network namespace's protection. On Docker Desktop, host networking applies to the Linux VM rather than your Mac or Windows machine unless the feature is explicitly enabled.

**Macvlan details.**

- Needs a parent interface (`-o parent=eth0`) and the switch or hypervisor must allow multiple MAC addresses on the port; most public-cloud VPCs drop frames from unknown MACs, so macvlan generally does not work there.
- The host cannot reach its own macvlan containers through the parent interface - a kernel design choice. The workaround is a macvlan sub-interface on the host itself.
- **IPvlan** is the alternative when MAC addresses are the problem: containers share the parent's MAC and get distinct IPs (L2 mode) or are routed (L3 mode).

**Trade-offs.** Bridge costs a little latency and CPU for NAT and conntrack but gives the best isolation; host gives the best performance and the least isolation; macvlan gives LAN-native addressing without NAT but depends on the physical network and is awkward to manage (IP allocation, DHCP conflicts). For multi-host networking, Swarm uses the `overlay` driver and Kubernetes uses CNI plugins rather than any of these.

## Example

```bash
# Bridge: user-defined network with name resolution and a local-only published port
docker network create app-net
docker run -d --name api --network app-net -p 127.0.0.1:8080:8080 registry.example.com/api:1.4.0
docker run --rm --network app-net busybox:1.37 wget -qO- http://api:8080/healthz

# Host: no namespace, no port mapping - binds straight onto the host's port 9100
docker run -d --name node-exporter --network host prom/node-exporter:v1.9.1

# Macvlan: a LAN address for the container on the eth0 subnet
docker network create -d macvlan \
  --subnet 192.168.10.0/24 --gateway 192.168.10.1 \
  --ip-range 192.168.10.192/27 -o parent=eth0 lan-net
docker run -d --name legacy --network lan-net --ip 192.168.10.200 registry.example.com/legacy:2.0

# See what Docker programmed for the bridge
sudo iptables -t nat -L DOCKER -n    # DNAT rules for published ports
ip link show type bridge             # docker0 and br-<id> bridges
```

## Interview tips

- Describe the packet path for each: veth plus bridge plus NAT; straight onto the host stack; a MAC-level sub-interface onto the LAN.
- Rank them on isolation versus performance and say why host mode is fast (no veth, no NAT) and risky (no network namespace).
- Mention the user-defined bridge's embedded DNS and that `-p` binds to all interfaces by default.
- Know macvlan's two gotchas: the host cannot reach its own macvlan containers, and cloud networks usually drop unknown MACs - then offer IPvlan.
- Bring up the `DOCKER-USER` chain when asked why published ports ignore the host firewall.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does the Kubernetes Gateway API evolve beyond standard Ingress resources?]] (`#520`): [How does the Kubernetes Gateway API evolve beyond standard Ingress resources?](../kubernetes/how-does-the-kubernetes-gateway-api-evolve-beyond-standard-ingress-resources.md)
- [[How does CoreDNS resolve services in Kubernetes and how do you troubleshoot DNS latency bottlenecks?]] (`#527`): [How does CoreDNS resolve services in Kubernetes and how do you troubleshoot DNS latency bottlenecks?](../kubernetes/how-does-coredns-resolve-services-in-kubernetes-and-how-do-you-troubleshoot-dns-latency-bottlenecks.md)
- [[What is the Container Network Interface (CNI) and how do overlay and routed CNI plugins differ?]] (`#528`): [What is the Container Network Interface (CNI) and how do overlay and routed CNI plugins differ?](../kubernetes/what-is-the-container-network-interface-cni-and-how-do-overlay-and-routed-cni-plugins-differ.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
