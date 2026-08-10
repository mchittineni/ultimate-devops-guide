---
title: "What DevOps interview questions does Accenture ask?"
id: 307
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - accenture
  - aws-engineering
  - kubernetes
  - infrastructure-as-code
  - network-security
  - cloud-engineering
  - devsecops
---

# What DevOps interview questions does Accenture ask?

## Questions

**IAM, access, and multi-account**

- **You have created an IAM user and configured role-based access inside EKS. How do you bind that IAM identity to the Kubernetes RBAC role so the cluster recognises it?**
- **With ten AWS accounts and a policy that forbids long-lived access keys, how do you give engineers secure sign-in to all of them?**
- **What are all the ways to authenticate into an AWS account, and when is each appropriate?**
- **How do you set up RBAC in Amazon EKS — which objects do you create, and how do they map to cluster permissions?**
- **If application secrets live in AWS Secrets Manager, how does a workload running in EKS read them without embedding credentials in the Pod?**

**Terraform**

- **What exactly happens when you run `terraform init`?**
- **Write Terraform that provisions an EC2 instance in more than one region.**
- **If your Terraform configuration declares three regions and you then create a single EC2 instance without specifying one, which region does it actually deploy into, and why?**

**Networking and services**

- **If the frontend, backend, and database all sit in private subnets, how does an external user reach the application?**
- **Does Amazon S3 sit inside a VPC? Explain how a VPC-bound workload reaches S3 if it does not.**

## Example

```text
Accenture — DevOps Engineer (6 YOE), reported round
10 questions

  Identity and access         5   IAM-to-EKS binding, 10-account login, login
                                  methods, EKS RBAC, Secrets Manager from EKS
  Terraform                   3   init internals, multi-region resource,
                                  which-provider-wins
  Networking / services       2   all-private-subnet ingress, S3 and VPC

WHAT THIS ROUND IS REALLY TESTING
  Half the questions are one idea: an identity in one system being
  trusted by another. IAM user -> Kubernetes RBAC. Engineer -> 10 accounts.
  Pod -> Secrets Manager. Prepare that mapping once and five answers fall out.
```

## Interview tips

- The IAM-to-EKS binding question is the one that separates candidates. Name the mechanism explicitly — the `aws-auth` ConfigMap historically, EKS access entries on current clusters — and then say the IAM principal maps to a Kubernetes user or group, which a RoleBinding or ClusterRoleBinding then grants permissions to. See [how RBAC works in Kubernetes](../kubernetes/how-does-rbac-work-in-kubernetes.md).
- For ten accounts without access keys, the expected answer is federated short-lived credentials: IAM Identity Center or an external IdP, permission sets, and role assumption from a management account. See [structuring a multi-account AWS organisation](../aws-engineering/how-do-you-structure-a-multi-account-aws-organisation.md) and [least-privilege identity](../cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md).
- Secrets Manager from EKS should reach IRSA or EKS Pod Identity within two sentences — a service account annotated with an IAM role, credentials vended by the OIDC provider, no static keys. See [securing Pod access to AWS resources](../aws-engineering/how-do-you-secure-pod-access-to-aws-resources-using-eks-pod-identity-or-irsa.md).
- The three-region trap tests whether you know that a resource uses the default provider unless you pass an aliased one. Say `provider = aws.region2` and explain provider aliases. See [Terraform providers](../infrastructure-as-code/what-are-terraform-providers.md).
- `terraform init` is not "it initialises Terraform". Say: reads configuration, downloads provider plugins to `.terraform/`, initialises the backend and pulls remote state, installs modules, and writes the dependency lock file. See [managing Terraform state safely](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- All-tiers-private is answered with a public-facing load balancer or ingress in public subnets, targets in private ones, and NAT only for egress. Draw the traffic path rather than listing services. See [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md).
- S3 is a regional service outside your VPC, reached over the public endpoint via NAT or an internet gateway, or privately through a gateway VPC endpoint. The interviewer is fishing for the endpoint. See [core AWS services](../aws-engineering/what-are-the-core-aws-services-a-devops-engineer-uses-daily.md).

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
