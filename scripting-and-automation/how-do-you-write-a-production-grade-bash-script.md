---
title: "How do you write a production-grade Bash script?"
id: 266
category: "Scripting and Automation"
difficulty: "Intermediate"
tags:
  - devops
  - scripting-and-automation
  - interview-questions
---

# How do you write a production-grade Bash script?

**Short answer:** Start with `set -euo pipefail` so failures stop the script instead of cascading, quote every variable expansion, use a `trap` to clean up on exit, validate inputs and required commands before doing any work, and make the script idempotent so re-running it is safe. Lint it with `shellcheck`. Know when to stop - once you need data structures, HTTP clients, or real error handling, switch to Python.

## Detail

**`set -euo pipefail` is the first line of every serious script,** and interviewers ask what each part does:

- `-e` - exit immediately if any command returns non-zero. Without it a failed `cd` is followed cheerfully by `rm -rf *` in the wrong directory.
- `-u` - error on an undefined variable. This is what stops `rm -rf "$PREFIX/"` from becoming `rm -rf /` when `PREFIX` is unset.
- `-o pipefail` - a pipeline returns the first non-zero status rather than the status of the last command. Without it, `curl bad-url | jq .` reports success because `jq` succeeded.

Know `-e`'s limits: it does not fire inside conditions, `&&`/`||` chains, or most function calls used in a test. Explicit error checks still matter.

**Quoting is where real bugs live.** `$var` unquoted is subject to word splitting and glob expansion, so a filename with a space becomes two arguments. Quote everything: `"$var"`, `"$@"` (never `$*`), `"${array[@]}"`. Use `"${var:?message}"` to fail loudly on a required variable and `"${var:-default}"` to supply a fallback.

**`&` vs `&&` - a question asked verbatim.** A single `&` backgrounds the command and returns immediately; `&&` runs the next command only if the previous one succeeded. Similarly `|` pipes stdout while `||` runs on failure.

**`trap` for cleanup.** Temporary files, lock files, and port-forwards must be removed whether the script succeeds, fails, or is interrupted. `trap cleanup EXIT` covers normal and error exits; add `INT TERM` to handle Ctrl-C and termination signals.

**Idempotency.** Automation gets re-run - by a retry, by a nervous operator, by a pipeline. Check before you create (`mkdir -p`, `[[ -f ... ]]`), make deletions tolerant (`rm -f`), and prefer declarative tools where you can. "Can I run this twice safely?" is a standard follow-up.

**Fail fast on preconditions.** Verify required commands exist (`command -v kubectl >/dev/null || die "kubectl not found"`), required variables are set, and arguments are valid - before mutating anything. A script that fails halfway through is worse than one that refuses to start.

**Other habits worth naming:** use `[[ ]]` rather than `[ ]` in Bash; use `$( )` not backticks; write functions with `local` variables; log to stderr so stdout stays parseable; use `mktemp` rather than a hardcoded `/tmp` path; and run `shellcheck` in CI - it catches the quoting bugs above automatically.

**Know when Bash is the wrong tool.** Bash is excellent glue for calling other programs. It is poor at JSON, arithmetic, error handling, and anything with nested data. The honest interview answer is: Bash for a hundred lines of orchestration, Python beyond that.

## Example

```bash
#!/usr/bin/env bash
# Promote a container image to an environment. Safe to re-run.
set -euo pipefail

readonly SCRIPT_NAME="${0##*/}"
readonly LOG_PREFIX="[${SCRIPT_NAME}]"

log()  { printf '%s %s\n' "$LOG_PREFIX" "$*" >&2; }   # stderr keeps stdout clean
die()  { log "ERROR: $*"; exit 1; }

usage() {
  cat >&2 <<EOF
Usage: ${SCRIPT_NAME} --env <staging|production> --image <tag>
EOF
  exit 64
}

# --- cleanup runs on success, failure, and Ctrl-C -------------------------
TMPDIR_LOCAL="$(mktemp -d)"
cleanup() {
  local rc=$?
  rm -rf "$TMPDIR_LOCAL"
  [[ $rc -ne 0 ]] && log "failed with exit code $rc"
  return $rc
}
trap cleanup EXIT INT TERM

# --- preconditions before any mutation ------------------------------------
for cmd in kubectl jq; do
  command -v "$cmd" >/dev/null 2>&1 || die "required command not found: $cmd"
done

ENVIRONMENT=""
IMAGE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)   ENVIRONMENT="${2:-}"; shift 2 ;;
    --image) IMAGE="${2:-}";       shift 2 ;;
    -h|--help) usage ;;
    *) die "unknown argument: $1" ;;
  esac
done

[[ -n "$ENVIRONMENT" ]] || usage
[[ -n "$IMAGE" ]]       || usage
[[ "$ENVIRONMENT" =~ ^(staging|production)$ ]] || die "invalid env: $ENVIRONMENT"

: "${KUBE_CONTEXT:?KUBE_CONTEXT must be set}"

# --- idempotent: setting the same image twice is a no-op -------------------
log "promoting ${IMAGE} to ${ENVIRONMENT}"
kubectl --context "$KUBE_CONTEXT" -n "$ENVIRONMENT" \
  set image deployment/api "api=${IMAGE}" --record=false

if ! kubectl --context "$KUBE_CONTEXT" -n "$ENVIRONMENT" \
     rollout status deployment/api --timeout=5m; then
  log "rollout failed - rolling back"
  kubectl --context "$KUBE_CONTEXT" -n "$ENVIRONMENT" rollout undo deployment/api
  die "promotion to ${ENVIRONMENT} failed and was rolled back"
fi

log "promoted ${IMAGE} to ${ENVIRONMENT} successfully"
```

```bash
shellcheck promote.sh          # run this in CI, not just locally
bash -n promote.sh             # syntax check without executing
bash -x promote.sh --env staging --image api:1.4.0   # trace execution
```

## Interview tips

- Open with `set -euo pipefail` and explain all three parts separately. It is the fastest way to signal you write scripts that run unattended.
- "What is the difference between `&` and `&&`?" is asked literally. Background versus conditional-on-success.
- Idempotency comes up as "what if this runs twice?" Have a concrete answer - `mkdir -p`, existence checks, declarative `kubectl apply`.
- Mention `trap ... EXIT` for cleanup. Very few candidates do, and it is exactly what separates a script from a one-off command.
- Name `shellcheck`. Saying it runs in CI is better than saying you use it.
- Be willing to say Bash is the wrong tool past a certain point. Interviewers respect the boundary more than a 600-line Bash program.
- If asked to write something live - "back up a directory to S3", "delete files older than 7 days" - narrate the guard rails first, then the logic.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you schedule work with cron and systemd timers?]] (`#497`): [How do you schedule work with cron and systemd timers?](../linux-administration/how-do-you-schedule-work-with-cron-and-systemd-timers.md)
- [[What are the basic Linux commands every DevOps engineer should know?]] (`#41`): [What are the basic Linux commands every DevOps engineer should know?](../linux-administration/what-are-the-basic-linux-commands-every-devops-engineer-should-know.md)
- [[What is Shell Scripting?]] (`#42`): [What is Shell Scripting?](../linux-administration/what-is-shell-scripting.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scripting and Automation](./README.md) · [All topics](../README.md)
