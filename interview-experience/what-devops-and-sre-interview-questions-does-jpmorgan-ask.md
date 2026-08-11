---
title: "What DevOps and SRE interview questions does JPMorgan ask?"
id: 343
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - jpmorgan
  - kubernetes
  - azure-engineering
  - aws-engineering
  - infrastructure-as-code
  - site-reliability-engineering
  - cicd
  - monitoring-and-logging
  - backup-and-disaster-recovery
---

# What DevOps and SRE interview questions does JPMorgan ask?

## Questions

### Round set 1 — application-plus-platform round

**Round 1 — Spring Boot, security, and AWS**

- **Explain the project you are currently working on.**
- **Which Spring Boot starters have you used?**
- **How have you implemented transaction management?**
- **How do you connect to two databases, and how do you guarantee rollback when an exception is thrown?**
- **How do you manage code coverage in your project?**
- **How do you load test the application?**
- **How have you implemented security in your project?**
- **Explain the Okta integration for identity and access management.**
- **How do you secure internal communication between microservices?**
- **How do you implement a retry mechanism for a failed API call?**
- **How do you implement blue-green deployment in your project?**
- **How do you deploy an application to AWS?**
- **What is serverless on AWS, and how are you using it?**
- **How would you handle the case where the payment succeeds but the order or shipping service fails?**
- **Using streams, build a map of duplicate colours and their counts from a list.**
- **Remove duplicates from that list of colours to produce a unique list.**
- **You have two candles and need to measure exactly 45 minutes. You may not cut or measure them.**

**Round 2 — cloud provisioning and messaging**

- **How are you provisioning your AWS services?**
- **How do you provision container-based services for microservice deployment?**
- **Which database services did you provision alongside the application?**
- **What is the primary difference between ECS and EKS?**
- **Where do you define autoscaling parameters?**
- **What do you know about serverless architecture, and what is serverless deployment on AWS?**
- **How do you reduce cold starts in Lambda?**
- **What is an HPA?**
- **What is a region and what is an availability zone?**
- **How do you monitor the health of your microservices?**
- **How do you enable Spring Boot Actuator, and are its endpoints reachable without authentication?**
- **Have you worked with Kafka or another messaging service?**
- **Have you used serialisation or deserialisation frameworks, and where do you register the Avro schema you create?**
- **Have you used Java concurrency APIs, and how do you combine the responses of three separate API calls?**
- **What is active-active, and how does active-passive differ from it?**
- **Find all pairs in an array that sum to a specific number.**

**Manager round**

- **Tell me about your previous experience, and any recently challenging tasks in your project.**
- **How do you deal with high-pressure situations or several critical deadlines at once?**
- **If your lead or a team member is not technically strong or behaves poorly, how do you handle it and keep working as a team?**
- **What do you do in your free time or at weekends?**

### Round set 2 — Senior DevOps Engineer, Azure scenarios

- **You deployed an application to AKS and it fails health checks intermittently. How do you debug that end to end?**
- **In a canary deployment to production, half the traffic returns 502 and the rest succeeds. Walk me through your troubleshooting.**
- **The CI/CD pipeline takes 40 minutes to deploy a small change. How would you optimise it?**
- **One Pod shows high CPU usage but the logs look clean. What do you do next?**
- **Design a highly available logging system for more than 100 microservices across three regions. Which tools and what architecture?**
- **A production application works for internal users but returns 403 for external ones. How do you isolate that?**
- **How do you achieve secure, dynamic secret rotation in Azure DevOps pipelines?**
- **How would you use Azure Application Gateway with a WAF for a sensitive banking application?**
- **During an Azure deployment you get intermittent DNS resolution failures. What could cause that?**
- **A user reports 10-second delays every 15 minutes on an application in AKS, with no code changes. How do you begin root cause analysis?**
- **Jenkins jobs fail randomly at the artefact upload step. Which layers would you check?**
- **How would you set up automated rollback in Kubernetes for a failed deployment?**
- **Design a cost-optimised architecture for an internal reporting application that runs nightly and retains logs for three years.**
- **How do you handle zero-downtime database migrations in a distributed application?**
- **What is your approach to disaster recovery for stateful applications running in containers?**
- **An Azure Function is being throttled. How do you detect that and fix it?**
- **Define a plan for blue-green deployment with rollback on Azure using Terraform and pipelines.**
- **How would you monitor end-to-end SLA across the services in a payments pipeline?**
- **How do scaling strategies differ for compute-intensive versus I/O-intensive workloads on Azure?**
- **Your production pipeline is blocked on missing approvals and the stakeholders are unreachable. What do you do?**

### Round set 3 — DevOps/SRE (5 YOE)

- **What is your strongest area in DevOps and SRE, and which technologies do you want to focus on next?**
- **Your application runs on EC2 instances in a public subnet. How would you migrate it to a private subnet with no downtime — the complete approach — and how would you roll back if it does not work?**
- **Two Pods cannot communicate. There are no errors in logs or events and both Pods look healthy. How do you troubleshoot and restore communication?**
- **A Pod's liveness or readiness probe is failing. How do you troubleshoot it?**
- **Besides Actuator health-check endpoints, what other checks can Kubernetes probes perform?**
- **An application has a single replica and you perform a rolling restart. Will there be downtime? Explain the sequence of events during the Pod restart, step by step.**
- **An application has two replicas. During a rollout the first Pod is replaced successfully, but the second enters `CrashLoopBackOff`. At that moment, does the load balancer route traffic to the new Pod, the old Pod, or both? Explain.**
- **Just as you gate images on code quality and OWASP checks, what mechanisms in Terraform prevent insecure infrastructure changes — for example someone opening a security group to `0.0.0.0/0`?**
- **How would you handle Terraform state for a team? Answer all three parts: store the state securely, ensure only one person can modify it at a time, and ensure it cannot be tampered with.**
- **You join a company where a large production estate was built by hand and the engineers who built it have left. How do you bring it under Terraform management? Walk me through the plan.**
- **Are you aware of the recent AWS and Azure outages? What were your takeaways?**
- **If an entire region goes down — and even a multi-cloud setup suffers outages — how do you guarantee your data is not lost? What backup and recovery strategies would you use?**
- **Which components or agents are typically installed alongside Prometheus, and what does each one do?**
- **In an EFK or ELK stack, what does each component do, how does the pipeline work overall, and how do filtering and indexing work inside Elasticsearch?**
- **Do you have any questions for me?**

## Example

```text
JPMorgan — DevOps / SRE, three reported interviews (~79 questions)

  SET 1  App + platform (3 rounds)    37   Spring Boot, Okta, saga/payment
                                           failure, ECS vs EKS, Lambda cold
                                           starts, Avro registry, Java streams,
                                           two-candle puzzle, manager round
  SET 2  Senior DevOps, Azure         20   ALL SCENARIOS. AKS flaky health
                                           checks, canary 502s, 40-min pipeline,
                                           403 external only, 10s delay every
                                           15 min, blocked approvals
  SET 3  DevOps/SRE (5 YOE)           15   public->private migration + rollback,
                                           2 pods can't talk, 1-replica rolling
                                           restart, 2-replica rollout with
                                           CrashLoopBackOff, Terraform policy
                                           gates, manual estate -> Terraform

JPMORGAN'S SIGNATURE
  Set 2 contains no definitions at all — 20 out of 20 are "here is a broken
  production system, what do you do". This is the most scenario-heavy
  employer in the collection. Prepare diagnostic METHOD, not facts.
```

## Interview tips

- The two-replica rollout question has an exact answer and it is the best discriminator in set 3: traffic goes to the **old Pod only**. The new Pod in `CrashLoopBackOff` never passes its readiness probe, so it is removed from the Service's EndpointSlice and receives nothing; meanwhile the rolling update stalls because `maxUnavailable` will not let it terminate the remaining healthy old Pod. So you are left serving from one old replica with the rollout stuck — which is exactly the safety property rolling updates are designed to give you. Say "readiness gates endpoint membership" and the answer is complete. See [how liveness, readiness, and startup probes differ](../kubernetes/how-do-liveness-readiness-and-startup-probes-differ.md).
- The single-replica rolling restart is its companion question, and the answer is yes, there will be downtime — unless `maxUnavailable` is 0 and `maxSurge` is at least 1, which lets a new Pod become Ready before the old one is terminated. Then give the sequence they asked for: the Deployment creates a new ReplicaSet, the Pod is scheduled, image pulled, init containers run, the container starts, the startup and readiness probes run, the endpoint is added, then the old Pod gets `SIGTERM`, its `preStop` hook runs, it is removed from endpoints, and after `terminationGracePeriodSeconds` it is `SIGKILL`ed. Mentioning that endpoint removal and `SIGTERM` race — which is why you need a `preStop` sleep — is a senior-level detail.
- "Two Pods cannot communicate, no errors anywhere" is testing whether you know that a NetworkPolicy denies silently. That should be your first hypothesis: a default-deny policy drops packets with no log and no event. Then work through the rest — wrong Service name or namespace in the client's URL, a Service with an empty EndpointSlice because its selector does not match, the wrong port or `targetPort`, CoreDNS not resolving, or the CNI dataplane broken on one node. Say you would `exec` in and test with `curl` and `nslookup` to separate DNS from connectivity. See [network segmentation](../network-security/what-is-network-segmentation.md).
- The Terraform policy-gate question wants named mechanisms, and there are several: `terraform plan` output scanned by Checkov, tfsec, or Trivy in CI with the job failing on a high-severity finding; OPA or Conftest policies evaluated against the plan JSON; Sentinel if you run Terraform Cloud or Enterprise; provider-level guards such as `lifecycle { prevent_destroy }`; and service control policies denying the API call outright so even a successful apply fails. Say that scanning the _plan_ rather than the HCL is better because it evaluates the resolved values. See [scanning infrastructure as code before it is applied](../devsecops/how-do-you-scan-infrastructure-as-code-before-it-is-applied.md).
- The three-part state question deserves three explicit answers, because the interviewer says "give me answers for all 3": secure storage is a remote backend with encryption at rest via KMS, versioning, and tightly scoped IAM; single-writer is state locking through DynamoDB or S3 native locking, or the backend's own lock; tamper-evidence is object versioning plus access logging on the bucket, CloudTrail on the key, and restricting write access to the CI role only so no human can modify state directly. Number them as you answer. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- Bringing an undocumented manual estate under Terraform is a plan question, so give phases: inventory everything first with Config, Resource Explorer, or `aws-nuke --dry-run`-style enumeration; pick one low-risk stack to start; use `import` blocks with `-generate-config-out` to scaffold HCL; iterate until `plan` is empty; then lock the console down so drift cannot reappear; and repeat stack by stack, never big-bang. Say explicitly that you would _not_ start with the production database. See [importing existing cloud infrastructure into Terraform](../infrastructure-as-code/how-do-you-import-existing-cloud-infrastructure-into-terraform.md).
- "Works internally, 403 externally" narrows fast if you say what 403 rules out: the request is reaching something that is deliberately refusing it, so it is not a routing or DNS failure. Candidates: a WAF rule or geo-restriction, an IP allowlist on the gateway, an internal-only DNS record resolving differently outside, missing authentication that internal users get via SSO, or a CDN or bucket policy. Say you would compare the two request paths header by header.
- The "10-second delay every 15 minutes" scenario is a periodicity clue and should be answered as one: something on a 15-minute cycle is doing work — a cron job or `CronJob`, a cache or token expiry and refresh, a metrics scrape or backup, garbage collection, log rotation, or a certificate or DNS TTL refresh. Say you would overlay the latency graph with deploy and job schedules to find the correlation before touching anything.
- For the canary 502 split, the fact that only _half_ fail is the signal: the canary version is the broken one. Check whether the canary Pods are actually Ready, whether the container listens on the port the Service expects, whether the new version needs a config or secret that was not created, and whether the gateway's timeout is shorter than the new version's startup. Say that this is exactly why canary analysis should compare canary against baseline and auto-abort. See [deployment strategies](../devops-tools-and-automation/what-are-deployment-strategies.md).
- The blocked-approvals question is a judgement test, not a technical one. Do not say you would bypass the gate. Say you would follow the documented escalation path to the delegated approver or on-call manager, and if it is a genuine production incident, invoke the break-glass emergency change procedure — which exists precisely for this, is logged, and gets reviewed afterwards. Then say you would raise the single-point-of-approval as a process risk after the fact. That answer wins in a bank.
- Zero-downtime database migrations should reach the expand-and-contract pattern: add the new column or table, deploy code that writes to both and reads from the old, backfill, switch reads to the new, then remove the old in a later release. Say that every migration must be backward compatible with the currently running version, because during a rollout both versions are live at once. See [continuous delivery versus continuous deployment](../cicd/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md).
- Prometheus companions: node-exporter for host metrics, kube-state-metrics for object state, cAdvisor via the kubelet for container metrics, Alertmanager for routing, application exporters, the Pushgateway for batch jobs, and Thanos or Mimir for long-term storage and global query. Say kube-state-metrics reports the desired state of objects while cAdvisor reports actual resource usage — people confuse the two. See [what Prometheus is](../monitoring-and-logging/what-is-prometheus.md).
- On the EFK question, cover collection (Fluentd or Fluent Bit as a DaemonSet), buffering, Elasticsearch for indexing and storage, Kibana for query, then filtering and indexing specifics: an inverted index for analysed text fields, `keyword` fields for exact matching and aggregation, filter context being cacheable and not scored, shards and replicas, and index lifecycle management moving data through tiers. See [what the ELK stack is](../monitoring-and-logging/what-is-elk-stack.md).
- The multi-region and multi-cloud data-loss question wants the 3-2-1 principle updated for cloud: multiple copies, across at least two providers or media, with one immutable and offline-equivalent copy — object lock or write-once storage so ransomware and accidental deletion cannot touch it — plus regular tested restores and a documented RPO. Say that replication is not backup, because a deletion replicates too. See [disaster recovery](../scalability-and-high-availability/what-is-disaster-recovery.md) and [designing for multi-region resilience](../cloud-engineering/how-do-you-design-for-multi-region-resilience.md).
- The payment-succeeds-but-shipping-fails question is a distributed transaction problem, so name the pattern: a saga with compensating transactions, or the outbox pattern with an idempotent consumer, rather than a two-phase commit across services. Say that the payment must be refundable by a compensating action and that every handler must be idempotent because retries will duplicate messages.
- Two candles measuring 45 minutes: light candle A at both ends and candle B at one end simultaneously. A burns out in 30 minutes; at that instant light B's second end, and B's remaining 30 minutes of material burns in 15. Total 45. Say the reasoning aloud — burning from both ends halves the time.
- Set 1 mixes application development into a DevOps interview, which is normal at JPMorgan. If Spring Boot, Java streams, and Kafka are outside your experience, say so cleanly and pivot to what you do own — but expect the platform half of the round to carry more weight for a DevOps title.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you integrate SonarQube and quality gates into a pipeline?]] (`#458`): [How do you integrate SonarQube and quality gates into a pipeline?](../cicd/how-do-you-integrate-sonarqube-and-quality-gates-into-a-pipeline.md)
- [[How do you do capacity planning?]] (`#230`): [How do you do capacity planning?](../site-reliability-engineering/how-do-you-do-capacity-planning.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
