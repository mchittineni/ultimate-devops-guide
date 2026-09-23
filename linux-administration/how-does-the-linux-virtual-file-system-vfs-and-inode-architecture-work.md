---
title: "How does the Linux Virtual File System (VFS) and inode architecture work?"
id: 570
category: "Linux Administration"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - linux
  - filesystem
  - inodes
  - vfs
quiz:
  stem: "Why can an application fail with 'No space left on device' when `df -h` reports 200 GB of free disk space?"
  options:
    - "The Linux kernel limits files to 10MB in size"
    - "The filesystem has exhausted its allocated inode table (`df -i`), typically caused by millions of tiny files"
    - "The CPU is overheating and throttling write operations"
    - "The hard disk sector size was changed while the machine was running"
  answer: 2
  explanation: "Filesystems pre-allocate a fixed number of inodes. Creating millions of tiny files can consume all available inodes before raw disk capacity is exhausted, preventing new file creation."
---

# How does the Linux Virtual File System (VFS) and inode architecture work?

**Short answer:** VFS is the kernel abstraction layer providing a uniform interface across diverse filesystems (ext4, XFS, NFS); inodes are metadata data structures storing file permissions, ownership, file size, and disk block pointers, but NOT the file name or file contents.

## Detail

In Linux, 'everything is a file', and VFS makes them behave consistently:

### Inode Structure & Data Separation

An inode stores:

- File mode (permissions, file type).
- Owner UID and Group GID.
- File size in bytes.
- Timestamps: `atime` (access), `mtime` (content modification), `ctime` (inode metadata change).
- Pointers to disk blocks containing actual content.

**What an inode does NOT store:**

- The filename!
- Directory entries (dentries) map a human-readable string (`app.log`) to an inode number (`142981`).

### The 'No Space Left on Device' Inode Mystery

You run `df -h` and disk space shows 50% free, but writing a file fails with `No space left on device`!

- **Root Cause**: The filesystem ran out of **inodes** (`df -i` shows 100% inode utilization).
- This happens when millions of tiny 0-byte cache or session files exhaust the pre-allocated inode table even though gigabytes of raw disk space remain.

## Example

```bash
ls -li /var/log/syslog                     # first column: the inode number
stat /var/log/syslog                       # mode, owner, size, links, atime/mtime/ctime (+ Birth on statx)
df -i /var                                 # inode usage per filesystem
debugfs -R 'stat <142981>' /dev/nvme0n1p1  # ext4: raw inode, including extents (read-only use)

# Find the directory eating inodes (millions of tiny files)
sudo find /var -xdev -type f | awk -F/ '{print "/"$2"/"$3}' | sort | uniq -c | sort -rn | head

# The VFS in action: the same syscalls against very different filesystems
findmnt -o TARGET,FSTYPE | head
strace -e trace=openat,read,close cat /proc/loadavg   # procfs has no disk at all
```

## Interview tips

- Describe the layering: applications call `open`/`read`/`write`; the VFS resolves the path through the dentry cache to an inode and dispatches to the filesystem's operations - which is why ext4, XFS, NFS, procfs, and overlayfs all look the same to a program.
- Be exact about what an inode holds (type and mode, owner, size, link count, timestamps, block or extent map) and what it does not (the name, which lives in the directory entry). That is why a file can have several names (hard links) and why renaming within a filesystem is cheap.
- Correct a common slip: `ctime` is the inode **change** time, not the creation time; creation (birth) time is exposed separately via `statx` where the filesystem supports it.
- Inode exhaustion: ext4 fixes the inode count at `mkfs` time (tunable with `-i`/`-N`), while XFS and Btrfs allocate inodes dynamically - so the "50% full but no space left" failure is mostly an ext4 story.
- Mention the caches: the dentry and inode caches are part of reclaimable kernel memory, which is why `slabtop` can show large `dentry` usage on hosts that touch millions of files.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[When do you use Bash and when do you use Python?]] (`#301`): [When do you use Bash and when do you use Python?](../scripting-and-automation/when-do-you-use-bash-and-when-do-you-use-python.md)
- [[What is Git?]] (`#46`): [What is Git?](../version-control/what-is-git.md)
- [[How does Git internally store data using Blobs, Trees, Commits, and Annotated Tags?]] (`#578`): [How does Git internally store data using Blobs, Trees, Commits, and Annotated Tags?](../version-control/how-does-git-internally-store-data-using-blobs-trees-commits-and-annotated-tags.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
