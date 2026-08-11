---
title: "What DevOps interview questions come up when the company is not named?"
id: 366
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - unattributed
  - aws-engineering
  - kubernetes
  - infrastructure-as-code
  - docker
  - network-security
  - linux-administration
  - cicd
  - version-control
---

# What DevOps interview questions come up when the company is not named?

## Questions

Eight reported DevOps Engineer rounds whose submitters did not name the employer. Because the company is unknown, these are the closest thing in this collection to a general-market sample.

### Round 1 — L1 and L2 screening

**L1**

- **In Git, explain the `push` and `pull` commands.**
- **What are Git tags used for?**
- **What are the different types of branch in Git?**
- **How do you write an Ansible playbook, and which client requirements do you take into account?**
- **In Python, what are lists and tuples and how do they differ?**
- **In CloudWatch, what are log groups and log trails for?**
- **In Terraform, what do `init`, `plan`, and `apply` do?**
- **What happens if the Terraform state file is accidentally deleted?**
- **What is the purpose of an S3 bucket policy?**
- **How do you manage the lifecycle of an S3 bucket?**
- **In Airflow, if a job fails, how do you debug it?**
- **If you are facing performance problems on a server, how do you troubleshoot?**

**L2**

- **What are network ACLs and security groups, and how do they differ?**
- **Explain EC2 instances and how you handle multiple VPCs.**
- **How do you configure RDS, and what factors do you weigh — size, requirements?**
- **How much data is in your RDS MySQL instance, and how many primaries and replicas are there?**
- **How do you build a Grafana dashboard?**
- **Which CI/CD pipelines are you familiar with, and what is the difference between declarative and scripted pipelines?**
- **In Kubernetes, if a Pod is `Pending`, how do you troubleshoot it?**
- **If Docker containers are consuming too much disk space, how do you fix it?**
- **In Linux, how do you attach and detach a filesystem?**
- **How do you print the last 15 lines of a file?**
- **How do you enable passwordless authentication between two servers?**

### Round 2 — AWS and Kubernetes with live writing

- **What is your organisation's current CI/CD process and toolchain?**
- **How comfortable are you with AWS — rate yourself out of five.**
- **Questions on IAM, Fargate, EC2, and Lambda.**
- **Write a Lambda function.**
- **Explain the Kubernetes architecture and walk me through the workflow.**
- **Write Terraform to provision an EC2 instance in a public subnet inside a VPC.**
- **Are you using a Dockerfile, and do you build it with CodeBuild?**
- **How many containers can run in a Pod? How many did you run, and give a use case for running four or five in one Pod.**
- **Did you configure Prometheus and Grafana?**
- **What security measures and tools did you put in your CI/CD pipeline?**
- **Questions on RBAC.**

### Round 3 — networking, DNS, and failure modes

- **How many NAT gateways do you need for two public and two private subnets in a single VPC — minimum and maximum?**
- **Explain TTL in DNS — how it works, when you use it, and the flow.**
- **How does weighted routing work in a load balancer?**
- **How is Docker operable on a Linux machine? Explain the Docker architecture components.**
- **There is one control-plane node and three workers. If the control plane fails, do the Pods keep running or crash?**
- **etcd is a key-value store — can you write to it manually?**
- **How do you roll back a failed deployment in Docker and in Kubernetes?**
- **How does SSL work — with Certbot, Let's Encrypt, and AWS? Explain the flow.**
- **What are the top five infrastructure attacks, and how do you mitigate them?**
- **If the state file is lost, what do you do — with a backup, and without one?**
- **What does load average mean in Linux, how is it calculated, and in what format is it reported?**
- **One of your worker nodes is not joining the cluster. How do you debug it?**
  The submitter also noted further scenario questions on load balancers, Route 53, and EKS plus database automation and administration.

### Round 4 — security, Terraform, and Kubernetes scheduling

**Security and access**

- **How do you ensure the best possible security for a highly available three-tier architecture?**
- **What is the difference between security groups and NACLs, and where do you use firewalls, security groups, and NACLs?**
- **Can you block traffic on a specific port using a security group?**
- **What is VPC peering?**
- **How do you scan for vulnerabilities specifically on AWS instances?**
- **What is the difference between IAM users and roles?**
- **How do you connect to private instances when SSH is not working?**
- **What password security practices does your organisation use?**
- **Which security parameters must you consider when creating a production EC2 instance, and how do you protect the data on it?**
- **How do you connect from AWS to on-premises servers, and what is Transit Gateway for?**
- **New members are joining your DevOps team. How do you give them AWS access, and what is the console login behaviour?**

**Terraform**

- **What provisioners does Terraform have, and what are their use cases?**
- **You have an EC2 instance A and want to create instance B without destroying A. How do you do that?**
- **You created an EC2 instance with Terraform. There is no state backup — not remote, not local. What happens when you apply?**
- **If you put a command in a `null_resource` and it should run every time, what is the behaviour?**
- **What is a map of objects in Terraform — write an example.**

**Kubernetes**

- **You have three nodes — small, medium, and large — and want only the data load to go to the large one. How?**
- **When Pods are deployed they should land on the large and medium nodes but never the small one. How do you configure that?**
- **What does this error mean and how do you debug it: `0/5 nodes are available: insufficient memory`?**
- **What is the difference between scaling and autoscaling in Kubernetes?**
- **If you do not specify `targetPort` in a Service, what happens?**
- **What are the different types of Secret in Kubernetes?**
- **An Ingress object is not routing traffic into the cluster. What are the reasons and how do you troubleshoot?**
- **You created a Service that is not mapped to a Deployment. What could be wrong and how do you debug it?**
- **What are the different ways to specify probes?**
- **If you set `restartPolicy: Never`, what happens?**
- **What is an init container and why do you need one?**
- **What is the difference between EKS, ECS, and Fargate?**
- **What is the difference between an EBS-backed and a non-EBS-backed instance?**

**Git**

- **What is the difference between `git push --force-with-lease` and `--force`?**
- **How do you delete the last two commits?**

### Round 5 — design and scripting

- **What happens if the firewall between the Kubernetes control plane and a worker node breaks? Do existing deployments keep working, are new ones affected, and how do you communicate that?**
- **How do you use Secrets in Kubernetes, and what encryption do you use?**
- **How does a GSLB — global server load balancer — work?**
- **What are SLI, SLO, and SLA?**
- **How do you create extensions or plugins in Grafana?**
- **How was your ELK setup built, and which agents collect the data?**
- **Give one scenario where you did a root cause analysis on Linux.**
- **You have JSON data. How would you ingest and collect it in key format?**
- **Design the Istio setup for your Kubernetes cluster.**
- **How do you create and set up an EventBridge rule via Terraform?**
- **What is the command to add an annotation and a label to an existing Pod?**
- **Design a Kubernetes cluster with Ingress.**
- **A sudden traffic surge makes a web application unresponsive. What steps do you take to mitigate it?**
- **Write the manifest for a Pod deployment with a replica count of three running the Apache httpd image.**
- **How do you reduce the size of a Dockerfile?**
- **Write a shell script that finds and deletes all files in a directory older than 30 days.**
- **Write a script that monitors disk usage and, if it exceeds 80%, logs the details to a file and sends an alert email.**
- **Write a script that renames every `.txt` file in a directory by appending the current date to the filename.**

### Round 6 — Azure-flavoured Kubernetes and Terraform

- **What is the difference between an NSG and a firewall?**
- **What is the difference between `COPY` and `ADD` in a Dockerfile?**
- **What is the difference between `ENTRYPOINT` and `CMD`?**
- **What are taints and tolerations?**
- **What is a StatefulSet?**
- **Explain the Kubernetes architecture.**
- **What is a Pod, what are the Service types, and what are namespaces?**
- **Give a use case for NodePort and for ClusterIP.**
- **What is a PodDisruptionBudget?**
- **What is the difference between a PV and a PVC?**
- **Why do the kubelet and kube-proxy exist?**
- **Explain a GitHub Actions workflow file.**
- **Can you connect two VMs that are in different virtual networks?**
- **What are private endpoints, and what is ExpressRoute in Azure?**
- **What is the Terraform state file, and what is the lock file?**
- **How do you build an image and push it to ACR, and how do you reference an existing image in a YAML file to deploy a Pod?**

### Round 7 — breadth plus live authoring

- **What is your organisation's current CI/CD process and toolchain?**
- **What do you know about CyberArk, and how are you consuming it in your pipeline?**
- **Which scripting language do you know, and how confident are you in it?**
- **Which AWS services have you used?**
- **If you had to design infrastructure for high scalability, how would you do it?**
- **What are NACLs, security groups, and a NAT gateway?**
- **Explain the Kubernetes architecture, and the difference between a ReplicaSet and a Deployment.**
- **Questions on Ansible and Terraform, and on ConfigMaps, PVs, and PVCs.**
- **Write a Deployment manifest.**
- **Write a Dockerfile, and explain multi-stage Dockerfiles.**
- **Which type of `Jenkinsfile` are you using? Write one.**
- **What is the toughest situation you have faced implementing something, and what did you learn?**
- **Have you handled debugging or troubleshooting in Kubernetes?**
- **Questions on Prometheus and Grafana, and on Fargate.**
- **What are Lambda functions, have you used any, and what did you achieve with them?**

### Round 8 — Jenkins, Terraform, and cross-account access

- **Write Terraform to create multiple S3 buckets.**
- **How did you manage the state file, and how do you handle state file conflicts?**
- **What did you do with Jenkins, and how do you integrate SonarQube with the Jenkins server?**
- **How were you authenticating Jenkins to push a Docker image to the registry?**
- **Which deployment strategy do you follow, and how do you implement blue-green?**
- **Do you know what an HPA is?**
- **You deploy an application, find an issue, and want to roll back to a particular version in Kubernetes. What is the command?**
- **What is a StatefulSet?**
- **How many types of IAM policy are there?**
- **What is the difference between S3 bucket policies and ACLs?**
- **What is dynamic autoscaling?**
- **What is the difference between security groups and NACLs?**
- **Two AWS accounts in one organisation: account A has an EC2 instance, account B holds some tokens. The instance needs to read those tokens. How do you achieve that?**

## Example

```text
Unattributed DevOps rounds 1-8 — 194 questions

  ROUND 1  L1 + L2 screening            23   Git, Ansible, Python, CloudWatch,
                                             Terraform basics, S3, Airflow,
                                             then NACL/RDS/Grafana/K8s/Linux
  ROUND 2  AWS + K8s, live writing      11   write a Lambda, write Terraform
                                             for EC2 in a public subnet,
                                             containers per Pod use case
  ROUND 3  Networking + failure modes   12   NAT gateway count, DNS TTL,
                                             control plane fails, write to etcd,
                                             top 5 infra attacks, load average
  ROUND 4  Security + TF + scheduling   34   the largest single round: SG vs
                                             NACL, no-state-file apply,
                                             null_resource, node targeting,
                                             insufficient memory, --force-with-lease
  ROUND 5  Design + scripting           18   firewall break between planes,
                                             GSLB, Istio design, traffic surge,
                                             three shell scripts
  ROUND 6  Azure-flavoured              21   NSG vs Firewall, ExpressRoute,
                                             private endpoints, ACR, PDB, PV/PVC
  ROUND 7  Breadth + authoring          15   CyberArk, design for scalability,
                                             write Deployment + Dockerfile +
                                             Jenkinsfile
  ROUND 8  Jenkins + cross-account      13   state conflicts, Sonar in Jenkins,
                                             registry auth, rollback command,
                                             cross-account token access

WHAT AN UNATTRIBUTED SAMPLE TELLS YOU
  Security groups versus NACLs appears in FOUR of eight rounds. Kubernetes
  architecture in four. Terraform state loss in three. Those three topics are
  the closest thing to a guaranteed question in the general market.
```

## Interview tips

- The NAT gateway count question has an exact answer: the **minimum is one** — a single NAT gateway in one public subnet can serve both private subnets, and it is the cheapest option. The **maximum you would sensibly build is two**, one per availability zone, because a NAT gateway is zonal: if its zone fails, private subnets routed through it lose egress. So the real answer is "one for cost, two for availability, and the deciding factor is whether you can tolerate losing egress in one zone" — plus the detail that cross-zone NAT traffic is charged, which is the other reason to run one per zone. See [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md).
- "Can a security group block a specific port?" is a trick and the answer is **no**. Security groups are allow-only — there is no `deny` rule — so you cannot block one port while allowing everything else. To deny a specific port or a hostile source range you need a NACL, which is stateless and supports explicit deny. That contrast is exactly why both exist, and it also answers the "where do you use firewalls, SGs, and NACLs" question in the same round. See [network segmentation](../network-security/what-is-network-segmentation.md).
- "Control plane fails — do Pods crash?" has a precise answer that many candidates get wrong: existing Pods **keep running and keep serving traffic**, because the kubelet on each node continues managing its containers independently. What you lose is the control plane's functions — no new scheduling, no `kubectl`, no self-healing, no rescheduling if a node dies, no scaling. So a control-plane outage is invisible to users until something else breaks. Say both halves. See [main components of Kubernetes architecture](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md).
- "Can you write to etcd manually?" — technically yes with `etcdctl`, and you must not. The API server owns the schema, performs validation, admission, and defaulting, and maintains resource versions and watch semantics; writing directly bypasses all of it and can corrupt the cluster in ways that are very hard to diagnose. Say "physically possible, operationally forbidden, and the API server is the only supported writer".
- `--force-with-lease` versus `--force` is a genuinely important distinction: `--force` overwrites the remote branch unconditionally and will silently destroy commits a colleague pushed after your last fetch; `--force-with-lease` refuses unless the remote is exactly where you last saw it. Say that `--force-with-lease` is the only force-push you should ever type. Pair it with deleting the last two commits — `git reset --hard HEAD~2` locally, or `git revert` if the commits are already shared, since rewriting published history is the thing that causes the problem in the first place. See [recovering from a bad Git history rewrite](../version-control/how-do-you-recover-from-a-bad-git-history-rewrite.md) and [undoing changes in Git safely](../version-control/how-do-you-undo-changes-in-git-safely.md).
- The apply-with-no-state-file question appears in rounds 3 and 4 and needs the honest answer: Terraform has no record of the resource, so `plan` proposes creating it and `apply` will build a **duplicate** alongside the one already running — it will not adopt or destroy the original. Recovery is to import the existing resources until `plan` is empty. Say that the infrastructure is fine and only Terraform's knowledge is gone, and that this is precisely why remote state with versioning is non-negotiable. See [recovering a lost or corrupted Terraform state file](../infrastructure-as-code/how-do-you-recover-a-lost-or-corrupted-terraform-state-file.md).
- The "create B without destroying A" question is asking about `create_before_destroy` and about _not_ accidentally replacing A. If A and B are separate resources, use `for_each` over a map so each is keyed independently and adding B does not touch A — whereas increasing `count` and reordering a list re-indexes and can destroy the wrong instance. That link between `count` re-indexing and accidental destruction is the real answer.
- `null_resource` with a command that should run every time: without a `triggers` value that changes, it runs **once** and never again, because Terraform considers it unchanged. To force it every apply you need a trigger that always differs — historically `timestamp()` — and the honest answer is that if you need something to run on every apply, Terraform is the wrong tool, because it is a convergence engine and not a task runner. Mention that `null_resource` is superseded by `terraform_data`.
- `0/5 nodes are available: insufficient memory` means the scheduler summed the Pod's memory **requests** against each node's _allocatable_ memory and none had room. Debug it with `kubectl describe node` to compare allocated requests against allocatable, then decide: lower the request if it was inflated, add nodes or let the Cluster Autoscaler do it, or evict lower-priority workloads. Say that allocatable is less than the node's nominal capacity because of kubelet and system reservations, and that scheduling uses requests rather than actual usage. See [autoscaling workloads and nodes](../kubernetes/how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md).
- The two node-targeting questions are a pair with different mechanisms. To send only the data workload to the large node, label the node and use `nodeSelector` or node affinity on that workload — and if you want to _reserve_ the node so nothing else lands there, taint it and add a matching toleration. To exclude the small node, use node affinity with `NotIn` against a size label, which is the expressive form `nodeSelector` cannot provide. Naming affinity's `NotIn` operator is what distinguishes the second answer from the first. See [controlling which node a Pod runs on](../kubernetes/how-do-you-control-which-node-a-pod-runs-on.md).
- Omitting `targetPort` in a Service is a small precise fact: it defaults to the same value as `port`. So a Service with `port: 8080` and no `targetPort` sends traffic to container port 8080 — which silently fails if the container actually listens on 80. Say that this is a common cause of a Service with healthy endpoints that still returns connection refused.
- `restartPolicy: Never` means the kubelet will not restart a container that exits, so the Pod goes to `Succeeded` or `Failed` and stays there. Add the context that makes it useful: `Never` and `OnFailure` are for Jobs and batch work, while `Always` is the only valid value for a Deployment — which is why you cannot set `Never` on a long-running service.
- The cross-account token question in round 8 is answered with role assumption, and the resource-policy half is what people forget: create a role in account B whose trust policy names account A (or the specific role), attach a policy allowing `secretsmanager:GetSecretValue`, give the EC2 instance in A an instance profile permitted to `sts:AssumeRole` into it, and — if the secret is KMS-encrypted with a customer-managed key — grant `kms:Decrypt` in the key policy too. The KMS key policy is the step that most often blocks this in practice. See [how AWS IAM evaluates a request](../aws-engineering/how-does-aws-iam-evaluate-a-request.md) and [structuring a multi-account AWS organisation](../aws-engineering/how-do-you-structure-a-multi-account-aws-organisation.md).
- Load average is asked with three parts, so answer all three: it is the exponentially-damped average number of processes in a runnable _or uninterruptible_ state, reported as three numbers over 1, 5, and 15 minutes, and it must be read relative to core count — 4.0 on a four-core machine is fully loaded, on sixteen cores it is quiet. The detail that earns the point is that Linux includes processes blocked on I/O in the D state, so a high load average can mean disk contention rather than CPU saturation. See [debugging a Linux performance problem from first principles](../linux-administration/how-do-you-debug-a-linux-performance-problem-from-first-principles.md).
- Containers consuming disk is answered with the layers: `docker system df` to see where it went, then `docker system prune -a --volumes` with a warning that it deletes unused volumes, plus log driver limits (`max-size`, `max-file`) because the default `json-file` driver grows without bound, and a check of whether it is actually the overlay filesystem, images, or logs. In Kubernetes the equivalent is the kubelet's image garbage collection thresholds, and `DiskPressure` evictions are the symptom.
- The firewall-break-between-planes question in round 5 is the control-plane question in different clothing, plus a communication element. Existing workloads keep serving; the node goes `NotReady` after the monitor grace period, its Pods are eventually marked for eviction and rescheduled elsewhere, and `kubectl logs` and `exec` to that node stop working because they go through the kubelet. On the communication half, say you would state user impact rather than component status, give a cadence, and be explicit that no user-facing outage has occurred yet — which is the accurate and reassuring message.
- Round 5's three scripts are all one-liners wrapped in safety. Files older than 30 days: `find /path -type f -mtime +30 -delete`, with `-xdev` and a `${DIR:?}` guard so an unset variable cannot expand to `/`. Disk usage above 80%: parse `df -P` with `awk`, log to a file, and send via a webhook rather than SMTP — and say a Prometheus alert on node-exporter is the better production answer. Renaming `.txt` files with a date: loop with parameter expansion `mv "$f" "${f%.txt}-$(date +%F).txt"`, quoting to survive spaces in filenames. See [writing a production-grade Bash script](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md).
- GSLB should be explained as DNS-or-anycast-based global traffic distribution: health-checked endpoints in multiple regions, with clients steered by latency, geography, or weight — Route 53 with health checks, or Global Accelerator for anycast IPs that fail over faster than DNS because they are not subject to client-side caching. Say why the DNS approach is slower to fail over: resolvers and browsers cache beyond the TTL. See [managing DNS and global traffic routing](../cloud-engineering/how-do-you-manage-dns-and-global-traffic-routing.md).
- IAM users versus roles, and the new-team-member question, are the same answer: users are long-lived identities with passwords and access keys; roles are assumable identities that vend temporary credentials. For onboarding, say you would not create IAM users at all — federate through IAM Identity Center with permission sets, MFA enforced, so console login goes through SSO and no static key exists. See [least-privilege identity in the cloud](../cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md).
- For "top 5 infrastructure attacks", pick five with a mitigation each rather than listing threat names: credential compromise and privilege escalation (short-lived federated credentials, MFA, least privilege), exposed storage or management ports (Block Public Access, no `0.0.0.0/0` on 22 or 3389, private subnets), unpatched vulnerabilities and supply-chain compromise (scanning, image signing, immutable rebuilds), DDoS and application-layer abuse (WAF, rate limiting, Shield), and misconfiguration drift (IaC scanning, Config rules, guardrails via SCPs). See [designing defence in depth for a cloud network](../network-security/how-do-you-design-defence-in-depth-for-a-cloud-network.md).
- The multi-container Pod use case question wants a real answer, not a number. Say containers in a Pod share the network namespace and volumes, so legitimate multi-container patterns are a sidecar proxy, a log shipper, a config or secret refresher, and an init container for setup — and that four or five containers in one Pod is usually a design smell unless there is a genuine tight coupling, because they scale and fail together. Naming that as a smell is the better answer. See [what a Pod is](../kubernetes/what-is-a-pod-in-kubernetes.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?]] (`#402`): [How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?](../cicd/how-do-you-troubleshoot-a-jenkins-pipeline-that-never-starts-or-hangs-in-the-queue.md)
- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
