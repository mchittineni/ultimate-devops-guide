---
title: "What cloud and DevOps interview questions does IBM ask?"
id: 338
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - ibm
  - infrastructure-as-code
  - configuration-management
  - kubernetes
  - aws-engineering
  - linux-administration
  - cicd
  - devsecops
  - scalability-and-high-availability
---

# What cloud and DevOps interview questions does IBM ask?

## Questions

### Round set 1 — Cloud Engineer (3.3 YOE)

**Terraform and drift**

- **What is Terraform and how does it work?**
- **Where do you run your Terraform code — your local machine or a dedicated server?**
- **What is a `tfstate` file, what does it actually do, and where does your organisation store it?**
- **Another engineer changed an instance through the console. You now run `terraform plan`. What does the output show?**
- **What do the `+` and `-` symbols mean in plan output?**
- **If changes were made through the console and you run `terraform apply` without planning first, what happens — will it error, and will it still execute?**

**Vulnerability handling**

- **A vulnerability appears in a running application. How do you handle it?**
- **What changes if it is a production server?**
- **It is a Python application, the vulnerability is in production, and the fix could take six months. What is your approach?**
- **Do you follow any standard or framework for handling these?**

**Ansible**

- **What is Ansible, and have you worked with it?**
- **Can you write a playbook?**
- **How do you store credentials in Ansible, and is there another approach you use for storing secrets securely?**
- **How do you store variables in Ansible?**
- **How do you debug errors in a playbook — what is the command?**
- **You want to run a single command without writing a playbook. What is the command and how do you write it?**
- **Which Ansible modules have you used? Name them.**

**AWS, scripting, and Linux**

- **How do you deploy your application on AWS, and which services do you use?**
- **When deploying to EKS, which other services do you use alongside it?**
- **Have you done shell and Python scripting? Where have you used Python, and for what tasks?**
- **Have you used monitoring tools, and what was your role with them?**
- **How do you disable root login on a server — and what is the exact file and path you change?**
- **Tell me about yourself and your day-to-day activities.**

### Round set 2 — DevOps Engineer (7 YOE)

- **How do you encrypt an EBS volume?**
- **A Jenkins pipeline is randomly failing at the EKS deployment stage, and the logs show timeouts during `kubectl apply`. How do you diagnose it?**
- **How do you securely manage Terraform state files, secrets, and environment isolation?**
- **How would you design an event-driven data ingestion architecture using S3, Lambda, and SNS?**
- **How do you create an HPA?**
- **You have three control-plane nodes and one goes down. What happens?**
- **How do you do global load balancing in Kubernetes?**
- **What is A/B testing and how would you implement it?**
- **How do you check your code for vulnerabilities?**
- **Two clusters run in different regions. One has a problem — how do you shift traffic to the other?**
- **In a log file, how do you extract only the entries with a 200 status code?**
- **When you run `kubectl get pods`, what happens in the background?**
- **How do you read the logs of a Pod from before it restarted?**
- **What is a reverse proxy?**
- **How would you resolve a Git conflict automatically?**

### Round set 3 — DevOps Engineer, scenario-led (5 YOE)

- **Our application is a Node.js app. How would you set up the CI/CD pipeline, and which tools would you use?**
- **We are launching a website with many products and many services, expecting very high load on Black Friday. How do you set it up and make it highly available?**
- **Users are reporting slowness. What do you do to resolve it?**
- **One of the services is leaking memory. How do you troubleshoot that?**
- **Between AWS and Azure, which would you choose and why?**
- **The bill is too high and the client wants it reduced. What do you do?**
- **What is the difference between Terraform, CloudFormation, and ARM templates, and which would you prefer?**
- **How would you store sensitive information inside S3?**
- **In a Lambda function, how do you handle failures and configure retries?**
- **The application is already live and changes have been made. How do you redeploy with zero downtime?**

### Round set 4 — Linux, Jenkins, and EKS (5+ YOE)

- **Write a script to delete files older than 10 days.**
- **What is the difference between a hard link and a soft link?**
- **What is `iptables` in Linux?**
- **How do servers connect to each other in Linux? Explain.**
- **Which configuration management tools do you use?**
- **How do you install a patch across more than 20 servers with Ansible?**
- **How do you reduce build time in Jenkins?**
- **What is a Jenkins agent?**
- **How do you trigger an automatic build in Jenkins?**
- **Write a Jenkins script that runs stages simultaneously, in parallel.**
- **Write Terraform to create an EKS cluster.**
- **How do Pods interact with each other?**
- **What problems have you hit with an EKS cluster?**
- **What do you do when etcd in EKS goes down?**
- **How do you run a container on an ECS cluster?**
- **My EKS cluster has two node groups, and before deploying any Pods, node group 2 shows as unhealthy. I have all the permissions needed to investigate. How do you troubleshoot it, and how do you prevent it in future?**
- **Two containers run on an EC2 instance — a backend and a frontend. How do I connect the backend container to RDS?**
- **The Terraform state file has been deleted, and it was never synced to S3 or version control, so there is no backup. How do you recover?**

## Example

```text
IBM — Cloud / DevOps Engineer, four reported interviews (~78 questions)

  SET 1  Cloud Engineer (3.3 YOE)     23   Terraform state + drift + plan
                                           symbols, 6-month-fix vulnerability,
                                           Ansible in depth, disable root login
  SET 2  DevOps Engineer (7 YOE)      15   Jenkins->EKS timeouts, 3 masters
                                           with 1 down, cross-region traffic
                                           shift, what kubectl does internally
  SET 3  Scenario-led (5 YOE)         10   Black Friday HA, slowness, memory
                                           leak, cut the bill, zero-downtime
                                           redeploy, Lambda retries
  SET 4  Linux / Jenkins / EKS        18   delete files >10 days, hard vs soft
                                           link, iptables, parallel Jenkins,
                                           unhealthy node group, unrecoverable
                                           state file

IBM'S PATTERN
  Every round pushes past the first answer. Vulnerability -> in production ->
  what if the fix takes 6 months -> what standard do you follow. Prepare the
  third and fourth follow-up, not just the definition.
```

```bash
# Delete files older than 10 days — and why -mtime +10 means "older than 10".
find /var/log/app -type f -mtime +10 -print -delete

# Safer production form: restrict the pattern, don't cross filesystems,
# and never let an empty variable expand to /
find "${TARGET:?TARGET not set}" -xdev -type f -name '*.log' -mtime +10 -delete
```

## Interview tips

- The unrecoverable state file is the hardest question here, and it is testing whether you will admit there is no magic recovery. With no remote backend, no versioning, and no VCS copy, the state is gone — but the _infrastructure is untouched_. The path back is to rebuild state: write or keep the configuration, then `terraform import` each resource one at a time (or generate `import` blocks and use `-generate-config-out`), and iterate until `terraform plan` reports no changes. Say the plan-shows-nothing test is how you know you are done, and finish with the prevention that should have existed: remote backend, versioning, locking. See [recovering a lost or corrupted Terraform state file](../infrastructure-as-code/how-do-you-recover-a-lost-or-corrupted-terraform-state-file.md).
- The three-follow-up vulnerability chain in set 1 needs a real answer at each level. In general: identify, assess exploitability and exposure, patch, verify. In production: the same, but with a change window, a rollback plan, and staged rollout. When the fix will take six months: you cannot leave it open, so you compensate — a WAF rule or virtual patch blocking the exploit path, restrict network reach, remove the vulnerable feature or endpoint, add detection and alerting, and record a risk acceptance with an owner and a review date. Then, for the standards question, name CVSS for scoring, a CVE and SBOM inventory, and your own SLA by severity. Compensating controls plus documented risk acceptance is the phrase that lands. See [prioritising vulnerabilities without blocking delivery](../devsecops/how-do-you-prioritise-vulnerabilities-without-blocking-delivery.md).
- The `apply`-without-`plan` question has a precise answer that surprises people: it does **not** error. `apply` runs a refresh and plan internally, shows you the diff, and asks for confirmation — so it executes and, if the configuration still says the old value, it reverts the console change. The only difference from planning first is that you never had a reviewable artefact. Combine that with the `+` and `-` symbols — `+` create, `-` destroy, `-/+` destroy and recreate, `~` update in place — and the drift question is answered too.
- Three control-plane nodes with one down: the cluster stays fully operational, because etcd's raft quorum for a three-member cluster is two. Say the number, then say what happens next — you are now one failure from losing quorum entirely, at which point etcd goes read-only and the API server cannot accept writes, so replacing that member is urgent. Quorum arithmetic is what is being tested, so also mention why control-plane counts are odd. See [main components of Kubernetes architecture](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md).
- "What does etcd going down on EKS mean" is a trick worth catching: on EKS, AWS manages and does not expose etcd, so you cannot log in, snapshot, or restore it. Your job is to raise a support case and, on your side, ensure workload manifests live in Git so the cluster is reproducible. Naming the managed-service boundary is the answer.
- `kubectl get pods` internals is a favourite depth probe. Walk it: `kubectl` reads `kubeconfig` for the endpoint and credentials, builds an HTTPS `GET` to `/api/v1/namespaces/<ns>/pods`, the API server authenticates the client, authorises through RBAC, passes admission (not relevant for reads), reads from etcd via the watch cache, and returns JSON that `kubectl` formats into a table. Mentioning the watch cache rather than "it reads etcd directly" is the detail that stands out.
- Logs from before a restart is one flag: `kubectl logs <pod> --previous` (or `-p`), with `-c <container>` for a multi-container Pod. Add that it only holds the immediately previous instance, which is why you ship logs off the node. See [troubleshooting a Pod stuck in Pending or CrashLoopBackOff](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md).
- The randomly-failing `kubectl apply` timeout is a good scenario. Split the causes: the API server endpoint is throttling or the private endpoint is unreachable from the agent's subnet, the agent's IAM credentials or token expired mid-run, webhook admission controllers are timing out, the cluster is under control-plane load, or the apply is waiting on a rollout that never becomes Ready. Say you would raise `--request-timeout`, check API server metrics and audit logs, and look at failing validating webhooks — webhooks are the most common real culprit.
- Cross-region traffic shift needs a named mechanism at the DNS or edge layer: Route 53 health checks with failover or weighted records, or Global Accelerator for a faster switch with static anycast IPs. Say that the hard part is the data tier, not the traffic — the standby region needs replicated data, and the RPO you accept determines whether this is minutes or seconds of loss. See [designing for multi-region resilience](../cloud-engineering/how-do-you-design-for-multi-region-resilience.md).
- Hard versus soft link should include the consequences: a hard link is another directory entry pointing at the same inode, so it cannot cross filesystems, cannot link a directory, and the data survives until the last link is removed; a symlink is a small file holding a path, can cross filesystems and point at directories, and breaks if the target moves. See [Linux filesystem hierarchy](../linux-administration/what-is-linux-file-system-hierarchy.md).
- Disabling root login is `PermitRootLogin no` in `/etc/ssh/sshd_config` — give the exact path since they asked for it explicitly — followed by `sshd -t` to validate and `systemctl reload sshd`. Add that on modern distributions a drop-in under `/etc/ssh/sshd_config.d/` is preferred, and that you should verify you still have a working sudo user before reloading. See [managing services in Linux](../linux-administration/how-do-you-manage-services-in-linux.md).
- For the memory-leak scenario, describe a measurement path rather than a guess: confirm the trend with RSS or container `working_set` over time, check whether restarts correlate with `OOMKilled` and exit code 137, then get a heap profile from the runtime — a Node.js heap snapshot, a JVM heap dump, or `pprof` — and diff two snapshots to find what is retained. Say that a memory limit turns a leak into a predictable restart rather than a host-wide failure, which buys time but is not a fix. See [debugging a Linux performance problem from first principles](../linux-administration/how-do-you-debug-a-linux-performance-problem-from-first-principles.md).
- Black Friday high availability should be answered as preparation with numbers: load test to a known ceiling, pre-scale rather than relying on reactive autoscaling, CDN for static and cacheable content, queue the slow work, cache reads, read replicas, multi-AZ everything, rate limiting, and a graceful-degradation plan that sheds non-essential features. Add a game day and a freeze on risky deploys. See [designing a system to degrade gracefully under overload](../scalability-and-high-availability/how-do-you-design-a-system-to-degrade-gracefully-under-overload.md).
- Secure data in S3 means several controls together: SSE-KMS with a customer-managed key, bucket policy denying unencrypted or non-TLS requests, Block Public Access on, versioning plus a lifecycle policy, access via IAM roles rather than keys, and a VPC endpoint so the traffic never leaves the private network. See [S3 storage classes](../aws-engineering/what-are-the-s3-storage-classes-and-when-do-you-use-each.md).
- Lambda retry behaviour differs by invocation type and interviewers know it: synchronous invocations do not retry server-side, asynchronous ones retry twice with backoff and then go to a dead-letter queue or on-failure destination, and stream sources such as Kinesis or DynamoDB retry until the record expires and can block the shard unless you set bisect-on-error or a failure destination. Naming that stream-blocking behaviour is the strongest part of the answer.
- Automatic Git conflict resolution should be answered carefully: you can pick a side with `-X ours` or `-X theirs`, configure `rerere` to replay resolutions you have made before, or use a merge driver for generated files such as lock files. But say plainly that automatic resolution on real source code risks silently discarding work, so the real fix is small, frequently integrated changes. See [handling merge conflicts](../version-control/how-to-handle-merge-conflicts-in-git.md).
- Parallel Jenkins stages: a `parallel` block containing named stages, or `parallel` with a map of closures in scripted syntax, plus `failFast true` when one failure should abort the rest. See [Jenkins pipelines](../cicd/what-are-jenkins-pipelines.md).
- For 200-status extraction from a log, `grep ' 200 '` is fragile — better is a field-aware match such as `awk '$9 == 200'` on a combined access log, and say why: a bare `grep 200` also matches byte counts and timestamps. See [analysing logs with grep, awk, and sed](../linux-administration/how-do-you-analyse-logs-and-text-files-with-grep-awk-and-sed.md).

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
