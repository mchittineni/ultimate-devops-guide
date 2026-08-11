---
title: "What DevOps scenario and pipeline questions come up when the company is not named?"
id: 367
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - unattributed
  - kubernetes
  - cicd
  - linux-administration
  - azure-engineering
  - aws-engineering
  - infrastructure-as-code
  - monitoring-and-logging
  - incident-management
---

# What DevOps scenario and pipeline questions come up when the company is not named?

## Questions

Eight further reported DevOps Engineer rounds whose submitters did not name the employer. These skew heavily toward broken-system scenarios, multi-round interview processes, and pipeline platform detail — GitHub Actions and Azure DevOps in particular.

### Round 9 — pure scenarios

- **The `/var` partition is 90% full. What is your immediate action?**
- **You are locked out over SSH with no root access. How do you recover?**
- **Add 50 GB to `/opt` using LVM with no downtime. What are the steps?**
- **Jenkins is failing to push a Docker image to the registry. How do you troubleshoot?**
- **An Ansible playbook times out on one host out of twenty. What do you check?**
- **An EC2 instance is unreachable and it is not a security group problem. What is your next step?**
- **An S3 bucket was made public by mistake. How do you secure and audit it?**
- **How would you approach an RDS migration with minimal downtime?**
- **A CI/CD pipeline needs rollback capability. How would you implement it?**
- **Write a shell script that checks whether a service is running, restarts it if not, and logs the event.**
- **Write Terraform to provision an EC2 instance with a custom security group and a `user_data` script.**
- **Design a highly available backend on AWS — which services and what architecture?**

### Round 10 — fundamentals with project follow-ups

- **What is a Dockerfile and what goes in it?**
- **Why Kubernetes instead of Docker Swarm?**
- **Explain the Kubernetes architecture.**
- **What is blue-green deployment? Explain a project where you used it, and how canary differs from it.**
- **What happens if etcd stops working?**
- **What are the Service types, and what is the difference between a Service and a Deployment?**
- **Explain a project where you used Docker, Kubernetes, and CI/CD, and describe your CI/CD in detail.**
- **If the Docker image exposes port 8080 but the application listens on a different port, what happens?**
- **Why is a load balancer used?**
- **What are your Git branching strategies?**
- **What is Terraform state file locking?**
- **Which Linux commands do you use, and can you write an Ansible file?**
- **Explain your CI/CD pipeline in detail and the stages of your `Jenkinsfile`.**
- **Questions on VPC.**

### Round 11 — identity, DR, and Azure monitoring

- **How do you host a static S3 website without enabling public access?**
- **What is the difference between Secrets Manager and Parameter Store?**
- **Why would you use a self-hosted runner instead of the default runner?**
- **What CI/CD does your project use for Terraform infrastructure?**
- **What is the difference between IAM users, a GitHub OIDC role, and a Terraform Cloud role? Which is more secure, and when do you use each?**
- **Write a simple Dockerfile, and write Terraform to provision an EC2 instance.**
- **You have a Lambda function and its role set up correctly, but no logs are appearing in the CloudWatch log group. How do you troubleshoot?**
- **When do you use EC2 and when Lambda? Give scenario-based answers.**
- **How does DRS work — explain the architecture — and how do failover and failback happen?**
- **How do you create a user without SSH access?**
- **What is the difference between `terraform validate` and `terraform fmt`?**
- **What are provisioners and how do you use them?**
- **What is the difference between an Azure managed identity and a service principal, and how do you explain that in an interview?**
- **How is an alert created for high CPU and memory on a VM, on which metrics, what is an action group, and how do you create the alert step by step? Also some basic KQL troubleshooting queries in a Log Analytics workspace, and any scripted automation for monitoring.**

### Round 12 — a four-round process (2 in person, 2 virtual)

**Round 1 — technical discussion (client, virtual)**

- **Tell me about yourself, and what were your roles and responsibilities on your project?**
- **How have you used Python in your projects, and what tasks did you do with it?**
- **Write a Python program to reverse a string.**
- **Do you know slicing in Python? Slice a string from 0 to 4.**
- **What is the difference between a list and a tuple in Python?**
- **Have you created your own Python module? Create one that prints "Hello, World".**
- **Explain inheritance in Python.**
- **Have you customised an operating system for a project requirement? How, and what did you customise?**
- **Write a shell script that takes the names of files being created in a directory and stores them in a file.**
- **What is the difference between `ADD` and `COPY`, and between `CMD` and `ENTRYPOINT`?**
- **How do you check the system load on a server?**
- **What is the difference between `git fetch` and `git pull`, and between `git rebase` and `git merge`?**
- **Write a shell script that compresses logs older than 30 days and deletes logs older than 90 days, and run it daily via cron.**
- **What is DNS?**
- **Questions on bare-metal servers and storage — HP and Dell.**
- **How would you optimise AWS resource costs, and by which methods?**

**Round 2 — technical manager (internal, in person)**

- **Create Terraform S3 resources and ensure the resource is deleted automatically after 7 days.**
- **What is a state file and how do you store it?**
- **What is Terraform lifecycle management and what does it do?**
- **Write both Jenkins pipeline syntaxes with examples — declarative and scripted.**
- **How do you secure secrets and credentials in your CI/CD process?**
- **Write an Ansible playbook and explain it.**
- **Reverse the words in a given list using Python, and remove the first duplicate element from a list.**
- **Explain the Kubernetes architecture and its components.**
- **What is the difference between a Pod and a Deployment, and what Services does Kubernetes have?**
- **Would you recommend a NodePort Service or a LoadBalancer Service, and why?**

**Round 3 — technical (client, in person)**

- **Have you worked on Salt, and what is the difference between Ansible and Salt?**
- **How did you use Ansible in your project and what tasks did you do?**
- **What are Ansible roles? Explain them.**
- **What is the inventory file, and how do you group hosts in it?**
- **Have you worked on Ansible Tower?**
- **Write an Ansible playbook and explain it.**
- **What are modules in Ansible, how many have you used, and can you name them?**
- **How do you debug an Ansible playbook?**
- **Write a Dockerfile and explain it, and how would you expose your application in Docker?**
- **You have a CI/CD process where manual intervention is required after the image is built. How and where would you configure that?**
- **What is IAM and how does it work?**
- **How did you migrate an application from an on-premises server to AWS — the process and the method?**

**Round 4 — client reporting manager (virtual)**

- **How do you check CPU details, and how do you check network details and traffic flow on a system — which command?**
- **In C++, if you do not want to store duplicate values, would you use a list or a set, and why?**
- **What are blue-green and canary deployment, and what is the difference?**
- **How do you create a copy of an existing Jenkins job?**
- **You have a microservices application that must scale dynamically with traffic. How would you design that on AWS?**
- **A critical production deployment failed and caused downtime. How would you handle the situation?**
- **What is the difference between liveness and readiness probes?**
- **What challenges have you faced in your organisation and how did you overcome them?**

### Round 13 — GitHub Actions and supply chain

- **What is the difference between `import` and `include` in Ansible?**
- **Can the same Terraform code be used for different cloud providers?**
- **What is the difference between a Deployment and a StatefulSet?**
- **Give a command to find a process and kill it.**
- **What is MongoDB and how does it work, and how does high availability work with primary and secondary nodes?**
- **What is artifact management, and which tool does your organisation use?**
- **How do you reduce the size of a Docker image?**
- **Write a Bash script for log analysis, one to get the total number of lines in a file, and one to count occurrences of the keyword `ERR` in a log.**
- **How do SSL and TLS certificates work?**
- **Explain the Maven lifecycle.**
- **What is the difference between continuous delivery and continuous deployment, and how do you implement them in Jenkins?**
- **Write a GitHub or GitLab pipeline that deploys a microservice with three services running in parallel.**
- **What is `runs-on` in a pipeline? Which runners does your organisation use, and do you know how to configure self-hosted runners — including for the application environment?**
- **How do you trigger a pipeline when code is pushed to a specific branch, ignore pushes to other branches, and trigger when a pull request is raised?**
- **What is a base image in a Dockerfile, and can you write a Dockerfile without one?**
- **What are decorators in Python?**
- **What is SonarQube and why is it used? Which is the optimised approach — running it on every pull request or on every push?**
- **How do you set up a manual trigger in GitHub Actions?**
- **If you use GitHub Marketplace actions, which are third-party, how do you address the security concerns?**
- **What is a matrix in GitHub Actions, and what does the `needs` keyword do? How do you run jobs in parallel?**
- **Briefly explain the architecture of your current project.**
- **Write the structure for building and pushing a Docker image in GitHub Actions.**
- **What GitHub branching strategy do you use? Explain it.**
- **How do you check the integrity of a Docker image or a file?**
- **How do you handle secrets in your project?**
- **What steps are in your GitHub Actions workflow file, and how is static code analysis configured in it?**
- **What are webhooks, and have you used them?**
- **How do you configure a pipeline with AWS or Docker?**

### Round 14 — cluster operations under failure

- **A Kubernetes node is in `Pending` — how do you debug it?**
- **A Pod is `Pending` because of a disk issue. How do you resolve it?**
- **Have you done a Kubernetes cluster upgrade?**
- **You are unable to evict Pods from a node. How do you resolve that?**
- **Describe the flow of network packets from the user hitting the application URL.**
- **During an upgrade the storage plugin has a problem and you cannot proceed. What do you do?** The candidate noted they could not answer this well.
- **What is a pull secret in OpenShift?**
- **What is a Kubernetes operator, and if you need to run a shell script before any container starts, how would you do it with an operator?**
- **How do you handle a Sev-1 issue?**
- **What extra component or service is present in a managed Kubernetes cluster in the cloud?**

### Round 15 — traffic, debugging, and platform breadth

- **The Pod is running fine and all parameters look good, but traffic is not reaching it when a user tries to access the application. What could be the reason?**
- **Why and when does `ImagePullBackOff` usually occur?**
- **How do you debug inside a container?**
- **If there are multiple Pods, how do they identify each other?**
- **How do Helm charts work, and do you actually use Helm for deployments?**
- **Explain the rolling update.**
- **If there is a deployment failure, what are your next steps and how do you approach debugging it?**
- **If sensitive data must be passed in a deployment, how do you pass it? What are Secrets, and which applications need them?**
- **Your deployment succeeded but the application returns 404. What is happening?**
- **Which API errors have you seen? What is a 504, and what is a 501? And explain what an API is.**
- **Questions on APIs and the difference between authorisation and authentication.**
- **Explain your observability stack.**
- **A new image has been deployed to production and it fails immediately. What steps do you take?**
- **How does Pod-to-Pod communication work, and what is the difference between an Ingress and an ingress controller?**
- **What cost optimisation strategies did you follow in your project?**
- **Explain trunk-based branching.**
- **Which errors have you faced working with Kubernetes?**
- **What is the difference between `CMD` and `ENTRYPOINT`?**
- **A PVC is in `Pending`. How do you debug it?**
- **If the application is responding slowly, how do you debug it and what could be the cause?**
- **How do you give a developer read-only access to RDS?**
- **What is a NAT gateway?**
- **Prometheus memory is growing enormously. How do you debug that?**
- **Production RDS storage is at 95%. How do you debug it and prevent it in future?**
- **Do you have migration experience?**
- **Explain the Kubernetes architecture and the Argo CD architecture, and do you have Helm experience?**
- **How did you manage secrets in your project?**
- **How do you map an SSL certificate to the Ingress file?**
- **How does a service mesh work, and do you have experience with one?**
- **A developer asks you to remove the code-quality stage from the pipeline because scanning is slow. What steps would you take?**
- **You have ten frontend and ten backend microservices. How would you design the CI/CD pipeline with Jenkins?**
- **How do you manage the Terraform state file and where do you store it?**
- **Write your Jenkins pipeline, and explain the purpose of the `agent`, `post`, and `environment` blocks.**
- **How do you take a complete Jenkins backup including jobs, configuration, and authentication? What are the ways to trigger a pipeline? And how would you give five Jenkins jobs view-only access to other users?**

### Round 16 — Azure DevOps pipelines and AWS forensics

**Azure DevOps**

- **What is the difference between build artefacts and pipeline artefacts, and which is better?**
- **Elaborate the pipeline steps to move a file from Azure Blob Storage to Google Cloud Storage in an automated way.**
- **If a pipeline is deleted by a team member, how would you recreate it and how would you prevent that in future?**
- **What is the difference between a stakeholder and an admin in Azure DevOps?**
- **How would you build a single or minimal set of reusable pipeline templates for 50 different applications?**
- **What is the syntax to reference a variable output from a previous stage in the current stage?**
- **How is sensitive data managed in pipelines, and how are authentication and networking established between an Azure DevOps pipeline and Azure Key Vault?**
- **How are pipeline logs stored in Azure DevOps?**

**Terraform**

- **Why are dynamic blocks used in Terraform? Write the skeleton for an Azure resource using one.**
- **How do you pass the subnet ID output of a VNet module as an input to a VM module?**
- **What is the difference between CloudFormation and Terraform, and how do you apply least privilege in CloudFormation stacks versus Terraform?**

**AKS and storage access**

- **How do you give only one Pod or application access to a storage account and restrict all other Pods in AKS?**
- **In a 32 GB AKS cluster where 30 GB is already used, can a new Pod with a 500 MB request and a 4 GiB limit be scheduled using HPA or VPA?**
- **Which Application Gateway setting is used to upload the SSL certificate, and why?**
- **Which alternative ingress controllers would you suggest, given the nginx ingress controller's deprecation?**

**AWS, IAM, and Jenkins**

- **List the running instances across five accounts.** The candidate answered using STS.
- **What do you do if an EC2 instance is compromised?** The candidate's answer was to set permissions to deny-all and then terminate the instance if it is not needed.
- **What types of IAM policy are there?**
- **List the IAM users whose access keys have not been used for more than 90 days, and delete the inline policy for users where `*` appears in the policy.**
- **How do you copy jobs from one Jenkins worker node to another, and how do you set up communication between Jenkins and Kubernetes?**
- **How is connectivity established from on-premises to the cloud, and how do you access S3 from a VPC securely?**

**Linux**

- **The filesystem is 50% full but cannot be written to, and `df -ih` shows it is full. What is happening?**
- **What is a zombie process?**

## Example

```text
Unattributed DevOps rounds 9-16 — 209 questions

  ROUND 9   Pure scenarios              12   /var 90% full, SSH lockout, LVM
                                             grow live, public S3 bucket,
                                             RDS migration, pipeline rollback
  ROUND 10  Fundamentals + project      14   why K8s over Swarm, etcd stops,
                                             port mismatch, state locking
  ROUND 11  Identity / DR / Azure       14   IAM user vs GitHub OIDC vs TFC
                                             role, no Lambda logs, DRS
                                             failover/failback, managed
                                             identity vs service principal
  ROUND 12  Four-round process          46   Python + shell + Docker + Git,
                                             Terraform 7-day auto-delete,
                                             Ansible/Salt, manual approval,
                                             failed prod deployment
  ROUND 13  GitHub Actions + supply     38   runs-on + self-hosted runners,
            chain                            marketplace action security,
                                             matrix, needs, image integrity,
                                             Sonar on PR vs push
  ROUND 14  Cluster ops under failure   10   node Pending, cannot evict Pods,
                                             storage plugin blocks upgrade,
                                             operator pre-start script, Sev-1
  ROUND 15  Traffic + debugging         34   pod healthy but no traffic, 404
                                             after success, PVC Pending,
                                             Prometheus memory growth, RDS 95%,
                                             developer wants Sonar removed
  ROUND 16  Azure DevOps + forensics    31   build vs pipeline artefacts, 50-app
                                             templates, blob->GCS, AKS memory
                                             maths, compromised EC2, inodes

WHAT THESE ROUNDS TEST THAT ROUNDS 1-8 DO NOT
  Rounds 9, 14, and 15 are almost entirely "here is a broken system". Round
  13 is a GitHub Actions specialist round. Round 16 is Azure DevOps plus AWS
  incident forensics. Prepare diagnostic METHOD and platform specifics, not
  definitions.
```

## Interview tips

- The inode question in round 16 is the sharpest Linux question in this whole collection, and `df -ih` is the giveaway. The filesystem has free _space_ but no free _inodes_, so it cannot create new files — classic when millions of tiny files accumulate, typically session files, cached objects, or unrotated per-request logs. Diagnose by finding the directories with the most entries (`for d in /*; do echo "$(find $d -xdev | wc -l) $d"; done`), then delete or archive the small files. The critical fact: you cannot add inodes to an existing ext4 filesystem — the count is fixed at `mkfs` time — so the real fix is recreating it with a higher inode count, or moving that workload to XFS which allocates inodes dynamically. Saying that is what wins this question. See [troubleshooting SSH failures, high CPU, and disk space](../linux-administration/how-do-you-troubleshoot-ssh-failures-high-cpu-and-disk-space-on-linux-servers.md).
- The AKS memory arithmetic in round 16 needs a careful answer, and the trap is that limits do not matter for scheduling. The scheduler compares the Pod's **request** — 500 MB — against _allocatable_ memory, not the limit of 4 GiB. With 30 of 32 GB used there is roughly 2 GB nominally free, but allocatable is lower still after kubelet and system reservations, and "used" needs clarifying: if it means 30 GB of _requests_ are already committed, then 500 MB likely still fits and the Pod schedules. Then say the important part: it schedules, but it can later be `OOMKilled` if it grows toward its 4 GiB limit while the node has nothing left — overcommitting limits is how you get node-level memory pressure and evictions. And neither HPA nor VPA creates capacity: HPA adds replicas that also need to be scheduled, VPA changes requests; only the Cluster Autoscaler adds nodes. That last correction is the real answer.
- The "Pod is healthy but no traffic reaches it" scenario appears in rounds 15 and 4, and there is an ordered list. Work from the outside in: DNS resolves to the load balancer; the ingress controller Pods are running and the Ingress has an `ADDRESS`; `ingressClassName` matches the controller; host and path rules match the request; the Service's `Endpoints` are **not empty** — a label-selector mismatch is the single most common cause; `targetPort` matches the container's listening port; the container is bound to `0.0.0.0` rather than `127.0.0.1`, which is a very common application-side cause; and no NetworkPolicy is silently dropping the traffic. Say that a healthy readiness probe only proves one path works. See [exposing an application in Kubernetes](../kubernetes/how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md).
- "Deployment succeeded but the app returns 404" is a different failure and should get a different answer. A 404 means something is answering — so routing reached a server that has no such route. Candidates: the Ingress path rule sends `/api` to a backend that expects `/`, and no rewrite annotation is set; the application has a context path or base URL that does not match; the wrong Service is selected by the rule; or the container serves a different route set than expected. Say "404 means we got to a server, so this is a routing or path problem, not a connectivity one" — that reasoning is what is being graded.
- The Lambda-with-no-CloudWatch-logs question in round 11 has a definite cause list: the execution role lacks `logs:CreateLogGroup`, `logs:CreateLogStream`, and `logs:PutLogEvents` — the most common reason even when the role "looks fine", because the managed basic-execution policy may be missing; the function is in a VPC with no route to the CloudWatch Logs endpoint, so it needs a NAT gateway or an interface VPC endpoint; the function is never actually invoked; you are looking at the wrong log group or region; or a resource policy or SCP denies logging. Say you would check whether the function is being invoked at all first, using the `Invocations` metric, to split "not running" from "running but not logging".
- The IAM-user versus GitHub-OIDC-role versus Terraform-Cloud-role comparison is an excellent question with a clear ranking. An IAM user with a long-lived access key is the least secure — the key can leak and lives forever until rotated. A GitHub OIDC role is far better: GitHub issues a short-lived signed token, AWS trusts that issuer with a condition on repository, branch, and environment, and no secret is stored anywhere. A Terraform Cloud dynamic-credentials role works the same way for runs executed there, and additionally gives you state management, policy enforcement, and run approvals. Say the deciding factor: use OIDC when the pipeline runs in GitHub Actions, use the Terraform Cloud role when runs execute in Terraform Cloud, and use neither if you can avoid a stored key. Emphasise that the OIDC trust policy **must** condition on the subject claim, or any repository could assume the role. See [least-privilege identity in the cloud](../cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md).
- Round 15's "developer wants code quality removed because scanning is slow" is a judgement question and the wrong answers are both extremes — refusing outright, or removing the gate. The good answer treats the complaint as legitimate and the requirement as non-negotiable: find out where the time actually goes, then fix the speed rather than the gate — incremental analysis on changed files only, caching, running the full scan on the pull request and a lighter check on push, moving the scan off the blocking path while still failing the merge, or parallelising it. Then agree an explicit gate policy: fail on new critical issues only, not the legacy baseline. Say you would come back with a measured before-and-after. That is the answer that gets you hired as a platform owner rather than a gatekeeper.
- Round 16's compromised-EC2 question deserves a better answer than the candidate's own. The correct order is contain, preserve, then eradicate: isolate the instance first by moving it to a quarantine security group with no ingress or egress rather than terminating it, and **do not terminate before taking a snapshot** — terminating destroys the forensic evidence. Then revoke the instance profile's permissions and rotate every credential it could reach, capture a memory and disk snapshot, review CloudTrail and VPC Flow Logs for what it accessed and talked to, then rebuild from a known-good AMI rather than cleaning the host. Saying "snapshot before you terminate" and "rebuild, do not disinfect" is what separates this from a guess. See [what an incident response plan is](../incident-management/what-is-an-incident-response-plan.md).
- The "cannot evict Pods from a node" question in round 14 has a canonical cause list: a PodDisruptionBudget that would be violated blocks eviction indefinitely — the most common cause by far; bare Pods with no controller need `--force`; Pods using `emptyDir` need `--delete-emptydir-data`; DaemonSet Pods are skipped and need `--ignore-daemonsets`; a long `terminationGracePeriodSeconds` or a hanging `preStop` hook makes it appear stuck; and there may be nowhere else to schedule the Pods, so eviction succeeds but replacements stay `Pending`. Say you would `kubectl get pdb` and read the drain output before reaching for `--force`.
- The storage-plugin-blocks-upgrade question is the one the candidate could not answer, so it is worth preparing. The answer is: stop and roll back rather than force through. Check the CSI driver's version compatibility matrix against the target Kubernetes version — an in-tree-to-CSI migration is a common cause — upgrade the driver _first_ if a compatible version exists, and if it does not, halt the upgrade, keep the cluster on the current version, and either wait for a compatible driver or plan a migration to a supported one. On a managed service, upgrade the storage add-on before the control plane. The principle to state: never upgrade a control plane past what your storage and network add-ons support, and verify add-on compatibility as a pre-flight check.
- A Kubernetes operator should be defined as a CustomResourceDefinition plus a controller that encodes operational knowledge — it watches your custom resource and reconciles the real world to match, which is how you automate a stateful system's backups, failovers, and upgrades. For the "run a shell script before any container starts" follow-up, the honest answer is that you would not use an operator for that: an **init container** is the built-in mechanism, and a mutating admission webhook is how you inject one automatically into every Pod. An operator would be the wrong tool for a per-Pod pre-start hook. Correcting the premise politely is the strong answer here.
- "What extra component exists in a managed cluster?" is looking for the **cloud controller manager** — the component that integrates Kubernetes with the provider's APIs to provision load balancers for Services, attach volumes, and manage node lifecycle. Add that the provider also runs and hides etcd and the API server, and installs managed add-ons such as the CNI and CSI drivers.
- The Terraform "delete the S3 resource automatically after 7 days" request in round 12 contains a category error worth naming politely: Terraform is a convergence tool and has no concept of a time-to-live on a resource — if you delete a resource out of band, the next apply recreates it. What you can do is an S3 _lifecycle_ rule expiring objects after 7 days (which deletes contents, not the bucket), or a scheduled pipeline that runs `terraform destroy` on a temporary workspace, or a Lambda on an EventBridge schedule tagging and deleting ephemeral resources. Say which interpretation you are answering.
- Round 13's GitHub Actions questions have crisp answers worth memorising: `runs-on` selects the runner (a GitHub-hosted image label, or `self-hosted` plus custom labels); self-hosted runners exist for private network access, specific hardware, or cost at high volume, and must be isolated because a compromised workflow gets code execution on them — never use self-hosted runners on public repositories. `needs` orders jobs and creates a dependency; `matrix` fans one job out across combinations of values with `fail-fast` and `max-parallel` controls; jobs are parallel by default, so `needs` is what serialises them. A manual trigger is `workflow_dispatch`, optionally with typed `inputs`. Branch filtering is `on.push.branches` with `branches-ignore` or `paths` filters, and pull requests are `on.pull_request`. See [what a CI/CD pipeline is](../cicd/what-is-ci-cd-pipeline.md).
- The marketplace-action security question is a supply-chain question with a specific expected answer: pin third-party actions to a full commit SHA rather than a tag, because tags are mutable and can be repointed at malicious code; review the action's source; prefer official or verified publishers; restrict which actions are allowed at the organisation level; set the default `GITHUB_TOKEN` permissions to read-only and grant per-job; and avoid passing secrets to third-party actions at all. Pinning to a SHA is the single answer they want to hear. See [SLSA and securing the software supply chain](../devsecops/what-is-slsa-and-how-do-you-secure-the-software-supply-chain.md) and [signing and verifying container images](../devsecops/how-do-you-sign-and-verify-container-images.md).
- "Sonar on every PR or every push?" has a defensible answer: on the pull request, because that is the gate that matters and it lets you analyse only new code, while every push wastes analysis on work-in-progress commits. Add a full scan on merge to the default branch to keep the baseline accurate. Say the reasoning — gate where the decision is made — rather than just picking one.
- The 50-reusable-pipeline-templates question in round 16 wants a template hierarchy: a small number of parameterised YAML templates in a central repository, referenced by each application's pipeline with `extends` and `resources.repositories`, with `parameters` for the per-application differences and `steps`/`jobs`/`stages` templates composed together. Add governance — a required template check so a pipeline cannot bypass the standard, and template versioning by tag so 50 applications do not all break at once when you change it. That last point is the one that shows scale experience.
- "Build artefacts versus pipeline artefacts" has a factual answer in Azure DevOps: build artefacts are the older mechanism backed by file-share or server storage, while pipeline artefacts are newer, faster, use content-addressable deduplicated storage, and are the recommended default. Say pipeline artefacts, and say why — speed and deduplication.
- The Prometheus-memory-growth question in round 15 has a specific cause: cardinality. Every unique label-value combination is a separate time series held in memory, so a label carrying a request ID, a user ID, a pod name, or a full URL path explodes the series count. Diagnose with `topk` on `count by (__name__)({__name__=~".+"})` and the TSDB status page, then fix by dropping or aggregating high-cardinality labels with `metric_relabel_configs`, shortening retention, reducing scrape frequency for chatty targets, and offloading long-term storage to Thanos or Mimir. Naming cardinality unprompted is what marks the answer. See [writing effective PromQL queries and Alertmanager rules](../monitoring-and-logging/how-do-you-write-effective-promql-queries-and-alertmanager-rules.md).
- The "RDS at 95% storage" question wants both halves. Immediate: enable or verify storage autoscaling, extend the allocated storage — which is an online operation but cannot be reversed — and find what is consuming it, usually bloat, unvacuumed tables, oversized indexes, binary logs, or unarchived audit tables. Prevention: a CloudWatch alarm on `FreeStorageSpace` well before 95%, storage autoscaling with a sane ceiling, retention and archival policies, and monitoring table growth trends rather than a single threshold. See [running a highly available database on AWS](../aws-engineering/how-do-you-run-a-highly-available-database-on-aws.md).
- The 20-microservice Jenkins pipeline question wants a template answer, not 20 pipelines: one shared library defining the standard build-test-scan-publish-deploy flow, a `Jenkinsfile` per service that calls it with parameters, multibranch pipelines so branches and pull requests get jobs automatically, and change detection so a monorepo only builds affected services. Say that 20 copy-pasted pipelines cannot be changed once, which is the reason the shared library exists. See [Jenkins shared libraries](../cicd/how-do-you-use-jenkins-shared-libraries.md).
- LVM growth with no downtime is a fixed sequence worth having memorised: attach the new disk, `pvcreate /dev/sdX`, `vgextend <vg> /dev/sdX`, `lvextend -l +100%FREE /dev/<vg>/<lv>`, then grow the filesystem online with `resize2fs` for ext4 or `xfs_growfs` for XFS. Say that growing is online and safe while shrinking XFS is impossible — that asymmetry is the follow-up.
- A zombie process is one that has exited but whose exit status has not been reaped by its parent, so it holds a process-table entry and shows as `Z` in `ps`. It consumes no CPU or memory, and you cannot kill it — you have to make the parent call `wait()`, or kill the parent so `init` adopts and reaps it. Add that many zombies indicate a buggy parent, and that this is exactly why the pause container in a Kubernetes Pod acts as PID 1 to reap orphans. See [basic Linux commands](../linux-administration/what-are-the-basic-linux-commands-every-devops-engineer-should-know.md).
- The nginx-ingress-controller deprecation question is current and worth knowing: the community ingress-nginx project has entered maintenance-only status, so the alternatives to name are the Gateway API implementations — Envoy Gateway, Istio's gateway, Cilium's, and Traefik — plus cloud-native controllers such as the AWS Load Balancer Controller and Application Gateway Ingress Controller on Azure. Say that Gateway API is the successor to Ingress and that a migration is the real answer, not just swapping controllers.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you scale CI/CD across many services and teams?]] (`#459`): [How do you scale CI/CD across many services and teams?](../cicd/how-do-you-scale-ci-cd-across-many-services-and-teams.md)
- [[How do you use Jenkins shared libraries?]] (`#268`): [How do you use Jenkins shared libraries?](../cicd/how-do-you-use-jenkins-shared-libraries.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
