---
title: "What are the most frequently asked DevOps interview questions?"
id: 274
category: "Interview Experience"
difficulty: "Beginner"
tags:
  - devops
  - interview-experience
  - interview-questions
---

# What are the most frequently asked DevOps interview questions?

**Short answer:** Nine areas account for most of what gets asked: Linux troubleshooting and text processing, Git branching and history, Docker images and layers, Kubernetes workloads and debugging, Terraform state, CI/CD pipeline design, cloud IAM and networking, monitoring and alerting, and secrets management. Within those, a small set of questions recurs almost verbatim across companies - and this page maps each to the answer in this guide.

## Detail

**How to use this page.** It is a revision checklist, not a script. Work down it and, for each line, check that you can answer in two to four sentences and defend the trade-off. If you cannot, follow the link.

**The recurring questions, by area:**

**Linux** - asked in nearly every interview, more often than any single tool.

- Print the last N lines of a file; read a huge log without opening it fully → [grep, awk, and sed](../linux-administration/how-do-you-analyse-logs-and-text-files-with-grep-awk-and-sed.md)
- Find the top 10 IPs or the most frequent errors in an access log → same
- Troubleshoot high CPU, a full disk, or a failed SSH login → [SSH, CPU, and disk troubleshooting](../linux-administration/how-do-you-troubleshoot-ssh-failures-high-cpu-and-disk-space-on-linux-servers.md)
- What is systemd, and how do you manage a service? → [systemd](../linux-administration/what-is-systemd.md) · [managing services](../linux-administration/how-do-you-manage-services-in-linux.md)
- Difference between `&` and `&&`; write a script that does X → [production-grade Bash](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md)

**Git**

- Merge vs rebase; what does cherry-pick do? → [merge, rebase, and cherry-pick](../version-control/what-is-the-difference-between-git-merge-rebase-and-cherry-pick.md)
- `git fetch` vs `git pull`; `--force` vs `--force-with-lease` → same
- Undo the last two commits; reset vs revert → [undoing changes safely](../version-control/how-do-you-undo-changes-in-git-safely.md)
- What is your branching strategy, and how do branches map to environments? → [branching strategy](../version-control/what-is-git-branching-strategy.md) · [trunk-based development](../version-control/what-is-trunk-based-development.md)
- Resolve a merge conflict → [merge conflicts](../version-control/how-to-handle-merge-conflicts-in-git.md)

**Docker**

- Image vs container → [image vs container](../docker/what-is-the-difference-between-docker-image-and-docker-container.md)
- Reduce image size; what is a multi-stage build? → [image size and build time](../docker/how-do-you-reduce-docker-image-size-and-build-time.md)
- Explain layer caching - if layer 5 changes, what happens to 6-10? → same
- Docker network types → [bridge, host, overlay, macvlan](../docker/what-are-docker-network-types-bridge-host-overlay-macvlan.md)
- Explain Docker architecture; what replaced dockershim? → [Docker architecture](../docker/explain-docker-architecture.md) · [CRI](../container-orchestration-advanced/what-is-container-runtime-interface-cri.md)

**Kubernetes** - the largest single block in most interviews.

- Explain the architecture and what each control-plane component does → [architecture](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md)
- Pod stuck `Pending` or `CrashLoopBackOff` - how do you debug it? → [debugging Pods](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md)
- Liveness vs readiness - what if liveness passes but readiness fails? → [probes](../kubernetes/how-do-liveness-readiness-and-startup-probes-differ.md)
- nodeSelector and affinity vs taints and tolerations → [controlling placement](../kubernetes/how-do-you-control-which-node-a-pod-runs-on.md)
- Service types; ClusterIP vs NodePort vs LoadBalancer; what is Ingress? → [exposing applications](../kubernetes/how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md) · [Services](../kubernetes/what-is-a-service-in-kubernetes.md)
- How does HPA work, and what if the cluster has no room? → [autoscaling](../kubernetes/how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md)
- How does RBAC work? → [RBAC](../kubernetes/how-does-rbac-work-in-kubernetes.md)
- Deployment vs StatefulSet vs DaemonSet → [StatefulSets](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md) · [DaemonSets](../container-orchestration-advanced/what-are-daemonsets-in-kubernetes.md)
- Why Helm instead of plain YAML? → [Helm](../container-orchestration-advanced/what-is-helm.md)

**Terraform** - state is the most-asked sub-topic in the whole IaC area.

- Explain the state file; where do you store it; how does locking work? → [managing state](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md)
- The state file was deleted and there is no backup - what now? → [recovering state](../infrastructure-as-code/how-do-you-recover-a-lost-or-corrupted-terraform-state-file.md)
- Two engineers apply at the same time - what happens? → [managing state](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md)
- What is drift, and how do you detect it? → same
- Import an existing resource → [importing infrastructure](../infrastructure-as-code/how-do-you-import-existing-cloud-infrastructure-into-terraform.md)
- Terraform vs Ansible → [the comparison](../infrastructure-as-code/what-is-the-difference-between-ansible-and-terraform.md)

**CI/CD**

- Walk me through your pipeline, stage by stage → [CI/CD pipelines](../cicd/what-is-ci-cd-pipeline.md)
- Continuous delivery vs continuous deployment → [the distinction](../cicd/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)
- Declarative vs scripted Jenkins pipelines; shared libraries → [Jenkins pipelines](../cicd/what-are-jenkins-pipelines.md) · [shared libraries](../cicd/how-do-you-use-jenkins-shared-libraries.md)
- How do you handle secrets in a pipeline, and what if one leaks? → [secrets in CI/CD](../devsecops/how-do-you-manage-secrets-in-ci-cd-pipelines.md) · [secret leaks](../cicd/how-do-you-prevent-and-handle-secret-leaks-in-ci-cd-pipelines.md)
- Why Argo CD rather than deploying from the pipeline? → [GitOps](../devops-tools-and-automation/what-is-gitops.md) · [Argo CD](../devops-tools-and-automation/what-is-argocd.md)
- Blue/green vs canary vs rolling → [deployment strategies](../devops-tools-and-automation/what-are-deployment-strategies.md)

**Cloud**

- Design a production VPC; public vs private subnets; NAT vs internet gateway → [production VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md)
- How does IAM evaluate a request? → [IAM evaluation](../aws-engineering/how-does-aws-iam-evaluate-a-request.md) · [least privilege](../cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md)
- How do Pods get cloud credentials without static keys? → [Pod Identity and IRSA](../aws-engineering/how-do-you-secure-pod-access-to-aws-resources-using-eks-pod-identity-or-irsa.md)
- ECS vs EKS vs Fargate → [the comparison](../aws-engineering/what-is-the-difference-between-ecs-eks-and-fargate.md)
- S3 storage classes and lifecycle rules → [storage classes](../aws-engineering/what-are-the-s3-storage-classes-and-when-do-you-use-each.md)
- How do you reduce cloud cost? → [cost optimisation](../cloud-cost-optimization/what-is-cloud-cost-optimization.md)

**Monitoring, networking, and security**

- Write a PromQL query; how do Alertmanager rules work? → [PromQL and Alertmanager](../monitoring-and-logging/how-do-you-write-effective-promql-queries-and-alertmanager-rules.md)
- Monitoring vs observability; what are the golden signals? → [monitoring vs logging](../monitoring-and-logging/explain-the-difference-between-monitoring-and-logging.md) · [observability](../advanced-devops-cloud/what-is-observability.md)
- SLI vs SLO vs SLA; what is an error budget? → [the four terms](../sla-management/what-is-the-difference-between-an-sla-an-slo-an-sli-and-an-ola.md) · [error budgets](../site-reliability-engineering/what-is-error-budget.md)
- L4 vs L7 load balancing; ALB vs NLB → [layer 4 vs layer 7](../scalability-and-high-availability/what-is-the-difference-between-a-layer-4-and-a-layer-7-load-balancer.md)
- What happens when a user opens the site? → [the request path](../network-security/what-happens-when-a-user-opens-your-application-in-a-browser.md)
- How does TLS work, and what happens when a certificate expires? → [SSL/TLS](../network-security/what-is-ssl-tls.md)
- How do you scan images and dependencies, and what do you gate on? → [SAST, DAST, IAST, SCA](../devsecops/what-is-the-difference-between-sast-dast-iast-and-sca.md) · [prioritising vulnerabilities](../devsecops/how-do-you-prioritise-vulnerabilities-without-blocking-delivery.md)

**Always asked, regardless of stack:** explain your project ([how to do it well](./how-do-you-explain-your-devops-project-in-an-interview.md)), a scenario you had to debug ([method](./how-do-you-answer-scenario-based-troubleshooting-questions.md)), and why you made a particular architectural choice.

## Example

```text
TWO-WEEK REVISION PLAN

  Week 1 — fundamentals you will definitely be asked
    Day 1   Linux: grep/awk/sed, disk & CPU triage, systemd
    Day 2   Git: merge vs rebase, reset vs revert, branching strategy
    Day 3   Docker: layers, cache, multi-stage, image size
    Day 4   Kubernetes I: architecture, workloads, probes, Services
    Day 5   Kubernetes II: debugging, scheduling, RBAC, autoscaling
    Day 6   Terraform: state, locking, drift, modules, import
    Day 7   Rehearse the 90-second project walkthrough, out loud

  Week 2 — depth, scenarios, and your specific stack
    Day 8   CI/CD: your pipeline end to end, secrets, GitOps
    Day 9   Cloud: VPC design, IAM evaluation, workload identity
    Day 10  Monitoring: PromQL, alerting, SLI/SLO/error budget
    Day 11  Networking + security: request path, TLS, L4 vs L7
    Day 12  Scenarios: practise the 5-step method out loud
    Day 13  Hands-on: write a Dockerfile, a pipeline, a TF module — by hand
    Day 14  Prepare "why did you choose X?" for every choice in your project

SELF-CHECK — can you answer each in 2-4 sentences, with a trade-off?

  [ ] What is the Terraform state file for, and what if it is deleted?
  [ ] Liveness passes, readiness fails — what happens?
  [ ] If layer 5 of a Dockerfile changes, what rebuilds?
  [ ] Merge or rebase, and why?
  [ ] 502 or 504 — what is the difference and where do you look?
  [ ] Why did you choose <every tool in your architecture>?
```

## Interview tips

- Prioritise Linux and Git. They are asked more consistently than any single platform tool, and candidates under-prepare them because they feel basic.
- For each item, prepare the _trade-off_ as well as the definition. Interviews at 5+ years are mostly "why that one?"
- Do not memorise answers. Interviewers detect recitation immediately and respond by going a level deeper, which is exactly where memorisation fails.
- Practise saying answers aloud. Knowing something and explaining it in four fluent sentences are different skills, and only one is being tested.
- Cover the whole checklist shallowly before going deep anywhere. A gap in a basic area costs more than extra depth in a strong one.
- Tailor the last 20% to the job description - the tools it names are the tools you will be asked about.

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
