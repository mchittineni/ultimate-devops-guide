---
title: "When do you use Bash and when do you use Python?"
id: 301
category: "Scripting and Automation"
difficulty: "Beginner"
tags:
  - devops
  - scripting-and-automation
  - interview-questions
---

# When do you use Bash and when do you use Python?

**Short answer:** Bash when the job is gluing command-line tools together on a Linux box - a handful of commands, some pipes, exit codes. Python when there is real logic: parsing JSON or YAML, calling APIs, error handling with retries, data structures, or anything another engineer will have to maintain. The practical rule of thumb: **if a Bash script passes 100 lines, needs an array of anything non-trivial, or starts parsing structured data, it wants to be Python.**

## Detail

**What Bash is genuinely good at.** Process orchestration. Running a program, checking whether it succeeded, piping its output into the next one, and moving files around. It is available on every Linux host without installing anything, it is what CI pipeline steps and container entrypoints run, and for that job nothing is more concise:

```bash
kubectl get pods -o name | grep failed | xargs -r kubectl delete
```

Nine words in Python would be twenty lines. Bash is also the right answer when the task _is_ the command line: a wrapper, a bootstrap script, a `make` target, a Dockerfile entrypoint, a git hook.

**Where Bash starts costing you.** It has no real data types (everything is a string), quoting rules that produce genuine security bugs, arithmetic that is awkward, and error handling that is opt-in - without `set -euo pipefail`, a failing command in the middle of a script is silently ignored and the script reports success. Parsing JSON with `grep` and `sed` is fragile by construction. Testing is unpleasant. And it does not run on Windows, which matters for shared tooling.

**What Python brings.** Real dictionaries and lists, exceptions and `try`/`except`, an ecosystem for the things DevOps actually does - `boto3` and the cloud SDKs, `requests`, `PyYAML`, `kubernetes`, `jinja2` - plus type hints, unit tests, and a debugger. If the script has branching logic, retries with backoff, or produces a report, Python will be shorter _and_ more reliable than the Bash equivalent, not just cleaner.

**A decision table you can say out loud:**

| Task                                            | Reach for |
| ----------------------------------------------- | --------- |
| Container entrypoint, CI step, `make` target    | Bash      |
| Chain 3-5 CLI tools, check exit codes           | Bash      |
| Log rotation, file moves, cron one-liners       | Bash      |
| Parse JSON/YAML and act on it                   | Python    |
| Call a REST API, handle pagination and retries  | Python    |
| Anything with a `for` loop over structured data | Python    |
| Produce a report, CSV, or spreadsheet           | Python    |
| Cross-platform tooling other people run         | Python    |
| Over ~100 lines, or needs tests                 | Python    |

**The middle ground worth knowing.** `jq` makes Bash competent at JSON for simple extraction, and a short Bash script calling `jq` is often the right answer where full Python would be over-engineering. Conversely, Python calling out to CLI tools via `subprocess` is completely normal - you do not have to use an SDK for everything. And "rewrite it in Python" is not automatic: a working 40-line Bash script that everyone understands should usually be left alone.

**Whichever you choose, make it safe.** Bash: `set -euo pipefail`, quote every variable expansion (`"$var"`), use `mktemp` for temporary files, `trap` for cleanup, and run `shellcheck` in CI. Python: pin dependencies, handle exceptions explicitly rather than bare `except`, log instead of printing, exit with a meaningful status code, and remember that a script running unattended in a pipeline needs to be idempotent - it will get retried.

## Example

```bash
#!/usr/bin/env bash
# Good Bash: orchestrating tools, with the safety flags that make it trustworthy.
set -euo pipefail

IMAGE="${1:?usage: deploy.sh <image>}"
NAMESPACE="${NAMESPACE:-staging}"

cleanup() { rm -f "$manifest"; }
manifest=$(mktemp)
trap cleanup EXIT

envsubst < deploy.yaml.tmpl > "$manifest"
kubectl apply -n "$NAMESPACE" -f "$manifest"
kubectl rollout status -n "$NAMESPACE" deploy/api --timeout=5m
```

```bash
# Bad Bash: parsing structured data by hand. This is the signal to switch languages.
aws ec2 describe-instances | grep InstanceId | cut -d'"' -f4 | while read id; do
  aws ec2 describe-tags --filters "Name=resource-id,Values=$id" | grep -A1 Environment | ...
done
# Fragile, unreadable, and wrong the moment the output format shifts.
```

```python
#!/usr/bin/env python3
"""The same job in Python: structured data, real error handling, testable."""
import sys
import boto3
from botocore.exceptions import ClientError

def untagged_instances(region: str) -> list[dict]:
    ec2 = boto3.client("ec2", region_name=region)
    found = []
    paginator = ec2.get_paginator("describe_instances")  # pagination handled for you
    for page in paginator.paginate(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    ):
        for reservation in page["Reservations"]:
            for inst in reservation["Instances"]:
                tags = {t["Key"]: t["Value"] for t in inst.get("Tags", [])}
                if "Environment" not in tags or "Owner" not in tags:
                    found.append({"id": inst["InstanceId"], "tags": tags})
    return found

if __name__ == "__main__":
    try:
        bad = untagged_instances("eu-west-1")
    except ClientError as exc:
        print(f"AWS call failed: {exc}", file=sys.stderr)
        sys.exit(1)
    for i in bad:
        print(f"{i['id']} missing required tags: {i['tags']}")
    sys.exit(1 if bad else 0)   # meaningful exit code for the pipeline
```

```bash
# The pragmatic middle: Bash + jq is fine for simple extraction.
aws ec2 describe-instances \
  | jq -r '.Reservations[].Instances[] | select(.Tags == null) | .InstanceId'
```

## Interview tips

- Give the rule of thumb - Bash for gluing commands, Python for logic - and then the switching triggers: 100 lines, structured data, an array, or someone else maintaining it.
- Say `set -euo pipefail` unprompted. It is the fastest way to show you have written Bash that ran in production.
- Explain that Bash has no real data types and that parsing JSON with `grep` is fragile. That is the technical reason behind the rule, not just a preference.
- Mention `shellcheck`. Interviewers notice.
- Do not be dogmatic. "Rewrite everything in Python" is as wrong as "Bash can do anything"; a working 40-line script should be left alone.
- Name `jq` as the middle ground, and note that Python calling `subprocess` is normal - you do not need an SDK for everything.
- Close on the operational point: pipeline scripts get retried, so they must be idempotent and exit with meaningful status codes.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you schedule work with cron and systemd timers?]] (`#497`): [How do you schedule work with cron and systemd timers?](../linux-administration/how-do-you-schedule-work-with-cron-and-systemd-timers.md)
- [[What are the basic Linux commands every DevOps engineer should know?]] (`#41`): [What are the basic Linux commands every DevOps engineer should know?](../linux-administration/what-are-the-basic-linux-commands-every-devops-engineer-should-know.md)
- [[What is Shell Scripting?]] (`#42`): [What is Shell Scripting?](../linux-administration/what-is-shell-scripting.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scripting and Automation](./README.md) · [All topics](../README.md)
