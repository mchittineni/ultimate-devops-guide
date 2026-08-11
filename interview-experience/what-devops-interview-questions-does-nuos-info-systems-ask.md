---
title: "What DevOps interview questions does NUOS INFO Systems ask?"
id: 351
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - nuos-info-systems
  - infrastructure-as-code
  - azure-engineering
  - cicd
  - version-control
  - docker
  - monitoring-and-logging
  - cloud-migration
---

# What DevOps interview questions does NUOS INFO Systems ask?

## Questions

The candidate recorded the stack up front: mainly Terraform, Azure, Azure DevOps, Docker, and Git.

**Terraform at scale**

- **How do you scale a Terraform pipeline that takes more than 25 minutes?**
- **What happens to the state file if someone deletes resources directly in Azure?**
- **If the pipeline fails because resources already exist, how do you handle the remove-import-plan cycle?**
- **How do you export existing Azure resources into Terraform code?**
- **How do you enforce Azure Policies — tag or location restrictions, for example — through Terraform at scale?**

**Repository and pipeline design**

- **What are the best practices for structuring repositories and pipelines in a large DevOps project?**
- **The pipeline fails only on Tuesdays and there have been no code changes. How do you debug that?**
- **Which tools would you recommend for CI/CD, artefact storage, vulnerability scanning, and a container registry in a hybrid on-premises-plus-Azure setup?**
- **How do you use the Azure DevOps REST API to apply a security policy to every repository programmatically?**
- **How do you assess readiness for an Azure DevOps migration and plan the transition?**
- **How do you manage both AWS and Azure through a single DevOps process, with a focus on security and cost?**

**Observability**

- **Logs are incomplete. How do you troubleshoot across AKS, the ingress, the application, and the infrastructure?**
- **How do you monitor memory on an Azure VM and alert when it goes above 80%?**

**Docker**

- **How do you write a multi-stage Dockerfile for a Node.js application that removes secrets and unnecessary layers?**

**Git recovery**

- **What is the difference between `git merge` and `git rebase`?**
- **Someone force-pushed and the `main` branch was lost. How do you recover it?**
- **How do you push the recovered branch back to the remote?**

## Example

```text
NUOS INFO Systems — DevOps Engineer (4 YOE), reported round
17 questions

  Terraform at scale          5   25-minute pipeline, out-of-band deletion,
                                  remove-import-plan, export Azure to HCL,
                                  Azure Policy as code
  Repo / pipeline design      6   large-project structure, Tuesday-only
                                  failure, hybrid toolchain, ADO REST API
                                  at scale, migration readiness, AWS+Azure
  Git recovery                3   merge vs rebase, recover a force-pushed
                                  main, push it back
  Observability               2   incomplete logs across 4 layers,
                                  Azure VM memory alert at 80%
  Docker                      1   multi-stage Node.js without secrets

THE STANDOUT QUESTION
  "Fails only on Tuesdays, no code changes." There is no tool that answers
  this — it tests whether you reason about time-correlated causes instead of
  re-reading the pipeline YAML.
```

## Interview tips

- The Tuesday-only failure is the question worth preparing hardest, because the answer is a way of thinking. Say the reasoning first: nothing in the code changed, so the variable is time, and something on a weekly cycle is the cause. Then enumerate candidates — a weekly scheduled job or maintenance window competing for the same resource, a certificate or token that renews weekly, a Monday-night backup or database maintenance still running, a weekly cache or cleanup task, a partner system's batch window, upstream dependency rate limits reset weekly, agent pool contention because every team schedules releases on Tuesday, or a cron expression with a day-of-week field someone set and forgot. Then say how you would confirm it: correlate the failure timestamps precisely, compare a passing run's logs with a failing one at the same stage, and check the platform's own maintenance and audit logs. Correlate before you change anything.
- The out-of-band deletion question has an exact answer: the state file is _unchanged_ — Terraform still records the resource as existing, because state is only updated when Terraform runs. The drift appears at the next `plan` or refresh, which reports the resource as needing to be created. Say that recreating the resource does not recover its _data_, so anything stateful needs a backup, and that scheduled `plan -refresh-only` in CI is how you detect this before someone else does. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- For the 25-minute pipeline, split the answer between Terraform-specific and pipeline-generic levers. Terraform: split one huge state into smaller per-component states so each plan touches less, use `-refresh=false` where safe or targeted refresh, raise `-parallelism`, cut provider and module download time by caching the plugin directory, and remove data sources that call slow APIs on every run. Pipeline: run `plan` on the pull request and `apply` on merge so you are not paying for both, cache the `.terraform` directory, and run independent stacks in parallel jobs. Say that state size is usually the real cause — a state file with thousands of resources refreshes slowly no matter what else you do.
- The remove-import-plan question is about reconciling reality with code. Give the sequence: identify the conflicting resource from the "already exists" error, decide whether it should be managed (import it) or discarded, then either `terraform import` — or better, an `import` block with `-generate-config-out` so the operation is planned and reviewable — and iterate `plan` until it reports no changes. `terraform state rm` is the counterpart when you want Terraform to forget a resource without destroying it. Say that an empty plan is the proof you got it right. For the Azure export question, name `aztfexport` (formerly `aztfy`) as the purpose-built tool. See [importing existing cloud infrastructure into Terraform](../infrastructure-as-code/how-do-you-import-existing-cloud-infrastructure-into-terraform.md).
- Azure Policy through Terraform at scale means policy _definitions_ and _initiatives_ assigned at management-group scope, not per-resource-group, so every subscription inherits them — with `deny` effects for hard rules such as allowed locations, `modify` or `append` to add missing tags automatically, and `audit` for anything you cannot enforce yet. Say that this is guardrails-as-code and that it is more reliable than trying to enforce tagging conventions inside Terraform modules, because it also catches resources created outside Terraform. See [what a cloud landing zone is](../cloud-engineering/what-is-a-cloud-landing-zone.md) and [scanning infrastructure as code before it is applied](../devsecops/how-do-you-scan-infrastructure-as-code-before-it-is-applied.md).
- The force-push recovery pair should be answered with confidence, because it is a very common real incident. The lost commits still exist in the repository until garbage collection, so recover with `git reflog` on any clone that has them — including a developer's local copy — find the pre-push commit, and `git branch recovered <sha>`. On the server side, Azure DevOps and GitHub keep a push or ref log, and `git fsck --lost-found` finds dangling commits. To push it back: `git push --force-with-lease origin recovered:main`, and say why `--force-with-lease` rather than `--force` — it refuses if the remote has moved since you last fetched, so you cannot destroy someone else's work while fixing your own. Finish with prevention: branch protection forbidding force-push to `main`. See [recovering from a bad Git history rewrite](../version-control/how-do-you-recover-from-a-bad-git-history-rewrite.md).
- The Azure VM memory question has a trap identical to CloudWatch on AWS: memory is a guest-OS metric and is _not_ collected by default. You need the Azure Monitor agent with a data collection rule gathering the memory performance counter, then a metric alert with a threshold at 80% and an action group to notify. Volunteering that gap is what earns the point. See [monitoring in DevOps](../monitoring-and-logging/what-is-monitoring-in-devops.md).
- Incomplete logs across four layers is a gap-analysis question, so answer per layer and name what breaks each one. Application: is it writing to stdout rather than a file, and is the log level too high? Ingress: is access logging enabled on the controller at all — it often is not by default? AKS platform: are the container-insights data collection rules capturing the right namespaces, and is a log rotation limit truncating output before the agent reads it? Infrastructure: are activity and diagnostic settings routed to the workspace? Then the cross-cutting causes: agent back-pressure and dropped records under load, sampling, and retention deleting what you are looking for. Say you would first prove whether logs are _not produced_ or _produced and not shipped_ — that split determines everything else.
- For the hybrid toolchain recommendation, give one option per slot with a reason rather than a list of everything: Azure DevOps or GitHub Actions with self-hosted agents on-premises for CI/CD, Azure Artifacts or a self-hosted Nexus/Artifactory for artefacts, Trivy or Defender for Cloud for vulnerability scanning, and Azure Container Registry with a geo-replicated or on-premises cache for images. Say that the deciding constraint in hybrid is usually network egress and where the build agents must sit for data-residency reasons.
- The AWS-plus-Azure question wants one process, not two: a single IaC tool with per-provider modules, one identity source federated to both clouds, a common tagging and naming standard enforced by policy in each, centralised logging and cost reporting across both, and one pipeline pattern. Then say the honest trade-off — a genuinely cloud-agnostic layer costs you the best managed services on each side, so most teams standardise the _process_ and accept provider-specific implementations. See [the real trade-offs of multi-cloud](../cloud-engineering/what-are-the-real-trade-offs-of-multi-cloud.md).
- The Node.js multi-stage Dockerfile has three specific things they asked for. Build stage: `npm ci` from the lockfile for reproducibility, then build. Runtime stage: copy only `dist` and production `node_modules`, on a slim or distroless base, running as a non-root user. And on secrets: never `ARG` or `ENV` a token, because it persists in the image history — use BuildKit's `--mount=type=secret` so it exists only during that build step, and add a `.dockerignore` covering `.env`, `.git`, and local `node_modules`. See [reducing Docker image size and build time](../docker/how-do-you-reduce-docker-image-size-and-build-time.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?]] (`#455`): [How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?](../cicd/how-do-you-trigger-a-pipeline-webhooks-polling-schedules-and-upstream-jobs.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
