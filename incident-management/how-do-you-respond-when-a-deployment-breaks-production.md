---
title: "How do you respond when a deployment breaks production?"
id: 425
category: "Incident Management"
difficulty: "Advanced"
tags:
  - devops
  - incident-management
  - interview-questions
  - cicd
  - devops-tools-and-automation
  - database-management-in-devops
---

# How do you respond when a deployment breaks production?

**Short answer:** Roll back first, diagnose second. The moment customer impact correlates with a release, the release is the prime suspect and reverting is the fastest mitigation available - you do not need to understand the bug to stop the bleeding. Concretely: declare the incident and take a role, **freeze further deploys**, **roll back or shift traffic away** from the new version, **verify the metrics actually recover**, and only then investigate with the old version safely serving traffic. Two things make this fail: a database migration or data change that a code rollback cannot undo, and a "rollback" nobody has ever practised. Afterwards the question is not "who broke it" but "why did the pipeline let it through" - and the answer becomes a test, a gate, or a canary.

## Detail

### The first ten minutes

1. **Declare, and say who is coordinating.** Even for a one-person fix, name the incident and open one channel of record. See [how do you run a major incident as incident commander](./how-do-you-run-a-major-incident-as-incident-commander.md).
2. **Confirm the correlation quickly, do not prove causation.** Did the error rate, latency, or a business metric change within a minute or two of the deployment timestamp? That is enough to act on. Deployment markers on your dashboards make this a two-second check, which is why they are worth adding before you need them.
3. **Freeze the pipeline.** Stop further deploys and stop the rollout in flight, or you will be debugging a moving target - and someone else's unrelated change will land in the middle of your incident.
4. **Mitigate with the fastest reversible lever available**, in this order:
   - **Feature flag off** - seconds, no deploy, smallest blast radius. This is why flags are the single best investment for incident response. See [what is feature flagging](../advanced-devops-cloud/what-is-feature-flagging.md).
   - **Traffic shift** - move the weighted canary or blue/green pointer back to the previous version. Seconds, and no Pod churn.
   - **Rollback** - `kubectl rollout undo`, redeploy the previous image digest, or `git revert` in a GitOps repository (which is the correct form when a controller is reconciling, because a manual rollback gets synced away).
   - **Scale, shed, or disable the affected path** if the failure is capacity-shaped rather than logic-shaped.
   - **Roll forward** only when rollback is genuinely impossible - and be honest that "fix forward" under pressure has a much higher failure rate than reverting to a version you know worked.
5. **Verify recovery on the metrics, not on the deployment status.** "Rollback complete" is not "the error rate is back to baseline". Say the two out loud separately.
6. **Communicate on a schedule** - a first customer-facing update within minutes even if it only says you are investigating, then every 20-30 minutes.

### What rollback cannot undo - decide this before you need to

A code rollback restores behaviour, not consequences. Enumerate the irreversible things:

- **Schema migrations.** If the release dropped or renamed a column, the old code cannot run. This is the entire argument for expand/contract - additive, backward-compatible migrations mean rollback stays available for at least one release. See [how do you change a production database schema without downtime](../database-management-in-devops/how-do-you-change-a-production-database-schema-without-downtime.md).
- **Data written in a new format** that the old code cannot read, or a new field the old code will not populate.
- **Messages already consumed**, events published, emails and webhooks sent, payments taken.
- **Cache and CDN state** - a poisoned cache key survives the rollback; plan the invalidation.
- **Third-party side effects** - anything you told another system, you cannot un-tell.

When any of these apply, the mitigation is a **compensating change** (a forward fix, a data repair script, a replay from a backup or event log) and the decision must be made deliberately, with a named owner and a timebox, rather than discovered halfway through.

### Then find out why the pipeline allowed it

This is the part interviewers actually weigh, because it is the difference between firefighting and engineering. The scenario in the classic version of this question - "the release passed every test but the database connection failed in production" - has a specific lesson: **the pipeline tested the code, not the deployed system in its real environment.** So the follow-ups are structural:

- Was the failure **environment-specific configuration** (a connection string, a secret, a security group, a firewall rule)? Then the gate is a post-deploy **smoke test that exercises the real dependency**, run automatically before traffic shifts - a health check that touches the database, a synthetic transaction on the critical journey.
- Was it **untested integration**? Add a contract or integration test against a real instance of the dependency, not a mock.
- Was it **load-dependent**? A canary with metric-based promotion catches what a functional test cannot, because it exposes the change to real traffic at a small percentage.
- Was it **caught late by a human watching graphs**? Automate the verdict: error-budget burn or an SLO-based alarm that triggers the rollback without a human decision.
- Was the **blast radius unnecessarily large**? Progressive delivery (canary, blue/green, per-cluster waves) means the next occurrence affects 5% of users for two minutes rather than everyone for twenty.
- Was the **rollback itself slow or untested**? Practise it. A rollback path exercised only during incidents is a hypothesis.

### The post-incident review

Blameless, within a few days, with a timeline captured while it is fresh: when the deploy happened, when the first signal appeared, when a human noticed, when mitigation started, when impact ended. Those intervals are the actionable output - **time to detect** usually points at missing alerts, and **time to mitigate** at a missing or untested rollback path. Produce a small number of follow-up actions with owners and dates, and prefer one systemic fix (an automated gate) over five reminders to be careful. See [what is post-mortem analysis](./what-is-post-mortem-analysis.md) and [what is blameless culture](../devops-culture-and-practices/what-is-blameless-culture.md).

## Example

```text
09:02  deploy checkout 1.9.0 -> prod (canary 10%)
09:04  alert: checkout 5xx 0.2% -> 41%, p99 1.2s -> 30s (timeouts)
09:05  IC declared. Deploy freeze on. Correlation with 09:02 release: yes.
09:06  MITIGATE: alias/canary weight back to 1.8.2 (seconds, no pod churn)
09:08  5xx 41% -> 0.3% = baseline. Mitigated, NOT resolved. Status page updated.
09:20  Cause: 1.9.0 reads DB_HOST from a new secret key that exists in staging
       only. Connection pool never initialised; health check did not touch the DB,
       so the readiness probe passed and traffic was routed to broken pods.
09:45  Root question: why did the pipeline pass? Integration tests ran against a
       docker-compose database using the OLD env var name. Nothing verified the
       real dependency in the real environment.

Follow-ups (owner, date - not "be more careful"):
  1. Readiness probe must verify the DB connection            @dana  14 Aug
  2. Post-deploy smoke test hits a real query before traffic  @kai   14 Aug
  3. Canary promotion gated on 5xx rate, auto-rollback        @sam   21 Aug
  4. CI fails if a referenced secret key is missing per env   @dana  21 Aug
  Detect 2 min (good) - mitigate 4 min (good) - the gap was PREVENTION.
```

```bash
# The mitigation levers, fastest first - know which one your platform gives you
curl -XPOST "$FLAGS/api/flags/new-checkout-flow" -d '{"enabled":false}'   # seconds

aws lambda update-alias --function-name checkout --name live \
  --routing-config '{}' --function-version 41                # drop the canary weight

kubectl rollout undo deployment/checkout -n prod            # imperative clusters
kubectl rollout status deployment/checkout -n prod --timeout=5m

git revert --no-edit 4f3c1ab && git push                    # GitOps: the CORRECT rollback
argocd app sync checkout --prune                            # ...or wait for auto-sync

# Verify on the metrics, not on the deploy status
kubectl -n prod logs -l app=checkout --since=2m | grep -c ' 5[0-9][0-9] '
```

## Interview tips

- Lead with "roll back first, diagnose second", and give the reason: you do not need to understand the bug to stop customer impact. Then say "mitigated" and "resolved" are two different events.
- Order the mitigation levers by speed - feature flag, traffic shift, rollback, shed load - and note that a flag is the fastest because it needs no deploy.
- Say "freeze the pipeline" early. It is a small, concrete action that shows you have actually run an incident with other engineers deploying around you.
- The rollback-cannot-undo list (migrations, data format, consumed messages, cache, third-party side effects) is what marks a senior answer. Follow it immediately with expand/contract as the practice that keeps rollback available.
- If the interviewer gives the classic "passed all tests but the database failed" setup, name the real gap: the pipeline validated code, not the deployed system against its real dependencies. Then propose a dependency-touching readiness probe and a post-deploy smoke test.
- In a GitOps context, be precise: a manual `kubectl rollout undo` gets reconciled away, so the rollback is `git revert`.
- Frame the review around time-to-detect and time-to-mitigate, and prefer one automated gate over several human reminders.
- Have a real story with numbers - what broke, how long, what you changed afterwards - and be willing to say what you would do differently. That self-critique is usually what earns the mark. See [what is an incident response plan](./what-is-an-incident-response-plan.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Incident Management](./README.md) · [All topics](../README.md)
