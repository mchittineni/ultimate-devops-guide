---
title: "What DevOps and SRE interview questions does Infosys ask?"
id: 341
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - infosys
  - kubernetes
  - monitoring-and-logging
  - docker
  - infrastructure-as-code
  - site-reliability-engineering
  - aws-engineering
  - version-control
  - cicd
---

# What DevOps and SRE interview questions does Infosys ask?

## Questions

### Round set 1 — DevOps fundamentals

- **Introduce yourself.**
- **Which Git commands do you use day to day?**
- **Write a sample Dockerfile.**
- **Write a sample Terraform resource file.**
- **What is the difference between `git rebase` and `git merge`?**
- **What is the difference between `CMD` and `ENTRYPOINT`?**
- **Explain Prometheus and Grafana.**
- **What is your approach when a `pod.yaml` fails to apply?**
- **Explain the blue-green deployment strategy.**
- **Explain the Kubernetes architecture.**
- **Which `kubectl` commands do you use?**
- **The application you are deploying has crashed and you cannot get a shell into the Pod. What is your approach?**
- **Explain your project's pipeline.**
- **Have you done production deployment work, and how often do you deploy to production?**

### Round set 2 — monitoring and platform operations

- **What are Prometheus, Grafana, and Loki?**
- **How does Prometheus collect metrics, and how is it set up?**
- **What is Kibana and how is it set up?**
- **What are indices and an index in Kibana?**
- **What are the data sources for Grafana and Kibana?**
- **How do you receive alerts in your project, and how is that set up?**
- **What is a log-rotate job and how does it work?**
- **How do you handle disk and CPU alerts?**
- **What are Jenkins and Ansible?**
- **What is Terraform, how do you use it in your project, and which resources have you provisioned?**
- **What are Deployments, DaemonSets, and StatefulSets?**
- **What is a Pod?**
- **Which basic Kubernetes commands do you use?**
- **What is Docker, how do you use it in your project, and have you written a Dockerfile?**
- **How is traffic routed inside a Kubernetes cluster?**
- **Questions on ELB and Ingress.**
- **What are cron jobs?**
- **Which Kubernetes issues have you worked on?**
- **If a Pod or node goes down, how do you troubleshoot and monitor it — through the cluster and through your monitoring tools?**
- **What are your daily tasks and activities, and questions about your current project?**
- **PaaS questions.**

### Round set 3 — DevOps Engineer (3 YOE)

- **What are your day-to-day activities?**
- **How do you reduce Docker image size?**
- **What difficulties have you faced building a Docker image?**
- **What is an HPA and how do you implement one?**
- **What is your branching strategy?**
- **What is Pod affinity?**
- **Explain the Kubernetes architecture.**
- **What is a security group, and what is the default traffic rule in one?**
- **Why is Terraform used, and which Terraform modules do you use?**
- **How do you set up a Prometheus dashboard, and how does data get into Prometheus?**
- **Which alerts have you set up in Grafana?**
- **Do you have experience with Python scripting?**
- **What do you work on in Kubernetes, and which tools do you use in your project?**
- **What is your team size, and how many Pods do you manage?**
- **Tell me one task or tool you built from scratch.**
- **Give me a crisp overview of your client — is it a banking project?**

### Round set 4 — SRE (5+ YOE)

- **What are SLI, SLA, SLO, and error budget?**
- **What is the difference between monitoring and observability?**
- **Users are complaining of latency on an application you support, and you have monitoring tools in place. How do those tools help you identify and fix the latency?**
- **What is chaos engineering?**
- **Which AWS services have you used?**
- **How do you make your cloud infrastructure more secure?**
- **How do you secure an S3 bucket?**
- **You have a VPC with a public and a private subnet, each holding instances that must be patched regularly. The public-subnet instances have internet access and update fine. How do you update the instances in the private subnet?**
- **Which Ansible modules have you used in your playbooks?**
- **What is your experience with Terraform?**
- **Which CI/CD tool have you used, and can you explain a CD pipeline you built — the steps and the tools you integrated?**
- **How do you manage your Kubernetes cluster — Helm, the command line, Rancher, or Argo CD?**
- **A Pod in your cluster is in `CrashLoopBackOff`. What could be wrong with it?**
- **What is your experience with Python?**
- **Which monitoring tools have you used, and what did you do with them?**
- **Do you have experience managing a team?**
- **Have you worked on writing client proposals?**

## Example

```text
Infosys — DevOps Engineer / SRE, four reported interviews (~78 questions)

  SET 1  DevOps fundamentals        14   write Dockerfile + Terraform,
                                         rebase vs merge, CMD vs ENTRYPOINT,
                                         failed pod.yaml, crashed pod you
                                         cannot exec into
  SET 2  Monitoring / platform ops  21   Prometheus + Grafana + Loki + Kibana,
                                         indices, alert routing, logrotate,
                                         disk/CPU alerts, traffic routing
  SET 3  DevOps Engineer (3 YOE)    16   image size, HPA, pod affinity, SG
                                         default rules, Prometheus data flow,
                                         "built from scratch"
  SET 4  SRE (5+ YOE)               17   SLI/SLO/SLA + error budget,
                                         observability, latency triage,
                                         chaos engineering, private-subnet
                                         patching, team + proposals

THE MOST-REPEATED TOPIC IN THIS COLLECTION
  Prometheus and Grafana appear in all four Infosys rounds. Kubernetes
  architecture appears in three. If you prepare only two things for Infosys,
  prepare those.
```

## Interview tips

- The private-subnet patching question in the SRE round is the best scenario Infosys asks, and there are three good answers. Systems Manager Patch Manager with VPC endpoints for SSM, EC2 Messages, and SSM Messages needs no internet at all and is the answer they want. Alternatively route egress through a NAT gateway, or host an internal repository mirror so packages never leave the VPC. Say why the endpoint approach is best — the instances stay genuinely private and every patch operation is logged. See [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md).
- "The application crashed and I cannot exec into the Pod" is a deliberately awkward scenario, because `kubectl exec` needs a running container. Give the alternatives in order: `kubectl logs --previous` for the dead container's output, `kubectl describe pod` for events and the exit code, `kubectl debug` with an ephemeral container to attach a shell with debugging tools to the running Pod, or `kubectl debug --copy-to` to clone the Pod with the command overridden to `sleep` so it stays up long enough to inspect. Naming `kubectl debug` is what separates a current answer from a 2019 one. See [troubleshooting a Pod stuck in Pending or CrashLoopBackOff](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md).
- For "how does Prometheus collect metrics", be specific about the model, because it is the one thing people get backwards: Prometheus _pulls_ by scraping HTTP `/metrics` endpoints on a schedule, discovering targets through Kubernetes service discovery or static configuration. Then cover what that implies — exporters for things that cannot expose metrics themselves, the Pushgateway as the exception for short-lived batch jobs, and Alertmanager as a separate component for routing. Say that Grafana only queries and does not scrape. See [what Prometheus is](../monitoring-and-logging/what-is-prometheus.md) and [what Grafana is](../monitoring-and-logging/what-is-grafana.md).
- The Loki and Kibana questions are checking whether you understand the two logging models. Loki indexes only labels and stores compressed log chunks, which makes it cheap and Prometheus-like to query with LogQL; Elasticsearch with Kibana fully indexes log content, which makes arbitrary full-text search fast but costs far more storage and shard overhead. On indices, say an index is the unit of storage and sharding, that a data stream or daily index pattern is how time-series logs are organised, and that index lifecycle management moves them through hot, warm, and cold tiers. See [what the ELK stack is](../monitoring-and-logging/what-is-elk-stack.md) and [designing a logging pipeline that stays affordable at scale](../monitoring-and-logging/how-do-you-design-a-logging-pipeline-that-stays-affordable-at-scale.md).
- "How do you handle disk and CPU alerts" invites a weak answer, so make it strong by talking about the alert design as well as the response. For disk: check what filled it, whether logs need rotation, whether it is inodes rather than bytes, then expand or clean — and alert on projected time-to-full rather than a static percentage, because 90% on a 10 TB volume is not the same as 90% on a 20 GB one. For CPU: distinguish sustained saturation needing capacity from a runaway process, and read load average relative to core count. See [designing alerts that page a human](../site-reliability-engineering/how-do-you-design-alerts-that-page-a-human.md) and [troubleshooting SSH failures, high CPU, and disk space](../linux-administration/how-do-you-troubleshoot-ssh-failures-high-cpu-and-disk-space-on-linux-servers.md).
- `logrotate` is a small question with a precise answer: a cron or `systemd`-timer-driven utility configured in `/etc/logrotate.conf` and `/etc/logrotate.d/`, which rotates by size or age, keeps a set number of generations, compresses old ones, and either signals the process to reopen its file or uses `copytruncate` for processes that will not. That last distinction is the detail worth giving — it is why logs sometimes silently stop after rotation.
- The latency-triage question in the SRE round wants a method, not tool names. Work from symptom to cause: confirm it with p95 and p99 latency rather than averages, narrow by endpoint and region, check whether errors rose alongside latency, use traces to find which downstream span owns the added time, then correlate with saturation — CPU, connection pool, database locks, queue depth — and check whether a deploy or config change lines up in time. Say that averages hide the tail, which is exactly what users feel. See [service level indicators](../site-reliability-engineering/what-are-service-level-indicators-slis.md).
- Chaos engineering should be defined as a discipline rather than "breaking things": you form a hypothesis about steady-state behaviour, inject a controlled failure in production or production-like conditions with a defined blast radius and an abort condition, and verify whether the system behaved as you predicted. Name a concrete experiment — kill a Pod, add latency to a dependency, fail an availability zone — and say that the value is in the surprises. See [designing a system to degrade gracefully under overload](../scalability-and-high-availability/how-do-you-design-a-system-to-degrade-gracefully-under-overload.md).
- Security group default behaviour is asked in round 3 and has an exact answer: a newly created security group denies all inbound and allows all outbound, it is stateful so a response to an allowed outbound request is permitted automatically, and it has allow rules only — there is no deny. Add that instances in the same security group are not automatically allowed to talk to each other unless a rule references the group itself. See [network segmentation](../network-security/what-is-network-segmentation.md).
- Pod affinity, HPA, and image size are the three technical questions in round 3 with real depth available. For affinity, distinguish node affinity from Pod affinity and anti-affinity, and say that `requiredDuringScheduling` is a hard constraint while `preferred` is a soft one, with topology spread constraints as the modern way to spread replicas across zones. See [controlling which node a Pod runs on](../kubernetes/how-do-you-control-which-node-a-pod-runs-on.md) and [reducing Docker image size and build time](../docker/how-do-you-reduce-docker-image-size-and-build-time.md).
- SLI, SLO, SLA, and error budget are asked as one question, so answer them as one chain rather than four definitions: the SLI is the measurement, the SLO is the internal target for that measurement, the SLA is the external promise with consequences, and the error budget is what is left of the SLO — the amount of unreliability you are allowed to spend, which is what makes the release-versus-reliability decision objective. See [SLA versus SLO versus SLI versus OLA](../sla-management/what-is-the-difference-between-an-sla-an-slo-an-sli-and-an-ola.md) and [error budgets](../site-reliability-engineering/what-is-error-budget.md).
- Rounds 3 and 4 both ask soft questions — team size, Pods managed, client overview, team management, client proposals. Infosys is a services company, so these are scored: have crisp factual answers ready and do not treat them as filler.
- "Tell me one task or tool you built from scratch" is the highest-leverage question in round 3. Prepare one story with the problem, what you built, and a measurable outcome. See [turning ad-hoc scripts into maintainable automation](../scripting-and-automation/how-do-you-turn-a-pile-of-ad-hoc-scripts-into-maintainable-automation.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?]] (`#455`): [How do you trigger a pipeline — webhooks, polling, schedules, and upstream jobs?](../cicd/how-do-you-trigger-a-pipeline-webhooks-polling-schedules-and-upstream-jobs.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
