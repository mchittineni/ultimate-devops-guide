---
title: "How do you troubleshoot a Kubernetes Job or CronJob that never completes?"
id: 408
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - kubernetes
  - interview-questions
  - scripting-and-automation
  - monitoring-and-logging
---

# How do you troubleshoot a Kubernetes Job or CronJob that never completes?

**Short answer:** A Job "hangs" for one of four reasons, and the Pod's state tells you which: **the Pod never started** (unschedulable, image pull, PVC pending - the Job is not at fault), **the process is genuinely blocked** (waiting on a lock, a query, a network call with no timeout), **the process exited but the Pod never terminated** (a sidecar or service-mesh proxy still running, so the Pod stays `NotReady` for ever), or **the Job is silently retrying** (`restartPolicy: OnFailure` with a `backoffLimit` you never set, so it fails and restarts indefinitely from the outside). The two settings that prevent all of this are `activeDeadlineSeconds` and `backoffLimit`, and every Job you write should have both.

## Detail

### How Jobs actually terminate

A Job counts a Pod as successful when its containers exit 0 and completes when `.spec.completions` successes are recorded. Two consequences catch people:

- **A sidecar that never exits keeps the Pod running.** A service-mesh proxy, a log shipper, or a cloud SQL proxy in the same Pod means the Pod never reaches `Succeeded`, so the Job never completes even though your work finished. The fixes: use the **native sidecar** support (an init container with `restartPolicy: Always`, stable since Kubernetes 1.29) so the kubelet stops it once the main container exits; exclude the Job from mesh injection with an annotation; or have the main container signal the sidecar to quit.
- **`restartPolicy` inside a Job is only `Never` or `OnFailure`.** With `OnFailure` the kubelet restarts the container in place, which can look like a job that runs for ever with no new Pods. With `Never` a failure creates a new Pod, so you can see the history - which is why `Never` plus a `backoffLimit` is usually easier to operate.

### The diagnostic sequence

1. **`kubectl describe job`** - read the events and the status: `Active`, `Succeeded`, `Failed`, and whether the controller reports `BackoffLimitExceeded` or `DeadlineExceeded`.
2. **Find the Pods and look at their phase**: `kubectl get pods -l job-name=<job>`. `Pending` means it never ran (scheduling, quota, node selector, PVC), `Running` means it is genuinely working or blocked, `CrashLoopBackOff` means it fails and restarts, many `Error` Pods mean it is burning through retries.
3. **Read the logs, including previous attempts**: `kubectl logs job/<job> --tail=100`, and `--previous` for a restarted container. If the log stops mid-work and never advances, you have a blocked process, not a Kubernetes problem.
4. **Prove where it is blocked.** `kubectl exec` into the Pod and look: `ps`, then whatever the workload gives you - an open database session waiting on a lock, an HTTP call with no timeout, `curl` to a dependency, a `SELECT * FROM pg_locks`. Long-running batch work that hangs is nearly always an unbounded wait on an external dependency.
5. **Check resource pressure.** An OOM-killed container shows exit code 137 in `Last State`; heavy CPU throttling makes a job that used to take 5 minutes take 50. Look at `resources.limits` and the node's condition.
6. **Check for eviction and preemption.** A batch Job with low priority on a busy node gets evicted repeatedly and restarts from the beginning. See [how do you handle node pressure and Pod evictions in Kubernetes](./how-do-you-handle-node-pressure-and-pod-evictions-in-kubernetes.md).

### CronJob-specific failures

- **`concurrencyPolicy`.** The default `Allow` lets a slow run overlap the next schedule, and overlapping migrations or reports cause data corruption or lock contention. Use `Forbid` for anything not safe to run twice, or `Replace` when only the latest matters.
- **A `suspend: true` CronJob** simply does not fire - check it before debugging anything else.
- **Missed schedules.** If the controller cannot start a run within `startingDeadlineSeconds` (or more than 100 schedules are missed), it gives up and logs `Cannot determine if job needs to be started: too many missed start times`. This usually follows a controller outage or a long `Forbid` overlap.
- **Timezone.** Schedules are UTC unless `spec.timeZone` is set - the cause of most "it ran at the wrong time".
- **History limits.** `successfulJobsHistoryLimit` and `failedJobsHistoryLimit` control how many completed Jobs (and their Pods, and their logs) survive. Set them deliberately: too high fills etcd and the node with completed Pods, too low destroys the evidence you need to debug.

### Writing Jobs that cannot hang

Set `activeDeadlineSeconds` so the Job is killed rather than running for ever; set `backoffLimit` so failures stop retrying; add `ttlSecondsAfterFinished` so completed Jobs clean themselves up; make the work **idempotent and restartable**, because retries and evictions will re-run it; and alert on Job failure and duration rather than discovering it a week later. For unrecoverable input, exit non-zero fast rather than retrying - and if you need per-item retry semantics, `podFailurePolicy` lets you distinguish a genuine application failure from an infrastructure disruption.

## Example

```bash
# What does the controller think is happening?
kubectl describe job nightly-reindex -n batch | tail -25
# Events:  SuccessfulCreate  Created pod: nightly-reindex-abc12
#          (no completion event, Active=1 for 4h)

# Which Pods, and in what state?
kubectl get pods -n batch -l job-name=nightly-reindex -o wide
# nightly-reindex-abc12   2/2  Running  0  4h    <- 2/2: the sidecar is still up

kubectl logs -n batch job/nightly-reindex --tail=50 --all-containers
kubectl logs -n batch nightly-reindex-abc12 --previous   # after a restart

# Blocked on what? Look inside rather than guessing.
kubectl exec -n batch nightly-reindex-abc12 -c worker -- ps -eo pid,etime,cmd
kubectl exec -n batch nightly-reindex-abc12 -c worker -- \
  psql "$DB" -c "select pid, state, wait_event, query from pg_stat_activity where state <> 'idle'"

# OOM or throttling?
kubectl describe pod -n batch nightly-reindex-abc12 | grep -A4 'Last State'

# Stop the bleeding, keep the evidence
kubectl delete job nightly-reindex -n batch --cascade=foreground
```

```yaml
apiVersion: batch/v1
kind: CronJob
metadata: { name: nightly-reindex, namespace: batch }
spec:
  schedule: "0 2 * * *"
  timeZone: "Europe/London" # otherwise UTC - the classic "ran an hour early"
  concurrencyPolicy: Forbid # never let a slow run overlap the next one
  startingDeadlineSeconds: 600
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 3 # keep evidence, do not fill the cluster
  jobTemplate:
    spec:
      backoffLimit: 2 # stop retrying a broken job
      activeDeadlineSeconds: 3600 # hard stop: kill it rather than hang for ever
      ttlSecondsAfterFinished: 86400 # self-cleaning
      template:
        spec:
          restartPolicy: Never # each failure is a new, inspectable Pod
          initContainers:
            - name: proxy # native sidecar: stopped when the main container exits
              image: cloud-sql-proxy:2.11
              restartPolicy: Always
          containers:
            - name: worker
              image: reindex:1.4.2
              resources:
                requests: { cpu: "1", memory: 2Gi }
                limits: { memory: 4Gi } # exit 137 here means raise this
```

## Interview tips

- Open with the four causes (never started / genuinely blocked / process done but Pod alive / silently retrying) and say that the Pod's phase tells you which. That framing is the answer.
- The sidecar-keeps-the-Pod-alive case is the detail that marks real experience - mention the native sidecar (`initContainers` with `restartPolicy: Always`) as the modern fix, and mesh-injection exclusion as the alternative.
- Point out that a Job's `restartPolicy` can only be `Never` or `OnFailure`, and explain why `Never` is easier to debug.
- Name `activeDeadlineSeconds`, `backoffLimit`, and `ttlSecondsAfterFinished` as the three fields every Job should set. Interviewers use this to check whether you write Jobs or only read about them.
- For CronJobs, bring up `concurrencyPolicy: Forbid` and the timezone default. Overlapping runs are a real data-corruption story, not a theoretical one.
- Say that batch work must be idempotent because evictions and retries will re-run it - and that "resume from where it stopped" is a design requirement, not a nice-to-have.
- Close on alerting: a failed nightly job discovered a week later is the actual production risk. See [how do you write effective PromQL queries and Alertmanager rules](../monitoring-and-logging/how-do-you-write-effective-promql-queries-and-alertmanager-rules.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How does Prometheus collect metrics, and what components sit around it?]] (`#500`): [How does Prometheus collect metrics, and what components sit around it?](../monitoring-and-logging/how-does-prometheus-collect-metrics-and-what-components-sit-around-it.md)
- [[How do the ELK and EFK stacks fit together?]] (`#501`): [How do the ELK and EFK stacks fit together?](../monitoring-and-logging/how-do-the-elk-and-efk-stacks-fit-together.md)
- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
