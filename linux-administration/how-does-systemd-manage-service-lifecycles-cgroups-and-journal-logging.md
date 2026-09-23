---
title: "How does systemd manage service lifecycles, cgroups, and journal logging?"
id: 575
category: "Linux Administration"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - linux
  - systemd
  - journalctl
  - cgroups
quiz:
  stem: "How does systemd guarantee that stopping a service also terminates all background child worker processes spawned by that daemon?"
  options:
    - "By parsing process names using regular expressions"
    - "By tracking all processes spawned by the unit inside a dedicated Linux cgroup and terminating the entire cgroup"
    - "By restarting the entire operating system"
    - "By blocking fork() system calls across the host"
  answer: 2
  explanation: "systemd places each service in its own distinct cgroup. When `systemctl stop` is issued, systemd signals all processes residing in that cgroup, preventing orphaned background processes."
---

# How does systemd manage service lifecycles, cgroups, and journal logging?

**Short answer:** systemd is the Linux init system (PID 1) that manages service dependencies in parallel, places every service in its own isolated cgroup to ensure clean process tree termination, and captures stdout/stderr into binary, indexed journal logs (`journalctl`).

## Detail

systemd superseded legacy SysVinit scripts with declarative `.service` unit files:

### Modern systemd Capabilities

1. **Parallel Dependency Resolution**: Services declare `Requires=`, `Wants=`, and `After=`. systemd starts non-dependent services concurrently, dramatically shortening boot times.
2. **Clean Cgroup Tracking (`KillMode=control-group`)**: In SysVinit, if a daemon spawned background child worker processes and crashed, the children became orphaned and continued running. systemd assigns each unit to a dedicated cgroup (`system.slice/nginx.service`); stopping the service reliably terminates every child process in the cgroup.
3. **Structured Binary Journal (`journalctl`)**:
   - Captures `stdout` and `stderr` directly from processes without third-party loggers.
   - Structured indexing by `_PID`, `_UID`, `_SYSTEMD_UNIT`:

     ```bash
     journalctl -u nginx.service --since "1 hour ago" -p err -f
     ```

4. **Sandboxing Directives**:
   - `ProtectSystem=strict` (makes the entire filesystem read-only except `/dev`, `/proc`, `/sys`, and paths you grant with `ReadWritePaths=`; `ProtectSystem=full` covers only `/usr`, `/boot`, and `/etc`).
   - `PrivateTmp=true` (isolates `/tmp` from other services).
   - `NoNewPrivileges=true` (prevents `setuid` privilege escalation).

## Example

```bash
systemctl status nginx                          # state, main PID, cgroup tree, last log lines
systemd-cgls -u nginx.service                   # every process in the unit's cgroup
systemctl show nginx -p KillMode -p TimeoutStopSec -p Restart
systemd-cgtop                                   # live CPU/memory/IO per unit

journalctl -u nginx -b -p warning --no-pager    # this boot, warnings and above
journalctl _SYSTEMD_UNIT=nginx.service _PID=1234 -o json-pretty | head
journalctl --disk-usage && sudo journalctl --vacuum-time=14d

systemd-analyze security nginx.service          # exposure score for the unit's sandboxing
```

## Interview tips

- Explain the lifecycle mechanics: unit files declare dependencies (`Requires=`/`Wants=`) separately from ordering (`After=`/`Before=`), systemd starts everything it can in parallel, and `Restart=` plus `StartLimitBurst=` govern crash loops.
- The cgroup point is the one that matters operationally: every unit gets its own cgroup, so `systemctl stop` finds and kills all descendants (`KillMode=control-group`), and resource controls (`MemoryMax=`, `CPUQuota=`) apply to the whole service.
- Stop sequence: `ExecStop=` or `SIGTERM`, wait `TimeoutStopSec=` (90s default), then `SIGKILL` - which is why a service ignoring SIGTERM makes shutdown hang for exactly 90 seconds.
- Journal trade-offs: structured, indexed, and per-boot, but binary and local; set retention (`SystemMaxUse=`) and make it persistent (`Storage=persistent`) where needed, and forward to a central log system for anything you must keep.
- Use `systemd-analyze security` to show you can harden a unit measurably rather than listing directives from memory.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you write a production-grade Bash script?]] (`#266`): [How do you write a production-grade Bash script?](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md)
- [[What do you use Python for as a DevOps engineer?]] (`#267`): [What do you use Python for as a DevOps engineer?](../scripting-and-automation/what-do-you-use-python-for-as-a-devops-engineer.md)
- [[When do you use Bash and when do you use Python?]] (`#301`): [When do you use Bash and when do you use Python?](../scripting-and-automation/when-do-you-use-bash-and-when-do-you-use-python.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
