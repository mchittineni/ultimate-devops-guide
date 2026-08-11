---
title: "What are Terraform provisioners and when should you avoid them?"
id: 467
category: "Infrastructure as Code"
difficulty: "Intermediate"
tags:
  - devops
  - infrastructure-as-code
  - interview-questions
  - configuration-management
---

# What are Terraform provisioners and when should you avoid them?

**Short answer:** Provisioners run imperative steps as part of a resource's create or destroy: **`local-exec`** runs a command on the machine running Terraform, **`remote-exec`** runs commands on the created resource over SSH or WinRM, and **`file`** copies a file to it. There is also the special **`null_resource`** (now better expressed as `terraform_data`) used to hang provisioners off nothing in particular. HashiCorp's own documentation calls provisioners **a last resort**, and the reasons are concrete: they are invisible to `terraform plan`, they are not idempotent, a failure marks the resource **tainted** so the next apply destroys and recreates it, they need inbound SSH plus credentials in your Terraform run, and they do not re-run when you change the script. The right answers instead: **`user_data`/`cloud-init`** or a custom image (Packer) for machine bootstrap, a **configuration-management tool** (Ansible) for ongoing configuration, and the cloud provider's own APIs through proper resources or a purpose-built provider for everything else. Use `local-exec` only for genuinely local glue that has no resource equivalent.

## Detail

### The three provisioners, plus the connection block

| Provisioner   | Runs where                                                   | Typical (mis)use                                                                      |
| ------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| `local-exec`  | The machine running Terraform (your laptop or the CI runner) | Trigger an Ansible playbook, write a kubeconfig, call a CLI with no provider coverage |
| `remote-exec` | Inside the created resource, over SSH/WinRM                  | `apt-get install nginx`, join a cluster, run a bootstrap script                       |
| `file`        | Copies local → remote over the same connection               | Drop a config file or a script before `remote-exec` runs it                           |

`remote-exec` and `file` need a `connection` block - host, user, private key or password, and network reachability. That is where the pain starts: Terraform must be able to reach the instance directly, which forces public IPs or a bastion path, and a private key must be available to the run.

### Creation-time versus destroy-time

By default a provisioner runs **at creation**, after the resource is created. `when = destroy` runs it **before** destruction - the legitimate use being graceful removal: deregister from a cluster, drain a node, remove a DNS record, unregister a licence. Destroy-time provisioners have real limitations: they must exist in the configuration at destroy time (so you cannot add one to clean up something you are removing), and if they fail the destroy is blocked.

`on_failure = continue` lets an apply proceed despite a failed provisioner; the default `fail` marks the resource tainted.

### Why they are a last resort

1. **Invisible to `plan`.** Terraform cannot tell you what a shell script will do, so the review-the-plan safety model breaks down entirely.
2. **Not idempotent.** `remote-exec` runs a script; running it twice may or may not be safe. Terraform's whole model assumes convergence, and provisioners opt out of it.
3. **Tainting.** If a provisioner fails, the resource is marked tainted and the **next apply destroys and recreates it** - so a transient SSH timeout costs you an instance. This is the behaviour people discover in production.
4. **They do not re-run on change.** Edit the script and `plan` shows nothing, because provisioners are part of create, not of ongoing state. Your instances now diverge silently from the code.
5. **Connectivity and credentials.** SSH reachability from the Terraform runner is an architectural constraint imposed by a convenience feature, and private keys in the run are a security concern.
6. **No error visibility at scale.** Fifty instances, one failed script, and the plan output tells you nothing useful.

### What to use instead

| Instead of                           | Use                                                                                        | Why                                                                                                             |
| ------------------------------------ | ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| `remote-exec` for bootstrap          | **`user_data` / cloud-init** (or `custom_data` on Azure, `metadata_startup_script` on GCP) | Runs on the instance itself with no inbound access needed, survives replacement, works with autoscaling         |
| `remote-exec` for full configuration | **Ansible** (or Chef/Puppet/Salt), triggered separately or pull-based                      | Idempotent by design, has its own reporting, and can converge repeatedly                                        |
| A long `user_data` script            | **A baked image via Packer**                                                               | Faster boot, deterministic, testable, no download-at-boot failures. This is the immutable-infrastructure answer |
| `local-exec` calling a CLI           | **The proper resource**, or a community provider, or the `http`/`external` data source     | Visible in the plan, tracked in state, destroyed correctly                                                      |
| `local-exec` for post-apply glue     | Outputs consumed by the **pipeline's next step**                                           | The pipeline is the right place for orchestration                                                               |
| `null_resource` with triggers        | **`terraform_data`** (1.4+), or move the work out of Terraform                             | Same capability, no provider dependency                                                                         |

The key argument for `user_data` over `remote-exec`, and the one that wins interviews: an autoscaling group launching a new instance at 3 a.m. will run `user_data`; it will never run your `remote-exec`, because Terraform is not there. Anything an instance needs in order to be functional must be in the image or in `user_data`.

### `null_resource` / `terraform_data` and `triggers`

`null_resource` exists to attach provisioners (or `depends_on` ordering) to something that is not a real resource. Its `triggers` map re-creates it - and therefore re-runs its provisioners - whenever a value in the map changes. That is how people force a script to run again:

```hcl
resource "terraform_data" "reindex" {
  triggers_replace = { schema_version = var.schema_version }
  provisioner "local-exec" { command = "./reindex.sh" }
}
```

The frequent question _"if a command is in a `null_resource` and it should run every time, what is the behaviour?"_ - it does **not** run every time. It runs on create, and again only when a trigger value changes. To force it every apply, people put a timestamp in `triggers` (`always_run = timestamp()`), which works but means the resource is permanently in the plan as a change - noisy, and a sign the work belongs outside Terraform.

`terraform_data` supersedes `null_resource` because it is built in and needs no `null` provider, and it can also hold arbitrary values as a stable substitute for `null_resource` used purely for `depends_on` sequencing.

### The legitimate uses

Be balanced - provisioners are not forbidden:

- `local-exec` writing a kubeconfig or an inventory file for the next pipeline stage.
- `local-exec` invoking `ansible-playbook` immediately after infrastructure exists, when you want one command for the whole flow (though a pipeline stage is cleaner).
- `when = destroy` cleanup that no provider resource covers: draining a node, deregistering an agent, revoking a licence.
- A one-off bootstrap in a lab or a proof of concept, where the cost of being non-idempotent is zero.
- `file` + `remote-exec` for appliances or legacy systems with no cloud-init and no API.

Say which of these you would accept and which you would refuse; that judgement is what is being tested.

## Example

```hcl
# WHAT NOT TO DO - and be able to explain every problem with it
resource "aws_instance" "bad" {
  ami           = data.aws_ami.al2023.id
  instance_type = "t3.micro"
  key_name      = "deploy-key"

  connection {                       # requires SSH reachability from the runner
    type        = "ssh"
    host        = self.public_ip      # forces a public IP
    user        = "ec2-user"
    private_key = file("~/.ssh/id_rsa")  # a private key inside the Terraform run
  }

  provisioner "remote-exec" {
    inline = ["sudo dnf install -y nginx", "sudo systemctl enable --now nginx"]
    # invisible to plan; not idempotent; a transient timeout taints the instance
    # and the next apply REPLACES it; editing this list changes nothing on reapply;
    # and an autoscaling replacement at 3am never runs it at all.
  }
}
```

```hcl
# WHAT TO DO - cloud-init, so it works for every instance including ASG replacements
resource "aws_instance" "good" {
  ami                    = data.aws_ami.hardened_base.id # baked with Packer
  instance_type          = "t3.micro"
  iam_instance_profile   = aws_iam_instance_profile.app.name
  vpc_security_group_ids = [aws_security_group.app.id]
  subnet_id              = aws_subnet.private["private-eu-west-1a"].id # no public IP

  user_data_replace_on_change = true # changing the script rebuilds the instance
  user_data = base64encode(templatefile("${path.module}/cloud-init.yaml", {
    environment = var.environment
    config_url  = "s3://acme-config/${var.environment}/app.yaml"
  }))

  lifecycle { create_before_destroy = true }
}
```

```yaml
# cloud-init.yaml - declarative bootstrap that runs on the instance, every time
#cloud-config
package_update: true
packages: [nginx, amazon-cloudwatch-agent]
write_files:
  - path: /etc/app/environment
    content: |
      ENVIRONMENT=${environment}
      CONFIG_URL=${config_url}
runcmd:
  - [systemctl, enable, --now, nginx]
  - [systemctl, enable, --now, amazon-cloudwatch-agent]
```

```hcl
# The acceptable local-exec: glue for the next pipeline stage, plus destroy-time cleanup
resource "local_file" "ansible_inventory" {
  filename = "${path.module}/inventory.ini"
  content  = templatefile("${path.module}/inventory.tmpl", {
    hosts = [for i in aws_instance.good : i.private_ip]
  })
}

resource "terraform_data" "drain_node" {
  input = aws_instance.good.id

  provisioner "local-exec" {
    when       = destroy
    command    = "./drain-and-deregister.sh ${self.input}" # graceful removal
    on_failure = fail
  }
}
```

```bash
# Diagnosing a tainted resource after a failed provisioner
terraform state list
terraform plan            # look for "-/+ ... (tainted)" - the next apply will REPLACE it
terraform untaint aws_instance.bad   # if the resource is actually fine, clear the mark
TF_LOG=DEBUG terraform apply 2>&1 | grep -A5 remote-exec   # see what the script did
```

## Interview tips

- Name the three provisioners and where each executes, then immediately say HashiCorp treats them as a **last resort** and give at least three of the reasons: invisible to `plan`, not idempotent, and a failure taints the resource so the next apply replaces it.
- The winning argument for `user_data` over `remote-exec` is the autoscaling one: a replacement instance launched by an ASG runs `user_data` and never runs your provisioner. Say it exactly like that.
- Map each provisioner to its proper replacement - cloud-init or a Packer image for bootstrap, Ansible for ongoing configuration, a real resource or provider for API calls, pipeline stages for orchestration.
- For "what is the difference between `user_data` and a remote provisioner?", answer in terms of who executes it (the instance versus Terraform), what it requires (nothing versus SSH plus keys), and what happens on replacement.
- Explain `null_resource` and `triggers` accurately: it runs on create and re-runs only when a trigger value changes - not on every apply - and mention `terraform_data` as the modern built-in replacement.
- Be balanced rather than dogmatic. Name the uses you would accept: local glue for the next stage, destroy-time graceful cleanup, and appliances with no cloud-init.
- If asked about the difference between a **provider** and a **provisioner**: a provider is the plugin that implements resources and talks to an API declaratively; a provisioner is an imperative escape hatch attached to a resource's lifecycle. They are unrelated despite the similar name, and interviewers use the pair as a trap. See [what are Terraform providers](./what-are-terraform-providers.md), [what is immutable infrastructure](./what-is-immutable-infrastructure-and-how-do-you-adopt-it.md), [Ansible versus Terraform](./what-is-the-difference-between-ansible-and-terraform.md), and [what do terraform init, plan, apply, and refresh actually do](./what-do-terraform-init-plan-apply-and-refresh-actually-do.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you structure an Ansible role and share it through Galaxy?]] (`#468`): [How do you structure an Ansible role and share it through Galaxy?](../configuration-management/how-do-you-structure-an-ansible-role-and-share-it-through-galaxy.md)
- [[What is Salt (SaltStack)?]] (`#54`): [What is Salt (SaltStack)?](../configuration-management/what-is-salt-saltstack.md)
- [[How do you handle secrets in Ansible with Vault?]] (`#470`): [How do you handle secrets in Ansible with Vault?](../configuration-management/how-do-you-handle-secrets-in-ansible-with-vault.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Infrastructure as Code](./README.md) · [All topics](../README.md)
