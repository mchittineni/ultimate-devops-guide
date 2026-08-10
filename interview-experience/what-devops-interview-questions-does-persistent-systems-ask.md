---
title: "What DevOps interview questions does Persistent Systems ask?"
id: 369
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - persistent-systems
  - kubernetes
  - aws-engineering
  - azure-engineering
  - cicd
  - infrastructure-as-code
  - devsecops
  - scalability-and-high-availability
  - serverless-architecture
---

# What DevOps interview questions does Persistent Systems ask?

## Questions

### Round set 1 — Kubernetes, GitHub Actions, and AWS (9 YOE, 5 in DevOps)

**Kubernetes**

- **Explain your current project and your activities in it.**
- **Explain the Kubernetes architecture.**
- **How do you upgrade a Kubernetes cluster?**
- **What is the difference between Pod affinity and node affinity?**
- **What are the HPA and the VPA?**

**GitHub Actions**

- **What is the matrix strategy in GitHub Actions?**
- **How does caching work in GitHub Actions?**
- **What is a stale branch?**

**AWS**

- **What are ACM, CloudTrail, CloudFront, and CloudFormation?**
- **What is CloudWatch, and how do you create a custom metric in it?**
- **How do you log into an EC2 instance if you have lost the `.pem` key?**
- **What makes a subnet public or private?**
- **Where does a NAT gateway reside?**

### Round set 2 — Azure architecture and Terraform at scale (13 YOE, 5 in DevOps)

- **Design a highly available, redundant three-tier architecture on Azure.**
- **Design an architecture for a React frontend and a Node.js backend — which Azure services would you use?**
- **You have an e-commerce application and it is slow. How do you troubleshoot it?**
- **What are the steps to create an Azure DevOps pipeline?**
- **What is GitHub Actions?**
- **In Azure Monitor, which metrics are used to monitor Kubernetes?**
- **What is the module approach in Terraform? Explain it.**
- **Your Terraform codebase has a thousand lines and keeps growing, and over time it becomes slow. How would you approach that?**
- **Have you worked with Python?**

### Round set 3 — AWS breadth and design reasoning (5 YOE)

- **Explain your last project, and which AWS resources you used in your previous role.**
- **Can you write Python?** Samples were provided.
- **What is `terraform state mv`, and explain the Terraform state file.**
- **What are microservices?**
- **Explain the flow of a CI/CD pipeline.**
- **Have you handled Lambda? Explain your project, and where have you used it?**
- **How do you ensure Pod-to-Pod communication?**
- **What is the hierarchy of Kubernetes objects?**
- **Given a project — EC2, EKS, or anything else — what would you consider from prerequisites through to output?**
- **How would you decide what type of environment a deployment requires?**
- **What is a subnet?**
- **You have an EC2 instance that must not talk to the internet, but intra-VPC communication should work. How do you configure that?**
- **What are ECS and EKS, and when would you choose each?**
- **A vendor provides VPN services for company A and their manager wants to view a dashboard but has no AWS account. How would you help them?**
- **Your web application is in India and users abroad are hitting latency. How would you fix that, and which service helps reduce latency?**
- **What is Athena?**
- **What are the different S3 storage classes?**
- **How do you scale EKS? Which metrics do you consider, where do you provide your inputs and how? Explain how you did autoscaling in your project.**

### Round set 4 — CI/CD tooling and SonarQube depth

- **Which tools and services have you used to set up CI/CD?**
- **Do you have experience with CodeDeploy, CodeBuild, and CodePipeline? How would you set up a pipeline using them?**
- **Do you have GitHub Actions experience? To build and test a Java Maven application and produce an artefact, what steps would you include?**
- **Where do you keep the GitHub Actions workflow file, and how do you upload a JAR artefact?**
- **You said you configured SonarQube. What does SonarQube do, and which edition have you used — Community, Developer, Enterprise, or SonarCloud?**
- **How did you integrate SonarQube with Jenkins, and which application language did you scan?**
- **How do you set up quality gates in SonarQube?**
- **What have you done in Jenkins?**
- **Write a `Jenkinsfile` for a Node.js application that builds, pushes a Docker image, and deploys to Kubernetes — and explain it in detail.**

## Example

```text
Persistent Systems — DevOps Engineer, four reported interviews (~59 questions)

  SET 1  K8s + GH Actions + AWS (9 YOE)   13   cluster upgrade, pod vs node
                                               affinity, matrix strategy,
                                               GH Actions caching, lost .pem key,
                                               what makes a subnet private
  SET 2  Azure design + TF scale (13 YOE)   9   HA three-tier on Azure, slow
                                               e-commerce app, Azure Monitor
                                               K8s metrics, 1000-line Terraform
  SET 3  AWS breadth + reasoning (5 YOE)   18   state mv, K8s hierarchy,
                                               no-internet EC2, dashboard for
                                               someone with no AWS account,
                                               cross-region latency, Athena
  SET 4  CI/CD + SonarQube depth            9   CodePipeline trio, Maven in GH
                                               Actions, Sonar edition + quality
                                               gates, write a Jenkinsfile

PERSISTENT ASKS "WHICH EDITION?"
  "Which version of SonarQube — Community, Developer, Enterprise, or
  SonarCloud?" is a verification question. Someone who really configured it
  knows which edition, because branch analysis is a paid feature. Expect that
  style of check on anything you claim.
```

## Interview tips

- The lost-`.pem`-key question has several correct answers and naming the best one first matters. Session Manager is the answer if the SSM Agent is running and the instance has the right role — you get a shell with no key at all. Otherwise: use EC2 Instance Connect, or attach a new key by stopping the instance, detaching the root volume, mounting it on a second instance, appending a new public key to `~/.ssh/authorized_keys`, and reattaching — or simply run a `user_data` script on next boot to add the key. Say that the real lesson is that key-based access is fragile and Session Manager removes the whole problem. See [troubleshooting SSH failures](../linux-administration/how-do-you-troubleshoot-ssh-failures-high-cpu-and-disk-space-on-linux-servers.md).
- "What makes a subnet public or private?" has one precise answer: the **route table**. A subnet is public if its route table sends `0.0.0.0/0` to an internet gateway; private if it does not — typically routing that prefix to a NAT gateway instead, or nowhere at all. It is not about the name, the CIDR, or whether instances have public IPs — though a public IP is also required for inbound reachability. That precision is what the question is testing, and it pairs with the NAT gateway question: the NAT gateway lives in a **public** subnet and serves private ones. See [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md).
- The 1000-line Terraform question in set 2 is the best design question here. The answer is decomposition, not tidying: split one monolithic state into smaller per-component states — network, cluster, data, applications — so each `plan` refreshes far fewer resources; extract reusable versioned modules; separate environments into their own state; and remove data sources that make slow API calls on every run. Then the pipeline levers: `plan` on the pull request and `apply` on merge, cache the provider plugins, and run independent stacks in parallel. Say that state size is almost always the actual cause of slowness, and that a blast-radius benefit comes free with the split. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- `terraform state mv` is asked twice across set 3, so be exact: it renames or moves a resource _within state_ — for example after you rename a resource block or move it into a module — so Terraform recognises the existing infrastructure under its new address instead of planning a destroy and create. Say that it changes nothing in the cloud, and that `moved` blocks in configuration are the modern, reviewable alternative to running the command by hand.
- The vendor-manager-with-no-AWS-account question is a nice access-design problem. The answer is not to create them an IAM user. Options, best first: publish the dashboard through a CloudWatch dashboard sharing link with its own credentials, or embed a QuickSight dashboard for anonymous or externally-authenticated users, or federate their identity through IAM Identity Center or SAML so they authenticate with their own directory and assume a read-only role, or simply export a scheduled report. Say the principle — grant the _view_, not an account — and that whatever you choose must be least-privilege and auditable. See [least-privilege identity in the cloud](../cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md).
- The cross-region latency question wants CloudFront first: cache and terminate connections at the edge so foreign users get a nearby TLS handshake even for dynamic content. Then Global Accelerator for anycast entry into the AWS backbone when the content is not cacheable, then Route 53 latency-based routing with a genuine second region if the data tier can be replicated. Say that the cheapest real win is usually CloudFront plus caching, and that a second region is a data-consistency decision rather than a networking one. See [designing for multi-region resilience](../cloud-engineering/how-do-you-design-for-multi-region-resilience.md) and [managing DNS and global traffic routing](../cloud-engineering/how-do-you-manage-dns-and-global-traffic-routing.md).
- The no-internet EC2 question is straightforward but people over-answer it: give it no public IP, put it in a private subnet whose route table has no internet gateway route, and it can still reach everything inside the VPC through local routing subject to security groups. Then add the practical follow-up — if it needs AWS APIs or patches, use VPC endpoints or an internal mirror rather than opening egress.
- GitHub Actions specifics are asked in three of the four rounds, so know them cold: `strategy.matrix` fans one job out across combinations of values, with `fail-fast` and `max-parallel` to control it — used for testing several language versions or platforms. Caching is `actions/cache` with a key, usually a hash of the lockfile, plus `restore-keys` for partial hits, and the cache is scoped per branch with fallback to the default branch. The workflow file lives in `.github/workflows/`. Uploading a JAR is `actions/upload-artifact`, retrieved later with `download-artifact`. A stale branch is one with no recent commits and no open pull request — dead weight that should be pruned, and often flagged by automation.
- The SonarQube block in set 4 is a verification sequence, so answer with edition-aware detail. Community Edition analyses only the main branch and has no pull-request decoration or branch analysis — those are Developer Edition and above, and SonarCloud is the hosted service. Jenkins integration is the SonarQube Scanner plugin plus a `withSonarQubeEnv` block and a `waitForQualityGate` step so the pipeline actually _fails_ on a gate breach rather than just reporting. Quality gates are conditions on new code — no new blocker issues, coverage above a threshold on new code, duplication below a limit, security hotspots reviewed — and the key operational point is gating on _new_ code rather than the legacy baseline, otherwise no existing project can pass. See [SAST, DAST, IAST, and SCA](../devsecops/what-is-the-difference-between-sast-dast-iast-and-sca.md).
- Pod affinity versus node affinity is easy to blur: node affinity attracts a Pod to nodes with certain labels; Pod affinity and anti-affinity place a Pod relative to _other Pods_ using a `topologyKey`, which is how you keep replicas apart across zones or co-locate a cache with its consumer. Say that `requiredDuringScheduling` is hard and `preferred` is soft, and that topology spread constraints are the modern way to spread replicas. See [controlling which node a Pod runs on](../kubernetes/how-do-you-control-which-node-a-pod-runs-on.md).
- The EKS scaling question asks where you "add your inputs", so be concrete: HPA on the Deployment with a target utilisation, requiring `resources.requests` to be set; metrics-server for CPU and memory, or an adapter plus KEDA for custom and external metrics such as queue depth; and the Cluster Autoscaler or Karpenter adding nodes when Pods cannot be scheduled. Say which metric you actually scaled on in your project and why CPU was or was not the right signal. See [autoscaling workloads and nodes](../kubernetes/how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md).
- The "prerequisites through to output" question in set 3 is asking whether you think in project terms. Structure it: requirements and constraints, then network and identity foundations, then sizing from expected load, then IaC and environment strategy, then CI/CD and observability, then security review and cost estimate, then a runbook and handover. Naming the _non-technical_ prerequisites — budget, ownership, and who is on call — is what makes it sound like experience.
- The Azure three-tier and slow-e-commerce questions in set 2 pair well: design with an Application Gateway or Front Door at the edge, App Service or AKS across availability zones for the application tier, and a zone-redundant managed database with read replicas. For the slowness, work from user-facing symptoms inward — p95 latency by endpoint, then which downstream call owns the time, then database query plans, cache hit rate, and saturation — and say you would look at what changed before tuning anything. See [designing a system to degrade gracefully under overload](../scalability-and-high-availability/how-do-you-design-a-system-to-degrade-gracefully-under-overload.md).
- Athena is serverless SQL over data in S3 using a schema in the Glue catalogue, priced per terabyte scanned — so the answer worth giving includes the cost lever: partition the data and use columnar Parquet, because that is what makes queries cheap. It is also the standard answer for querying VPC Flow Logs and CloudTrail at rest. See [S3 storage classes](../aws-engineering/what-are-the-s3-storage-classes-and-when-do-you-use-each.md).

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
