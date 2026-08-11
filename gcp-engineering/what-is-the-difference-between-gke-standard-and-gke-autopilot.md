---
title: "What is the difference between GKE Standard and GKE Autopilot?"
id: 210
category: "GCP Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - gcp-engineering
  - interview-questions
---

# What is the difference between GKE Standard and GKE Autopilot?

**Short answer:** In Standard mode you manage node pools - machine types, autoscaling, upgrades, and bin-packing - and pay for nodes. In Autopilot, Google manages nodes entirely and you pay for the CPU, memory, and storage your Pods request. Autopilot removes node operations and enforces hardened defaults, at the cost of restrictions on privileged workloads and host access.

## Detail

| Dimension       | Standard                                                            | Autopilot                                              |
| --------------- | ------------------------------------------------------------------- | ------------------------------------------------------ |
| Billing unit    | nodes (whether or not Pods use them)                                | Pod resource requests                                  |
| Node management | yours: pools, sizes, upgrades, repair                               | Google's                                               |
| Bin-packing     | your responsibility                                                 | handled, but per-Pod pricing removes the incentive     |
| Privileged Pods | allowed                                                             | blocked (no privileged, limited host paths)            |
| DaemonSets      | full support                                                        | supported with constraints                             |
| Good fit        | GPUs, custom kernels, agents needing host access, dense bin-packing | most stateless services, teams without a platform team |

**Requests become the contract in Autopilot.** Because you pay for requests, over-requesting is directly wasteful and under-requesting causes throttling - so accurate requests, and Vertical Pod Autoscaler recommendations, matter more than in Standard mode where slack is absorbed by the node you already paid for. Autopilot also applies minimum and rounding rules to requests, which surprises people converting existing manifests.

**Security posture is stronger by default in Autopilot:** Workload Identity is required, Shielded GKE Nodes are on, privileged containers and most host mounts are blocked, and node SSH is unavailable. That last point is also its main operational limitation - debugging techniques relying on the node are simply not available, so you need good observability instead.

**Where Standard is still necessary:** GPU or TPU workloads with specific drivers, security or observability agents that need privileged host access, workloads needing specific machine families or local SSDs, very dense bin-packing of tiny Pods, and any use of custom node images or kernel tuning.

**Regional versus zonal, in either mode.** Regional clusters replicate the control plane across three zones and spread nodes across them - the default for production. Zonal clusters are cheaper but a zone outage takes the cluster's control plane with it. Combine with `topologySpreadConstraints` so a zone failure does not remove all replicas of a service.

**Common to both:** release channels (rapid/regular/stable) for automatic upgrades, maintenance windows, Workload Identity for keyless access to Google APIs, GKE Dataplane V2 (eBPF/Cilium) for network policy and visibility, and Backup for GKE for stateful workloads. Version support is time-bounded, so upgrades are unavoidable in both modes - Autopilot just performs them for you.

## Example

```bash
# Autopilot: no node configuration to specify at all
gcloud container clusters create-auto checkout-prod \
  --region=europe-west1 \
  --release-channel=regular \
  --enable-private-nodes \
  --network=vpc-prod --subnetwork=sn-prod-euw1 \
  --cluster-secondary-range-name=pods --services-secondary-range-name=services
```

```yaml
# Requests are what you pay for in Autopilot - set them deliberately
apiVersion: apps/v1
kind: Deployment
metadata: { name: checkout }
spec:
  replicas: 3
  selector: { matchLabels: { app: checkout } }
  template:
    metadata: { labels: { app: checkout } }
    spec:
      serviceAccountName: checkout # Workload Identity, no keys
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector: { matchLabels: { app: checkout } }
      containers:
        - name: api
          image: europe-docker.pkg.dev/payments-prod/apps/checkout@sha256:1f4b
          resources:
            requests: { cpu: "500m", memory: "512Mi" }
            limits: { memory: "512Mi" }
```

## Interview tips

- The billing distinction - nodes versus Pod requests - is the cleanest way to express the difference.
- Say that Autopilot blocks privileged Pods and node SSH, and give an example of a workload that therefore needs Standard.
- Expect: "which would you pick?" - Autopilot as the default for ordinary services, Standard where the exceptions apply.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is Google Cloud Platform (GCP)?]] (`#24`): [What is Google Cloud Platform (GCP)?](../cloud-platforms/what-is-google-cloud-platform-gcp.md)
- [[What are the different types of cloud services?]] (`#25`): [What are the different types of cloud services?](../cloud-platforms/what-are-the-different-types-of-cloud-services.md)
- [[How do you choose a cloud provider for a new workload?]] (`#281`): [How do you choose a cloud provider for a new workload?](../cloud-platforms/how-do-you-choose-a-cloud-provider-for-a-new-workload.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to GCP Engineering](./README.md) · [All topics](../README.md)
