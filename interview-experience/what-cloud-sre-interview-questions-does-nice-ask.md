---
title: "What cloud SRE interview questions does Nice ask?"
id: 355
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - nice
  - azure-engineering
  - cicd
  - infrastructure-as-code
  - kubernetes
  - container-orchestration-advanced
  - devops-tools-and-automation
  - devsecops
---

# What cloud SRE interview questions does Nice ask?

## Questions

### Round set 1 — Cloud Site Reliability Engineer (3 YOE)

- **Explain your project.**
- **What is Terraform, and how did you configure it in your project?**
- **What are modules in Terraform?**
- **What is the difference between `CMD` and `ENTRYPOINT` in Docker?**
- **What is the difference between `ADD` and `COPY`?**
- **What is a Deployment, and what is a StatefulSet?**
- **What is the monitoring setup for your project?**
- **Have you created dashboards in Grafana?**
- **How do you handle Helm charts?**
- **Explain CI/CD.**
- **How are you maintaining Argo CD across three environments — E1, E2, and E3?**

### Round set 2 — Cloud Site Reliability Engineer (3 YOE)

- **Talk me through your profile.**
- **Is this client-based work, or are you in the middle of a deployment engagement?**
- **You claim you improved CI/CD efficiency by 60%. What specific optimisations produced that?**
- **What is your approach to integrating automated testing into pipelines to keep code quality high?**
- **How do you integrate a tool such as SonarQube into your pipelines?**
- **How do you design and manage a containerised environment for scalability and high availability?**
- **In Kubernetes, how do you manage deployment, scaling, and rollback? Walk me through a specific scenario.**
- **What is the advantage of a YAML pipeline over a classic build pipeline in Azure DevOps, and what other advantages have you personally experienced?**
- **Are you familiar with Terraform? Describe a real scenario where you used it to provision highly scalable infrastructure.**
- **What branching strategy do you follow for a large team working on a complex application?**
- **Do you have experience with Azure Key Vault, have you integrated it into pipelines, and did you create the access policies yourself or did someone else?**
- **What is a recent challenge you faced implementing a DevOps practice or pipeline?**
- **Other than Azure and AWS, are you familiar with any other cloud platforms?**

## Example

```text
Nice — Cloud Site Reliability Engineer (3 YOE), two reported rounds
24 questions

  SET 1  Tooling fundamentals      11   Terraform + modules, CMD vs ENTRYPOINT,
                                        ADD vs COPY, Deployment vs StatefulSet,
                                        monitoring, Grafana, Helm, CI/CD,
                                        Argo CD across E1/E2/E3
  SET 2  Claims + practice         13   "60% CI/CD improvement" audited,
                                        automated testing, SonarQube, container
                                        HA design, deploy/scale/rollback,
                                        YAML vs classic pipelines, Key Vault
                                        (asked 3 ways), recent challenge

WHAT ROUND 2 IS ACTUALLY DOING
  It audits the CV. "You said 60% — which optimisations?" and "did YOU create
  the Key Vault access policies, or did someone else?" are both checking
  whether you did the work or were nearby when it happened. Every number on
  your CV needs a mechanism behind it.
```

## Interview tips

- The "60% improvement" question is the one that decides round 2, and a vague answer is fatal. Come with the arithmetic: what the pipeline took before, what it takes now, and which changes produced the difference — parallelising independent stages, caching dependencies and Docker layers, reordering the Dockerfile so dependency installation caches above source copying, running only affected tests, moving integration tests off the blocking path, and using more or larger agents. Then say which single change gave the biggest win. If you cannot defend the number, do not put it on the CV.
- The Key Vault question is asked three times, ending with "did you create the access policies yourself?" — that is a deliberate ownership probe, and the honest answer is better than the impressive one. If you consumed a vault someone else configured, say so and then demonstrate that you understand what was configured: an access policy or, on current Azure, Azure RBAC role assignments granting get and list on secrets, a service connection or managed identity as the principal, and the variable group linked to the vault so secrets resolve at run time rather than being stored in the pipeline. Add that RBAC has replaced access policies as the recommended model — that detail shows current knowledge regardless of who clicked the buttons.
- The Argo CD across three environments question wants a repository and promotion model, not a definition. Give the structure: one Application per environment, either as separate Applications or generated by an ApplicationSet, pointing at environment-specific overlays or Helm value files in a config repository; promotion is a pull request changing the image tag in the next environment's values; sync policy is automated with self-heal in E1 and E2 but manual or approval-gated in production; and each environment has its own project with scoped destinations so E1 cannot deploy into E3. Say that the same manifests are reused with only values differing — configuration divergence between environments is the failure mode this design exists to prevent. See [Argo CD](../devops-tools-and-automation/what-is-argocd.md) and [GitOps](../devops-tools-and-automation/what-is-gitops.md).
- YAML versus classic pipelines in Azure DevOps has a clear list, and the interviewer explicitly asks for personal experience on top, so give both. The structural advantages: pipeline definition lives in the repository so it is versioned, reviewed, and branched with the code; it can be templated and reused across projects; it is diffable so you can see who changed what and when; and it can be recreated from scratch if the project is lost. Then the personally-experienced part — something like a pipeline change being caught in code review, or a feature branch safely testing a pipeline change without affecting `main`. That second half is what they are actually listening for.
- `ADD` versus `COPY` has a preferred answer: use `COPY`, because `ADD` additionally auto-extracts local tar archives and can fetch remote URLs, which makes builds surprising and can pull in content you did not audit. Say you default to `COPY` and reach for `ADD` only for the tar-extraction case. Pair it with `CMD` versus `ENTRYPOINT`: `ENTRYPOINT` is the executable, `CMD` supplies default arguments, and arguments passed to `docker run` replace `CMD` but not `ENTRYPOINT` unless you use `--entrypoint`. See [what a Dockerfile is](../docker/what-is-dockerfile.md).
- Deployment versus StatefulSet should be answered on identity rather than on statefulness alone: a Deployment's Pods are interchangeable with random names and no stable storage; a StatefulSet gives each Pod a stable ordinal name, a stable DNS record, and its own PersistentVolumeClaim that follows it across restarts, and it updates and scales in order. Say that this is why databases and quorum systems use StatefulSets. See [StatefulSets](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md).
- The deployment-scaling-rollback question explicitly asks for a _specific scenario_, so bring one narrative rather than three definitions: a Deployment with a rolling update strategy and `maxUnavailable: 0`, readiness probes gating traffic so a bad replica never receives requests, an HPA scaling on CPU or a custom metric with the Cluster Autoscaler adding nodes underneath, and `kubectl rollout undo` — or `helm rollback` — when a release regresses. Say what you watched to decide it had gone wrong. See [autoscaling workloads and nodes](../kubernetes/how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md) and [how probes differ](../kubernetes/how-do-liveness-readiness-and-startup-probes-differ.md).
- For containerised scalability and high availability, give the checklist as design properties: stateless application tier with state externalised, at least three replicas spread across availability zones with topology spread constraints, PodDisruptionBudgets so upgrades cannot drain a service to zero, requests and limits set from observed usage, HPA plus cluster autoscaling, health probes, and a multi-zone control plane. See [high availability](../scalability-and-high-availability/what-is-high-availability.md).
- SonarQube integration should be described as a _gate_, not a step: it runs after unit tests so it can consume coverage, publishes to the server, and the pipeline waits on the quality gate result and fails if it breaches. Add the adoption detail — gate on _new_ code rather than the whole legacy baseline, otherwise no existing project can ever pass. See [what shift-left security means](../devsecops/what-does-shift-left-security-mean.md) and [SAST, DAST, IAST, and SCA](../devsecops/what-is-the-difference-between-sast-dast-iast-and-sca.md).
- For automated testing in pipelines, describe the pyramid and where each layer runs: unit tests on every commit as a blocking gate, integration and contract tests after the artefact is built, and end-to-end or smoke tests against a deployed environment — with only the fast, reliable layers blocking the merge, because a flaky end-to-end suite in the critical path trains people to re-run until green. Naming flakiness as the thing you manage is a strong signal.
- Terraform modules should be answered with purpose plus interface: a module is a reusable, versioned package of resources with input variables and outputs, used so environments differ only in values rather than in duplicated code. Say you pin module versions and that a good module has a narrow interface — if it takes thirty variables, it is not really a module. See [what Terraform is](../infrastructure-as-code/what-is-terraform.md).
- The "recent challenge" question is a chance to look senior, so pick something with a real trade-off and a resolution — resistance to a quality gate, a migration that had to happen with no downtime, a cost overrun — and describe what you changed and what you learned rather than blaming a tool or a colleague.
- On the third-cloud question, be straightforwardly honest. Claiming GCP experience you do not have invites an immediate follow-up you cannot answer; saying "Azure and AWS in production, GCP only through personal projects" costs nothing and builds credibility for everything else you claimed. See [how the core services of AWS, Azure, and GCP map to each other](../cloud-engineering/how-do-the-core-services-of-aws-azure-and-gcp-map-to-each-other.md).

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
