---
title: "How do Linux file permissions, umask, and the setuid, setgid, and sticky bits work?"
id: 778
category: "Linux Administration"
difficulty: "Beginner"
tags:
  - devops
  - linux-administration
  - interview-questions
quiz:
  stem: "A directory is mode `drwxrwxrwt` (1777). What does the trailing `t` change compared with plain 777?"
  options:
    - "Files in it are deleted automatically at reboot"
    - "Any user can create files, but only a file's owner, the directory's owner, or root can delete or rename it"
    - "Programs in it run with the directory owner's privileges"
    - "New files inherit the directory's group"
  answer: 2
  explanation: "The sticky bit on a directory restricts unlink and rename to the file owner, the directory owner, or root - which is why /tmp is world-writable without letting users delete each other's files. Inheriting the group is setgid, not sticky."
---

# How do Linux file permissions, umask, and the setuid, setgid, and sticky bits work?

**Short answer:** Every file has an owner, a group, and three permission triplets - **user, group, other** - each of **read (4), write (2), execute (1)**, so `chmod 640` means owner read-write, group read, others nothing. The kernel checks exactly one triplet: the owner's if you own the file, else the group's if you are in its group, else other's. On a **directory** the bits mean something different: `r` lists names, `w` creates, deletes, and renames entries, and `x` lets you traverse into it - which is why deleting a file depends on the directory's permissions, not the file's. **umask** removes bits from the default mode of new files (`0666`) and directories (`0777`), so a umask of `022` yields `644` and `755`. Three special bits sit in front: **setuid (4)** runs an executable as its owner (`passwd`), **setgid (2)** runs as the file's group or, on a directory, makes new files inherit the directory's group, and the **sticky bit (1)** on a directory lets only a file's owner delete it (`/tmp`). Beyond the classic model come **ACLs** for per-user grants, **capabilities** to replace setuid-root, and SELinux/AppArmor as a mandatory layer on top.

## Detail

### Reading `ls -l`

```text
-rwxr-x---  1 deploy  app   4096  app.sh
│└┬┘└┬┘└┬┘
│ │  │  └── other: ---  (0)
│ │  └───── group: r-x  (5)
│ └──────── user:  rwx  (7)    -> mode 750
└────────── type: - file, d directory, l symlink, s socket, p pipe, c/b device
```

A capital `S` or `T` in the execute position means the special bit is set but execute is **not** - usually a mistake. A trailing `+` (`-rw-r-----+`) means an ACL is present, and `.` means an SELinux context.

### Files versus directories

| Bit | On a file       | On a directory                               |
| --- | --------------- | -------------------------------------------- |
| `r` | read contents   | list entry names (`ls`)                      |
| `w` | modify contents | create, delete, and rename entries in it     |
| `x` | execute it      | traverse it - access anything inside by name |

Two consequences interviewers like: you can delete a read-only file you do not own if you have `w` on its directory (unless the sticky bit is set), and a directory with `x` but not `r` lets you open a file whose name you know without being able to list the directory. Every directory on the path needs `x`, which is the usual cause of "permission denied" on a file whose own mode looks fine - `namei -l /path/to/file` shows each component.

### umask

umask is subtracted (bitwise, not arithmetically) from the requested mode at creation time. Files start from `0666` because the kernel never sets execute by default; directories from `0777`.

| umask | New file | New directory | Typical use                          |
| ----- | -------- | ------------- | ------------------------------------ |
| `022` | `644`    | `755`         | Most distribution defaults           |
| `027` | `640`    | `750`         | Servers: nothing for "other"         |
| `077` | `600`    | `700`         | Secrets, private keys, CI runners    |
| `002` | `664`    | `775`         | Shared-group development directories |

It is per process and inherited by children. Set it in the shell profile, in a systemd unit with `UMask=0027`, or at the top of a script that writes secrets. It only affects **new** files - `chmod` changes existing ones.

### The special bits

- **setuid (`4xxx`, `s` in the user execute slot)** - the program runs with the file **owner's** effective UID. `/usr/bin/passwd` is setuid root so it can write `/etc/shadow`. Every setuid-root binary is a privilege-escalation target, so audit them, and note that Linux ignores setuid on interpreted scripts. A filesystem mounted `nosuid` ignores the bit entirely - the standard hardening for `/tmp`, `/home`, and removable media.
- **setgid (`2xxx`)** - on an executable, runs with the file's group. On a **directory**, new files and subdirectories inherit the directory's group instead of the creator's primary group, which is how shared team directories stay usable (combine with umask `002`).
- **sticky (`1xxx`, `t` in the other execute slot)** - on a directory, only the file's owner, the directory's owner, or root can delete or rename entries. `/tmp` is `1777`: anyone can write, nobody can delete anyone else's files.

### Beyond the classic model

- **ACLs** (`setfacl`/`getfacl`) grant permissions to additional named users and groups without changing ownership - for example giving a log shipper read access to `/var/log/app` while the app user still owns it. A **default ACL** on a directory is inherited by new files, and the ACL **mask** caps what named entries actually get.
- **Capabilities** split root into pieces. `setcap cap_net_bind_service=+ep ./server` lets a binary bind port 443 without setuid root; in containers, dropping all capabilities and adding back only what is needed is the same idea.
- **Mandatory access control** - SELinux (RHEL family) or AppArmor (Ubuntu, Debian, SUSE) - is checked _after_ the permission bits, so a file can be `777` and still be denied. When permissions look right and access still fails, check `ausearch -m avc` or `dmesg` for an AppArmor denial before reaching for `chmod 777`.
- **Ownership** - `chown user:group`, and only root can give a file away. In containers, the UID matters rather than the name: a volume owned by UID 1000 on the host is unwritable by a container process running as UID 10001, whatever the user names say.

### Practical rules

- Secrets: `600` or `640` with a dedicated group, owned by the service user, umask `077` when writing them.
- SSH: `~/.ssh` `700`, `authorized_keys` and private keys `600`, home directory not group- or world-writable - otherwise `sshd` rejects the key under `StrictModes`.
- Never fix a permission problem with `chmod -R 777`. Find which check is failing (`namei -l`, the owning UID, ACLs, then MAC) and grant the minimum.

## Example

```bash
# Symbolic and octal forms
chmod 640 /etc/app/config.yaml           # rw- r-- ---
chmod u+x,g-w,o= deploy.sh               # add/remove per class
chown app:app /etc/app/config.yaml
stat -c '%A %a %U:%G %n' /etc/app/config.yaml   # -rw-r----- 640 app:app ...

# umask in action
umask 027; touch f; mkdir d; ls -ld f d  # -rw-r----- f, drwxr-x--- d

# Special bits
ls -l /usr/bin/passwd                    # -rwsr-xr-x  (setuid root)
ls -ld /tmp                              # drwxrwxrwt  (sticky)
install -d -m 2775 -g devs /srv/shared   # setgid dir: new files get group devs
find / -xdev -perm -4000 -type f 2>/dev/null   # audit every setuid binary

# Why can't I read this file? Check every component of the path
namei -l /srv/app/data/report.csv

# ACLs: give one extra user read access without changing ownership
setfacl -m u:fluentbit:rx /var/log/app
setfacl -d -m u:fluentbit:r /var/log/app # default ACL: inherited by new files
getfacl /var/log/app

# Capabilities instead of setuid root
sudo setcap cap_net_bind_service=+ep /usr/local/bin/server
getcap /usr/local/bin/server
```

## Interview tips

- Explain the check order - owner, then group, then other, and only one triplet applies - rather than reciting octal values. It explains why an owner with `0` permissions is denied even though "other" has read.
- Spend a sentence on directory semantics: `w` on the directory is what allows deletion, and `x` is needed on every component of the path. That answers most real "permission denied" puzzles.
- Show umask arithmetic as masking from `666`/`777`, and mention `UMask=` in a systemd unit for services that write files.
- For the special bits, give the canonical example of each: `passwd` for setuid, a shared team directory for setgid, `/tmp` for sticky - and that `nosuid` mounts neutralise setuid.
- Mention ACLs, capabilities, and SELinux/AppArmor to show you know the classic bits are not the whole story - and say you would never fix access with `chmod 777`. See [what is Linux File System Hierarchy](./what-is-linux-file-system-hierarchy.md), [troubleshooting SSH failures, high CPU, and disk space](./how-do-you-troubleshoot-ssh-failures-high-cpu-and-disk-space-on-linux-servers.md), and [why a container fails to start with a permission denied error](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you patch hundreds of servers safely?]] (`#430`): [How do you patch hundreds of servers safely?](../configuration-management/how-do-you-patch-hundreds-of-servers-safely.md)
- [[What Bash scripting exercises come up in DevOps interviews?]] (`#502`): [What Bash scripting exercises come up in DevOps interviews?](../scripting-and-automation/what-bash-scripting-exercises-come-up-in-devops-interviews.md)
- [[How do you write a production-grade Bash script?]] (`#266`): [How do you write a production-grade Bash script?](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
