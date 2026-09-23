---
title: "What is BGP routing and how do BGP Hijacking attacks redirect enterprise internet traffic?"
id: 673
category: "Network Security"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - network-security
  - bgp
  - networking
  - rpki
  - routing
quiz:
  stem: "Which routing rule allows an attacker executing a BGP Hijack to divert traffic away from a legitimate cloud provider?"
  options:
    - "BGP prefers routes with the lowest alphabetical domain name"
    - "The Longest Prefix Match rule: routers automatically prefer the more specific IP prefix announcement (e.g. `/24` over `/16`)"
    - "Routers always route traffic to the newest server on the internet"
    - "BGP routes packets based on server CPU load"
  answer: 2
  explanation: "BGP algorithms prioritize specificity. By announcing a `/24` subnet inside an authorized organization's `/16` block, global core routers route traffic to the more specific `/24` path."
---

# What is BGP routing and how do BGP Hijacking attacks redirect enterprise internet traffic?

**Short answer:** Border Gateway Protocol (BGP) is the routing protocol of the internet that exchanges IP prefix reachability between Autonomous Systems (AS); BGP hijacking occurs when a malicious or misconfigured network announces unauthorized IP prefixes, tricking routers into sending traffic to the attacker.

## Detail

The internet is a collection of independent Autonomous Systems (ISPs, universities, cloud providers).

### How BGP Works

Routers advertise which IP blocks (CIDR prefixes) they can reach, along with the AS path. Route selection prefers the **most specific prefix** (longest-prefix match), then policy and path attributes such as local preference and AS-path length. BGP has no built-in way to check that the announcing AS actually holds the prefix - neighbours trust each other.

- If Cloudflare advertises `104.16.0.0/12` (covers a broad range).
- An attacker announces `104.16.0.0/24` (a much more specific sub-range).
- Routers that accept the `/24` send traffic for that block to the attacker. Most networks reject IPv4 announcements more specific than `/24`, so a victim already announcing `/24`s can only be hijacked with an equal-length route, which wins only where the attacker's path looks shorter or more preferred.

### Real-World Incidents

- **2008, Pakistan Telecom / YouTube**: a more-specific announcement intended for a domestic block leaked globally and took YouTube offline for about two hours.
- **2018, Amazon Route 53 / MyEtherWallet**: attackers announced more-specifics of Route 53 address space through a small ISP, answered DNS for `myetherwallet.com` with a phishing server, and stole cryptocurrency.
- **Route leaks** (not malicious, same effect): a network re-announces routes learned from one provider to another, pulling traffic through a path that cannot carry it - as in the 2019 incident that degraded Cloudflare and others.

### Defense Mechanism: RPKI (Resource Public Key Infrastructure)

- Cryptographic certificate system where Regional Internet Registries (RIRs) issue Route Origin Authorizations (ROAs).
- Routers performing **Route Origin Validation (ROV)** mark an announcement valid, invalid, or not-found against the ROAs, and drop invalids. Major transit providers and clouds now do this, which has made origin hijacks of ROA-covered prefixes far less effective.
- **Limitation**: ROV validates only the _origin_ AS. An attacker who forges the path with the legitimate origin at the end passes the check. **ASPA** (Autonomous System Provider Authorization, still being standardised and deployed) and BGPsec address path validation.
- **Operational controls**: publish ROAs with a correct `maxLength`, filter customer announcements (MANRS practices), and monitor your prefixes for unexpected announcements (for example with public BGP monitoring such as Cloudflare Radar or RIPE RIS-based alerting).

## Example

```bash
# Check the RPKI status of an origin/prefix pair (RIPEstat public API)
curl -s "https://stat.ripe.net/data/rpki-validation/data.json?resource=AS13335&prefix=1.1.1.0/24" \
  | jq '.data.status'
#   "valid"   -> a ROA authorises AS13335 to originate 1.1.1.0/24

# Who is announcing a prefix right now, and from which origin AS?
curl -s "https://stat.ripe.net/data/routing-status/data.json?resource=1.1.1.0/24" \
  | jq '.data.announced_space, .data.visibility.v4'
```

```text
# Publishing a ROA (done in the RIR portal or via a hosted RPKI service):
Prefix: 203.0.113.0/24   Origin AS: 64500   maxLength: 24
# maxLength = the prefix length itself, so a forged /25 more-specific is RPKI-invalid
```

## Interview tips

- Start with the trust model: BGP accepts announcements from neighbours without proof of ownership, and routers prefer the most specific prefix - so a false more-specific announcement pulls traffic away globally.
- Separate **hijacks** (wrong origin, malicious or fat-fingered) from **route leaks** (valid routes propagated where they should not be); both redirect traffic, and they need different defences.
- RPKI + ROV is the deployed fix for origin hijacks; set `maxLength` tightly, because a loose ROA lets an attacker announce a more-specific with your origin AS forged in the path.
- Know the limitation: ROV does not validate the path, so path forgery and many leaks still work; ASPA and BGPsec target that, with ASPA the more deployable of the two.
- For an enterprise, the practical answers are: ROAs for your prefixes, providers that enforce ROV, monitoring and alerting on your prefixes, and TLS everywhere so a hijack yields a certificate error rather than readable traffic.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot Docker networking between containers?]] (`#415`): [How do you troubleshoot Docker networking between containers?](../docker/how-do-you-troubleshoot-docker-networking-between-containers.md)
- [[How do Docker bridge, host, and macvlan network drivers differ in packet routing and isolation?]] (`#517`): [How do Docker bridge, host, and macvlan network drivers differ in packet routing and isolation?](../docker/how-do-docker-bridge-host-and-macvlan-network-drivers-differ-in-packet-routing-and-isolation.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Network Security](./README.md) · [All topics](../README.md)
