---
title: "What DevOps interview questions does Rapidsoft ask?"
id: 374
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - rapidsoft
  - infrastructure-as-code
  - configuration-management
  - cicd
  - kubernetes
  - backup-and-disaster-recovery
  - database-management-in-devops
  - docker
---

# What DevOps interview questions does Rapidsoft ask?

## Questions

**Experience**

- **What have you worked on — describe your experience briefly.**
- **Have you worked on Docker Swarm before?**

**Terraform and Ansible**

- **Terraform throws errors while provisioning infrastructure. How do you investigate them — and how do you validate a Terraform file in the first place?**
- **In Ansible, how do you execute something as the root user?**

**CI/CD**

- **Your Jenkins CI/CD pipeline has failed. How do you investigate?**
- **How do you store sensitive information such as passwords in Jenkins?**
- **You have a multi-cloud environment. How do you manage pipelines across all those clouds?**

**Resilience and data**

- **How would you structure disaster recovery for your application?**
- **How would you perform a database migration for your database application?**

**Kubernetes**

- **You have a `CrashLoopBackOff` error. How do you fix it?**
- **What is the difference between a Deployment and a StatefulSet?**
- **Explain the fields in a `deployment.yml`.**

## Example

```text
Rapidsoft — DevOps Engineer (10.5 YOE total, 4-5 in DevOps), reported round
12 questions

  CI/CD                       3   Jenkins pipeline failure triage, storing
                                  passwords, multi-cloud pipeline management
  Kubernetes                  3   CrashLoopBackOff, Deployment vs StatefulSet,
                                  deployment.yml field by field
  Terraform and Ansible       2   investigating provisioning errors +
                                  validation, running as root in Ansible
  Resilience and data         2   DR structure, database migration
  Experience                  2   background, Docker Swarm

A DIAGNOSTIC-LEANING ROUND
  Three of twelve questions are "it broke, how do you investigate" — Terraform
  errors, a failed Jenkins pipeline, and CrashLoopBackOff. Prepare an ordered
  method for each rather than a list of causes.
```

## Interview tips

- The Terraform validation question has a specific tool chain and giving it in order is the answer: `terraform fmt -check` for style, `terraform validate` for syntax and internal consistency — noting it does _not_ contact the provider so it cannot catch a bad resource argument value — then `terraform plan` for the real check, since that is where provider-side validation and credentials are exercised. Add `tflint` for provider-specific linting and `checkov` or `tfsec` for security policy. Then, for investigating errors: read the error from the bottom up because the provider's message is usually the last line, re-run with `TF_LOG=DEBUG` to see the API calls, distinguish the three failure classes — HCL syntax, a plan-time type or reference error, and an apply-time API rejection such as a quota, permission, or naming conflict — and check whether state has partially applied, because a failed apply can leave resources created but untracked. Naming those three classes is what makes this a senior answer. See [scanning infrastructure as code before it is applied](../devsecops/how-do-you-scan-infrastructure-as-code-before-it-is-applied.md).
- The Ansible root question is short and exact: `become: true` — with `become_user` if you need a user other than root and `become_method` for something other than `sudo`. It can be set at play, block, or task level, and you supply the password with `--ask-become-pass` or a vaulted variable if `sudo` requires one. Say that `become` at task level is preferred over running an entire play as root, and that the old `sudo:` keyword is deprecated. See [what Ansible is](../infrastructure-as-code/what-is-ansible.md).
- For the failed-Jenkins-pipeline question, give a method rather than causes: read the console log and find the _first_ error rather than the last, because later failures are usually consequences; identify which stage failed and whether it is code, infrastructure, or credentials; check whether the agent is the problem — a label matching nothing, a full disk, or an offline node; check whether it is flaky by re-running the stage; and compare against the last successful build to see what changed, including whether a dependency version moved even though your code did not. Say you would use `Replay` to test a `Jenkinsfile` change without committing. See [Jenkins pipelines](../cicd/what-are-jenkins-pipelines.md).
- Jenkins secrets should be answered as a hierarchy with a named failure mode. Baseline: the Credentials plugin, folder-scoped so teams only see their own, consumed via `withCredentials` so values are masked in the log. Better: Jenkins fetches at run time from an external store — Vault, Secrets Manager, or Key Vault — so nothing sensitive lives on the controller. Best: no stored credential at all, using OIDC federation to the cloud provider for short-lived tokens. Then the failure mode: interpolating a secret inside a double-quoted Groovy string puts it in the build log, so use single quotes and let the shell expand it. Add that `JENKINS_HOME/secrets/` must be included in any backup or restored credentials become undecryptable. See [managing secrets in CI/CD pipelines](../devsecops/how-do-you-manage-secrets-in-ci-cd-pipelines.md) and [preventing and handling secret leaks in CI/CD](../cicd/how-do-you-prevent-and-handle-secret-leaks-in-ci-cd-pipelines.md).
- The multi-cloud pipeline question wants one process rather than three toolchains. Say: a single CI/CD platform with cloud-specific deployment stages; one IaC tool with per-provider modules; identity federated from one source into each cloud via OIDC so there are no stored keys anywhere; a shared library or reusable workflow holding the common build-test-scan-publish flow so only the deploy step differs; and consistent tagging, logging, and cost reporting across both. Then give the honest trade-off: a genuinely cloud-agnostic abstraction costs you the best managed services on each side, so most teams standardise the _process_ and accept provider-specific implementations. See [the real trade-offs of multi-cloud](../cloud-engineering/what-are-the-real-trade-offs-of-multi-cloud.md).
- On disaster recovery, lead with the two numbers and then pick a tier: RPO is tolerable data loss, RTO is tolerable time to recover, and the patterns are backup-and-restore (cheapest, hours), pilot light (data replicated, minimal compute), warm standby (scaled-down but live), and active-active (near-zero RTO, highest cost). Then say what actually makes it real: replication is not backup because a deletion replicates too, so you need an immutable copy; traffic redirection needs DNS health checks or a global load balancer; and an untested DR plan does not count — a restore rehearsal is the proof. See [disaster recovery](../scalability-and-high-availability/what-is-disaster-recovery.md) and [designing for multi-region resilience](../cloud-engineering/how-do-you-design-for-multi-region-resilience.md).
- The database migration question should be answered as expand-and-contract, because that is what makes it zero-downtime: add the new column or table, deploy code that writes to both and reads from the old, backfill historically, switch reads to the new, then remove the old in a later release. The principle to state is that every migration must be backward compatible with the currently running version, because during a rolling deploy both versions are live simultaneously. For a platform migration rather than a schema change, name the tooling — a change-data-capture service such as DMS replicating continuously until cutover — and say you would keep the old database readable for rollback. See [continuous delivery versus continuous deployment](../cicd/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md).
- `CrashLoopBackOff` should be answered as a mechanism plus a decision tree. Mechanism: the container starts, exits, and the kubelet restarts it with exponential backoff up to five minutes. Diagnosis: `kubectl describe pod` for events and restart count, `kubectl logs --previous` for the dead container's output, then the exit code — 137 means `OOMKilled`, 1 usually an application error, and 0 means the process finished, which is a `restartPolicy` mismatch. Then the causes people miss: a missing ConfigMap or Secret, a failing liveness probe killing a healthy-but-slow container, and a dependency that is not yet reachable. See [troubleshooting a Pod stuck in Pending or CrashLoopBackOff](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md) and [how probes differ](../kubernetes/how-do-liveness-readiness-and-startup-probes-differ.md).
- The `deployment.yml` walkthrough should be a structured tour rather than a list: `apiVersion` and `kind`; `metadata` with name, namespace, and labels; then `spec` — `replicas`, the `selector.matchLabels` that must match the Pod template, `strategy` with `rollingUpdate` `maxSurge` and `maxUnavailable`, and `revisionHistoryLimit`; then the Pod template with containers, image, ports, `env`/`envFrom`, `resources` requests and limits, probes, and `volumeMounts`; and Pod-level fields such as `volumes`, `serviceAccountName`, `securityContext`, `nodeSelector`, `tolerations`, and `terminationGracePeriodSeconds`. Call out that the selector must match the template labels or the API rejects it.
- Deployment versus StatefulSet is best framed on identity: a Deployment's Pods are interchangeable with random names and no stable storage; a StatefulSet gives each Pod a stable ordinal name, a stable DNS record via a headless Service, and its own PersistentVolumeClaim that follows it across restarts, with ordered creation, scaling, and updates. Say that is why databases and quorum systems use StatefulSets. See [StatefulSets](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md).
- The Docker Swarm question is a currency check. Answer honestly, and if you have used it, note where it is genuinely reasonable — a small fixed deployment where Kubernetes would be overkill — while acknowledging that Kubernetes has effectively won on ecosystem and hiring. Being able to say "Swarm is simpler and adequate here, Kubernetes is the default" shows judgement rather than fashion. See [what container orchestration is and why you need it](../container-orchestration-advanced/what-is-container-orchestration-and-why-do-you-need-it.md).
- With ten and a half years of total experience but four to five in DevOps, expect the opening question to probe how you transitioned. Frame the earlier experience as an asset — application, infrastructure, or support background that makes you better at the platform work — rather than as time to explain away.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
