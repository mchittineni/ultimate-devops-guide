---
title: "What DevOps interview questions does L and T ask?"
id: 346
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - l-and-t
  - docker
  - kubernetes
  - version-control
  - configuration-management
  - cloud-migration
  - container-orchestration-advanced
---

# What DevOps interview questions does L and T ask?

## Questions

**Git**

- **What is `git cherry-pick`?**
- **What does `git checkout` do?**
- **Explain your Git branching strategy.**
- **What is a Git merge conflict?**

**Docker and containerisation**

- **What is a Dockerfile?**
- **What is Docker Compose?**
- **What does `depends_on` do in Docker Compose?**
- **What is the difference between virtualisation and containerisation?**
- **What is your strategy for containerising an application?**
- **What is your approach to migrating an application from a monolith to containers?**
- **Can a container restart itself? Explain how.**

**Kubernetes**

- **Explain the Kubernetes architecture.**
- **What is a load balancer in Kubernetes?**
- **What is an ingress controller?**
- **What is kube-proxy?**
- **How do you get a static IP for a Kubernetes workload, and how do you manage it?**
- **How is access control handled in Kubernetes?**
- **How are you managing secrets in Kubernetes?**
- **Can you delete a Pod, and can multiple containers run inside one?**

**Ansible**

- **What are Ansible roles?**
- **What is Ansible Vault?**
- **How do you manage variables for different environments in Ansible?**
- **How do you run an Ansible playbook, and what are the different options?**

## Example

```text
L&T — DevOps Engineer (9 YOE, 4 in DevOps), reported round
23 questions

  Kubernetes                  8   architecture, LoadBalancer, ingress
                                  controller, kube-proxy, static IP, RBAC,
                                  secrets, pod deletion + multi-container
  Docker / containerisation   7   Dockerfile, Compose, depends_on, VM vs
                                  container, containerisation strategy,
                                  monolith migration, container self-restart
  Ansible                     4   roles, Vault, per-environment variables,
                                  running playbooks with options
  Git                         4   cherry-pick, checkout, branching, conflicts

NOTE THE ABSENCE
  No Terraform and no cloud-provider questions at all. This round is Docker,
  Kubernetes, Ansible, and Git — the on-premises-to-container toolchain,
  which fits an engineering conglomerate modernising legacy applications.
```

## Interview tips

- "Can a container restart itself?" is the trap in this round, and the precise answer is no — a process cannot restart its own container, because when PID 1 exits the container is finished. What restarts it is something _outside_: Docker's `--restart` policy (`no`, `on-failure`, `always`, `unless-stopped`), Compose's `restart:` key, or in Kubernetes the kubelet acting on the Pod's `restartPolicy` with exponential backoff — which is exactly what `CrashLoopBackOff` is. Saying "the container does not restart itself; the supervisor above it does" is the answer. See [Docker architecture](../docker/explain-docker-architecture.md).
- `depends_on` is a small question with a well-known catch, so give the catch: it controls _start order_ only, not readiness — Compose will start the database container before the application, but it does not wait for the database to be ready to accept connections. The fix is `depends_on` with `condition: service_healthy` plus a `healthcheck`, or making the application retry its connection. Application-level retry is the more robust answer because it also survives a restart in production. See [what Docker Compose is](../docker/what-is-docker-compose.md).
- The static IP question needs you to separate the layers, because Kubernetes deliberately does not give Pods stable IPs. For inbound traffic, you reserve a static public IP with the cloud provider and attach it to the LoadBalancer Service via annotations, or put a single ingress controller behind one reserved address so every service shares it. For _outbound_ traffic needing a fixed source IP — usually to satisfy a partner's allowlist — the answer is a NAT gateway with an Elastic IP, or an egress gateway. Say that Pod IPs are ephemeral by design and Services exist to solve exactly that. See [exposing an application in Kubernetes](../kubernetes/how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md).
- The monolith-to-containers question is the most open in the round, so answer it as a staged plan rather than a philosophy. Start by containerising the monolith as-is — lift and shift into an image — so you gain reproducible builds without changing behaviour. Then externalise configuration and state so the container becomes disposable: configuration into environment variables or ConfigMaps, sessions into Redis, files onto object storage or a shared volume, logs to stdout. Then add health endpoints and graceful shutdown so an orchestrator can manage it. Only then peel off services at genuine seams, starting with the least coupled. Say that "strangler fig" is the pattern and that rewriting everything at once is the failure mode. See [what container orchestration is and why you need it](../container-orchestration-advanced/what-is-container-orchestration-and-why-do-you-need-it.md).
- For containerisation strategy generally, name the properties a good image has: single concern per container, minimal base, multi-stage build so the toolchain does not ship, non-root user, no secrets baked in, configuration injected at runtime, and logs to stdout rather than files. See [reducing Docker image size and build time](../docker/how-do-you-reduce-docker-image-size-and-build-time.md) and [what a Dockerfile is](../docker/what-is-dockerfile.md).
- Virtualisation versus containerisation should reach the kernel in one sentence: a VM runs its own guest kernel on a hypervisor and isolates at the hardware level; a container shares the host kernel and isolates with namespaces and cgroups, which is why it boots in milliseconds and costs far less memory. Add the trade-off — VMs give stronger isolation and can run a different OS, which is why regulated workloads sometimes still require them.
- The "delete a Pod and multiple containers" question is two things at once. Yes you can delete a Pod, but if it is owned by a Deployment or ReplicaSet the controller immediately creates a replacement — that is the reconciliation loop, and saying so is the point. And yes, a Pod can hold several containers sharing its network namespace, IP, and volumes, which is what makes sidecars, init containers, and log shippers possible. See [what a Pod is](../kubernetes/what-is-a-pod-in-kubernetes.md).
- Kubernetes secrets management deserves an honest answer: built-in Secrets are only base64-encoded, not encrypted, so you enable encryption at rest for etcd, restrict access with RBAC, and for anything sensitive use an external store — Vault, or a cloud secret manager surfaced through the External Secrets Operator or the Secrets Store CSI driver. Add that a secret mounted as a file can be updated on rotation while one injected as an environment variable cannot. See [managing secrets in CI/CD pipelines](../devsecops/how-do-you-manage-secrets-in-ci-cd-pipelines.md).
- Access control in Kubernetes is a layered answer: authentication via certificates, tokens, or OIDC; authorisation via RBAC with Roles and ClusterRoles bound to users, groups, or service accounts; then admission control — Pod Security Admission or a policy engine — enforcing what a workload may do once allowed. Naming all three stages beats describing RBAC alone. See [how RBAC works in Kubernetes](../kubernetes/how-does-rbac-work-in-kubernetes.md).
- kube-proxy is frequently described wrongly, so be precise: it runs on every node as a DaemonSet, watches Services and EndpointSlices from the API server, and programs iptables or IPVS rules locally so traffic to a ClusterIP reaches a real Pod. It does not proxy traffic itself in iptables mode. Mention that eBPF-based CNIs such as Cilium can replace it entirely.
- The four Ansible questions have short exact answers, so know them cold. Roles are a directory convention (`tasks`, `handlers`, `templates`, `files`, `vars`, `defaults`, `meta`) that packages reusable automation. Vault encrypts files or individual variables, run with `--ask-vault-pass` or `--vault-password-file`. Per-environment variables live in `group_vars/<env>/` and `host_vars/`, with `defaults` lowest and `extra-vars` highest in precedence. Playbooks run with `ansible-playbook site.yml -i inventory` plus the options worth naming: `--check` for a dry run, `--diff`, `--limit`, `--tags` and `--skip-tags`, `-e` for extra variables, `-vvv` for verbosity, and `--become` for privilege escalation. See [what Ansible is](../infrastructure-as-code/what-is-ansible.md).
- `git checkout` is worth answering with the modern split: it historically did two unrelated jobs — switching branches and restoring files — which is why Git added `git switch` and `git restore`. Mentioning that shows you keep current. See [git merge, rebase, and cherry-pick](../version-control/what-is-the-difference-between-git-merge-rebase-and-cherry-pick.md) and [handling merge conflicts](../version-control/how-to-handle-merge-conflicts-in-git.md).
- Branching strategy is asked twice in this round. Pick the model you have actually used, name it, and say how a hotfix reaches production and how branches map to environments. See [Git branching strategy](../version-control/what-is-git-branching-strategy.md).

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
