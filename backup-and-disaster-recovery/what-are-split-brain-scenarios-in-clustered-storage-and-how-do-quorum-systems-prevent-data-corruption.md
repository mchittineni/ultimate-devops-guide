---
title: "What are Split-Brain scenarios in clustered storage and how do Quorum systems prevent data corruption?"
id: 601
category: "Backup and Disaster Recovery"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - backup-and-disaster-recovery
  - ha
  - quorum
  - split-brain
  - raft
  - etcd
quiz:
  stem: "Why does a 2-node database cluster have worse fault tolerance than a 3-node cluster when enforcing quorum to prevent split-brain?"
  options:
    - "2-node clusters use double the memory of 3-node clusters"
    - "In a 2-node cluster, quorum requires both nodes (2 of 2); if a single node fails, the cluster loses quorum and cannot accept writes"
    - "2-node clusters cannot run on Linux servers"
    - "Raft algorithms require an even number of nodes to operate"
  answer: 2
  explanation: "Quorum is $N/2 + 1$. For $N=2$, quorum is 2. The loss of either node drops active members below quorum, preventing any writes. For $N=3$, quorum is 2, allowing 1 node to die safely."
---

# What are Split-Brain scenarios in clustered storage and how do Quorum systems prevent data corruption?

**Short answer:** Split-brain occurs when a network partition divides a cluster into disconnected sub-groups that both believe they are the leader and accept conflicting writes; Quorum systems require a strict majority vote (`floor(N/2) + 1`) to elect leaders and commit data, ensuring only one partition can operate.

## Detail

If a 2-node cluster splits:

- Node A cannot communicate with Node B.
- Node A assumes Node B is dead and promotes itself to Master.
- Node B assumes Node A is dead and promotes itself to Master.
- Clients write different data to both nodes. When the network heals, the databases have hopelessly diverged and data is corrupted.

### The Quorum Rule

```text
quorum = floor(N / 2) + 1
```

Two disjoint partitions cannot both hold a strict majority, so at most one side can elect a leader or commit writes; the minority side stops accepting writes. Consensus algorithms (Raft, Paxos, Zab) work with any cluster size, but **odd sizes are recommended** because adding a node to make the count even raises the quorum without adding any fault tolerance:

| Cluster Size (N) | Quorum Needed | Tolerable Node Failures                         |
| ---------------- | ------------- | ----------------------------------------------- |
| 1                | 1             | 0                                               |
| 2                | 2             | 0 (If 1 node fails, quorum of 2 is impossible!) |
| 3                | 2             | 1 node                                          |
| 5                | 3             | 2 nodes                                         |
| 7                | 4             | 3 nodes                                         |

Notice that a 2-node cluster provides **zero fault tolerance**, and a 4-node cluster tolerates no more failures than a 3-node one. A 3-node cluster can tolerate 1 failure, while a 5-node cluster tolerates 2 failures.

### Quorum is not the whole answer

- **Fencing.** A deposed leader may not yet know it has lost quorum (a long GC pause, a stalled VM). Fencing - STONITH in Pacemaker, fencing tokens or epoch numbers on the storage side, leases that expire - stops the old leader's in-flight writes from landing.
- **Witnesses.** Two-site designs add a lightweight tie-breaker in a third location (a quorum device, a cloud witness, an arbiter) so that a site partition leaves one side with a majority.
- **Cost.** The minority side is deliberately unavailable during a partition: quorum trades availability for consistency (the CP side of CAP).

## Example

Check which etcd member is leader and whether a partition has left a member without quorum:

```bash
etcdctl --endpoints=https://10.0.1.10:2379,https://10.0.1.11:2379,https://10.0.1.12:2379 \
  --cacert=ca.crt --cert=client.crt --key=client.key \
  endpoint status --write-out=table
# IS LEADER is true on exactly one member; RAFT TERM increments on every election.
# A member cut off from the other two returns "context deadline exceeded" for
# writes and linearizable reads, rather than serving stale or divergent data.
```

## Interview tips

- Split-brain causing conflicting dual-master writes.
- Quorum formula: strictly greater than 50% majority (`floor(N/2) + 1`).
- Why clusters use odd numbers of nodes (3, 5, 7).
- A 2-node cluster has worse fault tolerance than a 3-node cluster.
- Mention fencing: quorum decides who _should_ lead, fencing stops the old leader from writing anyway.
- For two data centres, the answer is a third-site witness, not a bigger cluster in one of the two sites.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Backup and Disaster Recovery](./README.md) · [All topics](../README.md)
