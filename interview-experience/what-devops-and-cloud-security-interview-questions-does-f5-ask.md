---
title: "What DevOps and cloud security interview questions does F5 ask?"
id: 333
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - f5
  - network-security
  - devsecops
  - infrastructure-as-code
  - kubernetes
  - aws-engineering
  - secops
---

# What DevOps and cloud security interview questions does F5 ask?

## Questions

**Web application security**

- **What is a web application firewall?**
- **How would you protect a cloud-hosted web application against the OWASP Top 10?**
- **What are the best practices for cloud security generally?**
- **An instance has a security group, a WAF, and DDoS protection enabled. Will that combination protect it from a bot attack?**
- **If an instance already has a security group, do you actually need a network ACL as well?**

**HTTP semantics**

- **What are HTTP request headers, and what are the HTTP methods?**
- **You send the same record — same name, same location — twice through a `PUT` request. What does the database end up holding?**
- **Why is `PUT` described as idempotent? And if you send another request with the same name but a different location, what does the database store then?**

**The request path**

- **What happens in the background when you type an address such as `www.google.com` into a browser?**
- **What is the SSL/TLS handshake?**
- **What is DNS resolution? On a brand-new machine with an empty cache, walk through the process step by step.**

**Terraform**

- **What happens if the `tfstate` file is deleted?**
- **What is the `.terraform.lock.hcl` file for?**
- **What Terraform best practices do you follow?**

**AWS networking**

- **What is the difference between a Transit Gateway and a VPC?**

**Kubernetes**

- **What is Kubernetes? Explain its architecture.**
- **Can a Pod run on the control-plane node itself?**
- **Have you deployed a security application on Kubernetes?**

## Example

```text
F5 — Associate Consultant, reported round
18 questions

  Web application security    5   WAF, OWASP Top 10 in cloud, cloud security
                                  best practices, WAF+SG+DDoS vs bots,
                                  do you need NACL if you have SG
  HTTP semantics              3   headers + methods, double PUT, why PUT is
                                  idempotent
  Request path                3   browser to response, TLS handshake,
                                  cold-cache DNS resolution
  Terraform                   3   deleted state, lock file, best practices
  Kubernetes                  3   architecture, Pod on control plane,
                                  security app on K8s
  AWS networking              1   Transit Gateway vs VPC

READ THE COMPANY
  F5 sells application delivery and security. The round is weighted toward
  HTTP, TLS, DNS, and WAF — revise the request path and HTTP method
  semantics before revising Kubernetes.
```

## Interview tips

- The WAF-plus-DDoS-plus-security-group question is the trap of the round, and the answer is a qualified no. Those three controls stop different things: a security group filters by IP and port, DDoS protection absorbs volumetric floods, and a WAF matches known attack signatures and rules. A sophisticated bot sending well-formed, low-volume, legitimate-looking requests — credential stuffing, scraping, inventory hoarding — passes all three. Bot mitigation needs its own layer: behavioural fingerprinting, rate limiting per identity, CAPTCHA or challenge, and reputation feeds. Naming the gap rather than reciting the controls is what wins this. See [what a web application firewall is](../network-security/what-is-a-web-application-firewall-waf.md).
- Similarly, "do I need a NACL if I have a security group" is a defence-in-depth question, not a yes-or-no. Strictly you can operate with security groups alone, and many teams do — but NACLs are stateless, subnet-wide, and support explicit `deny`, which is the only way to block a specific hostile IP range across everything in the subnet regardless of per-instance configuration. Say that, and say that NACLs are a coarse blast-radius control while security groups are the primary mechanism. See [defence in depth for a cloud network](../network-security/how-do-you-design-defence-in-depth-for-a-cloud-network.md) and [network segmentation](../network-security/what-is-network-segmentation.md).
- The `PUT` idempotency pair is the sharpest pure-HTTP question in this collection, and it has an exact answer. `PUT` replaces the resource at a given URI, so sending the identical body twice leaves the database with _one_ record in the same state — the second request has no additional effect, which is the definition of idempotent. Change the location and keep the same identifier and the record is _overwritten_, so the database holds one row with the new location, not two rows. Then draw the contrast that makes the answer complete: `POST` is not idempotent and would create a second record each time, which is why `PUT` needs a client-supplied identifier and `POST` does not.
- On methods and headers, do not just list them. Group them by property: safe methods (`GET`, `HEAD`, `OPTIONS`) that do not change state, idempotent ones (`GET`, `PUT`, `DELETE`, `HEAD`), and the non-idempotent `POST` and `PATCH`. For headers, name the ones that matter operationally — `Host` for virtual hosting, `Authorization`, `Content-Type`, `X-Forwarded-For` for the real client IP behind a proxy, and `Cache-Control`.
- The cold-cache DNS walkthrough is asked explicitly step by step, so answer it that way: browser cache, then OS cache, then `/etc/hosts`, then the configured recursive resolver, which queries a root server for the TLD nameserver, then the TLD nameserver for the authoritative nameserver, then the authoritative server for the record — then it caches by TTL and returns. Mention that the recursive resolver does the walking and the client only asks once. There is a fuller version at [what happens when a user opens your application in a browser](../network-security/what-happens-when-a-user-opens-your-application-in-a-browser.md).
- For the TLS handshake, give the modern version: `ClientHello` with supported versions and cipher suites plus a key share, `ServerHello` with the chosen suite and its own key share and certificate, certificate chain validation against a trusted CA plus hostname check, then keys derived and the session encrypted symmetrically. Add that TLS 1.3 completes in one round trip and that the certificate proves identity while the key exchange provides secrecy — those are separate jobs, which is the point most candidates miss. See [what SSL/TLS is](../network-security/what-is-ssl-tls.md).
- OWASP Top 10 protection should be answered in layers rather than as a list of ten items: input validation and parameterised queries for injection, proper authentication and session management, authorisation checks server-side for broken access control, dependency scanning for vulnerable components, secure defaults and hardened configuration, logging and monitoring, plus a WAF as compensating control at the edge. Say the WAF is a safety net, not a substitute for fixing the code. See [SAST, DAST, IAST, and SCA](../devsecops/what-is-the-difference-between-sast-dast-iast-and-sca.md) and [what shift-left security means](../devsecops/what-does-shift-left-security-mean.md).
- Deleted state file: Terraform loses its mapping to real resources, so the next plan proposes creating everything that already exists. Recovery is object versioning on the backend, the local `.tfstate.backup`, or importing resources one by one. Say that the infrastructure itself is untouched — only Terraform's knowledge of it is gone. See [recovering a lost or corrupted Terraform state file](../infrastructure-as-code/how-do-you-recover-a-lost-or-corrupted-terraform-state-file.md).
- The lock file is `.terraform.lock.hcl` and it pins provider versions and their checksums so every machine and CI run resolves identically. Say it must be committed to version control — that is the point of the question — and that `terraform init -upgrade` is what changes it.
- Yes, a Pod can run on a control-plane node. Explain the mechanism rather than just answering: managed clusters do not let you, and self-managed control-plane nodes carry a `NoSchedule` taint, so a workload needs a matching toleration — and the control plane's own components run there as static Pods regardless. Add that you would not do it in production because a busy workload can starve the API server and etcd. See [controlling which node a Pod runs on](../kubernetes/how-do-you-control-which-node-a-pod-runs-on.md).
- Transit Gateway versus VPC is comparing a network to a router, so say that plainly: a VPC is an isolated virtual network containing your subnets and resources; a Transit Gateway is a regional hub that interconnects many VPCs and on-premises connections with transitive routing, which peering cannot do. See [structuring a multi-account AWS organisation](../aws-engineering/how-do-you-structure-a-multi-account-aws-organisation.md).

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
