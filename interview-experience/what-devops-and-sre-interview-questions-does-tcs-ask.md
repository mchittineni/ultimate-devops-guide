---
title: "What DevOps and SRE interview questions does TCS ask?"
id: 384
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - tcs
  - configuration-management
  - kubernetes
  - docker
  - azure-engineering
  - aws-engineering
  - devops-tools-and-automation
  - linux-administration
  - container-orchestration-advanced
---

# What DevOps and SRE interview questions does TCS ask?

## Questions

### Round set 1 — Artifactory, Ansible, and monitoring (9 YOE, 4 relevant)

- **What is JFrog Artifactory, what are its use cases, and what repository types does it have?**
- **What is JFrog Xray?**
- **What is the difference between a GitHub repository and a JFrog repository?**
- **What is Ansible Tower?**
- **What are Ansible roles, and which Ansible modules have you used?**
- **What is a Jinja2 template?**
- **What is Nagios, and how do you integrate Jenkins with it?**
- **How do you find the space available on a Linux mount point?**
- **What is your branching strategy?**

### Round set 2 — Ansible and Azure DevOps (4-5 YOE)

- **What is a role in Ansible?**
- **How do you encrypt data in Ansible?**
- **What does idempotent mean in Ansible?**
- **What is a module in Ansible?**
- **What are libraries in Python?**
- **What are deployment groups in Azure DevOps?**
- **How do you set approvals in a pipeline?**
- **What is the difference between a Microsoft-hosted agent and a self-hosted agent?**
- **What is the difference between a monolith and microservices?**
- **Explain any automation you have done in your project.**
- **Explain the flow of how a pipeline triggers across different environments.**
- **When a developer is working on code, what steps must they take — alongside the DevOps engineer — for the pipeline to run?**
- **Which deployment strategies do you use in Kubernetes? Explain canary and blue-green.**
- **What is DevSecOps, and have you used any tools for scanning images?**
- **What is the difference between a classic pipeline and a YAML pipeline?**
- **Give me the pipeline steps for an Angular, Java, or .NET application.**

### Round set 3 — SRE, Ansible, Kubernetes, and AWS

- **What is an Ansible playbook, what is a role and how do you create one, what is Ansible Tower, and what does idempotent mean?**
- **How does Ansible work?**
- **When you run a module such as `yum` or `apt` and get "command not found", what is the reason?**
- **What is the difference between a PV and a PVC in Kubernetes?**
- **What are ConfigMaps and the scheduler in Kubernetes?**
- **How does Kubernetes work — how do the control-plane and worker nodes communicate, and what runs inside each?**
- **What is `CrashLoopBackOff` and how do you troubleshoot it?**
- **Why does a Pod show `Pending` status?**
- **If a rollback fails, how do you handle it? And what is the command to roll back to a specific revision?**
- **Explain your current e-commerce project and its architecture.**
- **What types of node did you deploy on AWS?**
- **What is the difference between an interface endpoint and a gateway endpoint in AWS?**
- **What is the Terraform state file, and what interprets it?**
- **What do you do if `terraform apply` takes too long?**
- **How do you assign and print a variable in Bash?**
- **What are lists and tuples in Python?**
- **How do you restrict access to AWS resources for a specific user — for example limiting a user to EC2 and RDS only?**
- **When you create a VPC, which default components are added?**
- **Explain the AWS architecture in this diagram — CodePipeline, CodeBuild, CodeDeploy, CloudFormation, and CloudWatch.**
- **Do you have Windows or Linux experience, and what types of file permission exist in Linux?**

### Round set 4 — Docker layers and StatefulSets (client round)

- **What is Terraform drift?**
- **What is the difference between the `COPY` and `ADD` commands in a Dockerfile?**
- **If a Docker image becomes very large with many layers, what steps would you take to reduce its size?**
- **If you have 10 layers in a Dockerfile and layer 6 fails, after fixing it where does the rebuild start from, and why?**
- **What is the difference between bind mounts and volumes in Docker?**
- **Why do you need a StatefulSet when you can attach a PVC to a Deployment and make it stateful? And if you can run MySQL with a Deployment plus a PVC, why is a StatefulSet needed?**
- **If one Pod is created by a Deployment and another by a StatefulSet, will the StatefulSet Pod always stay on the same node?**
- **What happens if you scale a Deployment that has one PVC from one replica to three?**
- **What Service types exist in Kubernetes apart from ClusterIP, NodePort, and LoadBalancer?**
- **Why does a Pod created from a Deployment have two sets of random characters in its name?**

## Example

```text
TCS — DevOps Engineer / SRE, four reported interviews (~63 questions)

  SET 1  Artifactory + Ansible (9 YOE)     9   JFrog Artifactory/Xray/repo
                                               types, GitHub vs JFrog, Nagios
                                               plus Jenkins, Jinja2
  SET 2  Ansible + Azure DevOps (4-5 YOE) 16   deployment groups, approvals,
                                               classic vs YAML pipelines,
                                               per-stack pipeline steps
  SET 3  SRE breadth                      20   module "command not found",
                                               interface vs gateway endpoint,
                                               slow terraform apply, restrict
                                               a user to EC2 + RDS, VPC defaults
  SET 4  Docker + StatefulSets            10   layer 6 fails — where does the
                                               rebuild resume, StatefulSet vs
                                               Deployment+PVC (asked twice),
                                               scaling one PVC to 3 replicas

TCS'S DISTINCTIVE TOPIC
  JFrog Artifactory and Xray appear here and almost nowhere else in this
  collection. If TCS is your target, learn the repository types (local,
  remote, virtual) — it is a cheap, easily-prepared differentiator.
```

## Interview tips

- The "layer 6 fails, where does the rebuild resume" question has an exact answer: the build resumes **from layer 6**, because layers 1 to 5 are unchanged and still in the build cache — Docker validates the cache layer by layer and reuses everything up to the first changed instruction. Then add the crucial second half: layers 7 to 10 are **rebuilt** even if their instructions did not change, because each layer's cache key depends on the layer beneath it. So a fix at 6 invalidates everything above it. That cascade is the real content of the question, and it is why you order a Dockerfile with stable steps low and volatile steps high. See [reducing Docker image size and build time](../docker/how-do-you-reduce-docker-image-size-and-build-time.md).
- The "why do I need a StatefulSet if a Deployment plus a PVC works" question is asked twice, so it clearly matters, and the scaling question is the proof. A Deployment with one PVC works fine at **one replica**. Scale it to three and all three Pods try to mount the _same_ PVC — with `ReadWriteOnce` on EBS that only succeeds for Pods landing on the same node, so the others get stuck `Pending` or `ContainerCreating` with a volume attachment error; and even where the mount succeeds, three MySQL processes writing one data directory will corrupt it. A StatefulSet solves this with `volumeClaimTemplates`, giving each replica its own PVC, plus a stable ordinal name and DNS record via a headless Service, and ordered creation and updates so replication and quorum are respected. Say "a Deployment gives you _a_ stateful Pod; a StatefulSet gives you a _set_ of individually identified stateful Pods" — that is the distinction. See [StatefulSets](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md).
- "Will the StatefulSet Pod always stay on the same node?" is a trap and the answer is **no** — nothing pins a StatefulSet Pod to a node. What is stable is its _identity_ and its _volume_, not its placement. In practice it often appears pinned, because a zonal volume can only be attached in its own availability zone, so the scheduler is constrained to nodes in that zone — and with a `local` PersistentVolume it genuinely is pinned by the volume's node affinity. Distinguishing "stable identity" from "fixed node" is what makes the answer correct.
- The two-random-suffixes question is a nice piece of mechanism: a Deployment does not create Pods directly — it creates a **ReplicaSet**, whose name is the Deployment name plus a hash of the Pod template, and the ReplicaSet then creates Pods with its own name plus a random suffix. So `web-7d9f8b6c4d-x2k9p` is `deployment-templatehash-podrandom`. Say that the template hash is what makes rollback possible, because each revision has its own ReplicaSet — which links directly to the rollback question in round 3.
- The "module command not found" question in round 3 has a specific cause worth naming precisely: Ansible modules such as `yum` and `apt` are Python code executed **on the managed host**, so the error almost always means the underlying package manager or Python interpreter is missing or wrong on the target — for example running the `apt` module against a RedHat host, or the host having no Python at all, or `ansible_python_interpreter` pointing at a nonexistent path. Say the diagnostic: run `-vvv` to see which interpreter was used, and set `ansible_python_interpreter` explicitly or use the generic `package` module for cross-distribution work. See [what Ansible is](../infrastructure-as-code/what-is-ansible.md).
- Interface versus gateway VPC endpoint has a short factual answer: gateway endpoints exist only for **S3 and DynamoDB**, are free, and work through route-table entries; interface endpoints are PrivateLink ENIs in your subnets, charge per hour and per gigabyte, and cover nearly every other service. Naming the two-service limit is what proves you know it rather than guessing. See [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md).
- "What do you do if `terraform apply` takes too long?" wants diagnosis before optimisation: run with `TF_LOG=DEBUG` to see which resource is slow, since it is usually one resource waiting on a cloud operation such as an RDS instance or a CloudFront distribution rather than Terraform itself being slow. Then the levers: split a large state so each apply touches fewer resources, raise `-parallelism`, remove data sources that call slow APIs on every run, and cache the provider plugin directory in CI. Say that state size is the usual culprit and that some waits are simply the cloud provider's provisioning time, which no amount of tuning removes.
- The "restrict a user to EC2 and RDS only" question maps to a specific policy pattern: grant `ec2:*` and `rds:*` on the resources they need, and rely on the implicit deny for everything else — or, if you need a guardrail that survives someone attaching another policy, add a statement with `"Effect": "Deny"` and `"NotAction": ["ec2:*", "rds:*"]`. Add conditions on resource tags so they can only touch their own instances, and say that a permission boundary or an SCP is how you enforce this at a level the user cannot escape. See [how AWS IAM evaluates a request](../aws-engineering/how-does-aws-iam-evaluate-a-request.md) and [least-privilege identity in the cloud](../cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md).
- "Which default components does a new VPC get?" has an exact list: a default route table, a default network ACL that allows all inbound and outbound traffic, and a default security group that allows all outbound plus inbound from itself. Note what you do **not** get: no subnets, no internet gateway, and no NAT — those you create. And five addresses are reserved in every subnet you make. That "what you do not get" framing is the strongest version of the answer.
- The failed-rollback question needs a real answer rather than "try again". First establish why it failed: `kubectl rollout status` and `describe` on the Deployment, because the usual causes are that the previous ReplicaSet no longer exists (`revisionHistoryLimit` too low), the old image tag has been deleted from the registry, or the old version is incompatible with a database migration that already ran. Then the recovery: deploy a known-good image tag explicitly rather than relying on revision history, and if the schema is the blocker, roll _forward_ with a fix instead. The command they asked for is `kubectl rollout undo deployment/<name> --to-revision=<n>`, with `kubectl rollout history` to list revisions. Say that irreversible migrations are why expand-and-contract exists.
- JFrog is TCS's signature topic and the answers are short: Artifactory is a universal binary repository manager for Maven, npm, Docker, and more, holding your build artefacts and proxying public registries. Its **repository types** are the detail they want — _local_ for your own artefacts, _remote_ as a caching proxy of an external registry, and _virtual_ aggregating several into one URL. Xray is the security and compliance scanner that walks the dependency graph of stored artefacts for vulnerabilities and licence violations. And GitHub versus JFrog is a source-versus-binary distinction: Git stores source history, Artifactory stores immutable built binaries with promotion between repositories. See [what a CI/CD pipeline is](../cicd/what-is-ci-cd-pipeline.md).
- Bind mounts versus volumes has a clean answer: a bind mount maps a host path into the container, so it depends on the host's filesystem layout and is mainly a development convenience; a volume is managed by Docker in its own storage area, is portable, works with drivers and plugins, and is the production choice for persistent data. Add that neither belongs in an image layer, which is why volumes exist at all.
- Azure DevOps specifics: **deployment groups** are logical sets of target machines each running an agent, used by classic release pipelines to deploy to VMs — with environments and environment resources being the modern YAML equivalent. **Approvals** attach to an _environment_ (Approvals and checks), not to the YAML, which is the fact people get wrong. **Classic versus YAML**: classic is UI-configured and not versioned with the code, YAML lives in the repository so it is reviewable, branchable, and templatable — and YAML is the current recommendation. **Microsoft-hosted versus self-hosted agents**: clean ephemeral VMs with no private-network access, versus your own machines with private access, custom tooling, and caching, at the cost of patching them and the risk that state persists between jobs.
- Nagios plus Jenkins is a legacy pairing and the honest answer wins: Nagios is a host and service monitoring system using check plugins and thresholds, integrated with Jenkins either by having Jenkins trigger checks and consume results via the Nagios plugin or NRDP, or by Nagios monitoring the Jenkins service itself. Then say that Prometheus with Alertmanager is what you would use today for a containerised estate, and why — pull-based service discovery suits ephemeral workloads that Nagios' static host model does not. See [monitoring in DevOps](../monitoring-and-logging/what-is-monitoring-in-devops.md).
- The "steps a developer must take" question in round 2 is really about the contract between developer and platform: branch from the agreed base, commit and push, ensure the pipeline definition exists in the branch, open a pull request which triggers build, tests, and scans, get the required reviews and green checks, then merge — at which point the platform promotes the artefact. Framing it as a contract rather than a list of clicks is what a platform engineer sounds like. See [Git branching strategy](../version-control/what-is-git-branching-strategy.md).
- For the per-stack pipeline steps question, be ready with one concrete chain each: Angular — `npm ci`, lint, unit test, `ng build --prod`, publish the `dist` bundle, deploy to a CDN or bucket; Java — `mvn clean verify`, publish the JAR to Artifactory, build and scan an image, deploy; .NET — `dotnet restore`, `build`, `test`, `publish`, package and deploy. Say the common shape underneath: restore dependencies, build once, test, scan, publish an immutable artefact, promote it.
- `terraform drift` is not a command, so correct it: `terraform plan` reveals drift, and `plan -refresh-only` (with `apply -refresh-only`) is the purpose-built way to detect and reconcile it — the old `terraform refresh` being deprecated in its favour. Terraform Cloud has a managed drift-detection feature, which may be what the interviewer means. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- On Linux, `df -h /mount/point` gives space on a mount, and `df -i` gives inode usage — mention the inode variant, because a filesystem can be half empty and still unable to create files. File permissions are read, write, and execute for user, group, and other, expressed octally, plus the special bits (setuid, setgid, sticky) and ACLs. See [Linux filesystem hierarchy](../linux-administration/what-is-linux-file-system-hierarchy.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
