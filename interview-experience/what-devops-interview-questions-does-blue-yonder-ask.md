---
title: "What DevOps interview questions does Blue Yonder ask?"
id: 319
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - blue-yonder
  - azure-engineering
  - kubernetes
  - devsecops
  - cloud-cost-optimization
  - scalability-and-high-availability
  - cicd
---

# What DevOps interview questions does Blue Yonder ask?

## Questions

**Secrets and identity**

- **How do you consume Azure Key Vault secrets inside AKS?**
- **When a secret is rotated in Key Vault, how does the running container or Pod pick up the new value?**
- **How do you integrate Entra ID with AKS for cluster authentication?**

**Cluster security, availability, and cost**

- **How do you secure an AKS cluster?**
- **How do you make an AKS cluster highly available?**
- **How do you perform cost optimisation on AKS?**

**Scaling**

- **Which HPA triggers have you used, and what types of trigger are available?**

**State**

- **What is the difference between a stateful and a stateless workload?**
- **If an application is stateless, where does its data actually live and how do you manage it?**

**Pipeline security tooling**

- **How do you integrate SonarQube and Snyk into an Azure DevOps pipeline?**

## Example

```text
Blue Yonder — DevOps Engineer, reported round
10 questions

  Secrets and identity        3   Key Vault in AKS, rotated-secret pickup,
                                  Entra ID integration
  Cluster security / HA / cost 3  harden AKS, make it HA, reduce its cost
  State                       2   stateful vs stateless, stateless data
  Scaling                     1   HPA trigger types
  Pipeline security           1   SonarQube + Snyk in Azure Pipelines

100% AZURE
  Not one AWS or GCP question. If AKS is not your daily platform, the
  AWS-equivalent answer will not carry you — the interviewer names Azure
  services in every question.
```

## Interview tips

- The rotated-secret question is the one that separates candidates, because "mount the secret" is not an answer. The Key Vault provider for the Secrets Store CSI driver polls and updates the mounted file on rotation, so a file-watching application sees the change — but an application that read the value once at startup, or a synced Kubernetes Secret consumed as an environment variable, will _not_. Environment variables are immutable for the container's lifetime. Say that, then give the fixes: watch the file, use a sidecar or reloader that triggers a rolling restart, or fetch from Key Vault at request time. This is the single highest-value answer in the round.
- For Key Vault access itself, name workload identity — a Kubernetes service account federated to an Entra ID application — rather than the deprecated pod-identity approach or a stored connection string. The equivalent concept on AWS is described in [securing Pod access to AWS resources](../aws-engineering/how-do-you-secure-pod-access-to-aws-resources-using-eks-pod-identity-or-irsa.md).
- Securing AKS is a breadth question, so answer in layers: private API server or authorised IP ranges, Entra ID plus Kubernetes RBAC, network policies between namespaces, no privileged containers enforced by admission control, image scanning and a trusted registry, secrets from Key Vault rather than manifests, and node image auto-upgrade. See [enforcing admission control with Kyverno or OPA Gatekeeper](../devsecops/how-do-you-enforce-kubernetes-admission-control-with-kyverno-or-opa-gatekeeper.md) and [zero-trust security](../network-security/what-is-zero-trust-security.md).
- High availability on AKS has a specific vocabulary: multiple node pools spread across availability zones, the uptime SLA tier for the control plane, a minimum of three replicas with anti-affinity or topology spread constraints, PodDisruptionBudgets so upgrades cannot drain a service to zero, and multi-region only if the data tier supports it. PDBs are the detail interviewers listen for. See [high availability](../scalability-and-high-availability/what-is-high-availability.md) and [controlling which node a Pod runs on](../kubernetes/how-do-you-control-which-node-a-pod-runs-on.md).
- AKS cost optimisation should reach spot node pools for interruptible work, right-sized requests and limits driven by observed usage, the cluster autoscaler plus scale-to-zero on user node pools, reserved instances or savings plans for the steady baseline, and cutting log ingestion volume — which is very often the largest line item after compute. See [cloud cost optimisation](../cloud-cost-optimization/what-is-cloud-cost-optimization.md).
- On HPA triggers, distinguish native from extended: CPU and memory utilisation come built in, custom and external metrics need an adapter, and KEDA is what you use to scale on queue depth, an HTTP rate, or a Service Bus backlog. Naming KEDA is the expected answer for event-driven scaling on Azure. See [autoscaling workloads and nodes](../kubernetes/how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md).
- The stateless follow-up is a trap worth catching: a stateless application still has data, it just does not keep it locally — it lives in a database, cache, object store, or queue, and that is precisely what makes the Pod disposable. Then contrast with StatefulSets, stable network identity, and per-replica volumes for the workloads that genuinely cannot be stateless. See [StatefulSets](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md).
- For SonarQube and Snyk, describe them as gates rather than steps: SonarQube runs after unit tests and fails the build on a quality-gate breach, Snyk scans dependencies and the container image, and you decide which severity blocks the pipeline versus which only files a ticket. That policy decision is the real question. See [SAST, DAST, IAST, and SCA](../devsecops/what-is-the-difference-between-sast-dast-iast-and-sca.md) and [what a DevSecOps pipeline looks like end to end](../devsecops/what-does-a-devsecops-pipeline-look-like-end-to-end.md).

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
