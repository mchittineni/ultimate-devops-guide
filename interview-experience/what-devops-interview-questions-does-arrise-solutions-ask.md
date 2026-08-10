---
title: "What DevOps interview questions does Arrise Solutions ask?"
id: 315
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - arrise-solutions
  - aws-engineering
  - kubernetes
  - docker
  - linux-administration
  - network-security
  - cloud-engineering
---

# What DevOps interview questions does Arrise Solutions ask?

## Questions

**AWS networking and architecture**

- **Explain a three-tier architecture.**
- **What is the difference between an ALB and an NLB, in depth?**
- **What is the difference between a public and a private subnet?**
- **How do you give resources in a private subnet outbound internet access?**
- **Does a NAT gateway itself run in a public or a private subnet, and why?**
- **How would you connect an AWS VPC to a VPC in IBM Cloud?**
- **What is CloudFront and what problem does it solve?**

**Kubernetes**

- **Explain the Kubernetes architecture.**
- **What does CoreDNS do in a Kubernetes cluster?**
- **What is the purpose of the CNI?**
- **How does kube-proxy communicate with the nodes, and what does it program on them?**
- **What is the scheduler responsible for in Kubernetes?**

**Docker internals**

- **Explain layers in Docker — how they are built, cached, and stacked at runtime.**
- **What is the difference between running a workload in a virtual machine and in a Docker container?**
- **Does a Docker container have its own kernel?**
- **Which storage drivers does Docker support, and what are the trade-offs between them?**
- **What are the Docker network types? Explain each in detail.**
- **Which network type would you use to isolate communication between two containers?**
- **What are cgroups and namespaces in Docker, and what does each one control?**

**Linux internals and operations**

- **How do you inspect running processes on Linux?**
- **Walk through the Linux boot process.**
- **When a Linux machine reboots, which stages or layers are restarted, and in what order?**
- **How do you check the load on a Linux machine, and how do you read the numbers?**
- **In which directory are kernel logs stored?**
- **How do you terminate a running process, and what is the difference between the signals you can send?**
- **What are the possible states of a Linux process or machine?**
- **When you run `top`, what does each field and column mean?**

**The request path and TLS**

- **When you type `google.com` into a browser, what happens end to end behind the scenes?**
- **How does SSL/TLS work?**
- **Given a client and a remote machine, how do the certificates get exchanged and validated between them?**

## Example

```text
Arrise Solutions — DevOps Engineer (7 YOE), reported round
30 questions

  AWS networking              7   three-tier, ALB vs NLB, subnets, NAT egress,
                                  NAT placement, cross-cloud VPC, CloudFront
  Kubernetes                  5   architecture, CoreDNS, CNI, kube-proxy, scheduler
  Docker internals            7   layers, VM vs container, kernel, storage drivers,
                                  network types, container isolation, cgroups+ns
  Linux internals             8   processes, boot, reboot stages, load, kernel logs,
                                  kill signals, process states, top fields
  Request path / TLS          3   browser to response, TLS handshake, cert exchange

THE PATTERN
  Every question is one level below the standard answer. "Does Docker have a
  kernel" and "which subnet does a NAT gateway run in" are not definitions —
  they check whether you have actually reasoned about the mechanism.
```

## Interview tips

- "Does Docker have a kernel in place" is the trap of the round. A container shares the host kernel and has no kernel of its own — that is precisely the difference from a virtual machine, which boots its own kernel under a hypervisor. Answer both halves in one breath, because the VM-versus-Docker question is the same question asked twice. See [how namespaces, cgroups, and capabilities isolate a container](../docker/how-do-namespaces-cgroups-and-capabilities-isolate-a-container.md).
- A NAT gateway lives in a _public_ subnet and serves _private_ subnets. Candidates reverse this constantly. It needs a route to the internet gateway, and the private subnet's route table sends `0.0.0.0/0` to it. See [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md).
- For container isolation, the expected answer is a user-defined bridge network — containers on the same user-defined bridge reach each other by name, and containers on different networks cannot see each other at all. Add `--internal` to block egress. Then contrast with `none` for total isolation. See [Docker network types](../docker/what-are-docker-network-types-bridge-host-overlay-macvlan.md).
- "C name and namespace" is a transcription of cgroups and namespaces. Keep the split crisp: namespaces control what a process can _see_ (PID, network, mount, UTS, IPC, user), cgroups control how much it can _use_ (CPU, memory, I/O). See [how namespaces, cgroups, and capabilities isolate a container](../docker/how-do-namespaces-cgroups-and-capabilities-isolate-a-container.md).
- Storage drivers should reach `overlay2` as the modern default, with a sentence on why `devicemapper` and `aufs` are legacy and what copy-on-write means for write-heavy containers. Then say volumes exist because layers are the wrong place for persistent data. See [Docker architecture](../docker/explain-docker-architecture.md).
- The Linux block rewards precision: kernel logs come from the ring buffer via `dmesg` and are persisted under `/var/log` as `kern.log` or through `journalctl -k`; load average is three numbers over 1, 5, and 15 minutes and must be read relative to core count; process states are R, S, D, T, Z, and the uninterruptible D state usually means blocked on I/O. See [basic Linux commands](../linux-administration/what-are-the-basic-linux-commands-every-devops-engineer-should-know.md) and [debugging a Linux performance problem](../linux-administration/how-do-you-debug-a-linux-performance-problem-from-first-principles.md).
- For boot and reboot stages, walk BIOS or UEFI, bootloader, kernel and initramfs, then `systemd` bringing up targets in dependency order. The reboot question is asking which of those repeat, so say the kernel is reloaded and every service unit restarts in target order. See [what systemd is](../linux-administration/what-is-systemd.md).
- On killing processes, do not just say `kill -9`. Explain that `SIGTERM` asks politely and lets the process clean up, `SIGKILL` cannot be caught or ignored, and a process stuck in D state will not die from either because it is blocked in the kernel. See [managing services in Linux](../linux-administration/how-do-you-manage-services-in-linux.md).
- AWS-to-IBM-Cloud connectivity has two defensible answers: a site-to-site IPsec VPN over the internet between the two clouds' gateways, or a private circuit through a colocation provider such as Direct Connect paired with IBM's equivalent. Mention overlapping CIDRs as the practical hazard. See [the real trade-offs of multi-cloud](../cloud-engineering/what-are-the-real-trade-offs-of-multi-cloud.md).
- The browser question is the best opportunity in the round to show breadth, so keep it structured: cache and DNS resolution, TCP handshake, TLS handshake, HTTP request, load balancer and reverse proxy, application and database, response, then render. There is a dedicated walkthrough at [what happens when a user opens your application in a browser](../network-security/what-happens-when-a-user-opens-your-application-in-a-browser.md).
- Both TLS questions want the handshake mechanism, not "it encrypts traffic": certificate presented and validated against a trusted CA chain, hostname checked, key agreement, then symmetric encryption for the session. See [what SSL/TLS is](../network-security/what-is-ssl-tls.md).
- kube-proxy does not communicate with nodes; it runs _on_ each node, watches Services and EndpointSlices from the API server, and programs iptables or IPVS rules locally. Correcting the premise politely is a strong signal. See [main components of Kubernetes architecture](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md).

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
