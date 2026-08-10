---
title: "What DevOps interview questions does Techdome ask?"
id: 385
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - techdome
  - docker
  - kubernetes
  - infrastructure-as-code
  - container-orchestration-advanced
---

# What DevOps interview questions does Techdome ask?

## Questions

**Kubernetes**

- **Explain the Kubernetes architecture.**
- **What is the difference between a Deployment and a StatefulSet?**

**Docker**

- **Explain Docker networking and the network types. Which is the default?**
- **What is the difference between a Docker image and a container?**
- **What is the difference between a bind mount and a volume?**

**Terraform**

- **What are Terraform provisioners?**
- **What is the Terraform state file?**

## Example

```text
Techdome — DevOps Engineer, reported round
7 questions

  Docker                      3   networking types + the default,
                                  image vs container, bind mount vs volume
  Kubernetes                  2   architecture, Deployment vs StatefulSet
  Terraform                   2   provisioners, state file

A SHORT DEFINITIONS ROUND
  Seven questions, all standard, no scenarios. This is a screening filter —
  the goal is to be crisp and complete, not deep. Every answer should be two
  or three sentences plus one differentiator that shows real use.
```

## Interview tips

- Docker networking is the most detailed question here, so give the types with their purpose and then name the default explicitly. **`bridge`** is the default for standalone containers — a private internal network on the host with NAT for outbound traffic and published ports for inbound; **`host`** removes network isolation so the container shares the host's stack, giving maximum performance and no port mapping but risking port conflicts; **`none`** disables networking entirely; **`overlay`** spans multiple hosts, which is what Swarm services use; **`macvlan`** gives a container its own MAC address so it appears as a physical device on the LAN; and **`ipvlan`** is the similar layer-3 variant. Then add the detail that shows real use: the _default_ `bridge` network does not provide DNS-based service discovery, whereas a **user-defined** bridge does — so containers on a user-defined bridge can reach each other by name, and containers on different user-defined networks cannot see each other at all. That is why Compose creates its own network. See [Docker network types](../docker/what-are-docker-network-types-bridge-host-overlay-macvlan.md).
- Image versus container should be framed as class versus instance, then extended with the layer model: an image is an immutable, layered, read-only template built from a Dockerfile and identified by a digest; a container is a running instance of it with a thin writable layer on top, plus its own namespaces and cgroups. Say the two consequences that matter operationally — anything written to the writable layer is lost when the container is removed, which is why volumes exist, and one image can back many containers, which is why images are the unit you version and promote. See [image versus container](../docker/what-is-the-difference-between-docker-image-and-docker-container.md).
- Bind mount versus volume has a clear recommendation attached: a bind mount maps a specific host path into the container, so it depends on the host's filesystem layout, can be affected by host permissions and SELinux, and is mainly a development convenience for live-reloading source code. A volume is managed by Docker in its own storage area, is portable across hosts, can use drivers for network or cloud storage, is backed up and pruned through Docker's own commands, and is the production choice for persistent data. Add `tmpfs` mounts as the third option for data that must never touch disk, such as an in-flight secret.
- Deployment versus StatefulSet is best answered on **identity** rather than on the word "stateful": a Deployment's Pods are interchangeable, get random name suffixes, and share whatever volume you give them; a StatefulSet gives each replica a stable ordinal name (`db-0`, `db-1`), a stable DNS record through a headless Service, and its own PersistentVolumeClaim created from `volumeClaimTemplates` that follows it across restarts — with creation, scaling, and updates happening in order. Then give the consequence that proves you understand it: if `db-0` dies, its replacement is called `db-0` again and re-attaches the same volume, which is exactly what lets a database rejoin its cluster as the same member. Say that this is why you cannot make a Deployment properly stateful by bolting on a single PVC — scale it past one replica and every Pod tries to mount the same volume. See [StatefulSets](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md).
- For the Kubernetes architecture question, walk it in two halves and finish with the mechanism rather than the list. Control plane: the API server as the single front door and the only component that talks to etcd, etcd as the consistent key-value store, the scheduler binding Pods to nodes, the controller manager running reconciliation loops, and the cloud controller manager integrating with the provider. Node: the kubelet managing containers and reporting status, kube-proxy programming Service routing rules, and the container runtime via CRI. Then say the thing that ties it together — every component communicates _through_ the API server, and controllers continuously reconcile actual state toward declared state, which is why deleting a Deployment-owned Pod simply gets you a new one. See [main components of Kubernetes architecture](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md).
- Terraform provisioners should come with HashiCorp's own framing, because that is what distinguishes a considered answer: `local-exec` runs a command where Terraform is running, `remote-exec` runs one on the created resource over SSH or WinRM, and `file` copies content to it, with `connection` blocks supplying credentials and destroy-time variants available. They are documented as a **last resort**, because they are not tracked in state, have no meaningful retry or idempotency semantics, and require network reachability from wherever Terraform executes — which breaks in CI behind a bastion. Say what you use instead: `user_data` or cloud-init, a pre-baked image, or a configuration-management tool. See [what are Terraform providers](../infrastructure-as-code/what-are-terraform-providers.md).
- On the state file, cover four things: what it holds (the mapping from configuration addresses to real resource IDs, plus attributes and dependency metadata), why it exists (so Terraform can compute a diff between desired and actual), where it belongs (a remote backend that is encrypted, versioned, and lockable), and the risk (it can contain secrets such as generated passwords in plain text). Add that locking is what prevents two concurrent applies from corrupting it, and that versioning is what lets you recover from a bad write. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md) and [recovering a lost or corrupted state file](../infrastructure-as-code/how-do-you-recover-a-lost-or-corrupted-terraform-state-file.md).
- In a seven-question round each answer is worth roughly 14%, so do not give one-line replies — but also do not ramble. The pattern that works is definition, then mechanism, then one consequence or trade-off, then stop and let them follow up. Volunteering the adjacent detail (user-defined bridges for DNS, why a Deployment plus PVC breaks at scale, why provisioners are a last resort) is what turns a definitions screen into a strong impression.

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
