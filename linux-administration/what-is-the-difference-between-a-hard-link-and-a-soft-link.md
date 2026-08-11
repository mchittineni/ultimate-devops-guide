---
title: "What is the difference between a hard link and a soft link?"
id: 494
category: "Linux Administration"
difficulty: "Beginner"
tags:
  - devops
  - linux-administration
  - interview-questions
---

# What is the difference between a hard link and a soft link?

**Short answer:** A **hard link** is a second **name for the same inode**. The two names are indistinguishable - same inode number, same data, same permissions - and the file's contents survive until the **last** name is removed, because the inode keeps a link count. A **soft link** (symbolic link, symlink) is a separate small file whose contents are a **path string** pointing at another name. So a symlink has its own inode, can point across filesystems, can point at a directory, and **breaks** if the target is renamed or deleted (a "dangling" link), whereas a hard link cannot cross filesystem boundaries, cannot normally target a directory, and never dangles. The practical consequence you use daily: symlinks are how you express "current version" (`/opt/app/current → /opt/app/1.9.0`), and hard links are how tools such as `rsync --link-dest` and package managers build space-efficient snapshots where unchanged files share the same blocks.

## Detail

### The comparison

|                          | Hard link                                              | Soft link (symlink)                          |
| ------------------------ | ------------------------------------------------------ | -------------------------------------------- |
| What it is               | Another directory entry pointing at the **same inode** | A file containing a **path** to another name |
| Own inode                | No - shares the target's                               | Yes                                          |
| `ls -i`                  | Same inode number as the target                        | Different inode number                       |
| Cross filesystems        | **No**                                                 | **Yes**                                      |
| Link to a directory      | No (except `.` and `..`, maintained by the kernel)     | **Yes**                                      |
| Survives target deletion | **Yes** - data lives until link count hits 0           | No - becomes dangling                        |
| Survives target rename   | Yes                                                    | **No** - the stored path no longer resolves  |
| Size                     | N/A (no extra data)                                    | The length of the path string                |
| Permissions              | The inode's - there is only one set                    | Its own are ignored; the target's apply      |
| Shown by `ls -l`         | Looks like an ordinary file                            | `lrwxrwxrwx ... link -> target`              |
| Created with             | `ln target name`                                       | `ln -s target name`                          |

`ls -l` also shows the **link count** in the second column: a regular file with two hard links shows `2`. A directory shows at least `2` (itself and `.`), plus one per subdirectory - which is why an empty directory shows 2 and one with three subdirectories shows 5.

### Why the restrictions exist

- **No cross-filesystem hard links**: an inode number is only meaningful within one filesystem, so a directory entry on `/home` cannot reference an inode on `/var`. A symlink stores a path, which the kernel resolves at access time, so it does not care.
- **No hard links to directories**: allowing them would let you create loops in the directory tree that `find`, backups, and the kernel's own traversal could not safely handle. `.` and `..` are the controlled exceptions.

### Where each one is used in practice

**Symlinks** - almost everything you touch:

- **Release switching**: deploy to `/opt/app/1.9.0`, then atomically repoint `/opt/app/current`. Because a symlink swap is a single rename, it is the classic zero-downtime deployment primitive (`ln -sfn new current` via a temporary link and `mv -T`).
- **`/etc/alternatives`** and `update-alternatives`, `/usr/bin/python3 → python3.12`, systemd's `/etc/systemd/system/multi-user.target.wants/*` - the whole Linux configuration model leans on symlinks.
- **Kubernetes secret and ConfigMap mounts** are directories of symlinks into a hidden versioned directory - which is exactly how the kubelet updates a mounted secret atomically, and why a `subPath` mount (which bypasses the symlink) never refreshes.
- **Log directories** pointing at a bigger volume when `/var/log` is small - though a bind mount is usually the better answer.

**Hard links** - where identity of data matters:

- **Incremental backups**: `rsync --link-dest` hard-links unchanged files to the previous snapshot, so ten daily snapshots of a 100 GB tree may occupy little more than 100 GB while each looks like a full copy. `rsnapshot` and Time Machine work this way.
- **Deduplication** in package managers and container image tooling.
- **Atomic-ish replace patterns**: hard link the new file into place then rename, so the old inode is never lost mid-operation.
- **Making a file harder to lose**: deleting one path does not delete the data.

### The gotchas that come up in real work

- **Editing through a link.** Editors differ: a tool that writes in place (`>>`, `sed -i --follow-symlinks`) affects the shared inode; a tool that writes a temp file and renames (`sed -i` by default, many editors) **replaces the symlink or breaks the hard-link relationship**. This is why "I edited the file and the other copy did not change" happens with hard links, and why `sed -i` on a symlink can leave you with a regular file where a link used to be.
- **`cp` follows symlinks by default**; use `cp -a` (or `-P`/`-d`) to preserve them. Copying a tree of symlinks without `-a` silently turns them into duplicated files, which is a common way to inflate a build artefact.
- **`tar` and Docker `COPY`** follow their own rules; `tar -h` dereferences, and a Dockerfile `COPY` of a symlink pointing outside the build context simply fails.
- **`rm` on a symlink to a directory**: `rm -rf mylink/` (with the trailing slash) can act on the **target's contents**, while `rm mylink` removes just the link. Getting this wrong deletes real data.
- **Relative versus absolute symlink targets**: a relative target survives moving the whole tree (and works inside a `chroot` or container); an absolute one breaks. Prefer relative for anything that might be relocated, and use `ln -sfn` plus `readlink -f` to verify.
- **`find` and disk usage**: `du` counts a multiply-hard-linked file **once** per traversal, which is why `du` totals and `ls -l` sums disagree on a backup tree. `find -samefile` or `find -inum` locates all names for one inode.

## Example

```bash
# Create both and observe the difference immediately
echo "v1" > original.txt
ln    original.txt hard.txt      # same inode
ln -s original.txt soft.txt      # a path string

ls -li
# 1441802 -rw-r--r-- 2 me me   3 Aug 10 10:00 hard.txt      <- same inode, link count 2
# 1441802 -rw-r--r-- 2 me me   3 Aug 10 10:00 original.txt  <- same inode
# 1441913 lrwxrwxrwx 1 me me  12 Aug 10 10:00 soft.txt -> original.txt

stat -c '%n inode=%i links=%h size=%s' original.txt hard.txt soft.txt
```

```bash
# Delete the original: the hard link still has the data, the symlink dangles
rm original.txt
cat hard.txt          # v1        <- data survives; link count is now 1
cat soft.txt          # cat: soft.txt: No such file or directory
ls -l soft.txt        # still listed, but the target is gone (dangling)
find . -xtype l       # find dangling symlinks - useful in a real cleanup
```

```bash
# The release-switch pattern: an atomic symlink swap
install -d /opt/app/1.9.0 && echo "app v1.9.0" > /opt/app/1.9.0/VERSION
ln -sfn 1.9.0 /opt/app/current.tmp && mv -T /opt/app/current.tmp /opt/app/current
readlink -f /opt/app/current      # /opt/app/1.9.0
# rollback is the same operation pointed at the previous directory - instant, atomic

# Space-efficient snapshots with hard links
rsync -a --delete --link-dest=/backup/2026-08-09 /data/ /backup/2026-08-10/
du -sh /backup/*        # each looks full; unchanged files share blocks
find /backup/2026-08-10 -links +1 | head      # the shared files
```

```bash
# Gotchas, demonstrated
cp -a  src/ dst/            # preserves symlinks (use this)
cp -r  src/ dst/            # DEREFERENCES them: duplicated data, larger artefact

# find every name for one inode
find / -xdev -samefile /var/lib/app/data.db 2>/dev/null
find / -xdev -inum 1441802 2>/dev/null

# does this path resolve, and to what?
readlink    /opt/app/current   # 1.9.0            (one hop, as stored)
readlink -f /opt/app/current   # /opt/app/1.9.0   (fully resolved)
namei -l    /opt/app/current/VERSION   # every component's type and permissions
```

## Interview tips

- Answer with the mechanism, not a metaphor: a hard link is another name for the **same inode**; a symlink is a file containing a **path**. Everything else follows from that.
- Immediately give the four consequences: symlinks cross filesystems and can target directories but dangle when the target moves; hard links cannot cross filesystems or target directories but keep the data alive until the last name is gone.
- Prove it the way you would in a shell - `ls -li` showing an identical inode number and a link count of 2. Being able to say "the second column of `ls -l` is the link count" reads as familiarity rather than recall.
- Give one real use for each: a symlink for `current → 1.9.0` release switching (and note the swap is atomic, which is why it is a deployment primitive), and hard links for `rsync --link-dest` incremental backups.
- Volunteer the editing gotcha - tools that write a temp file and rename break the hard-link relationship or replace the symlink - because it explains a class of confusing bugs.
- Mention `cp -a` versus `cp -r` for preserving links, and `find -xtype l` for dangling symlinks. Small, practical, and they signal you have cleaned up a real filesystem.
- If Kubernetes comes up, note that mounted ConfigMaps and Secrets are directories of symlinks into a versioned directory, which is how atomic updates work - and why `subPath` mounts never refresh. That connects a Linux fundamental to a container problem, which is exactly the kind of link interviewers reward. See [what is Linux File System Hierarchy](./what-is-linux-file-system-hierarchy.md), [basic Linux commands every DevOps engineer should know](./what-are-the-basic-linux-commands-every-devops-engineer-should-know.md), and [how do you manage disks, filesystems, and LVM on Linux](./how-do-you-manage-disks-filesystems-and-lvm-on-linux.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What Bash scripting exercises come up in DevOps interviews?]] (`#502`): [What Bash scripting exercises come up in DevOps interviews?](../scripting-and-automation/what-bash-scripting-exercises-come-up-in-devops-interviews.md)
- [[How to handle merge conflicts in Git?]] (`#50`): [How to handle merge conflicts in Git?](../version-control/how-to-handle-merge-conflicts-in-git.md)
- [[What is the difference between git merge, rebase, and cherry-pick?]] (`#263`): [What is the difference between git merge, rebase, and cherry-pick?](../version-control/what-is-the-difference-between-git-merge-rebase-and-cherry-pick.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
