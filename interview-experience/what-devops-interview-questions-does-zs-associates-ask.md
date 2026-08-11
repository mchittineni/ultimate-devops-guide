---
title: "What DevOps interview questions does ZS Associates ask?"
id: 393
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - zs-associates
  - kubernetes
  - docker
  - aws-engineering
  - infrastructure-as-code
  - network-security
  - container-orchestration-advanced
  - devops-tools-and-automation
---

# What DevOps interview questions does ZS Associates ask?

## Questions

**Docker**

- **What is a multi-stage Docker build, in which scenarios is it useful, and is it suitable for compiled languages?**
- **Explain layer caching with an example.**
- **What is privileged mode in Docker? Explain with an example.**

**Kubernetes networking**

- **Design an architecture so that a request to your application hostname resolves through to the backend service.**
- **What is the difference between Calico and the VPC CNI plugin, why would you prefer one over the other, and how does each help set up Pod networking?**
- **How is an IP address allocated to a Pod? Does the CNI plugin use the same CIDR range the VPC provides, or a different one?**
- **Two Pods that are part of the same ReplicaSet cannot communicate with each other. What could be the reason?**
- **What are Ingress and the Gateway API?**

**Scaling and Karpenter**

- **How do you handle extra traffic arriving at your Pods — which solution would you implement?**
- **After implementing an HPA, some Pods are still in `Pending`. What could be the reason?**
- **How would you provision Karpenter, and what does its configuration need?**
- **How does Karpenter know which node to provision, and how does it learn about resource constraints?**

**Workloads and reliability**

- **Can you deploy a MongoDB database in an EKS cluster? If so, how, and what configuration considerations matter?**
- **What are the possible reasons for a Pod to be stuck in `CrashLoopBackOff`?**
- **A ReplicaSet has three Pods and one is not coming up. What could be the reason?**
- **There are three backend Pods in three different regions. If one Pod goes down, how is the request managed?**

**Load balancing and TLS**

- **You configured a load balancer but it is not accepting HTTPS requests. What would you do?**
- **Without installing a certificate, how would you redirect traffic coming in over HTTP to HTTPS?**

**Workload identity**

- **A backend Pod needs to interact with S3 and Lambda. How do you achieve that?**
- **How does the service account know which role to assume, and what do you configure on the service account?**

**Delivery and estate**

- **What is Argo CD, how do you manage CI/CD in your organisation, how many EKS clusters do you manage, and how many nodes?**

**Terraform**

- **How do you implement state locking in Terraform?**
- **Explain `for_each` in Terraform with an example, and answer some questions on modules.**
- **If you want to deploy EC2 instances in three different regions, what would the Terraform code structure look like?**
- **You changed a module for one resource. The resource should be updated but not destroyed and recreated when you run `terraform apply`. How do you approach that?**
- **You want to create a module for an EKS cluster. What would its structure be?**

## Example

```text
ZS Associates — DevOps Engineer (6 YOE), reported round
27 questions

  Kubernetes networking       5   hostname-to-backend design, Calico vs VPC
                                  CNI, how a Pod gets its IP, two Pods in one
                                  ReplicaSet cannot talk, Ingress vs Gateway API
  Terraform                   5   state locking, for_each, three-region
                                  structure, update-without-recreate, EKS module
  Scaling and Karpenter       4   handle extra traffic, Pending after HPA,
                                  provisioning Karpenter, how it picks a node
  Workloads and reliability   4   MongoDB on EKS, CrashLoopBackOff causes,
                                  1 of 3 ReplicaSet Pods down, cross-region
                                  Pod failure
  Docker                      3   multi-stage for compiled languages, layer
                                  caching, privileged mode
  Workload identity           2   Pod to S3 and Lambda, how the service
                                  account picks the role
  LB and TLS                  2   LB refusing HTTPS, HTTP-to-HTTPS without
                                  a certificate
  Delivery and estate         1   Argo CD + cluster and node counts

THE STANDOUT TOPIC
  Karpenter appears twice with real depth — how you provision it and how it
  decides which node to launch. Almost no other round in this collection asks
  about it, and the answer is genuinely different from Cluster Autoscaler.
```

## Interview tips

- The Pod-IP-allocation question is the crux of the networking block and has a definite answer for EKS: with the **AWS VPC CNI**, every Pod gets a **real VPC IP address from the same subnet CIDR as the nodes** — not a separate overlay range — because the CNI attaches secondary IPs to the node's ENIs and hands them to Pods. That is why Pods are directly routable from anywhere in the VPC, and why subnet IP exhaustion is a real EKS failure mode. Contrast that with an overlay CNI such as Calico in VXLAN or IPIP mode, which allocates from its **own** cluster CIDR independent of the VPC and encapsulates traffic between nodes. Say the trade-off plainly: VPC CNI gives native routability, security-group-per-Pod, and no encapsulation overhead, at the cost of consuming VPC addresses; Calico conserves VPC addresses and brings a mature NetworkPolicy implementation, at the cost of an overlay and Pods not being VPC-routable. Add that the VPC CNI historically did **not** enforce NetworkPolicy at all, which is exactly why many EKS clusters run Calico alongside it — that detail answers the "why prefer one" half.
- The two-Karpenter questions deserve a precise answer because Karpenter works differently from the Cluster Autoscaler. It watches for **unschedulable Pods**, reads their aggregate resource requests plus their constraints — node selectors, affinities, tolerations, topology spread, and architecture — and then calls the EC2 fleet API directly to launch a **right-sized** instance that satisfies them, rather than scaling a pre-defined Auto Scaling group to a fixed instance type. So it does not scale on a utilisation metric; it scales on pending-Pod requirements. For provisioning: install the controller via Helm, give it an IAM role via IRSA or Pod Identity with EC2 and IAM permissions, tag the subnets and security groups it should discover, and define `NodePool` and `EC2NodeClass` resources specifying allowed instance families, capacity types (on-demand and spot), AMI family, and disruption settings including consolidation and expiry. Say that consolidation — replacing under-used nodes with cheaper ones — is what makes Karpenter a cost tool as well as a scaling tool. This also answers the Pending-after-HPA question: the HPA created replicas but no node had room, so the missing piece is node-level autoscaling. See [autoscaling workloads and nodes](../kubernetes/how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md).
- "Two Pods in the same ReplicaSet cannot communicate" is a good question because being in one ReplicaSet is irrelevant to networking — say that first. The real candidates: a NetworkPolicy denying traffic, which drops packets **silently** with no error or event and is the most common cause; the Pods are trying to reach each other through a Service whose `Endpoints` are empty or whose `targetPort` is wrong; the application binds to `127.0.0.1` rather than `0.0.0.0`, so it is unreachable from outside its own network namespace; CoreDNS is failing so name resolution breaks; or the CNI dataplane is broken on one node. Say you would `exec` in and test with `curl` to the peer's Pod IP directly and then to the Service name, because that split immediately separates a DNS problem from a connectivity problem. See [network segmentation](../network-security/what-is-network-segmentation.md).
- The HTTP-to-HTTPS-without-a-certificate question is a nice trap: you **cannot serve** HTTPS without a certificate, but you can **redirect** to it without one, because the redirect happens on the plain-HTTP listener. So the answer is a listener rule on port 80 that returns a 301 to `https://` — an ALB listener with a `redirect` action, or `nginx.ingress.kubernetes.io/ssl-redirect: "true"` on an Ingress. Say explicitly that the HTTPS listener still needs a certificate for the redirected request to succeed, so the honest framing is "the redirect needs no certificate; the destination does". That pairs directly with the load-balancer-refusing-HTTPS question, where the causes are: no listener on 443 at all, no certificate attached to it, the certificate not validated or in the wrong region (an ACM certificate for CloudFront must be in `us-east-1`), the security group not allowing 443, a certificate/hostname mismatch, or the target group health check failing so there is nothing to forward to. See [what SSL/TLS is](../network-security/what-is-ssl-tls.md).
- The Pod-to-S3-and-Lambda pair has one correct answer: **IRSA or EKS Pod Identity**, never an access key. For IRSA, the cluster has an OIDC identity provider registered in IAM, the IAM role's trust policy conditions on that provider's subject claim — `system:serviceaccount:<namespace>:<name>` — and the Kubernetes ServiceAccount carries the `eks.amazonaws.com/role-arn` annotation. The Pod then receives a projected service-account token, which the SDK exchanges via `sts:AssumeRoleWithWebIdentity` for temporary credentials. So the answer to "how does the service account know which role" is: the **annotation** names the role, and the role's **trust policy** must name that exact service account — both halves are required, and a mismatch is the usual cause of "it should work but does not". Add that EKS Pod Identity is the newer mechanism using an association rather than an annotation, that the Pod must use `serviceAccountName`, and that the role's policy grants `s3:GetObject` and `lambda:InvokeFunction` on specific resources — plus `kms:Decrypt` if the S3 objects are encrypted with a customer-managed key. See [securing Pod access to AWS resources using EKS Pod Identity or IRSA](../aws-engineering/how-do-you-secure-pod-access-to-aws-resources-using-eks-pod-identity-or-irsa.md).
- The update-without-recreate Terraform question is the sharpest of the five. First diagnose: run `terraform plan` and read _why_ it says destroy-and-create — the output names the attribute forcing replacement, and it is almost always an immutable field (a name, an availability zone, a subnet, an engine version on some resources). Then the options, in order of correctness: if the change is not actually needed, revert it; if the field genuinely must change, accept replacement but add `lifecycle { create_before_destroy = true }` so the new resource exists before the old is destroyed, avoiding downtime; if the drift is in a field you do not manage, use `ignore_changes` on that attribute; and if the "change" is really a refactor — a renamed resource or a move into a module — use a `moved` block or `terraform state mv`, because that updates state without touching infrastructure at all. Say that distinction clearly: a _refactor_ should never destroy anything, and if it plans to, you needed a `moved` block. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- The three-region Terraform question is a provider-alias question: declare an aliased `provider "aws"` per region, then pass the correct one into each module invocation with `providers = { aws = aws.eu_west_1 }`, because a module inherits only the default provider otherwise. Structurally, `for_each` over a map of regions to their settings so adding a region is a data change, with per-region state (or at least per-region workspaces) so one region's apply cannot break another. Add the caveat that shows experience: some resources are global — IAM, Route 53, CloudFront — and an ACM certificate for CloudFront must live in `us-east-1`, so those belong in a single "global" stack rather than being created three times. See [what are Terraform providers](../infrastructure-as-code/what-are-terraform-providers.md).
- Multi-stage builds for compiled languages is a yes, and it is precisely the best case for them — say why: you compile in a stage that has the full toolchain, then copy **only the resulting binary** into a minimal runtime stage, so the compiler, headers, build caches, and source never ship. For a statically-linked Go or Rust binary the final stage can be `scratch` or distroless, which takes an image from hundreds of megabytes to a few. For Java or .NET the runtime stage still needs a JRE or the .NET runtime, but not the SDK. Contrast with an interpreted language, where the gain is smaller because the interpreter is required at runtime — though you still drop build tools and dev dependencies. Then the layer-caching example: copy the dependency manifest and install dependencies _before_ copying source, so a code change reuses the dependency layer — and note the cascade, that changing any layer invalidates every layer above it regardless of whether their instructions changed. See [reducing Docker image size and build time](../docker/how-do-you-reduce-docker-image-size-and-build-time.md).
- Privileged mode should be answered with what it actually removes: `--privileged` grants all Linux capabilities, disables seccomp and AppArmor confinement, and gives access to host devices — so the container is effectively root on the host and can load kernel modules or access raw block devices. The legitimate examples are Docker-in-Docker for CI, a storage or networking agent that must manipulate host devices, and low-level debugging tools. Then say the security consequence and the alternatives: a privileged container is a container escape waiting to happen, so prefer specific `capabilities.add` for the one capability you need, or a rootless builder such as Kaniko or Buildah instead of Docker-in-Docker, and block privileged Pods with Pod Security Admission or a policy engine. See [how namespaces, cgroups, and capabilities isolate a container](../docker/how-do-namespaces-cgroups-and-capabilities-isolate-a-container.md).
- MongoDB on EKS is a yes-with-conditions answer, and the conditions are the substance: a StatefulSet — not a Deployment — so each replica has a stable ordinal name, a stable DNS record via a headless Service, and its own PVC from `volumeClaimTemplates`; a StorageClass with `WaitForFirstConsumer` binding so the zonal volume is created where the Pod is scheduled; anti-affinity or topology spread so replica-set members do not share a node or zone; a PodDisruptionBudget that protects quorum during upgrades; resource requests equal to limits for Guaranteed QoS so it is evicted last under node pressure; credentials from a secret store rather than a manifest; and backups via volume snapshots plus `mongodump`, because replication is not backup. Then the judgement call, which is what a six-year candidate should add: unless you have a specific reason, a managed database is usually the better choice, and if you do run it in-cluster you should use an **operator** so failover, member addition, and version upgrades are automated rather than manual. See [StatefulSets](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md).
- The three-Pods-in-three-regions question needs a correction: Pods do not span regions — a Kubernetes cluster is regional, so three Pods in three regions means three _clusters_. Once you say that, the answer is straightforward: traffic is distributed above the cluster layer by Route 53 with health checks, or Global Accelerator, so a failed region's endpoint is removed from rotation and requests go to the survivors; within a region the Service and readiness probes handle a single failed Pod. Add that the hard part is the data tier, not the routing, and that failover latency is bounded by DNS TTL unless you use anycast. See [designing for multi-region resilience](../cloud-engineering/how-do-you-design-for-multi-region-resilience.md).
- Ingress versus Gateway API is a currency question: Ingress is the original, HTTP-only, extension-by-annotation resource where every controller invents its own annotations, so configuration is not portable. The Gateway API is its successor — a role-oriented, typed set of resources (`GatewayClass`, `Gateway`, `HTTPRoute`, `GRPCRoute`) that separates the infrastructure owner's concerns from the application team's, supports protocols beyond HTTP, and expresses traffic splitting, header manipulation, and cross-namespace references (`ReferenceGrant`) natively rather than through annotations. Say that the community ingress-nginx project is now maintenance-only, which is exactly why Gateway API matters, and name a couple of implementations. See [exposing an application in Kubernetes](../kubernetes/how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md).
- For the hostname-to-backend design question, answer as one continuous chain and say where each piece lives: Route 53 alias record pointing at an internet-facing ALB in public subnets; the ALB listener terminating TLS with an ACM certificate; the AWS Load Balancer Controller having provisioned it from your Ingress or Gateway, registering Pod IPs directly as targets in IP mode; the ingress rules matching host and path to a Service; the Service selecting Pods by label; and the Pod's container port receiving the request — with nodes and Pods in private subnets and a NAT gateway for egress. Mentioning IP-mode target registration is the detail that shows you have built it on EKS specifically.
- On state locking, say what it prevents and how it is implemented: the backend takes an exclusive lock for the duration of a plan or apply so two concurrent runs cannot corrupt state — S3 with a DynamoDB table historically, and now S3 native locking via `use_lockfile`, with `force-unlock` as the break-glass you only use after confirming nothing is running. Then the point that matters: locking prevents concurrent _writes_, not conflicting _intentions_, which is what code review and applying only from CI are for.
- For the EKS module structure, describe the interface rather than listing resources: inputs for cluster name, Kubernetes version, VPC and subnet IDs, node pool or Karpenter configuration, add-on versions, and access entries; outputs for the cluster endpoint, certificate authority data, and the OIDC issuer URL — that last one being essential because every IRSA role depends on it. Internally the module owns the cluster, its IAM roles, security groups, the OIDC provider, and managed add-ons. Say whether you would write it or use the well-maintained community module, and justify the choice; "I would not rebuild a module thousands of people test for me" is a perfectly strong answer when it comes with a reason. See [what Terraform is](../infrastructure-as-code/what-is-terraform.md).
- The estate questions at the end — how many clusters, how many nodes, how CI/CD is organised — are calibration checks. Have exact numbers ready, because a vague answer here retroactively weakens the confident technical answers that preceded it.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
