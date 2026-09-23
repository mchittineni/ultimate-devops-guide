---
title: "What is the difference between mutable and immutable infrastructure in modern deployment patterns?"
id: 586
category: "Configuration Management"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - architecture
  - immutable
  - mutable
  - packer
  - terraform
quiz:
  stem: "How does an immutable infrastructure deployment strategy handle a software update on production servers?"
  options:
    - "By opening an SSH session to run `yum update` on live instances"
    - "By building a new versioned machine image/container, provisioning fresh instances, and terminating the old ones"
    - "By manually editing configuration files in `/etc` on each node"
    - "By pausing all web traffic for 24 hours"
  answer: 2
  explanation: "Immutable infrastructure never modifies instances in-place. Updates involve deploying brand-new instances provisioned from updated golden images and retiring the old instances."
---

# What is the difference between mutable and immutable infrastructure in modern deployment patterns?

**Short answer:** Mutable infrastructure updates running servers in-place over time (e.g. running Ansible playbooks or `apt-get upgrade` on live VMs); Immutable infrastructure never modifies running instances, replacing servers entirely with pre-baked machine images (AMIs) or containers for every release.

## Detail

The shift from 'pets to cattle' defines modern cloud infrastructure:

### Comparison

| Feature             | Mutable Infrastructure ('Pets')                            | Immutable Infrastructure ('Cattle')                                  |
| ------------------- | ---------------------------------------------------------- | -------------------------------------------------------------------- |
| Update Mechanism    | In-place configuration changes (`ssh`, Ansible)            | Destroy and replace with fresh pre-baked image                       |
| Configuration Drift | High: servers slowly diverge over time due to ad-hoc fixes | Zero: running servers are never modified                             |
| Debugging Strategy  | SSH into live server to debug and patch                    | Terminate failing instance and inspect centralized logs              |
| Tooling             | Ansible, Chef, Puppet                                      | Packer (bake images), Terraform, Kubernetes                          |
| Rollback Speed      | Slow (must execute reverse playbook; unpredictable)        | Instant (re-point load balancer or rolling update to previous image) |

With immutable infrastructure, if a server misbehaves, you delete it; an autoscaling group or Kubernetes controller provisions an identical replacement from the golden image.

### Trade-offs

Immutability is not free. Every change, including a one-line config fix or an urgent CVE patch, needs an image build and a rollout, so you need a fast image pipeline and a base-image patch cadence. State has to live elsewhere (managed databases, object storage, external session stores), and debugging relies on centralised logs and metrics because the instance may be gone. Stateful, long-lived systems - databases, legacy appliances, licensed software tied to a host - often stay mutable, managed with configuration management and strict drift detection. Most real estates are a mix.

## Example

```bash
# Mutable: change the running fleet in place
ansible-playbook -i inventories/prod patch.yml --limit web   # hosts drift if a run half-fails

# Immutable: bake a new image, then replace instances
packer build -var "git_sha=$(git rev-parse --short HEAD)" web.pkr.hcl   # new AMI
terraform apply -var "web_ami_id=ami-0new123"                           # new launch template version
aws autoscaling start-instance-refresh --auto-scaling-group-name web   --preferences '{"MinHealthyPercentage": 90}'                          # roll the fleet
# rollback = apply the previous AMI id and refresh again
```

## Interview tips

- Define both by what happens to a running server: modified in place versus never modified, only replaced.
- Tie immutability to drift (structurally eliminated) and rollback (redeploy the previous artefact).
- Say where configuration management goes in an immutable world: into the image build.
- Be honest about the costs - image pipeline, slower small fixes, externalised state - and name what stays mutable.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Configuration Management](./README.md) · [All topics](../README.md)
