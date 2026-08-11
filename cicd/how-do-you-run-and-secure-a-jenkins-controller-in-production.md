---
title: "How do you run and secure a Jenkins controller in production?"
id: 456
category: "CI/CD"
difficulty: "Advanced"
tags:
  - devops
  - cicd
  - interview-questions
  - devsecops
  - infrastructure-as-code
---

# How do you run and secure a Jenkins controller in production?

**Short answer:** Treat the controller as a **stateful, high-value production system**, because it holds credentials to everything you deploy to. That means: **never run builds on the controller** (set its executors to 0 and use ephemeral agents), keep all state in `$JENKINS_HOME` on durable storage and back that up, define the configuration as code (JCasC plus a pinned plugin list) so the controller is rebuildable rather than hand-tuned, put authentication behind your identity provider with **matrix or role-based authorisation** rather than "logged-in users can do anything", scope credentials to folders and inject them per job, and keep plugins and the LTS version patched on a schedule. The framing that lands in an interview: **a Jenkins controller is a deployment target with production credentials - if it is compromised, every environment it can reach is compromised**, so its security posture should match the most sensitive thing it can deploy to.

## Detail

### Backup and restore: what actually matters

Everything Jenkins knows lives in `$JENKINS_HOME`. The parts you must have:

| Path                           | Contents                                          | Notes                                                                                                              |
| ------------------------------ | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `config.xml`                   | Global config, authorisation strategy             |                                                                                                                    |
| `jobs/*/config.xml`            | Job definitions                                   | Build _history_ is under `jobs/*/builds/` and is usually the bulk - decide whether you need it                     |
| `credentials.xml` + `secrets/` | Encrypted credentials **and the master key**      | Credentials are useless without `secrets/master.key` and `hudson.util.Secret`. This is the single most-missed item |
| `users/`                       | Local users, API tokens                           | Irrelevant if you use SSO, which you should                                                                        |
| `plugins/*.jpi`                | Installed plugins + versions                      | Or better, a pinned `plugins.txt` in your image                                                                    |
| `nodes/`                       | Agent definitions                                 |                                                                                                                    |
| `*.xml` at root                | Plugin-level config (JCasC replaces most of this) |                                                                                                                    |

Practical approach: **stop or quiet down** the controller (or use the ThinBackup plugin / a filesystem or EBS snapshot) so you get a consistent copy, exclude `workspace/` and `caches/`, keep the archive off the controller's own host, and **restore it into a throwaway instance periodically** to prove it works. The answer that impresses is the second half: "and I have restored it, so I know the credentials come back."

The stronger position is that you should not need the backup for configuration at all - **JCasC + Job DSL/multibranch + a pinned plugin list in a container image** means the controller is reproducible from Git, and the only genuinely stateful thing left is credentials and build history. That is the modern answer to "how do you back up Jenkins?"

### Authentication and authorisation

- **Authentication**: your IdP via SAML/OIDC (Entra ID, Okta, Google) or the GitHub/LDAP plugins. Disable local signup. Kill anonymous read.
- **Authorisation**: `Matrix Authorization Strategy` or `Role-Based Authorization Strategy` mapped to IdP groups. The frequently-asked scenario - _give five jobs view-only access to some users_ - is answered by folder-scoped permissions: put the jobs in a folder, grant that group `Job/Read` (and `Job/Discover`, optionally `Job/Workspace`) on the folder only, and grant nothing globally. Do not grant `Overall/Administer` to solve a permission problem.
- **`Overall/Administer` is root.** An admin can run Groovy on the controller through the script console, which means reading every credential and executing as the Jenkins user. Count your admins; that number is your blast radius.
- **CSRF protection and the Groovy sandbox stay on.** Approving arbitrary unsandboxed scripts is how controllers get owned from a pull request.
- **API tokens, not passwords**, for automation, scoped per integration and rotated.

### Credentials

Store them in Jenkins Credentials scoped to a **folder**, not globally, so a job in one team's folder cannot bind another team's secret. Inject them per step (`withCredentials`, or `environment { X = credentials('id') }`) so they exist only for that block and are masked in the log. Prefer short-lived, federated credentials wherever the target supports it - OIDC to AWS/Azure/GCP, so the controller stores no long-lived cloud keys at all. And note the limit of masking: `set -x`, a `curl -v`, or an application that echoes its environment will still leak. See the dedicated answer on secret leaks in pipelines.

### Architecture: controller, agents, and no builds on the controller

Set controller executors to **0**. A build on the controller has direct filesystem access to `credentials.xml`, `secrets/`, and every job's workspace - it is a privilege-escalation path by design. Then choose an agent model:

- **Kubernetes plugin** - one fresh Pod per build. Ephemeral, clean, autoscaling with the cluster, and the strongest isolation of the common options. This is the default recommendation now.
- **Cloud agents (EC2/Azure VM plugin)** - spin up on demand, terminate when idle. Good when builds need a full VM or specific hardware.
- **Static agents** - simple, but state accumulates and one build can poison the next. Label them carefully and rebuild them regularly.

Connect agents outbound (JNLP/WebSocket) so you do not need inbound access to build machines, and give agents only the credentials their builds need - not the controller's.

### Keeping it healthy

- **Upgrade cadence**: track Jenkins **LTS** and patch monthly; plugin CVEs are the most common Jenkins vulnerability class. Pin plugin versions, test upgrades in a staging controller, and use the plugin manager's security warnings as your queue. Remove plugins you no longer use - every plugin is attack surface and an upgrade constraint.
- **Resource sizing**: heap sized deliberately (not the default), `-XX:+UseG1GC`, and remember that `Jenkinsfile` Groovy executes on the controller - so a pipeline doing heavy string work in Groovy is a controller performance problem. Watch queue length, executor utilisation, and GC pauses.
- **Prune aggressively**: `buildDiscarder(logRotator(...))` on every job. Unbounded build history is the usual cause of a controller with a full disk and a slow UI.
- **Concurrency**: `disableConcurrentBuilds()` on deploy jobs; enough executors on agents that the queue does not back up. See the queue-troubleshooting answer for the diagnostic path.
- **HA reality check**: Jenkins OSS has no true active-active HA. What you build instead is fast recovery - immutable controller image plus JCasC plus a restored `$JENKINS_HOME` volume, with a documented and rehearsed RTO. If a controller failure is unacceptable, that is an argument for a managed/HA distribution or for a CI system that is stateless by design.

### If the controller is down

Diagnose in order: is the process alive (`systemctl status jenkins`, or the Pod's status and events), is the disk full (the most common single cause), is it thrashing in GC or out of heap (`jenkins.log`, GC logs), did a plugin upgrade break startup (start in safe mode with plugins disabled, or roll the image back), is the reverse proxy or ingress broken rather than Jenkins, and is `$JENKINS_HOME` mounted and writable. Recovery paths: fix in place, roll the container image back, or restore `$JENKINS_HOME` onto a fresh controller. Builds in flight are lost unless the pipeline was durable and the agents survived - which is a good argument for making pipelines idempotent and re-runnable.

## Example

```yaml
# jenkins.yaml - configuration as code: the controller is now reproducible from Git
jenkins:
  systemMessage: "Managed by JCasC - do not configure through the UI"
  numExecutors: 0 # never build on the controller
  mode: EXCLUSIVE
  authorizationStrategy:
    roleBased:
      roles:
        global:
          - name: admin
            permissions: ["Overall/Administer"]
            assignments: ["platform-admins"] # an IdP group, and a short list
          - name: readonly
            permissions: ["Overall/Read", "Job/Read", "Job/Discover"]
            assignments: ["authenticated"]
  securityRealm:
    oic: # SSO; local signup disabled
      clientId: "${OIDC_CLIENT_ID}"
      clientSecret: "${OIDC_CLIENT_SECRET}"
      wellKnownOpenIDConfigurationUrl: "https://idp.example.com/.well-known/openid-configuration"
  clouds:
    - kubernetes: # ephemeral agent per build
        name: k8s
        namespace: jenkins-agents
        jenkinsUrl: "http://jenkins.jenkins.svc.cluster.local:8080"
        containerCapStr: "50"
        templates:
          - name: build
            label: linux
            containers:
              - name: jnlp
                image: jenkins/inbound-agent:3283.v92c105e0f819-9
                resourceRequestCpu: "500m"
                resourceLimitMemory: "2Gi"
security:
  globalJobDslSecurityConfiguration: { useScriptSecurity: true }
  scriptApproval: { approvedSignatures: [] } # keep the sandbox meaningful
unclassified:
  location: { url: "https://jenkins.example.com/" }
```

```bash
# Backup: consistent, complete, and off-host
systemctl stop jenkins        # or use a volume snapshot / ThinBackup for hot copies
tar czf /tmp/jenkins-$(date +%F).tgz \
  --exclude='workspace' --exclude='caches' --exclude='*/builds/*/archive' \
  -C /var/lib jenkins        # includes secrets/ and credentials.xml - both required
systemctl start jenkins
aws s3 cp /tmp/jenkins-$(date +%F).tgz s3://acme-jenkins-backups/ \
  --sse aws:kms --storage-class STANDARD_IA

# Prove it: restore into a throwaway controller and check a credential binds
docker run -d -p 8081:8080 -v /restore/jenkins:/var/jenkins_home jenkins/jenkins:2.479.3-lts
```

```bash
# Health and hygiene checks worth scripting
curl -s -u "$U:$T" https://jenkins.example.com/api/json?tree=quietingDown,numExecutors
curl -s -u "$U:$T" https://jenkins.example.com/queue/api/json | jq '.items | length'
du -sh /var/lib/jenkins/jobs/*/builds | sort -h | tail   # who is eating the disk?

# Who has administer? (run in the script console, sparingly - it is root)
# Jenkins.instance.getAuthorizationStrategy().getGrantedRoles(...)  -> review, then reduce

# Plugin CVE queue
curl -s -u "$U:$T" https://jenkins.example.com/updateCenter/api/json?tree=jobs\[*\] | jq .
```

## Interview tips

- Open with the risk framing: the controller holds credentials to every environment, so its security bar equals the most sensitive target it can deploy to. That reframes a "backup" question into an architecture answer.
- Say "zero executors on the controller" early and explain why - a build on the controller can read `credentials.xml` and `secrets/` directly. This is the single most important Jenkins hardening fact.
- For the backup question, list `$JENKINS_HOME` and specifically call out `secrets/master.key` alongside `credentials.xml`. Forgetting the key is the classic failed restore, and mentioning it proves you have done one.
- Then upgrade the answer: with JCasC, a pinned plugin list, and multibranch/Job DSL, the controller is rebuildable from Git and the only irreplaceable state is credentials and history.
- Answer the view-only-access scenario concretely: folder-scoped `Job/Read` for an IdP group, nothing granted globally, and never `Overall/Administer` as a workaround.
- Mention ephemeral Kubernetes agents as the default agent model, with outbound-only agent connections.
- Cover patching explicitly - LTS line, monthly plugin updates, remove unused plugins - because plugin CVEs are the realistic attack path.
- Be honest that Jenkins OSS has no active-active HA and describe fast, rehearsed recovery instead. See [how do you prevent and handle secret leaks in CI/CD pipelines](./how-do-you-prevent-and-handle-secret-leaks-in-ci-cd-pipelines.md), [troubleshooting a Jenkins pipeline that never starts](./how-do-you-troubleshoot-a-jenkins-pipeline-that-never-starts-or-hangs-in-the-queue.md), [Jenkins shared libraries](./how-do-you-use-jenkins-shared-libraries.md), and [what is Jenkins](./what-is-jenkins.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you manage build artefacts with Nexus or Artifactory?]] (`#460`): [How do you manage build artefacts with Nexus or Artifactory?](../devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md)
- [[How do you troubleshoot a GitOps pipeline that will not sync?]] (`#428`): [How do you troubleshoot a GitOps pipeline that will not sync?](../devops-tools-and-automation/how-do-you-troubleshoot-a-gitops-pipeline-that-will-not-sync.md)
- [[What does a DevSecOps pipeline look like end to end?]] (`#161`): [What does a DevSecOps pipeline look like end to end?](../devsecops/what-does-a-devsecops-pipeline-look-like-end-to-end.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
