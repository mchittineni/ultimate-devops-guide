---
title: "What DevOps interview questions does Wipro ask?"
id: 392
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - wipro
  - kubernetes
  - infrastructure-as-code
  - configuration-management
  - cicd
  - api-gateway-and-service-mesh
  - aws-engineering
  - devsecops
  - cloud-native-architecture
---

# What DevOps interview questions does Wipro ask?

## Questions

### Round set 1 — deployment scenarios and customer handling

- **A file is used by two customers and must be deployed both into a Kubernetes cluster and on-premises. How do you do that?**
- **What is the problem with using a very large image in a Dockerfile?**
- **How do you deploy an application to a Kubernetes cluster — the application deployment only, so explain the CD part.**
- **A secret is stored in Vault inside a Pod and that Pod is down. How do you troubleshoot?**
- **How is Azure Key Vault integrated into CI/CD?**
- **What do you do if an application is down?**
- **A service has been down for more than two weeks and the customer is asking for an update. What do you tell the customer, how do you troubleshoot it, and what steps do you take so it cannot happen again?**
- **What goes inside a Dockerfile?**
- **What goes inside a `deployment.yaml` or a Helm chart?**

### Round set 2 — automation, APIs, and Ansible at scale (7 YOE)

- **Elaborate on your experience automating and optimising deployment across large infrastructure using AWS, Terraform, and Ansible.**
- **Describe your experience building CI/CD pipelines and using Docker, Grafana, and Prometheus — and a project where those skills were critical.**
- **With multi-tenant applications, how do you enforce tenant isolation at the API layer?**
- **Clients are reporting 504 Gateway Timeout errors. Describe your approach to debugging that.**
- **How would you implement optimistic locking on a RESTful update endpoint to avoid lost updates?**
- **If you had to run pre-task checks, main tasks, and post-task validation for patch automation, how would you structure your RedHat automation and virtualisation scripts?**
- **Describe an approach to automating the secure decommissioning of VMs, including data shredding.**
- **To keep very large Ansible inventories clear, what naming conventions should you follow for groups and hosts?**
- **Describe the structure and advantages of using an Ansible role to manage a three-tier web application — and what do you mean by a three-tier web application?**
- **If you have custom plugins that several roles depend on, how do you manage them?**
- **What is a cloud-agnostic strategy, and how do you use conditionals to make a role cloud-agnostic across AWS, Azure, and GCP?**
- **How would you structure a multi-stage pipeline in GitHub Actions that builds, tests, and deploys a containerised application to Kubernetes?**
- **How would you parameterise a workflow so downstream jobs know which environment to deploy to?**
- **What are the security implications of storing Kubernetes Secrets in etcd without encryption?**
- **How does Python's global interpreter lock affect multi-threaded web service performance, and what alternatives exist?**
- **How would you implement feature toggles in a deployment pipeline?**
- **How would you schedule a task to run every 15 minutes on Windows with PowerShell and on Linux with cron?**
- **How do you reduce the risk of miscommunication when multi-lingual stakeholders are involved in email threads?**

### Round set 3 — microservices and service mesh (4 YOE)

- **You have a monolith that must become microservices. What prerequisites would you ask of the development and technical teams before starting?**
- **When designing a microservices infrastructure, which technologies and components — load balancer, service mesh, Kubernetes — would you bring in, and how would you design the estate?**
- **With many services in a service mesh, how do you decide how many control planes and data planes you need?**
- **What security measures and policies should be in place when using a service mesh?**
- **Since some service mesh features are available through other tools, is it worth the burden of installing Istio?**
- **Is a service mesh always needed, or are alternative tools sometimes enough?**
- **How do you handle service discovery when moving from a monolith to microservices?**
- **You have a Kubernetes cluster with Pods running, but hitting the URL returns HTTP errors — 403, 404, or 503. What are your troubleshooting steps?**
- **In your four-year career, what is the biggest achievement you are most satisfied with? And do achievements always need to be big and complex, or can they be simple improvements?**

### Round set 4 — Terraform and AWS focus (4 YOE)

The candidate noted the interviewers were mainly looking for Terraform and AWS experience.

- **Which Terraform commands do you know, and what are the different types of module and why are they used?**
- **How do you manage the state file, and what is the command to use S3 native locking?**
- **Explain the process by which you receive a request to create cloud resources.**
- **Have you come across a scenario where you used `terraform destroy`?**
- **Explain your Terraform modules.**
- **Explain your CI/CD pipeline, and what policies do you apply to it?**
- **What is the difference between GitHub Actions and Argo CD?**
- **What is the difference between a NAT gateway and an internet gateway?**
- **What is a route table, and where is it placed?**
- **What types of alert are there in Dynatrace, and did you install the OneAgent in your applications?**
- **Explain your roles and responsibilities.**

### Round set 5 — troubleshooting breadth (9 YOE)

- **Brief me on yourself, your project, and your responsibilities.**
- **An application on EC2 behind a load balancer suddenly becomes unavailable. How do you troubleshoot?**
- **AWS billing increased suddenly. How do you identify the cost?**
- **A developer asks for an EC2 instance for local deployment. How do you provide it, and what instance type would you create?**
- **A Pod is going into `CrashLoopBackOff`. How do you troubleshoot?**
- **The Kubernetes deployment succeeded but you cannot access the application externally. How do you troubleshoot?**
- **When a Kubernetes node fails, what happens?**
- **From a production perspective, what should you configure in a Pod specification?**
- **What is Git, why do we use it, and what is a branching strategy?**
- **How do you write YAML for a CI/CD pipeline from scratch to test and deploy from dev to UAT?**
- **What is Maven, and explain its repositories.**
- **You must deploy an application to 100 servers using Ansible. How do you do it?**
- **Docker containers stopped suddenly after starting. How do you troubleshoot?**
- **A Jenkins pipeline deployment failed in production but works in dev. How do you troubleshoot and fix it?**
- **What is Argo CD and why do we use it? And what is GitOps?**
- **In AWS, how do you configure subdomains registered with an external registrar?**

## Example

```text
Wipro — DevOps Engineer, five reported interviews (~76 questions)

  SET 1  Deployment + customer handling      9   dual-target deploy (K8s +
                                                on-prem), Vault secret in a
                                                dead Pod, service down 2 weeks
  SET 2  Automation + APIs (7 YOE)          18   tenant isolation at the API,
                                                504 debugging, optimistic
                                                locking, VM decommissioning
                                                with data shredding, GIL,
                                                unencrypted etcd Secrets
  SET 3  Microservices + mesh (4 YOE)        9   monolith prerequisites, how
                                                many control/data planes, is
                                                Istio worth it (asked twice),
                                                403/404/503 triage
  SET 4  Terraform + AWS (4 YOE)            11   S3 native locking, module
                                                types, GH Actions vs Argo CD,
                                                Dynatrace alerts
  SET 5  Troubleshooting breadth (9 YOE)    16   LB target unavailable, bill
                                                spike, CrashLoopBackOff, node
                                                failure, 100-server Ansible
                                                deploy, works-in-dev-fails-in-prod

WIPRO'S RANGE IS THE WIDEST HERE
  Five interviews spanning 4 to 9 years, and the topics barely overlap. Set 2
  asks about the Python GIL and optimistic locking; set 5 is pure operational
  triage. There is no single "Wipro question set" — prepare for the round you
  are actually in.
```

## Interview tips

- The two-week-old outage question in set 1 is the most revealing in the whole collection, because it is testing whether you can be trusted in front of a customer. Do not answer it as a technical problem. Say what you tell the customer: acknowledge the duration honestly rather than minimising it, state the current impact and any workaround, give what you know and what you do not, commit to a next update _time_ rather than a fix time you cannot guarantee, and name an owner. Then the troubleshooting: if it has been broken two weeks, the fault is the _process_ — no alerting caught it, or an alert fired and nobody owned it, or it was triaged and dropped. So you check monitoring coverage first, then the change that coincided with the breakage, then work the technical fault. And the prevention: an SLO with alerting on the user-facing symptom so it cannot silently stay broken, an on-call rotation with clear ownership, and a rule that no incident is closed without an action item tracked to completion. Saying "two weeks means the detection failed, not just the service" is the answer they are listening for. See [incident severity levels](../incident-management/what-are-incident-severity-levels.md) and [post-mortem analysis](../incident-management/what-is-post-mortem-analysis.md).
- The Vault-secret-in-a-dead-Pod question has a specific insight: if the Pod is down, the secret is not the problem — the Pod is, and very often the _reason_ the Pod is down is that it could not get the secret. So debug the Pod, and check the secret path: `kubectl describe pod` and `logs --previous`; whether the Vault Agent injector's init container failed, which stops the main container from ever starting; whether the Kubernetes auth role and service account binding are correct; whether the Vault token or lease expired and renewal failed; whether Vault itself is sealed or unreachable, or the network policy blocks it; and whether the secret path or policy changed. Say that a sealed Vault or an expired lease presents exactly as an application crash loop, which is why you check the injector's logs before the application's.
- Tenant isolation at the API layer in set 2 is a strong senior question. Answer in layers: authenticate to a tenant-scoped identity so the tenant ID comes from a validated token claim and **never** from a request parameter or header a client can forge — that is the single most important point; authorise every data access against that claim, ideally enforced centrally in middleware or a policy engine rather than repeated in each handler; scope data with row-level security, a per-tenant schema, or separate databases depending on how strong the isolation must be; rate-limit and quota per tenant so one cannot starve another; and make tenant ID a required dimension in logs and metrics so you can prove isolation and debug per tenant. Say that the classic breach is an object-reference check that trusts an ID in the path, so every query must be filtered by tenant server-side.
- The 504 debugging question needs the meaning of the code first: a 504 comes from a _proxy or gateway_ that gave up waiting on an upstream — so the gateway is healthy and something behind it is slow or unresponsive. Then work the chain: compare the gateway's timeout against the backend's actual p99 latency, because a 504 is often just a timeout set below the slow path; check whether the backend has healthy targets at all; look for connection-pool or thread-pool exhaustion, a slow database query, or a downstream dependency timing out; check whether it correlates with a deploy or a traffic spike; and distinguish 504 from 502 (bad upstream response) and 503 (no capacity), because that triple tells you where to look. Say you would raise the timeout only after establishing why the backend is slow, never as the fix.
- The unencrypted-etcd-Secrets question has a precise answer: Kubernetes Secrets are only **base64-encoded**, not encrypted, so without encryption at rest they sit in plain text in etcd — meaning anyone with read access to etcd, to an etcd snapshot, or to the disks or backups holding it can read every secret in the cluster, and etcd backups are frequently less protected than the cluster itself. Then the mitigations: enable `EncryptionConfiguration` at rest, ideally with a KMS provider so the key lives outside the cluster; lock down etcd with mutual TLS and no direct access; restrict Secret read permissions with RBAC (many people forget that `get secrets` on a namespace exposes everything in it); and prefer an external store via the External Secrets Operator or the Secrets Store CSI driver so the sensitive value never lands in etcd at all. See [managing secrets in CI/CD pipelines](../devsecops/how-do-you-manage-secrets-in-ci-cd-pipelines.md).
- The service mesh questions in set 3 are asked twice in different words — "is Istio worth the burden" and "is a mesh always needed" — which means the interviewer wants a candidate willing to say **no**. Give the decision rule: a mesh earns its cost when you need mutual TLS between many services without touching application code, uniform retries, timeouts and circuit breaking, fine-grained traffic shifting for canaries or mirroring, and per-hop telemetry across dozens of services. It does not earn its cost for a handful of services, where an ingress controller plus a client library plus NetworkPolicies gets you most of the value — and the cost is real: a sidecar per Pod, added latency, extra CPU and memory, another control plane to upgrade, and a much harder debugging story. Mention ambient or sidecar-less modes as the direction that reduces that overhead. On the control-plane and data-plane sizing question: the data plane scales with your workloads (one proxy per Pod, so it is not a choice), while the control plane is sized for the number of proxies it must configure and is typically one per cluster, replicated for availability — with a multi-cluster mesh needing a decision between shared and per-cluster control planes based on failure isolation and latency. See [what Istio is](../container-orchestration-advanced/what-is-istio.md).
- The 403/404/503 triage question is excellent because each code points somewhere different, and saying so is the answer. **403** means something authorised and refused — a WAF rule, an ingress annotation, an authentication requirement, or an S3/bucket policy — so it is not a routing failure. **404** means you reached a server that has no such route — usually an ingress path rule not matching, a missing rewrite annotation, or the application's base path differing. **503** means no healthy backend — empty Service `Endpoints`, failing readiness probes, or the ingress controller having nothing to forward to. Say that the fact you get _any_ HTTP response proves DNS and the load balancer are fine, which immediately eliminates half the search space. See [exposing an application in Kubernetes](../kubernetes/how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md).
- The monolith-to-microservices prerequisites question in set 3 is asking what you would demand _before_ agreeing to start, so answer like an engineer protecting a project: clear service boundaries derived from business domains rather than from the existing code layout; an understanding of the data model and which transactions currently span would-be boundaries, because a transaction crossing a boundary is the hardest problem; API contracts and versioning agreed; observability instrumentation in place first, since you cannot debug a distributed system you cannot trace; a test strategy including contract tests; the team's operational readiness and on-call model; and an agreed migration order using the strangler-fig pattern rather than a big-bang rewrite. Say that if nobody can name the service boundaries, the project is not ready to start. See [what container orchestration is and why you need it](../container-orchestration-advanced/what-is-container-orchestration-and-why-do-you-need-it.md).
- S3 native locking in set 4 is a currency question with an exact answer: Terraform now supports S3-native state locking via `use_lockfile = true` in the `backend "s3"` block, which writes a `.tflock` object beside the state — removing the long-standing need for a separate DynamoDB table. Say that DynamoDB-based locking still works and remains common, and that `terraform force-unlock <LOCK_ID>` is the break-glass you use only after confirming no apply is running. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- GitHub Actions versus Argo CD is a category comparison, not a feature one — say that first. Actions is a general-purpose CI/CD engine that _pushes_ changes outward and stops once the job ends; Argo CD is a Kubernetes controller that _pulls_ desired state from Git and continuously reconciles the cluster to match, so it detects drift, self-heals, shows per-resource sync status, and gives one-click rollback — and it means no cluster credentials live in CI. Then say the usual architecture: Actions for build, test, scan, and publishing the image; Argo CD for the deployment half. See [GitOps](../devops-tools-and-automation/what-is-gitops.md) and [Argo CD](../devops-tools-and-automation/what-is-argocd.md).
- The route-table question has a precise answer that catches people out: a route table is **associated with subnets**, not placed "in" one — and a subnet is public or private _because of its route table_. A public subnet's table sends `0.0.0.0/0` to an internet gateway; a private subnet's sends it to a NAT gateway or nowhere. Every VPC has a main route table used by any subnet without an explicit association, and local routes between subnets are automatic. That pairs directly with the NAT gateway versus internet gateway question: the internet gateway gives bidirectional public access, while the NAT gateway lives in a _public_ subnet and gives private subnets outbound-only access via source NAT. See [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md).
- The "works in dev, fails in production" Jenkins question in set 5 should be answered by enumerating what actually differs between environments, because the code is the same: credentials and their scope, environment variables and config, network reachability and firewall rules, the agent and its installed tooling, resource limits, data volume and therefore query performance, approval or change gates, and whether production is running the same artefact or was rebuilt. Say you would diff the two builds' console logs and the two environments' configuration first, and that the durable fix is promoting one immutable artefact rather than rebuilding per environment — because rebuilding is how the environments diverge in the first place.
- For the 100-server Ansible deployment, give the mechanics and the safety: an inventory (ideally dynamic, from the cloud provider) grouped by role and environment, a role rather than a flat playbook, then the two directives that matter — `serial` for a batched rolling deployment so you do not take all hundred down at once, and `max_fail_percentage` so the run halts if a batch fails. Add `forks` for parallelism, `--limit` for targeting, `--check` and `--diff` for a dry run, and handlers so services restart only when configuration actually changed. Say that a rolling batch with a failure threshold is what turns a risky mass deployment into a safe one. See [what Ansible is](../infrastructure-as-code/what-is-ansible.md).
- Optimistic locking on a REST endpoint is a development question with a clean answer: give each resource a version — a version column or an `ETag` — return it on `GET`, require the client to send it back on `PUT` or `PATCH` via `If-Match`, and have the update succeed only if the stored version still matches, returning **409 Conflict** (or 412 Precondition Failed) if it does not. So the client is told to re-read and retry rather than silently overwriting someone else's change. Say why it is called _optimistic_: no lock is held, you simply detect the collision at write time — which scales far better than pessimistic locking for a web API.
- The GIL question needs the mechanism and the correct alternatives: CPython's global interpreter lock allows only one thread to execute Python bytecode at a time, so **CPU-bound** multi-threading gains nothing — but I/O-bound work still benefits, because the lock is released during blocking I/O. Alternatives: `multiprocessing` or a pre-fork server such as Gunicorn with multiple workers for CPU-bound parallelism, `asyncio` for high-concurrency I/O, offloading hot paths to C extensions or NumPy which release the GIL, or another runtime. Mention that recent CPython work on a free-threaded build is changing this. Say that for a typical web service the practical answer is multiple processes, one per core.
- The secure-VM-decommissioning question is unusual and worth structuring: verify nothing still depends on it, snapshot or export any data that must be retained under a retention policy, revoke its credentials and remove it from inventory, monitoring, DNS, and load balancer targets, then destroy the data — and here name the honest technical point: on cloud block storage you cannot physically shred a disk you do not own, so you rely on the provider's cryptographic erasure, which is why the real control is **encrypting the volume with a customer-managed key and destroying the key**. On-premises, that is where overwrite tools or physical destruction apply. Finish with the audit trail and a certificate of destruction if compliance requires it.
- Set 4's "explain the process by which you receive a request to create cloud resources" is a process question, not a technical one, and it is a chance to sound like a platform engineer: a ticket or pull request with the requirement, review against standards for naming, tagging, sizing, and cost, the change expressed as IaC in a pull request, a plan reviewed and approved, applied from CI, then handover with monitoring and ownership recorded. Say that "no resource is created by hand" is the rule the process exists to enforce.
- The large-image question in set 1 should list consequences rather than just "it is slow": longer builds and pushes, slower Pod start because the image must be pulled on every new node (which directly hurts autoscaling responsiveness), more registry storage and transfer cost, a larger attack surface with more packages to patch, and node disk pressure leading to image garbage collection and evictions. Then the fixes: multi-stage build, minimal or distroless base, cleaning caches within the same layer, and a `.dockerignore`. See [reducing Docker image size and build time](../docker/how-do-you-reduce-docker-image-size-and-build-time.md).
- The dual-target deployment question — same file into Kubernetes and on-premises — is best answered by separating the artefact from the delivery: build one versioned artefact, then deliver it two ways from the same source of truth. For Kubernetes, a ConfigMap or a mounted volume rendered from a Helm value or a Git-tracked manifest; for on-premises, an Ansible role or a pull-based agent inside that network so no inbound access is needed. Say that the file's content must come from one place — a repository or a config service — or the two environments will drift, which is the actual risk the question is probing.
- The multi-lingual stakeholder question is a genuine communication question, so answer it seriously: write short, plain sentences and avoid idiom and abbreviation; lead with the decision or ask rather than burying it; use structure — numbered points, explicit owners, explicit dates in unambiguous format; confirm understanding by restating agreed actions in a summary rather than assuming; and move anything complex or contentious to a call, then follow up in writing. Say that you never rely on tone to carry meaning across a language barrier.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[How do you integrate SonarQube and quality gates into a pipeline?]] (`#458`): [How do you integrate SonarQube and quality gates into a pipeline?](../cicd/how-do-you-integrate-sonarqube-and-quality-gates-into-a-pipeline.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
