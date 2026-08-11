---
title: "How do you debug a Linux performance problem from first principles?"
id: 295
category: "Linux Administration"
difficulty: "Advanced"
tags:
  - devops
  - linux-administration
  - interview-questions
---

# How do you debug a Linux performance problem from first principles?

**Short answer:** Work top-down through the four resources - **CPU, memory, disk, network** - narrowing from system-wide to per-process to per-syscall, and always compare against a known baseline. Start with the 60-second checklist (`uptime`, `dmesg`, `vmstat`, `mpstat`, `pidstat`, `iostat`, `free`, `sar`, `top`), form one hypothesis about which resource is saturated, then confirm it with a targeted tool (`strace`/`perf`/`bpftrace`) before changing anything. The discipline that matters is measuring utilisation _and saturation_, because a resource at 100% utilisation with no queue is fine while one at 60% with a deep queue is not.

## Detail

**The framework: USE - Utilisation, Saturation, Errors.** For every resource ask all three. CPU at 90% utilisation with a run queue of 1 is healthy; CPU at 70% with a run queue of 20 means processes are waiting. Disk at 40% utilisation with 200ms `await` means the queue is the problem, not the throughput. Errors (dropped packets, IO errors, OOM kills) are often the actual cause hiding behind a performance symptom.

**The 60-second triage, in order.** Each command answers one question:

| Command                | Question it answers                                                  |
| ---------------------- | -------------------------------------------------------------------- |
| `uptime`               | Load average trend - rising, falling, or steady?                     |
| `dmesg -T \| tail -40` | Did the kernel already tell you? OOM kills, IO errors, TCP drops     |
| `vmstat 1`             | Run queue (`r`), blocked (`b`), swap in/out (`si`/`so`), `wa`, steal |
| `mpstat -P ALL 1`      | Is one core pegged (single-threaded bottleneck) or all of them?      |
| `pidstat 1`            | Which process is actually consuming CPU, over time not instantly     |
| `iostat -xz 1`         | Per-device `%util`, `await`, queue depth - disk saturation           |
| `free -m`              | Available memory (not "free"), and whether swap is being used        |
| `sar -n DEV 1`         | Network throughput and, with `-n EDEV`, errors and drops             |
| `ss -s` / `ss -tan`    | Socket states - a pile of `TIME_WAIT` or a full accept queue         |
| `top` / `htop`         | The overall shape, last rather than first                            |

**Then narrow by resource.**

- **CPU.** Distinguish user time (your code), system time (syscalls - often IO or lock contention), `iowait` (blocked on disk, so the real problem is elsewhere), and `steal` (the hypervisor took your cycles - a noisy neighbour or a burstable instance out of credits). For user-time problems, `perf top` and a flame graph (`perf record -F 99 -a -g -- sleep 30` then `perf script | stackcollapse-perf.pl | flamegraph.pl`) tell you _which function_, which is where guessing usually ends.
- **Memory.** `free -m` and read **available**, not free - Linux uses spare RAM as page cache by design. The signals of real pressure are `si`/`so` in `vmstat`, a rising `pgscan`/`pgsteal` rate, and PSI (`/proc/pressure/memory`) which is the modern, direct measure. Then `dmesg | grep -i oom` for kills, and `smem` or `/proc/<pid>/status` for per-process RSS. In containers, check the cgroup: `memory.current` against `memory.max`, and `memory.events` for OOM counts - the host can look fine while a cgroup is being killed repeatedly.
- **Disk.** `iostat -xz 1`: `await` is the latency the application feels; `%util` on modern NVMe is misleading because the device is parallel. Find the culprit with `iotop -o` or `pidstat -d 1`, then `biolatency`/`biosnoop` from bcc for a latency histogram. Check the filesystem too - a full or nearly full filesystem, or exhausted inodes (`df -i`), produces symptoms that look nothing like "disk full".
- **Network.** `ss -s` for socket totals, `ss -tin` for per-connection retransmits and RTT, `nstat`/`netstat -s` for retransmits, listen-queue overflows, and drops. A full accept backlog (`ss -lnt` `Send-Q` at its limit) manifests as connection timeouts under load. `tcpdump` last, and only with a filter.
- **The process itself.** `strace -c -p <pid>` for a syscall count histogram (which syscall dominates, and which is returning errors); `strace -T` for per-call latency; `/proc/<pid>/stack` and `wchan` for where a blocked kernel thread is stuck. `bpftrace` when you need something bespoke and low-overhead - `strace` on a busy production process can slow it by an order of magnitude, which is a real trap.

**Rules that keep this honest.** Compare to a baseline - "high" is meaningless without yesterday's number, so `sar` historical data is worth having enabled everywhere. Change one thing at a time and re-measure. Do not tune sysctls from a blog post; find the saturated resource first. Check the boring causes early: a full disk, a cron job, log rotation, a runaway retry loop, an expired certificate causing retries, a `ulimit` on file descriptors. And remember `iowait` and `steal` both mean "the problem is not the CPU" - one points at storage, the other at the hypervisor or your instance's credit balance.

## Example

```bash
# 60-second triage. Run it in this order, every time.
uptime                              # load trend
dmesg -T | tail -40                 # OOM, IO errors, TCP drops - free answers
vmstat 1 5                          # r, b, si/so, wa, st
mpstat -P ALL 1 3                   # one hot core vs all cores
pidstat -u -r -d 1 3                # per-process cpu / mem / io over time
iostat -xz 1 3                      # await and queue depth per device
free -m                             # 'available' is the number that matters
sar -n DEV 1 3; sar -n EDEV 1 3     # throughput, then errors and drops
ss -s                               # socket summary; TIME_WAIT / accept queue
```

```bash
# Narrow to a cause once you have a hypothesis.
# CPU-bound in user code: which function?
perf record -F 99 -a -g -- sleep 30 && perf report --stdio | head -40

# Blocked, not busy: what syscall, and how long?
strace -c -p 4242              # syscall histogram + error counts (careful in prod)
strace -T -e trace=file -p 4242
cat /proc/4242/wchan; cat /proc/4242/stack

# Container memory: the host is fine, the cgroup is not.
cg=$(cat /proc/4242/cgroup | cut -d: -f3)
cat /sys/fs/cgroup$cg/memory.current /sys/fs/cgroup$cg/memory.max
cat /sys/fs/cgroup$cg/memory.events        # oom_kill count
cat /proc/pressure/{cpu,memory,io}         # PSI - direct saturation signal

# Disk latency distribution rather than an average.
biolatency-bpfcc 10 1
biosnoop-bpfcc | head -30

# Network: retransmits, drops, and a full listen backlog.
nstat -az | grep -Ei 'retrans|listendrop|listenoverflow'
ss -lnt                                     # Send-Q at its limit = backlog full
ss -tin state established | grep -A1 retrans | head

# The boring causes, checked early rather than late.
df -h; df -i                                # space and inodes
journalctl --since '30 min ago' -p warning
systemctl list-units --state=failed
```

```bash
# Baseline: you cannot call a number high without yesterday's number.
sar -u -f /var/log/sysstat/sa$(date -d yesterday +%d) | tail -20
sar -q -s 09:00:00 -e 10:00:00              # run queue during last week's incident
```

## Interview tips

- Lead with the USE method and the utilisation-versus-saturation distinction. It is the framing that turns a tool list into a method.
- Recite a version of the 60-second checklist with the question each command answers. Naming tools without their purpose reads as memorisation.
- Explain `iowait` and `steal` correctly - both mean the CPU is not the bottleneck. Misreading `iowait` as CPU load is the most common error in this question.
- Say "available, not free" for memory and mention PSI. Both date your knowledge to modern kernels.
- Know that `strace` has heavy overhead on a busy process, and that `perf`/`bpftrace` are the production-safe alternatives. This is a genuine hands-on marker.
- Include the container angle - cgroup `memory.max` and `memory.events` - because most production Linux debugging now happens inside one.
- Insist on a baseline and on changing one variable at a time. Then tell a real story where the cause was boring: a full disk, a cron job, or a retry loop.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you patch hundreds of servers safely?]] (`#430`): [How do you patch hundreds of servers safely?](../configuration-management/how-do-you-patch-hundreds-of-servers-safely.md)
- [[What Bash scripting exercises come up in DevOps interviews?]] (`#502`): [What Bash scripting exercises come up in DevOps interviews?](../scripting-and-automation/what-bash-scripting-exercises-come-up-in-devops-interviews.md)
- [[How do you write a production-grade Bash script?]] (`#266`): [How do you write a production-grade Bash script?](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
