---
title: "How do namespaces, cgroups, and capabilities isolate a container?"
id: 291
category: "Docker"
difficulty: "Advanced"
tags:
  - devops
  - docker
  - interview-questions
---

# How do namespaces, cgroups, and capabilities isolate a container?

**Short answer:** Three independent kernel features doing three different jobs. **Namespaces** change what a process can _see_ (its own PID tree, network stack, mounts, hostname, users). **Cgroups** limit what it can _consume_ (CPU, memory, IO, PIDs). **Capabilities**, plus seccomp and LSMs like AppArmor or SELinux, limit what it can _do_ (which privileged operations the kernel will accept). A container is just a normal Linux process with these three constraints applied - which is why it shares the host kernel and why "container escape" is a meaningful phrase in a way that "VM escape" rarely is.

## Detail

**Namespaces - visibility.** Each namespace type virtualises one global kernel resource:

| Namespace | Isolates                              | Practical effect                                       |
| --------- | ------------------------------------- | ------------------------------------------------------ |
| `pid`     | Process IDs                           | Your app is PID 1 and cannot see host processes        |
| `net`     | Interfaces, routes, iptables, sockets | Own `eth0`, own port space, own firewall rules         |
| `mnt`     | Mount table                           | Own root filesystem view                               |
| `uts`     | Hostname and domain name              | `hostname` returns the container ID                    |
| `ipc`     | Shared memory, semaphores             | Cannot reach host SysV IPC                             |
| `user`    | UID/GID mapping                       | Root in the container maps to an unprivileged host UID |
| `cgroup`  | Cgroup root view                      | Cannot see the host's cgroup hierarchy                 |
| `time`    | Clock offsets (`CLOCK_MONOTONIC`)     | Rarely used; supports checkpoint/restore               |

Being PID 1 has real consequences: PID 1 ignores default signal handlers unless the process installs them (so `SIGTERM` may be dropped and your container gets `SIGKILL`ed after the grace period), and PID 1 must reap zombies. That is why `--init` / `tini` exists, and why shell-form `CMD` (which leaves `/bin/sh` as PID 1) breaks graceful shutdown.

**Cgroups (v2) - consumption.** A unified hierarchy where each controller enforces one resource. `memory.max` is a hard wall: exceed it and the kernel OOM-kills the process inside the container - you see exit code 137 and `OOMKilled`, while the host stays healthy. CPU works differently: `cpu.max` sets a quota per period (throttling, not killing), and `cpu.weight` sets relative share under contention. This asymmetry is the single most useful thing to know - **memory limits kill, CPU limits throttle** - and it is why CPU limits on latency-sensitive services can cause mysterious p99 spikes while the average looks fine. `pids.max` prevents fork bombs; `io.max` throttles block IO.

**Capabilities - permitted operations.** Linux splits root's power into ~40 capabilities. Docker drops most by default and keeps a small set (`CHOWN`, `NET_BIND_SERVICE`, `SETUID`, `SETGID`, `KILL`, and others). This is why a container "root" cannot load kernel modules (`CAP_SYS_MODULE`) or change the host clock (`CAP_SYS_TIME`). The dangerous ones to grant deliberately: `CAP_SYS_ADMIN` (mount operations - effectively a path to escape), `CAP_NET_ADMIN`, `CAP_SYS_PTRACE`, `CAP_DAC_READ_SEARCH`.

**The layers above capabilities.** **Seccomp** filters syscalls themselves; Docker's default profile blocks around 40 of them. **AppArmor / SELinux** add mandatory access control on files and operations. **User namespaces** are the strongest single hardening step, mapping container UID 0 to an unprivileged host UID, so even a full capability set inside the container is unprivileged outside it - this is the core of rootless containers (Podman rootless, Docker rootless mode).

**Where isolation ends, and this is the part interviewers push on.** The kernel is shared, so a kernel vulnerability is a cross-container vulnerability. `--privileged` disables essentially all of the above. Mounting `/var/run/docker.sock` gives the container control of the daemon, which is root on the host. `hostPID`, `hostNetwork`, and host path mounts each remove one namespace's protection. Writable `hostPath` mounts of `/` or `/proc` are direct escapes. For genuinely untrusted workloads, process isolation is not enough - use a VM boundary (Firecracker, Kata Containers) or gVisor's user-space kernel.

## Example

```bash
# A container is a process. Prove it from the host.
docker run -d --name demo --memory=256m --cpus=0.5 nginx
pid=$(docker inspect -f '{{.State.Pid}}' demo)

ls -l /proc/$pid/ns/          # the namespaces this process is in
ps -o pid,comm -p $pid        # visible on the host as an ordinary process
cat /proc/$pid/status | grep -i cap   # the capability bounding set

# The cgroup v2 limits, as the kernel sees them
cgroup=$(cat /proc/$pid/cgroup | cut -d: -f3)
cat /sys/fs/cgroup$cgroup/memory.max      # 268435456
cat /sys/fs/cgroup$cgroup/cpu.max         # 50000 100000  (0.5 CPU)
cat /sys/fs/cgroup$cgroup/cpu.stat        # nr_throttled - the p99 latency culprit

# Enter one namespace at a time to see what isolation each provides.
nsenter -t $pid -n ip addr    # container's network namespace only
nsenter -t $pid -p -m ps aux  # its PID + mount view: just nginx, as PID 1
```

```bash
# Isolation removed - each of these is a known escape or a large step toward one.
docker run --privileged ...                      # drops seccomp/AppArmor, all caps, device access
docker run -v /var/run/docker.sock:/var/run/docker.sock ...   # = root on the host
docker run --pid=host --net=host ...             # host PID and network namespaces
docker run --cap-add=SYS_ADMIN ...               # mount(2): a path to escape

# Isolation strengthened
docker run --user 10001:10001 --read-only \
  --cap-drop=ALL --cap-add=NET_BIND_SERVICE \
  --security-opt no-new-privileges \
  --security-opt seccomp=./profile.json \
  --pids-limit 200 --memory=256m --init myapp:1.4.0
```

```yaml
# The same controls, expressed in Kubernetes.
securityContext:
  runAsNonRoot: true
  runAsUser: 10001
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities: { drop: ["ALL"], add: ["NET_BIND_SERVICE"] }
  seccompProfile: { type: RuntimeDefault }
resources:
  requests: { cpu: 100m, memory: 128Mi }
  limits: { memory: 256Mi } # memory limit yes; CPU limit only if you accept throttling
```

## Interview tips

- Give the three-way split in one sentence - namespaces see, cgroups consume, capabilities do. It is the cleanest possible framing and most candidates blur them.
- "Memory limits kill, CPU limits throttle" is the highest-value practical detail. Connect it to `nr_throttled` and unexplained p99 latency.
- Explain the PID 1 signal problem and why `--init` or exec-form `CMD` matters for graceful shutdown.
- Name user namespaces as the strongest hardening step and link them to rootless containers.
- Be specific about escapes: `--privileged`, the Docker socket, `hostPID`/`hostNetwork`, writable host path mounts. Vague "containers are less secure than VMs" answers score poorly.
- Finish with the boundary: shared kernel means untrusted workloads need a VM or gVisor. Knowing when process isolation is insufficient is the senior signal.

---

[⬅ Back to Docker](./README.md) · [All topics](../README.md)
