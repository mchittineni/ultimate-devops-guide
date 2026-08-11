---
title: "What DevOps interview questions does ITC Infotech ask?"
id: 339
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - itc-infotech
  - aws-engineering
  - kubernetes
  - infrastructure-as-code
  - cloud-engineering
  - network-security
---

# What DevOps interview questions does ITC Infotech ask?

## Questions

**Hybrid connectivity and storage**

- **How do you connect on-premises infrastructure to AWS — specifically if you need to share files from on-premises?**
- **A script on an EC2 instance generates files daily that need pushing to S3. How do you connect EC2 to S3 for that?**

**EKS and traffic flow**

- **How would you write a Terraform module for EKS?**
- **Your application runs on EKS. When a user hits the URL, how does traffic flow through to it?**
- **What is the difference between CoreDNS and kube-proxy?**

**Identity**

- **What is an OIDC provider in AWS, and what is it for?**

## Example

```text
ITC Infotech — DevOps Engineer (4 YOE), reported round
6 questions

  Hybrid connectivity / storage  2   on-prem file sharing to AWS,
                                     EC2 -> S3 daily upload
  EKS and traffic flow           3   Terraform module for EKS, URL-to-Pod
                                     request path, CoreDNS vs kube-proxy
  Identity                       1   OIDC provider in AWS

SHORT ROUND, NO FILLER
  Six questions and every one is open-ended. There is nowhere to hide behind
  a definition — each answer needs a mechanism and a design decision.
```

## Interview tips

- CoreDNS versus kube-proxy is the sharpest question here because both sit in the request path and are easy to blur. CoreDNS answers _name_ queries — it resolves `service.namespace.svc.cluster.local` to a Service's ClusterIP, and it runs as a Deployment. kube-proxy handles _packets_ — it runs as a DaemonSet on every node, watches Services and EndpointSlices, and programs iptables or IPVS rules so traffic to a ClusterIP is redirected to a real Pod IP. Name resolution versus packet forwarding, Deployment versus DaemonSet: say both contrasts and the answer is complete. See [what a Service is in Kubernetes](../kubernetes/what-is-a-service-in-kubernetes.md) and [main components of Kubernetes architecture](../kubernetes/what-are-the-main-components-of-kubernetes-architecture.md).
- The URL-to-Pod flow follows directly from that, so answer it as one continuous path: DNS resolves the public name to the load balancer, the load balancer forwards to the ingress controller Pods, the controller matches host and path rules and TLS terminates, the request goes to the backend Service, the Service's EndpointSlice selects a Pod, kube-proxy or the CNI dataplane routes it, and finally the container port receives it. Mentioning that an AWS Load Balancer Controller in IP mode targets Pods directly and bypasses the node hop is a strong finishing detail. See [exposing an application in Kubernetes](../kubernetes/how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md).
- The OIDC provider question connects to EKS whether or not the interviewer says so, and that link is what you should draw. An IAM OIDC identity provider lets AWS trust tokens issued by an external issuer, so an identity outside AWS can assume a role without any stored access key. For EKS that is IRSA: the cluster has an OIDC issuer, a Kubernetes service account is annotated with a role ARN, and the Pod's projected token is exchanged for temporary credentials. The same mechanism is how GitHub Actions authenticates to AWS. Say "no long-lived keys" as the reason it exists. See [securing Pod access to AWS resources using EKS Pod Identity or IRSA](../aws-engineering/how-do-you-secure-pod-access-to-aws-resources-using-eks-pod-identity-or-irsa.md).
- On-premises file sharing to AWS has several valid answers and naming the right _shape_ matters more than the product. For an ongoing file share, AWS Storage Gateway in file mode presents an SMB or NFS share locally and stores objects in S3; for a one-off or scheduled bulk copy, DataSync; for very large offline transfers, Snowball. Underneath all of them you need connectivity — Direct Connect for predictable bandwidth or a site-to-site VPN for lower cost — and you should say which you would choose and why. See [connecting an on-premises network to the cloud](../cloud-engineering/how-do-you-connect-an-on-premises-network-to-the-cloud.md).
- The EC2-to-S3 question is really an identity question in disguise, so lead with it: attach an IAM role to the instance through an instance profile, so the SDK or CLI picks up temporary credentials from the instance metadata service and no access key is ever stored on disk. Then the mechanism — a cron job or `systemd` timer running `aws s3 sync`, with a gateway VPC endpoint so the traffic never leaves the VPC, server-side encryption on the bucket, and a lifecycle rule for the uploaded files. Mention IMDSv2 as the hardening detail. See [how AWS IAM evaluates a request](../aws-engineering/how-does-aws-iam-evaluate-a-request.md).
- For the EKS Terraform module, describe the interface rather than reciting resources: inputs for cluster name, Kubernetes version, VPC and subnet IDs, node group definitions with instance types and scaling bounds, and add-on versions; outputs for cluster endpoint, certificate authority data, and OIDC issuer URL. Then name what the module must handle — the cluster IAM role and node role, security groups, the OIDC provider for IRSA, and the `aws-auth` mapping or access entries. Say whether you would write it yourself or use the community `terraform-aws-eks` module, and justify the choice; interviewers respect "I would not rebuild a well-maintained module" when it comes with a reason. See [what Terraform is](../infrastructure-as-code/what-is-terraform.md).
- With only six questions, each answer carries roughly 17% of the round. Do not give short answers here — take each one to a design decision and a trade-off, and expect follow-ups rather than a new topic.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)
- [[What is the difference between SRE, DevOps, and Platform Engineering?]] (`#232`): [What is the difference between SRE, DevOps, and Platform Engineering?](../site-reliability-engineering/what-is-the-difference-between-sre-devops-and-platform-engineering.md)
- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
