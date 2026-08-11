---
title: "How do you manage disks, filesystems, and LVM on Linux?"
id: 496
category: "Linux Administration"
difficulty: "Intermediate"
tags:
  - devops
  - linux-administration
  - interview-questions
  - infrastructure-monitoring
---

# How do you manage disks, filesystems, and LVM on Linux?

**Short answer:** Work down the stack: a **block device** (`/dev/nvme1n1`) optionally carries a **partition table**, on top of which you either create a filesystem directly or build **LVM** - a physical volume (`pvcreate`), grouped into a volume group (`vgcreate`), sliced into logical volumes (`lvcreate`) - and then a filesystem (`mkfs.xfs`/`mkfs.ext4`) mounted at a path, recorded in `/etc/fstab` **by UUID**. LVM exists to break the one-disk-one-filesystem coupling: you can add a disk to a volume group and **grow a logical volume and its filesystem online, with no downtime** (`lvextend -r`), which is exactly the answer to "add 50 GB to `/opt` with no downtime". The distinction people miss: a **directory** is a path in an existing filesystem, a **mount point** is a directory where a _different_ filesystem is attached - and `df -h <path>` versus `findmnt` is how you tell which you are looking at. Two failure modes are worth knowing cold: a filesystem that is only half full but cannot be written to because **inodes** are exhausted (`df -ih`), and a filesystem the kernel has remounted **read-only** after an I/O error.

## Detail

### The stack, and the commands at each level

```text
/dev/nvme1n1               block device        lsblk, fdisk -l, nvme list
  └─ /dev/nvme1n1p1        partition           parted, fdisk, sgdisk
      └─ PV                LVM physical vol    pvcreate, pvs, pvdisplay
          └─ VG            volume group        vgcreate, vgextend, vgs
              └─ LV        logical volume      lvcreate, lvextend, lvs
                  └─ FS    filesystem          mkfs.xfs, mkfs.ext4, blkid
                      └─ /opt   mount point    mount, /etc/fstab, findmnt, df
```

You do not always need partitions or LVM - in the cloud it is common to `mkfs` a whole attached device, because you resize the volume at the provider level instead. Use LVM when you want to span disks, snapshot, or resize a volume that is one of several on a host.

### Directory versus mount point - and why it matters

A **directory** is just a name inside a filesystem. A **mount point** is a directory where another filesystem is grafted on, so files under it live on a different device with its own free space, inode count, and options. Practical consequences: `du` of a mount point measures the other filesystem; a process holding a file open under it blocks unmounting (`lsof +D /data`, `fuser -vm /data`); and files that existed in the directory **before** something was mounted over it become invisible until you unmount - a genuinely confusing situation when a deploy writes to a path before the volume is attached.

```bash
findmnt /data          # is it a mount point, and what is mounted there?
mountpoint -q /data && echo "mount point" || echo "just a directory"
df -h /data            # which filesystem does this path resolve to?
```

### Growing storage online

The zero-downtime path, in order:

1. **Grow the underlying device** - in the cloud, `aws ec2 modify-volume` / Azure disk resize / GCP resize; on-premises, attach a new disk.
2. **Make the kernel see it**: for a resized device `partprobe` or `echo 1 > /sys/class/block/<dev>/device/rescan`; for a new disk it appears automatically or after a SCSI rescan.
3. **Grow the partition** if there is one - `growpart /dev/nvme1n1 1` (from cloud-utils) is the safe tool; `parted resizepart` also works.
4. **LVM**: `pvresize` if you grew an existing PV, or `pvcreate` the new disk and `vgextend` the volume group. Then `lvextend -r -L +50G /dev/vg0/opt` - the `-r` resizes the filesystem in the same step.
5. **Without LVM**: `xfs_growfs /mount/point` (XFS grows by mount point, and only grows) or `resize2fs /dev/nvme1n1p1` (ext4 grows online, and shrinks only when unmounted).

Everything above is online. **Shrinking** is not: XFS cannot shrink at all, and ext4 shrinking requires an unmount and a fsck. If someone asks how to shrink, the honest answer is "create a new smaller volume, copy, and swap" - and that is a maintenance window.

### XFS versus ext4, briefly

**XFS** is the default on RHEL-family systems, scales well to large files and parallel I/O, and cannot be shrunk. **ext4** is the Debian/Ubuntu default, can shrink offline, and has slightly lower metadata overhead for many small files. Both are fine; the choice matters less than the operational facts - XFS grows only, ext4 grows online and shrinks offline. Mention `noatime` (or `relatime`, the modern default) to cut needless metadata writes on write-heavy volumes, and `discard`/`fstrim.timer` for SSDs.

### The two failure modes worth memorising

**Inodes exhausted.** `df -h` shows 50% used but writes fail with "No space left on device". The filesystem has run out of **inodes** - one per file - typically because something created millions of tiny files (a session directory, a mail queue, unrotated per-request logs, or a container writing per-event files). Diagnose with `df -ih`; find the culprit by counting files per directory. You cannot add inodes to an existing ext4 filesystem (they are fixed at `mkfs` time), so the fix is deleting files or recreating the filesystem with a smaller `-i` bytes-per-inode ratio. XFS allocates inodes dynamically, which makes it more forgiving here.

**Read-only remount.** Writes fail and `mount` shows `ro` on a filesystem you created `rw`. The kernel remounted it read-only after an I/O error to protect data - check `dmesg -T` for I/O errors and the device's health. On a cloud volume this can also be an EBS/disk-level failure or a detached device. The wrong response is `mount -o remount,rw` and carrying on; the right one is reading `dmesg`, running a filesystem check on an unmounted device (`xfs_repair`, `fsck.ext4`), and replacing the volume from a snapshot if the device is failing.

Third one worth naming because it is more common than both: **space held by deleted-but-open files**. `du` says 20 GB, `df` says 90% full, because a process still holds a deleted log file open - so the blocks are not freed until the process closes it or restarts. `lsof +L1` (or `lsof | grep deleted`) finds it. This is the classic "I deleted the logs and nothing changed" incident, and the real fix is log rotation with `copytruncate` or a proper `postrotate` reload.

### Separating workloads onto their own filesystems

The frequent scenario - _"can you separate disk space on one instance so the application runs on one partition and the observability stack on another, and how?"_ - is a yes, and LVM is the clean way: one volume group across the attached disks, one logical volume per workload (`lv_app`, `lv_observability`), each with its own filesystem and mount point. Benefits: a runaway log directory cannot fill the application's filesystem, you can grow one without touching the other, and you can apply different mount options and quotas. The alternatives are separate cloud volumes (simplest in the cloud, and independently snapshot-able) or XFS project quotas (`prjquota`) if you want limits without separate filesystems. Say which you would choose and why - separate volumes in the cloud, LVM on bare metal with a fixed set of disks.

Standard split on a server: `/` , `/var` (logs and container storage - the usual culprit), `/var/log`, `/home`, and `/tmp` (or a tmpfs). Isolating `/var/log` in particular stops a log flood taking the whole host down.

### Snapshots, and their limits

LVM snapshots (`lvcreate -s`) give a point-in-time copy-on-write view - useful for taking a consistent backup of a database volume after flushing, then removing the snapshot. Two caveats: a snapshot that fills its allocated space is **invalidated**, and LVM snapshots impose a write penalty while they exist, so they are for short-lived operations, not retention. In the cloud, provider volume snapshots are usually the better tool, and for databases the engine's own backup is better than either.

## Example

```bash
# Survey the stack before changing anything
lsblk -f                          # devices, partitions, filesystems, UUIDs, mount points
df -hT                            # usage by filesystem, with type
df -ih                            # INODE usage - the check people forget
findmnt --real                    # what is mounted where, with options
pvs && vgs && lvs -o +devices     # the LVM picture
```

```bash
# Add 50 GB to /opt with no downtime (LVM path)
# 1. new disk attached as /dev/nvme2n1 (or an existing volume was grown in the cloud)
pvcreate /dev/nvme2n1
vgextend vg0 /dev/nvme2n1
vgs                                # confirm the free space landed in the VG

# 2. grow the logical volume AND the filesystem in one step
lvextend -r -L +50G /dev/vg0/opt
df -h /opt                         # done - no unmount, no reboot

# If you grew an existing device instead of adding one:
growpart /dev/nvme1n1 1            # extend the partition to the new device size
pvresize /dev/nvme1n1p1            # let LVM see the extra space
lvextend -r -l +100%FREE /dev/vg0/opt
```

```bash
# Separate the observability stack onto its own filesystem
lvcreate -L 100G -n lv_app  vg0
lvcreate -L 50G  -n lv_obs  vg0
mkfs.xfs /dev/vg0/lv_app && mkfs.xfs /dev/vg0/lv_obs
mkdir -p /opt/app /opt/observability

# fstab by UUID, with nofail so a missing volume cannot block boot
for lv in lv_app lv_obs; do blkid /dev/vg0/$lv; done
cat >> /etc/fstab <<'EOF'
UUID=9f2c8b1d-...  /opt/app            xfs  defaults,noatime,nofail,x-systemd.device-timeout=10s 0 2
UUID=4a3e4c2b-...  /opt/observability  xfs  defaults,noatime,nofail,x-systemd.device-timeout=10s 0 2
EOF
mount -a && findmnt --verify       # ALWAYS test before rebooting
```

```bash
# "Filesystem is 50% full but cannot be written to" -> inodes
df -h /var ; df -ih /var           # blocks fine, inodes at 100%
for d in /var/*; do printf '%8d %s\n' "$(find "$d" -xdev -type f 2>/dev/null | wc -l)" "$d"; done | sort -rn | head

# "I deleted the logs and df did not change" -> deleted-but-open files
lsof +L1 | awk '$5=="REG" {print $1, $2, $7, $NF}' | sort -k3 -rn | head
# fix properly: logrotate with copytruncate, or a postrotate reload

# "Writes are failing and the mount is read-only" -> read the kernel, not the mount table
dmesg -T | grep -iE 'I/O error|read-only|EXT4-fs error|XFS.*corrupt'
findmnt -no OPTIONS /data          # confirm ro
umount /data && xfs_repair /dev/vg0/data   # only on an UNMOUNTED device
```

## Interview tips

- Draw the stack out loud - device → partition → PV → VG → LV → filesystem → mount point - and name the command at each layer. That structure answers most variants of the question.
- Define the directory-versus-mount-point difference in one line (a mount point is a directory where a _different_ filesystem is attached) and give a consequence: `df` and `du` disagree, and files hidden under a mount become invisible.
- For "add 50 GB with no downtime", give the exact sequence and emphasise `lvextend -r`, which grows the filesystem in the same step. Add `growpart` + `pvresize` for the grow-an-existing-disk variant.
- Say clearly that growing is online and **shrinking is not** - XFS cannot shrink at all, ext4 needs an unmount - so shrinking means create-copy-swap in a maintenance window.
- Volunteer the **inode exhaustion** case with `df -ih`, because "50% full but out of space" is a classic interview scenario and the answer surprises people.
- Add the deleted-but-open-file case (`lsof +L1`) as the reason `du` and `df` disagree, and give the real fix - log rotation with `copytruncate` or a reload hook.
- Treat a read-only remount as an I/O error until proven otherwise: read `dmesg`, do not just remount read-write. That instinct is what separates someone who has lost data from someone who has not.
- Always mount by **UUID** with **`nofail`** and a device timeout, and say `mount -a` before rebooting. It is the same habit that prevents the most common boot failure.
- For splitting workloads, choose separate cloud volumes in the cloud and LVM on bare metal, and mention XFS project quotas as the lighter alternative. See [what is Linux File System Hierarchy](./what-is-linux-file-system-hierarchy.md), [walk through the Linux boot process](./walk-through-the-linux-boot-process.md), [troubleshooting SSH failures, high CPU, and disk space](./how-do-you-troubleshoot-ssh-failures-high-cpu-and-disk-space-on-linux-servers.md), and [choosing between EBS, EFS, and S3](../aws-engineering/how-do-you-choose-between-ebs-efs-and-s3.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What Bash scripting exercises come up in DevOps interviews?]] (`#502`): [What Bash scripting exercises come up in DevOps interviews?](../scripting-and-automation/what-bash-scripting-exercises-come-up-in-devops-interviews.md)
- [[How do you patch hundreds of servers safely?]] (`#430`): [How do you patch hundreds of servers safely?](../configuration-management/how-do-you-patch-hundreds-of-servers-safely.md)
- [[How do you turn a pile of ad hoc scripts into maintainable automation?]] (`#302`): [How do you turn a pile of ad hoc scripts into maintainable automation?](../scripting-and-automation/how-do-you-turn-a-pile-of-ad-hoc-scripts-into-maintainable-automation.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
