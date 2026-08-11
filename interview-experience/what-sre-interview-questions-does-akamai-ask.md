---
title: "What SRE interview questions does Akamai ask?"
id: 310
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - akamai
  - linux-administration
  - network-security
  - scripting-and-automation
  - docker
  - kubernetes
  - aws-engineering
---

# What SRE interview questions does Akamai ask?

## Questions

**Networking**

- **What is the difference between IPv4 and IPv6 — address size, notation, and what IPv6 solves?**
- **What is the valid range of an IPv4 address, and what does the first octet tell you about its class or purpose?**
- **Explain the OSI model layer by layer, and place a real protocol at each layer.**
- **What is the difference between a public and a private DNS hosted zone, and when do you use each?**
- **How do you check whether firewall protection is active on a Linux host, and how do you inspect the rules?**

**Scripting and shell one-liners**

- **Write a script that validates whether a given string is a legal IPv4 address.**
- **Write a Unix command that finds every file larger than 1 GB.**
- **Write a Unix command that finds the keyword `ERROR` in a text file, matching case-insensitively.**

**Python fundamentals**

- **In Python 3, what do `5/2` and `5//2` each evaluate to, and why do true division and floor division differ?**
- **Given `a = [0]` and `b = {0}`, what does `a[0]` return and what happens when you evaluate `b[0]`?**

**Linux operations**

- **You are logging into a Linux machine for the first time. What is your process — what do you check and in what order?**
- **You cannot access a Linux machine at all. How do you diagnose it?**

**Containers and Kubernetes**

- **What is the difference between `CMD` and `ENTRYPOINT` in a Dockerfile, and how do they interact when both are present?**
- **How would you create a Kustomize configuration — what goes in the base, and how do overlays change it per environment?**

## Example

```text
Akamai — SRE (8 YOE), reported round
14 questions

  Networking                  5   IPv4 vs IPv6, address range, OSI,
                                  hosted zones, firewall inspection
  Scripting / one-liners      3   IPv4 validator, find >1GB, case-insensitive grep
  Python traps                2   5/2 vs 5//2, set is not indexable
  Linux operations            2   first login checklist, host unreachable
  Containers                  2   CMD vs ENTRYPOINT, Kustomize

READ THE ROOM
  A CDN company weights networking at ~36% of the round. Cloud services
  barely appear. Revise IP addressing and OSI before revising Terraform.
```

```bash
# The two one-liners they expect you to produce without hesitation.
find / -type f -size +1G 2>/dev/null
grep -i "ERROR" application.log
```

## Interview tips

- `b[0]` on a set raises `TypeError: 'set' object is not subscriptable`. Sets are unordered and unindexed. Say that, then add that `0 in b` is the correct membership test — it shows you know what a set is for, not just that indexing fails.
- `5/2` is `2.5` and `5//2` is `2` in Python 3. Add that Python 2 returned `2` for `5/2`, and that `//` floors toward negative infinity, so `-5//2` is `-3`, not `-2`. That last detail is the differentiator.
- For the IPv4 validator, do not reach for a regex first. Split on `.`, require exactly four parts, require each to be all digits, and require `0 <= n <= 255`. Then mention `ipaddress.ip_address()` from the standard library as what you would actually ship. See [production-grade Bash scripting](../scripting-and-automation/how-do-you-write-a-production-grade-bash-script.md).
- The "unable to access a Linux machine" question is a layered-diagnosis prompt. Work outward: is it DNS, is the host reachable by ICMP, is port 22 open, is `sshd` running, is it a key or permissions problem, is the disk full, is the console reachable through the hypervisor or cloud provider. See [troubleshooting SSH failures, high CPU, and disk space](../linux-administration/how-do-you-troubleshoot-ssh-failures-high-cpu-and-disk-space-on-linux-servers.md).
- For first login, describe reconnaissance rather than commands at random: `uname -a`, `df -h`, `free -m`, `top`, `systemctl --failed`, who else is logged in, and what the host is actually for. See [basic Linux commands](../linux-administration/what-are-the-basic-linux-commands-every-devops-engineer-should-know.md).
- `CMD` versus `ENTRYPOINT` is graded on the interaction: `ENTRYPOINT` is the executable, `CMD` supplies default arguments, and arguments passed to `docker run` replace `CMD` but not `ENTRYPOINT` unless you use `--entrypoint`. See [what a Dockerfile is](../docker/what-is-dockerfile.md).
- Public versus private hosted zones is a Route 53 question in disguise: private zones are associated with specific VPCs and resolve only from inside them. Mention split-horizon DNS. See [managing DNS and global traffic routing](../cloud-engineering/how-do-you-manage-dns-and-global-traffic-routing.md).
- Add `grep -ri` and `grep -c` as follow-ups to the case-insensitive search, and be ready for "now show only the count" or "now search every file under this tree". See [analysing logs with grep, awk, and sed](../linux-administration/how-do-you-analyse-logs-and-text-files-with-grep-awk-and-sed.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?]] (`#402`): [How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?](../cicd/how-do-you-troubleshoot-a-jenkins-pipeline-that-never-starts-or-hangs-in-the-queue.md)
- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
