---
title: "What is Packer and how does it automate immutable golden machine image generation across clouds?"
id: 632
category: "DevOps Tools and Automation"
difficulty: "Beginner"
tags:
  - devops
  - devops-tools-and-automation
  - interview-questions
  - packer
  - iac
  - golden-images
  - ami
  - automation
quiz:
  stem: "Why do autoscaling production fleets use Packer golden machine images instead of running configuration scripts during EC2 user-data startup?"
  options:
    - "Packer images cost 50% less per hour to run"
    - "Pre-baking software into golden images allows new autoscaling instances to boot in seconds without depending on external package repositories or slow setup scripts"
    - "Cloud providers prohibit the use of EC2 user-data scripts"
    - "Packer converts virtual machines into container clusters"
  answer: 2
  explanation: "If autoscaling nodes download and configure software on every boot, scaling takes 15-30 minutes and fails if upstream package mirrors are offline. Golden images boot ready to serve traffic in seconds."
---

# What is Packer and how does it automate immutable golden machine image generation across clouds?

**Short answer:** Packer is an open-source tool that automates building identical golden machine images (AMIs, Azure VHDs, GCP Compute Images, Docker) from a single HCL template using automated builders and provisioners.

## Detail

Provisioning VMs with long bash or Ansible scripts at boot (EC2 user data, cloud-init) makes autoscaling slow and fragile: every new instance repeats the same installation, depends on package mirrors being up, and can end up subtly different from its neighbours.

### The golden image approach

Bake the OS hardening, runtime, agents (monitoring, EDR, log shippers), and application dependencies into an image **in CI**, test it, and publish it. At scale-out time the instance only has to boot and read its per-environment configuration, which typically takes well under a minute. Instances become **immutable**: to change them you build a new image and roll the fleet, rather than patching servers in place. The image is also a security artefact - scan it, sign it, and record what went into it.

### How Packer works

1. **Plugins** provide builders for each platform (Amazon EBS, Azure ARM, Google Compute, VMware vSphere, QEMU, Docker). Since Packer 1.10, plugins are no longer bundled: templates declare them in `required_plugins` and `packer init` installs them.
2. A **source** block describes the temporary build machine; a **build** block lists the sources and the **provisioners** (shell, Ansible, PowerShell, file) that configure it, followed by optional **post-processors** (manifest, checksum, and so on).
3. `packer build` launches the temporary VM, connects over SSH or WinRM, runs the provisioners, snapshots it into an image (an AMI, a managed image, a GCE image), and destroys the temporary resources. One template with several sources builds equivalent images for several clouds in parallel.

### Trade-offs

- **Image sprawl and freshness**: an image goes stale the day it is built, so rebuild on a schedule (for OS patches) and deregister old images - or they accumulate cost and risk. HCP Packer, or simply tagging with the Git SHA and build date, tracks which images are in use.
- **Secrets never belong in the image**: fetch them at boot from a secrets manager.
- **Build time moves, it does not disappear**: a 20-minute image build in CI replaces 20 minutes on every instance boot.
- **Licensing**: Packer, like other HashiCorp products, has been under the Business Source License since 2023. For containers, Dockerfiles/BuildKit fill this role; for managed pipelines, EC2 Image Builder and Azure VM Image Builder are cloud-native alternatives.

## Example

```hcl
# golden-node.pkr.hcl
packer {
  required_plugins {
    amazon  = { source = "github.com/hashicorp/amazon", version = "~> 1.3" }
    ansible = { source = "github.com/hashicorp/ansible", version = "~> 1.1" }
  }
}

locals {
  timestamp = regex_replace(timestamp(), "[- TZ:]", "")
}

source "amazon-ebs" "ubuntu" {
  ami_name      = "golden-node-${local.timestamp}"
  instance_type = "t3.medium"
  region        = "eu-west-1"
  ssh_username  = "ubuntu"

  source_ami_filter { # always start from the latest official Ubuntu 24.04 image
    filters = {
      name                = "ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"
      virtualization-type = "hvm"
    }
    owners      = ["099720109477"] # Canonical
    most_recent = true
  }

  tags = { Role = "golden-node", GitSha = "${env("GIT_SHA")}" }
}

build {
  sources = ["source.amazon-ebs.ubuntu"]

  provisioner "ansible" {
    playbook_file = "./playbooks/harden_os.yml"
  }

  provisioner "shell" {
    inline = ["sudo apt-get clean", "sudo rm -rf /tmp/*", "sudo cloud-init clean"]
  }

  post-processor "manifest" { output = "packer-manifest.json" } # AMI ID for the next pipeline stage
}
```

```bash
packer init .
packer validate .
packer build golden-node.pkr.hcl
```

## Interview tips

- Explain why baking beats boot-time configuration: faster, more reliable scale-out and identical instances.
- Walk the build: plugin, source, temporary VM, provisioners, snapshot, clean-up.
- Show current syntax: `required_plugins` plus `packer init`, and `source_ami_filter` instead of a hard-coded AMI ID.
- Name the operational costs: rebuilding for patches, deregistering old images, and keeping secrets out of images.
- Mention the BSL licence and cloud-native alternatives (EC2 Image Builder, Azure VM Image Builder) to show breadth.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[What is Semantic Release and how does it automate versioning and changelogs from commits?]] (`#540`): [What is Semantic Release and how does it automate versioning and changelogs from commits?](../cicd/what-is-semantic-release-and-how-does-it-automate-versioning-and-changelogs-from-commits.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Tools and Automation](./README.md) · [All topics](../README.md)
