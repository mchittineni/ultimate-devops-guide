---
title: "What is the difference between iptables, nftables, firewalld, and ufw?"
id: 779
category: "Linux Administration"
difficulty: "Intermediate"
tags:
  - devops
  - linux-administration
  - interview-questions
  - network-security
quiz:
  stem: "On a current RHEL, Debian, or Ubuntu host, what usually happens when you run an `iptables` command?"
  options:
    - "It programs the legacy x_tables kernel backend directly, bypassing nftables"
    - "It is the iptables-nft compatibility layer, which translates the rule into nftables objects in the kernel"
    - "It fails, because iptables has been removed from the kernel"
    - "It edits firewalld's XML zone files"
  answer: 2
  explanation: "Modern distributions ship iptables-nft: the familiar iptables syntax, translated into nftables rules. Mixing it with iptables-legacy, or hand-written nft tables, is what produces rules that seem to be ignored."
---

# What is the difference between iptables, nftables, firewalld, and ufw?

**Short answer:** They sit at two different layers. **Netfilter** is the packet-filtering framework inside the kernel. **iptables** and **nftables** are the two rule languages and kernel interfaces for it: iptables is the older one, with separate tools per family (`iptables`, `ip6tables`, `arptables`, `ebtables`) and rules evaluated as linear lists; **nftables** (`nft`) replaced it with one tool and one table model for IPv4, IPv6, ARP, and bridging, native **sets and maps** so a thousand addresses are one lookup instead of a thousand rules, and atomic replacement of the whole ruleset. **firewalld** (RHEL, Fedora, SUSE) and **ufw** (Ubuntu) are **front-ends** that generate those rules from a simpler model - firewalld with zones and services managed over D-Bus, ufw with a minimal allow/deny syntax. On current distributions the `iptables` command is usually **iptables-nft**, a compatibility layer writing nftables rules, and firewalld uses the nftables backend by default. The operational rule: pick **one** manager per host, because two tools writing rules (or Docker and Kubernetes adding their own) is the usual cause of "my rule is there but traffic is still blocked".

## Detail

### The layers

```text
 ufw / firewalld / Docker / kube-proxy / Cilium      <- managers that generate rules
        │
 iptables-nft (compat syntax)  │  nft (native)       <- rule languages / userspace tools
        │                      │
 nf_tables kernel subsystem  (or legacy x_tables)    <- netfilter in the kernel
        │
 hooks: prerouting -> input / forward -> output -> postrouting
```

Packets traverse hooks; tables attach chains to those hooks; chains hold rules evaluated in order until one gives a verdict (`accept`, `drop`, `reject`, `jump`). Connection tracking (`ct state established,related accept`) is what makes a stateful firewall short: allow replies once, then only list new connections you want.

### iptables versus nftables

|                      | iptables                                                        | nftables                                                      |
| -------------------- | --------------------------------------------------------------- | ------------------------------------------------------------- |
| Tools                | `iptables`, `ip6tables`, `ebtables`, `arptables`                | One `nft` command; `inet` family covers IPv4 and IPv6         |
| Tables and chains    | Fixed built-ins (`filter`, `nat`, `mangle`)                     | You create only the tables and chains you need                |
| Matching many values | One rule per address/port, or the ipset add-on                  | Native sets, maps, and verdict maps - O(1) lookups            |
| Updates              | Rule-by-rule; full reload rewrites everything                   | Atomic: `nft -f file` replaces the ruleset in one transaction |
| Status               | Legacy backend in maintenance; syntax lives on via iptables-nft | Default backend since RHEL 8, Debian 10, Ubuntu 21.10         |

The performance difference matters at scale: kube-proxy's iptables mode walks long rule chains per Service, which is why Kubernetes added an **nftables mode** for kube-proxy (GA in 1.33) and why eBPF data planes (Cilium) bypass netfilter for Service routing altogether.

### iptables-nft versus iptables-legacy

`iptables -V` prints `(nf_tables)` or `(legacy)`. Both can be installed, and rules written by one are **invisible** to the other's listing commands while both still apply in the kernel. A host where Docker uses one backend and an administrator uses the other is a classic source of phantom drops. Check with `iptables-legacy-save` and `nft list ruleset` and standardise on nftables.

### firewalld

- **Zones** (`public`, `internal`, `trusted`, `drop`) carry a policy; interfaces and source CIDRs are assigned to a zone.
- **Services** (`ssh`, `https`) are named port sets, so rules read as intent.
- **Runtime versus permanent**: `firewall-cmd --add-service=https` changes only the running state; add `--permanent` and `--reload` (or `--runtime-to-permanent`) or the change disappears at reboot - the most common firewalld mistake.
- It owns its own nftables tables, so hand-written `nft` rules in a separate table coexist, but direct edits to firewalld's tables are overwritten.

### ufw

Ubuntu's front-end: `ufw allow 22/tcp`, `ufw default deny incoming`, `ufw enable`. Simple and good for single hosts. Two traps: **enable it over SSH only after allowing SSH**, and Docker-published ports (`-p 8080:80`) are DNAT'd in the `nat` table and forwarded before ufw's `INPUT` rules see them, so a container port is reachable even when `ufw status` says it is denied. The fix is binding to `127.0.0.1`, using the `DOCKER-USER` chain, or not publishing the port.

### In the cloud

Security groups, NSGs, and VPC firewall rules filter before the packet reaches the instance and are managed as code, so many fleets keep the host firewall minimal or default-deny with only SSH/agent ports. Defence in depth argues for both; what matters is that each layer has a clear owner and the host rules are configuration-managed, not hand-edited.

## Example

```bash
# Which backend am I actually on?
iptables -V                         # iptables v1.8.x (nf_tables)
nft list ruleset | head -50         # the real, complete state in the kernel
```

```bash
# A minimal stateful host firewall in native nftables (atomic load)
cat > /etc/nftables.conf <<'EOF'
#!/usr/sbin/nft -f
flush ruleset

table inet filter {
  set admin_nets {
    type ipv4_addr; flags interval
    elements = { 10.0.0.0/8, 192.168.10.0/24 }
  }

  chain input {
    type filter hook input priority 0; policy drop;
    ct state established,related accept
    ct state invalid drop
    iif lo accept
    ip protocol icmp accept
    meta l4proto ipv6-icmp accept
    tcp dport 22 ip saddr @admin_nets accept      # SSH only from admin networks
    tcp dport { 80, 443 } accept
    counter log prefix "nft-drop: " limit rate 5/minute
  }
  chain forward { type filter hook forward priority 0; policy drop; }
  chain output  { type filter hook output priority 0; policy accept; }
}
EOF
nft -c -f /etc/nftables.conf        # syntax check without applying
nft -f /etc/nftables.conf           # apply atomically
systemctl enable --now nftables
```

```bash
# firewalld: runtime vs permanent
firewall-cmd --get-active-zones
firewall-cmd --zone=public --add-service=https --permanent
firewall-cmd --zone=public --add-rich-rule='rule family=ipv4 source address=10.0.0.0/8 service name=ssh accept' --permanent
firewall-cmd --reload && firewall-cmd --list-all

# ufw: allow SSH BEFORE enabling, or you lock yourself out
ufw allow OpenSSH
ufw default deny incoming && ufw default allow outgoing
ufw enable && ufw status verbose

# Translate an old iptables rule to nftables syntax
iptables-translate -A INPUT -p tcp --dport 443 -j ACCEPT
# nft 'add rule ip filter INPUT tcp dport 443 counter accept'
```

## Interview tips

- Separate the layers first: netfilter is the kernel framework, iptables and nftables are the rule interfaces, firewalld and ufw are managers that generate rules. Most confused answers mix these up.
- Give nftables' concrete advantages - one tool for IPv4/IPv6, native sets and maps, atomic ruleset replacement - and say it has been the default backend on the major distributions for years.
- Mention iptables-nft versus iptables-legacy and that mixing them produces rules you cannot see in one tool's listing. It is the detail that shows real debugging time.
- For firewalld, name zones, services, and the runtime-versus-`--permanent` trap; for ufw, allow SSH before enabling and the Docker published-port bypass.
- Connect it to Kubernetes: kube-proxy's iptables mode scales poorly with many Services, hence the nftables mode and eBPF alternatives. See [the difference between TCP and UDP and diagnosing packet loss](./what-is-the-difference-between-tcp-and-udp-and-how-do-you-diagnose-packet-loss-and-latency-with-ss-ip-and-tcpdump.md) and [how Docker network drivers route packets](../docker/how-do-docker-bridge-host-and-macvlan-network-drivers-differ-in-packet-routing-and-isolation.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What Bash scripting exercises come up in DevOps interviews?]] (`#502`): [What Bash scripting exercises come up in DevOps interviews?](../scripting-and-automation/what-bash-scripting-exercises-come-up-in-devops-interviews.md)
- [[How do you patch hundreds of servers safely?]] (`#430`): [How do you patch hundreds of servers safely?](../configuration-management/how-do-you-patch-hundreds-of-servers-safely.md)
- [[When do you use Bash and when do you use Python?]] (`#301`): [When do you use Bash and when do you use Python?](../scripting-and-automation/when-do-you-use-bash-and-when-do-you-use-python.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
