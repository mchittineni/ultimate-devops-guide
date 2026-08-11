---
title: "How do you manage services in Linux?"
id: 44
category: "Linux Administration"
difficulty: "Beginner"
tags:
  - devops
  - linux-administration
  - interview-questions
---

# How do you manage services in Linux?

**Short answer:** With `systemctl` on modern distributions - start, stop, restart, reload, enable, and disable units - plus `journalctl` for their logs, and unit files under `/etc/systemd/system` for configuration.

## Detail

**Lifecycle commands**

```bash
systemctl start nginx        # start now
systemctl stop nginx         # stop now
systemctl restart nginx      # stop then start (drops connections)
systemctl reload nginx       # re-read config without dropping connections
systemctl enable nginx       # start at boot
systemctl disable nginx      # do not start at boot
systemctl enable --now nginx # both
systemctl mask nginx         # prevent it starting at all, even as a dependency
```

**Inspection**

```bash
systemctl status nginx           # state, PID, recent log lines, cgroup tree
systemctl is-active nginx        # scriptable check
systemctl list-units --failed    # what is broken right now
systemctl cat nginx              # effective unit definition
systemctl show nginx -p Restart  # a single resolved property
```

**Modifying without editing the vendor file:** use a drop-in, so package upgrades do not overwrite your change.

```bash
systemctl edit nginx     # creates /etc/systemd/system/nginx.service.d/override.conf
```

**Logs**

```bash
journalctl -u nginx -f                      # follow
journalctl -u nginx --since "1 hour ago" -p err
journalctl -u nginx -b -1                   # previous boot
```

Older systems use SysV init (`service nginx start`, `chkconfig`), and containers invert the model entirely - the orchestrator, not systemd, supervises the process.

## Interview tips

- `reload` versus `restart` is a common trap: reload preserves connections where the daemon supports it.
- Drop-in overrides (`systemctl edit`) are the correct way to customise packaged units.
- Mention `mask` - the answer when a service keeps coming back because something depends on it.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What Bash scripting exercises come up in DevOps interviews?]] (`#502`): [What Bash scripting exercises come up in DevOps interviews?](../scripting-and-automation/what-bash-scripting-exercises-come-up-in-devops-interviews.md)
- [[How do you patch hundreds of servers safely?]] (`#430`): [How do you patch hundreds of servers safely?](../configuration-management/how-do-you-patch-hundreds-of-servers-safely.md)
- [[How do you write a production-grade Bash script?]] (`#266`): [How do you write a production-grade Bash script?](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
