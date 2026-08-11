---
title: "Walk through the Linux boot process"
id: 495
category: "Linux Administration"
difficulty: "Intermediate"
tags:
  - devops
  - linux-administration
  - interview-questions
  - incident-management
---

# Walk through the Linux boot process

**Short answer:** Six stages. **Firmware** (BIOS or UEFI) initialises hardware, runs POST, and finds a boot device - BIOS reads the MBR, UEFI reads an EFI executable from the EFI System Partition. **Bootloader** (GRUB2, or systemd-boot) presents entries and loads the **kernel** plus the **initramfs** into memory, passing the kernel command line. **Kernel** decompresses itself, initialises core subsystems and drivers, and mounts the **initramfs** as a temporary root. **initramfs** contains just enough drivers and tooling to find and mount the _real_ root filesystem - LVM, RAID, LUKS decryption, iSCSI, NFS - then pivots to it. **PID 1 (`systemd`)** starts and drives everything else: it resolves the dependency graph for the **default target** (usually `multi-user.target` on a server, `graphical.target` on a desktop), mounts filesystems from `/etc/fstab`, brings up networking, and starts units. Finally the login prompt (`getty` or a display manager) appears. The reason a DevOps engineer needs this: when an instance does not come back after a reboot, knowing which stage it died in tells you whether to look at the bootloader, the initramfs, `/etc/fstab`, or a failed unit - and `journalctl -b`, `systemd-analyze blame`, and the serial console are how you find out.

## Detail

### The stages, with what fails at each

| Stage                       | What happens                                                                                     | Typical failure and symptom                                                                                                                                                                      |
| --------------------------- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **1. Firmware** (BIOS/UEFI) | POST, hardware init, select boot device                                                          | Wrong boot order, Secure Boot rejecting an unsigned kernel/module, disk not detected. Nothing on the console beyond firmware output                                                              |
| **2. Bootloader** (GRUB2)   | Reads `/boot/grub2/grub.cfg`, shows the menu, loads kernel + initramfs, passes the command line  | Missing/corrupt `grub.cfg`, a kernel entry pointing at a deleted kernel after a bad cleanup, `/boot` full so the new initramfs was never written. You get a GRUB prompt or "no such partition"   |
| **3. Kernel**               | Decompress, init subsystems, load built-in drivers, mount initramfs                              | Missing driver for the root device, wrong `root=` UUID, kernel panic - "unable to mount root fs"                                                                                                 |
| **4. initramfs**            | Load modules for storage/network, assemble LVM/RAID, unlock LUKS, `switch_root` to the real root | The classic "dropped to the dracut/initramfs emergency shell" - the root device was not found, or LVM/LUKS did not come up                                                                       |
| **5. `systemd` (PID 1)**    | Resolve the dependency graph for the default target; mount `/etc/fstab`; start units             | **A bad `/etc/fstab` entry blocks boot** - this is the single most common self-inflicted failure. Also a failed critical unit, a network-mount timeout, or `network-online.target` never reached |
| **6. Login**                | `getty` on the console, `sshd` listening, display manager if graphical                           | System is up but `sshd` failed, or the network is up without a route so you cannot reach it                                                                                                      |

### Why `/etc/fstab` deserves its own warning

An entry that cannot be satisfied - a disk that was detached, a UUID that changed after a restore, an NFS server that is unreachable - makes systemd wait for the mount and eventually drop into **emergency mode**, which on a cloud instance means no SSH and no obvious cause. The mitigations are simple and you should name them:

- Mount by **UUID** (`blkid`) rather than `/dev/sdb1`, because device names are not stable across reboots or instance types.
- Add **`nofail`** to any non-essential mount, so a missing volume degrades instead of blocking boot.
- Add **`x-systemd.device-timeout=10s`** (and `_netdev` for network filesystems) so you fail fast rather than waiting 90 seconds per mount.
- **Test with `mount -a` before rebooting.** That one habit prevents most fstab incidents.

### `systemd` targets, and the runlevel question

systemd replaced SysV runlevels with **targets**, which are dependency groupings rather than sequential levels:

```text
poweroff.target   (0)      rescue.target       (1, single user)
multi-user.target (3)      graphical.target    (5)
reboot.target     (6)      emergency.target    (bare minimum, root FS read-only)
```

`systemctl get-default` shows the boot target and `systemctl set-default multi-user.target` changes it. The ordering model is what interviewers probe: units declare `After=`/`Before=` for ordering and `Requires=`/`Wants=` for dependencies, and systemd starts everything it can **in parallel** - which is why boot is fast and why "what starts first?" is the wrong question. Sockets and D-Bus activation let a dependent service start before its dependency is fully ready.

### The reboot question: what restarts and in what order

Asked as "when a Linux machine reboots, which stages or layers are restarted, in what order?" The clean answer is the stack above, plus the shutdown side: systemd stops units in reverse dependency order, sends `SIGTERM` then `SIGKILL` after `TimeoutStopSec` (default 90s), unmounts filesystems, and asks the kernel to reboot. A service that ignores `SIGTERM` is what makes a shutdown hang for exactly 90 seconds - a very recognisable symptom, and the reason `TimeoutStopSec` and a correct `ExecStop`/signal handler matter for anything holding state.

### Recovering a machine that will not boot

Give a path, not a panic:

1. **Read the console.** On a cloud instance that is the serial console or instance screenshot - it shows GRUB, kernel panics, and the emergency-mode prompt that SSH will never show you.
2. **From the GRUB menu**, boot the **previous kernel** (this fixes most bad-kernel-upgrade cases), or edit the entry (`e`) and append `systemd.unit=rescue.target`, or `init=/bin/bash` with `rw` for the extreme case.
3. **In the initramfs emergency shell**, check whether the root device exists (`ls /dev/mapper`, `lvm lvs`, `blkid`) - that tells you whether it is a missing module, a missing LVM volume, or a wrong `root=`.
4. **In emergency mode**, `journalctl -xb` names the failed unit or mount, and `mount -o remount,rw /` lets you fix `/etc/fstab`.
5. **Cloud escape hatch**: detach the root volume, attach it to a working instance, fix the file, reattach. This is often faster than console archaeology and is the answer worth naming for an EC2 or VM you cannot reach.
6. **Prevent it**: `mount -a` before reboots, `nofail`, keep two kernels installed, and monitor `/boot` free space.

### Cloud-init: the stage that is missing from the textbook answer

On a cloud instance there is a seventh stage that matters more than most of the others: **cloud-init** runs during boot, fetches metadata and user-data from the instance metadata service, and does the configuration - hostname, SSH keys, package installs, mounts, and your bootstrap script. So "the instance booted but is not configured / I cannot SSH in" is usually a cloud-init problem, not a boot problem, and the evidence is in `/var/log/cloud-init.log` and `/var/log/cloud-init-output.log`. Saying this is what makes the answer a DevOps answer rather than a sysadmin recital.

### Making boot fast, and measuring it

Boot time matters when it decides how quickly an autoscaling group can add capacity or how long a rolling node replacement takes. Measure with `systemd-analyze` and `systemd-analyze blame`, then fix the top offenders: disable units you do not need, avoid `network-online.target` dependencies unless genuinely required (waiting for DHCP is a common 10-30 second cost), and move work out of boot into a **baked image** so instances come up ready rather than configuring themselves. That last point connects directly to immutable infrastructure and to autoscaling health-check grace periods.

## Example

```bash
# What happened during this boot, and how long did it take?
systemd-analyze                       # Startup finished in 2.1s (kernel) + 8.4s (userspace)
systemd-analyze blame | head -10      # the units costing you the most
systemd-analyze critical-chain        # the dependency path that determined total time
journalctl -b -p err                  # errors from this boot only
journalctl -b -1 -p err               # ...and from the PREVIOUS boot (why did it reboot?)
```

```bash
# Where am I in the model?
systemctl get-default                 # multi-user.target
systemctl list-units --state=failed   # what did not start
systemctl list-dependencies multi-user.target | head -20
cat /proc/cmdline                     # the kernel command line GRUB passed
ls /boot/vmlinuz-* /boot/initramfs-*  # kernels and initramfs images present
df -h /boot                           # a full /boot silently breaks kernel updates
```

```bash
# fstab: the habits that prevent the most common boot failure
blkid /dev/nvme1n1                    # get the UUID - device names are not stable
cat >> /etc/fstab <<'EOF'
UUID=9f2c8b1d-4a3e-4c2b-9f11-8a7c6d5e4f30 /data xfs defaults,nofail,x-systemd.device-timeout=10s 0 2
EOF
mount -a                              # ALWAYS test before rebooting
systemctl daemon-reload               # systemd re-reads fstab-generated mount units
findmnt --verify                      # validate fstab syntax and targets
```

```text
GRUB recovery, from the boot menu

  1. Highlight an entry, press `e` to edit
  2. Find the `linux ... ` line and append one of:
        systemd.unit=rescue.target      -> minimal, root mounted rw, no network
        systemd.unit=emergency.target   -> bare minimum, root read-only
        init=/bin/bash rw               -> no systemd at all (last resort)
  3. Ctrl-X / F10 to boot
  4. Then:  journalctl -xb              (what failed)
            mount -o remount,rw /       (if root is read-only)
            vi /etc/fstab               (fix the entry that blocked boot)
            exec /usr/lib/systemd/systemd   (continue booting, if using init=/bin/bash)

  Cloud alternative, often faster: stop the instance, detach the root volume,
  attach it to a healthy instance, fix the file, reattach, start.
```

```bash
# The cloud-specific stage the textbook answer omits
cloud-init status --long
tail -50 /var/log/cloud-init-output.log     # your bootstrap script's stdout/stderr
journalctl -u cloud-init-local -u cloud-init -u cloud-config -u cloud-final
curl -s -H "X-aws-ec2-metadata-token: $(curl -sX PUT \
  -H 'X-aws-ec2-metadata-token-ttl-seconds: 60' \
  http://169.254.169.254/latest/api/token)" \
  http://169.254.169.254/latest/user-data | head   # what was it actually told to do?
```

## Interview tips

- Give the six stages in order and name the component at each: firmware → bootloader → kernel → initramfs → systemd (PID 1) → login. Structure is the whole answer here.
- Explain what the **initramfs** is for in one sentence - enough drivers and tooling to find and mount the real root, including LVM, RAID, and LUKS - because that is the stage most candidates cannot explain and it is where the "dropped to an emergency shell" failures happen.
- Volunteer that **a bad `/etc/fstab` entry blocks boot**, and give the three mitigations: mount by UUID, `nofail`, and `mount -a` before rebooting. This is the single most useful practical point in the topic.
- Describe systemd targets as dependency groupings rather than sequential runlevels, and say that units start in **parallel** based on `After`/`Requires` - so "what starts first" is the wrong framing.
- Cover the shutdown side too: units stopped in reverse order, `SIGTERM` then `SIGKILL` after `TimeoutStopSec`, which explains the recognisable 90-second hang when a service ignores `SIGTERM`.
- Have a recovery path ready: read the serial console, boot the previous kernel from GRUB, append `systemd.unit=rescue.target`, then `journalctl -xb`. Add the cloud escape hatch - detach the root volume, fix it from another instance, reattach - because that is often the fastest real fix.
- Add **cloud-init** as the stage that matters on a cloud instance, with `/var/log/cloud-init-output.log` as the evidence. It turns a sysadmin answer into a DevOps one.
- Close on boot time: `systemd-analyze blame`, avoiding unnecessary `network-online.target` waits, and baking the image so instances boot ready - which links to autoscaling and health-check grace periods. See [what is systemd](./what-is-systemd.md), [how do you manage services in Linux](./how-do-you-manage-services-in-linux.md), [how do you manage disks, filesystems, and LVM on Linux](./how-do-you-manage-disks-filesystems-and-lvm-on-linux.md), and [troubleshooting SSH failures, high CPU, and disk space](./how-do-you-troubleshoot-ssh-failures-high-cpu-and-disk-space-on-linux-servers.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you patch hundreds of servers safely?]] (`#430`): [How do you patch hundreds of servers safely?](../configuration-management/how-do-you-patch-hundreds-of-servers-safely.md)
- [[What Bash scripting exercises come up in DevOps interviews?]] (`#502`): [What Bash scripting exercises come up in DevOps interviews?](../scripting-and-automation/what-bash-scripting-exercises-come-up-in-devops-interviews.md)
- [[How do you turn a pile of ad hoc scripts into maintainable automation?]] (`#302`): [How do you turn a pile of ad hoc scripts into maintainable automation?](../scripting-and-automation/how-do-you-turn-a-pile-of-ad-hoc-scripts-into-maintainable-automation.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
