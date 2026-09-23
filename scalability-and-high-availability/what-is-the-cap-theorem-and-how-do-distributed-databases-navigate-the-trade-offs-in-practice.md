---
title: "What is the CAP Theorem and how do distributed databases navigate the trade-offs in practice?"
id: 589
category: "Scalability and High Availability"
difficulty: "Intermediate"
tags:
  - devops
  - scalability-and-high-availability
  - interview-questions
  - cap-theorem
  - distributed-systems
  - databases
  - consistency
quiz:
  stem: "Why do distributed database engineers state that the CAP theorem is effectively a choice between CP and AP rather than CA?"
  options:
    - "Cloud providers charge extra fees for CA databases"
    - "Physical network partitions (cables severed, routers hung) are inevitable in distributed systems, making Partition Tolerance mandatory"
    - "CA databases can only run on single-core processors"
    - "CAP theorem was superseded by the ACID model in 2020"
  answer: 2
  explanation: "In real-world networks, partitions cannot be prevented. When a partition occurs, a distributed system must choose between returning an error (Consistency) or serving potentially stale data (Availability)."
---

# What is the CAP Theorem and how do distributed databases navigate the trade-offs in practice?

**Short answer:** The CAP theorem states that a distributed data store can guarantee at most two of Consistency, Availability, and Partition Tolerance simultaneously; since network partitions (P) are unavoidable in distributed hardware, systems must choose between Consistency (CP) or Availability (AP) during network partitions.

## Detail

The terms are narrower than their everyday meaning, and precision here is what interviewers test:

- **Consistency** means _linearizability_: every read sees the most recent completed write, as if there were one copy of the data. It is not the "C" in ACID.
- **Availability** means every request to a non-failing node gets a non-error response - not "99.99% uptime".
- **Partition tolerance** means the system keeps operating when messages between nodes are lost or delayed.

### The real choice: CP vs AP

Because links fail, switches drop packets, and GC pauses look like partitions, **partition tolerance is not optional** for anything spread across machines. The real trade-off is what happens _during_ a partition:

- **CP (consistency + partition tolerance)**: the minority side refuses writes (and linearizable reads) because it cannot reach a quorum, returning errors or timing out. This prevents split-brain. Examples: etcd and ZooKeeper (Raft/Zab quorums), Spanner, CockroachDB.
- **AP (availability + partition tolerance)**: every reachable node keeps accepting reads and writes, and replicas are reconciled after the partition heals using last-write-wins, vector clocks, or CRDTs. Examples: Cassandra and DynamoDB in their default eventually consistent modes, CouchDB, Riak.

**In practice it is a dial, not a label.** Cassandra is tunable per query: with replication factor 3, `QUORUM` writes plus `QUORUM` reads ($W + R > N$) behave consistently but lose availability if two replicas are unreachable, while `ONE` stays available and may return stale data. DynamoDB offers strongly consistent reads within a region, and global tables can run in eventual or strong multi-Region consistency modes. Spanner is technically CP but engineers the network so partitions are rare enough that it is "effectively CA" for most users.

### PACELC

CAP only describes behaviour during a partition, which is rare. **PACELC** adds the everyday case: if **P**artitioned, choose **A** or **C**; **E**lse, choose **L**atency or **C**onsistency. Most of the time the real cost of consistency is latency - waiting for a quorum or a cross-region round trip - not unavailability. Cassandra and default DynamoDB are PA/EL; Spanner and CockroachDB are PC/EC.

**Limitation of the framing.** CAP is a proof about one extreme definition of consistency; real systems offer a spectrum (read-your-writes, monotonic reads, causal, bounded staleness), and many application bugs come from those weaker guarantees rather than from partitions.

## Example

```sql
-- Cassandra (cqlsh): the same table, tuned toward CP or AP per request.
CREATE KEYSPACE shop WITH replication = {'class': 'NetworkTopologyStrategy', 'dc1': 3};

CONSISTENCY QUORUM;   -- 2 of 3 replicas must answer: consistent, fails if 2 are down
SELECT balance FROM shop.accounts WHERE id = 42;

CONSISTENCY ONE;      -- any single replica: stays available, may read stale data
SELECT balance FROM shop.accounts WHERE id = 42;
```

```bash
# etcd (CP): a member cut off from the quorum refuses linearizable requests.
# 10.0.0.3 is the isolated member
etcdctl --endpoints=https://10.0.0.3:2379 get /config/flag
# Error: context deadline exceeded   <- no quorum, so no answer rather than a stale one
etcdctl --endpoints=https://10.0.0.3:2379 get /config/flag --consistency=s
# serializable read: served locally, possibly stale - the AP escape hatch
```

## Interview tips

- Define C as linearizability and A as "every non-failing node responds" - loose definitions are the most common mistake.
- Say P is not optional, so the choice is CP or AP _during a partition_.
- Show it is tunable in real systems: Cassandra consistency levels, $W + R > N$, DynamoDB read modes.
- Bring in PACELC: outside partitions, the everyday trade-off is latency versus consistency.
- Give concrete examples - etcd/ZooKeeper for CP, Cassandra for AP - and why Kubernetes relies on a CP store.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Scalability and High Availability](./README.md) · [All topics](../README.md)
