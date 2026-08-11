---
title: "What DevOps interview questions does Koerber Pharma ask?"
id: 344
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - koerber-pharma
  - aws-engineering
  - infrastructure-as-code
  - cloud-cost-optimization
  - kubernetes
  - network-security
  - docker
  - secops
  - monitoring-and-logging
---

# What DevOps interview questions does Koerber Pharma ask?

## Questions

**Cost optimisation**

- **How do you handle cost optimisation in AWS, and how do you plan for it?**

**Terraform**

- **If someone deleted a resource that Terraform manages, how do you identify it and recover it?**
- **If your state file is deleted, how do you recover without recreating the resources?**
- **How do you create separate dev, test, and production environments in Terraform?**
- **What is a Terraform provisioner?**
- **What is a Terraform workspace and how do you manage them?**
- **How do you connect your Terraform environment to AWS and drive it from CI/CD?**
- **What real problems have you hit with Terraform recently — which errors?**

**Architecture and latency**

- **How do you design a web application that handles fluctuating traffic with low latency, and how does traffic flow through it?**
- **How do you achieve low-latency routing, and which routing policy would you use?**
- **What is your strategy for zero downtime, and how do you achieve it?**
- **What are the strategies for deploying an application?**

**AWS services and networking**

- **What are the EC2 instance types, and what are Spot, Reserved, and On-Demand instances?**
- **What is the difference between a NAT gateway and a NAT instance?**
- **What is the difference between Transit Gateway and VPC peering?**
- **What are the storage types, and what is the difference between S3 and EBS?**
- **How do you back up an EBS volume and attach it to another server?**
- **Where would you use AWS Lambda — give a use case.**
- **What are CloudWatch, CloudTrail, and CloudWatch metrics?**
- **Which service do you use to monitor a spike in application CPU usage in the cloud?**
- **If a resource is deleted, how do you identify which one it was?**

**Security and access**

- **What are the security best practices in AWS?**
- **How do you manage certificates in AWS? If a certificate expires, how do you handle it and what action do you take?**
- **You have just joined an organisation. How should access be granted to you, and as an administrator how do you secure the AWS account?**
- **What is the difference between a role and a policy?**
- **How are you connecting to the client's environment from your AWS environment?**
- **You have found malware on a client machine. How do you remove it and build an environment that stays free of malware attacks?**

**Containers and Kubernetes**

- **What is the difference between `CMD` and `ENTRYPOINT`?**
- **What are Docker volumes, and what does `docker prune` do?**
- **Explain the Kubernetes architecture and Services, and how you troubleshoot an application Pod that fails.**
- **How do you schedule a Pod onto a specific node?**
- **What is the difference between a StatefulSet and a stateless application?**
- **Can you delete the pause container?**

**Observability and CI/CD**

- **What is the difference between observability and monitoring?**
- **Which Jenkins plugins do you use for CI/CD on AWS?**

## Example

```text
Koerber Pharma — DevOps Engineer (9 YOE, 5 relevant), reported round
36 questions

  AWS services / networking   9   instance purchase options, NAT gateway vs
                                  instance, TGW vs peering, S3 vs EBS, EBS
                                  backup + reattach, CloudWatch/Trail/metrics
  Terraform                   8   deleted resource detection + recovery,
                                  deleted state file, environments,
                                  workspaces, provisioners, real errors hit
  Security and access         6   AWS best practices, expired certificates,
                                  onboarding access + account hardening,
                                  role vs policy, client connectivity, malware
  Containers / Kubernetes     6   CMD vs ENTRYPOINT, volumes + prune,
                                  K8s architecture + pod triage, node
                                  pinning, StatefulSet vs stateless,
                                  the pause container
  Architecture / latency      4   fluctuating traffic design, low-latency
                                  routing, zero downtime, deploy strategies
  Cost optimisation           1   plan a cost programme
  Observability / CI/CD       2   observability vs monitoring, Jenkins plugins

ASKED TWICE
  "Observability vs monitoring" and the deleted-resource question both appear
  twice in the same round — the interviewer circled back. Treat both as
  guaranteed.
```

## Interview tips

- The pause container question is the sharpest item in this round and the answer is a firm no, with a reason. The pause container is the infrastructure container that holds the Pod's network and IPC namespaces open so the application containers can share them, and it reaps zombie processes as PID 1. Deleting it tears down the Pod's sandbox, so the kubelet immediately recreates the whole Pod. Say that it is created and managed by the kubelet, not by you, and that its presence is why every Pod shows an extra container on the node. See [what a Pod is](../kubernetes/what-is-a-pod-in-kubernetes.md) and [how namespaces, cgroups, and capabilities isolate a container](../docker/how-do-namespaces-cgroups-and-capabilities-isolate-a-container.md).
- The deleted-resource question is asked twice, so lead with detection and be specific: CloudTrail tells you _who_ deleted _what_ and when, AWS Config shows the configuration timeline and can alert on deletion, and `terraform plan` shows the resource as needing recreation because state still claims it exists. Recovery is `terraform apply` to recreate it — but say the important caveat: recreating an EC2 instance or a database is not the same as recovering its _data_, so you need snapshots or backups for anything stateful. That distinction is what a pharma company cares about. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- Low-latency routing has a named answer they are fishing for: Route 53 latency-based routing, which sends each client to the region with the lowest measured latency — as distinct from geolocation routing, which sends by where the user _is_, and weighted or failover routing which serve different purposes. Then add the layers that actually deliver low latency: CloudFront at the edge, Global Accelerator for anycast entry, regional replicas, and caching. See [managing DNS and global traffic routing](../cloud-engineering/how-do-you-manage-dns-and-global-traffic-routing.md).
- The malware question is unusual for a DevOps round, and the winning answer is containment before cleanup. Sequence it: isolate the machine from the network, snapshot it for forensics before changing anything, identify the entry point, then _rebuild rather than clean_ — because a cleaned host can never be trusted — restore data from a known-good backup after scanning, and rotate every credential that machine held. Then answer the second half about staying clean: immutable infrastructure so hosts are replaced not patched, least privilege, EDR, network segmentation, patch automation, and application allowlisting. "Rebuild, do not disinfect" is the line that lands. See [what an incident response plan is](../incident-management/what-is-an-incident-response-plan.md) and [zero-trust security](../network-security/what-is-zero-trust-security.md).
- Role versus policy is a small question with a precise answer: a policy is a JSON document listing permissions; a role is an identity that can be assumed, which has policies attached and issues temporary credentials. Say that roles are how you avoid long-lived access keys, which links straight into the onboarding question. See [how AWS IAM evaluates a request](../aws-engineering/how-does-aws-iam-evaluate-a-request.md).
- For onboarding and account hardening, answer as an administrator would be expected to: federated SSO through IAM Identity Center rather than IAM users, permission sets scoped by job function, MFA everywhere, no use of the root account with its credentials locked away, CloudTrail enabled organisation-wide to an immutable bucket, GuardDuty and Security Hub on, service control policies at the organisation level, and no long-lived access keys. See [least-privilege identity in the cloud](../cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md).
- Certificate management should reach ACM with DNS validation, because that gives automatic renewal — and then say what breaks it: a DNS validation record that was removed, or a certificate imported rather than issued by ACM, which does _not_ auto-renew. For an expiry, describe the response: replace the certificate on the listener or distribution, verify the chain, and add expiry monitoring so it never recurs. See [what SSL/TLS is](../network-security/what-is-ssl-tls.md).
- NAT gateway versus NAT instance should end in a recommendation: the gateway is managed, scales automatically to tens of gigabits, is highly available within its zone, and needs no patching; a NAT instance is an EC2 box you own, cheaper at small scale and able to double as a bastion or run port forwarding, but it is a single point of failure you must patch and scale. Say you would use the gateway unless you specifically need the flexibility.
- S3 versus EBS is object versus block: S3 is object storage reached over HTTP, effectively unlimited, region-scoped, and accessed by many clients at once; EBS is a block device attached to an instance in one availability zone, formatted with a filesystem. Then answer the backup-and-reattach question concretely — snapshot the volume, create a new volume from that snapshot _in the target availability zone_, attach it, and mount it by UUID. The availability-zone constraint is the detail that gets missed. See [S3 storage classes](../aws-engineering/what-are-the-s3-storage-classes-and-when-do-you-use-each.md).
- CloudWatch versus CloudTrail versus metrics: CloudWatch is monitoring — metrics, logs, alarms, dashboards; CloudTrail is the audit log of API calls; "CloudWatch metrics" are the individual time series CloudWatch stores. For the CPU spike question, name a CloudWatch alarm on `CPUUtilization` with an SNS action, and volunteer that memory is _not_ a default metric and needs the CloudWatch agent — that gap is a favourite follow-up. See [monitoring in DevOps](../monitoring-and-logging/what-is-monitoring-in-devops.md).
- Cost optimisation asked as "how do you _plan_ for it" wants a programme, not tactics: get visibility first with tagging and Cost Explorer, find the top spend lines, then right-size and modernise instance families, commit with Savings Plans for the steady baseline, move interruptible work to Spot, apply storage lifecycle rules, delete orphaned volumes and idle load balancers, cut log retention, and finally put a budget and anomaly alert in place so it does not regress. Say you would report savings against a baseline. See [cloud cost optimisation](../cloud-cost-optimization/what-is-cloud-cost-optimization.md).
- The Terraform environments and workspaces pair should be answered with an opinion: separate directories with separate state per environment is the mainstream choice because it makes the target explicit and lets configuration differ; workspaces suit identical infrastructure varying only by variables and are easy to apply to the wrong environment by accident. Say which you use and why.
- Have one real Terraform error ready for the "what errors did you face" question — a provider version bump changing a default, a cycle in dependencies, a state lock left behind after a cancelled apply, a resource that must be recreated because a field is immutable. A specific error with how you resolved it is worth far more than "sometimes there are errors".
- Zero downtime and deployment strategies are asked as separate questions, so do not merge them. Strategies: recreate, rolling, blue-green, canary, and A/B. Zero downtime is the _set of properties_ that makes any of them safe — readiness probes gating traffic, `maxUnavailable: 0`, connection draining, `preStop` hooks, backward-compatible database changes, and idempotent, retryable requests. See [deployment strategies](../devops-tools-and-automation/what-are-deployment-strategies.md).
- Client-environment connectivity should name the options and the decision: site-to-site VPN for cost and speed of setup, Direct Connect for predictable bandwidth and regulated traffic, PrivateLink if you only need to expose or consume one service, and Transit Gateway if many VPCs are involved. Flag overlapping CIDRs as the practical blocker. See [connecting an on-premises network to the cloud](../cloud-engineering/how-do-you-connect-an-on-premises-network-to-the-cloud.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
