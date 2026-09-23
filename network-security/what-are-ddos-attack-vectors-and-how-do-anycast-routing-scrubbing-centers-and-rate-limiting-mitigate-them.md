---
title: "What are DDoS attack vectors and how do Anycast routing, scrubbing centers, and rate limiting mitigate them?"
id: 671
category: "Network Security"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - network-security
  - ddos
  - anycast
  - cloudflare
  - cdn
quiz:
  stem: "How does BGP Anycast routing mitigate massive global volumetric DDoS attacks?"
  options:
    - "By blocking all UDP network packets automatically"
    - "By advertising the same IP address from hundreds of data centers worldwide, dispersing the attack traffic across global infrastructure rather than concentrating it on a single server"
    - "By encrypting the target server's hard drive"
    - "By changing the application's domain name every hour"
  answer: 2
  explanation: "Anycast allows multiple physical edge locations to share one IP. Incoming traffic routes to the nearest physical point of presence, diluting a massive global flood across hundreds of data centers."
---

# What are DDoS attack vectors and how do Anycast routing, scrubbing centers, and rate limiting mitigate them?

**Short answer:** DDoS attacks flood targets via volumetric (UDP/NTP amplification), protocol (SYN floods), or application (HTTP GET/POST floods) vectors; mitigation relies on Anycast routing to disperse traffic across hundreds of edge POPs, scrubbing centers to filter malicious packets, and edge rate limiting.

## Detail

Distributed Denial of Service (DDoS) attempts to exhaust server compute, network bandwidth, or connection tables:

### Attack Categories

1. **Volumetric (L3/L4)**: Multi-terabit floods (reflection/amplification via DNS, NTP, memcached, CLDAP; raw UDP floods from IoT botnets) designed to saturate links. Publicly reported peaks have passed 20 Tbps, far beyond any single data centre's capacity.
2. **Protocol (L4)**: SYN floods exhausting the half-open connection queue (`net.ipv4.tcp_max_syn_backlog`), ACK/RST floods, and state-exhaustion attacks against stateful firewalls and load balancers.
3. **Application Layer (L7)**: Requests that are cheap to send and expensive to serve (`POST /search` with a costly query, cache-busting query strings) consuming database CPU with minimal attacker bandwidth. Protocol abuse lives here too: **HTTP/2 Rapid Reset** (CVE-2023-44487) opened and cancelled streams in a tight loop to produce record request rates from a small botnet.

### Mitigation Architecture

- **BGP Anycast Routing**: The same public IP address is advertised by hundreds of global edge data centers simultaneously (Cloudflare, AWS CloudFront). An 800 Gbps botnet flood originating globally is automatically fractured and absorbed locally across 300 points of presence.
- **SYN Cookies**: The kernel responds to TCP SYN packets by encoding connection state inside the initial TCP sequence number, allocating zero server memory until the final ACK arrives.
- **DDoS Scrubbing Centers**: Traffic is diverted (by BGP announcement or DNS) through high-capacity centres that drop attack signatures and forward clean traffic to the origin over a tunnel or private link. Always-on scrubbing adds latency; on-demand scrubbing leaves a detection-and-diversion gap of minutes.
- **Edge Rate Limiting**: Per-IP, per-session, or per-API-key limits at the CDN/WAF for L7 floods, backed by bot detection and challenges, because volumetric filters cannot tell a valid-looking HTTP request from a real one.
- **Origin Protection**: None of this helps if the origin IP is reachable directly - lock origin ingress to the provider's ranges.

## Example

```bash
# Host-level protocol-attack hardening (Linux): SYN cookies and a larger half-open queue
sysctl -w net.ipv4.tcp_syncookies=1            # send cookies only when the SYN queue overflows
sysctl -w net.ipv4.tcp_max_syn_backlog=8192
sysctl -w net.ipv4.tcp_synack_retries=2        # give up on spoofed half-open connections sooner

# During an incident: is this a SYN flood? Count half-open connections.
ss -Hn state syn-recv | wc -l
nstat -az TcpExtSyncookiesSent TcpExtListenDrops
```

```nginx
# L7 rate limiting at the origin/edge proxy: 10 req/s per client IP, small burst, 429 on excess
limit_req_zone $binary_remote_addr zone=perip:10m rate=10r/s;
server {
  location /search {
    limit_req zone=perip burst=20 nodelay;
    limit_req_status 429;
  }
}
```

## Interview tips

- Classify first - volumetric, protocol, or application - because each is mitigated at a different place: volumetric by anycast capacity and upstream scrubbing, protocol by SYN cookies and stateless edges, application by rate limiting, caching, and bot management.
- Explain why anycast works: the same prefix is announced from many PoPs, so BGP delivers each bot's traffic to its nearest PoP and the flood is divided by the number of locations rather than concentrated on one.
- Name the gap in on-premises defence: you cannot filter a flood that has already saturated your uplink - volumetric mitigation must happen upstream (cloud provider, CDN, or ISP scrubbing).
- For L7, IP-based limits struggle against large residential botnets; key limits on session or API key, challenge suspicious clients, and make expensive endpoints authenticated or cached.
- Close with origin protection and graceful degradation: lock the origin to the edge, and shed load with 429s and circuit breakers rather than letting the database fall over.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot Docker networking between containers?]] (`#415`): [How do you troubleshoot Docker networking between containers?](../docker/how-do-you-troubleshoot-docker-networking-between-containers.md)
- [[What is progressive delivery and how does it differ from traditional deployment strategies?]] (`#509`): [What is progressive delivery and how does it differ from traditional deployment strategies?](../core-devops-concepts/what-is-progressive-delivery-and-how-does-it-differ-from-traditional-deployment-strategies.md)
- [[What is Shift-Left and how is it practically implemented across the SDLC?]] (`#510`): [What is Shift-Left and how is it practically implemented across the SDLC?](../core-devops-concepts/what-is-shift-left-and-how-is-it-practically-implemented-across-the-sdlc.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Network Security](./README.md) · [All topics](../README.md)
