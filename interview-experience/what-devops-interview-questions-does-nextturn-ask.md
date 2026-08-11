---
title: "What DevOps interview questions does Nextturn ask?"
id: 354
category: "Interview Experience"
difficulty: "Advanced"
tags:
  - devops
  - interview-experience
  - interview-questions
  - nextturn
  - kubernetes
  - cicd
  - infrastructure-as-code
  - docker
  - devops-tools-and-automation
  - configuration-management
  - scripting-and-automation
  - azure-engineering
---

# What DevOps interview questions does Nextturn ask?

## Questions

**Kubernetes troubleshooting**

- **Troubleshoot a worker node that has gone down.**
- **Troubleshoot a Pod stuck in `Pending`, `CrashLoopBackOff`, or `ImagePullBackOff`.**
- **You have a 30-node cluster. Twenty-nine nodes are `Ready` and one is `NotReady`. You have already run `kubectl logs`, `kubectl describe`, and the other basic commands. How do you investigate further?**
- **What are the common reasons a node becomes `NotReady`, and how do you identify the root cause?**
- **Describe your approach to troubleshooting worker node problems beyond the basic `kubectl` commands.**

**CI/CD concepts and structure**

- **Explain continuous integration, continuous delivery, and continuous deployment.**
- **What is the difference between continuous delivery and continuous deployment?**
- **Explain an end-to-end CI/CD pipeline.**
- **Explain the pre-build, build, and post-build stages of a pipeline.**
- **In a Jenkins pipeline, at which stage would you publish artefacts or images to Nexus or Artifactory — pre-build, build, or post-build? Why?**
- **Jenkins versus GitHub Actions.**
- **If the Jenkins controller node goes down, how do you troubleshoot and restore it?**
- **In GitOps, what is the difference between push-based and pull-based deployment?**

**Terraform and Ansible**

- **What is the difference between `terraform refresh` and `terraform plan`?**
- **When do you use Terraform and when Ansible, and how do they work together?**
- **In Terraform, how would you create multiple EC2 instances each with a different configuration — different instance types, AMIs, tags, or volumes?**
- **What is your hands-on experience with Ansible? Explain a real project where you used it.**

**Docker and Helm**

- **Explain Docker layer caching. During a build, layers 1 to 10 are cached and you modify layer 5 — what happens to layers 6 to 10? Does Docker reuse the cache or rebuild them, and why?**
- **A Helm upgrade failed. How do you roll it back and troubleshoot it?**

**Azure DevOps**

- **Explain variable groups, environment variables, and secrets in Azure DevOps.**

**Scripting and access**

- **Write a Python script that checks disk usage and sends an alert if it exceeds a threshold.**
- **You can launch an EC2 instance from the console but cannot SSH into it. How would you install the `tree` package?**

## Example

```text
Nextturn — DevOps Engineer, reported round
22 questions

  Kubernetes troubleshooting  5   node down, Pending/CrashLoop/ImagePull,
                                  1-of-30 NotReady beyond kubectl, NotReady
                                  causes, worker-node method
  CI/CD concepts / structure  8   CI vs CD vs CD, end-to-end pipeline,
                                  pre/build/post stages, where to publish
                                  artefacts, Jenkins vs GH Actions,
                                  controller down, GitOps push vs pull
  Terraform and Ansible       4   refresh vs plan, when to use each,
                                  heterogeneous EC2 fleet, real Ansible project
  Docker and Helm             2   layer-cache invalidation, failed upgrade
  Scripting / access          2   disk-usage alert script, install a package
                                  with no SSH
  Azure DevOps                1   variable groups, env vars, secrets

THE NODE QUESTION IS ASKED THREE TIMES
  "Node NotReady" appears as a scenario, as a causes question, and as a
  method question. Prepare one deep, ordered answer and it covers all three
  plus roughly 23% of the round.
```

## Interview tips

- The layer-cache question has an exact answer and it is the cleanest scoring opportunity in the round: layers 6 to 10 are **rebuilt**, not reused. Docker's cache is a chain — each layer's validity depends on the layer beneath it, so changing layer 5 changes its digest, which invalidates every layer above it regardless of whether their own instructions changed. Then give the design consequence: order your Dockerfile so slow, stable steps sit low and volatile steps sit high, which is exactly why you copy the dependency manifest and install dependencies _before_ copying application source. Add that `COPY . .` early in a Dockerfile destroys caching entirely because any file change invalidates it. See [reducing Docker image size and build time](../docker/how-do-you-reduce-docker-image-size-and-build-time.md).
- The "beyond `kubectl`" node question is explicitly asking you to leave the API server behind, so do not repeat `describe`. Say you would get onto the node — SSH or `kubectl debug node/<name>` — and work up the stack: is the kubelet running (`systemctl status kubelet`, `journalctl -u kubelet`), can it reach the API server, is the container runtime healthy (`crictl ps`, `crictl info`), is the disk full or out of inodes so the kubelet reports `DiskPressure`, is it out of memory, is `containerd` wedged, is the CNI plugin failing to allocate IPs, is the node's certificate expired, is the clock skewed, and is the cloud instance itself healthy in the provider console. Then name the conditions the kubelet reports — `MemoryPressure`, `DiskPressure`, `PIDPressure`, `NetworkUnavailable` — and say that `NotReady` with no kubelet logs at all usually means the kubelet is dead or the node is unreachable rather than unhealthy. See [debugging a Linux performance problem from first principles](../linux-administration/how-do-you-debug-a-linux-performance-problem-from-first-principles.md).
- The artefact-publishing question wants a reasoned answer, not just a stage name. Publish in **post-build** — after the build has produced an artefact and after tests have passed — because publishing a broken artefact pollutes the repository that downstream environments trust. Say the principle out loud: build once, verify, then publish an immutable versioned artefact that every environment promotes without rebuilding. Add that pre-build is where you _fetch_ dependencies from the same repository, which is the symmetry the interviewer is probing.
- Push versus pull GitOps is a favourite and has a crisp answer: push means the pipeline holds cluster credentials and runs `kubectl apply` or `helm upgrade` outward into the cluster; pull means an in-cluster controller such as Argo CD or Flux watches Git and reconciles continuously. Then give pull's three advantages — no cluster credentials in CI, continuous drift detection and self-healing rather than a one-shot apply, and the cluster can sit behind a firewall with no inbound access. See [GitOps](../devops-tools-and-automation/what-is-gitops.md) and [Argo CD](../devops-tools-and-automation/what-is-argocd.md).
- `refresh` versus `plan` needs precision because they overlap: `plan` already refreshes state in memory before computing the diff, so it shows you both drift and intended changes without writing anything. The standalone `terraform refresh` command _updated the state file_ to match reality and is now deprecated in favour of `terraform plan -refresh-only` and `terraform apply -refresh-only`, which make the state update explicit and reviewable. Saying "refresh is deprecated, use `-refresh-only`" is the current answer. See [managing Terraform state safely in a team](../infrastructure-as-code/how-do-you-manage-terraform-state-safely-in-a-team.md).
- The heterogeneous EC2 fleet question is a `for_each` question. Define a map where each key is an instance name and each value is an object holding its instance type, AMI, tags, and volume settings, then `for_each` over that map so every instance is addressed by a stable key. Say why not `count`: with `count` you would index by position and removing a middle entry re-indexes and destroys the wrong resources, and a list cannot cleanly express per-instance differences anyway. Show that you would put the map in `locals` or a variable so adding an instance is a data change, not a code change.
- The no-SSH package installation question has a specific intended answer: Systems Manager. Use Run Command or Session Manager through the SSM Agent, which needs no inbound port and no key — just the instance role with `AmazonSSMManagedInstanceCore` and a network path to the SSM endpoints. Alternatives worth naming: put the install in `user_data` so it runs at boot, bake it into the AMI, or use Ansible over SSM as a transport. Say that "cannot SSH" is often the _desired_ state in a hardened environment, not a fault to work around. See [troubleshooting SSH failures](../linux-administration/how-do-you-troubleshoot-ssh-failures-high-cpu-and-disk-space-on-linux-servers.md).
- For the Jenkins-controller-down question, structure it as triage then restore: check whether the process, disk, and memory are the problem — a full disk on `JENKINS_HOME` and JVM heap exhaustion are the two usual causes — read the controller log, and confirm whether it is the controller or the reverse proxy in front of it. Restore from a `JENKINS_HOME` backup including `secrets/` and `credentials.xml`, or rebuild from Configuration as Code plus job definitions in Git. Then say the real answer: a single controller is a single point of failure, so the fix is Configuration as Code, backed-up `JENKINS_HOME`, and ephemeral agents so the controller holds no build state. See [Jenkins pipelines](../cicd/what-are-jenkins-pipelines.md).
- Jenkins versus GitHub Actions should end in a trade-off, not a preference: Jenkins is self-hosted with a vast plugin ecosystem and full control over agents, at the cost of maintaining the controller, plugins, and security patching; GitHub Actions is managed, tightly integrated with pull requests, and uses a reusable-workflow model, at the cost of runner minutes, less control, and self-hosted runners if you need private network access. Say which fits which situation.
- Continuous delivery versus continuous deployment is asked twice, so get it exactly right: both keep every change release-ready and automatically deployed through pre-production, but delivery stops at a _manual approval_ before production while deployment goes all the way with no human gate. The gate is the entire difference. See [continuous delivery versus continuous deployment](../cicd/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md).
- Terraform and Ansible together is best answered as a division of labour rather than a competition: Terraform provisions and owns the lifecycle of infrastructure declaratively with state; Ansible configures what runs on it, and is procedural and stateless. In practice Terraform creates the instances and Ansible configures them — or, better, you bake an image and skip in-place configuration entirely. See [Ansible versus Terraform](../infrastructure-as-code/what-is-the-difference-between-ansible-and-terraform.md).
- The disk-usage script is a small task with room to show judgement: use `shutil.disk_usage()` from the standard library rather than shelling out to `df`, take the threshold and path as arguments or environment variables, exit with a non-zero status so a scheduler notices, and send the alert to a webhook or SNS rather than SMTP. Add that you would prefer this to be a Prometheus alert rule on node-exporter's filesystem metrics, and that a threshold on _projected time to full_ beats a fixed percentage — 90% on a 10 TB volume is not the same as 90% on a 20 GB one. See [what you use Python for as a DevOps engineer](../scripting-and-automation/what-do-you-use-python-for-as-a-devops-engineer.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)
- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
