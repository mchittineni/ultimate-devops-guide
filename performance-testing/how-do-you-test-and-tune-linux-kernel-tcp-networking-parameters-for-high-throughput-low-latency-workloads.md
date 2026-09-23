---
title: "How do you test and tune Linux kernel TCP networking parameters for high-throughput, low-latency workloads?"
id: 612
category: "Performance Testing"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - performance-testing
  - linux
  - kernel
  - sysctl
  - tcp
  - tuning
quiz:
  stem: "Which Linux kernel setting allows a high-throughput reverse proxy (like NGINX or Envoy) to safely reuse outgoing client TCP connections stuck in TIME_WAIT state?"
  options:
    - "`net.ipv4.tcp_tw_reuse = 1`"
    - "`net.ipv4.icmp_echo_ignore_all = 1`"
    - "`vm.swappiness = 0`"
    - "`fs.file-max = 1000`"
  answer: 1
  explanation: "`net.ipv4.tcp_tw_reuse = 1` allows the kernel to safely reallocate outgoing TCP sockets residing in TIME_WAIT state if timestamps show the old connection is terminated, preventing ephemeral port exhaustion."
---

# How do you test and tune Linux kernel TCP networking parameters for high-throughput, low-latency workloads?

**Short answer:** Tuning Linux networking for high throughput involves adjusting `sysctl` parameters to enlarge socket read/write buffers, expand connection listen backlogs (`somaxconn`), reuse TIME_WAIT sockets (`tcp_tw_reuse`), and adopt modern BBR congestion control.

## Detail

Default Linux kernel network parameters are conservative general-purpose values, not tuned for multi-gigabit cloud services handling 100,000 concurrent sockets. Modern kernels have raised several of them (for example `somaxconn` defaults to 4096 since kernel 5.4), so **measure first and change one thing at a time** - check `ss -s`, `nstat -az | grep -i -E 'listen|drop|retrans'`, and `ss -ltn` (the `Send-Q` of a listening socket is its backlog) before and after each change:

### Key `sysctl` Parameters (in a file under `/etc/sysctl.d/`)

```ini
# Enlarge listen backlog for high connection bursts
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535

# Enlarge maximum socket receive/send buffers (up to 16MB)
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216

# Allow reuse of TIME_WAIT sockets for OUTGOING connections (default 2 = loopback only).
# Never look for tcp_tw_recycle: it broke clients behind NAT and was removed in kernel 4.12.
net.ipv4.tcp_tw_reuse = 1

# Enlarge ephemeral outgoing port range, keeping clear of ports your services listen on
net.ipv4.ip_local_port_range = 10000 65535

# Enable Google BBR congestion control over legacy Cubic
net.core.default_qdisc = fq
net.ipv4.tcp_congestion_control = bbr
```

### Why BBR Congestion Control?

Cubic (the Linux default) treats packet loss as congestion, throttling throughput even when loss is random rather than caused by a full queue. BBR models the bottleneck bandwidth and round-trip time directly, which can give dramatically higher throughput on long-distance, lossy links and keeps queues shorter. The trade-off: BBRv1 (the version in mainline kernels) can take an unfair share of bandwidth from Cubic flows, and on low-latency, low-loss data-centre links the gain is often small - so it is a per-workload decision to validate, not a blanket default.

**Buffer sizes are about the bandwidth-delay product.** A 10 Gbit/s link with 50 ms RTT needs about 62 MB in flight to fill the pipe; a 16 MB maximum caps a single flow well below that. Inside one region (sub-millisecond RTT) the defaults are usually already enough, and oversized buffers just waste memory.

## Example

Apply a change, then prove it with a repeatable test rather than trusting the sysctl:

```bash
sudo tee /etc/sysctl.d/90-net-tuning.conf >/dev/null <<'EOF'
net.core.default_qdisc = fq
net.ipv4.tcp_congestion_control = bbr
EOF
sudo sysctl --system
sysctl net.ipv4.tcp_congestion_control        # verify it took effect

# Baseline vs tuned throughput and retransmits between two hosts
iperf3 -s                                      # on the server
iperf3 -c 10.0.2.15 -t 30 -P 4                 # on the client: 4 parallel streams, 30 s
ss -ti dst 10.0.2.15 | grep -E 'bbr|cubic|rtt|retrans'   # per-socket cwnd, RTT, retransmits

# Watch for listen-queue overflows under load (should stay at 0)
nstat -az TcpExtListenOverflows TcpExtListenDrops
```

## Interview tips

- Expanding `somaxconn` and `tcp_max_syn_backlog` to prevent connection drops during SYN bursts.
- Enlarging TCP window read/write buffers (`tcp_rmem`, `tcp_wmem`).
- `tcp_tw_reuse` and expanding `ip_local_port_range` to prevent port exhaustion on proxies.
- BBR congestion control for better throughput over lossy, high-latency links - and awareness of its fairness trade-off.
- Say you measure before tuning: listen overflows, retransmits, and ephemeral-port exhaustion each show up in `nstat`/`ss`, and each points at a different knob.
- In Kubernetes, most `net.*` sysctls are per network namespace, so they are set per pod (`securityContext.sysctls`, with unsafe ones allowed on the kubelet) rather than only on the node.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are Linux cgroups v2 and how do they improve container resource isolation over cgroups v1?]] (`#514`): [What are Linux cgroups v2 and how do they improve container resource isolation over cgroups v1?](../docker/what-are-linux-cgroups-v2-and-how-do-they-improve-container-resource-isolation-over-cgroups-v1.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Performance Testing](./README.md) · [All topics](../README.md)
