---
title: "What are the basic Linux commands every DevOps engineer should know?"
id: 41
category: "Linux Administration"
difficulty: "Beginner"
tags:
  - devops
  - linux-administration
  - interview-questions
---

# What are the basic Linux commands every DevOps engineer should know?

**Short answer:** File and text handling (`ls`, `find`, `grep`, `sed`, `awk`, `tail`), process and resource inspection (`ps`, `top`, `df`, `du`, `free`, `lsof`), networking (`ss`, `curl`, `dig`, `tcpdump`), service control (`systemctl`, `journalctl`), and permissions (`chmod`, `chown`).

## Detail

**Files and text**

```bash
find /var/log -name "*.log" -mtime +7 -delete     # delete logs older than 7 days
grep -rn "ERROR" /var/log/app/ | tail -50
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head   # top client IPs
sed -i 's/old.example.com/new.example.com/g' config.ini
tail -f /var/log/app.log | grep --line-buffered "timeout"
```

**Processes and resources**

```bash
ps aux --sort=-%mem | head            # top memory consumers
top -o %CPU                           # or htop
df -h                                 # disk usage by filesystem
du -sh /var/* | sort -h | tail        # what is filling the disk
free -h                               # memory and swap
lsof -p 1234                          # files/sockets held by a process
lsof +L1                              # deleted-but-open files eating disk
```

**Networking**

```bash
ss -tulpn                             # listening sockets and owning process
curl -sS -o /dev/null -w '%{http_code} %{time_total}\n' https://example.com/health
dig +short api.example.com
traceroute api.example.com
tcpdump -i eth0 port 443 -c 100 -nn
```

**Services and permissions**

```bash
systemctl status nginx
journalctl -u nginx -f --since "10 min ago"
chmod 640 /etc/app/secret.conf && chown app:app /etc/app/secret.conf
```

## Interview tips

- Interviewers usually ask a scenario ("the disk is full, what do you do?") rather than a list - answer with the command sequence: `df -h` → `du -sh` → `lsof +L1`.
- Knowing `ss` rather than the deprecated `netstat`, and `journalctl` rather than tailing `/var/log/messages`, signals current experience.
- Mention `set -euo pipefail` when the conversation turns to scripting.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What Bash scripting exercises come up in DevOps interviews?]] (`#502`): [What Bash scripting exercises come up in DevOps interviews?](../scripting-and-automation/what-bash-scripting-exercises-come-up-in-devops-interviews.md)
- [[How do you patch hundreds of servers safely?]] (`#430`): [How do you patch hundreds of servers safely?](../configuration-management/how-do-you-patch-hundreds-of-servers-safely.md)
- [[How do you write a production-grade Bash script?]] (`#266`): [How do you write a production-grade Bash script?](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
