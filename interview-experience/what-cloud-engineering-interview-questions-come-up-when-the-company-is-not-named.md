---
title: "What cloud engineering interview questions come up when the company is not named?"
id: 363
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - unattributed
  - kubernetes
  - aws-engineering
  - container-orchestration-advanced
  - infrastructure-as-code
  - cloud-cost-optimization
  - cloud-migration
  - network-security
---

# What cloud engineering interview questions come up when the company is not named?

## Questions

These come from two reported interviews whose submitters did not name the employer — a Senior Cloud Administrator round at 6 years of experience, and an AWS Cloud Engineer round.

### Round set 1 — Senior Cloud Administrator (6 YOE)

**Kubernetes architecture and operations**

- **Explain the Kubernetes architecture in depth, covering what every component does. And how would you join a new node to the control plane?**
- **The kubelet is the node-side agent. Is there an equivalent agent that manages the control-plane side of things?**
- **Which controller manages self-managed worker nodes?**
- **Walk through the entire EKS cluster upgrade process.**
- **When would you prefer an on-premises Kubernetes cluster over EKS, and when the other way round?**

**Scaling and scheduling**

- **If you implement an HPA for a StatefulSet, a new Pod arrives with an empty PersistentVolumeClaim. How can it serve requests?**
- **When would you use an HPA and when a VPA? Give an example of each.**
- **What is Karpenter, and on which metric does it scale up and down?**
- **Explain `nodeSelector`, taints, and tolerations.**
- **A Pod is in `Pending`. What are the reasons?**
- **Why would an application need to be deployed as a StatefulSet?**

**Security, registry, and delivery**

- **How would you implement security for Kubernetes — on both the container side and the infrastructure side — using native Kubernetes mechanisms?**
- **What is ECR and how do you use it?**
- **Which Helm commands do you use, how would you deploy an application via Helm, and how do you integrate that whole process into CI/CD?**

**Your estate**

- **How would you set up a new environment on AWS, and how is the Terraform code provisioned?**
- **How are you provisioning infrastructure with Terraform through CI/CD?**
- **How many clusters are you managing, and how many add-ons have you deployed?**

### Round set 2 — AWS Cloud Engineer

- **Explain the OSI model.**
- **How did you do cost optimisation in AWS?**
- **Explain Lambda, CloudFormation templates, data storage, and S3.**
- **How do you implement good security policies on AWS?**
- **Explain how you carried out your cloud migration.**
- **What motivates you about this role?**

## Example

```text
Unattributed cloud rounds — two reported interviews (23 questions)

  SET 1  Senior Cloud Administrator (6 YOE)      17
         K8s architecture + ops        5   components, join a node, control-plane
                                           agent, self-managed node controller,
                                           EKS upgrade, on-prem vs EKS
         Scaling and scheduling        6   HPA on a StatefulSet (empty PVC!),
                                           HPA vs VPA, Karpenter, taints,
                                           Pending causes, why StatefulSet
         Security / registry / Helm    3   native K8s security, ECR, Helm + CI/CD
         Your estate                   3   new AWS environment, Terraform via
                                           CI/CD, cluster and add-on counts

  SET 2  AWS Cloud Engineer                       6
         OSI model, AWS cost optimisation, Lambda + CFT + S3,
         AWS security policies, cloud migration, motivation

THE QUESTION THAT DEFINES SET 1
  "HPA on a StatefulSet — the new Pod's PVC is empty, so how does it serve
  requests?" This is a deliberately constructed trap and most candidates
  answer it wrongly by describing volume cloning.
```

## Interview tips

- The empty-PVC question is the best in this set, and the correct answer is to challenge the premise. Horizontally scaling a StatefulSet does not replicate data — each new Pod gets its _own_ fresh PersistentVolumeClaim from the `volumeClaimTemplates`, so it starts empty by design. Whether it can serve requests depends entirely on the application: a clustered system such as Cassandra, Kafka, or Elasticsearch handles this natively because the new member joins the cluster and streams or is assigned data from its peers; a single-writer database cannot, which is why you never horizontally autoscale a primary database. So the honest answer is that an HPA on a StatefulSet is appropriate only when the application knows how to admit a new member, and otherwise the correct answer is that you should not be autoscaling it at all. Add that scaling _down_ leaves the PVC behind by default, which is deliberate so data is not lost. See [StatefulSets](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md) and [autoscaling workloads and nodes](../kubernetes/how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md).
- "Is there an agent like the kubelet for the control plane?" is a subtle question with a precise answer: no, there is no control-plane equivalent of the kubelet. The control plane is a set of components — API server, etcd, scheduler, controller manager, cloud controller manager — and on a `kubeadm` cluster those run as _static Pods_ managed by the kubelet on each control-plane node, which is the closest thing to what they are describing. On a managed service the provider runs them for you and you never see them. Saying "the kubelet is what runs the control plane's static Pods" is the answer that lands. See [main components of Kubernetes architecture](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md).
- Joining a node should be answered concretely: `kubeadm token create --print-join-command` on a control-plane node, then run the resulting `kubeadm join` on the new node with the token and the CA certificate hash — which is how the node authenticates the control plane rather than trusting it blindly. On EKS the equivalent is a managed node group, or a self-managed node whose bootstrap script registers it, plus the access entry or `aws-auth` mapping that lets its IAM role authenticate. Mention that a node stuck `NotReady` after joining is usually the CNI not yet installed.
- Karpenter has a specific answer that distinguishes it from the Cluster Autoscaler, and the question about "which metric" is the trap: Karpenter does **not** scale on a metric such as CPU. It watches for _unschedulable Pods_ and provisions right-sized nodes directly against the EC2 fleet API to satisfy their aggregate requests, then consolidates and terminates underutilised nodes. The Cluster Autoscaler by contrast works through fixed auto-scaling groups and node group sizes. Saying "pending Pods and their resource requests, not a utilisation metric" is the correct answer.
- HPA versus VPA needs an example each because they asked for one. HPA adds replicas — use it for a stateless web or API tier scaling on request rate or CPU. VPA adjusts a single Pod's requests and limits from observed usage — use it for a workload that cannot scale horizontally, such as a single-instance batch processor or a controller. Add the warning that HPA and VPA on the same metric for the same workload conflict, and that VPA historically required a restart to apply new values.
- Native Kubernetes security should be answered in the two halves the question names. Infrastructure side: private API endpoint or authorised IP ranges, RBAC bound to least-privilege roles, separate namespaces with ResourceQuotas, NetworkPolicies default-deny, encryption at rest for etcd, audit logging, and regular node image upgrades. Container side: Pod Security Admission enforcing the `restricted` profile, `runAsNonRoot` with a read-only root filesystem and dropped capabilities, no `privileged` and no host namespaces, `seccomp` and AppArmor profiles, image provenance and admission control with Kyverno or Gatekeeper, and secrets from an external store. The phrase "native solutions" is inviting Pod Security Admission and NetworkPolicy specifically, so name both. See [enforcing admission control with Kyverno or OPA Gatekeeper](../devsecops/how-do-you-enforce-kubernetes-admission-control-with-kyverno-or-opa-gatekeeper.md) and [how RBAC works in Kubernetes](../kubernetes/how-does-rbac-work-in-kubernetes.md).
- On-premises versus EKS should be decided by constraints, not preference. On-premises wins when data residency or regulation forbids the cloud, when you have existing hardware and capacity to amortise, when latency to on-premises systems matters, or when egress costs would dominate. EKS wins when you do not want to own etcd backups, control-plane upgrades, and certificate rotation, when you need elastic capacity, and when integration with cloud IAM, load balancers, and storage saves real work. Say that the true cost of on-premises is the team that has to run the control plane at 3am.
- The EKS upgrade walkthrough has a fixed order and interviewers listen for it: check the Kubernetes version skew policy and deprecated API usage first, upgrade the control plane one minor version at a time, then upgrade the add-ons — VPC CNI, CoreDNS, kube-proxy, EBS CSI — then roll the node groups, cordoning and draining while respecting PodDisruptionBudgets, and verify afterwards that all nodes report the new version and nothing is `Pending` or crash-looping. Say you would test in a non-production cluster and check `kubectl api-resources` and audit logs for removed APIs before starting.
- Pod `Pending` is asked in almost every round in this collection: insufficient CPU or memory on any node, no node matching `nodeSelector` or affinity, an untolerated taint, an unbound PVC — often because the volume is in the wrong availability zone — or exhausted quota. `kubectl describe pod` and read the scheduler events. See [troubleshooting a Pod stuck in Pending or CrashLoopBackOff](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md).
- The three "your estate" questions — how many clusters, how many add-ons, how you provision — are calibration questions. Have exact numbers ready; a senior administrator who cannot say how many clusters they run sounds like they do not run them.
- In the Cloud Engineer round, "explain Lambda, CFT, data storage, and S3" is a breadth sweep, so structure it rather than rambling: Lambda as event-driven compute with its concurrency and duration constraints, CloudFormation as AWS-native declarative IaC with no state file to manage, then the storage taxonomy — object (S3), block (EBS), file (EFS) — and S3's storage classes and lifecycle rules. Grouping storage by type is what makes it sound like knowledge rather than recall. See [S3 storage classes](../aws-engineering/what-are-the-s3-storage-classes-and-when-do-you-use-each.md) and [when to choose CloudFormation, CDK, or Terraform](../aws-engineering/when-do-you-choose-cloudformation-cdk-or-terraform-on-aws.md).
- For AWS security policies, give layered controls rather than a list of services: identity through federated short-lived credentials with no long-lived keys, guardrails through service control policies and permission boundaries, network isolation with private subnets and VPC endpoints, encryption with customer-managed KMS keys, detection with CloudTrail, GuardDuty, and Config, and least privilege generated from observed activity with Access Analyzer. See [least-privilege identity in the cloud](../cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md).
- The migration question wants a narrative with a decision in it: what you assessed, which of the migration patterns you chose per workload — rehost, replatform, refactor — how you moved the data and cut over, and what you would do differently. See [connecting an on-premises network to the cloud](../cloud-engineering/how-do-you-connect-an-on-premises-network-to-the-cloud.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)
- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
