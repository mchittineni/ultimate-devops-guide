---
title: "What SRE interview questions does CMT ask?"
id: 321
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - cmt
  - aws-engineering
  - scalability-and-high-availability
  - network-security
  - linux-administration
  - kubernetes
  - infrastructure-as-code
  - monitoring-and-logging
  - incident-management
---

# What SRE interview questions does CMT ask?

## Questions

**High availability and architecture**

- **Design a highly available, fault-tolerant system on AWS.**
- **How would you maintain high availability on ECS with Fargate, or on EKS?**
- **What are the best practices for keeping systems highly available?**
- **Which AWS services have you used?**
- **What is the difference between an ALB and an NLB, and in which scenario do you choose each?**

**Networking fundamentals**

- **What is DNS and how does resolution work?**
- **What are TCP and UDP, and what are the trade-offs between them?**
- **What are IPv4 and IPv6, and what does IPv6 solve?**

**Monitoring**

- **On a web or application server, which metrics tell you whether it is highly available?**
- **Which metrics do you use to monitor CPU and memory on an EC2 instance in AWS?**

**Linux**

- **What is a PID?**
- **A Linux system has gone down. How do you troubleshoot it — and name the actual commands you would run.**

**Platform and IaC**

- **Explain the architecture of Kubernetes.**
- **How do you structure a Terraform codebase?**
- **Have you built any automation into your day-to-day work?**

**Decoupling and incidents**

- **If there is a slowness problem in your decoupling layer — an SQS queue — how do you handle it?**
- **Which production incidents have you handled? Explain them.**

## Example

```text
CMT — SRE (4-5 YOE), reported round
17 questions

  High availability / arch    5   design HA+FT on AWS, HA on Fargate/EKS,
                                  HA best practices, AWS services, ALB vs NLB
  Networking fundamentals     3   DNS, TCP vs UDP, IPv4 vs IPv6
  Monitoring                  2   HA metrics on app servers, EC2 CPU + memory
  Linux                       2   PID, system-down triage with commands
  Platform / IaC              3   K8s architecture, Terraform structure,
                                  daily automation
  Decoupling / incidents      2   slow SQS queue, production incidents

THE THREAD TO PULL
  Four separate questions circle high availability. Prepare ONE reference
  architecture — multi-AZ, health-checked, auto-scaled, stateless tier plus
  replicated data tier — and reuse it for all four.
```

## Interview tips

- Because HA is asked four different ways, build one reference architecture and reuse it: Route 53 in front, an ALB across at least two availability zones, an auto-scaling group or Fargate service with a minimum of two tasks per zone, a multi-AZ RDS with a standby, S3 for static assets, and no single instance holding state. Then adapt it per question rather than starting over. See [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md) and [running a highly available database on AWS](../aws-engineering/how-do-you-run-a-highly-available-database-on-aws.md).
- Distinguish high availability from fault tolerance explicitly, because the question names both. High availability minimises downtime and usually accepts a brief interruption during failover; fault tolerance means a component can fail with no interruption at all, which costs more. Naming that difference is the fastest way to sound senior on this question. See [high availability](../scalability-and-high-availability/what-is-high-availability.md) and [disaster recovery](../scalability-and-high-availability/what-is-disaster-recovery.md).
- The EC2 memory question contains a trap: CloudWatch publishes CPU utilisation natively but _not_ memory, because memory is a guest-OS metric. You need the CloudWatch agent to publish `mem_used_percent`. Volunteering that gap is a strong signal. See [monitoring in DevOps](../monitoring-and-logging/what-is-monitoring-in-devops.md).
- For availability metrics on an application server, do not list CPU. Answer with request-level signals: success rate or error ratio, latency percentiles, healthy target count behind the load balancer, and saturation of the connection or thread pool. That maps to the golden signals. See [service level indicators](../site-reliability-engineering/what-are-service-level-indicators-slis.md) and [designing alerts that page a human](../site-reliability-engineering/how-do-you-design-alerts-that-page-a-human.md).
- The slow-SQS question wants queue mechanics: check `ApproximateAgeOfOldestMessage` and queue depth to confirm consumers are behind, then scale consumers, increase batch size and use long polling, check whether the visibility timeout is shorter than processing time (which causes redelivery and duplicate work), confirm a dead-letter queue is catching poison messages, and consider a FIFO queue's throughput ceiling if one is in use. The visibility-timeout detail is the differentiator.
- "Tell the commands" is explicit, so name them: `uptime` and `top` for load, `free -m` for memory, `df -h` and `df -i` for disk and inodes, `dmesg -T` for kernel and OOM messages, `journalctl -xe` and `systemctl --failed` for services, `ss -tulpn` for listeners, and `iostat` for disk pressure. See [debugging a Linux performance problem from first principles](../linux-administration/how-do-you-debug-a-linux-performance-problem-from-first-principles.md) and [troubleshooting SSH failures, high CPU, and disk space](../linux-administration/how-do-you-troubleshoot-ssh-failures-high-cpu-and-disk-space-on-linux-servers.md).
- Terraform structure should describe a real layout: root modules per environment, reusable child modules, remote state per environment with locking, variables and outputs at module boundaries, and no hard-coded account IDs. Say whether you use workspaces or directories, and why. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- TCP versus UDP should end in a use case, not just "reliable versus unreliable": TCP for HTTP and databases, UDP for DNS, streaming, and metrics where a lost datagram is cheaper than a retransmit delay. See [network security in DevOps](../network-security/what-is-network-security-in-devops.md).
- Have two production incidents ready, ideally one where your first hypothesis was wrong. Interviewers at SRE level use the incident answer to check whether you reason from evidence or from memory. See [post-mortem analysis](../incident-management/what-is-post-mortem-analysis.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[What is the difference between SRE, DevOps, and Platform Engineering?]] (`#232`): [What is the difference between SRE, DevOps, and Platform Engineering?](../site-reliability-engineering/what-is-the-difference-between-sre-devops-and-platform-engineering.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
