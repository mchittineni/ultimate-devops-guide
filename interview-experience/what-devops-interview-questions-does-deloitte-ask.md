---
title: "What DevOps interview questions does Deloitte ask?"
id: 326
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - deloitte
  - aws-engineering
  - kubernetes
  - cicd
  - infrastructure-as-code
  - version-control
  - network-security
  - linux-administration
  - cloud-cost-optimization
---

# What DevOps interview questions does Deloitte ask?

## Questions

### Round set 1 — AWS networking and audit

- **Which node types did you deploy in AWS?**
- **What is the difference between an interface VPC endpoint and a gateway VPC endpoint?**
- **How did you set up ECS backed by EC2 instances?**
- **What are the node group types in Amazon EKS, and which did you use?**
- **What is Route 53, and could it not be used here?**
- **How do you use a third-party registrar's domain — say one bought from GoDaddy — with Route 53?**
- **What is the difference between AWS Config and AWS CloudTrail?**
- **What is the full process for granting a user access to an S3 bucket?**
- **How does VPC peering work?**
- **How does Transit Gateway work, and how did you configure it?**
- **When you attach VPCs to a Transit Gateway, what do you have to update in each VPC's route table?**
- **Do you configure the Transit Gateway attachment with a CIDR range for every VPC?**
- **What is a web application firewall, and what would an "application access firewall" be?**
- **What are VPC Flow Logs, and how do you use them to track which IPs are hitting your VPC?**
- **How do you filter for one specific IP inside a CloudWatch log group?**
- **If those logs are in an S3 bucket instead, how do you find that same IP?**
- **How do you back up AWS services?**
- **Can an AWS backup be driven from a shell script?**
- **Once a backup has run, where do the log files go?**

### Round set 2 — CI/CD and Kubernetes (4 YOE, two rounds)

**Round 1 — technical screening**

- **Explain the CI/CD workflow you follow and the kind of pipeline you use. How do you define and invoke pipelines in Jenkins?**
- **What are Jenkins shared libraries, how are they written, and how are they declared?**
- **What kinds of application do you deploy through Jenkins, and with which deployment tools?**
- **The Jenkins pipeline runs but no build happens. What could cause that?**
- **What is a webhook for, and how is it used in a CI/CD pipeline?**
- **How do you create and manage Kubernetes clusters — with Terraform, for instance — and what do the control-plane and worker nodes each do?**
- **Which Kubernetes errors have you hit — `CrashLoopBackOff`, `ImagePullBackOff` — and how did you resolve them?**
- **What is the command to get a shell inside a Pod, and how do you define a Kubernetes object?**
- **Explain the folder structure of a Helm chart, and which commands you use to deploy with Helm.**
- **What are the stages of a Docker image build, and why do `ENTRYPOINT` and `CMD` both exist?**
- **How do you manage and connect to services such as databases, EC2, EKS, or ECS — including the command to connect to ECS?**
- **Which container registry do you store images in?**

**Round 2 — in-depth technical screening**

- **What branching strategy do you follow, how do you keep merges from breaking the release branch, and what is your approach when a bug reaches production?**
- **Describe your deployment flow and the stages in your Jenkins pipeline, and how you enforce full quality checks during deployment.**
- **How do you use Jenkins shared libraries — their structure, and how they are wired into your `Jenkinsfile`s?**
- **Which security scanning tools do you know? How do you scan Docker images both at build time and in the registry?**
- **How do you pass environment variables into a `docker build`, and where do you store the resulting images?**
- **How do you establish database connections in your deployments and infrastructure?**
- **How do you handle EKS cluster authentication, and how do you store secrets securely?**
- **How do you create Lambda functions and manage their deployment artefacts — what options do you use to push the artefact?**
- **What is signing in this context — email signing and Helm chart signing — and which tools sign Helm charts?**

### Round set 3 — breadth round (5 YOE)

- **How do you migrate a Git repository between hosts — GitHub to GitLab — while preserving full commit history? What are the steps?**
- **What is the difference between `git fetch` and `git pull`, and when do you use each?**
- **What is `git cherry-pick` and how do you use it?**
- **How do you handle merge conflicts, and when resolving one, do you inspect commit history on the source branch or the target?**
- **Which CI/CD tools do you use?**
- **Given a fresh Jenkins installation, how do you connect it to GitHub? How many ways are there, and is webhook-based communication achievable out of the box or does something else need doing first?**
- **What kinds of stage appear in a pipeline?**
- **Can more than two stages run at the same time?**
- **Have you written Groovy from scratch? What is a declarative pipeline, and how does it differ from a scripted one?**
- **What is the difference between EKS and ECS?**
- **What are the prerequisites for standing up an EKS cluster with two worker nodes and some number of Pods?**
- **With two or more Pods running, how do you handle load balancing — and are you certain an ALB is the right choice?**
- **When do you use an ALB and when an NLB?**
- **You have a Dockerfile for a Tomcat application listening on 8080. You must build it and run a container that exposes port 9090. How do you do that?**
- **What are Helm charts for?**
- **What have you done on Linux, and what kinds of installation have you performed?**
- **Which command returns the number of CPU cores?**
- **What is a cron job and how is it used?**
- **Given a directory tree, how do you find the size of one particular file?**
- **Have you worked on Ansible automation?**
- **What have you done with Terraform on AWS?**
- **What is the difference between Terraform and CloudFormation?**
- **Given an empty AWS account, if I ask you to create a VPC and everything needed to expose a service running on EC2 to the internet, which services come into play?**
- **What is Transit Gateway?**
- **Explain the high-level architecture of Kubernetes.**
- **What have you done with monitoring solutions?**
- **What are the top five technologies you are strongest in?**

### Round set 4 — cost and cluster operations (4 YOE)

- **The web application is unreachable but the EC2 instance is healthy. What are the major causes?**
- **What measures would you take to cut infrastructure cost by 20%?**
- **Have you written automation specifically for cost optimisation?**
- **Write a Terraform configuration for an EC2 instance with an EBS volume attached.**
- **What is your Terraform file structure for a VPC and for EKS?**
- **What do `terraform init` and `terraform refresh` do?**
- **How do you achieve zero downtime during an EKS cluster upgrade?**
- **I want a count of running EC2 instances and attached EBS volumes across 50 to 60 AWS accounts, without logging into each one. How?**
- **How do you integrate SonarQube into your pipeline?**
- **What is the biggest issue you have resolved in Kubernetes?**

## Example

```text
Deloitte — DevOps Engineer, four reported interviews (~70 questions)

  SET 1  AWS networking + audit        19   VPC endpoints, peering, TGW routing,
                                            Route 53 + external registrar,
                                            Config vs CloudTrail, Flow Logs,
                                            backups
  SET 2  CI/CD + Kubernetes (4 YOE)    21   Jenkins pipelines and shared libs,
                                            webhooks, Helm layout, image
                                            scanning, EKS auth, chart signing
  SET 3  Breadth (5 YOE)               27   Git migration, cherry-pick, Jenkins
                                            to GitHub, EKS vs ECS, port
                                            remapping, Linux, Terraform vs CFN
  SET 4  Cost + cluster ops (4 YOE)    10   cut cost 20%, EKS zero-downtime
                                            upgrade, 50-account inventory

DELOITTE'S SIGNATURE
  AWS networking depth — Transit Gateway route tables, interface vs gateway
  endpoints, cross-account inventory. Consulting work means many accounts and
  many VPCs, and the questions reflect that.
```

## Interview tips

- The Transit Gateway route-table pair is the sharpest question in set 1. Attaching a VPC is not enough: each VPC's own route table needs a route for the remote CIDRs pointing at the TGW attachment, and the TGW route table needs to associate and propagate those attachments. On the CIDR follow-up, say no — the attachment is made to subnets, not configured with a CIDR range; the CIDRs appear as routes. See [structuring a multi-account AWS organisation](../aws-engineering/how-do-you-structure-a-multi-account-aws-organisation.md).
- Interface versus gateway endpoints has a short factual answer: gateway endpoints exist only for S3 and DynamoDB, are free, and work through route-table entries; interface endpoints are PrivateLink ENIs in your subnets, cost money per hour and per gigabyte, and work for almost every other service. Naming the two-service limit is what proves you know it. See [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md).
- AWS Config versus CloudTrail is asked because they are easy to conflate. CloudTrail records _who called which API and when_; Config records _what a resource's configuration looked like over time_ and whether it complies with rules. One is an audit log of actions, the other a history of state. See [how AWS IAM evaluates a request](../aws-engineering/how-does-aws-iam-evaluate-a-request.md).
- The 50-to-60-account inventory question wants a specific service: AWS Config aggregators or Resource Explorer across the organisation, or Systems Manager Inventory, queried centrally — not a script that assumes a role into each account in a loop. Mention the scripted approach as the fallback and the aggregator as the right answer.
- The port-remapping Dockerfile question is checking that you know `EXPOSE` is documentation only. The container keeps listening on 8080; you publish it with `docker run -p 9090:8080`, and the first number is the host port. If they want the application itself on 9090, that is a configuration change inside Tomcat, not a Docker flag. Say which interpretation you are answering. See [what a Dockerfile is](../docker/what-is-dockerfile.md).
- "Pipeline runs but no build happens" is a diagnostic question with a short list: the wrong branch or an empty changeset, a `when` condition skipping the stage, the agent label matching nothing so it queues forever, a webhook firing without triggering the job, the checkout succeeding on a stale commit, or the build step silently swallowing a failure. Say you would read the console log first. See [Jenkins pipelines](../cicd/what-are-jenkins-pipelines.md).
- For the Git host migration, give the mirror-clone answer: `git clone --mirror`, then `git push --mirror` to the new remote, which carries every branch, tag, and note. Add that pull requests, issues, and CI configuration do _not_ migrate that way and need the platform's own importer. That caveat is the mark of experience. See [what Git is](../version-control/what-is-git.md).
- On the merge-conflict follow-up about where to check history, the answer is both, but the useful framing is that you inspect the commits on the incoming branch to understand intent and the target branch to see what you would be overwriting — `git log --merge` and `git log -p <file>` are the tools. See [handling merge conflicts](../version-control/how-to-handle-merge-conflicts-in-git.md).
- "Are you sure you'll be using an ALB?" is a deliberate challenge. Hold your position with a reason or change it with a reason: an ALB for HTTP path and host routing, an NLB for TCP, static IPs, or very high throughput, and inside Kubernetes the Service or Ingress is what actually load-balances across Pods while the cloud load balancer only reaches the nodes. See [layer 4 versus layer 7 load balancers](../scalability-and-high-availability/what-is-the-difference-between-a-layer-4-and-a-layer-7-load-balancer.md) and [exposing an application in Kubernetes](../kubernetes/how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md).
- The 20% cost reduction question wants a prioritised plan, not a list: find the top spend lines first, then right-size and switch to Graviton, buy Savings Plans for steady baseline, move interruptible work to Spot, apply S3 lifecycle rules, delete unattached EBS volumes and idle load balancers, and cut log retention. Say you would measure before and after. See [cloud cost optimisation](../cloud-cost-optimization/what-is-cloud-cost-optimization.md).
- Helm chart signing is niche enough that naming the mechanism wins the point: `helm package --sign` with a GPG key produces a `.prov` provenance file, verified with `helm verify` or `helm install --verify`. Mention Cosign and Sigstore for OCI-based charts and images as the modern equivalent. See [signing and verifying container images](../devsecops/how-do-you-sign-and-verify-container-images.md) and [SLSA and securing the software supply chain](../devsecops/what-is-slsa-and-how-do-you-secure-the-software-supply-chain.md).
- Terraform versus CloudFormation should end in a trade-off rather than a preference: CloudFormation is AWS-native with no state file to manage and native drift detection and rollback; Terraform is multi-cloud with a richer module ecosystem but state you must host and protect. See [when to choose CloudFormation, CDK, or Terraform on AWS](../aws-engineering/when-do-you-choose-cloudformation-cdk-or-terraform-on-aws.md).
- For "app unreachable but EC2 is fine", the causes are the same as any 503 chain: the process is not listening, the security group or NACL blocks the port, the target group health check fails, DNS points elsewhere, or the certificate expired. Say you would `curl localhost` on the instance first to split application from network. See [what happens when a user opens your application in a browser](../network-security/what-happens-when-a-user-opens-your-application-in-a-browser.md).
- Small Linux answers worth having exact: `nproc` (or `lscpu`) for core count, `du -h <file>` or `ls -lh` for one file's size, and `crontab -e` with the five-field schedule for cron. See [basic Linux commands](../linux-administration/what-are-the-basic-linux-commands-every-devops-engineer-should-know.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?]] (`#402`): [How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?](../cicd/how-do-you-troubleshoot-a-jenkins-pipeline-that-never-starts-or-hangs-in-the-queue.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
