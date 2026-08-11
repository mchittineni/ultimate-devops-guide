---
title: "How does RBAC work in Kubernetes?"
id: 257
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - kubernetes
  - interview-questions
---

# How does RBAC work in Kubernetes?

**Short answer:** RBAC grants permissions through four objects: a `Role` (namespaced) or `ClusterRole` (cluster-wide) lists allowed verbs on resources, and a `RoleBinding` or `ClusterRoleBinding` attaches that list to a subject - a user, group, or ServiceAccount. Permissions are purely additive; there are no deny rules, and anything not explicitly granted is refused.

## Detail

**Authentication is not authorisation.** The API server first establishes _who_ you are (client certificate, OIDC token, or a ServiceAccount token), then RBAC decides _what_ you may do. Kubernetes has no user objects - human identity comes from your certificate's CN/O fields or your identity provider's claims. ServiceAccounts are the only identity Kubernetes itself creates.

**The four objects and the one combination that surprises people:**

| Object               | Scope                                                    |
| -------------------- | -------------------------------------------------------- |
| `Role`               | Permissions within one namespace                         |
| `ClusterRole`        | Permissions cluster-wide, or on cluster-scoped resources |
| `RoleBinding`        | Grants a Role **or a ClusterRole** within one namespace  |
| `ClusterRoleBinding` | Grants a ClusterRole across every namespace              |

The useful trick is the third row: define a `ClusterRole` once, then bind it with a `RoleBinding` in each namespace. The permissions apply only in that namespace. This is how you give a team admin rights over their own namespace without writing the same Role forty times.

**Rules are verbs on resources.** Verbs are `get`, `list`, `watch`, `create`, `update`, `patch`, `delete`, `deletecollection`; resources are named by their API plural (`pods`, `deployments`), with `apiGroups: [""]` meaning the core group. Subresources are separate grants - `pods/log` and `pods/exec` are not covered by `pods`.

**Deny is impossible, and that shapes design.** Because rules only add, the model is least-privilege-by-default: start with nothing, grant narrowly. There is no way to grant `*` and then carve out an exception.

**Escalation paths are the security-interview follow-up.** These grants are effectively cluster-admin even though they do not look like it:

- `create pods` in a namespace whose ServiceAccounts are privileged - you can mount any of their tokens.
- `pods/exec` - shell into any running container.
- `secrets: get/list` - read every credential in scope.
- `escalate` / `bind` on RBAC objects - grant yourself more than you have.
- `create` on `clusterrolebindings`.

**Built-in ClusterRoles** ship with every cluster: `cluster-admin` (everything), `admin` (namespace admin via RoleBinding), `edit` (mutate workloads but not RBAC), and `view` (read-only, excludes Secrets). Bind these before writing your own - `edit` and `view` cover most human access.

**ServiceAccounts are for workloads.** Modern tokens are short-lived and projected into the Pod, not long-lived Secrets. Every Pod gets `default` if you do not specify one - and `default` should have no permissions. Set `automountServiceAccountToken: false` on Pods that never call the API. In the cloud, bind the ServiceAccount to a cloud identity (EKS Pod Identity/IRSA, GKE Workload Identity, Entra Workload ID) instead of shipping static keys.

## Example

```yaml
# Namespaced read-only access for an on-call engineer, including logs.
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: payments
  name: oncall-reader
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log", "events", "services", "configmaps"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments", "replicasets", "statefulsets"]
    verbs: ["get", "list", "watch"]
  # Note: "secrets" is deliberately absent, and pods/exec is not granted.
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  namespace: payments
  name: oncall-reader
subjects:
  - kind: Group
    name: payments-oncall # comes from the OIDC provider
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: oncall-reader
  apiGroup: rbac.authorization.k8s.io
```

```bash
# Test permissions instead of guessing - the single most useful RBAC command
kubectl auth can-i delete pods --namespace payments
kubectl auth can-i list secrets --as system:serviceaccount:payments:api -n payments

# Everything a subject can do (kubectl 1.32+)
kubectl auth whoami
```

## Interview tips

- Name all four objects and immediately explain the ClusterRole-plus-RoleBinding combination - it is the detail that separates people who have written RBAC from people who have read about it.
- "Can you write a deny rule?" - no. Permissions are additive only.
- `kubectl auth can-i` is the answer to "how do you verify a policy?"
- If the interview leans security, volunteer the escalation paths: `pods/exec`, `secrets: list`, and `create pods` with a privileged ServiceAccount are cluster-admin in disguise.
- Tie ServiceAccounts to cloud workload identity rather than static keys - that connects RBAC to the secrets-management answer they will ask next.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)
- [[How do you troubleshoot a failed Helm release?]] (`#412`): [How do you troubleshoot a failed Helm release?](../container-orchestration-advanced/how-do-you-troubleshoot-a-failed-helm-release.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
