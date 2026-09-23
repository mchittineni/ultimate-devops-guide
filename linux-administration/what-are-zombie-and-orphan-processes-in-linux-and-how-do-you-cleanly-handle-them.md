---
title: "What are Zombie and Orphan processes in Linux and how do you cleanly handle them?"
id: 573
category: "Linux Administration"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - linux
  - processes
  - zombie
  - orphan
  - signals
quiz:
  stem: "Why does executing `kill -9 <PID>` on a zombie process fail to remove it from the output of `ps`?"
  options:
    - "Zombie processes are protected by immutable SELinux policies"
    - "The process is already dead and has released its memory; it only exists as an entry in the kernel process table until its parent calls `wait()`"
    - "Only the root user can issue signals to zombies"
    - "Zombie processes execute exclusively inside the kernel space"
  answer: 2
  explanation: "A zombie has already terminated; no executable code remains to receive signals. It persists only as an entry in the process table until its parent reaps its exit code via `wait()`."
---

# What are Zombie and Orphan processes in Linux and how do you cleanly handle them?

**Short answer:** An Orphan process is one whose parent died before it finished (adopted by PID 1/systemd); a Zombie process (`<defunct>`) is a terminated process that has released its memory but remains in the process table until its parent reads its exit status code via `wait()`.

## Detail

Understanding process lifecycle states (`R`, `S`, `D`, `Z`, `T`):

### 1. Orphan Processes

- A parent process terminates while its child is still executing.
- The Linux kernel automatically re-parents the orphan to **PID 1** (`systemd` on VMs, or `tini`/`dumb-init` in containers).
- When the orphan eventually terminates, PID 1 reaps it cleanly.

### 2. Zombie Processes (`Z` state in `ps` / `<defunct>`)

- A child process terminates (`exit()`).
- The kernel frees its memory, open files, and CPU allocations.
- However, the kernel keeps an entry in the **Process Table** holding the process ID, exit code, and termination status.
- The parent is expected to call `wait()` or `waitpid()` to collect this exit status.
- If the parent is poorly written and never calls `wait()`, the zombie process lingers!

### How to Kill a Zombie Process

You **cannot kill a zombie with `kill -9`** because the process is already dead!

- To clear zombies, you must either:
  1. Send `SIGCHLD` to the parent to prompt it to reap its children - this only helps if the parent has a `SIGCHLD` handler that calls `wait()`; a parent that never reaps will ignore it.
  2. Kill the parent process. Once the parent dies, the zombies become orphans adopted by PID 1, which instantly reaps them.

## Example

```bash
# Create a zombie on purpose: the child exits, the parent (exec'd sleep) never calls wait()
bash -c 'sleep 1 & exec sleep 60' &
sleep 2
ps -o pid,ppid,stat,cmd --ppid $!        # the child shows STAT "Z" and "<defunct>"

# Find zombies and their parents across the host
ps -eo pid,ppid,stat,cmd | awk '$3 ~ /^Z/'

# Fix the PARENT, not the zombie
kill -TERM <parent-pid>                  # its zombies are re-parented to PID 1 and reaped
```

```dockerfile
# Containers: give PID 1 a real init so orphans are reaped
FROM debian:13-slim
RUN apt-get update && apt-get install -y --no-install-recommends tini && rm -rf /var/lib/apt/lists/*
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/usr/local/bin/app"]
# or at run time: docker run --init ...
```

## Interview tips

- Separate the two clearly: an **orphan** is alive with a dead parent (harmless, adopted by PID 1 or the nearest subreaper); a **zombie** is dead with a living parent that has not collected its exit status.
- Zombies use no memory or CPU, only a PID and a process-table entry; the risk is PID exhaustion (`kernel.pid_max`, or a cgroup `pids.max` inside containers) when a buggy parent leaks thousands.
- You cannot kill a zombie - kill or fix the parent so the zombie is re-parented and reaped.
- In containers, PID 1 has special duties: it must reap adopted children and handle signals itself (the kernel does not apply default signal actions to PID 1). Use `tini`, `docker run --init`, or a language runtime that reaps, and exec-form `ENTRYPOINT` so signals reach the app.
- Mention subreapers: `prctl(PR_SET_CHILD_SUBREAPER)` lets a supervisor (systemd user instances, tini with `-s`) adopt orphans instead of PID 1.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[When do you use Bash and when do you use Python?]] (`#301`): [When do you use Bash and when do you use Python?](../scripting-and-automation/when-do-you-use-bash-and-when-do-you-use-python.md)
- [[What is Git Branching Strategy?]] (`#47`): [What is Git Branching Strategy?](../version-control/what-is-git-branching-strategy.md)
- [[What is Trunk Based Development?]] (`#49`): [What is Trunk Based Development?](../version-control/what-is-trunk-based-development.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
