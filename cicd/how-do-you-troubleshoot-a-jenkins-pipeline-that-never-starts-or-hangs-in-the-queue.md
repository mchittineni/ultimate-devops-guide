---
title: "How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?"
id: 402
category: "CI/CD"
difficulty: "Intermediate"
tags:
  - devops
  - cicd
  - interview-questions
  - version-control
  - linux-administration
---

# How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?

**Short answer:** Split the problem in two, because the causes are unrelated. If the job **never appears**, the trigger failed - check the webhook delivery on the Git provider first (it records the response code), then Jenkins' reachability, the token, and the branch or path filters. If the job **appears but sits in the queue**, hover the queue item: Jenkins states the reason. It is almost always no executor free, no agent matching the requested label, an agent offline, or a `throttle`/concurrency lock. Fix the immediate blockage, then remove the class of problem - autoscaled ephemeral agents, monitored agent connectivity, and a queue-time alert.

## Detail

### Case 1: the build never appears

Work outward from the sender:

1. **Check the webhook delivery log** on GitHub, GitLab, or Bitbucket - it shows every attempt with the request body and Jenkins' response. This one screen usually ends the investigation:
   - `HTTP 403` - the CSRF crumb or authentication is rejected; the webhook needs the correct endpoint and token.
   - `HTTP 404` - wrong path. The endpoint differs by plugin (`/github-webhook/`, `/gitlab-webhook/post`, `/generic-webhook-trigger/invoke`) and the trailing slash matters.
   - **Timeout or connection refused** - Jenkins is not reachable from the internet, or a firewall, security group, or reverse proxy is blocking it.
   - `HTTP 200` **but no build** - the trigger arrived and Jenkins chose not to build. Move to the next step.
2. **Confirm Jenkins accepted and filtered it.** Check the multibranch or organisation folder's **Scan Repository Log**, and the job's configuration: is the branch inside the "Discover branches" or `when { branch }` filter? Is a path filter excluding the changed files? For pipelines defined in the repository, does `Jenkinsfile` exist on _that_ branch? Is the job disabled? Is the "quiet period" swallowing the trigger?
3. **Check the plumbing that silently changes behaviour** - a proxy stripping headers, a shared-library resolution failure (which fails the build before any stage output), or a `Jenkinsfile` parse error that shows only in the log of a build you have not noticed.
4. **Prove the path manually.** Re-deliver the webhook from the provider's UI, or `curl` the endpoint with a representative payload. If a manual trigger builds fine, the problem is entirely upstream.

For scheduled jobs, remember `H` in cron (`H/15 * * * *`) spreads load and is not literal, and a timezone difference explains most "it ran an hour late".

### Case 2: the build is queued but never runs

The queue item's tooltip states the reason - read it before theorising. The recurring causes:

- **No executor available.** The controller or agent has fewer executors than concurrent demand. Check total executors versus queue depth over time; if queue time is a large share of pipeline duration, you have a capacity problem, not a build problem. See [how do you speed up a slow CI/CD pipeline](./how-do-you-speed-up-a-slow-ci-cd-pipeline.md).
- **Label mismatch.** `agent { label 'linux-docker' }` matches nothing because the agent is gone, renamed, or the label was misspelled. "Jenkins doesn't have label X" in the tooltip is definitive.
- **Agent offline or disconnected.** Common reasons: the agent process died, the JNLP/SSH connection dropped, a Java version mismatch after an upgrade, the agent's disk is full (Jenkins takes agents offline below a free-space threshold), the workspace disk is exhausted, or the controller-to-agent version skew after a controller upgrade.
- **Concurrency limits and locks.** `disableConcurrentBuilds()`, a `lock()` resource held by a hung build, throttle-category limits, or a `milestone` waiting on an earlier build. A stuck upstream build blocks everything behind it.
- **Node offline by policy** - marked offline temporarily by an operator, or an ephemeral cloud agent that failed to provision (check the cloud plugin's log: quota exceeded, no capacity in the availability zone, bad AMI or pod template, image pull failure for Kubernetes agents).
- **The controller itself is unhealthy.** A long GC pause, an exhausted thread pool, or a full `$JENKINS_HOME` disk stalls scheduling entirely; check the controller's load statistics and system log.

### Removing the class of problem

Run agents as **ephemeral and autoscaled** (Kubernetes pod templates, EC2 fleet, or Docker Cloud) so capacity follows demand and a broken long-lived agent cannot accumulate state. Monitor and alert on **queue time**, **agents offline**, and **`$JENKINS_HOME` free space** - all three are leading indicators. Keep the controller stateless in configuration terms (Configuration as Code plus job DSL or multibranch discovery) so rebuilding it is routine, and back up `$JENKINS_HOME` because that is where the state you cannot regenerate lives. For availability, an active/passive controller with shared persistent storage plus fast rebuild is the pragmatic pattern - Jenkins controllers do not run active/active, and claiming they do is a common interview error.

## Example

```groovy
// A pipeline that fails loudly instead of hanging
pipeline {
  agent { label 'linux-docker' }          // must match a real, online agent label
  options {
    timeout(time: 30, unit: 'MINUTES')    // never let a build hang for ever
    disableConcurrentBuilds(abortPrevious: true)  // supersede, do not queue behind
    buildDiscarder(logRotator(numToKeepStr: '30'))
  }
  triggers { pollSCM('H/15 * * * *') }    // fallback if the webhook is ever lost
  stages {
    stage('Build') { steps { sh 'make build' } }
  }
}
```

```bash
# Is anything actually connected and free? (Jenkins CLI or script console)
curl -s -u "$USER:$TOKEN" "$JENKINS/computer/api/json?tree=computer[displayName,offline,offlineCauseReason,numExecutors,idle]" | jq

# What is the queue waiting for - Jenkins tells you in plain text
curl -s -u "$USER:$TOKEN" "$JENKINS/queue/api/json?tree=items[why,task[name],inQueueSince]" | jq -r \
  '.items[] | "\(.task.name): \(.why)"'
# checkout-api: Jenkins doesn't have label 'linux-docker'
# orders-api:   Waiting for next available executor on 'agent-03'

# On the agent, the two things that take it offline silently
df -h /var/lib/jenkins /tmp && java -version
```

## Interview tips

- Split the question into "never triggered" and "queued but not running" in your first sentence. Interviewers ask this to see whether you diagnose or guess.
- The single highest-value line is "I would look at the webhook delivery log on the Git provider first, because it records the response code Jenkins returned". Very few candidates say it.
- Know the queue reasons by name - no executor, no matching label, agent offline, concurrency lock - and that Jenkins displays the reason on the queue item.
- Mention disk space taking an agent offline. It is the most common real cause and it surprises people.
- Add `timeout()` and `disableConcurrentBuilds(abortPrevious: true)` as the hygiene that turns a hang into a failure and stops the queue from filling with superseded runs.
- If asked about high availability, be precise: Jenkins controllers are active/passive, so the answer is fast rebuild plus backed-up `$JENKINS_HOME`, ephemeral agents, and configuration as code - not "run three replicas".
- Close on prevention: alert on queue time and offline agents, and keep `pollSCM` as a cheap safety net for a lost webhook. See [what is Jenkins](./what-is-jenkins.md) and [what are Jenkins pipelines](./what-are-jenkins-pipelines.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot a GitOps pipeline that will not sync?]] (`#428`): [How do you troubleshoot a GitOps pipeline that will not sync?](../devops-tools-and-automation/how-do-you-troubleshoot-a-gitops-pipeline-that-will-not-sync.md)
- [[How do you rotate secrets without downtime?]] (`#429`): [How do you rotate secrets without downtime?](../devsecops/how-do-you-rotate-secrets-without-downtime.md)
- [[How do you manage build artefacts with Nexus or Artifactory?]] (`#460`): [How do you manage build artefacts with Nexus or Artifactory?](../devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
