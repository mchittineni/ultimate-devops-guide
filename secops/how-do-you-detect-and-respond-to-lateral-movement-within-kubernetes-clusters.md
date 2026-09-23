---
title: "How Do You Detect and Respond to Lateral Movement Within Kubernetes Clusters?"
id: 716
category: "SecOps and Threat Detection"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - secops
  - kubernetes-security
  - network-policies
quiz:
  stem: "What is the default Kubernetes networking behavior regarding inter-pod communication if no NetworkPolicy resources are configured in a cluster?"
  options:
    - "Pods can only communicate with other pods running on the same physical worker node."
    - "All pods can communicate freely with any other pod across all namespaces without restriction."
    - "Inter-pod communication is blocked until an ingress controller establishes a proxy route."
    - "Only pods belonging to the 'kube-system' namespace can initiate outbound TCP connections."
  answer: 2
  explanation: "By default, Kubernetes uses an open flat network model where any pod can communicate with any other pod in any namespace unless restricted by NetworkPolicy or service mesh authorization policies."
---

# How Do You Detect and Respond to Lateral Movement Within Kubernetes Clusters?

**Short answer:** Detecting lateral movement in Kubernetes involves monitoring east-west network traffic, container process trees, and Kubernetes API audit logs. Response relies on automated network policies, Pod and ServiceAccount isolation, mutual TLS enforcement, and ephemeral pod termination.

## Detail

### Lateral Movement Vectors in Kubernetes

Once an adversary achieves initial execution inside a compromised pod, their primary objective is lateral movement: discovering and exploiting other services, pivoting to the Kubernetes API, or extracting credentials to reach cloud infrastructure.

Common attack paths include:

1. **Cluster DNS Enumeration**: Probing CoreDNS to discover internal service names and endpoints across namespaces.
2. **Kubernetes API Exploitation**: Using the mounted ServiceAccount token (`/var/run/secrets/kubernetes.io/serviceaccount/token`) to query secrets, list pods, or launch privileged workloads. Modern clusters mount short-lived, audience-bound projected tokens rather than the old non-expiring Secret-based tokens, but a stolen token is still usable from anywhere that can reach the API server until it expires or its Pod is deleted - and many API servers extend these tokens' validity well beyond the nominal hour for compatibility, so deleting the Pod (which invalidates its bound token) is part of containment.
3. **Unauthenticated Microservice Traffic**: Calling internal HTTP/gRPC services that lack authentication or transport encryption.
4. **Node and Kubelet Pivots**: Escaping the container, or reaching the kubelet API (`10250`) with weak authentication or the legacy read-only port (`10255`, disabled by default on current managed clusters but still found on older self-managed ones).
5. **Cloud Credential Pivots**: Calling the instance metadata service from a Pod to steal the node's IAM role - blocked by IMDSv2 with a hop limit of 1 and by giving Pods their own identity (EKS Pod Identity/IRSA, GKE Workload Identity, AKS Workload Identity).

### Detection Strategies

- **Kubernetes Audit Logs**: Alerting on unusual RBAC queries from workload service accounts (e.g., a payment pod executing `kubectl get secrets` or listing cluster roles).
- **Runtime Threat Detection with eBPF**: Tools like Falco, Tetragon, or Sysdig detect unexpected network connections initiated by container processes (e.g., a Python microservice running `nmap` or `arp-scan`).
- **Flow Log Inspection**: Using Calico, Cilium, or cloud VPC flow logs to identify abnormal east-west traffic between pods that do not usually communicate.

```text
[Attacker in Pod A]
        │
        ├─ 1. Query CoreDNS (*.svc.cluster.local) ──► Alert: DNS Reconnaissance
        ├─ 2. Connect to Pod B on port 5432       ──► Block: Calico NetworkPolicy
        └─ 3. Query Kube-API with ServiceAccount   ──► Alert: Audit Log RBAC Deny
```

### Incident Response and Containment Playbook

1. **Apply Quarantine Network Policy**: Immediately label the compromised pod (`quarantine=true`) and apply a restrictive `NetworkPolicy` dropping all ingress and egress traffic except forensic analysis taps.
2. **Revoke and Invalidate ServiceAccount**: Delete or bind the compromised ServiceAccount to a dummy role with zero permissions.
3. **Rotate Secrets**: Invalidate any secrets or database credentials exposed to the compromised pod's namespace.
4. **Capture Forensic State**: Preserve evidence before deleting the Pod - filesystem diff and logs, a container checkpoint via the kubelet checkpoint API where enabled, or a node snapshot - and cordon the node so the scheduler does not place new work next to a possibly compromised host.

### Real-World Production Scenario

A public-facing frontend pod is exploited via an arbitrary file read vulnerability. The attacker runs a shell script to scan internal RFC 1918 subnets. Falco detects the `nmap` binary execution in the container, Cilium reports an alert for unapproved egress connections across namespaces, and an automated SecOps webhook immediately attaches a quarantine network policy to cut off the pod's traffic.

## Example

```yaml
# Quarantine policy: selects any Pod labelled quarantine=true and allows nothing in or out
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: quarantine
  namespace: payments
spec:
  podSelector:
    matchLabels:
      quarantine: "true"
  policyTypes: [Ingress, Egress]
```

```bash
# Contain without destroying evidence
kubectl -n payments label pod frontend-7d9f quarantine=true --overwrite
kubectl -n payments patch pod frontend-7d9f --type=json \
  -p='[{"op":"remove","path":"/metadata/labels/app"}]'    # drop it from the Service's endpoints
kubectl cordon "$(kubectl -n payments get pod frontend-7d9f -o jsonpath='{.spec.nodeName}')"

# What could the stolen ServiceAccount do, and what did it do?
kubectl auth can-i --list --as=system:serviceaccount:payments:frontend
# then query API audit logs for that user.username across the incident window
```

## Interview tips

- Name the three telemetry sources and what each sees: API audit logs (identity and RBAC abuse), runtime sensors such as Falco or Tetragon (process and syscall behaviour), and network flow data from Cilium Hubble, Calico, or VPC flow logs (east-west connections).
- Contain before you delete: isolate with a quarantine NetworkPolicy, remove the Pod from Service endpoints by changing its labels (the ReplicaSet will start a clean replacement), cordon the node, and capture evidence. Deleting first destroys what you need for scoping. Because NetworkPolicies are additive, the quarantine policy only isolates the Pod if no other policy still selects it and allows traffic - which is another reason to strip its labels, or to use a CNI-level deny policy (Calico, Cilium) that overrides allows.
- Scope through identity: every credential the Pod could reach - its ServiceAccount token, mounted Secrets, and any cloud role - is presumed compromised and must be rotated.
- Prevention is what makes detection tractable: default-deny NetworkPolicies, `automountServiceAccountToken: false`, least-privilege RBAC with no `get secrets` for workloads, Pod Security Admission `restricted`, and IMDSv2 with a hop limit of 1.
- Trade-off to acknowledge: runtime sensors and flow logs add overhead and cost, and rules need tuning per workload - start with high-signal detections (shell in container, API calls from workload identities that never make them, connections to the metadata IP).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
- [[How do you take a monthly release process to daily deployments?]] (`#285`): [How do you take a monthly release process to daily deployments?](../core-devops-concepts/how-do-you-take-a-monthly-release-process-to-daily-deployments.md)
- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to SecOps and Threat Detection](./README.md) · [All topics](../README.md)
