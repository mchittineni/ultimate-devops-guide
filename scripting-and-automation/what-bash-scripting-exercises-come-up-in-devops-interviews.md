---
title: "What Bash scripting exercises come up in DevOps interviews?"
id: 502
category: "Scripting and Automation"
difficulty: "Intermediate"
tags:
  - devops
  - scripting-and-automation
  - interview-questions
  - linux-administration
---

# What Bash scripting exercises come up in DevOps interviews?

**Short answer:** The same eight tasks, in different clothing: **delete or archive files older than N days**, **alert when disk usage crosses a threshold**, **check a service and restart it if it is down**, **count or extract patterns from a log**, **rename or move files with a date stamp**, **find and replace text in a file**, **watch a directory for new files**, and **rotate or compress logs on a schedule**. What is being tested is rarely the algorithm - it is whether you write a script someone can run in production: `set -euo pipefail` at the top, quoted variables, `mktemp` instead of a hard-coded `/tmp` path, `find -print0 | xargs -0` instead of parsing `ls`, a `trap` for cleanup, `flock` so cron cannot run two copies, meaningful exit codes, and logging that says what happened. Write the safe version, say why each guard is there, and volunteer the failure mode you are preventing - that is what separates a candidate from a copy-paste answer.

## Detail

### The habits that earn the marks

```bash
#!/usr/bin/env bash
set -euo pipefail        # -e exit on error, -u error on unset var, -o pipefail catch pipe failures
IFS=$'\n\t'              # stop word-splitting on spaces
```

- **`set -euo pipefail`** is the single most recognisable signal of a production script. Without `pipefail`, `cmd_that_fails | wc -l` returns success. Without `-u`, a typo in a variable name silently becomes an empty string - and `rm -rf "$PREFXI/data"` becomes `rm -rf /data`.
- **Quote every expansion**: `"$file"`, `"${arr[@]}"`. Unquoted variables break on spaces and glob characters, which is how a filename with a space deletes the wrong thing.
- **Never parse `ls`.** Use `find -print0` with `xargs -0`, or `find -exec`, or a `while IFS= read -r -d ''` loop, so newlines and spaces in filenames are safe.
- **`mktemp`** for temporary files and directories, plus a `trap ... EXIT` to remove them - a predictable `/tmp/foo.$$` path is a symlink-attack vector and leaks on failure.
- **`flock`** if the script is scheduled, so a slow run does not overlap the next one.
- **Absolute paths or an explicit `PATH`**, because cron's environment is nearly empty.
- **Exit codes that mean something** (0 success, non-zero per failure class) so the scheduler and your monitoring can react.
- **Dry-run first**: a `--dry-run` flag, or `echo` before `rm`, on anything destructive. Say this out loud when writing a delete script - interviewers are watching for whether you are casual about `rm -rf`.
- **`shellcheck`** in CI. Mentioning it shows you treat scripts as code.
- Know when to stop: beyond a few hundred lines, or once you need data structures, JSON, or API calls with error handling, **switch to Python**. See [when do you use Bash and when do you use Python](./when-do-you-use-bash-and-when-do-you-use-python.md).

### The exercises, and the trap in each

| Exercise                       | The trap they are checking for                                                                                                 |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| Delete files older than N days | Using `ls` or `rm -rf` unguarded; forgetting `-type f`; not restricting to one filesystem (`-xdev`); no dry run                |
| Disk usage alert               | Parsing `df` fragilely; comparing a string with `%` as a number; alerting every minute with no de-duplication                  |
| Service check and restart      | Using `ps` piped to `grep` instead of `systemctl is-active`; restarting in a loop with no backoff or attempt limit; no logging |
| Count pattern occurrences      | `grep -c` counts **lines**, not occurrences - pipe `grep -o` into `wc -l` when you need occurrences                            |
| Rename with a date             | Unquoted filenames; clobbering an existing target; assuming the extension                                                      |
| Find and replace               | `sed -i` without a backup, and on a symlink it replaces the link with a regular file                                           |
| Watch a directory              | Polling in a tight loop instead of `inotifywait`; no state file, so a restart re-reports everything                            |
| Log rotation and compression   | Reinventing `logrotate`; truncating a file a process still holds open, so space is not reclaimed                               |

### Reference solutions

**Delete files older than 30 days, safely:**

```bash
#!/usr/bin/env bash
set -euo pipefail
DIR=${1:?usage: $0 <dir> [days] [--dry-run]}
DAYS=${2:-30}
DRY=${3:-}

[[ -d $DIR ]] || { echo "not a directory: $DIR" >&2; exit 2; }

# -xdev: never cross into another filesystem.  -print0/-0: safe with spaces and newlines.
if [[ $DRY == --dry-run ]]; then
  find "$DIR" -xdev -type f -mtime "+$DAYS" -print
else
  find "$DIR" -xdev -type f -mtime "+$DAYS" -print0 \
    | xargs -0 --no-run-if-empty rm -v -- \
    | logger -t cleanup -s
fi
```

**Disk usage alert above 80%:**

```bash
#!/usr/bin/env bash
set -euo pipefail
THRESHOLD=${THRESHOLD:-80}
LOG=/var/log/disk-alert.log
ALERT_TO=${ALERT_TO:-ops@example.com}

# read df line by line; strip the % so the comparison is numeric
df -hP --output=pcent,target -x tmpfs -x devtmpfs | tail -n +2 | while read -r pcent mount; do
  used=${pcent%\%}; used=${used// /}
  if (( used >= THRESHOLD )); then
    msg="$(date -Is) DISK ${mount} at ${used}% (threshold ${THRESHOLD}%)"
    printf '%s\n' "$msg" | tee -a "$LOG"
    du -xh --max-depth=1 "$mount" 2>/dev/null | sort -h | tail -5 | tee -a "$LOG"  # what is eating it
    printf '%s\n' "$msg" | mail -s "Disk alert on $(hostname -s): $mount" "$ALERT_TO" || true
  fi
done
```

**Check a service, restart it if down, log the event:**

```bash
#!/usr/bin/env bash
set -euo pipefail
SERVICE=${1:?usage: $0 <service>}
MAX=3

log() { printf '%s %s\n' "$(date -Is)" "$*" | logger -t svc-watch -s; }

if systemctl is-active --quiet "$SERVICE"; then
  exit 0                                   # healthy: say nothing, exit clean
fi

log "WARN $SERVICE is not active; attempting restart"
for i in $(seq 1 "$MAX"); do
  if systemctl restart "$SERVICE"; then
    sleep 5
    if systemctl is-active --quiet "$SERVICE"; then
      log "INFO $SERVICE restarted successfully on attempt $i"
      exit 0
    fi
  fi
  sleep $(( i * 5 ))                       # backoff, do not hammer
done

log "ERROR $SERVICE failed to restart after $MAX attempts"
journalctl -u "$SERVICE" -n 30 --no-pager | logger -t svc-watch
exit 1                                     # non-zero so monitoring notices
```

Say the caveat out loud: for a systemd service, `Restart=on-failure` with `RestartSec` and `StartLimitBurst` does this natively and better. A watchdog script is for things systemd does not manage.

**Log analysis - lines, occurrences, top offenders:**

```bash
#!/usr/bin/env bash
set -euo pipefail
FILE=${1:?usage: $0 <logfile> [pattern]}
PAT=${2:-ERR}

wc -l < "$FILE"                                    # total lines
grep -c -- "$PAT" "$FILE" || true                  # lines CONTAINING the pattern
grep -o -- "$PAT" "$FILE" | wc -l                  # OCCURRENCES (may be >1 per line)

# top 10 error messages, normalised so IDs do not fragment the count
grep -- "$PAT" "$FILE" \
  | sed -E 's/[0-9a-f]{8,}/<id>/g; s/[0-9]+/<n>/g' \
  | awk -F'ERR' '{print $2}' | sort | uniq -c | sort -rn | head -10

# alert when the SAME message repeats more than 3 times
awk '/ERROR/ { c[$0]++ } END { for (m in c) if (c[m] > 3) printf "[ALERT] %dx %s\n", c[m], m }' "$FILE"

# unique IPs and how many there are
grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}' "$FILE" | sort -u | tee /dev/stderr | wc -l
```

**Rename `.txt` files with today's date, and find-and-replace:**

```bash
#!/usr/bin/env bash
set -euo pipefail
DIR=${1:-.}
STAMP=$(date +%F)

find "$DIR" -maxdepth 1 -type f -name '*.txt' -print0 |
while IFS= read -r -d '' f; do
  base=$(basename "$f" .txt)
  target="$DIR/${base}_${STAMP}.txt"
  [[ -e $target ]] && { echo "skip (exists): $target" >&2; continue; }   # never clobber
  mv -n -- "$f" "$target"
done

# find and replace, with a backup, following symlinks rather than replacing them
sed -i.bak --follow-symlinks 's/old-hostname/new-hostname/g' /etc/app/config.conf
diff /etc/app/config.conf{.bak,} || true
```

**Watch a directory for new files:**

```bash
#!/usr/bin/env bash
set -euo pipefail
DIR=${1:?usage: $0 <dir>}

# event-driven: no polling, no missed files
if command -v inotifywait >/dev/null; then
  inotifywait -m -e close_write,moved_to --format '%f' "$DIR" | while read -r f; do
    printf '%s new: %s\n' "$(date -Is)" "$f"
    scp -q -- "$DIR/$f" backup@remote:/incoming/ && echo "shipped: $f"
  done
else
  # fallback: a STATE FILE, so a restart does not re-report everything
  STATE=$(mktemp -t seen.XXXXXX); trap 'rm -f "$STATE"' EXIT
  find "$DIR" -maxdepth 1 -type f -printf '%f\n' | sort > "$STATE"
  while sleep 60; do
    find "$DIR" -maxdepth 1 -type f -printf '%f\n' | sort > "$STATE.new"
    comm -13 "$STATE" "$STATE.new" | sed "s/^/$(date -Is) new: /"
    mv "$STATE.new" "$STATE"
  done
fi
```

**Compress logs older than 30 days, delete older than 90, run daily:**

```bash
#!/usr/bin/env bash
set -euo pipefail
LOGDIR=/var/log/app

find "$LOGDIR" -xdev -type f -name '*.log' -mtime +30 ! -name '*.gz' -print0 \
  | xargs -0 --no-run-if-empty gzip -9
find "$LOGDIR" -xdev -type f -name '*.log.gz' -mtime +90 -print0 \
  | xargs -0 --no-run-if-empty rm -v --

# schedule it - and note that logrotate already does all of this properly
# /etc/cron.d/app-logs
#   17 3 * * * root /usr/bin/flock -n /var/lock/app-logs /usr/local/bin/rotate-logs.sh
```

## Example

```bash
#!/usr/bin/env bash
# The template worth memorising: every guard, in order, with a reason.
set -euo pipefail

readonly SCRIPT_NAME=${0##*/}
readonly LOCK=/var/lock/${SCRIPT_NAME}.lock
TMPDIR_LOCAL=$(mktemp -d)                  # never a predictable /tmp path
trap 'rc=$?; rm -rf "$TMPDIR_LOCAL"; exit $rc' EXIT INT TERM   # cleanup on any exit

log()  { printf '%s [%s] %s\n' "$(date -Is)" "$1" "${*:2}" | logger -t "$SCRIPT_NAME" -s; }
die()  { log ERROR "$*"; exit 1; }
usage() { cat <<EOF
usage: $SCRIPT_NAME [-d DAYS] [-t THRESHOLD] [-n] TARGET
  -n  dry run
EOF
exit 2; }

DAYS=30 THRESHOLD=80 DRY=false
while getopts ':d:t:nh' opt; do
  case $opt in
    d) DAYS=$OPTARG ;; t) THRESHOLD=$OPTARG ;; n) DRY=true ;;
    h|*) usage ;;
  esac
done
shift $((OPTIND - 1))
TARGET=${1:-} ; [[ -n $TARGET ]] || usage
[[ -d $TARGET ]] || die "not a directory: $TARGET"

# one instance only - the script is on a cron schedule
exec 9>"$LOCK" || die "cannot open lock"
flock -n 9 || { log WARN "another run holds the lock; exiting"; exit 0; }

command -v find >/dev/null || die "find not found; check PATH"

log INFO "starting: target=$TARGET days=$DAYS dry_run=$DRY"
count=0
while IFS= read -r -d '' f; do
  if $DRY; then log INFO "would remove: $f"
  else rm -f -- "$f" && log INFO "removed: $f"
  fi
  (( ++count ))
done < <(find "$TARGET" -xdev -type f -mtime "+$DAYS" -print0)

log INFO "finished: $count file(s) processed"
```

```bash
# Prove it before shipping it
shellcheck -x cleanup.sh          # catches unquoted vars, useless cat, subshell bugs
bash -n cleanup.sh                # syntax only
bash -x cleanup.sh -n /tmp/test   # trace what it does, in dry-run mode
env -i /bin/bash --noprofile --norc ./cleanup.sh -n /tmp/test   # reproduce cron's environment
```

## Interview tips

- Write `#!/usr/bin/env bash` and `set -euo pipefail` before anything else, then say what each flag prevents - especially that without `pipefail` a failing command in a pipeline reports success, and without `-u` a typo'd variable becomes an empty string in an `rm` path.
- Quote every expansion and use `find -print0 | xargs -0`. Say "never parse `ls`" - it is a shibboleth, and the reason (spaces and newlines in filenames) matters.
- On any destructive script, volunteer a **dry-run** and `-xdev`. Being visibly careful with `rm -rf` is scored, and being casual with it is remembered.
- For the disk-alert exercise, strip the `%` before comparing numerically and add the `du` output showing _what_ is filling the disk - that turns an alert into something actionable.
- For the service watchdog, use `systemctl is-active` (not `ps | grep`), add backoff and an attempt limit, log the outcome, exit non-zero on failure - and then say that `Restart=on-failure` in the unit does this natively, so the script is for unmanaged processes.
- Know that `grep -c` counts **lines** and `grep -o | wc -l` counts **occurrences**. Interviewers use this to check whether you read output carefully.
- Mention `flock` for anything on a schedule, `mktemp` plus a `trap` for temporary files, and an explicit `PATH` because cron's environment is nearly empty.
- Say `shellcheck` runs in CI, and say where you would stop using Bash - once you need JSON, data structures, or API error handling, it is Python. Recognising the boundary is a senior signal. See [how do you write a production-grade Bash script](./how-do-you-write-a-production-grade-bash-script.md), [analysing logs with grep, awk, and sed](../linux-administration/how-do-you-analyse-logs-and-text-files-with-grep-awk-and-sed.md), [scheduling work with cron and systemd timers](../linux-administration/how-do-you-schedule-work-with-cron-and-systemd-timers.md), and [what Python exercises come up in DevOps interviews](./what-python-exercises-come-up-in-devops-interviews.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you schedule work with cron and systemd timers?]] (`#497`): [How do you schedule work with cron and systemd timers?](../linux-administration/how-do-you-schedule-work-with-cron-and-systemd-timers.md)
- [[What are the basic Linux commands every DevOps engineer should know?]] (`#41`): [What are the basic Linux commands every DevOps engineer should know?](../linux-administration/what-are-the-basic-linux-commands-every-devops-engineer-should-know.md)
- [[What is Shell Scripting?]] (`#42`): [What is Shell Scripting?](../linux-administration/what-is-shell-scripting.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scripting and Automation](./README.md) · [All topics](../README.md)
