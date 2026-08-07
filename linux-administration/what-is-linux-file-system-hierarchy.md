---
title: "What is Linux File System Hierarchy?"
id: 45
category: "Linux Administration"
difficulty: "Beginner"
tags:
  - devops
  - linux-administration
  - interview-questions
---

# What is Linux File System Hierarchy?

**Short answer:** The Filesystem Hierarchy Standard defines a single tree rooted at `/`, with each top-level directory having a defined purpose - `/etc` for configuration, `/var` for variable data, `/usr` for programs, `/proc` and `/sys` for kernel interfaces.

## Detail

| Path             | Purpose                                                               |
| ---------------- | --------------------------------------------------------------------- |
| `/`              | Root of the single tree; everything mounts under it                   |
| `/bin`, `/sbin`  | Essential user and system binaries (usually symlinks into `/usr` now) |
| `/boot`          | Kernel, initramfs, bootloader configuration                           |
| `/dev`           | Device nodes                                                          |
| `/etc`           | Host-specific configuration - never binaries                          |
| `/home`          | User home directories                                                 |
| `/lib`, `/lib64` | Shared libraries and kernel modules                                   |
| `/mnt`, `/media` | Temporary and removable mounts                                        |
| `/opt`           | Self-contained third-party software                                   |
| `/proc`          | Virtual filesystem exposing process and kernel state                  |
| `/root`          | Root user's home                                                      |
| `/run`           | Volatile runtime data (PIDs, sockets), cleared at boot                |
| `/srv`           | Data served by the system (web, ftp)                                  |
| `/sys`           | Virtual filesystem for devices and kernel objects                     |
| `/tmp`           | Temporary files, world-writable, often cleared on boot                |
| `/usr`           | Read-only user programs, libraries, and docs                          |
| `/var`           | Variable data: logs, caches, spools, databases                        |

Two directories earn special attention operationally. `/var` is where disks fill - logs and container layers live there, so it is often a separate filesystem. `/proc` is where you read live process state: `/proc/<pid>/limits`, `/proc/<pid>/fd`, `/proc/meminfo`, `/proc/loadavg`.

## Example

```bash
cat /proc/meminfo | head -3
ls -l /proc/$(pgrep -f myapp)/fd | wc -l    # open file descriptors
cat /proc/$(pgrep -f myapp)/limits          # actual ulimits in force
findmnt -t ext4,xfs                         # what is mounted where
```

## Interview tips

- Know why `/var` gets its own filesystem, and what you do when it fills.
- `/proc` questions are common in troubleshooting rounds - be able to name three useful files.
- Mention that `/etc` holding only configuration is what makes a host's state easy to back up and review.

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
