---
title: "What DevOps interview questions does Nitor Infotech ask?"
id: 357
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - nitor-infotech
  - cicd
  - kubernetes
  - aws-engineering
  - infrastructure-as-code
  - devops-tools-and-automation
  - scripting-and-automation
  - network-security
---

# What DevOps interview questions does Nitor Infotech ask?

## Questions

**CI/CD and Jenkins**

- **What is the CI/CD setup in your current project, and what does the flow look like?**
- **Tell me about the GitOps approach, Argo CD, and Flux.**
- **What are shared libraries in Jenkins?**
- **How is caching implemented in Jenkins in your project?**
- **Which Jenkins version are you on?**
- **How have you implemented parallelism in your pipelines?**
- **How would you reduce a pipeline's runtime — including multi-stage builds?**

**Kubernetes**

- **What are StatefulSets, DaemonSets, and Deployments?**
- **How have you implemented networking in Kubernetes?**
- **What are taints, tolerations, and affinity?**
- **How have you implemented RBAC in your EKS setup?**
- **Create a Deployment named `web-app` using image `nginx:1.25`, with 3 replicas, container port 80, and the label `app=web`.**
- **Write a NodePort Service that exposes that Deployment on port 8080.**

**AWS and IAM**

- **What is an SCP — a service control policy?**
- **What are VPC endpoints, internet gateways, Transit Gateway, and a virtual private gateway?**
- **You need to give a user permission only to start and stop EC2 instances. How do you do that?**
- **A user has a role with a policy granting S3 bucket access but still cannot access the bucket. What could be the reason?**

**Terraform**

- **What does the `terraform refresh` command do?**
- **How do you handle infrastructure code for multiple environments in Terraform?**
- **What is state locking in Terraform?**

**Scripting**

- **Write a script that counts how many processes are running as the user `ubuntu`.**

## Example

```text
Nitor Infotech — DevOps Engineer (6 YOE), reported round
21 questions

  CI/CD and Jenkins           7   current flow, GitOps + Argo CD + Flux,
                                  shared libraries, caching, version,
                                  parallelism, cut runtime
  Kubernetes                  6   workload types, networking, taints +
                                  affinity, EKS RBAC, write a Deployment,
                                  write a NodePort Service
  AWS and IAM                 4   SCP, four gateway types, EC2 start/stop
                                  only, role has policy but still denied
  Terraform                   3   refresh, multi-environment, state locking
  Scripting                   1   count processes for one user

TWO WRITE-IT-NOW QUESTIONS
  The Deployment and the NodePort Service are given with exact values —
  image, replicas, ports, labels. Practise typing both from memory; the
  marks are for the label selector matching, which is where people slip.
```

```yaml
# The two manifests, with the join that matters highlighted.
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels: { app: web } # must match template labels
  template:
    metadata:
      labels: { app: web } # <- the Service selects THIS
    spec:
      containers:
        - name: nginx
          image: nginx:1.25
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: web-app
spec:
  type: NodePort
  selector: { app: web } # <- matches the POD labels, not the Deployment
  ports:
    - port: 8080 # the Service's own port
      targetPort: 80 # the container port
      # nodePort: 30080   # optional; must be in 30000-32767
```

## Interview tips

- The role-has-a-policy-but-still-denied question is the best AWS question here and it has a definite evaluation order. Walk it: an explicit `Deny` anywhere wins, so check the bucket policy and any SCP first; then whether an SCP at the organisation level permits the action at all; then whether a permission boundary caps the role; then whether the _bucket policy_ grants access, since S3 requires the resource policy to allow cross-account principals; then whether the object is encrypted with a KMS key whose key policy does not grant the role `kms:Decrypt` — that last one is the most common real cause and the answer that impresses. Add the practical checks: was the role actually assumed rather than the user's own credentials being used, and did they run the IAM policy simulator or check CloudTrail for the exact `AccessDenied` reason. See [how AWS IAM evaluates a request](../aws-engineering/how-does-aws-iam-evaluate-a-request.md).
- The NodePort question hides a trap worth naming: port 8080 in the manifest is the _Service_ port, while `nodePort` — the port actually opened on every node — must fall in the 30000-32767 range unless the API server's range is reconfigured. So "expose on 8080" means `port: 8080` with `targetPort: 80`, and the node port is separate and auto-assigned. Say that distinction out loud; it separates people who have written Services from people who have read about them. See [what a Service is in Kubernetes](../kubernetes/what-is-a-service-in-kubernetes.md).
- On the two manifests, the point to verbalise is the label chain: the Deployment's `selector.matchLabels` must match its own Pod template labels, and the Service selects the _Pod_ labels directly — it has no relationship to the Deployment object at all. A mismatched selector produces a Service with empty `Endpoints`, which is the single most common cause of "my app is unreachable". See [exposing an application in Kubernetes](../kubernetes/how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md).
- EKS RBAC needs the AWS-to-Kubernetes mapping, not a generic RBAC answer. Say that an IAM principal is mapped to a Kubernetes user or group — historically through the `aws-auth` ConfigMap, and on current clusters through EKS access entries and access policies — and that a RoleBinding or ClusterRoleBinding then grants that group a Role or ClusterRole. Add IRSA or EKS Pod Identity for _workload_ identity, since that is the other half of access control on EKS, and mention `kubectl auth can-i --as` to verify what you granted. See [how RBAC works in Kubernetes](../kubernetes/how-does-rbac-work-in-kubernetes.md) and [securing Pod access to AWS resources](../aws-engineering/how-do-you-secure-pod-access-to-aws-resources-using-eks-pod-identity-or-irsa.md).
- The EC2 start-and-stop-only question wants a scoped policy, and the detail that earns credit is the condition. Grant `ec2:StartInstances`, `ec2:StopInstances`, and `ec2:DescribeInstances` — noting that `Describe*` cannot be resource-scoped, so it applies to `*` — and constrain the start and stop actions with a condition on a resource tag such as `aws:ResourceTag/Environment`, so the user can only cycle the instances they own. Say that without the tag condition you have granted power over every instance in the account. See [least-privilege identity in the cloud](../cloud-engineering/how-do-you-design-least-privilege-identity-in-the-cloud.md).
- The four-gateway question should be answered as a matrix rather than four definitions: an internet gateway gives a VPC bidirectional public internet access; a VPC endpoint reaches AWS services privately, with gateway endpoints (S3 and DynamoDB only, free, route-table based) versus interface endpoints (PrivateLink ENIs, chargeable, most other services); a virtual private gateway terminates a site-to-site VPN or Direct Connect on the VPC side; and Transit Gateway is a regional hub interconnecting many VPCs and on-premises connections with _transitive_ routing that peering cannot provide. The gateway-versus-interface endpoint distinction is the detail most often missed. See [designing a production-ready VPC](../aws-engineering/how-do-you-design-a-production-ready-vpc-on-aws.md).
- An SCP is an organisation-level guardrail that sets the _maximum_ available permissions for accounts in an organisational unit — it never grants anything, it only bounds what IAM in those accounts can grant, and it applies even to the account root user. Say that this is why it is the only control an account administrator cannot work around, which is what makes it the right answer for restricting regions, services, or instance types. See [structuring a multi-account AWS organisation](../aws-engineering/how-do-you-structure-a-multi-account-aws-organisation.md).
- Jenkins caching is a question about ephemeral agents, so answer it that way: a workspace on a persistent agent caches naturally but drifts and causes "works on one agent" bugs, while ephemeral Kubernetes agents start empty every time. The fixes are a mounted persistent volume for `~/.m2` or `~/.npm`, a remote build cache, Docker layer caching pushed to and pulled from a registry with `buildx --cache-to`/`--cache-from`, and `stash`/`unstash` to carry artefacts between stages. Say which you use and what it saved.
- Parallelism in Jenkins is the `parallel` block containing named stages, or `parallel` with a map of closures in scripted syntax, plus `failFast true` when one failure should abort the siblings. Add that parallel stages need either separate workspaces or careful use of `lock`/`lockable resources` to avoid contending on a shared dependency — that caveat is where the real experience shows. See [Jenkins pipelines](../cicd/what-are-jenkins-pipelines.md) and [Jenkins shared libraries](../cicd/how-do-you-use-jenkins-shared-libraries.md).
- Argo CD versus Flux should not be a feature list. Say both are pull-based GitOps controllers that continuously reconcile cluster state against Git and detect drift; Argo CD ships a strong UI, an application-centric model, and ApplicationSets for multi-cluster fan-out, while Flux is a set of composable controllers that integrates more naturally as a Kubernetes-native toolkit with Helm and image automation. Then give the shared advantage over push-based CI: no cluster credentials in the pipeline, and self-healing rather than a one-shot apply. See [GitOps](../devops-tools-and-automation/what-is-gitops.md) and [Argo CD](../devops-tools-and-automation/what-is-argocd.md).
- `terraform refresh` deserves the currency point: it updated the state file to match reality and is **deprecated**, replaced by `terraform plan -refresh-only` and `terraform apply -refresh-only`, which make the state update reviewable rather than a silent local mutation. Then pair it with state locking — the backend takes a lock (DynamoDB, or S3 native locking, or the backend's own) so two concurrent applies cannot corrupt state, with `terraform force-unlock` as the break-glass you only use after confirming no apply is running. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- For multiple environments, give an opinion rather than options: separate directories with separate state per environment, consuming shared versioned modules, so the target is explicit and configuration can legitimately differ. Say that workspaces suit identical infrastructure varying only by variables but make it easy to apply to the wrong environment by accident.
- The process-count script is a one-liner with a subtlety: `ps -u ubuntu --no-headers | wc -l` counts processes for that user, and `pgrep -u ubuntu -c` is cleaner. Mention that `ps aux | grep ubuntu | wc -l` is the wrong answer because it matches the grep itself and any command line containing the string. Naming that pitfall is the point of the question. See [basic Linux commands](../linux-administration/what-are-the-basic-linux-commands-every-devops-engineer-should-know.md).
- "Current Jenkins version" is a genuine check on whether you operate the tool or only consume it. Know your controller's version, whether you are on the LTS line, and when you last upgraded plugins — a candidate who says "we are on a recent LTS and upgrade plugins monthly" sounds like an owner.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you scale CI/CD across many services and teams?]] (`#459`): [How do you scale CI/CD across many services and teams?](../cicd/how-do-you-scale-ci-cd-across-many-services-and-teams.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
