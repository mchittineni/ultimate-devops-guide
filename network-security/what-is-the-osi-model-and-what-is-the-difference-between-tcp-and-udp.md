---
title: "What is the OSI model, and what is the difference between TCP and UDP?"
id: 489
category: "Network Security"
difficulty: "Beginner"
tags:
  - devops
  - network-security
  - interview-questions
  - linux-administration
---

# What is the OSI model, and what is the difference between TCP and UDP?

**Short answer:** The OSI model is a seven-layer reference for how network communication is structured: **1 Physical** (cables, radio, signalling), **2 Data Link** (frames, MAC addresses, switches, VLANs), **3 Network** (IP addresses, routing, ICMP), **4 Transport** (TCP and UDP, ports, end-to-end delivery), **5 Session**, **6 Presentation** (traditionally encryption and encoding), and **7 Application** (HTTP, DNS, TLS in practice, gRPC). The value for a DevOps engineer is not reciting it - it is that it gives you a **fault-isolation order**: cable/interface, then ARP/switching, then IP routing, then TCP handshake and ports, then the application protocol. **TCP** is connection-oriented and reliable: a three-way handshake, sequence numbers, acknowledgements, retransmission, ordering, and congestion control - so it costs a round trip to set up and can add latency when it retransmits. **UDP** is connectionless and fire-and-forget: no handshake, no ordering, no retransmission, minimal header - so it is faster and lighter, and the application must handle loss itself. Use TCP when correctness matters (HTTP, SSH, databases) and UDP when timeliness matters more than completeness (DNS, DHCP, NTP, VoIP, video, QUIC/HTTP-3, and most metrics shipping).

## Detail

### The layers, with what you actually touch at each

| Layer          | Unit    | Examples                                           | What you debug there                                       |
| -------------- | ------- | -------------------------------------------------- | ---------------------------------------------------------- |
| 7 Application  | Message | HTTP, DNS, gRPC, SMTP, SSH                         | Status codes, headers, TLS SNI, application logs           |
| 6 Presentation | -       | Serialisation, encoding, (historically) encryption | Content negotiation, charset, TLS in the OSI purist's view |
| 5 Session      | -       | Session establishment/teardown                     | Sticky sessions, connection reuse                          |
| 4 Transport    | Segment | **TCP**, **UDP**, QUIC (over UDP)                  | Ports, handshake, `SYN` retries, MSS/MTU, timeouts         |
| 3 Network      | Packet  | IP, ICMP, routing, NAT                             | Routes, subnets, `traceroute`, "no route to host"          |
| 2 Data Link    | Frame   | Ethernet, ARP, VLANs, switches                     | ARP tables, MAC, duplicate IPs, VLAN tagging               |
| 1 Physical     | Bits    | Cable, fibre, Wi-Fi, NIC                           | Link state, error counters, "the cable is out"             |

In practice the industry mostly uses the four-layer **TCP/IP model** (Link, Internet, Transport, Application) and folds 5-7 into "Application" - which is why arguments about whether TLS is layer 6 or 7 are unproductive. What matters is where a **load balancer** sits: a **layer 4** load balancer forwards by IP and port without reading the payload; a **layer 7** load balancer terminates the connection, parses HTTP, and can route by host and path. That is the single most useful application of the model in a DevOps interview.

### Placing real tools on the model

```text
7  ALB / Application Gateway / nginx / API gateway / WAF / Envoy / CoreDNS / Ingress
6  TLS termination, gRPC/protobuf, gzip
5  session affinity, connection pools
4  NLB / Azure Load Balancer / security groups (port level) / kube-proxy / iptables NAT
3  VPC route tables, NACLs, VPC peering, Transit Gateway, CNI overlay, ICMP
2  VLANs, ENIs, ARP, MAC filtering
1  the data-centre and the cable you will never see
```

Being able to say "a security group is effectively layer 3/4, a WAF is layer 7, so a security group cannot block SQL injection" is exactly the kind of statement that shows the model is a working tool for you rather than a memorised list.

### TCP versus UDP

|                           | TCP                                               | UDP                                               |
| ------------------------- | ------------------------------------------------- | ------------------------------------------------- |
| Connection                | Three-way handshake (`SYN` → `SYN-ACK` → `ACK`)   | None                                              |
| Reliability               | Acknowledged, retransmitted                       | None - loss is invisible to the sender            |
| Ordering                  | Guaranteed                                        | Not guaranteed                                    |
| Flow / congestion control | Yes (windowing, slow start, backoff)              | No                                                |
| Header                    | 20+ bytes                                         | 8 bytes                                           |
| Latency                   | One RTT before data; retransmits add tail latency | Lowest possible                                   |
| Broadcast/multicast       | No                                                | Yes                                               |
| Typical use               | HTTP/1.1 and 2, SSH, TLS, SQL, SMTP               | DNS, DHCP, NTP, syslog, StatsD, VoIP, video, QUIC |

Details worth having ready:

- **Teardown** uses `FIN`/`FIN-ACK`, and the closing side sits in `TIME_WAIT` for twice the maximum segment lifetime - which is why a busy proxy accumulates `TIME_WAIT` sockets and why port exhaustion is a real failure mode at high connection churn (`ss -s` shows it; connection reuse and keep-alive are the fix).
- **DNS uses UDP 53** for normal queries and falls back to **TCP 53** when a response exceeds 512 bytes (or with DNSSEC and zone transfers) - which is why a firewall that allows only UDP 53 breaks resolution intermittently and mysteriously. This is a genuinely common production bug and a great thing to volunteer.
- **QUIC / HTTP-3 runs over UDP** and re-implements reliability, ordering, and congestion control in user space, plus TLS 1.3 in the handshake - so "UDP is unreliable" is a property of the protocol, not a limitation you are stuck with.
- **MTU and MSS**: a mismatch (common with overlay networks and VPN tunnels) makes small requests work and large responses hang, because the oversized packet is dropped and ICMP "fragmentation needed" is often filtered. `ping -M do -s 1472` locates it; MSS clamping fixes it.
- **`SYN` retries** are what you see when a port is filtered: a `DROP` gives you a hanging connect and a timeout, while a `REJECT`/RST gives you an immediate "connection refused". That difference tells you whether a firewall is dropping or nothing is listening - one of the most useful diagnostic distinctions there is.

### The fault-isolation order, which is the real answer

When something cannot reach something, work up the layers instead of guessing:

1. **L1/L2** - is the interface up, does ARP resolve the next hop?
2. **L3** - `ip route get`, `ping`, `traceroute`/`mtr`: is there a route, and where does it stop?
3. **L4** - `nc -vz host port`, `ss -ltnp`: is anything listening, and is the port reachable? Hanging = dropped; refused = nothing listening.
4. **TLS** - `openssl s_client -connect host:443 -servername name`: certificate, chain, SNI, protocol version.
5. **L7** - `curl -v`, status codes, headers, application logs.

In cloud terms that maps to: route tables and peering (L3) → NACLs and security groups (L3/L4) → target group health (L4/L7) → WAF and application (L7). Saying that mapping out loud is what makes the OSI answer useful rather than academic.

### IPv4, IPv6, and the classes question

- An **IPv4** address is 32 bits, written as four dotted octets, valid range `0.0.0.0`-`255.255.255.255`. The **first octet** historically indicated class (A: 1-126, B: 128-191, C: 192-223, D: 224-239 multicast, E: 240-255 experimental), and `127.x.x.x` is loopback. Classful addressing is obsolete - **CIDR** replaced it - but the first-octet question still gets asked, and the honest answer is "historically class A/B/C, and it also tells you whether the address is loopback, multicast, or link-local; in practice we use CIDR prefixes."
- **Private ranges** (RFC 1918): `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, plus `169.254.0.0/16` link-local (which is where the cloud metadata service lives at `169.254.169.254`).
- **IPv6** is 128 bits in hexadecimal groups with `::` compression. It solves address exhaustion (so no NAT is needed), and brings simplified headers, mandatory multicast instead of broadcast, and stateless address autoconfiguration. In cloud terms it also removes the "we ran out of subnet IPs" class of problem that VPC-native Kubernetes networking runs into.

## Example

```bash
# Isolate the fault by layer, in order. Each command answers exactly one question.
ip -br addr ; ip -br link                 # L1/L2: interface up, address assigned?
ip neigh show                              # L2: does ARP resolve the gateway?
ip route get 10.20.1.10                    # L3: is there a route, and via what?
mtr -rwzc 20 10.20.1.10                    # L3: where does the path break?
nc -vz 10.20.1.10 5432                     # L4: reachable? hang=DROP, refused=nothing listening
ss -ltnp | grep 5432                        # L4: is anything actually listening, and as whom?
openssl s_client -connect api.example.com:443 -servername api.example.com </dev/null \
  | openssl x509 -noout -subject -dates    # TLS: cert, chain, SNI
curl -sS -o /dev/null -w '%{http_code} %{time_connect} %{time_starttransfer}\n' \
  https://api.example.com/healthz          # L7: status and where the time goes
```

```bash
# TCP versus UDP, visible
sudo tcpdump -ni any 'tcp port 443 and (tcp[tcpflags] & (tcp-syn|tcp-rst) != 0)'
#   repeated SYN with no SYN-ACK  -> filtered/dropped upstream
#   immediate RST                 -> nothing listening, or actively refused

dig +short A example.com @1.1.1.1            # UDP 53
dig +tcp +short A example.com @1.1.1.1       # TCP 53 - blocked? large answers break
dig +dnssec DNSKEY example.com | wc -c        # >512 bytes -> needs TCP fallback

# MTU: works small, hangs large -> classic overlay/VPN MSS problem
ping -M do -s 1472 10.20.1.10   # 1472 + 28 = 1500. Fails? lower until it passes
ip link show eth0 | grep -o 'mtu [0-9]*'

# TIME_WAIT / port exhaustion on a busy proxy
ss -s ; ss -tan state time-wait | wc -l
```

```text
Where the cloud controls sit - the mapping that makes OSI useful

  L7   WAF rules, ALB path routing, API gateway auth, Ingress, service mesh policy
  L4   security groups (port), NLB, kube-proxy/iptables, connection draining
  L3   route tables, NACLs, VPC peering / Transit Gateway, CNI routing, ICMP
  L2   ENIs, VLANs, ARP  (mostly invisible in cloud)
  L1   the provider's problem

  => "a security group cannot block SQL injection" - it is L3/L4, the WAF is L7.
```

## Interview tips

- Recite the seven layers with one concrete example each, then immediately pivot to why it matters: it gives you a **fault-isolation order**, and it explains the layer 4 versus layer 7 load balancer distinction.
- Place real tools on the model out loud - WAF and ALB at 7, NLB and security groups at 4, route tables and NACLs at 3. That converts a memory test into evidence of working knowledge.
- Note that the industry mostly uses the four-layer TCP/IP model and that arguing about whether TLS is 6 or 7 is unproductive. Being able to say that reads as confidence rather than ignorance.
- For TCP versus UDP, lead with connection-oriented-and-reliable versus connectionless-and-lightweight, then name the mechanisms: handshake, sequence numbers, acknowledgements, retransmission, congestion control.
- Volunteer the **DNS UDP 53 with TCP fallback above 512 bytes** detail, and the firewall bug it causes. It is specific, real, and very few candidates mention it.
- Mention QUIC/HTTP-3 running over UDP with reliability re-implemented in user space, so "UDP is unreliable" is not the end of the story.
- Have the hang-versus-refused distinction ready: a dropped packet gives you `SYN` retries and a timeout, a rejected one gives you an instant "connection refused". It is the fastest way to tell a firewall problem from a dead service.
- Add MTU/MSS mismatch as the cause of "small requests work, large responses hang" - the classic overlay-network and VPN symptom.
- For IPv4 classes, answer historically and then say CIDR replaced it, listing the RFC 1918 private ranges and `169.254.169.254` as the metadata endpoint. See [what happens when a user opens your application in a browser](./what-happens-when-a-user-opens-your-application-in-a-browser.md), [how do you plan CIDR ranges and subnets](./how-do-you-plan-cidr-ranges-and-subnets.md), [what is the difference between a layer 4 and a layer 7 load balancer](../scalability-and-high-availability/what-is-the-difference-between-a-layer-4-and-a-layer-7-load-balancer.md), and [how do you troubleshoot a DNS problem in production](../cloud-engineering/how-do-you-troubleshoot-a-dns-problem-in-production.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot Docker networking between containers?]] (`#415`): [How do you troubleshoot Docker networking between containers?](../docker/how-do-you-troubleshoot-docker-networking-between-containers.md)
- [[How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?]] (`#402`): [How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?](../cicd/how-do-you-troubleshoot-a-jenkins-pipeline-that-never-starts-or-hangs-in-the-queue.md)
- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Network Security](./README.md) · [All topics](../README.md)
