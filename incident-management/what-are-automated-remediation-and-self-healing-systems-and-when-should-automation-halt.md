---
title: "What are Automated Remediation and Self-Healing systems and when should automation halt?"
id: 679
category: "Incident Management"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - automation
  - self-healing
  - remediation
  - safety
quiz:
  stem: "Why must automated self-healing systems incorporate circuit breakers that halt automated restarts after repeated failures?"
  options:
    - "To prevent automated loops from amplifying the outage by repeatedly restarting services, clearing caches, and crashing backend databases"
    - "Because cloud providers charge a penalty for restarting containers"
    - "Automated scripts cannot run more than three times per month"
    - "To allow CPU temperatures to cool down"
  answer: 1
  explanation: "Uncontrolled automated restarts during an external dependency failure can cause cascading destruction, thrashing connection pools and worsening the outage."
---

# What are Automated Remediation and Self-Healing systems and when should automation halt?

**Short answer:** Automated remediation runs predefined scripts or controllers to fix known failure modes instantly (restarting hung pods, flushing caches, adding ASG capacity); automation must halt (circuit break) when remediations fail repeatedly or when flapping creates runaway cascading instability.

## Detail

Automating the first step of a runbook resolves routine issues in seconds without waking human engineers:

### Classic Self-Healing Examples

- Kubernetes Kubelet restarting a container when a liveness probe fails.
- AWS Auto Scaling Group replacing an EC2 instance that fails hardware health checks.
- A scheduled job (e.g. AWS Systems Manager Automation) purging temp files when a disk-usage alarm fires.

### The Danger: Runaway Self-Healing Cascades

If automated remediation is unchecked, it can destroy systems:

- An external payment API slows down.
- Self-healing system assumes local web pods are dead and restarts all 100 pods.
- Restarting 100 pods clears in-memory caches and sends 10,000 cold database connections, crashing the database!
- Kubernetes keeps restarting the crashing pods (with CrashLoopBackOff delays growing up to five minutes), so the database never gets room to recover.

### Safety Guardrails (Automation Circuit Breakers)

1. **Rate Limiting**: Allow at most $X$ restarts per hour across the fleet.
2. **Blast Radius Limits**: Never restart more than 20% of replicas simultaneously.
3. **Escalation & Backoff**: If automated mitigation fails twice, **halt automation immediately** and page human engineers with full context.
4. **Dependency Awareness**: Do not remediate locally when the cause is upstream - check a dependency health signal first, and prefer failing fast (circuit breakers, readiness probes that shed traffic) over restarts.
5. **Auditability & Kill Switch**: Every automated action is logged as an event on the incident timeline, and a single flag disables the whole remediation system during a major incident.

**Trade-off.** Automation removes toil and shortens mitigation for known failures, but it can hide chronic problems (the pod that is restarted nightly is never fixed) and it acts faster than humans can notice when it is wrong. Count automated remediations as a metric and review the frequent ones as bugs.

## Example

```python
# Guarded remediation: restart one pod, but refuse when limits are hit or a dependency is the cause
import time, subprocess

MAX_ACTIONS_PER_HOUR = 5
MAX_FRACTION = 0.2
history: list[float] = []

def remediate(pod: str, ready: int, total: int, upstream_healthy: bool) -> str:
    now = time.time()
    history[:] = [t for t in history if now - t < 3600]
    if not upstream_healthy:
        return "halt: dependency unhealthy - restarting pods will not help; page a human"
    if len(history) >= MAX_ACTIONS_PER_HOUR:
        return "halt: rate limit reached; page a human"
    if (total - ready + 1) / total > MAX_FRACTION:
        return "halt: would exceed blast-radius cap; page a human"
    subprocess.run(["kubectl", "-n", "prod", "delete", "pod", pod, "--wait=false"], check=True)
    history.append(now)
    return f"restarted {pod}"
```

## Interview tips

- Self-healing resolving known deterministic failures fast without human intervention.
- Risks of automated feedback loops (restarting pods overwhelming databases).
- Automation circuit breakers and blast radius caps (max 20% fleet impact).
- Halting automation and escalating to humans if initial attempts fail.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Semantic Release and how does it automate versioning and changelogs from commits?]] (`#540`): [What is Semantic Release and how does it automate versioning and changelogs from commits?](../cicd/what-is-semantic-release-and-how-does-it-automate-versioning-and-changelogs-from-commits.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Incident Management](./README.md) · [All topics](../README.md)
