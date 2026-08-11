---
title: "What is systemd?"
id: 43
category: "Linux Administration"
difficulty: "Intermediate"
tags:
  - devops
  - linux-administration
  - interview-questions
---

# What is systemd?

**Short answer:** systemd is the init system and service manager on most modern Linux distributions - PID 1. It starts the system, supervises services with dependency-aware parallel startup, and provides logging, timers, resource control, and sandboxing.

## Detail

systemd manages **units**, each a declarative file:

- `.service` - a daemon or one-shot process.
- `.socket` - socket activation; systemd holds the listening socket and starts the service on first connection.
- `.timer` - a cron replacement with calendar or monotonic schedules, randomised delays, and catch-up for missed runs.
- `.target` - a grouping/synchronisation point (`multi-user.target` replaces runlevels).
- `.mount`, `.path`, `.slice` - filesystems, path watches, and cgroup resource groups.

Why it matters operationally: services get automatic restart policies, cgroup-based resource limits, and strong sandboxing options (`ProtectSystem`, `PrivateTmp`, `NoNewPrivileges`, `CapabilityBoundingSet`) that harden a daemon without touching its code. `journald` captures stdout/stderr with structured metadata, queryable by unit, boot, priority, and time.

Everyday commands: `systemctl status|start|stop|restart|enable|disable|daemon-reload`, `systemctl list-units --failed`, `journalctl -u <unit> -f`, `systemd-analyze blame` for slow boots.

## Example

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My application
After=network-online.target postgresql.service
Wants=network-online.target

[Service]
Type=notify
User=myapp
Group=myapp
WorkingDirectory=/opt/myapp
EnvironmentFile=/etc/myapp/env
ExecStart=/opt/myapp/bin/server
Restart=on-failure
RestartSec=5s
LimitNOFILE=65535

# Hardening
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
ReadWritePaths=/var/lib/myapp

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload && systemctl enable --now myapp
journalctl -u myapp -f
```

## Interview tips

- `daemon-reload` after editing a unit file is the detail people forget.
- Timers versus cron: timers give you logging, dependencies, and randomised delays - a better answer for scheduled work on a modern host.
- The sandboxing directives are a strong security answer for hardening legacy daemons.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What Bash scripting exercises come up in DevOps interviews?]] (`#502`): [What Bash scripting exercises come up in DevOps interviews?](../scripting-and-automation/what-bash-scripting-exercises-come-up-in-devops-interviews.md)
- [[How do you patch hundreds of servers safely?]] (`#430`): [How do you patch hundreds of servers safely?](../configuration-management/how-do-you-patch-hundreds-of-servers-safely.md)
- [[How do you write a production-grade Bash script?]] (`#266`): [How do you write a production-grade Bash script?](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
