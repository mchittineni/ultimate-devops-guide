---
title: "What DevOps interview questions does Flentas ask?"
id: 335
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - flentas
  - kubernetes
  - infrastructure-as-code
  - aws-engineering
  - cloud-cost-optimization
  - database-management-in-devops
  - docker
  - container-orchestration-advanced
---

# What DevOps interview questions does Flentas ask?

## Questions

**Your architecture, challenged**

- **What is the architecture of your current project?**
- **Which applications run in the frontend and which in the backend?**
- **Why did you deploy the frontend on EKS rather than on S3 with CloudFront?**
- **What did you implement with Lambda and API Gateway?**

**Kubernetes concepts and capacity**

- **What is a namespace in EKS, and how many do you currently run?**
- **What is a node group?**
- **A node cannot join the cluster. What could be the reason?**
- **What is the difference between the control plane and the data plane?**
- **What is the difference between a Pod and a container?**
- **What are requests and limits in Kubernetes?**
- **A node has 8 vCPU and 32 GB RAM. Pod autoscaling goes up to 4 replicas, each Pod has limits of 4 vCPU and 16 GB and requests of 2 vCPU and 10 GB. How many Pod instances will actually run?**
- **How do you enable autoscaling for a traffic surge — scaling both cluster nodes and Pods?**
- **Can you use the Cluster Autoscaler for that?**
- **When do you use the Vertical Pod Autoscaler?**
- **How do you scale EC2 instances?**
- **Have you upgraded an EKS cluster?**

**Databases, caching, and cost**

- **How do you perform cost optimisation on ECS, RDS, and ElastiCache?**
- **Why did you use RDS Proxy?**
- **The client application had no connection pooling. How did you handle that?**
- **What is the difference between Redis and Memcached?**

**Terraform**

- **Explain your Terraform folder structure.**
- **What is the difference between Terraform and Terragrunt?**
- **What is the state file?**
- **How do you handle resource dependencies in Terraform?**
- **When you ran `terraform apply`, did you ever get unexpected changes?**
- **If something goes wrong in Terraform, how do you roll the change back?**
- **You created a load balancer with Terraform and it has since been updated. Now you want to delete only that load balancer. How?**
- **How do you handle secrets in Terraform?**
- **How do you pass secrets from AWS Secrets Manager into the pipeline?**
- **Do you commit the `tfvars` file to Git? Those parameters have to be supplied when the pipeline runs — how do you manage that in Jenkins?**

**Containers**

- **What is Docker?**
- **What is the difference between an image and a container?**
- **What is a Helm chart?**

## Example

```text
Flentas — DevOps Engineer (3.5 YOE), reported round
34 questions

  Terraform                  10   folder structure, Terragrunt, state,
                                  dependencies, unexpected diffs, rollback,
                                  targeted destroy, secrets, tfvars in Jenkins
  Kubernetes + capacity      12   namespaces, node groups, node won't join,
                                  control vs data plane, requests/limits,
                                  the 8 vCPU / 32 GB packing puzzle, HPA +
                                  Cluster Autoscaler + VPA, EKS upgrade
  DB / cache / cost           4   ECS+RDS+ElastiCache cost, RDS Proxy,
                                  no connection pooling, Redis vs Memcached
  Your architecture           4   project architecture, front/back split,
                                  "why not S3+CloudFront", Lambda + API GW
  Containers                  3   Docker, image vs container, Helm chart

THE QUESTION THAT DECIDES THE ROUND
  The scheduling arithmetic. It is the only question with a single correct
  numeric answer, and it separates people who know that the SCHEDULER USES
  REQUESTS from people who think it uses limits.
```

```text
THE PACKING PUZZLE — worked through

  Node capacity:      8 vCPU, 32 GB
  Allocatable:        LESS than that — kubelet, kube-proxy, CNI, and OS
                      reservations take a slice (on EKS, roughly 0.5 vCPU
                      and a few GB), so assume ~7.5 vCPU / ~28 GB usable.

  Scheduling uses REQUESTS, not limits:
      per pod requests = 2 vCPU, 10 GB
      by CPU:     7.5 / 2  = 3 pods
      by memory:  28  / 10 = 2 pods   <-- binding constraint

  ANSWER: 2 pods fit on that one node. The HPA will try for 4 replicas;
  the remaining 2 sit Pending until the Cluster Autoscaler adds nodes.

  Why limits don't decide placement: limits (4 vCPU / 16 GB) cap RUNTIME
  usage and set the QoS class. Requests are the reservation the scheduler
  subtracts from allocatable capacity.
```

## Interview tips

- Work the arithmetic out loud on the packing question and name the binding constraint. The key facts, in order: the scheduler sums **requests** against **allocatable** capacity; allocatable is less than the node's nominal capacity because of kubelet and system reservations; memory is the limiting dimension at 10 GB per Pod; and the Pods that do not fit go `Pending` rather than failing. Finishing with "and the Cluster Autoscaler is what turns two into four" ties it to the autoscaling questions that follow. See [autoscaling workloads and nodes](../kubernetes/how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md).
- "Why not S3 and CloudFront for the frontend?" is a challenge to your design, and the wrong move is to concede immediately. Give the legitimate reasons a frontend lives on EKS — server-side rendering, a Node process rather than static files, shared ingress and TLS with the backend, one deployment pipeline and one set of network controls — and then acknowledge that if it were genuinely static, S3 with CloudFront would be cheaper and faster. Showing you know the trade-off is what is being tested, not defending EKS at all costs.
- Targeted deletion of the load balancer has two answers and you should distinguish them. `terraform destroy -target=aws_lb.this` removes just that resource, but flag it as a blunt tool HashiCorp warns about because dependent resources drift out of sync. The cleaner path is to remove the resource block from the configuration and apply, so the dependency graph is respected — and if you want to keep the load balancer but stop managing it, `terraform state rm` is the right command instead. Naming all three distinctions is a strong answer.
- The `tfvars` question wants a policy, not a mechanism: commit non-sensitive per-environment `tfvars`, never commit secrets, and in Jenkins supply the sensitive values through `withCredentials` as environment variables Terraform reads as `TF_VAR_*`, or better, have Terraform fetch them at runtime from Secrets Manager via a data source so nothing is passed at all. Add that a secret retrieved with a data source still lands in the state file in plain text, which is why state must be encrypted — that detail wins the question. See [managing secrets in CI/CD pipelines](../devsecops/how-do-you-manage-secrets-in-ci-cd-pipelines.md).
- Terraform rollback is a trap for anyone expecting an undo command. There is none: you roll forward by reverting the commit and applying, restore from a previous state version if state was corrupted, or `terraform import` back anything destroyed. Say that this is exactly why plans are reviewed and why `prevent_destroy` exists on critical resources. See [recovering a lost or corrupted Terraform state file](../infrastructure-as-code/how-do-you-recover-a-lost-or-corrupted-terraform-state-file.md).
- RDS Proxy plus the "no connection pooling" question are one story, so answer them together. A Lambda or a Pod that scales horizontally opens a connection per instance and exhausts the database's `max_connections`; RDS Proxy sits in front and multiplexes those into a small pool, and it also shortens failover time and lets you authenticate via IAM. That is the answer to how you handled a client with no pooling — you put the pool outside the application. See [running a highly available database on AWS](../aws-engineering/how-do-you-run-a-highly-available-database-on-aws.md).
- Redis versus Memcached should end in a recommendation: Memcached is a simple multi-threaded key-value cache with no persistence and no data structures; Redis has lists, sets, sorted sets, streams, persistence, replication, pub/sub, and cluster mode. Say you default to Redis unless you specifically want the simplicity and raw multi-threaded throughput of Memcached for a pure cache.
- Three autoscalers appear in this round and interviewers want the boundaries clear: HPA adds Pod replicas, VPA adjusts a Pod's requests and limits and generally requires a restart to apply, and the Cluster Autoscaler (or Karpenter) adds nodes when Pods cannot be scheduled. Add the warning that HPA and VPA on the same metric for the same workload conflict, and that VPA suits workloads you cannot scale horizontally.
- A node failing to join has a short and well-known list: the kubelet cannot reach the API endpoint, IAM role or `aws-auth`/access-entry mapping is missing, the security group blocks control-plane-to-node traffic, no route or NAT for pulling the bootstrap image, the wrong cluster name in the bootstrap script, a full subnet with no free IPs, or a version skew between node AMI and control plane. Say you would read the kubelet logs on the node first.
- Terraform versus Terragrunt is really about what Terraform does not give you: Terragrunt is a wrapper adding DRY backend and provider configuration, dependency ordering across separate state files, and `run-all` across many modules. Mention that native features such as stacks and workspaces have reduced the need, and that adding Terragrunt is a real complexity cost.
- Pod versus container is short but easy to answer weakly: a Pod is the smallest schedulable unit and may hold several containers that share a network namespace, IP, and volumes — which is why sidecars work. Containers are the processes inside it. See [what a Pod is](../kubernetes/what-is-a-pod-in-kubernetes.md).
- For dependencies, say Terraform infers them from references and builds a DAG, `depends_on` is for the cases with no reference, and being explicit about ordering usually means the design could be improved. See [what Terraform is](../infrastructure-as-code/what-is-terraform.md).
- "Did you get unexpected changes on apply?" is an invitation to talk about drift honestly. Name a real cause — a console edit, a provider upgrade changing a default, an auto-generated tag, or a field the API normalises — and say how you handled it with `ignore_changes` or by importing reality into state. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
