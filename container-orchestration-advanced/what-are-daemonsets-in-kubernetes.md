---
title: "What are DaemonSets in Kubernetes?"
id: 82
category: "Container Orchestration Advanced"
difficulty: "Intermediate"
tags:
  - devops
  - container-orchestration-advanced
  - interview-questions
---

# What are DaemonSets in Kubernetes?

**Short answer:** A DaemonSet ensures a copy of a pod runs on every node (or every node matching a selector), automatically adding pods to new nodes and removing them when nodes leave - the pattern for node-level agents.

## Detail

**Typical uses:** log collectors (Fluent Bit, Filebeat), metrics agents (node_exporter, Datadog agent), CNI network plugins (Calico, Cilium), storage drivers (CSI node plugins), security agents (Falco), and node-level maintenance daemons.

**Behaviour.** The DaemonSet controller - not the scheduler's usual replica logic - creates one pod per eligible node. New nodes get the pod as soon as they join; nodes removed take their pod with them. `nodeSelector`, node affinity, and tolerations control which nodes are eligible.

**Tolerations matter.** Control-plane and specialised nodes carry taints. A monitoring agent that must run everywhere needs the corresponding tolerations, otherwise you get silent blind spots on exactly the nodes you most want to watch.

**Update strategies:** `RollingUpdate` with `maxUnavailable` (and `maxSurge` in newer versions) or `OnDelete` for manual control, which is common for network plugins where a botched rollout can partition the cluster.

**Priority and resources.** Node agents should carry a high `priorityClassName` (`system-node-critical`) so they are not evicted under pressure, and conservative resource requests since they multiply by node count - on a 500-node cluster, 100 MiB per agent is 50 GiB of cluster memory.

## Example

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata: { name: fluent-bit, namespace: logging }
spec:
  selector: { matchLabels: { app: fluent-bit } }
  updateStrategy: { type: RollingUpdate, rollingUpdate: { maxUnavailable: 1 } }
  template:
    metadata: { labels: { app: fluent-bit } }
    spec:
      priorityClassName: system-node-critical
      tolerations:
        - operator: Exists # run on every node, including tainted ones
      containers:
        - name: fluent-bit
          image: fluent/fluent-bit:3.1
          resources:
            requests: { cpu: 50m, memory: 64Mi }
            limits: { memory: 128Mi }
          volumeMounts:
            - { name: varlog, mountPath: /var/log, readOnly: true }
      volumes:
        - { name: varlog, hostPath: { path: /var/log } }
```

## Interview tips

- Tolerations for tainted nodes is the operational gotcha worth raising.
- Multiply resource requests by node count when discussing cost - it shows scale awareness.
- Contrast with a Deployment: DaemonSet replica count is derived from the node count, not declared.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[What is Continuous Delivery?]] (`#4`): [What is Continuous Delivery?](../core-devops-concepts/what-is-continuous-delivery.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
