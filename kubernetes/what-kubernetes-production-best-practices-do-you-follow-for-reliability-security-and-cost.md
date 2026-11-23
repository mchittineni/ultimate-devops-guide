---
title: "What Kubernetes production best practices do you follow for reliability, security, and cost?"
id: 790
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - kubernetes
  - best-practices
  - security
  - finops
quiz:
  stem: "A team alerts when any node passes 80% CPU. Which change best aligns alerting with production best practice?"
  options:
    - "Lower the threshold to 60% so alerts fire earlier"
    - "Alert on user-facing symptoms such as error rate and latency against an SLO, plus Pods stuck Pending, and treat node utilisation as a dashboard signal"
    - "Remove all alerts and rely on the cluster autoscaler"
    - "Alert on every container restart in every namespace"
  answer: 2
  explanation: "High node utilisation is often healthy and is what bin-packing aims for. Pages should fire on symptoms users feel and on capacity failures such as unschedulable Pods, not on resource percentages alone."
---

# What Kubernetes production best practices do you follow for reliability, security, and cost?

**Short answer:** Group the answer into three areas and give one concrete control for each item. **Reliability:** accurate requests, at least two replicas spread across zones, readiness and liveness probes, PodDisruptionBudgets, and autoscaling for both Pods and nodes. **Security:** least-privilege RBAC, per-workload cloud identity (EKS Pod Identity or IRSA, Azure or GKE Workload Identity), Pod Security Admission at `restricted`, default-deny NetworkPolicies, and secrets from an external manager. **Cost:** right-size requests from real usage, let the node autoscaler consolidate, use Spot for stateless work, and allocate spend by team label. All of it is delivered through Git and enforced with admission policy, so it is not left to memory.

## Detail

**Reliability**

- **Requests and limits.** Requests drive scheduling and bin-packing, so set them from observed usage. Set a memory limit (memory cannot be throttled, so an unbounded leak takes the node down). CPU limits are debated: they cause throttling even when the node is idle, so many teams set CPU requests only for latency-sensitive services.
- **Replicas and spread.** Two or more replicas with `topologySpreadConstraints` across zones, so one zone or node failure does not take the service down.
- **Probes.** A readiness probe that checks the app can serve, a liveness probe that only detects a hung process (never a dependency check, or one database blip restarts everything), and a startup probe for slow boots.
- **Disruption budgets and graceful shutdown.** A PDB per service so node drains and upgrades are paced, plus a `preStop` delay and a `terminationGracePeriodSeconds` the app actually honours.
- **Autoscaling.** HPA on CPU or a business metric, and a node autoscaler (Karpenter or Cluster Autoscaler) so Pods never wait long in `Pending`.
- **Upgrades.** Stay within the supported version window, test upgrades in a lower environment, and check for removed APIs before each one.

**Security**

- **RBAC.** Namespace-scoped Roles for teams, no wildcard verbs, and `get secrets` granted rarely. Turn off `automountServiceAccountToken` for workloads that never call the API.
- **Workload identity.** Pods get cloud permissions through their ServiceAccount (EKS Pod Identity or IRSA on AWS), never through the node's role or static access keys.
- **Pod hardening.** Pod Security Admission `restricted` on application namespaces: non-root, no privilege escalation, dropped capabilities, and a `RuntimeDefault` seccomp profile.
- **Network.** Default-deny NetworkPolicies per namespace, then explicit allows.
- **Supply chain.** Images built in CI, scanned, signed, and deployed by digest; an admission policy (Kyverno or Gatekeeper) rejects anything unsigned or from an untrusted registry.
- **Secrets.** Source of truth in Vault or a cloud secret manager, synced with the External Secrets Operator or mounted with the Secrets Store CSI driver, and etcd encryption at rest enabled.

**Cost**

- **Right-sizing.** Compare requests with actual usage (VPA in recommendation mode, or Prometheus queries) and shrink inflated requests, which are the largest source of waste.
- **Node efficiency.** Karpenter consolidation or Cluster Autoscaler scale-down, a mix of instance types, and Spot capacity for stateless, interruption-tolerant workloads.
- **Guardrails and visibility.** ResourceQuota and LimitRange per namespace, consistent `team` and `env` labels, and OpenCost or Kubecost to show spend per team.

**Observability ties it together.** Prometheus and Grafana (or a managed equivalent) for metrics, centralised logs, and alerts on symptoms: SLO burn rate, error rate, latency, Pods stuck `Pending`, and the autoscaler hitting its node limit. Node CPU at 80% belongs on a dashboard, not on a pager.

**Delivery.** Everything above lives in Git and reaches clusters through GitOps (Argo CD or Flux), so a missing PDB or probe is visible in review. For ingress, plan around the Gateway API; the community ingress-nginx controller has been retired.

## Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: checkout
  labels: { app.kubernetes.io/name: checkout, team: payments }
spec:
  replicas: 3
  selector: { matchLabels: { app.kubernetes.io/name: checkout } }
  template:
    metadata:
      labels: { app.kubernetes.io/name: checkout, team: payments }
    spec:
      serviceAccountName: checkout # bound to a cloud role via Pod Identity or IRSA
      automountServiceAccountToken: false
      securityContext:
        runAsNonRoot: true
        seccompProfile: { type: RuntimeDefault }
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: ScheduleAnyway
          labelSelector: { matchLabels: { app.kubernetes.io/name: checkout } }
      containers:
        - name: checkout
          image: registry.example.com/checkout@sha256:4f1c0e8d2b7a9c3e5f6a1b2c3d4e5f60718293a4b5c6d7e8f9a0b1c2d3e4f5a6
          resources:
            requests: { cpu: 250m, memory: 256Mi }
            limits: { memory: 512Mi } # memory limit, no CPU limit
          readinessProbe: { httpGet: { path: /ready, port: 8080 } }
          livenessProbe: { httpGet: { path: /healthz, port: 8080 }, periodSeconds: 20 }
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities: { drop: ["ALL"] }
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: checkout }
spec:
  maxUnavailable: 1
  selector: { matchLabels: { app.kubernetes.io/name: checkout } }
```

```bash
# Where are requests far above real usage? (needs metrics-server)
kubectl top pods -A --sort-by=memory | head -20
kubectl get pods -A --field-selector=status.phase=Pending   # should normally be empty
```

## Interview tips

- Structure the answer as reliability, security, and cost, with one specific control per point. A flat list of tools sounds rehearsed.
- The common answer stops at "set requests and limits, use ConfigMaps and Secrets, monitor with Prometheus, use RBAC and IRSA." That is a good start; add PDBs, zone spread, probes, Pod Security Admission, NetworkPolicies, image signing, and right-sizing to show depth.
- Expect "do you set CPU limits?" Say what throttling does and when you would still set them, for example on noisy batch jobs or in multi-tenant namespaces.
- Expect "how do you make sure teams follow this?" The answer is admission policy plus templates (a Helm library chart or a platform golden path), not a wiki page.
- On cost, lead with request right-sizing before Spot; inflated requests waste more than instance pricing.

**Telling it as a STAR story** (an adaptable example)

- **Situation:** A shared EKS cluster had frequent outages during node upgrades and a monthly bill that kept growing, with no clear owner for either.
- **Task:** Bring the platform up to a production baseline without blocking a dozen service teams.
- **Action:** I wrote the baseline as a Helm library chart (probes, PDB, zone spread, hardened security context, `team` label) and rolled it out service by service. Kyverno first audited and then enforced required labels, non-root, and signed images. I moved AWS access from the node role to EKS Pod Identity, added default-deny NetworkPolicies per namespace, and used Prometheus data to cut requests that were several times actual usage before enabling Karpenter consolidation with Spot for stateless services.
- **Result:** The next two upgrades finished without customer impact, and node spend fell noticeably within a quarter, with cost reported per team from the labels.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does Docker multi-stage building optimize container security and image size?]] (`#513`): [How does Docker multi-stage building optimize container security and image size?](../docker/how-does-docker-multi-stage-building-optimize-container-security-and-image-size.md)
- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)
- [[How do you troubleshoot a failed Helm release?]] (`#412`): [How do you troubleshoot a failed Helm release?](../container-orchestration-advanced/how-do-you-troubleshoot-a-failed-helm-release.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
