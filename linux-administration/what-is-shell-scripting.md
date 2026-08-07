---
title: "What is Shell Scripting?"
id: 42
category: "Linux Administration"
difficulty: "Beginner"
tags:
  - devops
  - linux-administration
  - interview-questions
---

# What is Shell Scripting?

**Short answer:** Shell scripting is automating sequences of shell commands in a file so operational tasks are repeatable, reviewable, and runnable by anyone or anything - including CI pipelines and cron.

## Detail

Shell remains the lingua franca of operations because it is present everywhere and glues tools together with no runtime to install. The craft is in making scripts safe.

**Safety essentials**

- `set -euo pipefail` - exit on error, fail on undefined variables, and propagate failures through pipes. The single most important line in any bash script.
- Quote every variable expansion: `"$var"`, `"${array[@]}"`. Unquoted variables break on spaces and glob characters.
- `trap ... EXIT` for cleanup of temporary files and locks.
- Check preconditions early and fail with a clear message.
- Prefer `[[ ]]` over `[ ]` in bash, and `$( )` over backticks.
- Run `shellcheck` in CI - it catches the majority of real bugs.

**When to stop.** Once a script needs data structures, complex error handling, or unit tests, move to Python or Go. Roughly, past 200 lines shell becomes a liability.

## Example

```bash
#!/usr/bin/env bash
set -euo pipefail

readonly BACKUP_DIR="${BACKUP_DIR:-/var/backups}"
readonly RETENTION_DAYS=7
readonly TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

log() { printf '%s [%s] %s\n' "$(date -Is)" "$1" "${*:2}" >&2; }

require() {
  command -v "$1" >/dev/null 2>&1 || { log ERROR "missing dependency: $1"; exit 1; }
}

main() {
  require pg_dump
  require gzip

  local target="${BACKUP_DIR}/db-$(date +%Y%m%d-%H%M%S).sql.gz"
  log INFO "backing up to ${target}"

  pg_dump "$DATABASE_URL" | gzip > "${TMP}/dump.sql.gz"
  mv "${TMP}/dump.sql.gz" "$target"

  find "$BACKUP_DIR" -name 'db-*.sql.gz' -mtime "+${RETENTION_DAYS}" -delete
  log INFO "backup complete"
}

main "$@"
```

## Interview tips

- Say `set -euo pipefail` unprompted; its absence is the most common bug in production scripts.
- Writing to a temp file then `mv` (an atomic rename) avoids half-written artifacts - a nice detail.
- Have a clear threshold for when you would rewrite the script in a real language.

---

[⬅ Back to Linux Administration](./README.md) · [All topics](../README.md)
