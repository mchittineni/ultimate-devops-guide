---
title: "How do you turn a pile of ad hoc scripts into maintainable automation?"
id: 302
category: "Scripting and Automation"
difficulty: "Advanced"
tags:
  - devops
  - scripting-and-automation
  - interview-questions
---

# How do you turn a pile of ad hoc scripts into maintainable automation?

**Short answer:** Treat the automation as software, not as sysadmin residue. Inventory what exists and what runs it, delete what nothing calls, then give the survivors the same properties you demand of application code: version control with review, a pinned execution environment (a container image, not "whatever is on the box"), **idempotency and dry-run**, structured logging and non-zero exit codes, tests in CI, and a single scheduler or pipeline as the only executor. The end state is that no automation runs from an engineer's laptop or a crontab nobody owns, and every run is observable and repeatable.

## Detail

**Diagnose the actual problem, because "messy scripts" is a symptom.** The failure modes are specific: scripts on hosts and laptops instead of in Git; a script that only works because of one person's local environment or credentials; cron jobs whose failures are silent; no idempotency, so a retry causes damage; copy-paste duplication so a bug fix reaches one of five copies; hardcoded secrets; and no way to know whether a job ran at all. Each has a different fix, and the cost of the mess is measured in the risk that the one person who understands it leaves.

**Step 1 - inventory and ruthlessly delete.** Find them: `crontab -l` across hosts, systemd timers, CI job definitions, Jenkins freestyle jobs, Lambda functions, and the `scripts/` directory of every repo. Record what each does, what triggers it, who owns it, when it last ran successfully, and what breaks if it stops. A surprising fraction have not run in a year or duplicate something else - deleting those is the cheapest progress you will make, and it shrinks everything that follows.

**Step 2 - make the survivors reliable.** These properties, in priority order:

- **Idempotent.** Running twice must be safe, because unattended automation gets retried. Check-then-act, upserts instead of inserts, `mkdir -p` rather than `mkdir`, and a guard that detects work already done.
- **Dry-run by default for anything destructive.** `--dry-run` printing what would change, with an explicit `--apply` to act. This single feature is what makes people willing to trust and modify the script.
- **Fails loudly.** Non-zero exit codes, `set -euo pipefail` in Bash, no bare `except` in Python, and a failure that reaches a human - a cron job emailing a mailbox nobody reads is a silent failure.
- **Configurable, not edited.** Parameters via flags or environment variables; no hardcoded hostnames, account IDs, or paths. Secrets fetched at runtime from a secret manager, never in the file and never in the repo.
- **Structured logs and a run identifier.** JSON logs with a run ID, shipped to the same place as everything else, so "did the nightly cleanup run and what did it do" is a query rather than an SSH session.
- **Scoped blast radius.** Explicit `--limit`-style targeting, a confirmation for wide-reaching actions, and least-privilege credentials per job rather than one admin role for all automation.

**Step 3 - deduplicate into a library or a tool.** Five scripts that differ by a hostname are one parameterised script. Extract the shared logic (auth, API clients, retries, logging) into a small internal package, published and versioned like any dependency. If the collection is large, promote it into a single internal CLI - one entry point with subcommands, one place for `--help`, one install path. That is also how you stop new one-offs appearing: contributing a subcommand is easier than writing a new script from scratch.

**Step 4 - pin the execution environment.** The most common failure is "it works on my machine". Ship the automation as a container image with pinned dependencies and a pinned interpreter version, built in CI. Then the same image runs locally, in the pipeline, and in the scheduler, and the words "which Python does the box have" never come up again.

**Step 5 - one executor, and observability.** Move everything to a single scheduling and execution plane: CI/CD scheduled workflows, Kubernetes `CronJob`s, an orchestrator like Airflow or Temporal for anything with dependencies or state, or an event trigger where a schedule is the wrong model. Requirements: history, logs, retries with backoff, concurrency control (`concurrencyPolicy: Forbid` prevents overlapping runs corrupting state), timeouts, and **alerting on failure and on absence** - a job that stops running is harder to notice than a job that fails, so alert on staleness too, via a dead-man's-switch or a `job_last_success_timestamp` metric.

**Step 6 - test and review.** Unit tests for the logic, `shellcheck` and a linter in CI, and a smoke run against a non-production account on every change. Review automation like application code: it holds production credentials and it runs unattended, which arguably makes it higher-risk than the application.

**Know when to stop scripting.** A script that reconciles infrastructure toward a desired state is a worse version of Terraform, Ansible, or a Kubernetes controller. A multi-step workflow with retries, state, and human approvals is a workflow-engine job, not a Bash script with a `sleep` in it. Recognising that the right answer is "delete this and use the tool built for it" is the most valuable judgement in this whole area.

## Example

```python
#!/usr/bin/env python3
"""Snapshot cleanup - idempotent, dry-run by default, structured logs, real exit codes."""
import argparse, json, logging, sys, uuid
import boto3
from botocore.config import Config

RUN_ID = str(uuid.uuid4())

def log(event: str, **fields) -> None:
    logging.info(json.dumps({"event": event, "run_id": RUN_ID, **fields}))

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--older-than-days", type=int, default=90)
    p.add_argument("--region", default="eu-west-1")
    p.add_argument("--apply", action="store_true", help="without this, dry-run only")
    p.add_argument("--limit", type=int, default=50, help="bound the blast radius")
    args = p.parse_args()

    ec2 = boto3.client("ec2", region_name=args.region,
                       config=Config(retries={"mode": "adaptive", "max_attempts": 5}))
    stale = find_stale_snapshots(ec2, args.older_than_days)[: args.limit]
    log("selected", count=len(stale), dry_run=not args.apply)

    failures = 0
    for snap in stale:
        if not args.apply:
            log("would_delete", snapshot_id=snap["SnapshotId"], age_days=snap["age_days"])
            continue
        try:
            ec2.delete_snapshot(SnapshotId=snap["SnapshotId"])  # idempotent: 404 is success
            log("deleted", snapshot_id=snap["SnapshotId"])
        except ec2.exceptions.ClientError as exc:
            if "InvalidSnapshot.NotFound" in str(exc):
                continue                                        # already gone - fine
            failures += 1
            log("delete_failed", snapshot_id=snap["SnapshotId"], error=str(exc))

    log("finished", failures=failures)
    return 1 if failures else 0     # the scheduler needs to know

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    sys.exit(main())
```

```yaml
# One executor, pinned image, retries, no overlapping runs, and a success heartbeat.
apiVersion: batch/v1
kind: CronJob
metadata: { name: snapshot-cleanup }
spec:
  schedule: "0 3 * * *"
  concurrencyPolicy: Forbid # overlapping runs corrupt state
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 5
  startingDeadlineSeconds: 600
  jobTemplate:
    spec:
      backoffLimit: 2
      activeDeadlineSeconds: 1800 # a hung job is a failed job
      template:
        spec:
          serviceAccountName: snapshot-cleanup # least privilege, per job
          restartPolicy: Never
          containers:
            - name: cleanup
              image: ghcr.io/acme/ops-tools:1.14.2 # pinned, built in CI
              args: ["snapshots", "cleanup", "--older-than-days=90", "--apply"]
```

```promql
# Alert on failure AND on absence - a job that stops running is the quieter failure.
- alert: CronJobFailing
  expr: kube_job_status_failed{job_name=~"snapshot-cleanup.*"} > 0
  for: 5m

- alert: CronJobStale
  expr: time() - max(kube_job_status_succeeded_time{job_name=~"snapshot-cleanup.*"}) > 172800
  annotations: { summary: "snapshot-cleanup has not succeeded in 48h" }
```

```bash
# Inventory: find what you are actually dealing with, before promising anything.
for h in $(cat hosts.txt); do ssh "$h" 'crontab -l 2>/dev/null; systemctl list-timers --all'; done
find . -name '*.sh' -newermt '-365 days' | xargs -r wc -l | sort -n   # and what is stale
gh api /repos/acme/infra/actions/workflows --jq '.workflows[] | select(.state=="active") | .name'
shellcheck scripts/*.sh                                              # the cheapest quality win
```

## Interview tips

- Say "treat automation as software" and then list the properties: idempotent, dry-run, fails loudly, configurable, observable, bounded blast radius. The list is the answer.
- Start with inventory and deletion. Volunteering that a chunk of the scripts should simply be deleted signals judgement rather than enthusiasm.
- Idempotency plus dry-run is the pair to emphasise, and explain why: unattended automation gets retried, and people only modify scripts they can test safely.
- Pinning the execution environment in a container image is the concrete fix for "works on my machine". Say it explicitly.
- Alert on absence as well as on failure. Most candidates only mention failure, and a job that silently stops is the more dangerous case.
- Mention consolidating into an internal CLI or library, and that it also discourages new one-offs.
- Finish by naming the limit: reconciliation belongs in Terraform or a controller, and multi-step stateful workflows belong in a workflow engine. Knowing when to delete the script entirely is the senior answer.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you schedule work with cron and systemd timers?]] (`#497`): [How do you schedule work with cron and systemd timers?](../linux-administration/how-do-you-schedule-work-with-cron-and-systemd-timers.md)
- [[What is Shell Scripting?]] (`#42`): [What is Shell Scripting?](../linux-administration/what-is-shell-scripting.md)
- [[What is Linux File System Hierarchy?]] (`#45`): [What is Linux File System Hierarchy?](../linux-administration/what-is-linux-file-system-hierarchy.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scripting and Automation](./README.md) · [All topics](../README.md)
