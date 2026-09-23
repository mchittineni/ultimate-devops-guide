---
title: "What are WireGuard and modern VPN protocols and how do they replace legacy IPsec and OpenVPN?"
id: 674
category: "Network Security"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - network-security
  - wireguard
  - vpn
  - cryptography
  - linux-kernel
quiz:
  stem: "Why does WireGuard achieve significantly higher network throughput and lower latency than OpenVPN?"
  options:
    - "WireGuard does not encrypt network traffic"
    - "WireGuard runs directly inside the Linux kernel using modern stream ciphers (ChaCha20), eliminating the userspace-to-kernel context switching overhead of OpenVPN"
    - "OpenVPN only functions on satellite connections"
    - "WireGuard compresses all packets with gzip"
  answer: 2
  explanation: "OpenVPN operates in userspace using `tun/tap` devices, copying packets between kernel and user memory. WireGuard runs in-kernel with optimized stream ciphers, delivering near line-rate speeds."
---

# What are WireGuard and modern VPN protocols and how do they replace legacy IPsec and OpenVPN?

**Short answer:** WireGuard is a lean VPN protocol, in the mainline Linux kernel since 5.6, that replaces the negotiation-heavy designs of IPsec and OpenVPN with a fixed modern cryptographic suite (Noise framework, Curve25519, ChaCha20-Poly1305), roughly 4,000 lines of auditable kernel code, and seamless roaming. The trade-off is that it is deliberately minimal: no cipher agility, no FIPS-validated mode, and no built-in user authentication or address management, which is why products such as Tailscale layer a control plane on top.

## Detail

Legacy VPN stacks are not insecure when configured well, but they are complex, and complexity is where misconfigurations and bugs live:

- **OpenVPN**: TLS-based, traditionally in userspace, so every packet crosses the kernel/userspace boundary; large codebase and many options. OpenVPN 2.6's Data Channel Offload (DCO) kernel module narrows the performance gap.
- **IPsec (IKEv2)**: The standards-based choice, supported by every firewall and cloud VPN gateway (AWS Site-to-Site VPN, Azure VPN Gateway), but with a large negotiation surface of cipher suites and modes. IKEv1 and weak groups should be disabled.

### The WireGuard Revolution

1. **Tiny Codebase (~4,000 Lines)**: Lives inside the Linux kernel (`drivers/net/wireguard`), with implementations for Windows, macOS, BSDs, and a userspace Go version. Small enough to audit and formally verify its protocol, with minimal attack surface.
2. **Cryptographic Opinionated**: No cipher negotiation! Uses fixed modern cryptography:
   - Curve25519 (ECDH key exchange)
   - ChaCha20 (symmetric encryption)
   - Poly1305 (authentication tag)
   - BLAKE2s (hashing)
3. **Connectionless & Roaming**: Operates over UDP and identifies peers by public key, not source address. If a user switches from office Wi-Fi to mobile 5G, the tunnel follows the new endpoint without the session dropping. Keys are re-exchanged automatically every couple of minutes for forward secrecy.
4. **Silent by Default**: Does not respond to unauthenticated packets; port scanners see a closed port, preventing reconnaissance.

### Limitations

- **No cipher agility**: if a primitive is ever broken, the fix is a new protocol version, not a config change - and the fixed suite is not FIPS 140-validated, which rules it out in some regulated environments (IPsec remains the default there).
- **Static configuration**: peers, keys, and `AllowedIPs` are configured by hand; there is no user login, MFA, or dynamic IP assignment. Mesh VPNs (Tailscale, NetBird, Netmaker) add an identity-aware control plane and NAT traversal on top of WireGuard.
- **UDP only**: networks that block UDP need a fallback (a relay or a TCP/TLS-based VPN).

## Example

```bash
# Generate a key pair on each peer
wg genkey | tee privatekey | wg pubkey > publickey
```

```ini
# /etc/wireguard/wg0.conf on the gateway
[Interface]
Address    = 10.100.0.1/24
ListenPort = 51820
PrivateKey = <gateway-private-key>

[Peer]
# laptop: only this key may use this tunnel address (cryptokey routing)
PublicKey  = <laptop-public-key>
AllowedIPs = 10.100.0.2/32
```

```bash
wg-quick up wg0     # bring the interface up
wg show             # peers, latest handshake, bytes transferred
```

## Interview tips

- Explain **cryptokey routing**: `AllowedIPs` is both the routing table (what to send to a peer) and the access list (what source addresses to accept from it), tying each tunnel IP to a public key.
- Give the design reasons for its speed and security: in-kernel data path, one fixed modern suite (no negotiation or downgrade attacks), a 1-RTT handshake from the Noise framework, and silence towards unauthenticated packets.
- Be balanced: IPsec/IKEv2 remains the interoperable standard for site-to-site links with cloud gateways and firewalls, and is the usual choice where FIPS-validated cryptography is required.
- Know what WireGuard leaves out - user authentication, key distribution, dynamic addressing - and that mesh products (Tailscale, NetBird) or a zero-trust access proxy supply it.
- Mention the privacy trade-off: the server keeps each peer's last endpoint IP in memory, which some commercial VPNs work around with extra tooling.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What happens under the hood when a container experiences an Out Of Memory (OOM) kill?]] (`#516`): [What happens under the hood when a container experiences an Out Of Memory (OOM) kill?](../docker/what-happens-under-the-hood-when-a-container-experiences-an-out-of-memory-oom-kill.md)
- [[How do you troubleshoot Docker networking between containers?]] (`#415`): [How do you troubleshoot Docker networking between containers?](../docker/how-do-you-troubleshoot-docker-networking-between-containers.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Network Security](./README.md) · [All topics](../README.md)
