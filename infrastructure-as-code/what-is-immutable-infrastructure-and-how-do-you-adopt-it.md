---
title: "What is immutable infrastructure and how do you adopt it?"
id: 421
category: "Infrastructure as Code"
difficulty: "Intermediate"
tags:
  - devops
  - infrastructure-as-code
  - interview-questions
  - configuration-management
  - devops-tools-and-automation
  - cloud-engineering
---

# What is immutable infrastructure and how do you adopt it?

**Short answer:** Immutable infrastructure means you never modify a running server - to change anything, you **build a new versioned artefact, deploy it alongside, shift traffic, and destroy the old one**. No in-place patching, no SSH to fix a config, no configuration-management run against live hosts. The pay-off is that every environment is reproducible from a known artefact, rollback is redeploying the previous version, and configuration drift becomes structurally impossible rather than something you detect and remediate. The costs are real too: image build pipelines, longer change cycles for trivial fixes, an explicit answer for state and data, and the operational discipline to stop treating SSH as a repair tool. Containers made this the default; the same pattern with Packer-built machine images predates them and still applies to VMs.

## Detail

### Mutable versus immutable, in practice

| Aspect           | Mutable (traditional)                             | Immutable                                                       |
| ---------------- | ------------------------------------------------- | --------------------------------------------------------------- |
| Change a package | `apt upgrade` on 200 live hosts                   | Rebuild the image, roll out new instances                       |
| Configuration    | Ansible/Puppet converges live servers, repeatedly | Baked in at build time, or injected at boot from a config store |
| Drift            | Inevitable; detected and remediated               | Structurally impossible - nothing changes after boot            |
| Rollback         | Reverse the change and hope                       | Redeploy the previous image version                             |
| Debugging        | Log in and inspect the accumulated state          | Reproduce from the image; the running host is disposable        |
| Failure recovery | Repair the host                                   | Replace the host                                                |
| Boot time cost   | Fast (nothing to build)                           | Slower change cycle, faster and more reliable boots             |

The phrase that captures it: **treat servers as cattle, not pets** - and the sharper test, _snowflake versus phoenix_: could you delete any host at random and have an identical replacement in minutes, with no human step?

### How you actually build it

1. **Bake the artefact in CI.** Packer for AMIs and Azure/GCP images, `docker build` for containers. The build installs packages, applies hardening, adds the agent stack, and pins versions. Tag the artefact with the Git SHA and treat it as immutable and versioned.
2. **Keep the artefact environment-agnostic.** Environment-specific values arrive at boot - user data, instance metadata, a parameter store, or Kubernetes ConfigMaps/Secrets - so the same image runs in staging and production. This is exactly the "build once, promote the artefact" rule from delivery, applied to infrastructure. See [how do you promote a release across dev, staging, and production](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md).
3. **Provision declaratively.** Terraform or CloudFormation references the image ID; changing that ID is the deployment. An Auto Scaling group with instance refresh, or a new launch template version, rolls the fleet. See [what is Terraform](./what-is-terraform.md).
4. **Roll out progressively.** Blue/green node groups, rolling instance refresh, or canary at the load balancer - so a bad image affects a fraction of traffic and rollback is repointing at the previous version. See [what is blue/green deployment](../advanced-devops-cloud/what-is-blue-green-deployment.md).
5. **Solve state explicitly.** This is the part that decides whether adoption succeeds: databases move to managed services or dedicated stateful clusters; user uploads to object storage; sessions to Redis; logs and metrics shipped off the host as they are produced, because you will delete the host. Anything that _must_ persist on the host is a design decision to make consciously, not an accident.
6. **Close the loopholes.** Remove interactive SSH (or make it break-glass, audited, and time-limited via SSM Session Manager or its equivalent), so "I'll just fix it on the box" is not available. Drift detection stays useful as an alarm that someone bypassed the process.

### Where configuration management still fits

Immutable infrastructure does not delete Ansible, Chef, or Puppet - it moves them **left**, into the image build, where they are the most convenient way to express "install and configure this". What goes away is _continuous convergence against live production hosts_. Some things also remain genuinely mutable: DNS records, secrets rotation, feature flags, database contents, and cloud resources with in-place update semantics. Claiming everything is immutable is a red flag; knowing where the boundary sits is the mark of experience. See [what is configuration management](../configuration-management/what-is-configuration-management.md) and [how do you run Ansible at scale across thousands of hosts](../configuration-management/how-do-you-run-ansible-at-scale-across-thousands-of-hosts.md).

### The honest trade-offs

- **Slower for small changes.** A one-line config fix becomes an image build and a fleet roll. Mitigate with fast pipelines, layered builds (a thin application layer on a stable base image), and configuration that is injected rather than baked where it legitimately changes often.
- **Image sprawl and cost.** Versioned images accumulate; you need lifecycle policies and a promotion path, plus a story for base-image CVE patching (rebuild everything on a cadence, which is a benefit disguised as a chore).
- **Debugging changes shape.** You cannot inspect the host afterwards if it is gone, so observability must be external by default: centralised logs, metrics, and traces, plus the ability to launch a copy of the exact image for reproduction.
- **Boot time becomes a reliability property.** Slow-booting images make autoscaling and rollout slow, which is why prebaked images beat long user-data scripts. See [why did your autoscaling not kick in during a traffic spike](../scalability-and-high-availability/why-did-your-autoscaling-not-kick-in-during-a-traffic-spike.md).

## Example

```hcl
# Packer: the artefact is built once in CI, versioned, and scanned
source "amazon-ebs" "base" {
  ami_name      = "app-base-${var.git_sha}"          # versioned, immutable
  instance_type = "t3.medium"
  source_ami_filter { filters = { name = "al2023-ami-*-x86_64" }, most_recent = true, owners = ["amazon"] }
}

build {
  sources = ["source.amazon-ebs.base"]
  provisioner "ansible" { playbook_file = "./provision.yml" }   # config mgmt at BUILD time
  provisioner "shell"   { inline = ["sudo /usr/local/bin/harden.sh"] }
  post-processor "manifest" { output = "manifest.json" }        # record the AMI id for Terraform
}
```

```hcl
# Terraform: changing the AMI id IS the deployment - instances are replaced, never patched
resource "aws_launch_template" "api" {
  name_prefix   = "api-"
  image_id      = var.app_ami_id            # produced by the Packer build above
  instance_type = "t3.large"
  user_data = base64encode(templatefile("bootstrap.sh.tftpl", {
    environment = var.environment           # the ONLY thing that differs per environment
  }))
}

resource "aws_autoscaling_group" "api" {
  min_size = 6
  max_size = 60
  launch_template { id = aws_launch_template.api.id, version = "$Latest" }

  instance_refresh {                        # rolling replacement, not in-place change
    strategy = "Rolling"
    preferences { min_healthy_percentage = 90, instance_warmup = 120 }
  }
  lifecycle { create_before_destroy = true }
}
```

```text
The two workflows, side by side

  MUTABLE                              IMMUTABLE
  openssl CVE published                openssl CVE published
    -> ansible-playbook -l prod          -> rebuild base image in CI (10 min)
    -> 3 hosts fail mid-run              -> scan, promote, update AMI id in Terraform
    -> re-run, 1 host still on old ver   -> instance refresh: 90% healthy maintained
    -> "which hosts are patched?"        -> every instance provably identical
    -> drift report, manual remediation  -> rollback = previous AMI id, one commit revert
```

## Interview tips

- Define it by the rule, not the tooling: never change a running server; replace it. Then give the consequence that matters - reproducibility and rollback.
- Say "cattle not pets", but immediately follow with the sharper test: can you delete any host at random and get an identical replacement with no human step?
- Name the artefact pipeline concretely - Packer for machine images, `docker build` for containers, versioned by Git SHA, deployed by changing an image ID in Terraform.
- Be clear that configuration management moves into the **build**, and that continuous convergence against live hosts is what disappears. Candidates who say "immutable means we deleted Ansible" have missed it.
- The state question is where interviews go next: databases to managed services, uploads to object storage, sessions to Redis, logs shipped off-host. Volunteer it before you are asked.
- Give the honest costs - slower small changes, image sprawl and lifecycle policies, debugging without the host - and how you mitigate each.
- Mention removing interactive SSH (or making it audited break-glass) as the change that makes it real. Process alone does not survive an incident at 3 a.m.
- Connect it to drift: immutability makes drift structurally impossible, whereas mutable infrastructure can only detect and remediate it. See [what is infrastructure drift](../advanced-devops-cloud/what-is-infrastructure-drift.md) and [what is infrastructure as code](./what-is-infrastructure-as-code.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[How do you structure an Ansible role and share it through Galaxy?]] (`#468`): [How do you structure an Ansible role and share it through Galaxy?](../configuration-management/how-do-you-structure-an-ansible-role-and-share-it-through-galaxy.md)
- [[How do you manage Ansible inventories and variables across environments?]] (`#469`): [How do you manage Ansible inventories and variables across environments?](../configuration-management/how-do-you-manage-ansible-inventories-and-variables-across-environments.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
