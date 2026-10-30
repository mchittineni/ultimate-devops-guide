---
title: "How do you roll back a failed deployment in a CI/CD pipeline?"
id: 762
category: "CI/CD"
difficulty: "Intermediate"
tags:
  - devops
  - cicd
  - interview-questions
  - deployment
  - rollback
quiz:
  stem: "A release included a database migration that dropped a column the previous application version still reads. Why does redeploying the previous image not fix the outage?"
  options:
    - "Container registries delete old images after a deployment"
    - "Rollback restores code, not data or schema - the old version now runs against a schema it is incompatible with, so migrations must follow expand/contract to keep the previous version working"
    - "Kubernetes cannot run two image versions at once"
    - "The previous image must be rebuilt from source first"
  answer: 2
  explanation: "Redeploying an artefact only changes code. Schema and data changes persist, so a destructive migration makes the previous version incompatible. Expand/contract migrations - additive first, destructive only after the old version is gone - keep rollback possible."
---

# How do you roll back a failed deployment in a CI/CD pipeline?

**Short answer:** Make rollback a **redeploy of the previous known-good artefact**, not a rebuild and not a hand-made fix: because you built once and deployed by digest, the last good version is already in the registry and the pipeline only has to point the environment back at it. Detect the failure automatically (health checks, error rate, latency, SLO burn rate) and let progressive delivery **abort and revert** a canary or blue/green rollout before most users see it. Turn features off with a **flag** when the code is fine but the feature is not - the fastest rollback of all. The hard limit is state: code rolls back, **data and schema do not**, so migrations must be backward compatible (expand/contract) or rollback is impossible. And rehearse it - an untested rollback path fails on the day you need it.

## Detail

### Roll back or roll forward?

- **Roll back** when the cause is unknown or the impact is high: restoring the previous version is the quickest way to stop the bleeding, and you debug afterwards.
- **Roll forward** (ship a fix) when the fix is small and understood, when rollback is unsafe (an irreversible migration already ran), or when the previous version has its own known problem.

The decision should be made in seconds, so agree the default in advance: "if error rate exceeds the threshold after a deploy, roll back first, ask questions later."

### The mechanisms, by platform

| Platform / strategy      | Rollback action                                                                   |
| ------------------------ | --------------------------------------------------------------------------------- |
| Kubernetes Deployment    | `kubectl rollout undo` (previous ReplicaSet), or redeploy the previous digest     |
| Helm                     | `helm rollback <release> <revision>`; `--atomic`-style upgrades revert on failure |
| GitOps (Argo CD, Flux)   | `git revert` the promotion commit; the controller reconciles back                 |
| Argo Rollouts / Flagger  | Automatic abort when an analysis fails; traffic returns to the stable version     |
| Blue/green               | Switch the load balancer or service selector back to the old colour               |
| AWS ECS / CodeDeploy     | Deployment circuit breaker or CodeDeploy alarm-based automatic rollback           |
| VMs / autoscaling groups | Instance refresh back to the previous AMI or launch template version              |
| Serverless               | Shift the alias back to the previous function version                             |
| Feature flag             | Turn the flag off - no deployment at all                                          |

In GitOps the rollback must go **through Git**: an imperative `kubectl rollout undo` is reverted by the controller on its next sync, so revert the commit (or pause auto-sync deliberately during the incident).

### Automate the trigger

A human watching a dashboard is slow and inconsistent. Define the signal before the release: health checks for crash loops, then golden signals against the previous version - error rate, p99 latency, saturation - ideally as SLO burn rate. Progressive delivery tools run that analysis during a canary (Argo Rollouts `AnalysisTemplate`, Flagger metrics, CodeDeploy CloudWatch alarms) and abort automatically. Post-deploy smoke tests in the pipeline catch the obvious failures in seconds.

### What does not roll back

- **Schema and data.** A dropped column or a rewritten table stays changed. Use expand/contract: add the new structure, deploy code that works with both, migrate data, and remove the old structure only after the previous version is gone from every environment.
- **External side effects.** Emails sent, payments captured, messages published to other services, events consumed by downstream systems. Idempotent consumers and versioned event schemas limit the damage.
- **Configuration and secrets** changed alongside the release. Version them with the artefact (values files in Git, versioned parameters) so they roll back together.
- **Infrastructure** changed by Terraform has no rollback command; you revert the code and apply again, which may replace resources.

### Make it routine

Record exactly which digest was live before each deploy, keep enough old artefacts and Helm revisions (`--history-max`), expose a one-click "deploy version X" pipeline, and run rollback drills in staging so the path is exercised. Afterwards, the post-incident review asks why the bad version passed the gates.

## Example

```yaml
# .github/workflows/rollback.yml - redeploy a known-good digest, never rebuild
name: rollback
on:
  workflow_dispatch:
    inputs:
      environment: { type: choice, options: [staging, production], required: true }
      digest: { type: string, required: true, description: "sha256:... of the last good image" }
permissions:
  contents: read
  id-token: write
concurrency:
  group: deploy-${{ inputs.environment }} # never race a deploy
  cancel-in-progress: false
jobs:
  rollback:
    runs-on: ubuntu-24.04
    environment: ${{ inputs.environment }} # same approvals and scoped credentials as a deploy
    steps:
      - uses: actions/checkout@v7
      - uses: aws-actions/configure-aws-credentials@v6
        with:
          role-to-assume: arn:aws:iam::111122223333:role/deploy-${{ inputs.environment }}
          aws-region: eu-west-1
      - run: aws eks update-kubeconfig --name "${{ inputs.environment }}"
      - env:
          DIGEST: ${{ inputs.digest }} # via env, not inline, to avoid script injection
        run: |
          kubectl set image deploy/checkout app="registry.example.com/checkout@${DIGEST}"
          kubectl rollout status deploy/checkout --timeout=5m
```

```bash
# The fast imperative paths, when the platform is not GitOps-managed
kubectl rollout history deploy/checkout
kubectl rollout undo deploy/checkout --to-revision=41
helm history checkout -n shop && helm rollback checkout 17 -n shop --wait

# GitOps: roll back through Git so the controller does not undo your undo
git revert --no-edit <promotion-commit-sha> && git push
```

## Interview tips

- Lead with "redeploy the previous artefact by digest" and explain why build-once makes that fast and safe; rebuilding the old version is not a rollback.
- Distinguish rollback from roll-forward and say when each is right, including that an irreversible migration forces roll-forward.
- Name automatic triggers - health checks, error rate, latency, SLO burn rate - and the tools that act on them (Argo Rollouts, Flagger, CodeDeploy alarms).
- Bring up the state limit unprompted: schema and data do not roll back, so expand/contract migrations are what keep rollback possible.
- In GitOps, roll back by reverting the commit; an imperative undo is reconciled away.
- Mention feature flags as the fastest rollback and rollback drills as the proof it works. See [deployment strategies](../devops-tools-and-automation/what-are-deployment-strategies.md), [promoting a release across environments](./how-do-you-promote-a-release-across-dev-staging-and-production.md), and [rolling back a Kubernetes rolling update](../kubernetes/how-do-you-perform-and-roll-back-a-rolling-update-in-kubernetes.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is progressive delivery and how does it differ from traditional deployment strategies?]] (`#509`): [What is progressive delivery and how does it differ from traditional deployment strategies?](../core-devops-concepts/what-is-progressive-delivery-and-how-does-it-differ-from-traditional-deployment-strategies.md)
- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#511`): [What is the difference between Continuous Delivery and Continuous Deployment?](../core-devops-concepts/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)
- [[How do you troubleshoot a GitOps pipeline that will not sync?]] (`#428`): [How do you troubleshoot a GitOps pipeline that will not sync?](../devops-tools-and-automation/how-do-you-troubleshoot-a-gitops-pipeline-that-will-not-sync.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
