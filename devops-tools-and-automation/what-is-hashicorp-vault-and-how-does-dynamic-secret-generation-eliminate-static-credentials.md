---
title: "What is HashiCorp Vault and how does dynamic secret generation eliminate static credentials?"
id: 631
category: "DevOps Tools and Automation"
difficulty: "Intermediate"
tags:
  - devops
  - devops-tools-and-automation
  - interview-questions
  - vault
  - security
  - secrets
  - hashicorp
quiz:
  stem: "What occurs on the target database when a HashiCorp Vault dynamic secret lease expires without renewal?"
  options:
    - "Vault crashes and restarts"
    - "Vault automatically connects to the database and drops or disables the generated temporary user credentials"
    - "The database tables are archived to S3"
    - "Vault sends an email to all developers"
  answer: 2
  explanation: "Dynamic secrets are leased. When the lease expires, Vault automatically executes revocation statements on the target database, dropping the temporary user account."
---

# What is HashiCorp Vault and how does dynamic secret generation eliminate static credentials?

**Short answer:** HashiCorp Vault is an identity-based secret management system that encrypts sensitive data; its dynamic secrets engine generates unique, short-lived database and cloud credentials on-demand with automatic expiration and revocation.

## Detail

Static credentials in `.env` files, CI variables, or even a secrets manager share the same weakness: they are long-lived, shared by many workloads, rarely rotated, and valid for as long as nobody notices they leaked. Dynamic secrets remove the standing credential altogether.

### How dynamic secrets work

The application first proves who it is with an **auth method** - Kubernetes (the Pod's ServiceAccount token), AWS/Azure/GCP IAM, JWT/OIDC for CI jobs, AppRole - and receives a short-lived Vault token scoped by policy. Then:

```text
1. App authenticates to Vault          -> receives a short-lived Vault token
2. App requests DB credentials          -> GET /v1/database/creds/readonly
3. Vault connects to PostgreSQL and runs the role's creation statements:
     CREATE ROLE "v-k8s-readonly-8f3a" WITH LOGIN PASSWORD '<random>'
       VALID UNTIL '2026-09-23 21:00:00+00';
     GRANT SELECT ON ALL TABLES IN SCHEMA public TO "v-k8s-readonly-8f3a";
4. Vault returns the username and password with a lease (e.g. 1 hour, renewable up to a max TTL)
```

Every Pod gets its **own** credential, so the database audit log names the workload, and revoking one does not affect the others.

### Leases and revocation

- Each credential has a **lease**. The client (usually Vault Agent, the Vault Secrets Operator, or an SDK) renews it while the workload runs, up to `max_ttl`, then fetches a new one.
- When a lease expires or is revoked, Vault runs the role's **revocation statements** on the target (e.g. `DROP ROLE`), so the credential stops working.
- In an incident, `vault lease revoke -prefix database/creds/readonly` kills every credential issued from that role at once. The same model applies to the AWS engine (short-lived IAM credentials or STS tokens), PKI (short-lived certificates), and others.
- Vault also rotates the **root credential** it uses to connect to the database, so no human knows it.

### Trade-offs and current landscape

- **Vault becomes a tier-0 dependency.** If it is unavailable, new Pods cannot get credentials. Run it HA (integrated Raft storage), plan unseal (auto-unseal via a cloud KMS), and monitor lease counts - millions of short leases put real load on Vault and on the target database.
- **Applications must handle credential changes**: reconnect pools when credentials rotate, or use Vault Agent/VSO to render and refresh them.
- **Licensing**: HashiCorp moved Vault to the Business Source License in 2023 (and HashiCorp is now part of IBM). **OpenBao**, a Linux Foundation fork of the last open-source release, offers the same core model under MPL 2.0. Cloud-native alternatives cover part of the use case: AWS RDS IAM authentication, Azure Entra ID authentication for databases, GCP IAM database auth, and workload identity for cloud APIs remove the need for a password at all.

## Example

```bash
# One-time setup by the platform team: database secrets engine plus a role.
vault secrets enable database
vault write database/config/orders \
  plugin_name=postgresql-database-plugin \
  connection_url="postgresql://{{username}}:{{password}}@orders-db:5432/orders" \
  username="vault-admin" password="$BOOTSTRAP_PASSWORD" \
  allowed_roles="readonly"
vault write -force database/rotate-root/orders    # now only Vault knows the admin password

vault write database/roles/readonly db_name=orders default_ttl=1h max_ttl=24h \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';
                       GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";"

# A workload (or a person, for testing) gets a unique, expiring credential.
vault read database/creds/readonly
# lease_id   database/creds/readonly/2f6a...   lease_duration 1h   username v-token-readonly-...

# Incident: revoke every credential this role has issued.
vault lease revoke -prefix database/creds/readonly
```

## Interview tips

- Start with the problem: static credentials are shared, long-lived, and rarely rotated.
- Walk the flow: auth method (Kubernetes ServiceAccount, cloud IAM, OIDC) → token → per-request credential with a lease.
- Explain revocation mechanically - Vault runs revocation statements on the target - and `lease revoke -prefix` for incidents.
- Name the costs: Vault is a critical dependency, applications must reconnect on rotation, and lease volume needs capacity planning.
- Mention the BSL licence change and OpenBao, and that cloud IAM database authentication can remove passwords entirely.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[What is Pipeline as Code and how do modern CI systems validate and isolate pipeline runs?]] (`#532`): [What is Pipeline as Code and how do modern CI systems validate and isolate pipeline runs?](../cicd/what-is-pipeline-as-code-and-how-do-modern-ci-systems-validate-and-isolate-pipeline-runs.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Tools and Automation](./README.md) · [All topics](../README.md)
