---
title: "How do you inspect and manage Linux processes, signals, and resource limits?"
id: 498
category: "Linux Administration"
difficulty: "Intermediate"
tags:
  - devops
  - linux-administration
  - interview-questions
  - incident-management
---

# How do you inspect and manage Linux processes, signals, and resource limits?

**Short answer:** Every process has a **PID**, a parent, an owner, and a **state** - `R` running, `S` interruptible sleep (the normal idle state, waiting on I/O or an event), `D` **uninterruptible sleep** (blocked in the kernel, usually on disk or NFS - it cannot be killed and it counts towards load average), `T` stopped, `Z` **zombie** (finished, but its parent has not reaped the exit status). You inspect with `ps`, `top`/`htop`, `pgrep`, and `/proc/<pid>/`, and you signal with `kill`. The distinction interviewers test: `kill` sends **SIGTERM (15)** by default, which asks a process to shut down gracefully and can be handled; `kill -9` sends **SIGKILL**, which the process cannot catch, block, or ignore because the kernel destroys it - so it loses in-flight work, leaves temporary files and locks behind, and cannot flush buffers. Always try SIGTERM first and reserve SIGKILL for something that has genuinely stopped responding. Limits are per-process and set with `ulimit` (interactively), `/etc/security/limits.conf` or a systemd unit's `LimitNOFILE=` (persistently), and cgroups (which is what containers use) - and the specific one you will meet is **"Too many open files"**, which is the `nofile` limit, not a disk problem.

## Detail

### Process states, and why `D` and `Z` matter

| State     | Meaning                                                       | What to do                                                                                                                                             |
| --------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `R`       | Running or runnable                                           | Normal                                                                                                                                                 |
| `S`       | Interruptible sleep - waiting on I/O, a timer, a socket       | Normal; most processes sit here                                                                                                                        |
| `D`       | **Uninterruptible sleep** - blocked in a kernel call          | **Cannot be killed, not even with -9.** Investigate the storage: `dmesg`, a hung NFS mount, a failing disk. Contributes to load average even at 0% CPU |
| `T` / `t` | Stopped (SIGSTOP / by a debugger)                             | `kill -CONT` to resume                                                                                                                                 |
| `Z`       | **Zombie** - exited, exit status not yet reaped by the parent | You cannot kill a zombie; it is already dead. Fix or restart the **parent**                                                                            |
| `I`       | Idle kernel thread                                            | Ignore                                                                                                                                                 |

**A zombie** is a process that has terminated but whose entry remains in the table because its parent has not called `wait()`. It consumes a PID and nothing else. A handful is harmless and transient; thousands means a buggy parent that is not reaping children, and the fix is restarting the parent (at which point `init`/`systemd` adopts and reaps the orphans). In containers this is the **PID 1 problem**: an application running as PID 1 that does not reap adopted children accumulates zombies, which is why `docker run --init` (or `tini`) exists.

**`D` state** is the more operationally important one. Uninterruptible sleep means the process is in the middle of a kernel operation that cannot be interrupted - almost always I/O. High load average with low CPU utilisation is the signature: load counts runnable **and** uninterruptible processes, so a stuck NFS mount or a failing disk produces a load of 30 on an idle box. That is also the answer to "load average is high but CPU is fine" - look at I/O wait and `D`-state processes, not at CPU.

### Load average, precisely

Three numbers - 1, 5, and 15 minute exponentially-weighted averages of the number of processes **runnable or in uninterruptible sleep**. It is a count, not a percentage, so interpret it **relative to core count**: 4.0 on a 4-core box is fully utilised, 4.0 on a 32-core box is idle. Reported by `uptime`, `top`, and `/proc/loadavg` (which also shows running/total processes and the last PID). Rising 1-minute above the 5- and 15-minute values means the problem is getting worse; the reverse means it is recovering. Pair it with `vmstat 1` (`r` = runnable, `b` = blocked, `wa` = I/O wait) to tell CPU saturation from I/O blocking.

### Signals worth knowing

| Signal                | Number  | Catchable | Use                                                                                  |
| --------------------- | ------- | --------- | ------------------------------------------------------------------------------------ |
| `SIGHUP`              | 1       | Yes       | Historically "terminal closed"; by convention **reload configuration** (nginx, sshd) |
| `SIGINT`              | 2       | Yes       | Ctrl-C                                                                               |
| `SIGQUIT`             | 3       | Yes       | Quit + core dump; on the JVM it prints a **thread dump** - very useful               |
| `SIGKILL`             | **9**   | **No**    | Kernel destroys the process. No cleanup, no flush, no handler                        |
| `SIGTERM`             | **15**  | Yes       | The polite "please shut down". **What `kill` and `docker stop` send**                |
| `SIGSTOP` / `SIGCONT` | 19 / 18 | No / Yes  | Pause and resume                                                                     |
| `SIGUSR1` / `SIGUSR2` | 10 / 12 | Yes       | Application-defined (log rotation, dumping state)                                    |

Linux has 64 signals (31 standard plus 33 real-time); `kill -l` lists them. The number people quote is 64 - and the honest answer is "31 standard, 64 in total including real-time".

The operational point: **SIGTERM is the graceful path and your software must handle it.** A service that ignores SIGTERM makes `systemctl stop` hang for `TimeoutStopSec` (90s by default) and then get SIGKILLed; a container that ignores it makes `docker stop`/Kubernetes wait out `terminationGracePeriodSeconds` and then kill it mid-request. That is why shell-form `ENTRYPOINT` in a Dockerfile is a bug - `/bin/sh` becomes PID 1 and does not forward the signal.

### Finding and killing the right thing

`kill <pid>` (SIGTERM) → wait → `kill -9 <pid>` only if it has not gone. Prefer `pkill`/`pgrep` with `-f` for full command-line matching, `killall` by exact name, and `systemctl stop` for anything systemd manages (killing the process directly just makes systemd restart it, or leaves the unit in a confused state). To kill a whole process tree, `pkill -P <ppid>` or `kill -- -<pgid>` targets the process group - which matters because killing a parent often leaves orphaned children running.

Before killing anything, know what it is: `ps -p <pid> -o pid,ppid,user,etime,%cpu,%mem,cmd`, `ls -l /proc/<pid>/cwd` and `exe`, `lsof -p <pid>` for open files and sockets, and `cat /proc/<pid>/environ | tr '\0' '\n'` for how it was configured.

### Limits: `ulimit`, systemd, and cgroups

**`ulimit`** shows and sets per-process limits inherited by children, with a **soft** limit (current, raisable up to hard) and a **hard** limit (ceiling, only root can raise). The ones that matter:

| Limit                  | `ulimit`        | Failure when exhausted                                                                 |
| ---------------------- | --------------- | -------------------------------------------------------------------------------------- |
| Open files             | `-n` (`nofile`) | **"Too many open files"** - `EMFILE`. Sockets count as files, so a busy server hits it |
| Processes/threads      | `-u` (`nproc`)  | "Resource temporarily unavailable" on fork/thread create                               |
| Core dump size         | `-c`            | No core file after a crash                                                             |
| Memory (address space) | `-v`            | Allocation failure                                                                     |
| Stack size             | `-s`            | Segfault in deeply recursive code                                                      |

**"Too many open files" - the fix, in order**: first check whether it is a **leak** (`ls /proc/<pid>/fd | wc -l` climbing steadily means the application is not closing descriptors - raising the limit only delays the crash); then raise the limit properly. For a systemd service that means `LimitNOFILE=` in the unit, **not** `/etc/security/limits.conf`, because limits.conf is applied by PAM at login and systemd services do not go through PAM - this is the single most common reason "I raised the limit and it did not work". Also check the system-wide ceiling `fs.file-max` and, per process, `fs.nr_open`.

**cgroups** are the container answer: `memory.max`, `cpu.max`, `pids.max`. A container's memory limit is a cgroup limit, and exceeding it gets the process **OOM-killed** by the kernel (exit code 137, visible in `dmesg` and in `kubectl describe pod` as `OOMKilled`) rather than getting a graceful allocation failure. `systemd-cgtop` shows live cgroup usage, and a systemd unit can set `MemoryMax=`, `CPUQuota=`, and `TasksMax=` for the same effect on a host service.

**The OOM killer** deserves a sentence: when the kernel cannot satisfy memory demand it picks a victim by `oom_score` (roughly, biggest memory user, adjustable via `oom_score_adj`) and kills it. So the process that dies is often not the process that caused the problem - which is why "the database was killed" frequently means "a batch job leaked memory". Evidence is always in `dmesg -T | grep -i oom`.

### Priority: `nice` and `ionice`

`nice` sets CPU scheduling priority from **-20 (highest) to 19 (lowest)**; only root can lower the number below 0. `renice` changes it on a running process, and `ionice -c3` puts a process in the idle I/O class. The practical use is making backups, `updatedb`, log compression, and antivirus scans yield to production traffic - `nice -n 19 ionice -c3 tar ...`. It is a courtesy mechanism, not a limit: for hard isolation use cgroups (`CPUQuota=`), which is what containers do.

### Inspecting without `ps` or `top`

Sometimes asked as a puzzle, and the answer is `/proc`: it is a virtual filesystem where every PID is a directory. `ls -d /proc/[0-9]*` enumerates processes, `/proc/<pid>/comm` and `cmdline` name them, `/proc/<pid>/status` gives state, memory, and threads, `/proc/<pid>/fd/` lists open descriptors, and `/proc/<pid>/stack` shows where a `D`-state process is stuck. `ps` and `top` are just readers of `/proc`. Knowing that is the difference between memorising commands and understanding the system.

## Example

```bash
# Find it, understand it, then act
pgrep -a -f 'java.*payments'                     # PID + full command line
ps -p 4412 -o pid,ppid,user,stat,etime,%cpu,%mem,rss,nlwp,cmd
ls -l /proc/4412/cwd /proc/4412/exe              # where it runs, what binary
cat /proc/4412/environ | tr '\0' '\n' | grep -i java_opts
lsof -p 4412 | wc -l                             # open files/sockets
cat /proc/4412/limits                            # THIS process's effective limits
```

```bash
# Graceful first, forceful only if needed
kill 4412                                        # SIGTERM (15) - handled, flushes, cleans up
sleep 10; kill -0 4412 2>/dev/null && kill -9 4412   # SIGKILL only if still alive
kill -HUP $(pgrep -x nginx | head -1)            # reload config without dropping connections
kill -QUIT 4412                                  # JVM: thread dump to stdout - before you kill it
systemctl stop payments                          # for a managed service, use systemd

# Whole tree, not just the parent
pkill -TERM -P 4412                              # children of 4412
kill -TERM -- -$(ps -o pgid= -p 4412 | tr -d ' ') # the process group
```

```bash
# High load, low CPU -> look for D-state and I/O, not CPU
uptime                                           # load 31.4, 28.9, 22.1 on 8 cores
cat /proc/loadavg
ps -eo state,pid,ppid,wchan:25,cmd | awk '$1=="D"'   # who is blocked, and in which kernel call
vmstat 1 5                                        # r=runnable b=blocked wa=iowait
iostat -xz 1 3                                    # %util and await per device
cat /proc/4412/stack                              # exactly where in the kernel it is stuck
dmesg -T | tail -30                               # I/O errors, NFS timeouts, OOM kills

# Zombies: count them, then fix the PARENT
ps -eo stat,ppid,pid,cmd | awk '$1 ~ /^Z/ {print}' | head
ps -eo stat | grep -c '^Z'
```

```bash
# "Too many open files" - leak first, limit second
ls /proc/4412/fd | wc -l                          # is this climbing over time? -> leak
cat /proc/4412/limits | grep 'open files'
sysctl fs.file-max fs.nr_open                     # system-wide ceilings
lsof -p 4412 | awk '{print $5}' | sort | uniq -c | sort -rn | head   # what kind of fds?

# The RIGHT place to raise it for a systemd service (limits.conf does NOT apply)
sudo systemctl edit payments        # creates a drop-in
# [Service]
# LimitNOFILE=65535
# LimitNPROC=8192
sudo systemctl daemon-reload && sudo systemctl restart payments
grep 'Max open files' /proc/$(pgrep -x payments)/limits    # verify it actually took effect
```

```bash
# Limits and priority via cgroups (the container mechanism, on a host service)
systemd-cgtop -1
systemctl set-property payments MemoryMax=2G CPUQuota=200% TasksMax=4096
nice -n 19 ionice -c3 tar czf /backup/data.tgz /data     # yield to production
renice -n 10 -p 4412

# Who did the OOM killer choose, and why was it not the culprit?
dmesg -T | grep -iE 'killed process|oom-kill' | tail
cat /proc/4412/oom_score /proc/4412/oom_score_adj
```

## Interview tips

- Answer the `kill` versus `kill -9` question by mechanism: SIGTERM (15) is catchable so the process can flush, close, and clean up; SIGKILL (9) is handled by the kernel and cannot be caught, so in-flight work, locks, and temporary files are lost. Then state the rule - TERM first, KILL only after it has stopped responding.
- Know the signal count: 31 standard, 64 including real-time, and `kill -l` to list them. Name SIGHUP for config reload and SIGQUIT for a JVM thread dump - both are genuinely useful and few candidates mention them.
- List the process states and spend your time on the two that matter: **`D`** cannot be killed even with -9 and points at storage, and **`Z`** is already dead so you fix the parent. Connect `D` state to high load with low CPU.
- Define load average precisely - a count of runnable **plus uninterruptible** processes, interpreted against core count - and use it to explain the "load 30 on an idle box" scenario.
- For "Too many open files", say it is the `nofile` limit, check for a **descriptor leak first** (`ls /proc/<pid>/fd | wc -l` climbing), and then raise it in the **systemd unit** with `LimitNOFILE=`, noting that `/etc/security/limits.conf` does not apply to systemd services because they do not go through PAM. That last detail is the one that impresses.
- Explain cgroups as the container mechanism and connect exceeding a memory limit to being **OOM-killed with exit code 137** rather than getting a graceful failure.
- Mention that the OOM killer chooses by `oom_score`, so the process that dies is often not the one that leaked - and `dmesg -T | grep -i oom` is the evidence.
- Use `nice`/`ionice` to make backups yield, and say it is a courtesy, not isolation - cgroups are how you enforce.
- If asked to inspect processes without `ps` or `top`, answer `/proc` and explain that `ps` is just a reader of it. See [how do you debug a Linux performance problem from first principles](./how-do-you-debug-a-linux-performance-problem-from-first-principles.md), [troubleshooting SSH failures, high CPU, and disk space](./how-do-you-troubleshoot-ssh-failures-high-cpu-and-disk-space-on-linux-servers.md), [how do namespaces, cgroups, and capabilities isolate a container](../docker/how-do-namespaces-cgroups-and-capabilities-isolate-a-container.md), and [requests, limits, and QoS classes in Kubernetes](../kubernetes/how-do-requests-limits-and-qos-classes-work-in-kubernetes.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you patch hundreds of servers safely?]] (`#430`): [How do you patch hundreds of servers safely?](../configuration-management/how-do-you-patch-hundreds-of-servers-safely.md)
- [[What Bash scripting exercises come up in DevOps interviews?]] (`#502`): [What Bash scripting exercises come up in DevOps interviews?](../scripting-and-automation/what-bash-scripting-exercises-come-up-in-devops-interviews.md)
- [[How do you write a production-grade Bash script?]] (`#266`): [How do you write a production-grade Bash script?](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
