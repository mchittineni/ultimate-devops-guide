---
title: "What Python exercises come up in DevOps interviews?"
id: 503
category: "Scripting and Automation"
difficulty: "Intermediate"
tags:
  - devops
  - scripting-and-automation
  - interview-questions
  - aws-engineering
---

# What Python exercises come up in DevOps interviews?

**Short answer:** Two categories, and they are graded differently. The **operational** ones are what the job actually is: parse a log and aggregate it, filter a list of dictionaries (job records, API responses) by a field, extract unique IP addresses from a live log, check disk usage and alert above a threshold, list cloud resources with boto3 filtered by tag, retrieve a secret, and watch a directory for new files. The **language** ones are quick screens: reverse a string, palindrome, count word occurrences, longest substring without repeats, find pairs summing to N, list versus tuple versus set, shallow versus deep copy, decorators, `5/2` versus `5//2`, and what the GIL means. For the operational ones you are being judged on **using the right data structure, handling errors, and not loading a 4 GB file into memory**; for the language ones, on picking `set` when you need membership testing and `dict`/`Counter` when you need counting - and on saying the complexity out loud. The habit that earns most of the credit: iterate over a file line by line rather than `read()`, use `collections.Counter` and `defaultdict` instead of hand-rolled loops, and pass subprocess arguments as a list so nothing is ever interpreted by a shell.

## Detail

### The data structures, because every question reduces to picking one

| Need                                         | Use                                 | Why                                                                            |
| -------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------ |
| Ordered, mutable sequence                    | `list`                              | Indexable, `O(n)` membership                                                   |
| Fixed record, hashable, usable as a dict key | `tuple`                             | Immutable, so it can be a key or set member                                    |
| Unique values, fast membership               | **`set`**                           | `O(1)` `in`, automatic dedupe - the answer to "unique IPs" and "no duplicates" |
| Key → value lookup                           | `dict`                              | `O(1)`, insertion-ordered since 3.7                                            |
| Counting occurrences                         | **`collections.Counter`**           | `most_common(n)` for free                                                      |
| Grouping into lists                          | **`collections.defaultdict(list)`** | No `if key not in d` boilerplate                                               |
| Fixed-size window / queue                    | `collections.deque(maxlen=N)`       | `O(1)` at both ends                                                            |

**List versus tuple**: mutable versus immutable; a tuple can be a `dict` key or a `set` member and is slightly cheaper. **Set versus list**: `in` is `O(1)` versus `O(n)`, which is the whole answer to "why does the directory-watching script use a set?" - comparing two directory listings with sets is one operation and stays fast as the directory grows. In C++ terms (asked as "list or set if you do not want duplicates?") the answer is the same: a set, because uniqueness is enforced by the container rather than by your code.

### The operational exercises

**Filter a list of dicts - job logs where `status` is `FAILED`:**

```python
def failed_job_ids(records: list[dict]) -> list[str]:
    """Return job_ids whose status is FAILED. Tolerates missing keys."""
    return [r["job_id"] for r in records if r.get("status") == "FAILED"]

logs = [
    {"job_id": "101", "status": "SUCCESS", "timestamp": "2026-08-10T01:00:00Z"},
    {"job_id": "102", "status": "FAILED",  "timestamp": "2026-08-10T01:05:00Z"},
    {"job_id": "103", "status": "FAILED",  "timestamp": "2026-08-10T01:09:00Z"},
    {"job_id": "104", "status": "SUCCESS", "timestamp": "2026-08-10T01:12:00Z"},
]
print(failed_job_ids(logs))          # ['102', '103']
```

Say why `.get()` rather than `[...]`: real log records have missing fields, and a `KeyError` in a monitoring script is an outage you caused. That single choice is often what the question is testing.

**Unique IPs from a log that is still being written:**

```python
import re
from collections import Counter

IP = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

def unique_ips(path: str) -> tuple[set[str], Counter]:
    seen: set[str] = set()
    counts: Counter = Counter()
    with open(path, "r", errors="replace") as fh:      # never read() a growing log
        for line in fh:                                # streaming: constant memory
            for ip in IP.findall(line):
                seen.add(ip)
                counts[ip] += 1
    return seen, counts

ips, counts = unique_ips("/var/log/nginx/access.log")
print(f"{len(ips)} unique addresses")
for ip, n in counts.most_common(5):
    print(f"{n:>8} {ip}")
```

**Disk check with an alert:**

```python
import shutil, socket, logging, sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def check(path: str = "/", threshold: int = 80) -> int:
    total, used, free = shutil.disk_usage(path)        # stdlib; no df parsing
    pct = used / total * 100
    if pct >= threshold:
        logging.error("%s at %.1f%% (threshold %d%%) on %s - %.1f GiB free",
                      path, pct, threshold, socket.gethostname(), free / 2**30)
        return 1                                        # non-zero: the scheduler notices
    logging.info("%s at %.1f%%", path, pct)
    return 0

if __name__ == "__main__":
    sys.exit(check(*sys.argv[1:2] or ["/"]))
```

**boto3: running instances tagged `PROD`, across many accounts:**

```python
import boto3

def running_prod_instances(region: str = "eu-west-1") -> list[dict]:
    ec2 = boto3.client("ec2", region_name=region)
    paginator = ec2.get_paginator("describe_instances")   # ALWAYS paginate
    out = []
    for page in paginator.paginate(Filters=[
        {"Name": "instance-state-name", "Values": ["running"]},
        {"Name": "tag:Environment",     "Values": ["PROD"]},   # filter server-side
    ]):
        for res in page["Reservations"]:
            for i in res["Instances"]:
                tags = {t["Key"]: t["Value"] for t in i.get("Tags", [])}
                out.append({"id": i["InstanceId"], "type": i["InstanceType"],
                            "az": i["Placement"]["AvailabilityZone"],
                            "name": tags.get("Name", "-")})
    return out

def across_accounts(account_ids: list[str], role: str = "ReadOnly") -> dict:
    """Count instances across many accounts with STS - no keys per account."""
    sts = boto3.client("sts")
    result = {}
    for acct in account_ids:
        creds = sts.assume_role(RoleArn=f"arn:aws:iam::{acct}:role/{role}",
                                RoleSessionName="inventory")["Credentials"]
        ec2 = boto3.client("ec2", aws_access_key_id=creds["AccessKeyId"],
                           aws_secret_access_key=creds["SecretAccessKey"],
                           aws_session_token=creds["SessionToken"])
        result[acct] = sum(len(r["Instances"])
                           for p in ec2.get_paginator("describe_instances").paginate()
                           for r in p["Reservations"])
    return result
```

Two things to say here: **paginate** (a `describe_*` call returns a page, not everything - forgetting this is the most common boto3 bug), and **filter server-side** rather than pulling everything and filtering in Python. For "count instances across 50 accounts without logging into each", the answer is STS `assume_role` in a loop (as above) or AWS Config's aggregator / Resource Explorer for a single query.

**Retrieve a secret, and watch a directory:**

```python
import boto3, json, time
from pathlib import Path

def get_secret(name: str, region: str = "eu-west-1") -> dict:
    client = boto3.client("secretsmanager", region_name=region)
    raw = client.get_secret_value(SecretId=name)["SecretString"]
    return json.loads(raw)

def watch(directory: str, interval: int = 60):
    """Report files that appeared since the last check - set difference, O(1) lookups."""
    seen = {p.name for p in Path(directory).iterdir() if p.is_file()}
    while True:
        time.sleep(interval)
        now = {p.name for p in Path(directory).iterdir() if p.is_file()}
        for new in sorted(now - seen):      # set difference: this is why a set, not a list
            print(f"{time.strftime('%FT%T')} new: {new}")
        seen = now
```

### The language screens, answered quickly

```python
# reverse a string - three ways, and know the constraint being applied
s[::-1]                                  # slicing
"".join(reversed(s))                     # built-in
def rev(s):                              # no slicing, no builtins (the strict version)
    out = ""
    for ch in s:
        out = ch + out
    return out

# palindrome, with a for loop as asked
def is_pal(s):
    s = "".join(c.lower() for c in s if c.isalnum())
    for i in range(len(s) // 2):
        if s[i] != s[-1 - i]:
            return False
    return True

# count occurrences of a word
from collections import Counter
Counter("Hello World Hello".split())["Hello"]        # 2

# longest substring without repeating characters - O(n) sliding window
def longest_unique(s: str) -> int:
    last, start, best = {}, 0, 0
    for i, ch in enumerate(s):
        if ch in last and last[ch] >= start:
            start = last[ch] + 1
        last[ch] = i
        best = max(best, i - start + 1)
    return best

# pairs summing to a target - O(n) with a set, not O(n^2) nested loops
def pairs(nums, target):
    seen, out = set(), set()
    for n in nums:
        if target - n in seen:
            out.add((min(n, target - n), max(n, target - n)))
        seen.add(n)
    return sorted(out)

# second largest, without sorting the whole list
def second_largest(nums):
    first = second = float("-inf")
    for n in nums:
        if n > first: first, second = n, first
        elif first > n > second: second = n
    return second if second != float("-inf") else None
```

**The trivia, with the answer that shows understanding:**

- **`5/2` = 2.5, `5//2` = 2.** True division always returns a float in Python 3; floor division rounds **towards negative infinity**, so `-5//2` is `-3`, not `-2`. That second half is the interesting part.
- **`a = [0]; b = {0}`** - `a[0]` returns `0`; `b[0]` raises `TypeError` because a set is unordered and not subscriptable. To get a value out, iterate or `next(iter(b))`.
- **Shallow versus deep copy**: `copy.copy` copies the container and shares the nested objects, so mutating a nested list is visible through both; `copy.deepcopy` recurses. The gotcha that matters in real code is a mutable default argument (`def f(x=[])`) sharing state across calls.
- **Decorators** are functions that wrap functions - the mechanism behind `@retry`, `@timing`, and `@app.route`. Show one with `functools.wraps`.
- **The GIL** means only one thread executes Python bytecode at a time, so threads help with **I/O-bound** work (waiting on the network - exactly what DevOps scripts do) and not with **CPU-bound** work, for which you use `multiprocessing`, a C extension that releases the GIL (NumPy), or `asyncio` for high-concurrency I/O. Free-threaded builds are changing this, but the practical rule stands.
- **`re.search` versus `re.match`**: `match` anchors at the start, `search` scans anywhere. Half of all "my regex does not work" is this.

### The habits interviewers are actually scoring

- **Stream, do not slurp**: `for line in fh` over a 4 GB log; `read()` on it kills the box.
- **Handle errors explicitly**: `try/except` around I/O and API calls, catching the specific exception (`ClientError`, `FileNotFoundError`), not bare `except:`.
- **`logging`, not `print`**, with levels - so the same script works in cron and in a container.
- **`argparse`** for arguments, `sys.exit(code)` for exit status, and `if __name__ == "__main__":`.
- **Type hints and a docstring** on anything you expect someone else to run.
- **`subprocess.run([...], check=True, capture_output=True)`** - pass a **list of arguments**. Never build a command string from user input and hand it to a shell; that is command injection, and it is the one mistake in a scripting interview that will be remembered.
- **`pathlib`** over string path concatenation, `shutil.disk_usage` over parsing `df`, `json`/`yaml` parsers over regex on structured data.
- **A retry with backoff** around anything network-facing, and mention `tenacity` or boto3's built-in `retries` config.

## Example

```python
#!/usr/bin/env python3
"""Report the top error signatures in a log and exit non-zero if any repeats too often.

The shape of a real DevOps script: argparse, logging, streaming, Counter,
explicit errors, meaningful exit code.
"""
from __future__ import annotations

import argparse, logging, re, sys
from collections import Counter
from pathlib import Path

NOISE = re.compile(r"[0-9a-f]{8,}|\b\d+\b")     # normalise IDs so counts do not fragment
log = logging.getLogger("logscan")


def signatures(path: Path, level: str) -> Counter:
    counts: Counter = Counter()
    try:
        with path.open("r", errors="replace") as fh:
            for line in fh:                      # streaming: constant memory on a 4 GB file
                if level in line:
                    counts[NOISE.sub("<x>", line.strip())] += 1
    except FileNotFoundError:
        log.error("no such file: %s", path)
        raise SystemExit(2)
    except PermissionError:
        log.error("cannot read %s - check permissions", path)
        raise SystemExit(2)
    return counts


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("logfile", type=Path)
    p.add_argument("--level", default="ERROR")
    p.add_argument("--threshold", type=int, default=3)
    p.add_argument("--top", type=int, default=10)
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")

    counts = signatures(args.logfile, args.level)
    if not counts:
        log.info("no %s lines in %s", args.level, args.logfile)
        return 0

    for msg, n in counts.most_common(args.top):
        print(f"{n:>6}  {msg[:140]}")

    breaches = [(m, n) for m, n in counts.items() if n > args.threshold]
    for m, n in sorted(breaches, key=lambda kv: -kv[1]):
        log.error("[ALERT] %dx %s", n, m[:120])
    return 1 if breaches else 0                   # exit code drives the scheduler/monitor


if __name__ == "__main__":
    sys.exit(main())
```

```python
# Retry with backoff around anything network-facing - asked as a follow-up constantly
import time, functools, random, logging

def retry(attempts=4, base=0.5, exceptions=(Exception,)):
    def deco(fn):
        @functools.wraps(fn)                       # keep __name__ and docstring
        def wrapper(*a, **kw):
            for i in range(1, attempts + 1):
                try:
                    return fn(*a, **kw)
                except exceptions as e:
                    if i == attempts:
                        raise
                    sleep = base * 2 ** (i - 1) + random.random() * 0.1   # jitter
                    logging.warning("%s failed (%s), retry %d/%d in %.1fs",
                                    fn.__name__, e, i, attempts, sleep)
                    time.sleep(sleep)
        return wrapper
    return deco

@retry(attempts=5, exceptions=(TimeoutError, ConnectionError))
def call_api(url): ...
```

```python
# Shelling out safely: a list of arguments, so the shell never parses anything
import subprocess

def pods(namespace: str) -> str:
    result = subprocess.run(
        ["kubectl", "get", "pods", "-n", namespace, "-o", "json"],
        check=True, capture_output=True, text=True, timeout=30,
    )
    return result.stdout
# `namespace` is passed as its own argv entry, so a value like "; rm -rf /" is
# just a (nonexistent) namespace name rather than a second command.
```

## Interview tips

- Before writing anything, say which data structure you are reaching for and why - `set` for uniqueness and `O(1)` membership, `Counter` for counting, `defaultdict(list)` for grouping. Most of these exercises are really a data-structure question.
- On the log exercises, stream the file (`for line in fh`) and say explicitly that `read()` on a multi-gigabyte log would exhaust memory. That one sentence carries a lot of weight.
- Use `.get()` on dictionaries from external data and explain why: real records have missing fields, and a `KeyError` in a monitoring script is an outage you created.
- With boto3, **paginate** and **filter server-side**. Forgetting pagination is the most common real bug, and mentioning it unprompted marks you as someone who has shipped a boto3 script.
- For cross-account inventory, answer STS `assume_role` in a loop (or Config aggregator / Resource Explorer) rather than "log into each account".
- Give complexity for the algorithm questions - sliding window is `O(n)`, the pair-sum with a set is `O(n)` versus `O(n²)` nested loops - and mention the trade-off if asked to avoid extra memory.
- For `5//2`, add that floor division rounds towards negative infinity so `-5//2` is `-3`. For sets, that they are unordered and not subscriptable. For the GIL, that threads help I/O-bound work (which is what our scripts do) and `multiprocessing` is for CPU-bound.
- Show a decorator with `functools.wraps` if asked, and volunteer the retry-with-backoff decorator - it is the most useful thing in a DevOps Python toolkit.
- Always pass subprocess arguments as a list, and say why: building a command string from an input value hands control of the shell to whoever supplied it. See [what do you use Python for as a DevOps engineer](./what-do-you-use-python-for-as-a-devops-engineer.md), [when do you use Bash and when do you use Python](./when-do-you-use-bash-and-when-do-you-use-python.md), [what Bash scripting exercises come up in DevOps interviews](./what-bash-scripting-exercises-come-up-in-devops-interviews.md), and [turning a pile of ad hoc scripts into maintainable automation](./how-do-you-turn-a-pile-of-ad-hoc-scripts-into-maintainable-automation.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you schedule work with cron and systemd timers?]] (`#497`): [How do you schedule work with cron and systemd timers?](../linux-administration/how-do-you-schedule-work-with-cron-and-systemd-timers.md)
- [[How do you troubleshoot SSH failures, high CPU, and disk space on Linux servers?]] (`#238`): [How do you troubleshoot SSH failures, high CPU, and disk space on Linux servers?](../linux-administration/how-do-you-troubleshoot-ssh-failures-high-cpu-and-disk-space-on-linux-servers.md)
- [[How do you analyse logs and text files with grep, awk, and sed?]] (`#265`): [How do you analyse logs and text files with grep, awk, and sed?](../linux-administration/how-do-you-analyse-logs-and-text-files-with-grep-awk-and-sed.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scripting and Automation](./README.md) · [All topics](../README.md)
