---
title: "What release engineering interview questions does Syncortex ask?"
id: 382
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - syncortex
  - configuration-management
  - kubernetes
  - infrastructure-as-code
  - devsecops
  - backup-and-disaster-recovery
---

# What release engineering interview questions does Syncortex ask?

## Questions

**Ansible**

- **What are `block` and `rescue` in Ansible, and what does `release_on` mean in that context?**
- **Which Ansible command or flag lets you view the log while a playbook is executing?**
- **You have two different VMs with different requirements. How do you modify your playbook to handle both?**

**Kubernetes**

- **What are taints and tolerations?**
- **How do you investigate a Pod failure?**
- **What parameters are used for a Horizontal Pod Autoscaler?**
- **How do you take a regular backup of Kubernetes clusters?**

**Supply chain**

- **If you want your developers to use only authorised images, what can you do?**

**Terraform**

- **How would you implement multi-region Terraform code?**
- **How do you make sure an EC2 instance is not deleted when someone runs `terraform destroy`?**

## Example

```text
Syncortex — Release Engineer (5 YOE), reported round
10 questions

  Kubernetes                  4   taints and tolerations, Pod failure triage,
                                  HPA parameters, cluster backup
  Ansible                     3   block/rescue, live log during execution,
                                  one playbook for two different VMs
  Terraform                   2   multi-region code, protect an EC2 instance
                                  from destroy
  Supply chain                1   allow only authorised images

A COMPACT ROUND WITH TWO PRECISE ANSWERS
  "Only authorised images" and "protect an instance from destroy" both have
  named, specific mechanisms. Getting those two exactly right carries a fifth
  of the round.
```

## Interview tips

- The authorised-images question has a definite answer and naming the mechanism matters: **admission control**. Use a policy engine — Kyverno or OPA Gatekeeper — with a validating policy that rejects any Pod whose image does not come from an approved registry prefix, and strengthen it by requiring a digest rather than a mutable tag. Then go one level further, because that is what separates a good answer: policy on the registry name only proves _where_ the image came from, so verify _what_ it is with signature enforcement — Cosign signatures checked by Kyverno's `verifyImages` rule, or Sigstore policy — so an unsigned or tampered image is rejected even from the right registry. Add the supporting controls: a private registry with tag immutability, scanning in CI as a gate, and `imagePullSecrets` restricted so nodes cannot pull from anywhere else. See [enforcing Kubernetes admission control with Kyverno or OPA Gatekeeper](../devsecops/how-do-you-enforce-kubernetes-admission-control-with-kyverno-or-opa-gatekeeper.md) and [signing and verifying container images](../devsecops/how-do-you-sign-and-verify-container-images.md).
- Protecting an instance from `terraform destroy` should be answered in layers, because a single mechanism is a weak answer. In the code: `lifecycle { prevent_destroy = true }`, which makes the destroy **fail loudly** rather than silently skipping — say that explicitly, because people assume it excludes the resource. Outside the code: IAM or a service control policy denying `ec2:TerminateInstances` to the pipeline role, EC2 termination protection (`disable_api_termination`), applying only from CI so nobody runs destroy locally, and requiring approval on any plan that shows deletions. Then mention `terraform state rm` as the deliberate way to hand a resource out of Terraform's management if that is the real intent. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- The Ansible `block` question is transcribed oddly — `release_on` is almost certainly `rescue` or `always`. Answer the real construct: `block` groups tasks so directives such as `when`, `become`, and `tags` apply to all of them, `rescue` runs if any task in the block fails, and `always` runs regardless — giving Ansible try/catch/finally semantics. Say what it is actually for: making a multi-step change safe, so a failed migration or deployment can roll itself back in `rescue` and clean up in `always`. Mentioning that `rescue` marks the play as successful if it handles the failure is the detail that shows real use. See [what Ansible is](../infrastructure-as-code/what-is-ansible.md).
- For viewing logs during execution, the answer is verbosity flags — `-v` through `-vvvv`, where `-vvv` shows the connection and module arguments and `-vvvv` adds connection debugging — plus the `debug` module with `var:` or `msg:` to print state at a chosen point, and `--diff` to see what a task would change. Add two practical extras: `ANSIBLE_LOG_PATH` or `log_path` in `ansible.cfg` writes a persistent log, and long-running tasks need `async` with `poll` so they do not appear hung. Saying that `no_log: true` should mask sensitive tasks even at high verbosity is a good closing detail.
- The two-different-VMs question is really about inventory design, and the strong answer avoids conditionals sprawling through tasks. Group the hosts in inventory and put the differences in `group_vars/`, so the same tasks run with different variables — that is the idiomatic Ansible answer. Then name the alternatives for genuinely different _work_: `when` conditions on host facts such as `ansible_distribution`, separate roles included conditionally, and `--limit` to target one group. Say that variable-driven differences scale and task-level `when` chains do not.
- HPA parameters should be listed concretely: `scaleTargetRef` naming the workload, `minReplicas` and `maxReplicas`, and `metrics` — resource metrics such as CPU or memory with `averageUtilization` or `averageValue`, plus custom, external, and object metric types. Then the newer controls that show currency: the `behavior` block with `scaleUp` and `scaleDown` policies and `stabilizationWindowSeconds` to stop thrashing. Add the prerequisite people forget — utilisation-based scaling requires `resources.requests` to be set, and metrics-server must be running — and that HPA and VPA on the same metric conflict. See [autoscaling workloads and nodes](../kubernetes/how-do-you-autoscale-workloads-and-nodes-in-kubernetes.md).
- Taints and tolerations should be answered as the inverse of node selection: a taint is applied to the **node** and repels Pods that do not tolerate it, with effects `NoSchedule`, `PreferNoSchedule`, and `NoExecute` — where `NoExecute` also evicts already-running Pods that do not tolerate it. A toleration on the Pod lets it be scheduled there but does not _attract_ it, which is the distinction from node affinity. Give the real use cases: reserving GPU or licensed nodes, keeping workloads off control-plane nodes, and the built-in taints the node controller applies on `NotReady` or pressure conditions — with `tolerationSeconds` controlling how long a Pod survives before eviction. See [controlling which node a Pod runs on](../kubernetes/how-do-you-control-which-node-a-pod-runs-on.md).
- Pod-failure investigation should be an ordered method keyed on the phase rather than a list of commands: `kubectl get pod` for phase and restart count, `describe` for events and the container's last state and exit code, `logs --previous` for the crashed instance, then branch — `Pending` means the scheduler cannot place it, `ImagePullBackOff` means registry or pull secret, `CrashLoopBackOff` means it starts and exits, and `Running` but not `Ready` means the readiness probe is failing. Name `kubectl debug` with an ephemeral container for images with no shell, and exit-code triage: 137 is `OOMKilled`, 1 an application error, 0 a `restartPolicy` mismatch. See [troubleshooting a Pod stuck in Pending or CrashLoopBackOff](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-in-pending-or-crashloopbackoff.md).
- Cluster backup should separate the three layers, because naming only one is the common weak answer: etcd snapshots for the whole API state on a self-managed control plane — and nothing you can do on a managed cluster, since the provider owns etcd; workload definitions in Git, which is the real backup for anything declarative; and application data on persistent volumes, captured by Velero with a CSI snapshotter or by the database's own tooling. Say that Velero is the standard answer on managed clusters because it covers namespaced resources _and_ volume data, and that a restore rehearsal is the only proof a backup works. See [disaster recovery](../scalability-and-high-availability/what-is-disaster-recovery.md).
- Multi-region Terraform is a provider-alias question at its core: declare aliased providers per region and pass the right one into each module with `providers = { aws = aws.eu_west_1 }`, since a module inherits only the default provider otherwise. Then the structural points: keep per-region state separate so one region's apply cannot break another, factor region-agnostic infrastructure into modules invoked once per region, use `for_each` over a region map rather than copy-pasting blocks, and remember that some resources are global — IAM, Route 53, CloudFront, and ACM certificates for CloudFront must live in `us-east-1`. That global-resource caveat is the detail that marks experience. See [what are Terraform providers](../infrastructure-as-code/what-are-terraform-providers.md) and [designing for multi-region resilience](../cloud-engineering/how-do-you-design-for-multi-region-resilience.md).
- For a release engineering role specifically, tie the Ansible and Terraform answers back to release safety wherever it fits naturally: `block`/`rescue` gives a change an automatic rollback path, `prevent_destroy` and approval gates stop a release from destroying state, and admission control stops an unapproved artefact reaching production. That framing is what distinguishes a release engineer from a general automation engineer.

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
