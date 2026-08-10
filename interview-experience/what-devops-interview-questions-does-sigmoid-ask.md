---
title: "What DevOps interview questions does Sigmoid ask?"
id: 378
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - sigmoid
  - kubernetes
  - aws-engineering
  - infrastructure-as-code
  - scripting-and-automation
  - docker
  - linux-administration
  - monitoring-and-logging
  - cicd
  - scalability-and-high-availability
---

# What DevOps interview questions does Sigmoid ask?

## Questions

### Round set 1 — coding and Kubernetes basics (7 YOE)

- **Reverse a string using a `for` loop.**
- **Check whether a string is a palindrome using a `for` loop.**
- **Given `"Hello World Hello"`, count how many times `Hello` is repeated.**
- **What is the difference between a ReplicaSet and a ReplicationController?**
- **What are your Kubernetes backup policies?**
- **How do you handle deployment failures?**
- **What happens if the control-plane node fails suddenly?**

### Round set 2 — Kubernetes resources, Terraform, and log parsing (7 YOE)

- **What is `terraform taint`?**
- **How do you limit resource usage in Kubernetes? Write the YAML showing requests and limits.**
- **Write a Deployment named `space-alien-welcome-message-generator` using image `httpd:alpine` with one replica, and a readiness probe that runs `stat /tmp/ready` so the Pod becomes ready once that file exists — with `initialDelaySeconds: 10` and `periodSeconds: 5`.**
- **If the liveness probe is healthy but the readiness probe is failing, what happens?**
- **How would you find out whether data was lost when switching back between databases?**
- **Have you integrated a global load balancer with a Kubernetes cluster?**
- **How do you enable RBAC for service accounts?**
- **You created a resource through Terraform and it failed during provisioning. What happens?**
- **What is `null_resource` for in Terraform?**
- **If a developer accidentally hardcoded a password in source code and pushed it, how do you catch and fix that in the CI process?**
- **If a Terraform deployment fails, what is your approach?**
- **Write a script that reads a log and alerts when the same error message occurs more than three times.** The sample input mixes `ERROR` and `INFO` lines, and the expected output is one `[ALERT]` line per repeated message.
- **What is a DNS custom resolver?**
- **Which metrics do you use for monitoring?**

### Round set 3 — regional failure and design (7 YOE)

- **A load balancer is created in one region and that region goes down. What happens?**
- **RDS is hosted in one region with read replicas in others. That primary region goes down — how do you redirect traffic, given that a second writable database is too expensive for the client?**
- **Which deployment strategy is best if you only have one Pod running?**
- **If you use blue-green deployment, exactly which configuration do you change to reroute traffic between blue and green?**
- **A new web deployment went out today. How do you make sure the application is behaving, and find problems before users do?**
- **What are the practical difficulties of running infrastructure in two different regions?**
- **What is the failover mechanism in a load balancer?**
- **Is it possible to have an auto-scaling group and a load balancer in different regions?**
- **Write a shell script to delete log files older than 30 days.**
- **How do you create a non-root user in a Dockerfile, and how do you create custom images?**
- **How do you enable debug logs in Terraform?**
- **Create a system design for a three-tier architecture with security and availability in place.**
- **Write a Python script for: given a string, find the length of the longest substring without duplicate characters.**

### Round set 4 — three-round in-person process (4-7 YOE)

**Round 1 — whiteboard architecture**

- **Walk me through the flow from development to production, and the security checks in your CI pipeline.**
- **What branching strategy does your organisation follow, and why that one over the alternatives?**
- **Design a three-tier architecture on AWS — frontend, backend, and database — with security best practices, high availability, and low latency. As a DevOps engineer you must choose the optimal option for each component: should the database run as a StatefulSet or as a managed cloud database, should the frontend be a Pod or S3 with CloudFront, and so on.**
- **How can you tell whether a subnet is public or private — what has to be in place?**
- **How is an end user able to reach an application running in Pods on private-subnet nodes?**
- **What is Route 53, and in what order does traffic actually flow when a user requests or submits something from the UI?**
- **Explain every component involved from the user's request in the UI to the request reaching the backend Pod, and how they connect to ensure inbound and outbound flow — including firewall, NACL, security groups, and route tables.**
- **If you used a Service of type LoadBalancer and the cluster is in a private subnet, how is it able to create a load balancer in a public subnet? Which control-plane component does that, and how does it get the access?**
- **Why did you choose EKS over ECS?**
- **How are you managing the cluster nodes?**
- **For your specific architecture, how many IP addresses across all components would be sufficient out of the available addresses in both subnets of your VPC?**
- **There is a DDoS attack on your cluster nodes or services consuming 100% of resources. What steps do you take to recover, and what do you put in place to prevent it in future?**
- **How are you handling high availability in your cluster, and why did you choose a specific feature over similar alternatives?**
- **Why does your cluster need a NAT gateway, and where must it be placed to work as intended?**
- **Write a script that finds a particular name in a file and replaces it with another word — and run it.**
- **Write a script that finds the first occurrence of a pattern in a file and extracts the full line containing it — and run it.**
- **Write a script that finds all files in the current directory and subdirectories modified more than 5 hours ago but not before today.**

**Round 2 — cloud DevOps architect**

- **Write a Python script to reverse a string without a loop, without slicing shortcuts, and without built-in functions or libraries.**
- **Write a Python script that takes an integer of at least two digits and reports whether it is divisible by only 3, only 5, or both — returning only the combined result when both apply. If divisible by neither, check whether it is prime; if it is not prime, return the list of all its divisors excluding 1 and itself.**
- **Draw and explain your current project's end-to-end architecture, including the measures you took for security and for complying with your SLA.**
- **How do you handle CI integration across dev, test, QA, staging, and production?**
- **Which branching strategy do you follow, and how did you wire it into the CI pipeline so pushed code deploys to the right environment cluster? Where exactly in the CI code did you handle deploying to dev, then QA, and so on to production, and how did you handle pull-request checks and approvals?**
- **What activities happen after deploying to each environment and before it is ready for the next one?**
- **Did you use AWS accounts, and how did you segregate environments within AWS?**
- **How is a `data` block different from a `resource` block in Terraform? Give a scenario where both are used together.**
- **A new integration requires a couple of Terraform-managed resources to be taken completely out of the Terraform lifecycle and handled manually. Propose an approach that leaves them untouched and undestroyed while making them independent.**
- **What is `taint` in Terraform? Give a scenario where you need it and explain how it works.**
- **What are Terraform workspaces, and what is the main requirement for using them?**
- **A configuration change to a Terraform resource caused brief downtime during apply. What might have caused it, how do you handle config changes in future for minimum downtime, and write the Terraform code that handles it.**
- **Explain the S3 lifecycle, and what the S3 storage classes are.**
- **Have you worked on CloudFront, and how did you use it to serve the front-end static code for the UI?**
- **What is the Kubernetes API? Can you connect to it with REST calls directly from an external application, the way `kubectl` connects to the endpoints exposed by the API server?**
- **If a recent deployment introduced a problem, how do you roll it back? Is it just `kubectl rollout undo`, and how does it know which image to revert to — does it read that from the image repository or somewhere else?**

**Round 3 — managerial plus technical**

- **Explain the use of these Linux commands: `finger`, `comm`, `netstat`, `jq`, `yq`, `at`, `atq`, `shuf`, `lsblk`, `less`, `last`, `nc`, `mtr`, `iftop`, `lsof`, `blkid`, `mkfs`, `nice`.**
- **Write a Python script that takes a single capital letter as input — rejecting lowercase and non-alphabetic input — then, from a given CSV-style file, finds the minimum, maximum, and sum of the numbers on the lines matching that letter, prints them, and then deletes those matched lines from the file.**
- **An application log is updating in real time and contains many IP addresses that attempted to connect. Write a Python script that returns all the unique IP addresses along with the total count of unique addresses.**
- **Write a three-stage Dockerfile using the pre-built images provided for each stage: stage one sets and copies environment config files, environment variables, and shell profiles such as `.bashrc` that already ship with the image; stage two uses those files, performs prerequisite tasks, and builds the code from the current directory; stage three uses the previous stage's output to build the image.**
- **Explain how image creation happens — what layers are, how they form, and what the final-stage image actually contains.**
- **Which steps or commands in a Dockerfile create intermediate images, and once the final image exists are those intermediate images still used?**
- **What is the difference between `CMD` and `ENTRYPOINT`? Explain with a scenario how and why you use both together.**
- **If a Dockerfile contains multiple `CMD` and `ENTRYPOINT` lines, will the build error? If not, how does Docker handle them?**
- **What is a publisher in Jenkins?**
- **What are executors in Jenkins, and how do they work under the hood?**
- **How did you set up SonarQube in your Jenkins pipeline, what are quality gates, and how did you set the threshold checks for code coverage using the developers' test reports?**
- **In an Ansible playbook, how do you pass the output of one task to the next — especially across different blocks, for example from the first block to the second, or from the fourth block to later tasks?**
- **If Services already route traffic to the right Pod, why do you need extra load-balancing capabilities such as host-based and path-based routing? What can a standalone Service not handle? For example, as a user browses various product details, how does the frontend fetch data from the right backend Pod, and how are the API calls to the backend and to the database handled?**
- **How does a real-time application such as a multiplayer game or a streaming service handle heavy concurrent user sessions without latency or delay?**
- **A live production application suddenly develops latency — requests that took 5 ms now take around 5 minutes. How do you troubleshoot, do a deep root cause analysis to find the exact source, and resolve it quickly given the application is critical?**
- **Write a PromQL expression that alerts if CPU usage is above 80% on any node.**
- **How would you alert if CPU usage stays above 90% for five minutes, but only when the number of running Pods is below five?**
- **What is the difference between a custom resource and a CustomResourceDefinition?**
- **Explain the end-to-end ELK stack setup in your current cluster.**
- **How does Kibana connect to Elasticsearch? Write the YAML snippet that handles that connectivity.**
- **What are operators in Kubernetes, and is an Elastic operator involved in how Elasticsearch runs?**
- **A MySQL operator runs in a Pod on one of your nodes. How is the database it manages different from a plain Pod started from a MySQL image via a Deployment? Beyond handling updates, version changes, lifecycle, vulnerabilities, and security, what further advantages does it give — explain with scenarios.**
- **If you must run exactly one MySQL database on every node in the cluster, how would you set that up using custom operators?**

## Example

```text
Sigmoid — DevOps Engineer, four reported interviews (~110 questions)

  SET 1  Coding + K8s basics (7 YOE)     7   reverse/palindrome/word count,
                                             ReplicaSet vs ReplicationController,
                                             control-plane failure
  SET 2  K8s + TF + log parsing (7 YOE) 15   write a readiness-probe Deployment
                                             to spec, liveness OK + readiness
                                             failing, hardcoded password in CI,
                                             log-alert script
  SET 3  Regional failure + design      13   LB region down, RDS failover on a
                                             budget, blue-green config switch,
                                             ASG and LB in different regions,
                                             longest substring
  SET 4  Three-round in-person          75   THE BIG ONE. Whiteboard 3-tier
                                             design with 11 counter-questions,
                                             architect round on Terraform
                                             lifecycle + K8s API, managerial
                                             round with 18 Linux commands,
                                             3-stage Dockerfile, PromQL,
                                             operators

THE MOST DEMANDING PROCESS IN THIS COLLECTION
  Set 4 is three in-person rounds where the architecture answer is attacked
  with eleven follow-ups, scripts must be WRITTEN AND EXECUTED, and the final
  round asks you to explain eighteen Linux commands by name. Expect five to
  six hours of interviewing.
```

```yaml
# Set 2's Deployment, exactly to spec — the readiness probe is the point.
apiVersion: apps/v1
kind: Deployment
metadata:
  name: space-alien-welcome-message-generator
spec:
  replicas: 1
  selector:
    matchLabels: { app: space-alien-welcome-message-generator }
  template:
    metadata:
      labels: { app: space-alien-welcome-message-generator }
    spec:
      containers:
        - name: httpd
          image: httpd:alpine
          readinessProbe:
            exec:
              command: ["stat", "/tmp/ready"]
            initialDelaySeconds: 10
            periodSeconds: 5
```

## Interview tips

- The LoadBalancer-from-a-private-subnet question is the sharpest in the whole set, and it names a component most candidates cannot. The answer is the **cloud controller manager** (on EKS, the AWS Load Balancer Controller or the legacy in-tree cloud provider): it watches Services of type LoadBalancer and calls the cloud provider's API to provision one. The key insight is that it does not need network access to a public subnet — it needs _IAM permission_ and a route to the AWS API endpoint, which it gets via IRSA and a VPC endpoint or NAT. Then say how it knows _where_ to put the load balancer: the public subnets are tagged `kubernetes.io/role/elb`, and the controller discovers them from those tags. Control plane calls an API, tags decide placement — that is the complete answer.
- "Liveness healthy but readiness failing" has an exact answer: the container keeps running because liveness is what triggers a restart, but the Pod is removed from the Service's EndpointSlice, so it receives **no traffic**. The Pod shows `Running` but `0/1 READY`. During a rolling update this also stalls the rollout, because the new replica never becomes ready. Say that this is the correct and desired behaviour — readiness gates traffic, liveness gates restarts — and that the classic misconfiguration is pointing both probes at the same endpoint, which turns a slow dependency into a restart loop. See [how liveness, readiness, and startup probes differ](../kubernetes/how-do-liveness-readiness-and-startup-probes-differ.md).
- The RDS-failover-on-a-budget question is excellent because the constraint rules out the obvious answer. You cannot afford a second writable database, so: promote the existing cross-region **read replica** to primary — you are already paying for it, and promotion is exactly what it is for — then repoint the application via a Route 53 record or a connection string held in Parameter Store rather than hardcoded, and accept the replication lag as your RPO because replication is asynchronous. Say the two caveats that show real experience: promotion is irreversible and breaks the replication chain, and the _application_ must be able to follow the endpoint change, which is why the endpoint belongs in configuration. Mention Aurora Global Database as the better-but-pricier option. See [running a highly available database on AWS](../aws-engineering/how-do-you-run-a-highly-available-database-on-aws.md).
- "ASG and LB in different regions" is a hard no, and the reason is the point: both are regional and a target group can only register targets inside its own VPC, so cross-region is impossible. The correct pattern is an ASG plus load balancer per region, fronted by Route 53 latency or failover routing, or Global Accelerator for anycast entry. Similarly, for "the LB's region goes down" — the load balancer itself is multi-AZ but single-region, so it goes with the region; only DNS or an anycast layer above it can fail over. Saying "regional service, so the failover has to live above it" answers both questions.
- Blue-green "exactly which configuration changes" wants a precise answer, not a description. In Kubernetes it is the **Service's label selector** — patch `spec.selector` from `version: blue` to `version: green`, which is atomic and instant. On AWS it is the **listener rule's target group** (or the weighted forward action) on the ALB. Say the mechanism by name and add that rollback is patching it back, which is why you keep the old version running for a soak window. See [deployment strategies](../devops-tools-and-automation/what-are-deployment-strategies.md).
- "Best strategy with only one Pod" is a trap: with a single replica you _cannot_ do a zero-downtime rolling update, because there is nothing to serve while the one Pod is replaced — unless you set `maxUnavailable: 0` and `maxSurge: 1`, which temporarily gives you two Pods. So the honest answer is that the strategy question is secondary to the replica count: run at least two replicas. If you truly must stay at one, `maxUnavailable: 0` with surge is the closest to zero downtime, and recreate is the honest choice if the workload cannot tolerate two instances at once — for example a singleton with an exclusive lock.
- `terraform taint` is asked twice across sets 2 and 4, and the currency answer matters: it marked a resource for replacement on the next apply, and it is **deprecated** in favour of `terraform apply -replace=<address>`, which is better because the replacement appears in a reviewable plan rather than being a hidden state mutation. Give the scenario: an instance that is running but misbehaving — configuration drifted, a bad bootstrap — where you want a clean rebuild without changing any code. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- The "take resources out of the Terraform lifecycle" question in set 4 is the one people answer wrongly with `prevent_destroy`. That only makes the apply _fail_. The correct answer is `terraform state rm` — or a `removed` block in current Terraform, which is the reviewable declarative form — so Terraform forgets the resource entirely while the infrastructure keeps running untouched. Then, if the configuration still needs to _reference_ those resources, replace the `resource` blocks with `data` sources, which read without owning. That `resource`-to-`data` swap is the elegant half of the answer, and it also answers the `data`-versus-`resource` question in the same round.
- The downtime-during-apply question has a specific fix and they ask you to write it: the cause is an in-place update that the provider must implement as destroy-then-create — changing an immutable field — so the resource disappears before its replacement exists. The fix is `lifecycle { create_before_destroy = true }`, which inverts the order. Write it out, and add the caveats: it needs unique names, since the old and new coexist briefly, and it propagates to dependencies. Mention `ignore_changes` for fields mutated outside Terraform.
- The `kubectl rollout undo` follow-up is genuinely good: it does **not** read the image repository. A Deployment keeps previous **ReplicaSets** (bounded by `revisionHistoryLimit`), each holding the full Pod template of that revision — so rollback scales the old ReplicaSet back up. Say `kubectl rollout history` shows the revisions and `--to-revision` targets one, and note the two gotchas: `revisionHistoryLimit: 0` destroys your rollback ability, and rolling back the Deployment does _not_ roll back a ConfigMap, Secret, or database migration — which is why configuration should be versioned alongside the image.
- The Kubernetes API question expects a yes with detail: the API server is a REST API over HTTPS, so any client can call it — `curl -H "Authorization: Bearer $TOKEN" https://<api>/api/v1/namespaces/default/pods` — because `kubectl` is only a convenience wrapper that reads `kubeconfig` and formats the JSON. Say that the token comes from a service account, that RBAC governs the call the same way regardless of client, and that this is exactly how controllers and operators work: they watch the API with the `watch` verb rather than polling.
- The operator questions in round 3 are the deepest, and the MySQL comparison is the one to prepare. A Deployment running a MySQL image gives you a process; an operator gives you _operational knowledge encoded as software_. Name the scenarios: automated primary election and failover when the primary Pod dies, consistent backups with point-in-time recovery, adding a replica with correct initial data seeding rather than an empty volume, ordered version upgrades that respect replication compatibility, schema-aware scaling, and reconciliation that restores a member after a node loss — none of which a Deployment can do, because Kubernetes only knows "keep N Pods running". For the "one MySQL per node" follow-up, the mechanism is a **DaemonSet** — or an operator whose custom resource generates one — plus per-node local storage; and say why you would question the requirement, since one database per node is an unusual topology that usually indicates a caching or sidecar need instead. Then for custom resource versus CRD: the CRD _defines_ the new kind and registers it with the API server, the custom resource is an _instance_ of that kind, and neither does anything without a controller watching it. See [what container orchestration is and why you need it](../container-orchestration-advanced/what-is-container-orchestration-and-why-do-you-need-it.md).
- The two PromQL questions have writable answers, and the second is the discriminator. For node CPU above 80%: `100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80`. For the compound alert, the sustained part is `for: 5m` in the alerting rule rather than anything in the expression, and the Pod-count condition is joined with `and on()` against a second query — something like `... > 90 and on() (count(kube_pod_status_phase{phase="Running"}) < 5)`. Say that `for: 5m` is what makes it sustained and that `and on()` is how you combine unrelated series — those two facts are the answer. See [writing effective PromQL queries and Alertmanager rules](../monitoring-and-logging/how-do-you-write-effective-promql-queries-and-alertmanager-rules.md).
- "Why do you need path and host routing if Services already route to Pods?" is a layering question. A Service load-balances across the Pods of _one_ workload at layer 4 — it cannot inspect a URL, so it cannot send `/products` to one service and `/checkout` to another, cannot terminate TLS for multiple hostnames, and cannot rewrite paths or do header-based canaries. That is what an Ingress or Gateway provides at layer 7, and without it you would need a separate cloud load balancer per Service, which is expensive and unmanageable. Then answer the product-browsing example concretely: the browser calls one hostname, the ingress routes by path to the correct backend Service, that Service load-balances to a backend Pod, and the Pod queries the database through its own ClusterIP Service or a managed endpoint using credentials from a Secret. See [exposing an application in Kubernetes](../kubernetes/how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md).
- The 5 ms-to-5-minutes latency RCA is the flagship scenario, so answer with a method that narrows: confirm and scope it first — which endpoints, which regions, all users or a cohort, and check p50 against p99 because a five-hundred-fold jump suggests queuing or a timeout rather than gradual load; then check what changed, since a deploy, config change, or scaling event at that timestamp is the most likely cause; then walk the request path with traces to find which span owns the added time; then check saturation at each tier — connection pool exhaustion, database locks or a missing index after a data-volume change, thread pool, queue depth, DNS, and disk or burst-credit exhaustion. Mitigate before you finish diagnosing — roll back, scale the bottleneck, or shed load — and only then complete the RCA. Say that a jump of that magnitude is almost always a queue forming behind a resource that has hit a hard limit. See [debugging a Linux performance problem from first principles](../linux-administration/how-do-you-debug-a-linux-performance-problem-from-first-principles.md).
- The hardcoded-password question wants CI _and_ incident response. Detection: a secret scanner such as Gitleaks or `trufflehog` as a pre-commit hook and as a blocking CI job, plus push protection at the forge. Response, in order: revoke and rotate the credential **first**, because the secret is compromised the moment it is pushed; then review logs for use during the exposure window; then rewrite history with `git filter-repo` or BFG and force-push; then prevent it recurring. Emphasise that rewriting history first is the classic mistake — the key stays valid while you tidy up. See [preventing and handling secret leaks in CI/CD](../cicd/how-do-you-prevent-and-handle-secret-leaks-in-ci-cd-pipelines.md).
- ReplicaSet versus ReplicationController is a legacy-versus-current question: ReplicationController is the original object and ReplicaSet replaced it, the functional difference being that ReplicaSet supports **set-based selectors** (`in`, `notin`, `exists`) while ReplicationController only did equality-based matching. Add that you should use neither directly — a Deployment manages ReplicaSets for you and provides rolling updates and rollback.
- For the eighteen Linux commands in round 3, group them so you sound organised rather than recalling at random: **users and sessions** — `finger`, `last`; **files and text** — `comm`, `less`, `shuf`, `jq`, `yq`; **scheduling and priority** — `at`, `atq`, `nice`; **disks and filesystems** — `lsblk`, `blkid`, `mkfs`; **network** — `netstat`, `nc`, `mtr`, `iftop`; **open files and sockets** — `lsof`. Add the modern replacements where they exist, since that shows currency: `ss` supersedes `netstat`, and `mtr` combines `ping` and `traceroute`. See [basic Linux commands](../linux-administration/what-are-the-basic-linux-commands-every-devops-engineer-should-know.md).
- The multiple-`CMD`-and-`ENTRYPOINT` question has a precise answer: the build **succeeds with no error**, and only the **last** `CMD` and the last `ENTRYPOINT` take effect — all earlier ones are silently ignored. Say that this silent-override behaviour is exactly why it is a bug worth catching in review. Then the conjunction scenario they asked for: `ENTRYPOINT ["python", "app.py"]` with `CMD ["--port", "8080"]` makes the arguments overridable at `docker run` while the executable is fixed. For the intermediate-images question: each instruction creates a layer, and multi-stage builds produce intermediate stages that exist during the build and are **not** part of the final image — the final image contains only the layers copied into the last stage, which is precisely why multi-stage builds are the answer to image size. See [what a Dockerfile is](../docker/what-is-dockerfile.md) and [reducing Docker image size and build time](../docker/how-do-you-reduce-docker-image-size-and-build-time.md).
- The Ansible task-output question has an exact mechanism: `register` a task's result into a variable, which is then available to every later task in the same play — including across `block` boundaries, because registered variables are play-scoped host facts, not block-scoped. Say that explicitly, since the question implies blocks isolate them. Add `set_fact` for values you want to persist and name deliberately, `hostvars` to read another host's registered value, and that `register` inside a loop produces a `results` list you index into. See [what Ansible is](../infrastructure-as-code/what-is-ansible.md).
- The IP-address-budget question in set 4's whiteboard round is unusual and worth thinking through out loud: AWS reserves five addresses per subnet, the VPC CNI assigns an IP per **Pod** (not per node), so you size from expected Pod count plus node count plus load balancer ENIs plus headroom for a rolling update's surge — and say that this is why EKS subnets are commonly `/20` or larger, and why prefix delegation or a secondary CIDR is the fix when you run short. Showing you know Pods consume VPC addresses is the whole point.
- Jenkins executors and publishers are small precise questions: an executor is a slot on a node that runs one build at a time, so a node with four executors runs four concurrent builds — and building on the controller starves it, which is why you use agents. A publisher is a post-build step that reports or distributes results — JUnit reports, artefact archiving, coverage publishing, notifications — running after the build steps complete. See [Jenkins pipelines](../cicd/what-are-jenkins-pipelines.md).
- Round 4 asks you to _execute_ the scripts, so practise typing them, not describing them. `sed -i 's/old/new/g' file` for find-and-replace, `grep -m1 'pattern' file` for the first matching line, and `find . -type f -mmin +300 -mmin -1440` for the modified-more-than-5-hours-but-today window — noting `-mmin` is minutes, which is what makes that constraint expressible. See [writing a production-grade Bash script](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md).

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
