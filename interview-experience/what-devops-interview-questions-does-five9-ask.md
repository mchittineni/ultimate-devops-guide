---
title: "What DevOps interview questions does Five9 ask?"
id: 334
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - five9
  - infrastructure-as-code
  - network-security
  - linux-administration
  - monitoring-and-logging
  - aws-engineering
  - scripting-and-automation
---

# What DevOps interview questions does Five9 ask?

## Questions

**Terraform**

- **Besides storing Terraform log or state files in S3, what other backend options are there?**
- **What provisioner types does Terraform have?**
- **What is the difference between a local and a remote provisioner?**
- **What is the difference between using EC2 `user_data` and using a remote provisioner?**

**DNS**

- **What are A, AAAA, and CNAME records in DNS?**
- **What is the failover mechanism in DNS when one IP address becomes unreachable?**

**Security and TLS**

- **Explain the TLS handshake.**
- **Other than a password, how do you log into an EC2 instance?**

**Linux**

- **How do you set CPU and memory limits on a Linux machine?**

**Logging**

- **How are logs separated and organised in ELK?**

**Coding**

- **How do you find the second-largest integer in an array?**

## Example

```text
Five9 — DevOps Engineer (7 YOE), reported round
11 questions

  Terraform                   4   backend options, provisioner types,
                                  local vs remote, user_data vs provisioner
  DNS                         2   A/AAAA/CNAME, failover when an IP dies
  Security / TLS              2   TLS handshake, EC2 login without a password
  Linux                       1   CPU and memory limits
  Logging                     1   log segregation in ELK
  Coding                      1   second-largest integer

SMALL ROUND, DEEP QUESTIONS
  Only 11 questions, but three of them (provisioner comparison, user_data vs
  remote-exec, DNS failover) are ones most candidates answer vaguely. Depth
  beats breadth here.
```

```python
# Second largest in one pass, no sorting, handles duplicates.
def second_largest(nums):
    first = second = float("-inf")
    for n in nums:
        if n > first:
            first, second = n, first
        elif first > n > second:      # skip duplicates of the max
            second = n
    return second if second != float("-inf") else None
```

## Interview tips

- The `user_data` versus remote provisioner comparison is the best question in the round, and there is a clearly preferred answer. `user_data` is handed to the instance at launch and executed by cloud-init on the machine itself, so Terraform needs no network path, no SSH key, and no credentials — and changing it can be made to trigger a replacement. A `remote-exec` provisioner requires Terraform to open an SSH or WinRM connection _from wherever it is running_, which fails behind a bastion or from a CI runner with no route, has no retry semantics, and is documented by HashiCorp as a last resort. Say you default to `user_data`, or to a pre-baked image, and reserve provisioners for genuinely unavoidable cases.
- Provisioner types worth naming: `local-exec` runs on the machine running Terraform, `remote-exec` runs on the created resource, `file` copies content to it, and there are `connection` blocks plus creation-time and destroy-time variants. Add that `null_resource` with `triggers` — now largely superseded by `terraform_data` — is how people force provisioners to re-run, and that all of this is a sign you should be using configuration management or a baked image instead. See [Terraform providers](../infrastructure-as-code/what-are-terraform-providers.md).
- For backends, name several and group them: object storage with a lock table such as S3 with DynamoDB or now S3 native locking, Azure Blob Storage, Google Cloud Storage, HashiCorp Consul, Terraform Cloud or Enterprise, and a generic HTTP backend. Say what a backend must provide — durability, versioning, locking, and encryption — because that framing is better than a list. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- The DNS question is transcribed as "AAA" but means A and AAAA. Answer all three: A maps a name to an IPv4 address, AAAA to an IPv6 address, and CNAME aliases one name to another name. Add the two rules that show real experience — a CNAME cannot coexist with other records at the same name, and you cannot put a CNAME at a zone apex, which is why cloud providers offer alias or ANAME records.
- DNS failover has a specific mechanism, so do not answer "DNS just retries". Say that plain DNS has no health awareness: it returns whatever records exist, and a client will happily connect to a dead IP until the TTL expires. Real failover needs health checks driving record changes — Route 53 health checks with failover or latency routing policies, or a global load balancer — and you keep TTLs low, typically 60 seconds, so clients re-resolve quickly. Mention that browsers and resolvers cache beyond the TTL in practice, which is why an anycast load balancer with a stable IP is more reliable than DNS failover. See [managing DNS and global traffic routing](../cloud-engineering/how-do-you-manage-dns-and-global-traffic-routing.md).
- EC2 login without a password should reach four answers: an SSH key pair, Systems Manager Session Manager with no inbound port at all, EC2 Instance Connect, and the serial console for a broken instance. Say Session Manager is the production answer because it needs no open port, no key distribution, and logs every session. See [troubleshooting SSH failures](../linux-administration/how-do-you-troubleshoot-ssh-failures-high-cpu-and-disk-space-on-linux-servers.md).
- Linux CPU and memory limits means cgroups, and the modern answer is `systemd` resource control — `CPUQuota`, `MemoryMax`, and `MemoryHigh` on a unit, or `systemd-run` for an ad-hoc process. Mention `ulimit` for per-process limits and note it is the weaker, older mechanism, and that containers use the same cgroup primitives underneath. See [what systemd is](../linux-administration/what-is-systemd.md) and [how namespaces, cgroups, and capabilities isolate a container](../docker/how-do-namespaces-cgroups-and-capabilities-isolate-a-container.md).
- Log segregation in ELK is about index strategy: separate indices per application and per day or via data streams, an index naming convention plus index lifecycle management for hot, warm, and cold tiers, and Logstash or Ingest pipelines adding fields such as service, environment, and severity so Kibana can filter. Say that too many small indices costs shard overhead — that trade-off is the depth marker. See [what the ELK stack is](../monitoring-and-logging/what-is-elk-stack.md) and [designing a logging pipeline that stays affordable at scale](../monitoring-and-logging/how-do-you-design-a-logging-pipeline-that-stays-affordable-at-scale.md).
- On the coding question, say the complexity and handle the edge cases out loud: one pass, O(n) time and O(1) space, and decide explicitly what `[5, 5, 5]` should return. Sorting works but is O(n log n) — mention that you know the sorted answer exists and chose the linear one deliberately.
- The TLS handshake appears in many rounds in this collection. Cover certificate validation, key agreement, and the switch to symmetric encryption, and note that TLS 1.3 needs one round trip. See [what SSL/TLS is](../network-security/what-is-ssl-tls.md).

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
