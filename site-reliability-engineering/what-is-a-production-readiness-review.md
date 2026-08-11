---
title: "What is a production readiness review?"
id: 231
category: "Site Reliability Engineering (SRE)"
difficulty: "Intermediate"
tags:
  - devops
  - site-reliability-engineering
  - interview-questions
---

# What is a production readiness review?

**Short answer:** A PRR is a structured check, before a service takes production traffic or SRE support, that it can be operated: SLOs defined, alerts that page on symptoms, dashboards, a runbook, capacity and dependency analysis, rollback tested, and an owner with an on-call rotation. Done well it is a collaborative design review with a checklist; done badly it is a gate that teams learn to route around.

## Detail

**What the checklist covers:**

| Area          | The question being answered                                            |
| ------------- | ---------------------------------------------------------------------- |
| Ownership     | Which team owns it, and who is paged at 3am?                           |
| SLOs          | What are the SLIs, targets, and the error budget policy?               |
| Alerting      | Do alerts page on user-visible symptoms, and does each have a runbook? |
| Observability | Can you answer "what is slow and why?" from existing telemetry?        |
| Dependencies  | What is hard versus soft, and what happens when each fails?            |
| Capacity      | Measured limits, autoscaling bounds, quota headroom                    |
| Failure modes | Rollback tested, retries bounded, timeouts set, graceful degradation   |
| Data          | Backups, tested restore, migration and rollback plan, retention        |
| Security      | Authentication, authorisation, secrets handling, data classification   |
| Operations    | Runbook, deploy/rollback procedure, known issues, escalation path      |

**Do it early, not at the launch gate.** A review two weeks before launch finds problems that require architectural change and cannot be fixed in time, so it either delays the launch or gets waived. A lightweight review at design time plus a verification pass before traffic is the pattern that actually improves services.

**Verify, do not ask.** "Do you have backups?" invites a yes. "Show me the last restore test" produces evidence. The strongest reviews trigger the failure in a staging environment - kill the primary database, block the dependency - and watch what the alerts and dashboards actually do.

**Automate the mechanical parts.** Whether an SLO exists, whether alerts are wired, whether the catalogue lists an owner and a runbook, whether the base image is supported, whether backups are configured - all of that can be a scorecard computed from the catalogue and monitoring APIs. Then the human review spends its time on failure modes and dependencies, which is where judgement is needed.

**Tie it to the support model.** In Google's original formulation, a PRR is what a service must pass for SRE to take on its on-call burden, and SRE can hand a service back if it degrades. Even without a separate SRE team, making the review the entry condition for tier-1 support and platform-provided reliability features gives it teeth without making it bureaucratic.

**Reviews are not one-off.** Services drift: dependencies change, traffic grows, the runbook goes stale. Re-review tier-1 services annually, and after any incident that revealed a gap the review should have caught - that feedback loop is what keeps the checklist relevant rather than ritual.

## Example

```text
PRR - checkout v2 - verdict: CONDITIONAL GO

PASS   owner team-payments; on-call rotation staffed 24/7
PASS   SLO 99.9% availability, 99% < 300 ms; error budget policy signed off
PASS   symptom-based paging via burn-rate alerts; each alert links a runbook
PASS   dashboards answer latency/error/saturation; traces sampled, errors always kept
PASS   rollback rehearsed in staging: 4 min, verified twice
FAIL   restore test: last verified 2025-11 (policy: every 90 days)   -> BLOCKER
FAIL   payment provider treated as hard dependency; no degraded path -> BLOCKER
WARN   DB connection pool ceiling is the binding capacity limit at 2.4x peak
WARN   runbook missing the "queue backed up" scenario

Conditions before production traffic: complete a restore test; implement queue-and-settle
degradation for provider timeouts. Re-review in 2 weeks; capacity item tracked for Q4.
```

## Interview tips

- Frame it as design-time collaboration plus a verification pass - pure gatekeeping is the answer that reads badly.
- "Ask for evidence, not assurances" and automating the mechanical checks are the two strong points.
- Expect: "what if the team refuses?" - tie support and platform features to it, escalate on risk, and never silently accept an unowned service.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you choose an SLO target?]] (`#177`): [How do you choose an SLO target?](../slo-engineering/how-do-you-choose-an-slo-target.md)
- [[What is multi-window multi-burn-rate alerting?]] (`#178`): [What is multi-window multi-burn-rate alerting?](../slo-engineering/what-is-multi-window-multi-burn-rate-alerting.md)
- [[How do you define SLOs for batch and asynchronous workloads?]] (`#181`): [How do you define SLOs for batch and asynchronous workloads?](../slo-engineering/how-do-you-define-slos-for-batch-and-asynchronous-workloads.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Site Reliability Engineering (SRE)](./README.md) · [All topics](../README.md)
