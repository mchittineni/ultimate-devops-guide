---
title: "What DevOps interview questions does Publicis Global Delivery ask?"
id: 371
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - publicis-global-delivery
  - kubernetes
  - version-control
  - cicd
  - database-management-in-devops
  - container-orchestration-advanced
---

# What DevOps interview questions does Publicis Global Delivery ask?

## Questions

**Kubernetes**

- **What is the approach to upgrading a Kubernetes cluster from one version to another?**
- **What is a PodDisruptionBudget in Kubernetes?**
- **What are the access modes on a PersistentVolumeClaim?**
- **You have a stateful application that must be deployed on a specific node. How?**

**Git**

- **How do you extract all Git commits from the last three days?**

**CI/CD and cloud authentication**

- **How does a Jenkins pipeline authenticate to AWS as a particular identity, given you have a single login?**

**Databases**

- **You have a MongoDB dump and need to free up some space from it. How would you do that?**

## Example

```text
Publicis Global Delivery — DevOps Engineer, reported round
7 questions

  Kubernetes                  4   cluster upgrade approach, PodDisruptionBudget,
                                  PVC access modes, pin a stateful app to a node
  Git                         1   commits from the last three days
  CI/CD authentication        1   Jenkins to AWS as a specific identity
  Databases                   1   reclaim space from a MongoDB dump

A SMALL ROUND WITH ONE UNUSUAL QUESTION
  Reclaiming space from a MongoDB dump is not a standard DevOps question, and
  the phrasing is ambiguous — clarifying what "the dump" means before
  answering is the correct move, not a weakness.
```

## Interview tips

- PVC access modes have exact names and one detail that separates a real answer: `ReadWriteOnce` (RWO) mounts the volume read-write by a single _node_ — not a single Pod, which is the misconception; `ReadOnlyMany` (ROX) allows read-only mounts on many nodes; `ReadWriteMany` (RWX) allows read-write on many nodes; and `ReadWriteOncePod` (RWOP) restricts it to exactly one Pod. Say that most block storage — EBS, Azure Disk — only supports RWO, so RWX requires a network filesystem such as EFS, Azure Files, or NFS. Then add the operational consequence: RWO is why a Pod can get stuck `Pending` during a rolling update when the replacement is scheduled on a different node while the old Pod still holds the volume.
- The stateful-app-on-a-specific-node question should be answered on two axes, because "stateful" changes the answer. Placement: label the node and use `nodeSelector` or node affinity, or taint the node and add a matching toleration to reserve it. But the storage half matters more: if the volume is node-local — a `local` PersistentVolume or `hostPath` — the Pod is _already_ bound to that node by the volume's node affinity, so the scheduler has no choice. Say that pinning to one named node removes the scheduler's ability to reschedule if the node dies, so a StatefulSet with per-replica PVCs and zone-aware storage is the production pattern. See [controlling which node a Pod runs on](../kubernetes/how-do-you-control-which-node-a-pod-runs-on.md) and [StatefulSets](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md).
- "PDP" is a transcription of PodDisruptionBudget. Define it as a constraint on _voluntary_ disruptions — `minAvailable` or `maxUnavailable` limiting how many replicas a drain, node upgrade, or eviction may take down at once — with no effect at all when a node crashes unexpectedly. Then give the failure mode, which is the real content: a PDB requiring 100% availability blocks node drains indefinitely, so a cluster upgrade hangs. That connects it directly to the upgrade question they asked first.
- Because the upgrade and PDB questions sit together, answer the upgrade with PDBs in the story: check the version skew policy and scan for deprecated APIs first, upgrade the control plane one minor version at a time, then the add-ons — CNI, CSI, CoreDNS, kube-proxy — then roll the nodes by cordoning and draining while respecting PodDisruptionBudgets, surging new nodes before removing old ones. Verify afterwards that every node reports the new version, nothing is `Pending` or crash-looping, and your own smoke tests pass. Say you would rehearse it on a non-production cluster. See [main components of Kubernetes architecture](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md).
- The Git question has a direct answer worth knowing verbatim: `git log --since="3 days ago"`, with `--all` to cover every branch, `--oneline` for a compact list, `--author` to filter, and `--pretty=format:` when you need a specific shape for a report or release note. Mention `--since` accepts both relative and absolute dates, and that `git log --since --until` bounds a window — useful when assembling a changelog for a release. See [what Git is](../version-control/what-is-git.md).
- The Jenkins-to-AWS authentication question is asking how you authenticate as a _specific_ identity when the controller itself has one identity. The good answer is a hierarchy. Best: no stored credential at all — the Jenkins agent runs on EC2 or EKS with an instance profile or IRSA, and each pipeline assumes a _role_ scoped to its own environment via `sts:AssumeRole`, so identity comes from role assumption rather than from separate logins. Next best: per-folder AWS credentials in the Credentials plugin, consumed with `withCredentials` so each team's jobs can only see their own. Say the two things to avoid: one shared administrator key for every pipeline, and interpolating a secret inside a double-quoted Groovy string, which leaks it into the build log. See [how AWS IAM evaluates a request](../aws-engineering/how-does-aws-iam-evaluate-a-request.md) and [preventing and handling secret leaks in CI/CD](../cicd/how-do-you-prevent-and-handle-secret-leaks-in-ci-cd-pipelines.md).
- The MongoDB-dump question is ambiguously worded, so say so and answer both readings — that is stronger than guessing. If they mean the _dump artefact_ is too large: `mongodump --gzip` compresses it, `--collection` and `--query` let you export a subset, and `--excludeCollection` skips large ephemeral collections such as logs or sessions; then archive it to object storage with a lifecycle rule rather than keeping it on a volume. If they mean freeing space _in the database_: deleting documents does not return disk to the operating system, because WiredTiger keeps the space for reuse — you need `compact` on a collection, or a resync of a replica-set member, and the safe production pattern is a rolling initial-sync of secondaries rather than compacting the primary. Also check for oversized indexes and TTL indexes for automatic expiry. Naming that deletes-do-not-reclaim-disk behaviour is what makes this answer stand out.
- With only seven questions, each carries roughly 14% of the round, so extend every answer into its operational consequence and invite the follow-up. The PDB and upgrade questions in particular are two halves of one story — linking them explicitly shows joined-up knowledge rather than recall.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?]] (`#402`): [How do you troubleshoot a Jenkins pipeline that never starts or hangs in the queue?](../cicd/how-do-you-troubleshoot-a-jenkins-pipeline-that-never-starts-or-hangs-in-the-queue.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
