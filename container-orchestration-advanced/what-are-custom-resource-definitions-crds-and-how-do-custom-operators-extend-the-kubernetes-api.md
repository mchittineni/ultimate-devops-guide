---
title: "What are Custom Resource Definitions (CRDs) and how do Custom Operators extend the Kubernetes API?"
id: 623
category: "Container Orchestration Advanced"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - kubernetes
  - crd
  - operators
  - controller-runtime
quiz:
  stem: "What is the primary role of a Custom Operator in a Kubernetes cluster?"
  options:
    - "To replace the Linux kernel on worker nodes"
    - "To encode human operational expertise into automated software that manages complex, stateful applications (like databases and message queues)"
    - "To provide an alternative to Docker desktop"
    - "To automatically generate HTML user interfaces"
  answer: 2
  explanation: "The Operator pattern pairs a custom resource with automated controller logic to manage stateful application lifecycles (automated backups, failover, scaling) without human operator toil."
---

# What are Custom Resource Definitions (CRDs) and how do Custom Operators extend the Kubernetes API?

**Short answer:** A **CustomResourceDefinition** registers a new resource type with the API server - its group, versions, schema, and scope - so objects of that kind can be created, validated, stored in etcd, watched, and secured with RBAC exactly like built-in ones. A CRD on its own is only data. An **operator** pairs one or more CRDs with a controller that reconciles them, encoding the operational knowledge a human would otherwise apply - provisioning, failover, backups, upgrades - for software like PostgreSQL, Kafka, or cert-manager's certificates. The trade-off is that every operator becomes part of your platform: it must be upgraded, monitored, and kept compatible with the cluster, and a broken one leaves its resources unmanaged.

## Detail

**What the API server does with a CRD.** Once the `CustomResourceDefinition` is created, the API server serves a new REST endpoint (`/apis/<group>/<version>/namespaces/<ns>/<plural>`), validates writes against the OpenAPI v3 schema, prunes unknown fields, and stores objects in etcd. `kubectl get`, watches, RBAC, admission, and GitOps tools all work with no extra code.

**Features worth knowing.**

- **Structural schema and validation**: types, required fields, enums, and defaults, plus **CEL validation rules** (`x-kubernetes-validations`, GA since 1.29) for cross-field rules such as "`minReplicas` ≤ `maxReplicas`" - no webhook needed.
- **Subresources**: `status` (so users write `spec` and the controller writes `status` under separate RBAC) and `scale` (so `kubectl scale` and the HPA work on the custom kind).
- **Versions**: several versions can be served, one is the storage version; a conversion webhook translates between schemas. This is how an API evolves from `v1alpha1` to `v1` without breaking users.
- **Printer columns** and short names for a usable `kubectl get`.

**The operator pattern.** The controller watches the custom resources (and the objects it creates), and on each reconcile compares the declared spec with reality: create the StatefulSet, Services, and Secrets; check replication health; promote a replica if the primary is gone; schedule backups; roll an upgrade one member at a time. Status and conditions report progress back on the custom resource. Operators are usually built with **Kubebuilder** or the **Operator SDK** (both on controller-runtime), or with frameworks in other languages such as Kopf (Python) and Java Operator SDK.

**Trade-offs and limitations.**

- **Operational cost.** An operator is privileged software in your cluster. Its quality matters more than its feature list: look at maintenance activity, upgrade paths, and how it behaves when it crashes.
- **CRD lifecycle.** CRDs are cluster-scoped and shared by every tenant, so two teams cannot run incompatible versions of the same operator in one cluster. Deleting a CRD deletes every object of that kind.
- **Uninstall ordering.** Remove the operator before its custom resources and their finalizers can never be cleared - the classic stuck-namespace cause.
- **API server load.** Large numbers of big custom objects, or chatty controllers, consume etcd space and API capacity like any other resource.
- **Not everything needs one.** If a Helm chart and a Deployment do the job, an operator adds a controller to run for no benefit; operators earn their keep on stateful, day-2-heavy software.

## Example

```yaml
# 1. The CRD: registers the PostgresCluster kind with schema and CEL validation
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: postgresclusters.database.example.com
spec:
  group: database.example.com
  scope: Namespaced
  names: { plural: postgresclusters, singular: postgrescluster, kind: PostgresCluster, shortNames: [pgc] }
  versions:
    - name: v1
      served: true
      storage: true
      subresources: { status: {} }
      additionalPrinterColumns:
        - { name: Replicas, type: integer, jsonPath: .spec.replicas }
        - { name: Ready, type: string, jsonPath: ".status.conditions[?(@.type=='Ready')].status" }
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              required: [replicas, version]
              x-kubernetes-validations:
                - rule: "self.replicas % 2 == 1"
                  message: "replicas must be odd to keep quorum"
              properties:
                replicas: { type: integer, minimum: 1, maximum: 7 }
                version: { type: string, enum: ["16", "17"] }
                backupSchedule: { type: string }
            status:
              type: object
              x-kubernetes-preserve-unknown-fields: true
---
# 2. A custom resource the operator reconciles
apiVersion: database.example.com/v1
kind: PostgresCluster
metadata: { name: production-db, namespace: data }
spec:
  replicas: 3
  version: "17"
  backupSchedule: "0 2 * * *"
```

```bash
kubectl apply -f postgrescluster-crd.yaml
kubectl api-resources --api-group=database.example.com   # the new kind is served
kubectl get pgc -n data                                   # printer columns from the CRD
kubectl explain postgrescluster.spec                      # schema-driven docs
```

## Interview tips

- Separate the two halves: a CRD extends the API with a schema; an operator is the controller that gives it behaviour.
- Mention what you get for free - validation, RBAC, watches, `kubectl`, GitOps - once a kind is registered.
- Show current knowledge: structural schemas, CEL `x-kubernetes-validations`, `status` and `scale` subresources, and versioning with conversion webhooks.
- Name real operators (CloudNativePG, Strimzi, cert-manager, Prometheus Operator) and the frameworks (Kubebuilder, Operator SDK).
- Volunteer the costs: operators are privileged, CRDs are cluster-wide and shared, and uninstall ordering can strand finalizers.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is GitOps and how does it fundamentally change release management?]] (`#508`): [What is GitOps and how does it fundamentally change release management?](../core-devops-concepts/what-is-gitops-and-how-does-it-fundamentally-change-release-management.md)
- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[What are ephemeral preview environments and how do you manage their lifecycle and cleanup?]] (`#535`): [What are ephemeral preview environments and how do you manage their lifecycle and cleanup?](../cicd/what-are-ephemeral-preview-environments-and-how-do-you-manage-their-lifecycle-and-cleanup.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
