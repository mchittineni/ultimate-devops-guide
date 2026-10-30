---
title: "How do you test and lint shell and Python automation scripts?"
id: 781
category: "Scripting and Automation"
difficulty: "Intermediate"
tags:
  - devops
  - scripting-and-automation
  - interview-questions
  - cicd
---

# How do you test and lint shell and Python automation scripts?

**Short answer:** In layers, the same as application code, because automation holds production credentials and runs unattended. **Static checks** on every commit: `shellcheck` and `shfmt` for Bash, `ruff` (lint and format) plus `mypy` or `pyright` for Python, all wired into pre-commit and CI. **Unit tests** for the logic: **bats-core** for shell functions, **pytest** for Python, with external systems replaced by stubs - a fake `kubectl` on `PATH`, botocore's `Stubber` or `moto` for AWS. **Integration or smoke tests** against something real but disposable: a kind cluster, a LocalStack or sandbox account, a container with the target OS. And design for testability - put logic in functions, keep side effects at the edges, and give every destructive script a `--dry-run` - because a script that is one long sequence of commands can only be tested by running it.

## Detail

### Static analysis: the cheapest and highest-yield layer

- **ShellCheck** catches the bugs that actually cause shell incidents: unquoted expansions (SC2086), `local x=$(cmd)` masking a failure (SC2155), `cd` without `|| exit` (SC2164), useless `cat`, and portability problems when the shebang is `sh`. Treat warnings as errors in CI; disable a rule only inline with a comment explaining why.
- **shfmt** normalises formatting so reviews are about logic, and `bash -n` catches syntax errors without executing anything.
- **Ruff** replaces flake8, isort, pyupgrade, and Black-style formatting in one fast tool; enable the bugbear (`B`) and security (`S`, the Bandit rules) rule sets for automation code, which flag `subprocess` calls that go through a shell, bare `except`, and hard-coded passwords.
- **Type checking** (`mypy --strict` or `pyright`) pays off quickly in scripts that pass dictionaries from cloud APIs around - typed SDK stubs such as `boto3-stubs` turn a misspelt key into a CI failure.
- **Run them through pre-commit** so developers get the feedback before CI, and pin hook versions so CI and laptops agree.

### Unit testing shell with bats-core

bats runs each `@test` block in a subshell and gives you `run` (captures `$status` and `$output`) plus assertion helpers from `bats-assert`. The technique that makes shell testable is **sourcing the script without executing `main`** - guard the entry point with `[[ "${BASH_SOURCE[0]}" == "$0" ]] && main "$@"` - and **stubbing external commands** by putting fake executables first on `PATH`. That lets you test "does the script call `kubectl rollout undo` when the rollout fails" without a cluster.

### Unit testing Python automation

- **pytest** with fixtures for shared setup and `tmp_path` for filesystem work.
- **Stub the cloud, not your logic**: botocore's `Stubber` asserts the exact API calls and parameters; `moto` emulates many AWS services in memory for broader behaviour; for Kubernetes, inject the client and pass a fake.
- **Test the dangerous paths explicitly**: dry-run does not call the delete API; `--limit` bounds the work; a `NotFound` error is treated as success (idempotency); a throttling error is retried; the exit code is non-zero on partial failure.
- **Freeze time** (`freezegun` or `time-machine`) for anything with age thresholds, or pass `now` as a parameter.
- **CLI tests**: call `main(["--older-than-days", "30"])` directly, or use Click/Typer's `CliRunner`, and assert on exit code and output.

### Integration and smoke tests

Unit tests with stubs prove your logic against your assumptions about the API; integration tests prove the assumptions. Keep a small set that runs against real but disposable targets: a `kind` or `k3d` cluster in CI for kubectl-driven scripts, LocalStack or a dedicated sandbox account (with tight IAM and budget alerts) for cloud automation, and a container matching the production OS for scripts that depend on distro tools (`env -i` to reproduce cron's empty environment). Run them on every merge to main and nightly, not necessarily on every push.

### Design choices that make testing possible

- Functions with inputs and outputs, not one top-level script body.
- Side effects isolated behind a small interface (`run_cmd`, an injected client) so tests can swap them.
- Configuration through arguments and environment, never edited constants.
- `--dry-run` that exercises the same code path up to the mutation, so the dry run is itself a test.
- Deterministic output (sorted, structured logs) so assertions are stable.

## Example

```bash
#!/usr/bin/env bash
# scripts/rollout.sh - testable shape: functions, and main only when executed directly
set -euo pipefail

promote() {
  local ns=$1 image=$2
  kubectl -n "$ns" set image deployment/api "api=${image}"
  if ! kubectl -n "$ns" rollout status deployment/api --timeout=5m; then
    kubectl -n "$ns" rollout undo deployment/api
    return 1
  fi
}

main() { promote "${1:?namespace}" "${2:?image}"; }
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then main "$@"; fi
```

```bash
# test/rollout.bats - bats-core with a stubbed kubectl on PATH
setup() {
  load 'test_helper/bats-support/load'
  load 'test_helper/bats-assert/load'
  STUB_DIR="$(mktemp -d)"
  export CALLS="$STUB_DIR/calls"
  : > "$CALLS"
  cat > "$STUB_DIR/kubectl" <<'EOF'
#!/usr/bin/env bash
echo "$*" >> "$CALLS"
if [[ "$*" == *"rollout status"* ]]; then exit "${ROLLOUT_EXIT:-0}"; fi
exit 0
EOF
  chmod +x "$STUB_DIR/kubectl"
  PATH="$STUB_DIR:$PATH"
  source "$BATS_TEST_DIRNAME/../scripts/rollout.sh"
}

teardown() { rm -rf "$STUB_DIR"; }

@test "successful rollout does not undo" {
  run promote staging api:1.9.0
  assert_success
  run grep -c "rollout undo" "$CALLS"
  assert_output "0"
}

@test "failed rollout triggers undo and returns non-zero" {
  export ROLLOUT_EXIT=1
  run promote staging api:1.9.0
  assert_failure
  run grep -c "rollout undo" "$CALLS"
  assert_output "1"
}
```

```python
# test_cleanup.py - pytest + botocore Stubber: assert the exact AWS calls
from datetime import datetime, timedelta, timezone

import boto3
from botocore.stub import Stubber

from cleanup import delete_stale   # delete_stale(ec2, older_than_days, apply) -> list[str]


def test_dry_run_never_deletes():
    ec2 = boto3.client("ec2", region_name="eu-west-1")
    old = datetime.now(timezone.utc) - timedelta(days=120)
    with Stubber(ec2) as stub:
        stub.add_response("describe_snapshots",
                          {"Snapshots": [{"SnapshotId": "snap-1", "StartTime": old}]},
                          {"OwnerIds": ["self"]})
        # no delete_snapshot response registered: any delete call fails the test
        assert delete_stale(ec2, older_than_days=90, apply=False) == ["snap-1"]
        stub.assert_no_pending_responses()
```

```yaml
# .pre-commit-config.yaml - the same checks locally and in CI (pin to current releases)
repos:
  - repo: https://github.com/koalaman/shellcheck-precommit
    rev: v0.11.0
    hooks: [{ id: shellcheck, args: ["--severity=warning"] }]
  - repo: https://github.com/scop/pre-commit-shfmt
    rev: v3.12.0-2
    hooks: [{ id: shfmt, args: ["-i", "2", "-ci"] }]
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.14.0
    hooks: [{ id: ruff-check, args: [--fix] }, { id: ruff-format }]
```

```bash
# CI step
pre-commit run --all-files
bats test/
pytest -q
```

## Interview tips

- Answer in layers - static checks, unit tests with stubs, integration against disposable targets - and say why automation deserves it: it runs unattended with production credentials.
- Name the tools concretely: ShellCheck and shfmt, bats-core, Ruff plus a type checker, pytest with botocore `Stubber` or `moto`. Then give one bug each would have caught.
- Explain how you make shell testable: functions, a `BASH_SOURCE` guard so tests can source the file, and fake commands on `PATH`. Few candidates know this, and it shows you have actually done it.
- Say what you test, not just how: dry-run never mutates, limits bound the blast radius, "not found" counts as success, retries happen on throttling, and exit codes reflect partial failure.
- Mention pre-commit so the same pinned checks run on laptops and in CI. See [how do you write a production-grade Bash script](./how-do-you-write-a-production-grade-bash-script.md), [turning a pile of ad hoc scripts into maintainable automation](./how-do-you-turn-a-pile-of-ad-hoc-scripts-into-maintainable-automation.md), and [what Python exercises come up in DevOps interviews](./what-python-exercises-come-up-in-devops-interviews.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you schedule work with cron and systemd timers?]] (`#497`): [How do you schedule work with cron and systemd timers?](../linux-administration/how-do-you-schedule-work-with-cron-and-systemd-timers.md)
- [[How do you run Terraform through a CI/CD pipeline?]] (`#466`): [How do you run Terraform through a CI/CD pipeline?](../infrastructure-as-code/how-do-you-run-terraform-through-a-ci-cd-pipeline.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scripting and Automation](./README.md) · [All topics](../README.md)
