---
title: "What DevOps interview questions does LTIMindtree ask?"
id: 345
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - ltimindtree
  - infrastructure-as-code
  - kubernetes
  - cicd
  - aws-engineering
  - azure-engineering
  - docker
  - devsecops
  - devops-tools-and-automation
---

# What DevOps interview questions does LTIMindtree ask?

## Questions

### Round set 1 — mechanics and edge cases

- **Can you install Docker inside a container?**
- **You created three instances from a Terraform script where the names are given as a list. If you remove the second name from that list and apply again, what happens to the three instances that already exist?**
- **A Jenkins pipeline has five stages and the fifth has a syntax error. What happens when you run it?**
- **What are the main differences between a scripted and a declarative pipeline?**
- **What is the difference between code quality and code coverage?**
- **What is the default quality gate in SonarQube?**
- **How do you apply a YAML manifest without having a manifest file on disk?**

### Round set 2 — AWS and tooling breadth (5 YOE)

- **What are your day-to-day activities in your current role?**
- **What is `git rebase`?**
- **What is `git clone`?**
- **What is the `git cherry-pick` command?**
- **Explain the AWS CodeCommit flow.**
- **What are the deployment types?**
- **What is `appspec.yml` used for?**
- **What are Lambda functions, and how do you secure a Lambda?**
- **Explain the Kubernetes architecture.**
- **What goes in a Dockerfile?**
- **How do you handle environment variables in AWS?**
- **Questions on Ansible.**

### Round set 3 — hands-on writing round (5 YOE)

- **Write Terraform to create an Azure App Service, or Terraform to create an AWS Lambda.**
- **Build three different images, store them in ECR or ACR, and deploy them to EKS or AKS — write the Kubernetes YAML files.**
- **Explain your branching strategy.**
- **You have an Application Gateway, the backend services are healthy, and you are getting a 404. How do you troubleshoot further?**
- **What is the difference between a firewall and a network security group?**

### Round set 4 — pipeline and cluster operations (3 YOE)

- **How do you deploy a Python application on AWS using a Jenkins pipeline?**
- **How does your day start and what activities do you perform?**
- **How do you upgrade EKS?**
- **How do you handle it when a Pod dies?**
- **Your AWS Jenkins pipeline takes a long time. How do you troubleshoot that?**
- **Create a manifest for two nginx replicas.**
- **Create an S3 bucket for the Terraform state file whose objects expire within 30 days.**
- **How do you provide security in Docker?**

### Round set 5 — L2 design round (3-5 YOE)

- **How do you design a fault-tolerant architecture in the cloud?**
- **How do you manage secrets securely in GitOps or deployment pipelines, and how do you secure sensitive data such as passwords or API keys in infrastructure setups?**
- **How do you implement blue-green or canary deployments with container orchestration?**
- **How do you manage multiple environments using reusable infrastructure code?**
- **What are backends for in infrastructure as code, and how do you implement remote state with locking?**
- **How do you implement rollback in an automated deployment pipeline?**
- **How do readiness and liveness probes work, and why do they matter in production?**
- **How do you troubleshoot a Pod stuck in `CrashLoopBackOff`?**
- **How does your GitOps tool detect drift, and how do you manage it?**
- **Write a script that monitors a service and restarts it if it fails, with proper logging.**
- **How do you handle parallel execution in CI/CD workflows?**
- **What is the difference between `count` and `for_each` in infrastructure code, and when should you use each?**
- **How do you monitor and alert on cloud resources effectively?**

## Example

```text
LTIMindtree — DevOps Engineer, five reported interviews (~45 questions)

  SET 1  Mechanics + edge cases    7   Docker-in-Docker, list re-index on
                                       Terraform apply, syntax error in
                                       stage 5, code quality vs coverage,
                                       apply YAML with no file
  SET 2  AWS + tooling breadth    12   CodeCommit flow, appspec.yml,
                                       securing Lambda, env vars in AWS
  SET 3  Hands-on writing          5   write TF for App Service/Lambda,
                                       3 images -> ECR/ACR -> EKS/AKS,
                                       App Gateway 404, firewall vs NSG
  SET 4  Pipeline + cluster ops    8   Python on AWS via Jenkins, EKS
                                       upgrade, slow pipeline, 2-replica
                                       manifest, state bucket with 30-day
                                       expiry, Docker security
  SET 5  L2 design round          13   fault tolerance, GitOps secrets and
                                       drift, rollback, probes, count vs
                                       for_each, service-watchdog script

TWO QUESTIONS WITH A DEFINITE RIGHT ANSWER
  The Terraform list re-index (set 1) and the stage-5 syntax error (set 1).
  Both catch people who have never actually hit them.
```

```hcl
# Set 4's state bucket with a 30-day expiry — note the contradiction worth
# raising out loud: expiring your own STATE is dangerous. This is the right
# shape for a LOGS bucket; for state you expire noncurrent versions only.
resource "aws_s3_bucket" "tfstate" {
  bucket = "acme-tfstate"
}

resource "aws_s3_bucket_versioning" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_lifecycle_configuration" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  rule {
    id     = "expire-old-versions"
    status = "Enabled"
    noncurrent_version_expiration { noncurrent_days = 30 } # NOT the current object
  }
}
```

## Interview tips

- The Terraform list question is the best in the whole set and it has an exact, surprising answer. With `count` over a list, resources are addressed by _index_ — `[0]`, `[1]`, `[2]`. Remove the middle element and the list shifts, so index 1 now holds what used to be at index 2 and index 2 no longer exists. Terraform therefore plans to **modify instance 1 and destroy instance 2** — it does not simply delete the one you removed. Say that, then give the fix: `for_each` over a map or set keys resources by a stable string, so removing one element destroys exactly that one and leaves the others untouched. This is also the answer to set 5's `count` versus `for_each` question, so the two link together.
- The stage-5 syntax error question depends on which syntax you use, and saying so is the strong answer. A **declarative** pipeline is parsed and validated up front, so a syntax error means the pipeline fails immediately without running stages 1 to 4. A **scripted** pipeline is Groovy executed sequentially — but Groovy is compiled before execution, so a true compile-time syntax error still fails before anything runs; only a _runtime_ error in stage 5 would let the first four complete. Distinguishing compile-time from runtime is what makes this answer correct rather than a guess. See [Jenkins pipelines](../cicd/what-are-jenkins-pipelines.md).
- Applying a manifest with no file on disk has several valid answers and naming two or three wins it: pipe from stdin with `kubectl apply -f -` and a heredoc, apply from a URL with `-f https://...`, use `kubectl create <resource> --dry-run=client -o yaml` to generate then apply, or use imperative commands such as `kubectl create deployment nginx --image=nginx --replicas=2` — which also answers the two-replica manifest question in set 4. Mention `kubectl run --dry-run=client -o yaml` as the fastest way to get a manifest skeleton in an interview.
- "Can you install Docker inside a container?" is yes, with important caveats. Docker-in-Docker requires the `--privileged` flag, which effectively removes container isolation and is a real security risk; the common alternative is mounting the host's Docker socket, which is arguably worse because it grants root on the host. Say that in a Kubernetes CI context the right answers are rootless builders — Kaniko, Buildah, or BuildKit — precisely to avoid privileged mode. See [how namespaces, cgroups, and capabilities isolate a container](../docker/how-do-namespaces-cgroups-and-capabilities-isolate-a-container.md).
- Code quality versus code coverage is easy to state and easy to make impressive: coverage measures what fraction of code your tests execute, quality measures defects, complexity, duplication, and maintainability. Add the point that matters — 100% coverage says nothing about whether the assertions are meaningful, so coverage is a necessary but not sufficient signal. Then, for the default SonarQube quality gate, name it accurately: the built-in "Sonar way" gate is focused on _new_ code, requiring no new issues, at least 80% coverage on new code, duplication under 3%, and all new security hotspots reviewed. Emphasising that it gates new code rather than the legacy baseline is what shows real use. See [SAST, DAST, IAST, and SCA](../devsecops/what-is-the-difference-between-sast-dast-iast-and-sca.md).
- The state-bucket-with-30-day-expiry request contains a hazard you should flag politely: expiring the current version of a state object would destroy your ability to manage the infrastructure. Say you would expire _noncurrent versions_ after 30 days while keeping versioning on, and that if they genuinely mean an artefacts or logs bucket then a straightforward `expiration` rule is correct. Spotting the difference is the answer. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- The Application Gateway 404 with healthy backends points at routing, not health. Check the path-based routing rules and whether a rewrite or path override is sending the request to a path the backend does not serve, whether the backend expects a specific `Host` header and the gateway is not overriding it, whether the listener's hostname matches, and whether the backend settings use the wrong path prefix. Say that a healthy probe only proves one URL works — the probe path may differ from the request path.
- Firewall versus NSG on Azure: an NSG is a distributed layer-3 and layer-4 stateful allow-and-deny rule set attached to a subnet or NIC, free, with no logging of application content; Azure Firewall is a managed stateful appliance with FQDN filtering, threat intelligence, application rules, and NAT, deployed in a hub subnet, and it costs real money. Say NSGs are your default segmentation and Firewall is for centralised egress control and inspection. See [defence in depth for a cloud network](../network-security/how-do-you-design-defence-in-depth-for-a-cloud-network.md).
- `appspec.yml` is the CodeDeploy file describing what to copy where and which lifecycle hooks to run — `BeforeInstall`, `AfterInstall`, `ApplicationStart`, `ValidateService` — and its shape differs between EC2 and ECS or Lambda deployments. Pair it with the CodeCommit flow answer: commit triggers CodePipeline, CodeBuild produces the artefact using `buildspec.yml`, CodeDeploy consumes it using `appspec.yml`. See [building a CI/CD pipeline with CodePipeline, CodeBuild, and CodeDeploy](../aws-engineering/how-do-you-build-a-ci-cd-pipeline-using-aws-codepipeline-codebuild-and-codedeploy.md).
- Securing Lambda should cover the whole surface: a least-privilege execution role, environment variables encrypted with a customer-managed KMS key or better held in Secrets Manager, VPC attachment only when it needs private resources, reserved concurrency to bound blast radius and cost, resource policies restricting who may invoke it, code signing, and dependency scanning of the deployment package or layer.
- GitOps drift detection is a two-part answer: the controller continuously compares the live cluster state against the desired state in Git and reports `OutOfSync`, and you then choose between manual sync, automated sync, and automated self-heal which reverts the manual change. Say that self-heal is what actually eliminates drift, and that pruning must be enabled for deletions to propagate. See [GitOps](../devops-tools-and-automation/what-is-gitops.md) and [Argo CD](../devops-tools-and-automation/what-is-argocd.md).
- For the service-watchdog script, the answer that impresses is to say you would not write one: `systemd` already does this with `Restart=on-failure`, `RestartSec`, and `StartLimitBurst`, and it logs to the journal. Then, since they asked for a script, write one with `set -euo pipefail`, a `systemctl is-active` check, logging via `logger` so it lands in syslog, and a guard against restart loops. Offering the built-in first and the script second is the senior answer. See [managing services in Linux](../linux-administration/how-do-you-manage-services-in-linux.md) and [writing a production-grade Bash script](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md).
- The slow-pipeline question wants measurement before action: read the stage timings to find where the time actually goes, then apply the relevant lever — parallelise independent stages, cache dependencies and Docker layers, order the Dockerfile so installs cache above source copies, run only affected tests, use larger or more agents, and move long integration suites off the blocking path.
- "How do you handle it when a Pod dies" is deliberately open. Say that a Pod dying is normal and the platform handles it — the controller reconciles the replica count, the scheduler places a replacement, and readiness gates traffic — then pivot to what _you_ do: read the exit code and previous logs to find out why, check whether it was `OOMKilled`, and fix the cause rather than the symptom. See [troubleshooting a Pod stuck in Pending or CrashLoopBackOff](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md) and [how probes differ](../kubernetes/how-do-liveness-readiness-and-startup-probes-differ.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
