---
title: "What DevOps interview questions does Sapient ask?"
id: 377
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - sapient
  - aws-engineering
  - infrastructure-as-code
  - kubernetes
  - network-security
  - cloud-engineering
---

# What DevOps interview questions does Sapient ask?

## Questions

**AWS breadth and DNS**

- **Which AWS services have you used?**
- **In Route 53, what is the difference between an A record and a CNAME record?**
- **What is DNS used for in your project?**
- **What was your domain name, and how do you establish the connection between the domain name and the service? Have you created DNS records yourself?**

**VPC and network architecture**

- **Describe your VPC structure and the networking architecture in your project, and how many subnets do you have?**
- **Which subnet is your EKS cluster in, and which networking components did you use?**
- **Why are you keeping your web application in a public subnet?**
- **Where does the load balancer sit?**

**Storage**

- **How many storage services does AWS have?**
- **You hold sensitive data on EBS. How do you secure it?**
- **What are EBS and EFS in a Kubernetes context?**

**Terraform**

- **What is an iteration limit in Terraform?**
- **What is a `data` block?**
- **What are modules in Terraform, and how do you call them?**
- **Have you worked with `null_resource`?**
- **Explain the Terraform state file, and in which configuration file do you define where the state is generated and maintained?**

**Kubernetes access and workload identity**

- **How do you manage your cluster — with `kubectl` commands or something else?**
- **If your cluster is in a private subnet, `kubectl` from outside will not work. How do you access it?**
- **You have an S3 bucket with a file in it and a Pod that needs to read it. How does the Pod get access?**

## Example

```text
Sapient — DevOps Engineer (6 YOE), reported round
19 questions

  Terraform                   6   iteration limit, data block, modules and
                                  how you call them, null_resource, state
                                  file + which file declares the backend
  VPC / network architecture  4   your VPC structure, EKS subnet placement,
                                  "why is the web app public?", LB placement
  AWS breadth and DNS         4   services used, A vs CNAME, DNS purpose,
                                  domain-to-service wiring
  Storage                     3   how many storage services, securing EBS
                                  data, EBS vs EFS in Kubernetes
  K8s access / identity       2   private-subnet cluster access, Pod to S3

THE QUESTION THAT IS A TRAP
  "Why are you keeping your web application in a public subnet?" is a
  challenge, not a request for information. The expected answer is that you
  should not be — only the load balancer belongs there.
```

## Interview tips

- The public-subnet question is a deliberate challenge and the strong move is to correct the premise rather than defend it. Only internet-facing components belong in a public subnet — the load balancer, a NAT gateway, and possibly a bastion. The web application tier belongs in private subnets, receiving traffic only from the load balancer's security group, with the NAT gateway providing outbound access for patching. If your project really did put the application in a public subnet, say so honestly and name what you would change and why. Interviewers ask this to see whether you will hold an incorrect position under pressure. This also answers the load balancer question in the same breath. See [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md).
- The EKS subnet question has a specific structure worth giving precisely: control-plane ENIs and worker nodes in **private** subnets across at least two availability zones, public subnets only for the internet-facing load balancers, and the subnets tagged so the AWS Load Balancer Controller can discover them — `kubernetes.io/role/elb` on public subnets and `kubernetes.io/role/internal-elb` on private ones. Naming those tags is the detail that proves you built a cluster rather than read about one. Add the VPC CNI's IP-per-Pod behaviour as the reason subnet sizing matters, and secondary CIDRs or prefix delegation as the fix when addresses run short.
- The Pod-to-S3 question is the most important in the round and there is exactly one right answer: **IRSA or EKS Pod Identity**, not an access key. A Kubernetes service account is associated with an IAM role — annotated with the role ARN for IRSA, backed by the cluster's OIDC provider — and the Pod's projected token is exchanged for temporary credentials, so the SDK picks them up with nothing stored. Add the bucket-side half: the IAM policy grants `s3:GetObject` on the specific prefix, and if the object is encrypted with a customer-managed KMS key the role also needs `kms:Decrypt` — which is the most common reason this "should work" and does not. Mention a gateway VPC endpoint so the traffic never leaves the VPC. See [securing Pod access to AWS resources using EKS Pod Identity or IRSA](../aws-engineering/how-do-you-secure-pod-access-to-aws-resources-using-eks-pod-identity-or-irsa.md).
- The private-cluster access question wants options with a recommendation. If the API endpoint is private, `kubectl` must originate from inside the network: a bastion or jump host in the VPC, Session Manager port forwarding — which needs no open port and logs every session — a VPN or Direct Connect from the office, or a CI runner inside the VPC for automation. Say that the better production posture is a private endpoint plus authorised CIDR ranges rather than a fully public API server, and that GitOps removes most of the need for human `kubectl` access entirely because the controller reconciles from inside. That last point reframes the answer well.
- "In which file do you define where the state file lives?" has a precise answer: the `backend` block inside a `terraform {}` block, conventionally in `backend.tf` or `versions.tf` — and the important constraint is that it cannot use variables or interpolation, which is why partial configuration with `-backend-config` or a `.hcl` backend file is how you vary it per environment. Then cover the state file itself: it maps configuration to real resource IDs and stores attributes, it must live in a remote backend that is encrypted, versioned, and lockable, and it can contain secrets in plain text. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- "Iteration limit" is not standard Terraform terminology, so the confident move is to name the likely readings and answer the useful one. Terraform's iteration constructs are `count`, `for_each`, `for` expressions, and `dynamic` blocks — there is no configurable iteration cap, but `for_each` requires a map or set of strings with keys known at plan time, which is the real constraint people hit. If they mean concurrency, that is `-parallelism`, defaulting to 10. Give the `count`-versus-`for_each` distinction while you are there, since it is the substance behind the question: `count` indexes by position so removing a middle element re-indexes and destroys resources that did not change, while `for_each` keys by a stable string.
- The `data` block and `null_resource` questions have short, opinionated answers. A `data` source _reads_ something Terraform does not own — an existing VPC, the latest AMI, a secret — and never creates or modifies it, which is the ownership distinction against `resource`. `null_resource` is a placeholder for attaching provisioners or `triggers`, and the answer worth giving is that it is superseded by `terraform_data`, and that needing it usually means the work belongs in `user_data`, a baked image, or a configuration-management tool instead.
- Modules should be answered with the interface, not the definition: inputs as variables, outputs for consumption, called with a `module` block naming a `source` — a registry address, a Git URL, or a local path — and a pinned `version` for registry and Git sources. Say that you pass a module's output into another module's input by reference (`module.vpc.private_subnet_ids`), which is also how Terraform infers the dependency order. Add that a module taking thirty variables is not really an abstraction. See [what Terraform is](../infrastructure-as-code/what-is-terraform.md).
- A versus CNAME needs the two operational rules, not just the definitions: an A record maps a name to an IPv4 address (AAAA for IPv6), a CNAME aliases one name to another name — and a CNAME cannot coexist with other records at the same name, nor sit at a zone apex, which is precisely why Route 53 offers **alias** records. Alias records point at AWS resources such as an ALB, CloudFront distribution, or S3 website, work at the apex, and are not charged for queries. Naming alias records is the Route 53-specific answer the question is fishing for, and it also answers how you wire a domain to a service. See [managing DNS and global traffic routing](../cloud-engineering/how-do-you-manage-dns-and-global-traffic-routing.md).
- The storage question is better answered by taxonomy than by a count: object storage (S3, Glacier), block storage (EBS, instance store), file storage (EFS, FSx), plus backup and transfer services (Backup, Storage Gateway, DataSync, Snow family). Giving the three categories and then examples is far stronger than attempting an exact number.
- Securing sensitive data on EBS should list layered controls: encryption at rest with a customer-managed KMS key — enabled by default account-wide if you set it — encryption in transit for anything crossing the network, snapshots inherit encryption and their sharing must be controlled, IAM restricting who can attach or snapshot the volume, deletion protection and lifecycle policies for snapshots, and no public snapshot sharing. Add that the filesystem should be encrypted-at-rest _and_ the data encrypted at the application layer if the sensitivity warrants defence in depth.
- EBS versus EFS in Kubernetes is really an access-modes question: EBS is block storage attached to one node at a time, so it supports `ReadWriteOnce` and is provisioned per Pod by the EBS CSI driver — which is why a StatefulSet replica keeps its own volume, and why a Pod can be stuck `Pending` if rescheduled to a different zone. EFS is a network filesystem supporting `ReadWriteMany`, so many Pods across zones can mount it simultaneously, at higher latency and cost. Say the rule: EBS for per-replica databases, EFS when several Pods must write the same data. See [StatefulSets](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md).

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
