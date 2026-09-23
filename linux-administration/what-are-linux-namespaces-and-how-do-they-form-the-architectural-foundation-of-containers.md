---
title: "What are Linux namespaces and how do they form the architectural foundation of containers?"
id: 569
category: "Linux Administration"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - linux
  - kernel
  - namespaces
  - containers
  - docker
quiz:
  stem: "Which Linux namespace allows a container process to appear as PID 1 inside the container while running as a high PID number on the underlying host?"
  options:
    - "Network (NET) namespace"
    - "Process ID (PID) namespace"
    - "Mount (MNT) namespace"
    - "User (USER) namespace"
  answer: 2
  explanation: "The PID namespace isolates process ID numbering, allowing the initial container process to be assigned PID 1 while appearing as a regular process on the host."
---

# What are Linux namespaces and how do they form the architectural foundation of containers?

**Short answer:** Linux namespaces partition kernel resources so that a group of processes sees its own isolated instance of them. Linux has eight namespace types - mount, UTS, IPC, PID, network, user, cgroup, and time - and container runtimes combine them (plus cgroups for resource limits, and capabilities, seccomp, and LSMs for privilege) to make an ordinary process look like its own machine. It is isolation, not virtualisation: every container still shares the host kernel.

## Detail

Containers are not virtual machines; they are ordinary Linux processes isolated by kernel **Namespaces** (what you can see) and restricted by **Cgroups** (how much you can use).

### The Namespace Types

1. **PID (Process ID)**: Isolates the process ID space. The container process sees itself as PID 1, while on the host it is PID 45291.
2. **NET (Network)**: Virtualizes network devices, IP routing tables, port bindings, and firewall rules. A container has its own `eth0` and `localhost`.
3. **MNT (Mount)**: Provides an isolated filesystem mount table. The container sees its own root filesystem (`/`) decoupled from the host.
4. **UTS (UNIX Timesharing)**: Allows the container to have its own hostname and domain name.
5. **IPC (Inter-Process Communication)**: Isolates System V IPC and POSIX message queues, preventing cross-container shared memory access.
6. **USER (User ID)**: Maps container user and group IDs to different host UIDs/GIDs (e.g. root UID 0 inside maps to unprivileged UID 100000 outside). This is the one runtimes most often leave **off** by default - Docker needs `userns-remap` or rootless mode, and Kubernetes Pods opt in with `hostUsers: false` - so root in a typical container is still root on the host kernel, constrained only by capabilities, seccomp, and LSMs.
7. **CGROUP**: Virtualises the view of `/sys/fs/cgroup`, so a container sees its own cgroup as the root and cannot inspect the host hierarchy.
8. **TIME** (Linux 5.6+): Gives a namespace its own offsets for the monotonic and boot-time clocks - mainly useful for checkpoint/restore; rarely used by default.

These are created with `clone()`/`clone3()` flags such as `CLONE_NEWPID | CLONE_NEWNET`, detached into new namespaces with `unshare()`, and joined with `setns()` - which is exactly what `docker exec`, `kubectl exec`, and `nsenter` do. Each namespace is visible as a file under `/proc/<pid>/ns/`, and Kubernetes Pods work by sharing the network (and optionally PID) namespace between their containers.

## Example

```bash
# Build a "container" by hand: new PID, mount, UTS, and user namespaces, no runtime involved
unshare --user --map-root-user --pid --fork --mount-proc --uts bash -c '
  hostname sandbox
  echo "hostname: $(hostname)  uid: $(id -u)"
  ps -o pid,cmd       # only this shell and ps - PID 1 is our bash
'

lsns                                   # every namespace on the host and its owning process
ls -l /proc/$$/ns                      # this shell's namespace handles
sudo nsenter --target "$(pgrep -o nginx)" --net ss -ltn   # run a host tool inside nginx's netns
```

## Interview tips

- One line to lead with: namespaces decide what a process can **see**, cgroups decide how much it can **use**, and capabilities/seccomp/LSMs decide what it is **allowed** to do - a container is all three applied to a normal process.
- Name all eight types, and point out that the user namespace is the security-critical one and is often not enabled by default, so container root is host root unless you use rootless mode, `userns-remap`, or Kubernetes user namespaces (`hostUsers: false`).
- Explain how Pods use namespaces: containers in a Pod share the network namespace (hence `localhost` between them), and can share the PID namespace with `shareProcessNamespace`.
- The limitation to state: all containers share one kernel, so a kernel exploit crosses every namespace boundary - which is why sandboxed runtimes (gVisor) and micro-VMs (Kata, Firecracker) exist for untrusted workloads.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you write a production-grade Bash script?]] (`#266`): [How do you write a production-grade Bash script?](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md)
- [[When do you use Bash and when do you use Python?]] (`#301`): [When do you use Bash and when do you use Python?](../scripting-and-automation/when-do-you-use-bash-and-when-do-you-use-python.md)
- [[What is Git?]] (`#46`): [What is Git?](../version-control/what-is-git.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
