---
title: "What cloud platform engineering interview questions does UST ask?"
id: 387
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - ust
  - infrastructure-as-code
  - cicd
  - aws-engineering
  - backup-and-disaster-recovery
  - devsecops
  - scalability-and-high-availability
  - advanced-devops-cloud
---

# What cloud platform engineering interview questions does UST ask?

## Questions

**Terraform**

- **Something was created on the cloud platform but is not present in Terraform. How do you bring it under management?**
- **`terraform apply` is creating all the resources again. What could be the problem?**
- **If somebody deleted the Terraform state file locally, what can be done?**
- **Write Terraform to create an EC2 instance, with variables for `instance_type` and `region`.**
- **You need to create 50 instances in one go. How would you do that in Terraform?**

**Troubleshooting and reliability**

- **If a Python program is failing because of memory problems, what could be the cause?**
- **If a production instance is failing, what are the possible causes?**
- **There is a sudden spike in traffic on the server. How do you troubleshoot it?**
- **In a disaster recovery scenario, what do you do if users cannot access the application?**

**CI/CD and security**

- **A CI pipeline takes 45 minutes to run. How can you optimise it?**
- **Credentials are visible in the CI/CD pipeline logs. What do you do?**
- **Explain blue-green deployment.**

**AI in platform work**

- **How can AI assist with cloud infrastructure monitoring?**
- **How can AI assist developers in increasing their productivity?**

## Example

```text
UST — Cloud Platform Engineer (3-5 YOE), reported round
14 questions

  Terraform                   5   import an unmanaged resource, apply
                                  recreating everything, state deleted
                                  locally, write EC2 with variables,
                                  50 instances at once
  Troubleshooting             4   Python memory failure, production instance
                                  failing, sudden traffic spike, DR outage
  CI/CD and security          3   45-minute pipeline, credentials in logs,
                                  blue-green
  AI in platform work         2   AI for infrastructure monitoring,
                                  AI for developer productivity

THE UNUSUAL PAIR
  Two questions about AI — for monitoring and for developer productivity.
  Almost no other round in this collection asks this, and a vague answer
  ("it helps with automation") is worse than none. Prepare specifics.
```

## Interview tips

- "`terraform apply` is creating all the resources again" has a small set of causes and naming them in order is the answer. Almost always the state is not where Terraform expects it: `terraform init` was never run against the remote backend so it is using an empty local state; the backend configuration changed (different bucket, key, or workspace) so it initialised a fresh state; you are in the wrong workspace; or the state file was deleted or emptied. Less commonly, resource _addresses_ changed — a rename, or moving resources into a module — so Terraform sees the old addresses as gone and the new ones as absent, which is what `moved` blocks and `terraform state mv` exist to prevent. Say the diagnostic: run `terraform state list` first, and if it is empty you have a state problem rather than a configuration problem. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- The deleted-local-state question should be answered with an important clarification first: if a remote backend is configured, a deleted _local_ file is irrelevant — the authoritative state is remote and `terraform init` simply pulls it again. That distinction is the answer. If the state genuinely was local-only, recovery goes: `terraform.tfstate.backup` in the same directory, then any copy in CI artefacts or a colleague's machine, and failing all that you rebuild state by importing each resource until `terraform plan` reports no changes. Say the infrastructure is untouched throughout — only Terraform's knowledge of it is gone — and that this is precisely why remote state with versioning is non-negotiable. See [recovering a lost or corrupted Terraform state file](../infrastructure-as-code/how-do-you-recover-a-lost-or-corrupted-terraform-state-file.md).
- Bringing an unmanaged resource under Terraform is `terraform import`, but the better modern answer is an `import` block in configuration with `-generate-config-out`, so the operation appears in a reviewable plan and Terraform scaffolds the HCL for you. Say the two things that matter: import populates state but does **not** write your configuration, so you still author the resource block to match reality; and an empty `terraform plan` afterwards is how you prove you got it right. See [importing existing cloud infrastructure into Terraform](../infrastructure-as-code/how-do-you-import-existing-cloud-infrastructure-into-terraform.md).
- The 50-instances question is a `count` versus `for_each` question in disguise. `count = 50` is the literal answer and is fine for 50 genuinely identical instances. But say why `for_each` over a map is usually better: with `count`, resources are addressed by numeric index, so removing one from the middle re-indexes everything above it and Terraform destroys and recreates resources that did not change — whereas `for_each` keys each instance by a stable string so removals are surgical. Then add the real-world point: for 50 identical instances you would not use Terraform's loop at all, you would use an **Auto Scaling group**, because that also gives you health-check replacement and elasticity. Offering the better architecture, not just the syntax, is what a platform engineer does.
- The two AI questions need concrete, defensible answers rather than enthusiasm. For **monitoring**: anomaly detection on metrics so you alert on deviation from a learned baseline rather than a static threshold — which is exactly what CloudWatch Anomaly Detection and Azure Monitor's dynamic thresholds do; log clustering to collapse thousands of lines into a handful of distinct error signatures; alert correlation and grouping to cut noise during an incident; forecasting for capacity planning; and LLM-assisted incident summarisation that drafts a timeline from logs and alerts for a human to verify. Then state the limits honestly — these tools produce hypotheses, not conclusions, they need labelled feedback to stop being noisy, and you must never let a model take an automated remediation action you cannot audit or roll back. For **developer productivity**: code completion and test generation, pull-request summarisation and first-pass review, generating IaC or pipeline boilerplate, and explaining unfamiliar code — with the caveats that output must be reviewed, that generated code can carry licence and security risk, and that secrets must never be pasted into a third-party tool. Naming the limits is what makes this answer credible rather than promotional. See [observability](../advanced-devops-cloud/what-is-observability.md).
- The credentials-in-pipeline-logs question is an incident, and the order of operations is what is being graded. **Revoke and rotate the credential first** — it is compromised the moment it appeared in a log, and logs are often readable by anyone with repository access and may be replicated to a log aggregator. Then check for use during the exposure window via CloudTrail or the provider's audit log. Then purge: delete the build logs, and remember any copy in an external logging system or artefact retention. Only then fix the cause — mark the variable as secret so it is masked, use `withCredentials` or the platform's secret store, avoid `set -x` and `echo` on secret-bearing lines, note that interpolating a secret inside a double-quoted Groovy string leaks it, and add secret scanning to catch it next time. Best of all, remove the standing credential entirely with OIDC federation so the pipeline gets a short-lived token. Say "rotate before you clean up" — tidying first while the key stays valid is the classic mistake. See [preventing and handling secret leaks in CI/CD](../cicd/how-do-you-prevent-and-handle-secret-leaks-in-ci-cd-pipelines.md).
- The Python memory question wants causes, not tools, so give categories: loading an entire dataset into memory instead of streaming or chunking it; a genuine leak from unbounded caches, module-level accumulators, or objects held by a reference you forgot — including reference cycles with `__del__` that the collector cannot reclaim; large intermediate copies from list comprehensions or `pandas` operations that duplicate a frame; C-extension leaks that Python's own tooling cannot see; and the container case, where the process is fine but the **memory limit** is too low, so it is `OOMKilled` with exit code 137. Then the diagnostic path: `tracemalloc` or `memory_profiler` for allocation hotspots, `objgraph` for what is holding references, two heap snapshots diffed to find what grows, and `container_memory_working_set_bytes` to confirm whether the limit rather than the code is the problem. Say that a generator instead of a list is the fix in a surprising number of real cases. See [debugging a Linux performance problem from first principles](../linux-administration/how-do-you-debug-a-linux-performance-problem-from-first-principles.md).
- "A production instance is failing" is deliberately open, so impose structure: separate the _instance_ failing from the _application on it_ failing, because the answers diverge. Instance level: EC2 status checks (system versus instance), a full disk or exhausted inodes, memory exhaustion and OOM kills, credit exhaustion on a burstable instance type, or underlying hardware degradation. Application level: the process not listening, an expired certificate, a saturated connection pool, or a dependency being down. Then say what you would do first — `curl localhost` on the instance to split network from application, and check whether a deploy or config change lines up in time. See [troubleshooting SSH failures, high CPU, and disk space](../linux-administration/how-do-you-troubleshoot-ssh-failures-high-cpu-and-disk-space-on-linux-servers.md).
- The traffic-spike question should distinguish legitimate load from an attack, because the response differs. Confirm the shape first — requests per second, source distribution, and which endpoints — then check whether it is a genuine event (a campaign, a partner batch job, a retry storm from your own clients after an earlier failure) or malicious. For legitimate load: scale out, verify the autoscaler is not blocked by quota or unschedulable Pods, protect the data tier with caching and connection pooling, and shed non-essential work. For abuse: rate limiting, WAF rules, and blocking at the edge. Name a retry storm explicitly, because a self-inflicted spike caused by clients retrying without backoff is very common and scaling up makes it worse. See [designing a system to degrade gracefully under overload](../scalability-and-high-availability/how-do-you-design-a-system-to-degrade-gracefully-under-overload.md).
- The DR question should lead with the two numbers and then the sequence: state your RTO and RPO, declare the incident and communicate, verify the primary really is unrecoverable rather than transiently broken (because failing over unnecessarily costs you data), then execute the documented runbook — promote the standby database, bring the standby compute up or scale it out, redirect traffic via Route 53 health-checked failover records or a global accelerator, and verify with smoke tests. Afterwards, plan failback deliberately rather than reflexively, because failing back has its own data-reconciliation problem. Say that an untested DR plan does not count and that a restore rehearsal is the only proof. See [disaster recovery](../scalability-and-high-availability/what-is-disaster-recovery.md) and [designing for multi-region resilience](../cloud-engineering/how-do-you-design-for-multi-region-resilience.md).
- The 45-minute pipeline needs measurement before optimisation: read the per-stage timings to find where the time actually goes rather than guessing. Then the levers, roughly in order of payoff — parallelise independent stages, cache dependencies and Docker layers with a registry-backed cache so ephemeral runners benefit, reorder the Dockerfile so dependency installation caches above source copying, run only the tests affected by the change, move long integration and end-to-end suites off the blocking path, use larger or more agents, and split a monorepo build by change detection. Say which single change gave the biggest win in your experience, and that you would measure before and after. See [reducing Docker image size and build time](../docker/how-do-you-reduce-docker-image-size-and-build-time.md).
- On the Terraform EC2 writing task, the marks are for hygiene rather than the resource block: declare `variable "instance_type"` and `variable "region"` with types, descriptions, and sensible defaults; pass the region to the provider; look the AMI up with a `data "aws_ami"` block rather than hardcoding an ID that is region-specific; and add tags. Mentioning that an AMI ID is not portable across regions — which is exactly why the `region` variable makes a hardcoded AMI a bug — is the detail that shows you have done this for real.
- Blue-green should be answered with purpose, the switch mechanism, and the constraint: two complete environments, validate the idle one, then cut over atomically — the Service label selector in Kubernetes, or the ALB listener rule's target group on AWS — keeping the old version warm so rollback is a switch rather than a deployment. The constraint that usually rules it out is a shared database schema that must satisfy both versions simultaneously, which is why expand-and-contract migrations matter. See [deployment strategies](../devops-tools-and-automation/what-are-deployment-strategies.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)
- [[How do you integrate SonarQube and quality gates into a pipeline?]] (`#458`): [How do you integrate SonarQube and quality gates into a pipeline?](../cicd/how-do-you-integrate-sonarqube-and-quality-gates-into-a-pipeline.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
