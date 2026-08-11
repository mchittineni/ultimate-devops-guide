---
title: "How do you troubleshoot SSH failures, high CPU, and disk space on Linux servers?"
id: 238
category: "Linux Administration"
difficulty: "Beginner"
tags:
  - devops
  - linux-administration
  - interview-questions
---

# How do you troubleshoot SSH failures, high CPU, and disk space on Linux servers?

**Short answer:** Troubleshoot SSH failures by inspecting `/var/log/auth.log` and SSH client debug output (`ssh -vvv`), CPU spikes using `top`/`htop`/`vmstat` and `kill -9`, and disk space issues using `df -h`, `du -sh *`, and log retention automation (`logrotate` / cron cleanup).

## Detail

System administrators and DevOps engineers regularly encounter three baseline Linux server production incidents:

### 1. SSH Connection Failures (`Permission denied` / `Timeout`)

- **Connection Timeout:** Check network connectivity (Security Groups, firewalls `ufw`/`iptables`, route tables, subnet NACLs), check if `sshd` process is running (`systemctl status sshd`), and verify SSH listening port (default `22`).
- **Permission Denied (publickey):** Check permissions on home directory (`700` or `755`), `.ssh` folder (`700`), and `.ssh/authorized_keys` file (`600`). If owned by incorrect user or readable by group/others, SSH daemon rejects authentication. Run verbose mode: `ssh -vvv user@server-ip`.

### 2. High CPU & Memory Consumption Troubleshooting

- **Identify Hogs:** Run `top` (press `P` to sort by CPU, `M` to sort by memory) or `htop`.
- **System Load Average:** Check `uptime` load averages over 1, 5, and 15 minutes relative to total CPU core count (`nproc`).
- **Trace Process:** Inspect thread usage with `ps -ef --sort=-%cpu | head -10`. Terminate runaway processes gracefully (`kill -15 <PID>`) or forcefully (`kill -9 <PID>`).

### 3. Disk Space Full & Log Cleanup Scripting

- **Identify Usage:** Check mounted filesystems (`df -h`) and inode consumption (`df -i`).
- **Locate Large Directories/Files:** Run `du -ah /var/log | sort -rh | head -n 20` or `find / -type f -size +100M`.
- **Deleted File Lock (Open File Handles):** If `df -h` reports 100% full but `du` cannot find files, deleted files are still held open by running processes. Check with `lsof | grep deleted` and restart the holding service.

## Example

**1. Verbose SSH Troubleshooting:**

```bash
# Client side verbose logging
ssh -vvv -i ~/.ssh/prod_key.pem ubuntu@203.0.113.45

# Server side checking permissions
ls -ld ~/.ssh
# drwx------ 2 ubuntu ubuntu 4096 Aug  7 10:00 /home/ubuntu/.ssh
ls -l ~/.ssh/authorized_keys
# -rw------- 1 ubuntu ubuntu 1200 Aug  7 10:00 /home/ubuntu/.ssh/authorized_keys
```

**2. Automated Log Maintenance Shell Script (`clean_old_logs.sh`):**

```bash
#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="/var/log/app"
DAYS_TO_KEEP=7

echo "[$(date)] Starting log cleanup in ${LOG_DIR} for files older than ${DAYS_TO_KEEP} days..."

if [ -d "${LOG_DIR}" ]; then
    # Compress logs older than 1 day that are not yet compressed
    find "${LOG_DIR}" -type f -name "*.log" -mtime +1 -exec gzip -9 {} \;

    # Delete archived logs older than DAYS_TO_KEEP
    find "${LOG_DIR}" -type f -name "*.gz" -mtime +"${DAYS_TO_KEEP}" -exec rm -f {} \;
    echo "[$(date)] Log cleanup completed successfully."
else
    echo "Directory ${LOG_DIR} does not exist!"
    exit 1
fi
```

## Interview tips

- Always mention `ssh -vvv` when asked about SSH connection issues — it pinpoints whether authentication, key exchange, or network connection failed.
- Explain the `lsof | grep deleted` scenario: interviewers love asking why `df -h` shows 100% full even after `rm -rf /var/log/huge.log`.
- Know `systemctl` commands (`systemctl status`, `journalctl -u sshd -n 50 --no-pager`) for service log inspection.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What Bash scripting exercises come up in DevOps interviews?]] (`#502`): [What Bash scripting exercises come up in DevOps interviews?](../scripting-and-automation/what-bash-scripting-exercises-come-up-in-devops-interviews.md)
- [[How do you patch hundreds of servers safely?]] (`#430`): [How do you patch hundreds of servers safely?](../configuration-management/how-do-you-patch-hundreds-of-servers-safely.md)
- [[What do you use Python for as a DevOps engineer?]] (`#267`): [What do you use Python for as a DevOps engineer?](../scripting-and-automation/what-do-you-use-python-for-as-a-devops-engineer.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
