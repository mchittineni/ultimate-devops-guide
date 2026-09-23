---
title: "What is the difference between TCP and UDP and how do you diagnose packet loss and latency with ss, ip, and tcpdump?"
id: 576
category: "Linux Administration"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - linux
  - networking
  - tcp
  - udp
  - tcpdump
quiz:
  stem: "When inspecting a listening TCP port with `ss -lnt`, what does a high non-zero value in the `Recv-Q` column indicate?"
  options:
    - "The network cable has been physically disconnected"
    - "The application has failed to call `accept()` quickly enough, and the TCP backlog queue is filling up"
    - "The remote client has disconnected cleanly"
    - "The server has run out of available hard drive storage"
  answer: 2
  explanation: "For listening sockets, `Recv-Q` represents the number of established TCP connections waiting in the socket backlog queue to be accepted by the application process."
---

# What is the difference between TCP and UDP and how do you diagnose packet loss and latency with ss, ip, and tcpdump?

**Short answer:** TCP is a connection-oriented, reliable protocol with handshakes, sequencing, and congestion control; UDP is connectionless and lightweight without retransmissions; network issues are diagnosed using `ip` (interfaces/routing), `ss` (socket buffers/state), and `tcpdump` (packet capture).

## Detail

Modern Linux network engineering requires using contemporary tools rather than obsolete commands (`netstat`, `ifconfig`, `route` are deprecated in favor of `iproute2`):

### Diagnostic Toolchain

1. **`ip route` & `ip addr`**: Verify interface IPs, subnets, and default gateway routes.
2. **`ss` (Socket Statistics)**: Inspect socket buffers and TCP connection states:

   ```bash
   # Listening TCP and UDP sockets, numeric, with the owning process:
   ss -tulpn
   # Per-connection internals: RTT, congestion window, retransmits, and timers:
   ss -tino state established
   # On a LISTEN socket, Recv-Q = connections waiting to be accepted, Send-Q = the backlog limit.
   # Recv-Q near Send-Q means the app is not calling accept() fast enough:
   ss -lnt '( sport = :80 )'
   ```

3. **`tcpdump`**: Deep packet inspection:

   ```bash
   # Capture TCP SYN/RST packets on port 443 to diagnose handshake failures:
   tcpdump -nn -i eth0 'tcp port 443 and (tcp[tcpflags] & (tcp-syn|tcp-rst) != 0)'
   ```

4. **`mtr` / `traceroute -T`**: Diagnose intermediate hops dropping packets or adding latency; `mtr --tcp --port 443` (or `traceroute -T -p 443`) probes with TCP where ICMP is filtered. Loss shown only at an intermediate hop is often ICMP rate limiting on that router - real loss persists to the final hop.
5. **Counters**: `ip -s link` (interface drops and errors), `nstat -az | grep -i retrans` (system-wide retransmissions), and `ss -ti` per connection. Retransmissions are how TCP loss shows up; for UDP there is no retransmit, so look at `nstat` `UdpRcvbufErrors` / `UdpInErrors` for receive-buffer overflows.

## Example

```bash
# 1. Path and interface: are we even using the route and NIC we think?
ip route get 10.20.1.10
ip -s link show eth0                          # RX/TX errors and drops on the interface

# 2. Loss and latency per hop, using TCP where ICMP is filtered
mtr --tcp --port 443 -rwc 50 api.example.com

# 3. Sockets: retransmits and RTT on live connections to the database
ss -tin state established '( dport = :5432 )'   # look at rtt:, retrans:, cwnd:
nstat -az | grep -Ei 'TcpRetransSegs|TcpExtTCPLostRetransmit|UdpRcvbufErrors'

# 4. Packets: capture only what you need, to a file, then analyse
sudo tcpdump -nn -i eth0 -c 2000 -w /tmp/db.pcap 'host 10.20.1.10 and tcp port 5432'
tcpdump -nn -r /tmp/db.pcap 'tcp[tcpflags] & tcp-rst != 0' | head   # who is resetting?
```

## Interview tips

- Contrast them on mechanism: TCP gives a reliable, ordered byte stream (handshake, sequence numbers, ACKs, retransmission, flow and congestion control); UDP gives independent datagrams with no delivery guarantee, so loss handling moves into the application (or into QUIC, which rebuilds reliability over UDP).
- Say how loss shows up differently: in TCP as retransmissions and rising latency (visible in `ss -ti` and `nstat`), in UDP as silently missing data or receive-buffer overflow counters.
- Work in layers - route and interface (`ip`), socket state and counters (`ss`, `nstat`), then packets (`tcpdump`) - and always filter captures by host and port and write them to a file for Wireshark.
- Read `ss` queues correctly: on listening sockets `Recv-Q` is the accept queue and `Send-Q` its limit; on established sockets they are unread and unacknowledged bytes.
- Know the traceroute trap: loss at one intermediate hop but not the destination is usually ICMP rate limiting, not real loss.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you write a production-grade Bash script?]] (`#266`): [How do you write a production-grade Bash script?](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md)
- [[What do you use Python for as a DevOps engineer?]] (`#267`): [What do you use Python for as a DevOps engineer?](../scripting-and-automation/what-do-you-use-python-for-as-a-devops-engineer.md)
- [[When do you use Bash and when do you use Python?]] (`#301`): [When do you use Bash and when do you use Python?](../scripting-and-automation/when-do-you-use-bash-and-when-do-you-use-python.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
