---
title: "How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?"
id: 455
category: "CI/CD"
difficulty: "Intermediate"
tags:
  - devops
  - cicd
  - interview-questions
  - version-control
---

# How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?

**Short answer:** There are five mechanisms, and choosing correctly matters more than knowing all of them. **Webhooks** are the default for code changes: the SCM pushes an event the instant a commit or pull request lands, so builds start in seconds and nothing is wasted. **Polling** (`pollSCM`) asks the SCM on a schedule - use it only when the SCM cannot reach your controller (no inbound network path), because it scales badly and adds latency. **Schedules** (`cron`, `triggers { cron('H 2 * * *') }`) are for work that is time-driven rather than change-driven: nightly integration runs, security scans, dependency updates, cache warms. **Upstream/downstream** triggers chain jobs (`build job:` or `upstream()`), which is how "pipeline B runs after pipeline A succeeds" works. And **manual/API** triggers - a button, `curl` on the build URL with a token, `workflow_dispatch`, or a repository dispatch event - cover releases and cross-system integration. The rule of thumb: webhook for anything driven by a commit, cron for anything driven by the clock, upstream for anything driven by another pipeline's result, and manual for anything a human must authorise.

## Detail

### Webhooks: how they actually work, and how they fail

The SCM (GitHub, GitLab, Bitbucket) sends an HTTP POST to your CI endpoint on push, pull-request, tag, or comment events. In Jenkins, the modern setup is the GitHub/GitLab plugin with a **multibranch pipeline** or organisation folder: one webhook per repository (or per org) and Jenkins figures out branches, PRs, and tags itself.

A fresh Jenkins install does **not** get webhooks for free - the interview question "is webhook communication achievable out of the box?" has a specific answer. You need: the SCM plugin installed and credentials configured, the Jenkins URL reachable **from** the SCM (which for a private controller means an ingress, a reverse proxy, or the SCM's IP allowlist), the webhook created in the repository or organisation pointing at `/github-webhook/` or `/gitlab-webhook/`, and a shared secret so the endpoint is not anonymous. On GitHub, "Manage hooks" permission on the token lets Jenkins create the hook automatically; otherwise it is a manual step. If the controller is not internet-reachable, the fallbacks are polling, a self-hosted runner/agent that polls outward, or an SCM app that establishes an outbound connection.

Debugging is nearly always the same three checks: **the SCM's delivery log** (did it send, what response did it get - 200, 403, timeout?), the controller's log for a rejected payload or signature, and the job's branch/path filters silently excluding the event. "The pipeline runs but no build happens" usually means the job triggered and then every stage was skipped by a `when` guard or a path filter.

### Polling versus webhooks

|                                    | Webhook                     | Polling                                                                   |
| ---------------------------------- | --------------------------- | ------------------------------------------------------------------------- |
| Latency                            | Seconds                     | Up to the poll interval                                                   |
| Load                               | One request per real change | Every job asks the SCM on every interval, forever                         |
| Requires inbound access to CI      | Yes                         | No                                                                        |
| Scales to hundreds of repositories | Yes                         | Poorly - a known cause of controller CPU saturation and SCM rate limiting |
| Good for                           | Everything normal           | Air-gapped controllers, SCMs without webhook support                      |

Note the hybrid that solves most real constraints: **multibranch scan** on a schedule (`Scan Repository Triggers` / periodic indexing) detects new branches and PRs without per-job polling, and webhooks handle the commits. If someone tells you "we poll every minute across 300 jobs", that is the thing to fix.

### Schedules and the `H` you should always use

`triggers { cron('H 2 * * *') }` - the `H` (hash) spreads jobs deterministically across the interval based on the job name, so 200 nightly jobs do not all start at 02:00:00 and flatten the controller. Prefer `H 2 * * *` over `0 2 * * *` for that reason alone. Cron in Jenkins has the same five fields as Unix, plus `H`, ranges (`H(0-29)`), and aliases (`@daily`, `@midnight`).

`pollSCM` and `cron` look identical syntactically and are frequently confused: `cron` builds unconditionally on the schedule; `pollSCM` checks the SCM on the schedule and builds **only if something changed**.

### Chaining pipelines

- **Downstream from upstream**: `build job: 'deploy-staging', wait: false, parameters: [string(name: 'IMAGE', value: env.IMAGE)]` at the end of pipeline A. Explicit and passes context.
- **`triggers { upstream(upstreamProjects: 'build-api', threshold: hudson.model.Result.SUCCESS) }`** in pipeline B, so B declares its own dependency. Better when many pipelines depend on one upstream.
- **Artefact or event driven**: publish an image/artefact and let the next stage trigger from a registry webhook or a GitOps controller noticing the new tag. This decouples the pipelines entirely and is the GitOps-native answer.

Say which you would choose and why: parameterised `build job:` when the two pipelines are one logical delivery flow, `upstream()` when ownership is separate, event-driven when you want no coupling at all.

### Filtering: the part that saves the most compute

Triggering is only half the job; **not** running is the other half.

- **Branch and tag filters** - build `main` and PRs, tag builds go to the release pipeline.
- **Path filters** - in a monorepo, `paths:` (GitHub Actions) or `changeset` conditions (Jenkins `when { changeset "services/api/**" }`) so a docs change does not rebuild twenty services.
- **Concurrency control** - `disableConcurrentBuilds()` / GitHub Actions `concurrency: { group: ..., cancel-in-progress: true }` so a rapid series of pushes does not run five overlapping deploys; the newest supersedes the rest. For deploy pipelines, use `cancel-in-progress: false` with a queue instead, because cancelling a half-finished deploy is worse than serialising.
- **Skip conditions** - `[skip ci]` in a commit message, and ignoring events from the CI's own bot commits to avoid infinite trigger loops. That loop - pipeline commits a version bump, which triggers the pipeline - is a real outage people cause once.

### PR triggers and the security boundary

For pull requests from forks, the event carries untrusted code. GitHub Actions distinguishes `pull_request` (runs in the fork's context, no secrets, read-only token) from `pull_request_target` (runs in the base repo's context **with** secrets - and is the source of most CI compromises when it checks out the PR's head). Jenkins has the equivalent decision in the GitHub Branch Source "build fork PRs" and "trust" settings. Answering a trigger question with this distinction is a strong signal: **never expose secrets to a trigger that runs untrusted code**, and require approval for first-time contributors.

### "Only build after N commits"

Occasionally asked, and the honest answer is that CI systems trigger per event, not per count - so you implement it: a scheduled job that checks the commit count since the last successful build and exits early otherwise, or a webhook-triggered job whose first stage does that check and aborts. Say that you would push back on the requirement first, because batching commits delays feedback, which is the opposite of what CI is for.

## Example

```groovy
// Jenkins declarative: several triggers, plus the filters that keep it cheap
pipeline {
  agent none
  triggers {
    // webhook is configured in the SCM; this covers the fallback and the clock
    pollSCM('H/15 * * * *')          // only if the SCM cannot reach Jenkins
    cron('H 2 * * 1-5')              // nightly integration suite, spread by H
    upstream(upstreamProjects: 'platform/build-base-images',
             threshold: hudson.model.Result.SUCCESS)
  }
  options { disableConcurrentBuilds(); timeout(time: 45, unit: 'MINUTES') }
  stages {
    stage('Unit tests') {
      agent { label 'linux' }
      when { anyOf { branch 'main'; changeRequest() } }
      steps { sh 'make test' }
    }
    stage('Rebuild only what changed') {
      agent { label 'linux' }
      when { changeset "services/api/**"; beforeAgent true }
      steps { sh 'make -C services/api build' }
    }
    stage('Trigger deployment') {
      when { branch 'main' }
      steps {
        build job: 'deploy/staging', wait: false,
              parameters: [string(name: 'IMAGE_TAG', value: env.GIT_COMMIT.take(12))]
      }
    }
  }
}
```

```yaml
# GitHub Actions: the same five mechanisms, declaratively
on:
  push:
    branches: [main]
    paths: ["services/api/**", ".github/workflows/api.yml"] # monorepo filter
    tags-ignore: ["v*"] # tags go to the release workflow
  pull_request: # fork-safe: no secrets, read-only token
    branches: [main]
  schedule:
    - cron: "17 2 * * *" # off-the-hour: shared runners are less contended
  workflow_dispatch: # manual, with inputs
    inputs:
      environment:
        type: choice
        options: [staging, production]
  workflow_run: # downstream of another workflow
    workflows: ["build-base-images"]
    types: [completed]
  repository_dispatch: # external system triggers us via the API
    types: [image-published]

concurrency:
  group: api-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }} # cancel PRs, queue deploys
```

```bash
# Debugging "the webhook did not fire" - in order
# 1. did the SCM send it, and what did it get back?
gh api repos/acme/api/hooks/12345678/deliveries | jq -r '.[0] | .status_code, .event'

# 2. is the endpoint reachable from the SCM's network at all?
curl -sS -o /dev/null -w '%{http_code}\n' https://jenkins.example.com/github-webhook/

# 3. trigger manually to separate "trigger broken" from "pipeline broken"
curl -X POST -u "$USER:$API_TOKEN" \
  "https://jenkins.example.com/job/api/job/main/build?token=$JOB_TOKEN"
gh workflow run api.yml -f environment=staging      # GitHub Actions equivalent
```

## Interview tips

- Enumerate the five mechanisms and pair each with its natural use: webhook for commits, cron for clock-driven work, polling only when there is no inbound path, upstream for pipeline chaining, manual/API for releases and external systems. That structure answers "how many ways can a pipeline be triggered?" completely.
- For "is webhook communication available out of the box on a fresh Jenkins?", say no and list what is needed: SCM plugin and credentials, a Jenkins URL reachable _from_ the SCM, the hook created with a shared secret. That specificity is what the question is testing.
- Give the polling trade-off in one line - latency plus load on every interval versus one request per real change - and mention SCM rate limiting at scale.
- Use `H` in Jenkins cron and explain why: it spreads load deterministically instead of stampeding at the top of the hour. Small detail, strong signal.
- Distinguish `cron` from `pollSCM` explicitly; they look the same and mean different things.
- Volunteer filtering as the other half of the answer: branch and path filters for monorepos, concurrency groups so overlapping pushes do not run overlapping deploys, and `[skip ci]` plus ignoring bot commits to avoid trigger loops.
- Raise the fork-PR security boundary - `pull_request` versus `pull_request_target`, secrets never exposed to untrusted code. Very few candidates bring this up unprompted and it matters. See [how do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue](./how-do-you-troubleshoot-a-jenkins-pipeline-that-never-starts-or-hangs-in-the-queue.md), [declarative versus scripted pipelines](./what-is-the-difference-between-a-declarative-and-a-scripted-jenkins-pipeline.md), [writing an efficient and secure GitHub Actions workflow](./how-do-you-write-an-efficient-and-secure-github-actions-workflow.md), and [scaling CI/CD across many services and teams](./how-do-you-scale-ci-cd-across-many-services-and-teams.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you troubleshoot a GitOps pipeline that will not sync?]] (`#428`): [How do you troubleshoot a GitOps pipeline that will not sync?](../devops-tools-and-automation/how-do-you-troubleshoot-a-gitops-pipeline-that-will-not-sync.md)
- [[How do you manage build artefacts with Nexus or Artifactory?]] (`#460`): [How do you manage build artefacts with Nexus or Artifactory?](../devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md)
- [[How do you rotate secrets without downtime?]] (`#429`): [How do you rotate secrets without downtime?](../devsecops/how-do-you-rotate-secrets-without-downtime.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
