---
title: "How do you containerise a legacy application and move it to Kubernetes?"
id: 431
category: "Cloud Migration"
difficulty: "Advanced"
tags:
  - devops
  - cloud-migration
  - interview-questions
  - docker
  - kubernetes
  - cloud-native-architecture
---

# How do you containerise a legacy application and move it to Kubernetes?

**Short answer:** Lift the application into a container **without rewriting it**, then fix only what Kubernetes actually requires. In order: **discover the real dependencies** (files on disk, local state, hostnames, licences, cron jobs, scheduled tasks, that one NFS mount nobody documented), **externalise configuration and state** (config from environment or ConfigMaps, sessions to Redis, uploads to object storage, logs to stdout), **build a single-process image** with a health endpoint and graceful `SIGTERM` handling, **run it beside the existing deployment** and shift traffic gradually rather than cutting over, and only afterwards consider decomposing it. Resist the temptation to containerise and microservice at the same time - two risky changes at once make failure impossible to attribute. The honest part of the answer: some applications should not be containerised, and knowing which is the senior skill.

## Detail

### Phase 1: discovery - the phase people skip and then regret

Legacy applications carry undocumented dependencies. Find them before you build anything:

- **Filesystem state.** Uploaded files, generated reports, caches, embedded databases (SQLite, Access), and lock files. Every one is a decision: move to object storage, to a PVC, or accept a `ReadWriteMany` mount.
- **Local services.** A daemon on `localhost`, a message broker on the same VM, a scheduled `cron` job, a Windows service, or a log rotation script. Each becomes a separate workload - a sidecar, a CronJob, or its own Deployment.
- **Network identity.** Hardcoded hostnames or IPs, firewall rules keyed on the server's address, an SSL certificate tied to that hostname, or a licence bound to a MAC address or CPU count. Licences bound to hardware are a genuine blocker worth raising early.
- **Configuration.** Where does it live - INI files, a registry key, a properties file baked into the WAR, an environment-specific build? All of it must become injectable.
- **Startup and shutdown.** How long to boot, does it require an ordered start with the database, and does it survive being killed?
- **Resource profile.** Measure real CPU, memory, and I/O under load, because your requests and limits come from data, not from the VM's spec sheet.

Write it down as a dependency inventory. That document is what makes the estimate credible and the migration boring.

### Phase 2: make it container-shaped

Kubernetes assumes a specific shape. The minimum changes:

- **One process per container**, foreground, PID 1 behaving properly (or an init shim like `tini` so signals and zombies are handled). If the application needs a supervisor for several processes, split them into separate containers or Pods instead.
- **Logs to stdout/stderr**, not to files inside the container. Keep the file paths if you must, but symlink or tee them out - see [what is log management](../infrastructure-monitoring/what-is-log-management.md).
- **Configuration from the environment** (12-factor style), with secrets injected at runtime. See [what are the 12-Factor App principles](../cloud-native-architecture/what-are-the-12-factor-app-principles.md).
- **Health endpoints.** Add `/healthz` (process alive) and `/readyz` (dependencies reachable, warm-up complete) even if you have to bolt them on - Kubernetes cannot route safely without them, and a rolling update without real readiness is just a faster outage. See [how do liveness, readiness, and startup probes differ](../kubernetes/how-do-liveness-readiness-and-startup-probes-differ.md).
- **Graceful shutdown.** Handle `SIGTERM`, finish in-flight requests, and set `terminationGracePeriodSeconds` plus a `preStop` sleep so endpoints drain first.
- **State externalised.** Sessions to Redis (or sticky sessions as a documented interim), uploads to S3/Blob, and the database left where it is for now - moving compute and data in the same change doubles the risk.
- **Non-root, no writable root filesystem** where you can manage it, with an `emptyDir` for the paths that genuinely need writes. Expect this to be the fiddliest part of an old application. See [why does a container fail to start with a permission denied error](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md).

Where the application cannot be changed at all, a **strangler sidecar** is legitimate: keep the legacy process as-is and add a sidecar that translates configuration, exposes health, or ships logs.

### Phase 3: run it in parallel and shift traffic

Do not cut over. Deploy to Kubernetes alongside the existing VMs, point a small percentage of traffic at it (weighted DNS, a load balancer with both target groups, or an ingress with weighted routing), compare error rates and latency against the old fleet, and increase gradually. Keep the old environment warm and ready to take 100% again until you are confident. If sessions are sticky and not yet externalised, route by cohort rather than per request. This is the same discipline as a canary release, applied to infrastructure - see [what is blue/green deployment](../advanced-devops-cloud/what-is-blue-green-deployment.md).

Two things to prepare specifically:

- **Data.** If the database moves too, do it as its own project with replication and a small cutover window. See [how do you migrate a production database to the cloud with near-zero downtime](./how-do-you-migrate-a-production-database-to-the-cloud-with-near-zero-downtime.md).
- **Rollback.** Written, timeboxed, and tested - "point DNS back and the VMs are still running" is a good rollback; "restore from backup" is not.

### Phase 4: only now consider decomposition

Once it runs in Kubernetes with observability and a pipeline, you can decide whether to decompose - and you may find you do not need to. Strangle the parts that genuinely need independent scaling or ownership, one seam at a time, leaving the monolith in place. See [what is the difference between a monolith and microservices](../cloud-native-architecture/what-is-the-difference-between-a-monolith-and-microservices.md) and [what is application modernization](./what-is-application-modernization.md).

### When the answer is no

Be willing to say a workload should not move: a hardware-locked licence, a kernel-module dependency, a Windows application older than container support for its stack, sub-millisecond latency requirements with kernel bypass, or an application whose owner is retiring it in six months. "We left three of the eleven applications on VMs and documented why" is a stronger answer than a heroic migration of everything.

## Example

```dockerfile
# Lift, do not rewrite: one process, logs to stdout, config from env, health added
FROM tomcat:9.0-jdk17-temurin
# 1. the application, unchanged
COPY --chown=1001:1001 target/legacy-app.war /usr/local/tomcat/webapps/app.war
# 2. configuration comes from the environment at start, not baked into the WAR
COPY --chmod=0755 entrypoint.sh /entrypoint.sh
# 3. logs: Tomcat writes files by default - send them to stdout instead
RUN ln -sf /dev/stdout /usr/local/tomcat/logs/catalina.out \
 && chown -R 1001:1001 /usr/local/tomcat/work /usr/local/tomcat/temp
USER 1001
EXPOSE 8080
ENTRYPOINT ["/entrypoint.sh"]   # execs the JVM in the foreground so SIGTERM reaches it
```

```yaml
# Deployment: readiness the old app never had, graceful drain, state externalised
spec:
  replicas: 4
  template:
    spec:
      terminationGracePeriodSeconds: 60 # long enough for in-flight requests
      containers:
        - name: app
          image: registry.example.com/legacy-app@sha256:9f2c8b1d...
          envFrom:
            - configMapRef: { name: legacy-app-config } # was an INI file on the VM
            - secretRef: { name: legacy-app-secrets }
          env:
            - name: SESSION_STORE # was in-memory: sticky sessions blocked scaling
              value: "redis://sessions:6379"
            - name: UPLOAD_BACKEND # was /var/app/uploads on local disk
              value: "s3://acme-legacy-uploads"
          readinessProbe: # added during migration - it did not exist before
            httpGet: { path: /app/readyz, port: 8080 }
            initialDelaySeconds: 20
            periodSeconds: 5
          startupProbe: # 90s JVM + JPA warm-up: do not let liveness kill it
            httpGet: { path: /app/healthz, port: 8080 }
            failureThreshold: 30
            periodSeconds: 5
          resources: # from measured VM usage, not from the VM's spec sheet
            requests: { cpu: "1", memory: 2Gi }
            limits: { memory: 3Gi }
          lifecycle:
            preStop: { exec: { command: ["sh", "-c", "sleep 10"] } }
          volumeMounts:
            - { name: tmp, mountPath: /usr/local/tomcat/temp }
      volumes:
        - { name: tmp, emptyDir: {} }
---
# The 02:00 cron job from the VM's crontab - now a first-class object
apiVersion: batch/v1
kind: CronJob
metadata: { name: legacy-nightly-report }
spec:
  schedule: "0 2 * * *"
  timeZone: "Europe/London"
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      backoffLimit: 2
      activeDeadlineSeconds: 3600
      template:
        spec:
          restartPolicy: Never
          containers:
            - name: report
              image: registry.example.com/legacy-app@sha256:9f2c8b1d...
              command: ["/usr/local/bin/run-report.sh"]
```

```text
Traffic shift, not a cutover

  week 1   VMs 100%   k8s   0%   shadow traffic only, compare logs and latency
  week 2   VMs  95%   k8s   5%   one cohort, sticky; watch p99 and 5xx per target group
  week 3   VMs  75%   k8s  25%   sessions now in Redis, stickiness removed
  week 4   VMs  25%   k8s  75%   nightly CronJob cut over, VM crontab disabled
  week 5   VMs   0%   k8s 100%   VMs kept warm for 2 more weeks = the rollback plan
```

## Interview tips

- Say "lift first, refactor later" and give the reason: containerising and decomposing at the same time makes any failure impossible to attribute. Interviewers are checking for exactly this discipline.
- Lead with discovery, and name the unglamorous dependencies - local files, cron jobs, hardcoded hostnames, hardware-bound licences. That list is what makes you sound like someone who has done a migration rather than read about one.
- The Kubernetes-shape checklist (one foreground process, logs to stdout, config from env, health endpoints, graceful `SIGTERM`, state externalised) is the core of the answer. Health endpoints and shutdown handling are the two most often missing from legacy code.
- Mention that resource requests come from **measured** usage, not the VM's specification. It is a small point that separates real migrations from paper ones.
- Describe the parallel run and gradual traffic shift, plus keeping the old fleet warm as the rollback. "Point DNS back" beats "restore from backup" every time.
- Bring up cron jobs and scheduled tasks becoming CronJobs, and the double-run hazard if you forget to disable the VM's crontab. It is a genuine incident people hit.
- Keep data migration as a separate project, and say why: moving compute and state in one change multiplies risk.
- Finish by naming the cases where you would decline - hardware-locked licences, kernel modules, imminent retirement - and that documenting the exceptions is part of the deliverable. See [what are cloud migration strategies](./what-are-cloud-migration-strategies.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do you speed up a slow CI/CD pipeline?]] (`#396`): [How do you speed up a slow CI/CD pipeline?](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md)
- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Migration](./README.md) · [All topics](../README.md)
