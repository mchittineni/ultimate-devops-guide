---
title: "How do you handle secrets in Ansible with Vault?"
id: 470
category: "Configuration Management"
difficulty: "Intermediate"
tags:
  - devops
  - configuration-management
  - interview-questions
  - devsecops
---

# How do you handle secrets in Ansible with Vault?

**Short answer:** `ansible-vault` encrypts files or individual values with a symmetric key so they can live safely in Git. `ansible-vault encrypt group_vars/prod/vault.yml` encrypts a whole file; `ansible-vault encrypt_string` encrypts one value inline; and at run time you supply the password with `--vault-password-file` (pointing at a file **or an executable script** that prints the password) or `--ask-vault-pass`. Use **`--vault-id`** to keep separate passwords per environment, so a developer with the dev password cannot decrypt production. The convention that makes this workable in practice is **indirection**: keep encrypted variables in a `vault.yml` with a `vault_` prefix and reference them from plain-text variables (`db_password: "{{ vault_db_password }}"`), so you can still grep to see _where_ a secret is used without decrypting anything. And be clear about the limit - Vault is encryption at rest for your repository, not a secret manager: there is no rotation, no audit trail, and no per-request access control, so for anything serious, look secrets up at run time from HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault instead.

## Detail

### The commands

| Command                                                           | Purpose                                                                  |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `ansible-vault create secrets.yml`                                | Create a new encrypted file in `$EDITOR`                                 |
| `ansible-vault encrypt group_vars/prod/vault.yml`                 | Encrypt an existing plain-text file in place                             |
| `ansible-vault edit secrets.yml`                                  | Decrypt to a temp file, edit, re-encrypt - never leaves plaintext behind |
| `ansible-vault view secrets.yml`                                  | Print decrypted content without editing                                  |
| `ansible-vault decrypt secrets.yml`                               | Permanently decrypt (avoid; use `view`)                                  |
| `ansible-vault rekey secrets.yml`                                 | Change the password - this is how you "rotate" a Vault password          |
| `ansible-vault encrypt_string 'value' --name 'vault_db_password'` | Encrypt one value to paste inline in a normal YAML file                  |

An encrypted file is opaque to diffs, which is the main practical annoyance: a one-character change shows as a whole-file change and code review cannot see what altered. That is the strongest argument for `encrypt_string` on individual values (each value diffs independently) or for keeping secrets out of the repository entirely.

### Supplying the password without typing it

- `--ask-vault-pass` - interactive, fine for humans, useless in CI.
- `--vault-password-file ~/.vault_pass` - a file with mode `0600`, outside the repository.
- **A password _script_**: if the file is executable, Ansible runs it and reads the password from stdout. This is the mechanism that lets CI fetch the Vault password from a real secret manager instead of storing it on disk - and it is the answer to "how do you use an environment variable to supply a password?" (a two-line script that echoes `$VAULT_PASS`).
- `ANSIBLE_VAULT_PASSWORD_FILE` environment variable, or `vault_password_file` in `ansible.cfg`, so nobody has to remember the flag.

### `--vault-id`: separate passwords per environment

```bash
ansible-vault encrypt --vault-id prod@prompt group_vars/prod/vault.yml
ansible-playbook site.yml --vault-id dev@~/.vault_dev --vault-id prod@./scripts/get-prod-pass
```

Each encrypted file records which vault-id encrypted it, and Ansible tries the matching id first. This is how you enforce that only the release pipeline can decrypt production secrets, and it is a differentiating detail - most candidates only know the single-password form.

### The indirection convention, and why it matters

```yaml
# group_vars/prod/vault.yml   (ENCRYPTED)
vault_db_password: "s3cr3t-actual-value"
vault_api_key: "sk_live_..."

# group_vars/prod/main.yml    (plain text, in review, greppable)
db_password: "{{ vault_db_password }}"
api_key: "{{ vault_api_key }}"
```

Benefits: reviewers can see which variables are secrets and where they are consumed; renaming a variable does not require decryption; and `grep -r vault_db_password` finds every use. Without it, the only way to know what is in the encrypted file is to decrypt it, which nobody does during review.

### Keeping secrets out of logs and off disk

- **`no_log: true`** on any task that handles a secret. Without it, a failed task prints the module arguments - including the password - into the job log and into your CI artefacts. This is the most common real leak.
- Encrypted variables are decrypted **in memory on the control node** and passed to the target. They are not stored on the managed host unless a task writes them there - so avoid `copy: content=...` for secrets and prefer `template` with restrictive `mode: "0400"` and an owner that is not world-readable.
- Beware `-vvv`: verbose output prints task arguments. Debugging a failing task and pasting the output into a ticket is how secrets escape.
- **`ansible.cfg`** should set `no_log` friendly defaults where possible, and CI should mask the vault password variable.
- Registered results can contain secrets; `no_log` on the task suppresses them, and do not `debug: var=result` on such a task.

### Vault's real limits, and what to use instead

Say this part out loud in an interview, because it is what separates "I know the commands" from "I have run this":

| Vault gives you                   | Vault does not give you                                |
| --------------------------------- | ------------------------------------------------------ |
| Encryption at rest in Git         | Rotation - you must edit, re-encrypt, commit, redeploy |
| A shared password per environment | Per-user or per-service access control                 |
| Simplicity, no infrastructure     | An audit trail of who read what, when                  |
| Works offline                     | Dynamic, short-lived credentials                       |
| Version history of the ciphertext | Readable diffs in code review                          |

The production pattern is to fetch secrets at run time:

- **HashiCorp Vault** via the `community.hashi_vault.vault_kv2_get` lookup, with AppRole or JWT auth from CI.
- **AWS Secrets Manager / SSM Parameter Store** via `amazon.aws.secretsmanager_random_password`, the `aws_secret` lookup, or `aws_ssm`, authenticated by an instance profile or OIDC.
- **Azure Key Vault** via `azure.azcollection.azure_keyvault_secret`, authenticated by a managed identity.

Then Ansible Vault holds only the **bootstrap** credential (or nothing at all, if the runner has a machine identity). Rotation happens in the secret manager and Ansible picks up the new value on the next run, with no commit and no redeploy - which is the whole point.

### Encrypting a whole playbook

Occasionally asked - yes, `ansible-vault encrypt playbook.yml` works, and `ansible-playbook` will prompt for the password to run it. It is almost never the right thing: it makes the playbook unreviewable while hiding nothing sensitive (logic is not a secret). Encrypt the _variables_, not the code, and say so.

## Example

```bash
# Per-environment vault ids, with the prod password fetched from a real secret manager
ansible-vault encrypt --vault-id prod@prompt inventories/prod/group_vars/vault.yml
ansible-vault encrypt --vault-id dev@~/.vault_dev inventories/dev/group_vars/vault.yml

cat > scripts/get-prod-vault-pass <<'EOF'
#!/bin/sh
# executable password file: Ansible runs it and reads stdout
exec aws secretsmanager get-secret-value \
  --secret-id ansible/vault/prod --query SecretString --output text
EOF
chmod 0700 scripts/get-prod-vault-pass

ansible-playbook site.yml -i inventories/prod \
  --vault-id prod@scripts/get-prod-vault-pass

# One value at a time - diffs stay reviewable
ansible-vault encrypt_string --vault-id prod@scripts/get-prod-vault-pass \
  'changeme' --name 'vault_db_password'

# Rotate the vault password itself
ansible-vault rekey --vault-id prod@old-pass --new-vault-id prod@new-pass \
  inventories/prod/group_vars/vault.yml
```

```yaml
# Tasks that touch secrets: no_log, restrictive modes, no content= for secrets
- name: Configure the application datasource
  ansible.builtin.template:
    src: datasource.properties.j2
    dest: /etc/app/datasource.properties
    owner: app
    group: app
    mode: "0400" # not world-readable
  no_log: true # without this, a failure prints the rendered secret
  notify: Restart app

- name: Create the database user
  community.mysql.mysql_user:
    name: app
    password: "{{ db_password }}"
    priv: "app.*:ALL"
    state: present
  no_log: true

- name: Inline-encrypted value in an otherwise normal vars file
  ansible.builtin.set_fact:
    api_key: !vault |
      $ANSIBLE_VAULT;1.2;AES256;prod
      33613764653862...
```

```yaml
# The better pattern: look secrets up at run time, so rotation needs no commit
- name: Fetch credentials from HashiCorp Vault at run time
  ansible.builtin.set_fact:
    db_creds: "{{ lookup('community.hashi_vault.vault_kv2_get',
                          'prod/api/db', engine_mount_point='kv') }}"
  no_log: true
  delegate_to: localhost
  run_once: true

- name: Or from AWS Secrets Manager, authenticated by the runner's role
  ansible.builtin.set_fact:
    db_password: "{{ lookup('amazon.aws.aws_secret', 'prod/api/db',
                            nested=true, region='eu-west-1') }}"
  no_log: true
```

```bash
# Hygiene checks worth automating
grep -rL '\$ANSIBLE_VAULT' inventories/*/group_vars/vault.yml   # any left unencrypted?
git secrets --scan || gitleaks detect --no-banner                # nothing plaintext committed
ansible-playbook site.yml --check --diff -i inventories/prod     # --diff can print secrets:
                                                                # review before sharing output
```

## Interview tips

- Give the mechanism in one sentence - symmetric encryption of files or single values so secrets can live in Git - then name the commands: `encrypt`, `edit`, `view`, `rekey`, `encrypt_string`.
- Volunteer that a `--vault-password-file` can be an **executable script**, which is how CI fetches the password from a secret manager instead of storing it. That also answers the environment-variable question in a way that shows you have automated it.
- Bring up `--vault-id` for per-environment passwords, and say why: a developer with the dev password must not be able to decrypt production.
- Describe the `vault_`-prefix indirection convention and explain the review benefit. It is the practice that most distinguishes real usage.
- Say `no_log: true` unprompted and give the failure mode it prevents - a failed task printing the credential into the CI log. Add that `-vvv` output has the same problem.
- Be honest about the limits: no rotation, no audit trail, no per-request access control, and unreadable diffs. Then name the run-time lookup alternatives (HashiCorp Vault, Secrets Manager, Key Vault) with Ansible Vault holding only the bootstrap credential.
- If asked whether you can encrypt a whole playbook, say yes and then say why you would not - encrypt variables, not logic.
- Mention that secrets are decrypted on the control node in memory, and that writing them to a managed host needs restrictive file modes and ownership. See [managing Ansible inventories and variables](./how-do-you-manage-ansible-inventories-and-variables-across-environments.md), [managing secrets in CI/CD pipelines](../devsecops/how-do-you-manage-secrets-in-ci-cd-pipelines.md), [rotating secrets without downtime](../devsecops/how-do-you-rotate-secrets-without-downtime.md), and [preventing secret leaks in pipelines](../cicd/how-do-you-prevent-and-handle-secret-leaks-in-ci-cd-pipelines.md).

---

[⬅ Back to Configuration Management](./README.md) · [All topics](../README.md)
