---
title: "What DevOps interview questions does Emphasis ask?"
id: 331
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - emphasis
  - aws-engineering
  - infrastructure-as-code
  - cicd
  - kubernetes
  - docker
  - network-security
  - serverless-architecture
  - database-management-in-devops
---

# What DevOps interview questions does Emphasis ask?

## Questions

### Round set 1 — fundamentals

The candidate's own framing: the round stayed on basic DevOps and AWS throughout.

- **Explain the components of a three-tier architecture.**
- **Explain the Kubernetes architecture.**
- **How does a private subnet reach the outside world?**
- **What is the difference between a network ACL and a security group?**
- **What is a NAT gateway for?**
- **Explain how to write a Dockerfile.**
- **When you run `docker pull`, where is the image actually fetched from?**
- **How does the pull work when the image lives in a private registry?**
- **What is an Ingress in Kubernetes?**
- **Explain a CI/CD pipeline and its stages.**

### Round set 2 — Terraform, RDS, and Jenkins

**Serverless and Terraform**

- **What is AWS Lambda, and how do you design a serverless application around it?**
- **What is the difference between `terraform plan` and `terraform apply`?**
- **Which AWS resources have you created with Terraform, and how would you promote an RDS read replica to primary using Terraform?**
- **Specifically, which parameter or code change in Terraform makes a read replica become the primary?**

**Architecture**

- **What is a three-tier architecture?**
- **Which components or resources do you need to build a three-tier architecture in Terraform?**
- **If the RDS instance is in a private subnet, how do you access it securely without exposing a public tool such as a MySQL client?**

**CI/CD and Jenkins**

- **Explain the end-to-end CI/CD pipeline in your current project.**
- **Now explain a simple CI/CD pipeline, briefly.**
- **Show me a sample Jenkins pipeline as code.**
- **Would a standalone single-server Jenkins setup work, and what would you need to consider?**
- **What is an application pipeline?**
- **How many ways can a Jenkins pipeline be triggered?**

**Experience**

- **What are your roles and responsibilities on your current project, and can you explain the project end to end?**

## Example

```text
Emphasis — DevOps Engineer, two reported rounds (24 questions)

  SET 1  Fundamentals               10   3-tier, K8s architecture, private
                                         subnet egress, NACL vs SG, NAT
                                         gateway, Dockerfile, docker pull
                                         (public + private), Ingress, CI/CD

  SET 2  Terraform / RDS / Jenkins  14   Lambda + serverless design, plan vs
                                         apply, read-replica promotion (asked
                                         twice), 3-tier in Terraform, private
                                         RDS access, Jenkins x5, project

DIFFICULTY SPLIT
  Round 1 is a definitions round — answer tightly and move on. Round 2 has
  exactly one hard question: promoting an RDS read replica through Terraform.
  That is where the round is decided.
```

## Interview tips

- The read-replica promotion question is asked twice, which means it is the question that matters, and it has a genuinely awkward answer worth knowing precisely. In Terraform you promote a replica by removing the `replicate_source_db` argument from the `aws_db_instance` resource and applying — that detaches it and makes it a standalone primary. The details that earn credit: the operation is irreversible, the instance reboots, and you must have `backup_retention_period` set above zero beforehand or promotion fails. Add the honest caveat that in a real failover you would usually promote through the console or CLI for speed and then reconcile Terraform, because an emergency is not the moment to run an apply. Saying that shows judgement rather than dogma. See [running a highly available database on AWS](../aws-engineering/how-do-you-run-a-highly-available-database-on-aws.md).
- Accessing a private RDS instance without exposing it is the other good question. Name Systems Manager Session Manager with port forwarding as the answer that needs no bastion, no inbound port, and leaves an audit trail — then mention a bastion host or an EC2 Instance Connect Endpoint as alternatives, and IAM database authentication so there is no static password. Say explicitly that you would never give the database a public IP.
- `docker pull` is asked in two steps, so answer both halves properly. By default the client resolves the image name against Docker Hub, requests the manifest, then pulls the layers it does not already have by digest and assembles them. For a private registry, the image name carries the registry host, and you authenticate first — `docker login`, or in Kubernetes an `imagePullSecret` referenced by the Pod or attached to the service account, or IAM-based auth for ECR. Naming `imagePullSecret` is what distinguishes a Kubernetes-aware answer. See [Docker architecture](../docker/explain-docker-architecture.md) and [image versus container](../docker/what-is-the-difference-between-docker-image-and-docker-container.md).
- Round 1 is a definitions round, so discipline matters more than depth: two or three sentences, one differentiator, then stop. On "how does a private subnet reach the outside world", the complete answer is a NAT gateway in a public subnet for IPv4 egress, an egress-only internet gateway for IPv6, or a VPC endpoint if the destination is an AWS service — and note that this is outbound only, which is exactly what "private" means. See [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md).
- `plan` versus `apply` is trivial to state and easy to make impressive: `plan` computes and displays the diff without changing anything, `apply` executes it. Add that you should save the plan to a file and apply _that_ file in CI, so the change reviewed is provably the change applied. That single detail lifts the answer.
- For the three-tier-in-Terraform question, enumerate resources rather than concepts: VPC, public and private subnets across two availability zones, internet gateway, NAT gateway, route tables and associations, security groups per tier, an application load balancer with target group and listener, an auto-scaling group or ECS service, an RDS subnet group and instance, and IAM roles. A structured list is the answer; naming modules and how environments consume them is the bonus. See [what Terraform is](../infrastructure-as-code/what-is-terraform.md).
- The standalone-Jenkins question is inviting you to name the risks: a single controller is a single point of failure, building on the controller starves it of resources, `JENKINS_HOME` needs backup including `secrets/`, plugin upgrades can break pipelines, and there is no horizontal capacity. Say it works fine for a small team and then describe what you would add — agents, backups, Configuration as Code — as it grows. See [Jenkins pipelines](../cicd/what-are-jenkins-pipelines.md).
- Trigger types are a completeness question, so list them all: webhook from the forge, SCM polling, `cron` schedule, upstream job, manual with parameters, remote API call with a token, and pull-request events through multibranch scanning. Then say webhooks are preferred over polling because polling scales badly and adds latency.
- The pipeline is asked three ways — end to end on your project, briefly, and as code. Prepare one pipeline you know well and three lengths of the same answer: a thirty-second version, a two-minute stage-by-stage version, and a `Jenkinsfile` you can write from memory. See [what a CI/CD pipeline is](../cicd/what-is-ci-cd-pipeline.md) and [continuous delivery versus continuous deployment](../cicd/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md).
- For serverless design around Lambda, do not just define Lambda. Describe the architecture — an event source such as API Gateway, S3, or a queue; the function; downstream state in DynamoDB or RDS Proxy; and the constraints that shape the design: cold starts, the execution time limit, concurrency limits, and why you need RDS Proxy if a function talks to a relational database. Those constraints are the real answer.
- NACL versus security group appears in nearly every round in this collection. Keep the four contrasts ready — stateless versus stateful, ordered numbered rules versus an evaluated set, allow-and-deny versus allow-only, subnet versus network interface. See [network segmentation](../network-security/what-is-network-segmentation.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)
- [[How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?]] (`#455`): [How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?](../cicd/how-do-you-trigger-a-pipeline-webhooks-polling-schedules-and-upstream-jobs.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
