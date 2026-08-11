---
title: "What release engineering interview questions does Morgan Stanley ask?"
id: 349
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - morgan-stanley
  - linux-administration
  - network-security
  - scripting-and-automation
  - cloud-engineering
  - kubernetes
---

# What release engineering interview questions does Morgan Stanley ask?

## Questions

**Linux internals**

- **What are ulimits?**
- **Your script fails with "Too many open files". What is the fix?**
- **What is the `/proc` directory for in Linux?**
- **What are stdin, stdout, and stderr?**
- **What is the difference between a hard link and a soft link?**
- **Which Linux command creates a symbolic link?**
- **The date on a VM is behind the current date. How do you fix that?**

**Text processing**

- **What is the `sed` command for?**
- **Using `sed`, how do you remove the first and last line of a file?**
- **How do you extract errors from log files?**

**DNS, domains, and certificates**

- **What are A and CNAME records?**
- **Can you add multiple aliases to a domain?**
- **You have two different domains. How do you enable communication between them?**
- **How do you create certificates covering multiple subdomains?**

**Proxies and web security**

- **What is the difference between a reverse proxy and a forward proxy?**
- **What is Cross-Origin Resource Sharing?**
- **What is the difference between ingress and egress?**

**Scripting**

- **Write Python to find a missing file.**

## Example

```text
Morgan Stanley — Release Engineer (7 YOE), reported round
18 questions

  Linux internals             7   ulimits, "too many open files", /proc,
                                  stdin/stdout/stderr, hard vs soft link,
                                  ln -s, clock drift on a VM
  DNS / domains / certs       4   A vs CNAME, multiple aliases, cross-domain
                                  communication, multi-subdomain certificates
  Text processing             3   sed purpose, strip first + last line,
                                  extract errors from logs
  Proxies / web security      3   reverse vs forward proxy, CORS,
                                  ingress vs egress
  Scripting                   1   Python: find a missing file

A RELEASE ENGINEERING ROUND, NOT A CLOUD ONE
  No Terraform, no Kubernetes objects, no CI/CD tooling. It is Linux
  internals, DNS, certificates, and text processing — the things that
  actually break a release at 2am in a bank.
```

```bash
# "Remove the first and last line" — the classic two-part sed answer.
sed '1d;$d' file.txt

# The ulimit chain, in the order you would actually work through it:
ulimit -n                      # current soft limit for this shell
cat /proc/<pid>/limits         # what the RUNNING process actually has
ls /proc/<pid>/fd | wc -l      # how many descriptors it is really holding
```

## Interview tips

- The "too many open files" question is the anchor of this round and it deserves a layered answer rather than "raise the ulimit". Work outward: check the current limit with `ulimit -n`, then check what the _running_ process has via `/proc/<pid>/limits`, then count actual descriptors with `ls /proc/<pid>/fd | wc -l`. Raise the soft and hard limits properly — `/etc/security/limits.conf` for login sessions, but `LimitNOFILE` in the `systemd` unit for a service, because `limits.conf` does not apply to `systemd`-started processes, and that is the detail most candidates miss. Then say the important part: a rising descriptor count usually means the application is leaking sockets or file handles, so raising the limit buys time and the real fix is closing them. See [troubleshooting SSH failures, high CPU, and disk space](../linux-administration/how-do-you-troubleshoot-ssh-failures-high-cpu-and-disk-space-on-linux-servers.md).
- That answer connects directly to the `/proc` question, so link them: `/proc` is a virtual filesystem exposing kernel and process state as files — `/proc/<pid>/` for a process's limits, environment, open descriptors, and status, plus system-wide entries such as `/proc/cpuinfo`, `/proc/meminfo`, and `/proc/sys/` for tunable kernel parameters. Say it lives in memory, not on disk, which is why `ps`, `top`, and `free` all read from it.
- The clock-drift question wants the modern answer: check status with `timedatectl` and `chronyc tracking` (or `ntpq -p` on older systems), confirm the NTP service is running and reachable, then let it correct — `chronyc makestep` forces an immediate step rather than a slow slew. Add the two details that show real experience: a large step can break applications that assume monotonic time, and a wrong clock breaks TLS certificate validation and Kerberos authentication, which in a bank means logins start failing. That consequence is why the question is asked. See [what systemd is](../linux-administration/what-is-systemd.md).
- `sed '1d;$d' file` removes the first and last line — `1` addresses line one, `$` addresses the last, and `d` deletes. Say that `sed` is a stream editor that applies commands line by line, and that `-i` edits in place while `-i.bak` keeps a backup. Being able to produce the one-liner instantly is the whole point of the question. See [analysing logs with grep, awk, and sed](../linux-administration/how-do-you-analyse-logs-and-text-files-with-grep-awk-and-sed.md).
- For extracting errors from logs, go beyond `grep -i error`: use `grep -iE 'error|fatal|exception'` with `-A5 -B5` for surrounding context, `grep -c` to count, `awk` when you need a specific field rather than a substring, and `journalctl -p err -u <service> --since "1 hour ago"` on a `systemd` host. Mention that in a structured-logging setup you would query by severity field rather than pattern-match text.
- The multi-subdomain certificate question has two correct answers and naming both wins it: a wildcard certificate for `*.example.com`, which covers one level only — so `a.b.example.com` is _not_ covered by `*.example.com` — or a SAN certificate listing each subdomain explicitly, which also lets you cover several distinct domains in one certificate. Say that wildcards are convenient but concentrate risk in one private key, and that ACME with DNS-01 validation is how you automate wildcard issuance. See [what SSL/TLS is](../network-security/what-is-ssl-tls.md).
- A versus CNAME should come with the two rules that matter operationally: a CNAME cannot coexist with other records at the same name, and it cannot be placed at a zone apex — which is why providers offer alias or ANAME records for the bare domain. For "multiple aliases to a domain", the answer is yes: many CNAMEs can point at one target, and one name can carry multiple A records for round-robin, but you cannot have several CNAMEs at the _same_ name. See [managing DNS and global traffic routing](../cloud-engineering/how-do-you-manage-dns-and-global-traffic-routing.md).
- "Communication between two different domains" is ambiguous, and the strongest move is to say so and answer both readings. If it means web browsers, this is the CORS question — the browser blocks cross-origin requests unless the server returns `Access-Control-Allow-Origin`, with a preflight `OPTIONS` for non-simple requests. If it means DNS or network domains, it is conditional forwarding and zone delegation, or in a Windows estate a trust relationship between Active Directory domains. Offering both and asking which they mean beats guessing.
- Reverse versus forward proxy is a direction question: a forward proxy sits in front of _clients_, which configure it deliberately, and is used for egress control, filtering, and caching outbound requests; a reverse proxy sits in front of _servers_, is invisible to clients, and handles TLS termination, load balancing, caching, and routing inbound. Say "forward protects and controls the client side, reverse protects and fronts the server side". Then tie ingress versus egress to the same axis — inbound versus outbound traffic — and note that in Kubernetes the words are also object and policy names, where `Ingress` is an API object and NetworkPolicy has `ingress` and `egress` rule sections.
- On the Python "find a missing file" task, clarify the requirement out loud before coding, because there are two readings: check whether a specific path exists (`pathlib.Path(p).exists()`, or `os.access` if you need to test readability), or find which file is missing from an expected set — in which case compute the set difference between the expected filenames and the directory listing. The set-difference version is almost certainly what a release engineer would actually need, since it is how you verify a deployment delivered every artefact. Handle the edge cases aloud: a broken symlink exists as a link but not as a target, and a race between checking and opening is why `try`/`except FileNotFoundError` is safer than a pre-check. See [what you use Python for as a DevOps engineer](../scripting-and-automation/what-do-you-use-python-for-as-a-devops-engineer.md).
- stdin, stdout, and stderr are file descriptors 0, 1, and 2. Give the redirection forms as well as the definitions — `2>&1` merges stderr into stdout, `>` truncates while `>>` appends, `2>/dev/null` discards errors — and say why the split exists: so you can pipe real output onward while still seeing diagnostics.
- Hard versus soft link needs the consequences, not just the definition: a hard link is a second directory entry pointing at the same inode, so it cannot cross filesystems or link a directory, and the data survives until the last link is gone; a symlink stores a path, can cross filesystems and point at directories, and dangles if the target moves. `ln -s target linkname` creates the symlink — note that omitting `-s` gives you a hard link, which is the trap in the pair. See [Linux filesystem hierarchy](../linux-administration/what-is-linux-file-system-hierarchy.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#20`): [What is the difference between Continuous Delivery and Continuous Deployment?](../cicd/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)
- [[What is the difference between SRE, DevOps, and Platform Engineering?]] (`#232`): [What is the difference between SRE, DevOps, and Platform Engineering?](../site-reliability-engineering/what-is-the-difference-between-sre-devops-and-platform-engineering.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
