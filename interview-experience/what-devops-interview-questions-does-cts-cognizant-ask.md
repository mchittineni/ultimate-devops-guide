---
title: "What DevOps interview questions does CTS Cognizant ask?"
id: 322
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - cts-cognizant
  - azure-engineering
  - infrastructure-as-code
  - kubernetes
  - aws-engineering
  - network-security
  - docker
  - configuration-management
  - cicd
---

# What DevOps interview questions does CTS Cognizant ask?

## Questions

### Round 1 — Azure and troubleshooting

- **What is connection draining, and what problem does it solve during a deployment or scale-in?**
- **Your `backend.tf` is visible in the repository but the state is not appearing in the storage account. What could be wrong?**
- **How do you log into a VM that only has a private IP address?**
- **A web application was working and is now down. Networking is confirmed fine and the relevant ports are open. How do you troubleshoot?**
- **What types of load balancer are available?**
- **What is Azure Application Gateway, and how does it handle and encrypt HTTP and HTTPS traffic?**
- **The application is down and returning a 503. What steps do you take?**
  The candidate also recorded their own proposed answer to the web-application question, which is a useful checklist in its own right: verify the nginx or Apache service is running; check whether firewall or security-group rules are blocking traffic; note that ping and telnet add nothing once the network is confirmed healthy; clear stale browser cache and cookies; run `nslookup` to confirm DNS resolution; check whether the TLS certificate is valid or corrupt; and check whether the server has run out of memory and can no longer load the application's resources.

### Round 2 — comparisons and design (3-4 YOE)

- **How do you manage the Terraform state file?**
- **How would you design the architecture for a two-tier application?**
- **What is the difference between a subnet and a network ACL?**
- **What is the difference between a NAT gateway and an internet gateway?**
- **How do you make Jenkins pipeline B run automatically once pipeline A has finished?**
- **How do you tell whether a network policy is actually in effect in a Kubernetes cluster?**
- **What is the difference between a ClusterRole and a ClusterRoleBinding?**
- **What happens when a resource managed by infrastructure as code is changed manually, and how do you prevent it?**
- **What is the difference between a DaemonSet and a StatefulSet?**
- **How do you set up networking within a VPC?**
- **How do you route traffic to and from an instance that sits in a private subnet?**

### Round 3 — portfolio and hands-on

- **What are your day-to-day responsibilities?**
- **How did you reduce the size of your Docker images?**
- **Explain the CI/CD pipeline you worked with.**
- **What have you done in Kubernetes?**
- **How did you write Deployment manifests for your microservices, and how did you configure the Services and Ingress?**
- **Did you configure ingress and egress network rules?**
- **What have you done in Terraform, and how did you integrate it into your delivery process?**
- **What is the difference between `terraform destroy` and `terraform refresh`?**
- **How do you stop someone from running `terraform destroy` and tearing down infrastructure?**
- **How did you do cost optimisation in your project?**
- **Write a Python script that separates the items of a list according to whether they start with `a` or `b` — for example `['abc', 'vca', 'abc', 'bca']`.**
- **What have you done in Ansible?**
- **An Ansible playbook has been running for two to three hours. What do you do next?**
- **What is Ansible Tower, and when would you use it over the command line?**

## Example

```text
CTS (Cognizant) — DevOps Engineer, three reported rounds

  ROUND 1 (Azure, troubleshooting)         7 questions
    connection drain, backend.tf missing from storage account,
    private-IP VM login, app down with healthy network, LB types,
    App Gateway TLS, 503 triage

  ROUND 2 (comparisons, 3-4 YOE)           11 questions
    TF state, 2-tier design, subnet vs NACL, NAT GW vs IGW,
    chained Jenkins pipelines, verifying NetworkPolicy, ClusterRole vs
    ClusterRoleBinding, manual drift, DaemonSet vs StatefulSet,
    VPC networking, private-subnet routing

  ROUND 3 (portfolio + hands-on)           14 questions
    day-to-day, image size, pipeline, K8s work, manifests/Services/Ingress,
    ingress+egress rules, Terraform work, destroy vs refresh, blocking
    destroy, cost optimisation, Python list split, Ansible work,
    3-hour playbook, Ansible Tower

CROSS-ROUND THEME
  Terraform state and drift appear in every round in some form. It is the
  single most reliable topic to over-prepare for CTS.
```

```python
# The list question: one pass, grouped by first character.
items = ["abc", "vca", "abc", "bca"]

starts_a = [s for s in items if s.startswith("a")]   # ['abc', 'abc']
starts_b = [s for s in items if s.startswith("b")]   # ['bca']
other    = [s for s in items if not s.startswith(("a", "b"))]  # ['vca']
```

## Interview tips

- The `backend.tf` question is the sharpest in round one and the answer is almost always "`terraform init` was never run against that backend", so the state is still local in `terraform.tfstate`. Other candidates: the configuration is commented out or in a file Terraform is not reading, the container or key path differs from where you are looking, credentials lack write permission on the storage account, or a `-backend=false` init. Say the diagnostic — run `terraform init -reconfigure` and check whether a local state file exists. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- ClusterRole versus ClusterRoleBinding trips people because both are cluster-scoped. The ClusterRole is the set of permissions; the ClusterRoleBinding grants them to a subject. Add the detail that earns the mark: a ClusterRole can also be referenced by a namespaced RoleBinding, which grants those permissions only inside that namespace. See [how RBAC works in Kubernetes](../kubernetes/how-does-rbac-work-in-kubernetes.md).
- Verifying a NetworkPolicy is a two-part answer. First, `kubectl get networkpolicy -A` shows the objects exist — but they do nothing unless the CNI enforces them, and several CNIs do not. Second, prove enforcement empirically: exec into a Pod and try to reach a blocked Service, expecting a timeout rather than a refusal. Naming the CNI dependency is the whole point of the question. See [network segmentation](../network-security/what-is-network-segmentation.md).
- DaemonSet versus StatefulSet is an odd pairing, so answer on the axis that distinguishes them: a DaemonSet places one Pod per node for node-local agents; a StatefulSet gives ordered, stably named Pods each with their own persistent volume, for databases and quorum systems. See [DaemonSets](../container-orchestration-advanced/what-are-daemonsets-in-kubernetes.md) and [StatefulSets](../container-orchestration-advanced/what-are-statefulsets-in-kubernetes.md).
- `destroy` versus `refresh` needs one sentence each and a warning: `destroy` deletes real infrastructure, while `refresh` only reconciles state with reality and changes nothing in the cloud. Add that `terraform refresh` is deprecated in favour of `terraform plan -refresh-only`, which shows drift without silently rewriting state.
- Blocking `destroy` has layers, and listing several beats naming one: `prevent_destroy` in a `lifecycle` block, IAM or RBAC denying delete actions, running Terraform only from CI with a protected pipeline so nobody applies locally, requiring approval on plans that show deletions, and enabling resource locks or deletion protection on critical resources. See [scanning infrastructure as code before it is applied](../devsecops/how-do-you-scan-infrastructure-as-code-before-it-is-applied.md).
- The 503 and the "app down but network is fine" questions are the same question twice — no healthy backend. Structure it as: are the targets registered, are health checks passing, is the application process actually listening, is it out of memory or threads, has the certificate expired. The candidate's own note in round one lists memory exhaustion last, but it is one of the most common real causes, so raise it earlier. See [what happens when a user opens your application in a browser](../network-security/what-happens-when-a-user-opens-your-application-in-a-browser.md).
- Reaching a private-IP VM on Azure means Azure Bastion, a jump box, a VPN or ExpressRoute, or Just-In-Time access — the same shape as Session Manager on AWS. Name Bastion first since round one is Azure-flavoured. See [connecting an on-premises network to the cloud](../cloud-engineering/how-do-you-connect-an-on-premises-network-to-the-cloud.md).
- For the three-hour playbook, describe triage rather than cancellation: re-run with `-vvv` to see the hanging task, check whether it is waiting on an interactive prompt or an unreachable host, look for a missing `async`/`poll` on a long operation, confirm `gather_facts` is not stalling on a slow host, and check SSH timeouts and the fork count. Then say what you would change — make the task idempotent, add timeouts, and use `--limit` to test. See [what Ansible is](../infrastructure-as-code/what-is-ansible.md).
- Chaining Jenkins pipelines is answered with a `build job:` step at the end of A (with `wait: false` if you do not want to block), or the Parameterized Trigger plugin, and the better modern answer is an event or webhook so the coupling is explicit. See [Jenkins pipelines](../cicd/what-are-jenkins-pipelines.md).
- Connection draining — deregistration delay on AWS, drain on Azure — lets in-flight requests finish before a target is removed. Tie it to Kubernetes: `preStop` hooks and `terminationGracePeriodSeconds` do the same job for Pods. That cross-mapping is a strong finish. See [deployment strategies](../devops-tools-and-automation/what-are-deployment-strategies.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you use Jenkins shared libraries?]] (`#268`): [How do you use Jenkins shared libraries?](../cicd/how-do-you-use-jenkins-shared-libraries.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
