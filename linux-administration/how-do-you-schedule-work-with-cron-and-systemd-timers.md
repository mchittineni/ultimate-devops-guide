---
title: "How do you schedule work with cron and systemd timers?"
id: 497
category: "Linux Administration"
difficulty: "Beginner"
tags:
  - devops
  - linux-administration
  - interview-questions
  - scripting-and-automation
---

# How do you schedule work with cron and systemd timers?

**Short answer:** A **cron job** is a scheduled command, defined either in a user's crontab (`crontab -e`) or in a system file (`/etc/crontab`, `/etc/cron.d/*` - which take an extra **user** field). The schedule is five fields: **minute, hour, day-of-month, month, day-of-week**, so `0 2 * * *` is 02:00 daily and `*/15 * * * *` is every fifteen minutes. **systemd timers** do the same job with a unit file pair (`foo.service` plus `foo.timer`) and are better for anything that matters: dependency ordering, `journalctl` logging, `RandomizedDelaySec` to spread load, `Persistent=true` to catch up after downtime, resource limits, and `systemctl list-timers` to see what will run next. The three things that cause nearly every cron incident: **cron runs with a minimal environment** (a tiny `PATH`, no profile, so a script that works in your shell fails silently), **overlapping runs** when a job takes longer than its interval, and **output going nowhere** because nobody reads the mail cron tries to send. So: absolute paths, a lock, and explicit logging - or use a systemd timer, which handles two of the three for you.

## Detail

### The cron format, and where jobs live

```text
 ┌─ minute (0-59)
 │ ┌─ hour (0-23)
 │ │ ┌─ day of month (1-31)
 │ │ │ ┌─ month (1-12)
 │ │ │ │ ┌─ day of week (0-7, 0 and 7 = Sunday)
 │ │ │ │ │
 0 2 * * *   /usr/local/bin/backup.sh      # 02:00 every day
*/15 * * * * /usr/local/bin/check.sh       # every 15 minutes
 0 */6 * * * ...                           # every 6 hours
 0 9 * * 1-5 ...                           # 09:00 weekdays
 0 0 1 * *   ...                           # midnight on the 1st
@reboot      /usr/local/bin/start.sh       # once at boot
```

| Location                           | Has a user field       | Notes                                                                                                                      |
| ---------------------------------- | ---------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `crontab -e` (user crontab)        | No - runs as that user | Stored under `/var/spool/cron/`; **not** in version control unless you put it there                                        |
| `/etc/crontab`                     | **Yes**                | System-wide; convention is to leave it to the distribution                                                                 |
| `/etc/cron.d/myjob`                | **Yes**                | The right place for configuration-managed jobs - one file per job, drop-in friendly                                        |
| `/etc/cron.{hourly,daily,weekly}/` | N/A                    | Run by `run-parts`; **scripts here must have no file extension** and must be executable, which is a classic silent failure |

Note the day-of-month / day-of-week trap: if **both** are restricted (`0 0 13 * 5`), cron runs when **either** matches, not both - so that means "the 13th, and every Friday". It is the one piece of cron syntax that is genuinely counter-intuitive.

### The three things that break cron jobs

**1. The environment.** Cron gives you a near-empty environment - typically `PATH=/usr/bin:/bin`, `HOME`, `SHELL`, and nothing else. No `.bashrc`, no `.profile`, no `nvm`/`pyenv` shims, no `AWS_PROFILE`, no proxy variables. A script that runs perfectly interactively fails with "command not found" or "credentials not found". Fixes: use **absolute paths** for every binary, set `PATH=` explicitly at the top of the crontab, and source any environment file the script needs _inside_ the script. When someone says "the script works when I run it but not from cron", this is the answer nine times out of ten.

**2. Overlap.** Cron starts the job on schedule whether or not the previous run finished. A 20-minute job on a `*/15` schedule accumulates runs until the box falls over. Fix with `flock`:

```bash
*/15 * * * * /usr/bin/flock -n /var/lock/sync.lock /usr/local/bin/sync.sh
```

`-n` means "fail immediately if locked" (skip this run); use `-w 60` to wait a minute instead. Do not hand-roll a PID file - `flock` is atomic and cleans up when the process dies.

**3. Output and failure visibility.** Cron mails stdout/stderr to the user, and on a server with no MTA that mail goes nowhere - so a job that has been failing for six months looks exactly like a job that is working. Redirect explicitly to a log or the journal (`| logger -t backup`), and monitor **success**, not failure: a heartbeat/dead-man's-switch (Healthchecks.io, Cronitor, or a Prometheus push with an `absent()` alert) catches the case where the job did not run at all, which no error-based alert can.

### systemd timers, and why they are better

|                        | cron                     | systemd timer                                                            |
| ---------------------- | ------------------------ | ------------------------------------------------------------------------ |
| Definition             | One line                 | `.service` + `.timer` unit pair                                          |
| Logging                | Mail, or you redirect it | **`journalctl -u name`** automatically                                   |
| Dependencies           | None                     | `After=`, `Requires=`, `Wants=` - wait for the network or a mount        |
| Missed runs while down | Lost                     | **`Persistent=true`** runs it on next boot                               |
| Load spreading         | You stagger by hand      | **`RandomizedDelaySec=`**                                                |
| Overlap                | Needs `flock`            | A service will not start if already running                              |
| Resource limits        | No                       | `MemoryMax=`, `CPUQuota=`, `Nice=`, `IOSchedulingClass=`                 |
| Sandboxing             | No                       | `PrivateTmp=`, `ProtectSystem=`, `NoNewPrivileges=`, `User=`             |
| Visibility             | `crontab -l` per user    | **`systemctl list-timers --all`** shows next and last run for everything |
| Testing                | Wait, or run by hand     | `systemctl start name.service` runs it immediately, exactly as scheduled |

`OnCalendar=` accepts both calendar expressions (`*-*-* 02:00:00`, `Mon..Fri 09:00`, `daily`, `weekly`) and monotonic forms (`OnBootSec=`, `OnUnitActiveSec=` for "15 minutes after the last run finished", which is subtly better than "every 15 minutes" for long-running jobs). `systemd-analyze calendar 'Mon..Fri 09:00'` tells you exactly when it will next fire - a much better answer than reasoning about cron syntax in your head.

The strongest argument for timers in a DevOps context is `RandomizedDelaySec` plus dependency ordering: a fleet of 500 hosts all running `0 2 * * *` hits your artefact repository, monitoring backend, or database at exactly the same second. Timers spread that automatically, which is the same reasoning behind Jenkins's `H` in cron expressions.

### Timezones, DST, and the ambiguity nobody plans for

Cron uses the system timezone (or `CRON_TZ=` / `TZ=` in the crontab). Systems should run **UTC** and jobs should be scheduled in UTC, because under a local timezone a job at 02:30 either **runs twice** or **does not run** on DST transition days. If a job must run at a local wall-clock time, use a systemd timer with `OnCalendar=` and an explicit timezone (or `Persistent=true` so a skipped run is caught up), and make the job **idempotent** so a double run is harmless. Being able to say "we run UTC and make jobs idempotent because of DST" is a strong, specific answer.

### Writing a job that is safe to schedule

Regardless of the scheduler:

- **Idempotent**: running it twice must be harmless. Assume it will be, because retries, catch-ups, and human re-runs all happen.
- **Locked**: `flock`, or a systemd service which cannot run concurrently with itself.
- **Bounded**: a timeout (`timeout 30m ...`, or `RuntimeMaxSec=` on the unit) so a hung job does not block the next hundred runs.
- **Logged with context**: start, finish, duration, and outcome, tagged so you can find it (`logger -t jobname`).
- **Correct exit codes**: `set -euo pipefail` in Bash, and exit non-zero on failure so the scheduler and your monitoring can tell.
- **Monitored for absence**: alert when the job has _not_ succeeded recently.

### The container and Kubernetes equivalents

Do not run cron inside an application container - the container's job is one process. In Kubernetes use a **`CronJob`**, which is the same five-field syntax plus the important extras: `concurrencyPolicy: Forbid` (the `flock` equivalent), `startingDeadlineSeconds`, `backoffLimit`, `successfulJobsHistoryLimit`, and `activeDeadlineSeconds` as the timeout. On AWS, **EventBridge Scheduler** invoking a Lambda or an ECS task removes the host entirely, which also removes "the cron host was replaced and nobody noticed the jobs stopped" - a real and embarrassing incident class. See [troubleshooting a Kubernetes Job or CronJob that never completes](../kubernetes/how-do-you-troubleshoot-a-kubernetes-job-or-cronjob-that-never-completes.md).

### Debugging a job that "did not run"

Check in this order: did the scheduler fire (`journalctl -u cron`/`crond`, or `systemctl list-timers`), did the command start (log the first line), did it fail on `PATH` or credentials (run it with `env -i` to reproduce cron's environment), was it skipped by a lock, and is the host even the one you think (a replaced instance with no crontab). `run-parts --test /etc/cron.daily` shows what would run from the drop-in directories.

## Example

```bash
# A cron entry that will not surprise you: explicit env, absolute paths, lock, logging
sudo tee /etc/cron.d/db-backup <<'EOF'
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
MAILTO=""
# m  h  dom mon dow  user   command
  17 2  *   *   *    backup /usr/bin/flock -n /var/lock/db-backup.lock \
                       /usr/bin/timeout 3h /usr/local/bin/db-backup.sh \
                       2>&1 | /usr/bin/logger -t db-backup
EOF
# note: minute 17, not 0 - do not stampede shared services on the hour
```

```ini
# The systemd equivalent: logging, spreading, catch-up, limits, and sandboxing for free
# /etc/systemd/system/db-backup.service
[Unit]
Description=Nightly database backup
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=backup
ExecStart=/usr/local/bin/db-backup.sh
RuntimeMaxSec=3h                 # hard timeout
Nice=10
IOSchedulingClass=idle           # do not fight production I/O
MemoryMax=1G
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/var/backups
NoNewPrivileges=true
```

```ini
# /etc/systemd/system/db-backup.timer
[Unit]
Description=Run the nightly database backup

[Timer]
OnCalendar=*-*-* 02:00:00        # UTC, because the host runs UTC
RandomizedDelaySec=1800          # spread 500 hosts over 30 minutes
Persistent=true                  # if the host was down at 02:00, run on next boot
AccuracySec=1min
Unit=db-backup.service

[Install]
WantedBy=timers.target
```

```bash
# Operate it
systemctl daemon-reload
systemctl enable --now db-backup.timer
systemctl list-timers --all | grep db-backup   # NEXT, LEFT, LAST, PASSED - all visible
systemctl start db-backup.service              # test it now, exactly as it will run
journalctl -u db-backup.service -n 50 --no-pager
systemd-analyze calendar 'Mon..Fri 09:00'      # when will this actually fire?
```

```bash
# Debugging "it works by hand but not from cron"
env -i /bin/bash --noprofile --norc -c '/usr/local/bin/db-backup.sh'   # reproduce cron's env
journalctl -u crond --since -1d | grep db-backup     # did cron even fire it?
grep -r CRON /var/log/syslog | tail                   # Debian/Ubuntu
run-parts --test /etc/cron.daily                      # what would run from the drop-ins
crontab -l -u backup                                  # per-user crontabs are easy to forget

# The alert that matters: absence of success, not presence of failure
#   Prometheus:  time() - node_systemd_timer_last_trigger_seconds{name="db-backup.timer"} > 90000
#   or a dead-man's-switch ping at the end of a successful run
```

## Interview tips

- Give the five cron fields in order without hesitating, then a couple of real expressions (`0 2 * * *`, `*/15 * * * *`, `0 9 * * 1-5`). Add `@reboot` as the special form.
- Volunteer the day-of-month / day-of-week **OR** behaviour when both are set. It is the one syntax subtlety interviewers use to separate people who have read the man page from people who have not.
- Name the three classic failures - minimal environment, overlapping runs, invisible output - and the fixes: absolute paths and an explicit `PATH`, `flock -n`, and explicit logging plus a heartbeat alert. "It works by hand but not from cron" should get the environment answer instantly.
- Say you monitor for **absence of success** rather than for failure, because a job that never ran produces no error. That is the most senior point in this answer.
- Compare systemd timers on the axes that matter: journal logging, dependency ordering, `Persistent=true` for missed runs, `RandomizedDelaySec` to stop 500 hosts stampeding, resource limits, and `systemctl list-timers` for visibility.
- Mention `OnUnitActiveSec=` as "N after the last run finished", which avoids overlap by construction, and `systemd start <service>` as the way to test a scheduled job immediately.
- Raise UTC and DST: schedule in UTC, keep jobs idempotent, and note that a 02:30 local job either runs twice or is skipped on transition days.
- Note the drop-in directory gotcha - scripts in `/etc/cron.daily` must be executable and have **no extension** - and that `/etc/cron.d` files need a user field while a user crontab does not.
- Close with the modern equivalents: a Kubernetes `CronJob` with `concurrencyPolicy: Forbid`, or EventBridge Scheduler invoking Lambda/ECS so there is no cron host to lose. See [what is systemd](./what-is-systemd.md), [how do you manage services in Linux](./how-do-you-manage-services-in-linux.md), [writing a production-grade Bash script](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md), and [troubleshooting a Kubernetes Job or CronJob that never completes](../kubernetes/how-do-you-troubleshoot-a-kubernetes-job-or-cronjob-that-never-completes.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What Bash scripting exercises come up in DevOps interviews?]] (`#502`): [What Bash scripting exercises come up in DevOps interviews?](../scripting-and-automation/what-bash-scripting-exercises-come-up-in-devops-interviews.md)
- [[How do you patch hundreds of servers safely?]] (`#430`): [How do you patch hundreds of servers safely?](../configuration-management/how-do-you-patch-hundreds-of-servers-safely.md)
- [[What do you use Python for as a DevOps engineer?]] (`#267`): [What do you use Python for as a DevOps engineer?](../scripting-and-automation/what-do-you-use-python-for-as-a-devops-engineer.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
