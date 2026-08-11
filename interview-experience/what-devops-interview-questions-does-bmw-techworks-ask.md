---
title: "What DevOps interview questions does BMW TechWorks ask?"
id: 317
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - bmw-techworks
  - aws-engineering
  - devsecops
  - linux-administration
  - cicd
  - docker
  - cloud-migration
---

# What DevOps interview questions does BMW TechWorks ask?

## Questions

**EC2 security and patching**

- **An EC2 instance has a known vulnerability. How do you identify it and how do you remediate it?**
- **What is your process for patching EC2 instances at scale?**

**Storage layout**

- **Can you separate disk space on a single EC2 instance so the application runs on one partition and the observability stack on another?**
- **How do you actually perform that separation, and which AWS services or Linux tools do you use to do it?**

**Experience and capability**

- **Introduce yourself and describe your DevOps responsibilities in your current organisation.**
- **Explain the migration project you worked on.**
- **Have you containerised an application yourself?**
- **Have you built CI/CD pipelines from scratch, as opposed to maintaining existing ones?**
- **Have you used HashiCorp Vault, and for what?**
- **Do you write Java?**

## Example

```text
BMW TechWorks — DevOps Engineer (3-4 YOE), reported round
10 questions

  EC2 security / patching     2   find the vulnerability, patch at scale
  Storage layout              2   separate app and observability partitions,
                                  how exactly (LVM / extra EBS volume)
  Capability sweep            6   intro, migration project, containerisation,
                                  pipelines built solo, Vault, Java

WHAT THIS ROUND IS
  A hands-on screen. 6 of 10 questions are "have you actually done X
  yourself?" — one-word answers waste the opportunity. Each deserves a
  two-sentence example.
```

```bash
# The disk-separation answer, concretely: attach a second EBS volume
# and mount it where the observability stack writes.
lsblk                                  # confirm the new device
mkfs.ext4 /dev/nvme1n1
mkdir -p /var/lib/observability
mount /dev/nvme1n1 /var/lib/observability
# then persist it, by UUID, so a reboot does not lose the mount
blkid /dev/nvme1n1                     # -> add the UUID line to /etc/fstab
```

## Interview tips

- The disk-separation question is the technical core of this round, and the answer that lands is "yes, and here is why you would want to": a separate volume or partition stops a runaway metrics or log store from filling the root filesystem and taking the application down with it. Then give the mechanism — an additional EBS volume, or LVM if you need to grow it later — and mention `/etc/fstab` by UUID so the mount survives a reboot.
- Say explicitly that EBS volumes can be expanded online but shrinking requires a new volume and a copy. That asymmetry is the follow-up.
- For vulnerability identification, name the scanner rather than describing scanning in the abstract: Amazon Inspector for EC2, plus your OS package manager's security updates, and image scanning if the workload is containerised. Then split remediation into patch, restart or replace, and verify. See [prioritising vulnerabilities without blocking delivery](../devsecops/how-do-you-prioritise-vulnerabilities-without-blocking-delivery.md).
- Patching at scale should reach Systems Manager Patch Manager with maintenance windows and patch baselines, and — better — the immutable answer: bake a new AMI, roll the auto-scaling group, and never patch a live instance. Offer both and say which you prefer and why. See [how auto-scaling groups and load balancers work together](../aws-engineering/how-do-auto-scaling-groups-and-load-balancers-work-together-on-aws.md).
- Six questions are closed yes-or-no capability checks. Convert each into a short concrete claim — "yes, I containerised a Spring Boot service, multi-stage build, image went from 800 MB to 180 MB" — because a bare "yes" gives the interviewer nothing to grade. See [reducing Docker image size and build time](../docker/how-do-you-reduce-docker-image-size-and-build-time.md).
- The Vault question invites a specific detail: dynamic database credentials, leases and renewal, or the Kubernetes auth method. Any one of those proves real use rather than exposure. See [managing secrets in CI/CD pipelines](../devsecops/how-do-you-manage-secrets-in-ci-cd-pipelines.md).
- The Java question is a fit check for an automotive engineering organisation, not a coding test. Answer honestly and pivot to the languages you do use and what you build with them. See [when to use Bash and when to use Python](../scripting-and-automation/when-do-you-use-bash-and-when-do-you-use-python.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
- [[How do you integrate SonarQube and quality gates into a pipeline?]] (`#458`): [How do you integrate SonarQube and quality gates into a pipeline?](../cicd/how-do-you-integrate-sonarqube-and-quality-gates-into-a-pipeline.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
