---
title: "What DevOps interview questions does NPCI ask?"
id: 350
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - npci
  - docker
  - kubernetes
  - container-orchestration-advanced
  - network-security
---

# What DevOps interview questions does NPCI ask?

## Questions

**Docker**

- **You can reach the application from outside the container, but from inside the container you see packet loss. How do you troubleshoot that?**
- **How do you get logs at the Docker level?**
- **You have a two-tier application with one container running the frontend and one running the database. You need the database to start first. How do you achieve that?**

**Kubernetes networking and storage**

- **How do you reach Pod 2 from Pod 1 without using a Service?**
- **What is the Container Network Interface?**
- **What is a CSI driver?**
- **What is the difference between static and dynamic volume provisioning? Explain with a use case for each.**
- **What is automatic volume expansion?**

## Example

```text
NPCI — DevOps Engineer (5 YOE), reported round
8 questions

  Kubernetes storage          3   static vs dynamic provisioning + use cases,
                                  CSI driver, automatic volume expansion
  Kubernetes networking       2   Pod-to-Pod without a Service, CNI
  Docker                      3   packet loss from inside the container,
                                  Docker-level logs, ordered start (db first)

STORAGE-WEIGHTED, WHICH IS UNUSUAL
  Three of eight questions are about volumes — provisioning modes, CSI, and
  expansion. Most DevOps rounds barely touch storage. For a payments
  organisation running stateful systems, it is the core of the round.
```

## Interview tips

- Pod-to-Pod without a Service is the question that checks whether you understand the Kubernetes network model rather than just its objects. Every Pod gets its own cluster-routable IP and can reach every other Pod directly with no NAT, so you can simply `curl` the target Pod's IP and container port — `kubectl get pod -o wide` gives it to you. Then say why nobody does this in practice: Pod IPs are ephemeral and change on every restart, so a Service exists to provide a stable virtual IP and DNS name. Add the two legitimate exceptions — a headless Service giving per-Pod DNS records, which is how StatefulSet members find each other, and using the downward API or an environment variable to pass a peer address. See [what a Pod is](../kubernetes/what-is-a-pod-in-kubernetes.md) and [what a Service is](../kubernetes/what-is-a-service-in-kubernetes.md).
- Static versus dynamic provisioning needs a use case each, because they explicitly asked for one. Static means an administrator creates PersistentVolumes in advance and a claim binds to a matching one — the use case is pre-existing storage you do not control, such as an NFS export, an on-premises SAN LUN, or a volume containing data that already exists. Dynamic means a StorageClass with a provisioner creates the volume on demand when a PVC appears — the use case is self-service, where application teams request storage without an administrator in the loop, which is how nearly every cloud cluster runs. Say that dynamic is the default you would choose and static is what you fall back to for legacy or shared storage.
- Automatic volume expansion has a precise mechanism worth naming exactly: set `allowVolumeExpansion: true` on the StorageClass, then edit the PVC to request a larger size and the CSI driver resizes the underlying volume, with the filesystem grown online by the kubelet if the driver supports it. Give the two constraints — you can only grow, never shrink, and older setups needed a Pod restart to complete the filesystem resize. Mention that this is why you should not over-provision from the start.
- CSI and CNI are asked side by side, so contrast them as the same idea applied to two domains: both are pluggable interfaces that moved vendor-specific code out of the Kubernetes core so a storage or network vendor can ship and version a driver independently. CSI handles the storage lifecycle — provision, attach, mount, snapshot, resize; CNI handles Pod networking — IP allocation and wiring the interface into the dataplane. Say that a NetworkPolicy does nothing unless the CNI enforces it, which is the practical consequence people miss. See [container runtime interface](../container-orchestration-advanced/what-is-container-runtime-interface-cri.md).
- The packet-loss-from-inside-the-container question is the best diagnostic scenario here, and the asymmetry is the clue: inbound works, outbound is lossy, so the problem is on the egress path, not the published port. Work through it out loud — check the container's own DNS resolution first, since intermittent failure very often turns out to be DNS rather than packet loss (`/etc/resolv.conf`, `ndots`, and CoreDNS or the embedded DNS server); then MTU mismatch, which is the classic overlay-network cause of _partial_ loss where small packets succeed and large ones vanish; then `conntrack` table exhaustion on the host; then NAT and iptables rules on the bridge; then whether an egress firewall or NetworkPolicy is dropping selectively. Say you would test from inside with `ping`, `curl -v`, and `ping -M do -s <size>` to prove or disprove MTU. Naming MTU and `conntrack` is what marks this as an answer from experience.
- Docker-level logs should cover three layers rather than one command. Container output: `docker logs <id>`, with `--since`, `--tail`, and `-f`, which reads what the logging driver captured from stdout and stderr. The daemon itself: `journalctl -u docker` on a `systemd` host. And the design point — the default `json-file` driver writes to local disk and will fill it without `max-size` and `max-file` limits, which is why production uses a driver or agent that ships logs off the host. In Kubernetes the equivalent is `kubectl logs`, with `--previous` for a crashed container. See [designing a logging pipeline that stays affordable at scale](../monitoring-and-logging/how-do-you-design-a-logging-pipeline-that-stays-affordable-at-scale.md).
- The database-before-frontend question has a Compose answer and a better answer, and you should give both. In Compose, `depends_on` alone only orders _starting_, not _readiness_ — so the correct form is `depends_on` with `condition: service_healthy` plus a `healthcheck` on the database. In Kubernetes there is no dependency ordering between Pods at all, so the mechanisms are an init container that blocks until the database answers, or simply an application that retries its connection with backoff. Then say the principle: ordering is a fragile guarantee, so the robust design is a frontend that tolerates the database being briefly unavailable, because it will be — during a database restart, long after startup. See [what Docker Compose is](../docker/what-is-docker-compose.md).
- For a payments organisation, volunteer the operational detail on stateful storage: `ReclaimPolicy: Retain` so a deleted PVC does not delete the data, volume snapshots before an upgrade, and access modes — `ReadWriteOnce` binding a volume to one node, which is the constraint that surprises people when a Pod cannot reschedule. See [StatefulSets](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[How do you prevent and handle secret leaks in CI/CD pipelines?]] (`#237`): [How do you prevent and handle secret leaks in CI/CD pipelines?](../cicd/how-do-you-prevent-and-handle-secret-leaks-in-ci-cd-pipelines.md)
- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
