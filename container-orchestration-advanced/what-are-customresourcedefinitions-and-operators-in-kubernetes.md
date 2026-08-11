---
title: "What are CustomResourceDefinitions and operators in Kubernetes?"
id: 452
category: "Container Orchestration Advanced"
difficulty: "Advanced"
tags:
  - devops
  - container-orchestration-advanced
  - interview-questions
  - platform-engineering
  - kubernetes
---

# What are CustomResourceDefinitions and operators in Kubernetes?

**Short answer:** A **CustomResourceDefinition** extends the Kubernetes API with a new object type - after you apply it, `kind: PostgresCluster` is a first-class resource with the same RBAC, validation, `kubectl`, audit, and watch machinery as a built-in. But a CRD on its own only gives you **storage**: the API server will happily save your object and nothing will happen. An **operator** is the other half - a controller that watches those objects and runs a reconciliation loop, comparing desired state (the spec you wrote) with observed state (what actually exists) and taking action until they match. So the distinction interviewers test: the **CRD is the schema**, a **custom resource is an instance** of it, and the **operator is the controller** that gives it behaviour. Operators are how you encode operational knowledge - failover, backup, version upgrade, resharding - as software rather than a runbook.

## Detail

### CRD, custom resource, controller

```text
CustomResourceDefinition   "the type exists"        (cluster-scoped, one per kind)
        │
        └── CustomResource "an instance"            kind: PostgresCluster, name: orders-db
                    ▲
                    │ watch + reconcile
             Operator (a Deployment running a controller)
                    │
                    └── creates/updates: StatefulSet, Service, Secret, PVC, CronJob…
```

`kubectl api-resources` lists the new kind after the CRD is established. The `spec` is what the user asks for; the operator writes progress and health back into `status` (and, done well, `status.conditions`) - the same contract built-in controllers use.

### What the CRD gives you for free

- **Structural schema** (OpenAPI v3) with required fields, types, enums, defaults, and `x-kubernetes-validations` (CEL) rules, so bad input is rejected at admission rather than discovered at runtime.
- **Versioning and conversion**: `v1alpha1` → `v1beta1` → `v1` with one storage version and, if needed, a conversion webhook. This is how operators evolve without breaking users.
- **Subresources**: `/status` (so RBAC can let the operator write status but not spec) and `/scale` (so `kubectl scale` and even an HPA can target your custom resource).
- **`additionalPrinterColumns`**, so `kubectl get postgresclusters` shows the columns that matter.
- **RBAC, audit logging, admission webhooks, label selectors, `kubectl explain`** - all of it applies automatically, which is the real argument for a CRD over a config file in a ConfigMap.

### The reconciliation loop, which is the whole idea

A controller does not run once per event; it is **level-triggered**. It receives a watch event, reads the _current_ desired and actual state, converges them, and requeues on error with backoff. Consequences worth saying out loud: reconciliation must be **idempotent** (running it twice changes nothing extra), it must tolerate **missing events** (a resync catches drift), and it should be **edge-agnostic** - "I saw an update" is a hint to reconcile, not a description of what to do. Deletion is handled with **finalizers**: the operator adds one so Kubernetes blocks removal until it has done its cleanup (delete the cloud resource, take a final backup), then removes the finalizer. A stuck finalizer is the reason a namespace hangs in `Terminating` forever - a classic operational question.

### Why an operator beats a Deployment for stateful software

The frequently-asked version is _"a MySQL operator runs in a Pod - how is the database it manages different from a plain Deployment plus a PVC?"_ The answer is that the operator supplies the behaviour a Deployment cannot express:

| Concern                             | Deployment + PVC              | Operator                                              |
| ----------------------------------- | ----------------------------- | ----------------------------------------------------- |
| Ordered bootstrap, primary election | You script it                 | Built in, reconciled                                  |
| Failover when the primary dies      | Manual, or a human at 3 a.m.  | Detect, promote a replica, update the Service         |
| Adding a replica                    | Clone the data yourself       | Provision, seed from a base backup, join replication  |
| Version upgrade                     | Hand-run migration steps      | Encoded sequence with pre-flight checks and rollback  |
| Backups and PITR                    | External CronJob you maintain | A `Backup`/`Restore` CRD with schedules and retention |
| Configuration change                | Restart and hope              | Validate, apply, rolling restart in the right order   |
| Observability                       | You add exporters             | Ships metrics, conditions, and events                 |

That is "operational knowledge as code". The cost is real too: an operator is software you now depend on - it needs upgrades, has CVEs, holds broad RBAC (often cluster-wide), and can cause a cluster-wide incident if its reconcile logic is wrong. Choose a mature, well-maintained operator, pin its version, read its RBAC, and prefer a managed service when the operational value is not worth the dependency.

### Building one

- **Frameworks**: Kubebuilder / controller-runtime (Go, the mainstream choice), Operator SDK (Go/Ansible/Helm variants - the Helm and Ansible flavours let you wrap existing automation without writing Go), KUDO, kopf (Python), and Metacontroller for simple cases.
- **Capability levels** are a useful vocabulary: Level 1 basic install → 2 seamless upgrades → 3 full lifecycle (backup/restore) → 4 deep insights (metrics, alerts) → 5 autopilot (auto-scaling, auto-tuning). Referencing the ladder shows you understand that "we have an operator" is not one thing.
- **Practical rules**: keep the reconcile function short and idempotent, never block it on long operations (requeue instead), write meaningful `status.conditions`, emit Events, scope RBAC to the namespaces you need, run with leader election so two replicas do not fight, and treat CRD schema changes as an API-compatibility problem.

### The lifecycle detail that catches teams

CRDs installed by Helm from the `crds/` directory are **applied once and never upgraded or deleted** by Helm. Operator upgrades therefore frequently require applying the new CRDs yourself, in the right order, before the new controller starts - and deleting a CRD **cascades to every instance of it**, so `kubectl delete crd postgresclusters...` deletes every database. Say that; it is the sort of thing you only learn by having nearly done it.

## Example

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata: { name: postgresclusters.acme.io }
spec:
  group: acme.io
  scope: Namespaced
  names:
    { kind: PostgresCluster, plural: postgresclusters, singular: postgrescluster, shortNames: [pgc] }
  versions:
    - name: v1
      served: true
      storage: true
      subresources:
        status: {} # operator writes status without spec permissions
        scale: { specReplicasPath: .spec.replicas, statusReplicasPath: .status.readyReplicas }
      additionalPrinterColumns:
        - { name: Replicas, type: integer, jsonPath: .spec.replicas }
        - { name: Primary, type: string, jsonPath: .status.primary }
        - { name: Phase, type: string, jsonPath: .status.phase }
      schema:
        openAPIV3Schema:
          type: object
          required: [spec]
          properties:
            spec:
              type: object
              required: [version, replicas, storage]
              properties:
                version: { type: string, enum: ["15", "16"] }
                replicas: { type: integer, minimum: 1, maximum: 9, default: 3 }
                storage: { type: string, pattern: "^[0-9]+Gi$" }
                backup:
                  type: object
                  properties:
                    schedule: { type: string, default: "0 2 * * *" }
                    retentionDays: { type: integer, default: 14 }
              x-kubernetes-validations:
                - rule: "self.replicas % 2 == 1"
                  message: "replicas must be odd so the cluster can hold quorum"
```

```yaml
# An instance: the user asks for a database, not for 14 objects
apiVersion: acme.io/v1
kind: PostgresCluster
metadata: { name: orders-db, namespace: payments }
spec:
  version: "16"
  replicas: 3
  storage: 200Gi
  backup: { schedule: "0 */6 * * *", retentionDays: 30 }
```

```bash
# It is a first-class API object: same tooling, same RBAC, same audit trail
kubectl api-resources --api-group=acme.io
kubectl explain postgrescluster.spec.backup
kubectl get pgc -n payments
# NAME        REPLICAS   PRIMARY        PHASE
# orders-db   3          orders-db-0    Running
kubectl auth can-i create postgresclusters --as system:serviceaccount:payments:dev

# What the operator built on your behalf
kubectl get statefulset,svc,secret,cronjob -n payments -l acme.io/cluster=orders-db
kubectl describe pgc orders-db -n payments | sed -n '/Conditions/,$p'
kubectl logs -n operators deploy/postgres-operator --tail=100   # reconcile errors live here

# Danger: deleting the CRD deletes every instance of it
kubectl get crd postgresclusters.acme.io -o jsonpath='{.spec.names.kind}{"\n"}'
```

```bash
# The finalizer problem: a namespace stuck Terminating
kubectl get pgc orders-db -n payments -o jsonpath='{.metadata.finalizers}'
# only after confirming the operator cannot complete its cleanup:
kubectl patch pgc orders-db -n payments -p '{"metadata":{"finalizers":null}}' --type=merge
```

## Interview tips

- Separate the three concepts in your first sentence: the CRD is the **type**, the custom resource is an **instance**, the operator is the **controller**. Then say the line that proves you get it - "a CRD without a controller just stores YAML; nothing happens."
- Describe reconciliation as **level-triggered and idempotent**, comparing desired to observed state and requeuing with backoff. That is the language of someone who has written or read a controller.
- Mention finalizers and immediately connect them to the practical symptom - a namespace stuck in `Terminating` - because that is how the topic usually arrives in a real interview.
- For the MySQL-operator-versus-Deployment question, answer in capabilities: failover, replica bootstrap from a base backup, ordered upgrades, backup/restore as CRDs, config changes applied in the right order. Then name the cost: another piece of software with broad RBAC that you must upgrade and monitor.
- List what a CRD gives you for free - schema validation, versioning with conversion, `/status` and `/scale` subresources, RBAC, audit, printer columns. It explains _why_ CRDs rather than config files.
- Know the Helm CRD lifecycle gap (`crds/` is install-once) and that deleting a CRD deletes all its instances. Both are operational scars worth showing.
- If asked how you would run a shell script before every container starts, note that this is an init container's job, not an operator's - and an operator would be the tool if you needed it enforced across every workload, via a mutating webhook. See [what is inside a Helm chart](./what-is-inside-a-helm-chart-and-how-do-you-customise-one.md), [running a multi-tenant Kubernetes cluster](./how-do-you-run-a-multi-tenant-kubernetes-cluster.md), [Kubernetes admission control with Kyverno or OPA Gatekeeper](../devsecops/how-do-you-enforce-kubernetes-admission-control-with-kyverno-or-opa-gatekeeper.md), and [what is Crossplane and how does it compare to Terraform](../platform-engineering/what-is-crossplane-and-how-does-it-compare-to-terraform.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you scale CI/CD across many services and teams?]] (`#459`): [How do you scale CI/CD across many services and teams?](../cicd/how-do-you-scale-ci-cd-across-many-services-and-teams.md)
- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Container Orchestration Advanced](./README.md) · [All topics](../README.md)
