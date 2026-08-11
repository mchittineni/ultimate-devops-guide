---
title: "What DevOps interview questions does SquareOps ask?"
id: 381
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - squareops
  - kubernetes
  - aws-engineering
  - container-orchestration-advanced
  - infrastructure-as-code
  - cicd
  - network-security
  - cloud-cost-optimization
  - database-management-in-devops
---

# What DevOps interview questions does SquareOps ask?

## Questions

This is the most systematically drilled interview in the collection. The submitter recorded each main question together with the follow-ups the interviewer used to probe it, so the follow-ups are preserved as sub-bullets — they are where the round is actually decided.

### Round 1 — architecture, EKS, Helm, storage, and delivery

**Infrastructure and architecture**

- **Explain the infrastructure and application setup of your last project — how is the application hosted?**
  - Where exactly is the frontend hosted, where is the backend hosted, and where is the database?
  - Is everything on AWS, or is it multi-cloud?
  - Which part of the infrastructure do you personally manage?
  - What do the microservices do, and why did you choose this architecture?

**AWS responsibilities**

- **What exactly do you do in AWS on this project?**
  - Do you manage VPCs, subnets, and security groups?
  - Do you create EC2, EKS, or ECS resources?
  - Do you manage S3 lifecycle policies?
  - Do you handle IAM and Kubernetes RBAC?
  - Do you take part in cost optimisation?
- **Which compute platform are the applications hosted on?** The expected answer was EKS.
  - Why EKS over ECS?
  - How do you manage the worker nodes?
  - How many replicas do you run?
  - Do you use the Cluster Autoscaler or Karpenter?

**EKS and Kubernetes access**

- **Have you created an EKS cluster? Explain the process.**
  - Did you use the console, the CLI, or Terraform?
  - Which VPC and subnet configuration did you use?
  - How did you configure the node groups?
  - How do you bootstrap `kubectl` access?
- **Have you upgraded an EKS cluster before? How?**
  - What risks come with upgrading?
  - How do you handle node draining?
  - Do deployments get recreated?
  - What checks do you perform after the upgrade?
- **A teammate also needs `kubectl` access to the same cluster. What steps do you follow?**
  - Which IAM policy do you attach?
  - What is the `aws-auth` ConfigMap, and where is it stored?
  - How do you map users and roles?
  - Do you give them a RoleBinding or a ClusterRoleBinding?
- **In which Kubernetes resource do you map IAM users and roles?** The expected answer was the `aws-auth` ConfigMap.
  - Which sections does it contain? (`mapUsers`, `mapRoles`)
  - What mistakes can break authentication?

**Helm and application deployment**

- **Have you worked with Helm and Helm charts?**
  - Why use Helm instead of plain YAML?
  - Show the folder structure of a Helm chart.
  - What is the `templates` folder, and what is `values.yaml` used for?
  - How do you manage multiple environments?
- **How do you securely inject sensitive data into Helm?**
  - Do you use AWS Secrets Manager?
  - Do you avoid committing secrets in `values.yaml`?
  - What are Sealed Secrets?
  - What are the `--set` and `--set-file` flags for?
- **Can a public Helm chart be customised?**
  - Why is editing the chart directly not recommended?
  - How do you update configuration safely?
  - What happens during chart upgrades?
  - How do you extend a chart with new templates?
- **How do you add extra Kubernetes manifests to a public Helm chart?**
  - Where do you put the extra YAML files?
  - How do you reference new values?
  - Can this break the original chart?

**Kubernetes storage**

- **How do you implement shared storage across multiple Pods running on multiple nodes in EKS?**
  - Why EFS over EBS?
  - What is the EFS CSI driver?
  - What are the access modes?
  - How do you mount the PVC in a Deployment?
- **If there is one node but multiple Pods, can you use EBS for shared storage?**
  - Which access mode does EBS support?
  - Why can EBS not work across multiple nodes?
  - When is EFS mandatory?
- **Why choose EFS over EBS — which supports multi-node, which is cheaper, and which is faster?**
- **Can EBS be attached to multiple nodes, and why not?**
  - Explain ReadWriteOnce versus ReadWriteMany.
  - Who enforces the mount restriction?

**Kubernetes reliability and troubleshooting**

- **What is a PodDisruptionBudget?**
  - What is a voluntary disruption, and what is an involuntary one?
  - When do you use `minAvailable` versus `maxUnavailable`?
- **What is your approach to debugging a `CrashLoopBackOff`?**
  - Which logs do you check, and how do you check events?
  - How do you inspect the liveness and readiness probes?
  - How do you check resource limits?
  - How do you inspect environment variables and ConfigMaps?
- **During peak traffic the ingress controller is routing requests slowly. How do you debug it?**
  - Do you check the ingress controller logs, and its CPU and memory usage?
  - Do you check Pod replicas, and do you use an HPA?
  - Could it be load balancer throttling, or endpoint misconfiguration?
  - Are readiness probes failing, and is target response latency high?
- **Should you increase ingress controller replicas permanently or dynamically?**
  - Why is static scaling bad?
  - When do you use an HPA, and when the Cluster Autoscaler?

**CI/CD and Terraform**

- **Which CI/CD tools have you worked with?**
  - Explain your GitHub Actions pipeline.
  - How do you run iOS build automation?
  - How do you handle secrets in pipelines?
  - How do you deploy to EKS through GitHub Actions?
- **How do you handle multi-environment pipelines — dev to QA to production?**
  - What is the promotion strategy, and are there manual approvals?
  - What is your Git branching strategy?
- **How do you implement rolling deployments?**
  - What happens to the old Pods?
  - What are `maxSurge` and `maxUnavailable`?
- **Have you used Terraform?**
  - Show the module structure and the provider file.
  - How do you manage a remote backend, and how do you manage state locking?
  - What is a `data` block, and what is a `module` block?

### Round 2 — AWS hands-on, networking maths, and Terraform

**AWS breadth**

- **Which AWS services do you have the most hands-on experience with — EC2, IAM, VPC, S3, RDS, CloudWatch? Are you confident in these, and have you worked on cost optimisation?**

**IAM and policies**

- **Create an EC2 IAM role that allows access only to S3 and DynamoDB and denies access to every other service.**
  - What is the logic behind a custom policy?
  - What is an explicit deny?
  - How would you restrict everything except two services?
  - Which policy pattern do you use — `Allow` plus a `Deny` with `NotAction`?

**Cost optimisation**

- **What exact cost optimisation steps have you implemented?**
  - What was the percentage saving?
  - Have you used Reserved Instances or Savings Plans?
  - Do you know the cost difference between a public and a private ALB, and which scenario costs more?

**ALB cross-communication**

- **Two applications sit in the same VPC, each behind its own public ALB. If App A calls App B, how does the traffic flow?**
  - Does it go out to the internet, and does it come back through the internet gateway?
  - Which is costlier — a public or a private ALB?
  - What stays inside the VPC and what leaves it?

**Auto scaling on memory and disk**

- **How do you create auto-scaling policies based on memory and disk usage?**
  - Are memory and disk metrics available by default?
  - Why do you need the CloudWatch agent, and how do you configure it?
  - Where do you create the CloudWatch alarms?
  - Do you need to update the launch template?

**S3 lifecycle and versioning**

- **In a versioned bucket, how do you delete objects and all their older versions after 10 days?**
  - Which options appear in a lifecycle rule?
  - Do you explicitly delete previous versions?
  - What is the difference between current and previous versions?

**RDS troubleshooting**

- **The application is slow and you suspect RDS. What do you check?**
  - CPU, memory, latency, IOPS, connections, disk queue depth?
  - Slow query logs, error logs, Performance Insights?
- **You found memory pressure on RDS and cannot resize it. What immediate action can you take with no downtime?**
  - Can you kill heavy queries, or remove idle connections?
  - Can you create a read replica?
  - Which action applies instantly, and which causes zero downtime?

**VPC, NACLs, and CIDR maths**

- **A request arrives from the internet and enters the VPC through the internet gateway. Which security layer evaluates it first — the NACL or the security group?**
  - Why the NACL first?
  - Which is stateless and which is stateful?
  - Which takes precedence if they conflict?
- **If a NACL denies a CIDR but a security group allows the same IP, can that IP reach the load balancer?**
  - Why not, and which one checks traffic first?
- **Does the address `10.11.7.44` fall within `10.11.0.0/16`?**
- **Does the address `10.11.44.76` fall within `10.1.0.0/16`?**
- **What does a `/32` prefix represent — how many addresses does it cover, and which exact address? How do you calculate whether an IP is inside a CIDR block?**

**CI/CD branch triggers and rollback**

- **The repository has three branches — dev, staging, and prod. How do you ensure that pushing to staging triggers only the staging deployment?**
  - Separate pipelines or a single pipeline?
  - Branch conditions, environment variables, webhooks?
  - Should the pipeline constantly poll the repository?
  - Which type of Jenkins job is best for this?
- **Have you ever set up rollback in CI/CD?**
  - How do you implement automatic rollback, and what triggers it?
  - Is rollback handled by the CI/CD system or by Kubernetes?
- **Have you integrated SonarQube into your pipeline?**
  - How do you get a Sonar token, and where do you store it?
  - How do you insert the scanner stage?
  - What is a quality gate?
- **A Jenkins job starts but gets stuck. How do you debug it?**
  - Console logs, node resources, agent logs, external API calls?
  - When do you restart the agent?

**Terraform advanced**

- **Terraform generated an RDS password and you did not save it. Can you retrieve it?**
  - Where does Terraform store generated values?
  - Local state or remote backend?
  - Why is storing secrets in plain text dangerous?
- **What is a custom Terraform module, and what does a module contain?**
- **What goes in `main.tf`, `variables.tf`, `outputs.tf`, and `providers.tf`, and how do you call a module from the root module?**

## Example

```text
SquareOps — DevOps Engineer, two reported rounds
43 main questions with ~225 recorded follow-ups

  ROUND 1                                   23 main questions
    Infrastructure and AWS scope       3    hosting, your actual AWS duties,
                                            compute platform (EKS expected)
    EKS and cluster access             4    create, upgrade, give a teammate
                                            kubectl, aws-auth ConfigMap
    Helm                               4    charts, secrets into Helm,
                                            customising a public chart,
                                            adding extra manifests
    Kubernetes storage                 4    shared storage across nodes,
                                            EBS for one node, EFS vs EBS,
                                            why EBS is single-node
    Reliability and troubleshooting    4    PDB, CrashLoopBackOff, slow ingress
                                            under peak load, static vs dynamic
                                            ingress scaling
    CI/CD and Terraform                4    tools + GH Actions to EKS,
                                            multi-env promotion, rolling
                                            deployments, Terraform structure

  ROUND 2                                   20 main questions
    IAM / cost / ALB                   4    allow-only-two-services policy,
                                            real cost savings, public ALB
                                            cross-talk path
    Scaling / S3 / RDS                 4    memory + disk autoscaling,
                                            versioned-bucket expiry, RDS
                                            slowness, memory pressure with
                                            no resize
    Networking + CIDR maths            5    NACL before SG, deny vs allow
                                            conflict, two IP-in-CIDR
                                            calculations, /32
    CI/CD + Terraform                  7    branch-specific triggers,
                                            rollback ownership, SonarQube,
                                            stuck Jenkins job, lost RDS
                                            password, module anatomy

WHAT MAKES THIS ROUND DIFFERENT
  Roughly five follow-ups per main question. The interviewer does not accept
  a headline answer — every claim gets pushed until it either holds up or
  breaks. Depth is the only thing being measured here.
```

## Interview tips

- The lost-RDS-password question is the best in the round because it exposes something people prefer not to say out loud: **yes, you can retrieve it — it is in the state file in plain text.** `terraform output` if it is declared as an output, or `terraform state show` on the resource, or by reading the state JSON directly. Then give the consequence, which is the real answer: any generated password, `random_password` value, or secret read through a data source is stored unencrypted in state — so state must live in an encrypted, versioned, access-controlled backend, and anyone with read access to that bucket has every secret in it. Say the better pattern: have RDS manage the password itself (`manage_master_user_password`), or generate it into Secrets Manager and have the application read it from there, so Terraform never holds the value. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- The public-ALB cross-communication question is a cost trap and the answer is worth being precise about. App A resolves App B's ALB DNS name, which returns **public** addresses — so the traffic leaves the VPC through the internet gateway, reaches the ALB's public interface, and comes back in to App B's targets. So yes, it egresses; it is billed as data processing and, in cross-AZ or NAT paths, as data transfer; and it is slower and less secure than it needs to be. The fix is an internal ALB, or split-horizon DNS resolving the same hostname to a private address inside the VPC, or PrivateLink for service-to-service. On the "which costs more" follow-up: the ALB hourly and LCU pricing is the same, but a public ALB path adds data-transfer and NAT charges that an internal one avoids — so the public route costs more in practice. See [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md).
- The NACL-versus-security-group ordering question has a definite answer: for **inbound** traffic the NACL is evaluated first, because it operates at the subnet boundary and the packet must enter the subnet before it reaches the ENI where the security group applies. Then answer the conflict follow-up decisively: if the NACL denies the CIDR, the security group's allow is irrelevant — the packet never arrives, so the IP **cannot** reach the load balancer. Say that NACLs are stateless (so return traffic needs an explicit rule, which is why ephemeral port ranges matter) while security groups are stateful, and that there is no "precedence" in the usual sense — both must permit the traffic, and a deny at either layer wins. See [network segmentation](../network-security/what-is-network-segmentation.md).
- The two CIDR calculations are pass-or-fail arithmetic, so get them right and show the working. `10.11.0.0/16` fixes the first two octets, so the range is `10.11.0.0` to `10.11.255.255` — therefore `10.11.7.44` **is** inside it. `10.1.0.0/16` covers `10.1.0.0` to `10.1.255.255` — therefore `10.11.44.76` is **not** inside it, because the second octet is 11, not 1. State the method rather than just the verdict: a `/16` fixes 16 bits, which is the first two octets, so compare octet by octet. And `/32` is a single host address — one IP, all 32 bits fixed — which is why you write `x.x.x.x/32` in a security group rule to allow exactly one host.
- The allow-only-S3-and-DynamoDB policy question is asking for a specific pattern, and the follow-up names it. The clean answer is a single statement with `"Effect": "Deny"`, `"NotAction": ["s3:*", "dynamodb:*"]`, and `"Resource": "*"` — which denies everything except those two services — attached alongside the allows for S3 and DynamoDB. Explain why: an explicit deny always wins and cannot be overridden, so `NotAction` with `Deny` is how you express "everything except". Say that the alternative — only granting the two allows and relying on the implicit deny — is usually sufficient and simpler, and that you would use the `NotAction` deny when you need a guardrail that survives someone attaching another policy later. Naming both and saying when each applies is the complete answer. See [how AWS IAM evaluates a request](../aws-engineering/how-does-aws-iam-evaluate-a-request.md).
- The memory-and-disk autoscaling question has a gap the follow-ups are hunting for: **neither memory nor disk is a default CloudWatch metric**, because both are guest-OS level and EC2 only reports what the hypervisor can see. So you install and configure the CloudWatch agent — with its JSON config specifying `mem_used_percent` and `disk_used_percent`, stored in Parameter Store so instances pull it at boot — publish those as custom metrics, then create alarms on them and attach a step or target-tracking scaling policy to the ASG. And yes, the launch template needs updating so new instances install and start the agent via `user_data` or a baked AMI, and the instance role needs `cloudwatch:PutMetricData`. Naming the agent unprompted is the whole point of the question.
- The RDS memory-pressure question asks specifically which action is instant and which is zero-downtime, so answer in that frame. Instant and zero-downtime: terminate the heavy queries (`pg_terminate_backend` or `KILL`), drop idle and idle-in-transaction connections, and reduce the connection ceiling at the pooler rather than the database. Zero-downtime but not instant: add a read replica and shift read traffic to it, which takes minutes to build. Not zero-downtime: changing the instance class or most parameter-group values requiring a reboot. Say that a connection pooler such as RDS Proxy or PgBouncer is the durable fix, because memory pressure on RDS is very often connection-count driven rather than data driven. See [running a highly available database on AWS](../aws-engineering/how-do-you-run-a-highly-available-database-on-aws.md).
- The EBS-across-nodes questions are asked three times in different forms, so have one crisp answer: EBS is a zonal block device attached to a single instance, so it supports `ReadWriteOnce` — meaning read-write by a single **node**, not a single Pod. Several Pods _can_ share it if they are scheduled on that same node, which answers the one-node follow-up: yes, that works. Across nodes it cannot, because the block device is attached to one instance at a time, and the restriction is enforced by the **cloud provider's attachment API** via the CSI driver, not by Kubernetes. EFS is mandatory whenever you need `ReadWriteMany` across nodes or zones — at higher latency and cost, though it is elastic and needs no capacity planning. Mention `ReadWriteOncePod` as the stricter mode limiting to one Pod, and EBS Multi-Attach as a niche exception requiring a cluster-aware filesystem. See [StatefulSets](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md).
- The versioned-bucket lifecycle question has a precise answer: you need **two** rules in the lifecycle configuration, because current and noncurrent versions are governed separately. An `Expiration` action after 10 days on current objects — which in a versioned bucket does not delete data but adds a _delete marker_ — and a `NoncurrentVersionExpiration` after the retention you want, which is what actually removes the old versions and reclaims storage. Add `ExpiredObjectDeleteMarker` cleanup and an `AbortIncompleteMultipartUpload` rule. The insight to state: in a versioned bucket, "delete" is not deletion until the noncurrent versions expire — which is exactly why people are surprised by their storage bill. See [S3 storage classes](../aws-engineering/what-are-the-s3-storage-classes-and-when-do-you-use-each.md).
- The branch-specific trigger question wants you to reject polling. Use a **webhook** so the forge pushes the event, not a `pollSCM` schedule which wastes cycles and adds latency — the follow-up "should the pipeline constantly check the repo?" is asking for exactly that. Then: a single pipeline definition with branch conditions (`when { branch 'staging' }` in Jenkins, or `on.push.branches` in GitHub Actions) so behaviour is versioned with the code, and a **multibranch pipeline** as the best Jenkins job type because it creates and destroys jobs per branch automatically from the `Jenkinsfile` in that branch. Add environment-scoped credentials so the staging pipeline physically cannot deploy to production. See [Jenkins pipelines](../cicd/what-are-jenkins-pipelines.md).
- "Is rollback handled by CI/CD or Kubernetes?" has a good answer: **both, at different layers**, and you should say which owns what. Kubernetes owns the mechanism — a Deployment keeps previous ReplicaSets so `kubectl rollout undo` restores the prior Pod template, and Helm keeps release revisions for `helm rollback`. CI/CD owns the _decision_ — detecting the regression from health checks or metrics and triggering the rollback, ideally automatically via `helm upgrade --atomic` or an Argo Rollouts analysis step that aborts on a failed metric. Say that the durable answer is GitOps: reverting the commit is the rollback, and the controller reconciles it. See [deployment strategies](../devops-tools-and-automation/what-are-deployment-strategies.md).
- The `aws-auth` questions are asked twice, and the currency point matters: `aws-auth` is a ConfigMap in the `kube-system` namespace with `mapUsers` and `mapRoles` sections that map IAM ARNs to Kubernetes usernames and groups — and current EKS prefers **access entries and access policies**, an API-level mechanism that avoids editing a ConfigMap. For the teammate question, the full path is: IAM permission to call `eks:DescribeCluster` so they can run `aws eks update-kubeconfig`, then a mapping (access entry or `aws-auth`) placing them in a group, then a RoleBinding for namespace-scoped access or a ClusterRoleBinding for cluster-wide — prefer the RoleBinding. On the "what mistakes break authentication" follow-up, say the one everybody hits: a malformed `aws-auth` edit locks **everyone** out of the cluster, because the only remaining access is the IAM identity that created it — which is why access entries exist and why you back the ConfigMap up before editing. See [how RBAC works in Kubernetes](../kubernetes/how-does-rbac-work-in-kubernetes.md).
- The public-Helm-chart questions have one governing principle: never fork or edit the chart, because you inherit the maintenance burden and lose upgrade compatibility. Instead override through your own `values.yaml`, use `--set` and `--set-file` for individual and file-backed values, and add extra manifests either through the chart's own `extraObjects`-style hook if it provides one, or by wrapping the public chart as a **dependency** in your own parent chart whose `templates/` folder holds your additional YAML. Say why that is safe: your additions live in your chart, so a dependency version bump does not overwrite them. On the secrets follow-up, name the options and rank them: External Secrets Operator or the Secrets Store CSI driver pulling from Secrets Manager at runtime (best, because rotation needs no commit), Sealed Secrets or SOPS for encrypted-in-Git, and never plain values in a committed `values.yaml`. See [what Helm is](../container-orchestration-advanced/what-is-helm.md) and [managing secrets in CI/CD pipelines](../devsecops/how-do-you-manage-secrets-in-ci-cd-pipelines.md).
- The slow-ingress-under-peak-load question has eight follow-ups, so answer it as an ordered narrowing rather than touching each in turn. First establish where the latency is: compare the load balancer's target response time against the controller's own request duration, which tells you whether the controller or the backend is slow. Then, if it is the controller: check its CPU — nginx ingress is CPU-bound on TLS handshakes — replica count, worker connections and `keepalive` settings, and whether it is CPU-throttled against its limit. If it is the backend: check whether readiness probes are flapping so endpoints churn, and whether backend Pods are saturated. Then the platform layer: ALB or NLB LCU limits, and target group health. Say that the fix is an HPA on the controller rather than a fixed replica count, and that the ingress controller should have generous requests and ideally its own node pool. That answers the static-versus-dynamic follow-up too: static scaling either wastes capacity off-peak or is too small at peak, so you scale on load with an HPA and let the Cluster Autoscaler add nodes underneath. See [autoscaling workloads and nodes](../kubernetes/how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md).
- The stuck-Jenkins-job question wants a layered check: read the console log to see the last step reached; check whether the agent is online and whether the node has disk, memory, or executor capacity; look at whether the job is waiting on an input step, a lock, or a `waitForQualityGate` that will never return; check whether an external API call or a `docker pull` is hanging with no timeout; and check for a deadlock where the job holds an executor while waiting for another job. Say the two preventive fixes: a `timeout` block around every stage so nothing hangs forever, and `retry` with backoff for genuinely flaky external calls. Restarting the agent is a last resort, not a first response.
- The PDB question needs the voluntary-versus-involuntary distinction stated explicitly, because the follow-ups ask for it: a PDB constrains **voluntary** disruptions — `kubectl drain`, node upgrades, cluster autoscaler scale-down, eviction API calls — and has no effect whatsoever on **involuntary** ones such as a node crashing, hardware failure, or a kernel OOM kill. Use `minAvailable` when you care about a floor of serving capacity (natural for a fixed replica count), and `maxUnavailable` when you care about the churn rate (natural for large or autoscaled deployments, since it scales with replica count). Then the failure mode: `minAvailable` equal to the replica count blocks drains indefinitely, which is how a cluster upgrade gets stuck.
- Round 1's opening two questions are ownership probes disguised as architecture questions — "which part do _you_ personally manage", "do _you_ handle IAM and RBAC". Answer precisely about your own scope and do not inflate it, because every subsequent follow-up will test the claim. Saying "I owned the EKS layer and the pipelines; another team owned the network baseline" is far stronger than an implied "everything", which collapses two follow-ups later.
- For the cost question, come with numbers: what you measured, which levers you pulled — right-sizing from observed usage, Savings Plans for the steady baseline, Spot for interruptible work, storage lifecycle rules, deleting orphaned volumes and idle load balancers, cutting log retention — and the resulting percentage. The follow-up about ALB pricing tells you they want cost fluency at the line-item level, not slogans. See [cloud cost optimisation](../cloud-cost-optimization/what-is-cloud-cost-optimization.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
