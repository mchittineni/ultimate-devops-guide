---
title: "How does Ansible handle secret encryption with Ansible Vault and what are its production trade-offs?"
id: 585
category: "Configuration Management"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - ansible
  - vault
  - secrets
  - security
quiz:
  stem: "What is the primary advantage of using Ansible Vault's `!vault` inline variable encryption over full-file encryption?"
  options:
    - "Inline encryption runs three times faster"
    - "It allows variable keys and non-sensitive settings to remain readable in Git diffs, preventing merge conflicts on unrelated parameters"
    - "Inline encryption does not require a vault password to decrypt"
    - "It automatically changes passwords every 30 days"
  answer: 2
  explanation: "Full-file encryption turns the entire YAML file into binary ciphertext, making Git diffs opaque and merge conflicts impossible to review. Inline encryption encrypts only the sensitive scalar value."
---

# How does Ansible handle secret encryption with Ansible Vault and what are its production trade-offs?

**Short answer:** Ansible Vault encrypts sensitive YAML files or individual strings with a symmetric AES-256 cipher (key derived from the vault password with PBKDF2, integrity-protected with HMAC-SHA256), allowing secrets to be committed safely to Git and decrypted at runtime via vault password files or client scripts.

## Detail

Storing plaintext secrets (passwords, TLS private keys, API tokens) in configuration management repos is a catastrophic security vulnerability.

### Using Ansible Vault

- **Full File Encryption**: `ansible-vault encrypt vars/production_secrets.yml`
- **Variable-Level Encryption (`!vault`)**: Encrypts only the sensitive value while leaving key names readable for clean git diffs:

  ```yaml
  db_user: "postgres"
  db_password: !vault |
    $ANSIBLE_VAULT;1.1;AES256
    6334653639316531393663666531383863373539356361376332616434656662...
  ```

### Production Trade-Offs

- **Pros**: Secrets live alongside code; versioned synchronously with playbooks; zero external infrastructure required.
- **Cons**: Git merge conflicts in fully encrypted files are impossible to resolve without decrypting; no built-in automatic secret rotation; access audit logging is non-existent compared to dedicated secret managers (HashiCorp Vault/OpenBao, AWS Secrets Manager); and everyone who holds the vault password can decrypt every secret encrypted with it, including all of Git history - so a leaked or departing-employee password means rotating the secrets themselves, not just running `rekey`.
- **Mitigations**: separate `--vault-id` passwords per environment, the vault password delivered by an executable script from a real secret manager in CI, `no_log: true` on tasks that handle secrets, and moving high-value or frequently rotated secrets to run-time lookups.

## Example

```bash
# Encrypt one value for inline use, with an environment-specific vault id
ansible-vault encrypt_string --vault-id prod@prompt 'S3cr3t!' --name 'vault_db_password'

# Run with the password supplied by a script (e.g. fetching from a secret manager)
ansible-playbook site.yml -i inventories/prod --vault-id prod@scripts/get-vault-pass

# Change the vault password (does NOT rotate the secrets it protects)
ansible-vault rekey --vault-id prod@prompt --new-vault-id prod@prompt group_vars/prod/vault.yml
```

## Interview tips

- State the crypto accurately: symmetric AES-256 with a password-derived key; there is no per-user access control.
- Compare inline `!vault` values (readable keys, clean diffs) with whole-file encryption (opaque diffs, unresolvable conflicts).
- Distinguish `rekey` (new password, same secrets) from real rotation (new secret values), and say which one a leaked password requires.
- Recommend a dedicated secret manager for rotation and audit, with Ansible Vault holding only bootstrap values.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Shift-Left and how is it practically implemented across the SDLC?]] (`#510`): [What is Shift-Left and how is it practically implemented across the SDLC?](../core-devops-concepts/what-is-shift-left-and-how-is-it-practically-implemented-across-the-sdlc.md)
- [[What is Pipeline as Code and how do modern CI systems validate and isolate pipeline runs?]] (`#532`): [What is Pipeline as Code and how do modern CI systems validate and isolate pipeline runs?](../cicd/what-is-pipeline-as-code-and-how-do-modern-ci-systems-validate-and-isolate-pipeline-runs.md)
- [[How does OpenID Connect (OIDC) eliminate long-lived cloud credentials in CI/CD pipelines?]] (`#533`): [How does OpenID Connect (OIDC) eliminate long-lived cloud credentials in CI/CD pipelines?](../cicd/how-does-openid-connect-oidc-eliminate-long-lived-cloud-credentials-in-ci-cd-pipelines.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Configuration Management](./README.md) · [All topics](../README.md)
