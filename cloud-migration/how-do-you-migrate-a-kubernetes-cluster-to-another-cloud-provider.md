---
title: "How do you migrate a Kubernetes cluster to another cloud provider?"
id: 432
category: "Cloud Migration"
difficulty: "Advanced"
tags:
  - devops
  - cloud-migration
  - interview-questions
  - kubernetes
  - backup-and-disaster-recovery
  - cloud-engineering
---

# How do you migrate a Kubernetes cluster to another cloud provider?

**Short answer:** Do not migrate the cluster - **rebuild it** on the target and move the workloads into it. Stand up the new cluster from Infrastructure as Code, redeploy every application from Git via GitOps, replicate the data separately, then shift traffic gradually at the DNS or global load-balancer layer with the old cluster kept warm as the rollback. The work is almost never in the Deployments; it is in everything that touches the provider: **storage classes and existing volumes**, **LoadBalancer and Ingress annotations**, **IAM integration** (IRSA versus Workload Identity versus Entra workload identity), **the CNI and its IP model**, **managed add-ons**, **container registries**, and **DNS and certificates**. Velero moves cluster objects and PVs; it does not translate any of those provider-specific pieces.

## Detail

### The portable part and the provider-specific part

Portable, essentially unchanged: Deployments, StatefulSets, Services, ConfigMaps, HPAs, NetworkPolicies, CRDs. Provider-specific, and where all the effort lives:

| Concern            | What changes                                                                                          |
| ------------------ | ----------------------------------------------------------------------------------------------------- |
| **Storage**        | `StorageClass` provisioner and parameters; EBS/Azure Disk/PD are not portable, so data must be copied |
| **Load balancing** | `Service` and `Ingress` annotations are entirely provider-specific; controller differs                |
| **Identity**       | IRSA / EKS Pod Identity → GKE Workload Identity → Entra Workload ID; every service account changes    |
| **Networking**     | CNI, Pod CIDR sizing, IP-per-Pod limits, private endpoint layout, egress NAT                          |
| **Add-ons**        | Cluster autoscaler vs Karpenter, DNS, metrics, CSI drivers, monitoring agents                         |
| **Registry**       | ECR → GAR → ACR: image copy plus imagePullSecrets or workload identity                                |
| **Secrets**        | Secrets Manager → Secret Manager → Key Vault; the CSI/ESO configuration is rewritten                  |
| **Node images**    | AMI → node image family; taints, labels, and bootstrap differ                                         |
| **Observability**  | CloudWatch → Cloud Logging → Azure Monitor, or the chance to move to a portable stack                 |

An honest answer names these before reaching for a tool, because "we ran Velero and it worked" is only true for the stateless half.

### The migration, in phases

1. **Inventory and portability audit.** Every namespace, every CRD and operator, every PVC and its size and access mode, every LoadBalancer and Ingress, every service account with cloud permissions, every external dependency and its allow-list of source IPs. Flag anything provider-locked (a proprietary database, a managed queue, an ALB-specific WAF rule) - those are separate decisions, not cluster work.
2. **Build the target cluster from code.** Terraform (or the provider's equivalent) for the cluster, node pools, networking, and IAM. Non-overlapping CIDRs with the source, in case you need connectivity between them during the transition.
3. **Redeploy applications from Git, not from the old cluster.** This is the key decision: if your manifests are in Git and applied by ArgoCD or Flux, the "migration" of stateless workloads is registering a new cluster and letting it sync. Provider-specific values move into a per-cluster overlay. If they are _not_ in Git, do that first - it is the migration. See [what is GitOps](../devops-tools-and-automation/what-is-gitops.md).
4. **Move the data.** The part with real risk, handled per system:
   - **Databases**: replicate with the engine's own replication or a change-data-capture tool, then cut over with a short freeze. See [how do you migrate a production database to the cloud with near-zero downtime](./how-do-you-migrate-a-production-database-to-the-cloud-with-near-zero-downtime.md).
   - **Object storage**: bulk copy, then a delta sync, then dual-write or a redirect until the cutover.
   - **PersistentVolumes**: Velero with a file-level backup (Restic/Kopia) can restore into a different provider's storage class, because volume snapshots themselves are not portable. For large or busy volumes, prefer the application's own replication (add a replica in the new cluster and let it stream) over copying files.
   - Anything cached or reproducible - do not migrate it, rebuild it.
5. **Rewire the provider-specific edges** in the new cluster's overlay: storage classes, ingress annotations, workload identity bindings, registry pull configuration, secret store, and DNS-controller configuration.
6. **Test properly before any traffic moves.** Full smoke and integration suites, a load test at production volume, a failure drill (kill a node, kill a zone), and a check that every external dependency accepts calls from the new egress addresses. The IP allow-list problem is the classic late surprise: partners and payment providers often filter on source IP.
7. **Shift traffic gradually.** Weighted DNS or a global load balancer: 1%, then 10%, then 50%, comparing error rate and latency between clusters at each step. Keep the old cluster fully warm. Where sessions are sticky or state is not yet shared, shift by cohort rather than by request.
8. **Decommission deliberately** - after a defined period at 100%, with backups retained and the Terraform for the old cluster kept until you are certain.

### The strategic framing worth stating

This is exactly the same procedure as a cluster **upgrade** done immutably, or a **disaster-recovery rebuild**. Teams who can rebuild a cluster from Git and restore data on demand can migrate clouds almost as a side effect; teams whose cluster state exists only in the cluster cannot, and that is the real finding. So the deliverable is not just the new cluster - it is the repeatable path. And be honest about the business case: if the motive is cost or a contract, a migration costs months of engineering time plus dual-running spend, and portability is only cheap if you already avoided the managed services you liked. See [what are the real trade-offs of multi-cloud](../cloud-engineering/what-are-the-real-trade-offs-of-multi-cloud.md) and [how do you run an application across multiple Kubernetes clusters](../container-orchestration-advanced/how-do-you-run-an-application-across-multiple-kubernetes-clusters.md).

## Example

```bash
# 1. Portability audit - what is provider-specific in what we run today?
kubectl get sc -o custom-columns='NAME:.metadata.name,PROVISIONER:.provisioner'
kubectl get svc -A -o json | jq -r '.items[]
  | select(.spec.type=="LoadBalancer")
  | "\(.metadata.namespace)/\(.metadata.name): \(.metadata.annotations // {} | keys | join(","))"'
kubectl get ingress -A -o json | jq -r '.items[] | "\(.metadata.namespace)/\(.metadata.name): \(.spec.ingressClassName)"'
kubectl get sa -A -o json | jq -r '.items[]
  | select(.metadata.annotations["eks.amazonaws.com/role-arn"])
  | "\(.metadata.namespace)/\(.metadata.name) -> \(.metadata.annotations["eks.amazonaws.com/role-arn"])"'
kubectl get pvc -A -o custom-columns='NS:.metadata.namespace,NAME:.metadata.name,SIZE:.spec.resources.requests.storage,SC:.spec.storageClassName,MODE:.spec.accessModes[0]'

# 2. Cluster objects + file-level PV data (snapshots are NOT portable across clouds)
velero install --provider aws --bucket migration-bucket --use-node-agent
velero backup create pre-migration --include-namespaces prod,data \
  --default-volumes-to-fs-backup                # Kopia/Restic: restorable elsewhere
velero backup describe pre-migration --details

# 3. On the target cluster: restore, remapping storage classes as you go
velero restore create --from-backup pre-migration \
  --namespace-mappings prod:prod \
  --exclude-resources services.v1,ingresses.networking.k8s.io   # rewrite these per provider
kubectl apply -k ./clusters/gke-prod/overlays   # provider-specific edges from Git

# 4. Verify the boring things that break late
dig +short api.example.com                       # weighted records ready?
kubectl -n prod exec deploy/checkout -- curl -s https://partner.example.com/ping
#   ^ does the partner's IP allow-list include the new egress addresses?
```

```yaml
# The per-cluster overlay: same workloads, provider-specific edges swapped
# clusters/eks-prod/overlays/storage.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata: { name: standard-rwo } # SAME NAME in both clusters - so PVCs are portable
provisioner: ebs.csi.aws.com
parameters: { type: gp3, encrypted: "true" }
volumeBindingMode: WaitForFirstConsumer
---
# clusters/gke-prod/overlays/storage.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata: { name: standard-rwo } # identical name, different provisioner
provisioner: pd.csi.storage.gke.io
parameters: { type: pd-balanced }
volumeBindingMode: WaitForFirstConsumer
```

```text
Cutover: weighted DNS, both clusters live, old one warm

  T-14d  new cluster built from Terraform, GitOps synced, smoke tests green
  T-7d   data replicating (CDC for Postgres, delta sync for object storage)
  T-3d   load test at 1.2x production peak; zone-kill drill; partner IP allow-lists updated
  T-0    1% -> 10% -> 50%  (30 min at each step, comparing 5xx and p99 side by side)
  T+1d   100% on the new cluster; old cluster still running, 0% weight = rollback
  T+14d  decommission old cluster; backups retained 90 days
```

## Interview tips

- Say "rebuild, do not migrate" in the first sentence. Anyone proposing to move a control plane between clouds has misunderstood what a cluster is.
- The strongest structural point: if the manifests live in Git and a GitOps controller applies them, migrating stateless workloads is registering a cluster - so the real work is data plus provider-specific edges.
- Enumerate the provider-specific list (storage classes, LB/Ingress annotations, workload identity, CNI and IP model, add-ons, registry, secrets, node images). This is what interviewers are actually testing.
- Be precise that volume snapshots are not portable, so PV data needs file-level backup (Velero with Kopia/Restic) or, better, the application's own replication into the new cluster.
- Mention keeping the same `StorageClass` **name** across clusters with different provisioners - a small trick that keeps PVCs portable.
- The partner IP allow-list surprise is an excellent detail: new cluster, new egress addresses, and a third party silently rejecting you at cutover.
- Describe the gradual weighted cutover with both clusters live and the old one warm as the rollback, rather than a big-bang switch.
- Close on the strategic point: this procedure is identical to an immutable cluster upgrade and to a DR rebuild, so the durable deliverable is the repeatable path - and be honest that migration costs months and dual-running spend. See [what is cloud migration](./what-is-cloud-migration.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Migration](./README.md) · [All topics](../README.md)
