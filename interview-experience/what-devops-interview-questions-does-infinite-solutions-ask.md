---
title: "What DevOps interview questions does Infinite Solutions ask?"
id: 340
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - infinite-solutions
  - kubernetes
  - backup-and-disaster-recovery
  - container-orchestration-advanced
  - scalability-and-high-availability
---

# What DevOps interview questions does Infinite Solutions ask?

## Questions

**Kubernetes resilience**

- **How are you managing disaster recovery for Kubernetes?**
- **How do you take a backup of Kubernetes?**

**Kubernetes networking**

- **How do you set up an ingress controller?**

## Example

```text
Infinite Solutions — DevOps Engineer (5 YOE), reported round
3 questions

  Kubernetes resilience       2   DR strategy, cluster backup
  Kubernetes networking       1   ingress controller setup

THE SHORTEST ROUND IN THIS COLLECTION
  Three questions means this was almost certainly a screening call, or the
  candidate recorded only the questions that mattered. Either way, all three
  are open-ended "how do YOU do it" questions — the interviewer is checking
  whether you have operated a cluster, not whether you know definitions.
  Each answer should run two to three minutes with named tools and a
  real decision you made.
```

## Interview tips

- Kubernetes disaster recovery and Kubernetes backup are asked as separate questions, so do not give the same answer twice. Backup is the mechanism — what you capture and where it goes. DR is the strategy — what you would actually do to serve traffic again, with an RTO and RPO attached. Lead the DR answer with those two numbers and the recovery pattern you chose.
- For backup, distinguish the three things that need protecting, because most candidates name only one. First, cluster state: an etcd snapshot on a self-managed control plane, and nothing you can do on a managed one because the provider owns etcd. Second, workload definitions: your manifests, Helm values, and Terraform in Git, which is the real backup for anything declarative. Third, application data: persistent volumes, backed up via Velero with a volume snapshotter or CSI snapshots, or by the database's own backup tooling. Say that Velero covers namespaced resources plus PV data and is the standard answer on managed clusters. See [disaster recovery](../scalability-and-high-availability/what-is-disaster-recovery.md).
- The sharpest thing you can say on DR is that a cluster is disposable and the data is not. If every manifest is in Git and reconciled by a GitOps controller, rebuilding a cluster is a Terraform apply plus a sync, so your DR plan should focus on the data tier and on DNS — how traffic reaches the new cluster. That reframing is what distinguishes an operator from someone reciting Velero commands. See [GitOps](../devops-tools-and-automation/what-is-gitops.md) and [designing for multi-region resilience](../cloud-engineering/how-do-you-design-for-multi-region-resilience.md).
- Name a DR tier explicitly rather than being vague: backup and restore is cheapest with an RTO in hours; a pilot light keeps the data replicated and the control plane minimal; warm standby runs a scaled-down cluster ready to take traffic; active-active runs both and is the only one with a near-zero RTO. Then say which you have actually run, and add that an untested DR plan does not count — a restore rehearsal is what makes it real.
- For the ingress controller, describe an actual installation and the decisions in it, not just "install nginx-ingress with Helm". Cover: which controller and why (ingress-nginx for portability, or the AWS Load Balancer Controller so the cloud provisions an ALB, or a Gateway API implementation for newer clusters); installing it via Helm with a pinned chart version; whether it runs as a Deployment behind a `LoadBalancer` Service or as a DaemonSet with host ports; setting `ingressClassName` so multiple controllers can coexist; TLS through cert-manager with automatic certificate issuance and renewal; and replica count plus a PodDisruptionBudget so an upgrade cannot drain it to zero. See [exposing an application in Kubernetes](../kubernetes/how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md).
- Anticipate the follow-up that always comes after ingress setup: what to check when an Ingress exists but nobody can reach the application. Have the ordered list ready — DNS resolves to the load balancer, controller Pods running, the Ingress object has an address, `ingressClassName` matches, the backend Service has non-empty Endpoints, ports line up, and the TLS secret exists in the right namespace. Empty Endpoints is the most common cause. See [what a Service is in Kubernetes](../kubernetes/what-is-a-service-in-kubernetes.md).
- In a three-question round, silence is your enemy. Volunteer the adjacent detail — mention Velero's schedule and retention when asked about backup, mention cert-manager when asked about ingress — because the interviewer has little else to grade you on.

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
