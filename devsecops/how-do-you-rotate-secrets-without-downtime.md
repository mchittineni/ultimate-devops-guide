---
title: "How do you rotate secrets without downtime?"
id: 429
category: "DevSecOps"
difficulty: "Advanced"
tags:
  - devops
  - devsecops
  - interview-questions
  - cicd
  - security-and-compliance
  - configuration-management
---

# How do you rotate secrets without downtime?

**Short answer:** Never swap a secret in place - **overlap two valid credentials**. The pattern is the same for every secret type: create the new credential while the old one still works, distribute it, let every consumer pick it up (or fetch it dynamically), verify nothing is still using the old one, then revoke the old one as a separate, deliberate step. Downtime happens when rotation is a single atomic swap, when consumers cache the secret at startup and are never restarted, or when nobody knows the full list of consumers. The strategic answer is to remove long-lived secrets where you can - **short-lived dynamic credentials** (Vault database engine, IAM roles, IRSA/Workload Identity, OIDC federation in CI) turn rotation from a scheduled project into a property of the system.

## Detail

### The overlap pattern, in five phases

1. **Create** the new credential alongside the old. Both valid simultaneously - this is the whole trick. For a database, that means a second user or a second password where the engine supports dual passwords; for an API key, a second key; for a certificate, a second key pair with both trusted.
2. **Distribute** the new value to the secret store, and let consumers acquire it - by refresh (a sidecar or agent re-reading it), by controlled restart, or by the application re-reading on a schedule or a signal.
3. **Verify adoption.** Check that no client is authenticating with the old credential any more - database `pg_stat_activity` by username, cloud CloudTrail/audit logs by access key ID, or the secret store's own lease and access telemetry. **Do not skip this**: it is the step that separates a clean rotation from an outage, and it is the step people cut when they are in a hurry.
4. **Revoke** the old credential, as its own change, after the verification window.
5. **Record** it - what rotated, when, who approved, next due date - because that record is both the audit evidence and the thing that stops rotation silently lapsing.

### How consumers get the new value (the part that decides your downtime)

- **Dynamic fetch at use time** - the application asks Vault or Secrets Manager for the credential, with caching and a TTL. Best outcome: rotation needs no deployment and no restart. The cost is a dependency on the secret store on the request path, so cache and fail gracefully.
- **Sidecar or agent injection** - Vault Agent, the Secrets Store CSI driver, or External Secrets Operator writes the value into a file or a Kubernetes Secret and refreshes it. Note the subtlety: a Kubernetes Secret mounted as a **volume** updates in place (within the kubelet's sync period), but one consumed via **`env`** is fixed for the life of the Pod - so an env-var consumer requires a rolling restart. Knowing that distinction is the practical heart of this question.
- **Rolling restart** - simplest and often correct: update the Secret, then `kubectl rollout restart deployment/x`, which uses your existing zero-downtime mechanism. Tools like Reloader automate the restart on a Secret change.
- **Reload on signal** - the application re-reads configuration on `SIGHUP` or a watch. Good when restarts are expensive (a database, a stateful service).

### Type-specific notes worth knowing

- **Database passwords.** Prefer a second user (`app_a` / `app_b`) alternating between rotations, or an engine feature for dual passwords (Oracle, MySQL 8's `RETAIN CURRENT PASSWORD`, or Postgres with a role per generation). Watch connection pools: they hold open connections authenticated with the **old** password and only fail on reconnect, so problems appear minutes or hours later - which is why verification must look at active sessions, not just a successful test connection. The strongest answer is Vault's database secrets engine issuing a per-application short-lived user, so there is nothing long-lived to rotate.
- **Cloud access keys.** The correct answer is usually to delete them: use an instance role, IRSA/Pod Identity, Workload Identity, or OIDC federation from CI. Where a key must exist, the AWS pattern is well defined - create a second key, deploy, confirm zero usage of the first via `GetAccessKeyLastUsed`, deactivate (do not delete) it, wait, then delete. Deactivate-before-delete gives you a fast, reversible abort.
- **TLS certificates.** Automate with cert-manager or ACME. Overlap is inherent - issue and deploy the new certificate before the old expires - and the danger is a private CA whose **root** rotation must be a trust-distribution exercise: distribute the new CA to all trust stores first, then start serving the new leaf.
- **Signing keys and JWTs.** Publish both keys in the JWKS with distinct `kid` values, start signing with the new one, keep verifying with the old until every issued token has expired, then remove it.
- **Message broker, third-party, and webhook secrets.** Many support two active credentials (a "current" and "previous" webhook signing secret) - use it. Where they do not, you need a maintenance window or a proxy that can present either.

### When a secret is compromised, the rules change

Rotation for hygiene is a planned overlap; rotation after a leak is an incident. Revoke **first** and accept the outage - a leaked credential in an attacker's hands costs more than a few minutes of errors. Then rotate everything reachable with it, check the audit log for use you did not authorise, and remember that removing a secret from Git does not remove it from history, forks, or clones. See [how do you prevent and handle secret leaks in CI/CD pipelines](../cicd/how-do-you-prevent-and-handle-secret-leaks-in-ci-cd-pipelines.md).

### Making it routine rather than heroic

Inventory every secret with an owner and a consumer list (you cannot rotate what you cannot enumerate); automate rotation on a schedule (Secrets Manager rotation Lambdas, Vault leases, cert-manager) so the path is exercised constantly rather than annually; test rotation in staging as a first-class scenario; alert on expiry _before_ it happens (certificates, tokens, keys with a known lifetime); and set the ambition at **no long-lived secrets** so rotation becomes something the platform does rather than a quarterly project. See [how do you manage secrets in CI/CD pipelines](./how-do-you-manage-secrets-in-ci-cd-pipelines.md).

## Example

```bash
# AWS access key rotation: overlap, verify zero usage, deactivate, then delete
aws iam create-access-key --user-name svc-reporting          # 1. second key valid
# 2. push the new key to the secret store; consumers pick it up
aws secretsmanager put-secret-value --secret-id svc-reporting/key \
  --secret-string '{"AWS_ACCESS_KEY_ID":"AKIA...NEW","AWS_SECRET_ACCESS_KEY":"..."}'

# 3. VERIFY the old key is genuinely unused before touching it
aws iam get-access-key-last-used --access-key-id AKIA...OLD \
  --query 'AccessKeyLastUsed.LastUsedDate'
# 2026-08-10T09:04:00Z   <- still in use: something did not pick up the new key. Stop.

aws iam update-access-key --access-key-id AKIA...OLD --status Inactive   # 4. reversible
# wait out the verification window, then:
aws iam delete-access-key --access-key-id AKIA...OLD                     # 5. irreversible
```

```sql
-- Database rotation with two users, and the verification that actually matters
CREATE USER app_b WITH PASSWORD 'new-strong-value';         -- 1. overlap
GRANT app_role TO app_b;                                     --    identical grants

-- 3. who is still connected as the OLD user? Pools hold old connections open.
SELECT usename, count(*), min(backend_start)
FROM pg_stat_activity WHERE usename IN ('app_a','app_b') GROUP BY 1;
--  app_a | 18 | 2026-08-10 06:11   <- 18 pooled connections still on the old user
--  app_b | 22 | 2026-08-10 09:06

DROP USER app_a;                                             -- 5. only when count = 0
```

```yaml
# External Secrets Operator: rotation with no deployment, and a restart for env consumers
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata: { name: checkout-db, namespace: prod }
spec:
  refreshInterval: 1m # picks up the rotated value automatically
  secretStoreRef: { name: vault-backend, kind: ClusterSecretStore }
  target:
    name: checkout-db # the Kubernetes Secret it maintains
    creationPolicy: Owner
  data:
    - secretKey: password
      remoteRef: { key: database/creds/checkout, property: password }
---
# Volume-mounted secrets update in place; env vars do NOT - so trigger a restart
apiVersion: apps/v1
kind: Deployment
metadata:
  name: checkout
  namespace: prod
  annotations:
    reloader.stakater.com/auto: "true" # rolling restart when checkout-db changes
spec:
  template:
    spec:
      containers:
        - name: api
          volumeMounts: # preferred: file mount refreshes without a restart
            - { name: db, mountPath: /etc/secrets/db, readOnly: true }
      volumes:
        - name: db
          secret: { secretName: checkout-db }
```

## Interview tips

- Lead with the principle: **overlap two valid credentials**, never swap atomically. Every specific technique follows from it.
- The Kubernetes detail that proves hands-on experience: volume-mounted Secrets refresh in place, `env`-injected Secrets are fixed for the Pod's lifetime and need a rolling restart.
- Insist on the verification step and give a concrete method - `GetAccessKeyLastUsed`, `pg_stat_activity` by username, or the secret store's access log. Most candidates skip straight from "deploy new" to "delete old".
- Connection pools holding connections authenticated with the old password is the best war story here: the rotation looks successful and fails hours later on reconnect.
- Say "deactivate before delete" for cloud keys. It is a small operational habit that gives you a reversible abort.
- Distinguish planned rotation from compromise: for a leak you revoke first and accept the outage. Being decisive about that trade-off is what interviewers want to hear.
- Push toward eliminating long-lived secrets - dynamic database credentials, IRSA/Workload Identity, OIDC federation in CI - and note that this converts rotation from a project into a property of the platform.
- Mention the inventory problem honestly: rotation fails most often because nobody knows the complete list of consumers. Owner plus consumer list per secret is the unglamorous prerequisite. See [what does a DevSecOps pipeline look like end to end](./what-does-a-devsecops-pipeline-look-like-end-to-end.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[How do you keep dependencies up to date without breaking the build?]] (`#401`): [How do you keep dependencies up to date without breaking the build?](../cicd/how-do-you-keep-dependencies-up-to-date-without-breaking-the-build.md)
- [[How do you integrate SonarQube and quality gates into a pipeline?]] (`#458`): [How do you integrate SonarQube and quality gates into a pipeline?](../cicd/how-do-you-integrate-sonarqube-and-quality-gates-into-a-pipeline.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevSecOps](./README.md) · [All topics](../README.md)
