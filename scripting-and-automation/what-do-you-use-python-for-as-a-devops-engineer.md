---
title: "What do you use Python for as a DevOps engineer?"
id: 267
category: "Scripting and Automation"
difficulty: "Intermediate"
tags:
  - devops
  - scripting-and-automation
  - interview-questions
---

# What do you use Python for as a DevOps engineer?

**Short answer:** Everything Bash is bad at - cloud API automation with `boto3` or the Azure/Google SDKs, parsing and reshaping JSON and YAML, custom Kubernetes controllers and operators, glue between systems that only speak HTTP, and internal CLI tooling. Interviews pair the "what do you use it for" question with two or three language fundamentals: list vs tuple, shallow vs deep copy, and the GIL.

## Detail

**Where Python earns its place.** Bash shells out to other programs; Python calls APIs, handles structured data, retries with backoff, and produces useful errors. Typical DevOps uses:

- **Cloud automation** - `boto3` for AWS (tag audits, snapshot lifecycle, cost reports, cleaning orphaned volumes), `azure-identity`/`azure-mgmt-*`, `google-cloud-*`.
- **Data reshaping** - transforming a Terraform plan JSON, a Trivy report, or a Prometheus query result into something a pipeline can gate on.
- **Kubernetes tooling** - the official `kubernetes` client, or `kopf` for writing operators when a controller in Go is more than you need.
- **Lambda / Cloud Functions** - event-driven automation such as auto-remediation of non-compliant resources.
- **Internal CLIs** - `click` or `typer` for the golden-path tooling a platform team ships.
- **Ansible modules** - Ansible itself is Python, so custom modules and filters are Python.

**Use the SDK, not a shell-out.** Calling `subprocess.run(["aws", "s3", ...])` and parsing the text output is fragile; `boto3` gives you typed responses, pagination, and retries. Always use paginators - `list_objects_v2` and friends silently truncate at 1000 results, which is a real production bug and an occasional interview trap.

**The language fundamentals that get asked:**

- **List vs tuple** - lists are mutable, tuples are immutable and hashable, so a tuple can be a dict key or set member. Tuples are marginally faster and signal "this will not change". The practical answer: tuples for fixed records, lists for collections you mutate.
- **Shallow vs deep copy** - `copy.copy()` copies the outer object but shares the nested objects; `copy.deepcopy()` recursively copies everything. This bites when copying a nested config dict, mutating the copy, and finding the original changed too. Note `dict.copy()` and slicing are both shallow.
- **The GIL** - CPython's Global Interpreter Lock allows only one thread to execute Python bytecode at a time, so threads do not give you CPU parallelism. They _do_ help with I/O-bound work, because the lock is released during I/O waits - which is most DevOps work. For CPU-bound work use `multiprocessing` or a native extension. (Recent CPython releases ship an experimental free-threaded build, but assume the GIL applies unless told otherwise.)
- **Mutable default arguments** - `def f(items=[])` shares one list across every call. Use `None` and create inside.
- **Generators** - `yield` streams items lazily instead of building a list in memory. The correct answer to "how would you process a 10 GB log file in Python."
- **Context managers** - `with open(...)` guarantees cleanup; the same pattern applies to locks and connections.
- **Virtual environments and pinning** - `venv` plus a lock file (`pip-tools`, `poetry`, or `uv`). Unpinned dependencies in automation is the failure interviewers probe for.

**Error handling is the difference between a script and a tool.** Catch specific exceptions (`ClientError`, not bare `except:`), retry transient failures with exponential backoff and jitter, log with the `logging` module rather than `print`, and exit with meaningful codes so a pipeline can branch on them.

## Example

```python
#!/usr/bin/env python3
"""Report EBS volumes that are unattached and older than N days."""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timedelta, timezone

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

log = logging.getLogger("ebs-audit")

# Adaptive retries handle throttling without a hand-rolled backoff loop.
BOTO_CONFIG = Config(retries={"max_attempts": 10, "mode": "adaptive"})


def stale_volumes(region: str, older_than_days: int):
    """Yield unattached volumes older than the cutoff.

    A generator, so a 50,000-volume account never lands in memory at once.
    """
    ec2 = boto3.client("ec2", region_name=region, config=BOTO_CONFIG)
    cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)

    # Paginator, not a bare call - describe_* truncates silently.
    for page in ec2.get_paginator("describe_volumes").paginate(
        Filters=[{"Name": "status", "Values": ["available"]}]
    ):
        for volume in page["Volumes"]:
            if volume["CreateTime"] < cutoff:
                yield volume


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", default="eu-west-1")
    parser.add_argument("--older-than-days", type=int, default=30)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    try:
        total_gb = 0
        for volume in stale_volumes(args.region, args.older_than_days):
            name = next(
                (t["Value"] for t in volume.get("Tags", []) if t["Key"] == "Name"),
                "<untagged>",
            )
            total_gb += volume["Size"]
            log.info("%s %s %sGiB created=%s",
                     volume["VolumeId"], name, volume["Size"],
                     volume["CreateTime"].date())

        log.info("total reclaimable: %s GiB (~$%.2f/month gp3)", total_gb, total_gb * 0.08)
    except ClientError as exc:                       # specific, not bare except
        log.error("AWS API call failed: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## Interview tips

- Answer the "what do you use it for" question with concrete artefacts you have built - a tag-compliance report, a snapshot cleaner, a Lambda that auto-remediates. Naming libraries without a use case sounds rehearsed.
- Say you use the SDK rather than shelling out to the CLI, and mention paginators. That one detail reads as production experience.
- Have crisp two-sentence answers ready for list vs tuple, shallow vs deep copy, and the GIL - they are the three most common Python questions in DevOps interviews.
- The GIL answer that lands: threads help I/O-bound work because the lock is released during I/O; use `multiprocessing` for CPU-bound work.
- "How would you process a huge file?" - generators, line by line. Never `.read()` or `.readlines()` on something large.
- Mention virtual environments and pinned dependencies unprompted; unpinned automation is a stability question waiting to be asked.
- If you are not strong in Python, say so and describe what you _have_ automated. Claiming fluency and then failing a shallow-copy question is worse than an honest boundary.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you schedule work with cron and systemd timers?]] (`#497`): [How do you schedule work with cron and systemd timers?](../linux-administration/how-do-you-schedule-work-with-cron-and-systemd-timers.md)
- [[What is Shell Scripting?]] (`#42`): [What is Shell Scripting?](../linux-administration/what-is-shell-scripting.md)
- [[What is Linux File System Hierarchy?]] (`#45`): [What is Linux File System Hierarchy?](../linux-administration/what-is-linux-file-system-hierarchy.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scripting and Automation](./README.md) · [All topics](../README.md)
