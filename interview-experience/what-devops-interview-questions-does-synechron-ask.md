---
title: "What DevOps interview questions does Synechron ask?"
id: 383
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - synechron
  - azure-engineering
  - cicd
  - kubernetes
  - docker
  - version-control
  - monitoring-and-logging
  - site-reliability-engineering
  - backup-and-disaster-recovery
---

# What DevOps interview questions does Synechron ask?

## Questions

### Round set 1 — Azure DevOps, with screen sharing (13 YOE, 5 in DevOps)

- **What is Azure Boards, and what does it contain?**
- **What is `pom.xml` in Maven?**
- **Share your screen and write the structure of an Azure pipeline.**
- **Share your screen and write a simple Dockerfile.**
- **How do you troubleshoot a failed Pod in AKS — give the commands.**
- **What is the `terraform drift` command?**
- **What are the different types of Azure storage?**
- **How do you store credentials in Azure pipelines?**
- **What are the different types of Azure subscription?**
- **How would you implement DC/DR in Azure, and which services would you use?**
- **What issues have you faced in your project? Explain them.**
- **Do you register the App Service first, or deploy it first?**
- **Have you used a scripting language for automation?**
- **What is Azure Artifacts?**
- **What is the difference between a self-hosted agent and a Microsoft-hosted agent?**
- **What is the difference between `CMD` and `ENTRYPOINT` in Docker, and how do you configure SonarQube with Azure?**

### Round set 2 — mixed fundamentals and SRE (3 YOE)

- **What is the difference between Docker and Docker Compose, and how do Docker Compose and Kubernetes relate?**
- **What is the difference between the `ADD` and `COPY` commands?**
- **Explain the Terraform architecture, and what is a backend?**
- **What is the difference between `find` and `sed`?**
- **How do you find the 10th word in a file?**
- **How do you monitor system performance?**
- **What is CI/CD, and what challenges have you faced with it in your team — how did you overcome them?**
- **What is Blue Ocean in Jenkins?**
- **How do you configure a Flask application in Jenkins — the procedure?**
- **What is the difference between CloudWatch and CloudFormation?**
- **How do you create custom alerts — the procedure?**
- **What are ACM and S3?**
- **What is Ansible Galaxy?**
- **Explain the Kubernetes architecture.**
- **What are SLI and SLO?**
- **What is monkey patching?**
- **Have you worked on SRE, and what is the difference between DevOps and SRE?**

### Round set 3 — scenario and counter-question round (4 YOE, client: Morgan Stanley)

The candidate noted that every question was scenario-based with counter-questions, concentrated on CI/CD and Kubernetes.

- **Explain what CI/CD is and describe how you implemented CI/CD pipelines in one of your projects.**
- **How does AWS CodePipeline differ from a Jenkins pipeline, and when would you choose one over the other?**
- **How do you configure your CI/CD pipelines? Walk me through the steps you followed to set one up in a recent project.**
- **If you need to deploy an application to both cloud environments and on-premises servers, how would you design and configure the pipeline to handle that hybrid case?**
- **Where and how do you manage environment variables for your applications in a CI/CD setup, and how do you write and use them securely?**
- **After an application is deployed, what post-deployment steps do you perform to make sure everything is running smoothly?**
- **How would you deploy a Kubernetes application using Jenkins, and which plugins or tools would you use?**
- **What is the difference between `git pull` and `git clone`?**
- **What is the difference between `git pull` and `git fetch`, and when would you use each? And what is `git merge`?**
- **You have two commits. How would you check the differences between them?**
- **What are Prometheus and Grafana?**
- **How do you monitor the health and performance of your Kubernetes Pods in production?**
- **What is Helm, and why do you prefer it for managing Kubernetes applications over deploying manifests directly?**
- **Describe the main components of a Kubernetes cluster and the role each plays.**
- **If you want to use a feature branch instead of the main branch, how will you design the CI/CD?**
- **When an issue occurs in the pipeline, who handles it and how do they troubleshoot?**

## Example

```text
Synechron — DevOps Engineer, three reported interviews (~54 questions)

  SET 1  Azure DevOps (13 YOE)         16   Azure Boards, screen-share a
                                            pipeline and a Dockerfile, AKS Pod
                                            triage commands, subscription
                                            types, DC/DR, self-hosted vs
                                            Microsoft-hosted agents
  SET 2  Mixed fundamentals (3 YOE)    17   Docker vs Compose, find vs sed,
                                            10th word in a file, Blue Ocean,
                                            CloudWatch vs CloudFormation,
                                            monkey patching, DevOps vs SRE
  SET 3  Scenario round (4 YOE)        16   CodePipeline vs Jenkins, hybrid
                                            cloud + on-prem pipeline, secure
                                            env vars, post-deployment steps,
                                            feature-branch CI/CD

THREE DIFFERENT INTERVIEWS, THREE DIFFERENT BARS
  Set 1 makes a 13-year candidate write code on a shared screen. Set 2 is a
  broad definitions sweep with two odd ones out (monkey patching, Blue Ocean).
  Set 3 is pure scenarios with counter-questions. Prepare for the format, not
  just the topics.
```

## Interview tips

- The `terraform drift` question is a trap because **there is no such command**. Say so directly and give what actually exists: `terraform plan` shows drift as part of computing the diff, and `terraform plan -refresh-only` (with `apply -refresh-only`) is the purpose-built way to detect and reconcile drift without proposing configuration changes. Note that the old `terraform refresh` is deprecated in favour of that, and that Terraform Cloud has a managed drift-detection feature which may be what the interviewer had in mind. Correcting a non-existent command politely is a strong signal. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- The hybrid cloud-plus-on-premises pipeline in set 3 is the best design question here. Structure it: build **once** in the cloud producing one immutable artefact, then have two deployment paths from that same artefact. For the cloud, a normal deployment job. For on-premises, a **self-hosted runner or agent inside the on-premises network** that pulls work from the CI system — so no inbound firewall rule is needed, which is the crux of the answer — or a pull-based agent such as an Ansible pull or a GitOps controller running on-premises. Handle the differences in configuration rather than in the artefact, use an artefact repository reachable from both sides (or a replicated registry), and keep secrets in a store each side can read with its own identity. Say why you would not open inbound access from the internet to the data centre — that is what the question is really testing.
- The `git pull` versus `git clone` versus `git fetch` chain should be answered as one coherent explanation rather than three definitions: `clone` creates a new local copy of a repository that does not exist locally yet; `fetch` downloads new objects and updates remote-tracking refs on an existing clone, changing nothing in your working tree; `pull` is `fetch` followed by `merge` (or `rebase`); and `merge` is what integrates two histories, creating a merge commit unless the merge is fast-forward. Say that you use `fetch` when you want to inspect before integrating, and `pull --rebase` to avoid the merge commits that make history unreadable. For comparing two commits, `git diff <sha1> <sha2>`, with `--stat` for a summary and `git log <sha1>..<sha2>` to see the commits in between. See [git merge, rebase, and cherry-pick](../version-control/what-is-the-difference-between-git-merge-rebase-and-cherry-pick.md).
- The self-hosted versus Microsoft-hosted agent question has a clear answer with a security warning attached. Microsoft-hosted agents are clean ephemeral VMs, maintained for you, with no persistent state, limited parallel jobs, and no access to your private network. Self-hosted agents give you private-network access, custom tooling and hardware, caching between builds, and no per-minute limits — at the cost of patching and securing them yourself. Add the warning: a self-hosted agent retains state between jobs, so a compromised pipeline can persist on it, which is why they should be isolated per environment and never used for untrusted pull requests. That caveat is what distinguishes the answer.
- "Register the App Service first or deploy it first?" is an infrastructure-versus-application ordering question. The App Service (and its plan) must exist before you can deploy code onto it — so infrastructure first, provisioned by Terraform or Bicep in a separate pipeline or a separate stage, then the application deployment. Say the principle: separate the infrastructure lifecycle from the release lifecycle, because they change at different rates and have different blast radius, and the deployment pipeline should be able to run many times against infrastructure that changes rarely.
- `find` versus `sed` is a category question rather than a comparison: `find` locates files by name, type, size, time, or permission and can act on them with `-exec` or `-delete`; `sed` is a stream editor that transforms text line by line within files. They compose — `find . -name '*.conf' -exec sed -i 's/old/new/g' {} +` is the idiom worth giving, because it shows you know they solve different halves of one job. For the 10th word: `awk '{print $10}' file` gives the 10th field of every line, whereas `tr -s ' ' '\n' < file | sed -n '10p'` gives the 10th word of the whole file — ask which they mean, or answer both. That clarification is the better response. See [analysing logs with grep, awk, and sed](../linux-administration/how-do-you-analyse-logs-and-text-files-with-grep-awk-and-sed.md).
- CloudWatch versus CloudFormation is asked because the names look similar and they are entirely unrelated: CloudWatch is the monitoring service — metrics, logs, alarms, dashboards; CloudFormation is AWS-native infrastructure as code that provisions resources from templates in managed stacks. Say them as one sentence each and move on; the question is a check, not a discussion. Pair it with ACM (managed TLS certificates with automatic renewal when DNS-validated) and S3 (object storage) in the same crisp style.
- Monkey patching is the odd one out in set 2 and worth knowing: it is replacing or extending a module, class, or function at **runtime** rather than editing the source — most commonly in Python, and most legitimately in tests, where you patch a network call or a clock with `unittest.mock.patch` so the test is deterministic. Say the risk: it makes behaviour depend on import order and is invisible to anyone reading the original source, so outside tests and urgent third-party workarounds it is a maintenance hazard. Framing it as "a testing tool, occasionally a hotfix, never an architecture" is the right answer.
- DevOps versus SRE should not be answered as "SRE is Google's DevOps". Give the concrete distinction: DevOps is a set of practices and a culture aimed at reducing the gap between development and operations; SRE is a specific engineering discipline that implements reliability with measurable objectives — SLIs, SLOs, and an error budget that governs whether you ship features or fix reliability — plus explicit limits on toil and a blameless postmortem practice. Say that the error budget is the mechanism that makes SRE different: it converts an argument about risk into arithmetic. See [the difference between SRE, DevOps, and platform engineering](../site-reliability-engineering/what-is-the-difference-between-sre-devops-and-platform-engineering.md) and [error budgets](../site-reliability-engineering/what-is-error-budget.md).
- The post-deployment-steps question in set 3 is a chance to sound operationally mature: verify the rollout completed (`kubectl rollout status`), confirm readiness probes pass and endpoints are populated, run smoke tests against the real public endpoint rather than inside the cluster, compare error rate and latency against the pre-deploy baseline, check logs for new error signatures, verify any migration applied, watch for the first few minutes rather than declaring success immediately, and keep the previous version available for rollback for a defined soak window. Add updating the change record and notifying stakeholders — in a bank-adjacent engagement that is part of the job.
- CodePipeline versus Jenkins should end in a decision rule rather than a preference: CodePipeline is managed, integrates natively with AWS services and IAM, has no server to patch, and is cheap for AWS-only workflows — but it is less flexible and awkward for non-AWS targets. Jenkins is self-hosted with a vast plugin ecosystem, full control over agents, and portability across clouds and on-premises, at the cost of maintaining the controller, plugins, and security. Say you would pick CodePipeline for an AWS-only estate with a small platform team, and Jenkins (or GitHub Actions) when you need hybrid or on-premises reach — which links directly to the hybrid question in the same round. See [building a CI/CD pipeline with CodePipeline, CodeBuild, and CodeDeploy](../aws-engineering/how-do-you-build-a-ci-cd-pipeline-using-aws-codepipeline-codebuild-and-codedeploy.md).
- The secure environment-variables question wants a hierarchy: non-secret configuration in the pipeline definition or a ConfigMap so it is versioned and reviewable; secrets never in the repository, never in plain variables, but in a secret store — Key Vault, Secrets Manager, or Vault — referenced at run time, with variable groups linked to Key Vault on Azure; and best of all, no stored credential at all where OIDC federation is possible. Add the leak mechanics: mark variables as secret so they are masked, avoid echoing them, and remember that a secret injected as an environment variable is visible to any process in the container. See [managing secrets in CI/CD pipelines](../devsecops/how-do-you-manage-secrets-in-ci-cd-pipelines.md).
- The feature-branch CI/CD question wants branch-to-environment mapping made explicit: every feature branch and pull request gets a full build plus tests and scans — with a multibranch pipeline or `on: pull_request` creating jobs automatically — but only merges to the integration branch deploy to a shared environment, and only the release branch or a tag deploys to production. Say that ephemeral preview environments per feature branch are the mature version of this, and that branch protection with required checks is what enforces it. See [Git branching strategy](../version-control/what-is-git-branching-strategy.md).
- The AKS Pod troubleshooting question explicitly asks for commands, so give them in diagnostic order: `kubectl get pods -o wide`, `kubectl describe pod` for events and the last state's exit code, `kubectl logs --previous -c <container>`, `kubectl get events --sort-by=.lastTimestamp`, `kubectl exec -it` or `kubectl debug` for images without a shell, and `kubectl top pod` for usage. Add `az aks` commands for node-level issues and mention that exit code 137 means `OOMKilled`. See [troubleshooting a Pod stuck in Pending or CrashLoopBackOff](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md).
- Azure specifics worth knowing exactly: Azure Boards is the work-tracking component — work items, backlogs, sprints, boards, and queries, linked to commits and pull requests for traceability. Azure Artifacts is the package feed for NuGet, npm, Maven, Python, and universal packages, with upstream sources so it can proxy public registries. Azure storage types are blob, file, queue, table, and managed disks, with access tiers from hot through archive. Subscription types are the billing and isolation boundary — Enterprise Agreement, pay-as-you-go, CSP, and free or trial — and the useful answer is that subscriptions are how you isolate environments and cap spend, organised under management groups.
- Blue Ocean is a legacy Jenkins UI plugin providing a visual pipeline view — it is no longer actively developed, so the currency-aware answer is to say what it was for and that the modern equivalent is the built-in pipeline graph or an external dashboard. Being able to say "that plugin is effectively retired" is better than describing it as current. See [Jenkins pipelines](../cicd/what-are-jenkins-pipelines.md).
- Docker versus Docker Compose versus Kubernetes is a scope ladder: Docker runs one container, Compose declaratively runs a multi-container application on **one host** for local development, and Kubernetes orchestrates containers across a **cluster** with scheduling, self-healing, scaling, and rolling updates. Say that Compose is a development tool that does not replace an orchestrator, and that the natural progression is Compose locally and Kubernetes in production from the same images. See [what Docker Compose is](../docker/what-is-docker-compose.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
- [[How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?]] (`#402`): [How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?](../cicd/how-do-you-troubleshoot-a-jenkins-pipeline-that-never-starts-or-hangs-in-the-queue.md)
- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
