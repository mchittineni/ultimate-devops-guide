---
title: "What is the difference between process states D (uninterruptible sleep) and S (interruptible sleep)?"
id: 574
category: "Linux Administration"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - linux
  - processes
  - kernel
  - uninterruptible-sleep
quiz:
  stem: "Why does a Linux system show a high load average (e.g. load of 15 on a 2-core CPU) even though CPU utilization is under 5%?"
  options:
    - "The system clock is running backward"
    - "Multiple processes are blocked in state `D` (uninterruptible sleep) waiting for disk or network I/O, which Linux counts toward load average"
    - "The memory cache is disabled"
    - "The network interface is running in half-duplex mode"
  answer: 2
  explanation: "Unlike UNIX systems that only measure runnable processes on the CPU, Linux includes processes in uninterruptible disk/network sleep (`D` state) in its load average calculation."
---

# What is the difference between process states D (uninterruptible sleep) and S (interruptible sleep)?

**Short answer:** State `S` (Interruptible Sleep) means the process is waiting for an event (timer, socket) and wakes up immediately upon receiving signals; State `D` (Uninterruptible Sleep) means the process is waiting on hardware or disk I/O inside a kernel driver and will not respond to any signals, including `SIGKILL`.

## Detail

When observing high system load average with near-zero CPU utilization, processes are almost always stuck in `D` state.

### State `S` (Interruptible Sleep)

- Typical state for daemons (e.g. NGINX worker waiting for an incoming HTTP request).
- Sleeping, but responds immediately to `SIGTERM` or `SIGKILL`.

### State `D` (Uninterruptible Sleep)

- The process is executing inside a kernel driver waiting for a hardware response:
  - Waiting for disk blocks from an unmounted or hung NFS network share.
  - Waiting for a failing physical hard drive / SAN controller.
  - Page fault waiting for disk swap.
- To prevent filesystem or device corruption, the kernel forbids the process from being interrupted or killed until the hardware call returns.

### How to Handle `D` State Processes

- `kill -9` usually has no effect until the kernel call returns. The exception is `TASK_KILLABLE` sleeps (also shown as `D`), which many NFS and filesystem paths use on modern kernels: they ignore ordinary signals but do die on `SIGKILL`.
- If caused by a hung NFS mount, fix the NFS server or force/lazy unmount (`umount -f -l /mnt/nfs`), and consider `soft`/`timeo` mount options for non-critical mounts (with the trade-off that `soft` can return I/O errors to applications).
- If caused by physical I/O deadlocks, the only resolution is often a host reboot.

## Example

```bash
# High load, idle CPU? Count processes by state, then look at the D ones
ps -eo stat= | cut -c1 | sort | uniq -c              # R, S, D, Z ... counts
ps -eo pid,stat,wchan:32,cmd | awk '$2 ~ /^D/'       # which kernel function each is waiting in
cat /proc/<pid>/stack                                # full kernel stack (root)
vmstat 1 5                                           # "b" column = processes blocked in D state

# Kernel's own report of tasks stuck in D for too long
dmesg -T | grep -A5 'blocked for more than'          # hung_task warnings, with the stack
```

## Interview tips

- Define both by what wakes them: `S` sleeps until an event **or a signal**; `D` sleeps until a kernel operation completes and ignores signals, so the process cannot run its handlers or exit.
- Explain why `D` exists: some kernel paths (block I/O, certain filesystem and driver operations) cannot safely be abandoned half-way, so the kernel does not let signals interrupt them.
- Connect it to load average: Linux counts `D` tasks in the load, so a hung NFS server or failing disk produces a high load on an idle CPU - the classic interview scenario.
- Brief `D` states are normal on busy I/O systems; many processes stuck in `D`, `hung_task` messages in `dmesg`, or the same `wchan` for minutes indicate a storage or driver problem.
- Know the modern nuance: `TASK_KILLABLE` waits (common in NFS) still show as `D` but can be killed with `SIGKILL`; truly uninterruptible waits need the I/O to complete, a forced unmount, or a reboot.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What do you use Python for as a DevOps engineer?]] (`#267`): [What do you use Python for as a DevOps engineer?](../scripting-and-automation/what-do-you-use-python-for-as-a-devops-engineer.md)
- [[When do you use Bash and when do you use Python?]] (`#301`): [When do you use Bash and when do you use Python?](../scripting-and-automation/when-do-you-use-bash-and-when-do-you-use-python.md)
- [[What is Git?]] (`#46`): [What is Git?](../version-control/what-is-git.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
