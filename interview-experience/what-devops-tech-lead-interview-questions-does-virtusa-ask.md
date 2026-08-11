---
title: "What DevOps tech lead interview questions does Virtusa ask?"
id: 389
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - virtusa
  - kubernetes
  - aws-engineering
  - infrastructure-as-code
  - docker
  - container-orchestration-advanced
  - scripting-and-automation
---

# What DevOps tech lead interview questions does Virtusa ask?

## Questions

**Kubernetes workloads and scheduling**

- **What is the difference between a Deployment, a ReplicaSet, a DaemonSet, and a StatefulSet — and which keywords would you write in each, for example rolling update or canary in a `deployment.yml`?**
- **What is node affinity and what is Pod affinity?**
- **What are taints and tolerations?**
- **You have a minimum and maximum number of Pods running. On a festival day traffic increases and you must add Pods, then reduce them when traffic drops. How do you achieve that?**

**Helm**

- **What does `Chart.yaml` contain?**
- **Which files are present in a Helm chart?**
- **What do you declare in `values.yaml`?**

**Terraform**

- **What is the Terraform command to unlock the state file?**
- **What is a module in Terraform?**
- **Several EC2 instances were created manually through the console and you must now manage them with Terraform. What is the command?**
- **What is the difference between CloudFormation and Terraform?**

**Docker**

- **What is the difference between `ENTRYPOINT` and `CMD`?**
- **What is the difference between the `COPY` and `RUN` commands?**
- **You have an image and want to build it, tag it, and deploy it to Docker Hub. What are the commands?**

**ECS and traffic flow**

- **You have an ECS task definition and a website. When a developer hits the URL, what is the flow of traffic? Fargate is serverless — how do you configure DNS or the website there?**
- **What is a task definition in ECS?**
- **What is the difference between ECS and Fargate?**

**Python**

- **Write a Python program to reverse a string.**
- **What is a list and what is a tuple in Python?**

## Example

```text
Virtusa — Tech Lead, reported round
19 questions

  Kubernetes                  4   four workload types + their keywords,
                                  node vs Pod affinity, taints and tolerations,
                                  festival-day scaling
  Terraform                   4   unlock the state file, modules, import
                                  manually-created instances, TF vs CFN
  Docker                      3   ENTRYPOINT vs CMD, COPY vs RUN,
                                  build/tag/push commands
  ECS and traffic flow        3   task definition, ECS vs Fargate,
                                  URL-to-container flow on Fargate
  Helm                        3   Chart.yaml, chart files, values.yaml
  Python                      2   reverse a string, list vs tuple

A TECH LEAD ROUND THAT STAYS HANDS-ON
  Despite the lead title, there are no team or delivery questions — it is all
  mechanics, and several want exact commands. Expect to be asked "what is the
  command", not "how would you approach it".
```

## Interview tips

- The "ECS versus Fargate" question contains a category error worth correcting politely, and doing so is the strongest answer in the round: **Fargate is not an alternative to ECS — it is a launch type _for_ ECS (and a compute mode for EKS)**. The real comparison is ECS on **EC2** versus ECS on **Fargate**: with EC2 you own the instances, patch them, and pay for the whole instance whether tasks fill it or not, but you get GPUs, privileged containers, DaemonSet-style agents, and cheaper steady-state cost via Reserved Instances or Spot; with Fargate AWS runs the capacity, you pay per task vCPU and memory, and there is no host to manage — at the cost of no privileged mode, no host access, slower task start, and a higher unit price. Say the framing first, then the trade-off. See [ECS versus EKS versus Fargate](../aws-engineering/what-is-the-difference-between-ecs-eks-and-fargate.md).
- The Fargate traffic-flow question follows from that and has a specific chain: Route 53 resolves the hostname to an **Application Load Balancer**, the ALB's listener terminates TLS with an ACM certificate and its rule forwards to a target group; because Fargate tasks have their own ENIs, the target group is of type **`ip`** rather than `instance`, and the ECS service registers and deregisters task IPs with it automatically as tasks come and go; the ALB then forwards to the container port declared in the task definition. Say the two details that prove you have built it: `awsvpc` network mode is mandatory on Fargate, which is _why_ the target group must be IP-based, and the task's security group is what allows the ALB in. Then answer the DNS half plainly — you do not point DNS at a task, because task IPs are ephemeral; you point an alias record at the load balancer, or use ECS Service Connect or Cloud Map for service-to-service discovery.
- The state-unlock question wants the exact command: **`terraform force-unlock <LOCK_ID>`**, with the lock ID printed in the error message. But lead with the safety rule, because that is what a lead is expected to say: confirm no apply is genuinely still running first — breaking a live lock is how state gets corrupted — and check the lock's `Who` and `Created` fields, which usually reveal an interrupted CI job. Then say the durable fix: apply only from CI so a cancelled local run cannot leave an orphan lock. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- For the manually-created EC2 instances, the command is `terraform import aws_instance.example i-0abc123`, one per instance — and the better modern answer is an **`import` block** in configuration with `-generate-config-out`, so the operation appears in a reviewable plan and Terraform scaffolds the HCL. Say the two things that matter: import populates state but does _not_ write your configuration, so you still author the resource block to match reality; and an empty `terraform plan` afterwards is how you prove you got it right. For several instances, use `for_each` over a map of names to instance IDs so each is keyed stably. See [importing existing cloud infrastructure into Terraform](../infrastructure-as-code/how-do-you-import-existing-cloud-infrastructure-into-terraform.md).
- The four-workload-types question explicitly asks which _keywords_ you would write, so answer with the manifest fields rather than prose. Deployment: `replicas`, `strategy.type: RollingUpdate` with `maxSurge` and `maxUnavailable` (and note that canary is **not** a native Deployment field — you achieve it with two Deployments and traffic splitting, or Argo Rollouts, which is worth saying because the question implies otherwise). ReplicaSet: `replicas` and `selector`, but you rarely author one directly because a Deployment manages it and gives you rollback. DaemonSet: no `replicas` at all — one Pod per matching node, with `nodeSelector` and `tolerations` to choose which. StatefulSet: `serviceName` for the headless Service, `volumeClaimTemplates` for per-replica storage, `updateStrategy` with `partition` for staged rollouts, and `podManagementPolicy`. Naming `volumeClaimTemplates` and the absence of `replicas` on a DaemonSet is what shows you have written all four. See [DaemonSets](../container-orchestration-advanced/what-are-daemonsets-in-kubernetes.md) and [StatefulSets](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md).
- Node affinity versus Pod affinity is easy to blur, so separate them by _what they select against_: node affinity matches **node labels**, so it attracts a Pod to a class of machine; Pod affinity and anti-affinity match **other Pods' labels** across a `topologyKey`, so they co-locate or spread replicas relative to each other. Say the two canonical uses — anti-affinity with `topologyKey: topology.kubernetes.io/zone` to keep replicas out of one zone, and affinity to place a cache next to its consumer — and that `requiredDuringScheduling` is a hard constraint while `preferred` is a soft one. Add that topology spread constraints are the modern, cheaper way to spread replicas, because Pod anti-affinity is expensive to evaluate at scale.
- The festival-day scaling question wants both layers named, because Pods alone are not enough: an **HPA** with `minReplicas` and `maxReplicas` scaling on CPU, or better on a request-rate or queue-depth metric via KEDA, plus `behavior.scaleDown.stabilizationWindowSeconds` so it does not thrash as traffic ebbs — and underneath it the **Cluster Autoscaler or Karpenter**, because extra replicas with nowhere to schedule just sit `Pending`. Then the lead-level addition: for a _known_ event you pre-scale ahead of it rather than relying on reactive autoscaling, because autoscaling loses the first few minutes — which is exactly when a festival spike arrives. See [autoscaling workloads and nodes](../kubernetes/how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md).
- `COPY` versus `RUN` is a slightly odd pairing — they are not alternatives — so say that plainly and then define each: `COPY` moves files from the build context into the image, `RUN` executes a command in a new layer during the build. The useful content is how they interact: each creates a layer, and because the cache is a chain, a `COPY` of frequently-changing source code invalidates every `RUN` above it — which is why you copy the dependency manifest and `RUN` the install _before_ copying application source. Then handle `ENTRYPOINT` versus `CMD`: `ENTRYPOINT` is the executable, `CMD` supplies default arguments, and arguments passed to `docker run` replace `CMD` but not `ENTRYPOINT` unless you use `--entrypoint`. See [what a Dockerfile is](../docker/what-is-dockerfile.md).
- The build-tag-push sequence should be given as commands: `docker build -t myapp:1.2.3 .`, `docker tag myapp:1.2.3 <user>/myapp:1.2.3`, `docker login`, `docker push <user>/myapp:1.2.3`. Then add the practice that matters at lead level: tag with an immutable identifier such as the Git SHA rather than `latest`, deploy by digest so what runs is what you tested, and use `docker buildx build --platform` for multi-architecture images — because an `amd64`-only image on Graviton or Apple silicon nodes is a common production surprise.
- CloudFormation versus Terraform should end in a trade-off, not a preference: CloudFormation is AWS-native with no state file to host, native drift detection, and automatic rollback on stack failure, but it is AWS-only and slower to support new services in some cases; Terraform is multi-cloud with a far larger module and provider ecosystem and a more expressive language, at the cost of state you must host, encrypt, lock, and protect. Say which you would pick and why — and that for an AWS-only estate with a small platform team, CloudFormation or CDK removes a real operational burden. See [when to choose CloudFormation, CDK, or Terraform on AWS](../aws-engineering/when-do-you-choose-cloudformation-cdk-or-terraform-on-aws.md).
- The three Helm questions have precise answers, so give the files and their jobs: `Chart.yaml` holds chart metadata — `apiVersion`, `name`, `version` (the chart's own version), `appVersion` (the application's), plus `dependencies`; the chart also contains `values.yaml` for default configuration, `templates/` with the manifests plus `_helpers.tpl` for named templates and `NOTES.txt` for post-install output, `charts/` for subchart dependencies, `Chart.lock`, and `.helmignore`. In `values.yaml` you declare everything that varies per environment — image repository and tag, replica count, resources, ingress hosts and TLS, service type, environment variables, and node placement — with per-environment overrides in separate files passed via `-f`. Say that the discipline is to keep templates generic and push all variability into values, because that is what makes one chart serve every environment. See [what Helm is](../container-orchestration-advanced/what-is-helm.md).
- Taints and tolerations should be framed as the inverse of affinity: the taint sits on the **node** and repels Pods, with effects `NoSchedule`, `PreferNoSchedule`, and `NoExecute` — the last also evicting already-running Pods that do not tolerate it. A toleration merely _permits_ scheduling, it does not attract, which is the distinction from node affinity. Give the real uses: reserving GPU or licensed nodes, keeping workloads off control-plane nodes, and the built-in taints the node controller applies on `NotReady` or pressure — with `tolerationSeconds` controlling how long a Pod survives before eviction.
- List versus tuple in Python is a two-line answer with one consequence worth adding: lists are mutable and tuples immutable, which is why a tuple can be a dictionary key or a set member and a list cannot, and why tuples are slightly faster and safer as fixed records. For reversing a string, give the idiomatic `s[::-1]` and then a loop version, and say which you would ship — interviewers often follow up by banning slicing, so having the manual version ready costs nothing. See [what you use Python for as a DevOps engineer](../scripting-and-automation/what-do-you-use-python-for-as-a-devops-engineer.md).
- One thing to notice about this round: it is titled Tech Lead but contains no questions about people, delivery, estimation, or architecture ownership. That gap is an opportunity — where an answer naturally allows it, add the lead framing: how you would standardise the Helm chart across teams, why you would put Terraform behind a pipeline rather than trusting discipline, or how you would document the ECS traffic path for on-call. It costs a sentence and it is the only signal in the round that you can operate at lead level.

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[What is Continuous Deployment?]] (`#5`): [What is Continuous Deployment?](../core-devops-concepts/what-is-continuous-deployment.md)
- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
