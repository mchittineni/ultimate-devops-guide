---
title: "What DevOps interview questions does Qentelli Solutions ask?"
id: 373
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - qentelli-solutions
  - aws-engineering
  - infrastructure-as-code
  - network-security
  - linux-administration
  - monitoring-and-logging
  - cloud-cost-optimization
---

# What DevOps interview questions does Qentelli Solutions ask?

## Questions

**Terraform**

- **Create an S3 bucket with Terraform.**
- **How do you manage resources in Terraform?**

**AWS security and networking**

- **A developer changed a private subnet into a public one. What should you do?**
- **What is KMS?**
- **Explain inflow and outflow on an ELB.**
- **What is the difference between a security group and a network ACL?**
- **How do you secure your environments in AWS, and what security options are available?**

**Monitoring and cost**

- **Which CloudWatch metrics should you focus on?**
- **Your AWS bill spikes. What should you check?**

**Linux**

- **What is the difference between a soft link and a hard link?**
- **A user cannot get in over SSH. What troubleshooting steps do you perform?**
- **Write a shell script that backs up the last seven days of logs and removes older ones.**

## Example

```text
Qentelli Solutions — DevOps Engineer (5 YOE), reported round
12 questions

  AWS security / networking   5   developer made a subnet public, KMS,
                                  ELB inflow/outflow, SG vs NACL,
                                  securing environments
  Linux                       3   soft vs hard link, SSH failure triage,
                                  7-day log backup script
  Monitoring and cost         2   which CloudWatch metrics matter,
                                  investigating a billing spike
  Terraform                   2   create an S3 bucket, manage resources

THE SCENARIO WORTH PREPARING
  "A developer made a private subnet public." It is a governance question
  disguised as a networking question — the interviewer wants to hear
  containment, then root cause, then the guardrail that prevents a repeat.
```

```bash
# The 7-day log backup script — archive the recent window, then prune.
#!/usr/bin/env bash
set -euo pipefail

SRC=${1:?usage: $0 <log-dir> <backup-dir>}
DEST=${2:?usage: $0 <log-dir> <backup-dir>}
stamp=$(date +%F)

mkdir -p "$DEST"
# Archive files modified within the last 7 days (-mtime -7).
find "$SRC" -xdev -type f -name '*.log' -mtime -7 -print0 \
  | tar --null -czf "$DEST/logs-$stamp.tar.gz" --files-from=-

# Only prune AFTER the archive exists and is non-empty.
[[ -s "$DEST/logs-$stamp.tar.gz" ]] || { echo "archive empty, not pruning" >&2; exit 1; }
find "$SRC" -xdev -type f -name '*.log' -mtime +7 -delete
```

## Interview tips

- The public-subnet question is the best in this round and the wrong answer is to jump straight to "revert it". Structure the response in three phases. **Contain**: work out what is now exposed — check whether any instance actually received a public IP, whether security groups allow inbound from `0.0.0.0/0`, and whether anything sensitive is reachable; remove the `0.0.0.0/0` route to the internet gateway and disable auto-assign public IP. **Investigate**: use CloudTrail to find who made the change and when, and check whether anything connected in that window. **Prevent**: this is where the marks are — the change should not have been possible by hand, so put the VPC under Terraform with `plan` reviewed in CI, deny route-table and internet-gateway modifications outside the pipeline via IAM or a service control policy, add an AWS Config rule that flags subnets with auto-assign public IP or a public route, and alert on `CreateRoute` and `ModifySubnetAttribute` events. Say the sentence "a developer should not have had that permission" — that is the answer they are listening for. See [defence in depth for a cloud network](../network-security/how-do-you-design-defence-in-depth-for-a-cloud-network.md).
- The billing-spike question wants a systematic investigation, not a list of cost tips. Go in order: Cost Explorer grouped by service, then by usage type, then by tag or account, comparing against the same period last month to isolate _what_ changed; check Cost Anomaly Detection if it is enabled; then look for the usual culprits — data transfer and NAT gateway processing charges, which are invisible until you look; a forgotten test cluster or GPU instance; an autoscaling group that thrashed; CloudWatch log ingestion after someone raised a log level; S3 request costs or a lifecycle rule transitioning millions of small objects; and cross-AZ traffic. Then say the preventive control: budgets with alerts, mandatory tagging so cost is attributable, and anomaly detection on. Naming NAT gateway and log ingestion specifically marks the answer as experienced. See [cloud cost optimisation](../cloud-cost-optimization/what-is-cloud-cost-optimization.md).
- "Which CloudWatch metrics should you focus on?" invites a shopping list, so give a principle first: alert on user-facing symptoms, not on causes. That means load balancer 5xx rate, target response time percentiles, and healthy host count for the request path; then saturation signals as _diagnostic_ rather than paging metrics — CPU, queue depth, database connections, disk and burst-credit exhaustion. Then volunteer the gap that always comes up: memory and disk usage on EC2 are **not** default CloudWatch metrics, because they are guest-OS level and need the CloudWatch agent. Saying that unprompted is the strongest part of the answer. See [designing alerts that page a human](../site-reliability-engineering/how-do-you-design-alerts-that-page-a-human.md).
- The log-backup script has one trap and the interviewer is watching for it: `-mtime -7` means _newer_ than seven days while `-mtime +7` means _older_, so getting the signs backwards deletes exactly the logs you meant to keep. Say that you archive first, verify the archive is non-empty, and only then prune — and that you would guard the source directory with `${DIR:?}` so an unset variable cannot expand to `/`. Mention `logrotate` as the tool that already does this properly on a server, with `compress`, `rotate`, and a post-rotate signal to the process. See [writing a production-grade Bash script](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md).
- The SSH triage question should be answered as a layered walk, and saying the layers out loud is the technique being graded: is it DNS or the wrong address; is the host reachable at all by ICMP or is the instance itself unhealthy; is port 22 open through the security group, NACL, and any host firewall; is `sshd` actually running; is it authentication — wrong key, wrong username, or `authorized_keys` permissions, since `~/.ssh` must be 700 and the file 600; is the account locked or the shell set to `nologin`; and is the disk full, because a full root filesystem breaks logins. Add that Session Manager or the serial console is your way in when SSH is the thing that is broken. See [troubleshooting SSH failures, high CPU, and disk space](../linux-administration/how-do-you-troubleshoot-ssh-failures-high-cpu-and-disk-space-on-linux-servers.md).
- Soft versus hard link needs consequences rather than definitions: a hard link is another directory entry pointing at the same inode, so it cannot cross filesystems, cannot link a directory, and the data survives until the last link is removed; a symlink stores a path, can cross filesystems and point at directories, and dangles if the target moves. Add that `ln -s` creates the symlink and omitting `-s` gives a hard link — the flag is the trap. See [Linux filesystem hierarchy](../linux-administration/what-is-linux-file-system-hierarchy.md).
- "ELB inflow and outflow" is an oddly-worded question best answered as the traffic path plus the security model. Inbound: the client resolves the load balancer's DNS name, connects to it, TLS terminates there, and the listener rule forwards to a target group over a _new_ connection from the load balancer's own network interfaces. Outbound: responses return through the load balancer, and the target's security group therefore needs to allow inbound from the _load balancer's security group_ rather than from the client's CIDR — which is the practical point the question is circling. Mention `X-Forwarded-For` as how the target still learns the real client IP, and cross-zone load balancing and its data-transfer implications.
- KMS should be answered with the envelope-encryption mechanism, not just "it manages keys": KMS holds a customer master key that never leaves the service, services request a data key which KMS returns in both plaintext and encrypted form, the plaintext key encrypts the data and is then discarded, and the encrypted key is stored alongside the ciphertext. Then the operational points: key policies are separate from IAM and both must allow access — which is the most common cause of a mysterious `AccessDenied` on an encrypted resource — plus automatic rotation, aliases, and the fact that a customer-managed key is required for cross-account sharing of encrypted AMIs or snapshots. See [how AWS IAM evaluates a request](../aws-engineering/how-does-aws-iam-evaluate-a-request.md).
- "How do you manage resources in Terraform?" is broad, so answer with the practices that matter: remote state with locking and versioning, one state per environment, reusable versioned modules, `plan` reviewed on the pull request and `apply` only from CI, mandatory tags, `lifecycle` guards on stateful resources, scheduled `plan -refresh-only` for drift detection, and `import`/`state rm` for reconciling reality. Pair the S3-bucket task with the modern detail that the bucket resource is now split into separate resources for versioning, encryption, public-access block, and lifecycle — writing them all is what distinguishes a current answer. See [what Terraform is](../infrastructure-as-code/what-is-terraform.md).
- Security group versus NACL appears in almost every round in this collection, so have the four contrasts ready — stateful versus stateless, allow-only versus allow-and-deny, evaluated as a set versus in numbered order, attached to a network interface versus a subnet — and finish with the consequence: you cannot block a single hostile IP with a security group, which is precisely why NACLs exist. See [network segmentation](../network-security/what-is-network-segmentation.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
