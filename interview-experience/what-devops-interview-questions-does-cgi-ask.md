---
title: "What DevOps interview questions does CGI ask?"
id: 320
category: "Interview Experience"
difficulty: "Intermediate"
tags:
  - devops
  - interview-experience
  - interview-questions
  - cgi
  - cicd
  - docker
  - devsecops
  - kubernetes
  - database-management-in-devops
---

# What DevOps interview questions does CGI ask?

## Questions

**CI/CD and Jenkins**

- **How did you reduce a pipeline's run time from one hour to twenty minutes? What specifically did you change?**
- **Write a checkout stage that authenticates to Git with credentials.**
- **If every team wants to use shared variables, what approach would you take to manage them?**
- **How do you define and reference variables in a Jenkins pipeline?**
- **What is a Jenkins agent, and how does work get distributed to one?**

**Docker**

- **Write a multi-stage Dockerfile.**

**Troubleshooting**

- **A Pod cannot connect to the database, but only for you — colleagues are fine. How do you troubleshoot that?**
- **The database logs have stopped being written. How do you diagnose it?**

**Security and CVEs**

- **What is a CVE?**
- **Which CVEs have you actually encountered in production, and how did you resolve them?**
- **Name five tools for identifying and remediating CVEs.**
  **How the round was run** — the candidate's closing note:

- **Expect CI/CD in depth, and expect to write out the pipeline stages in detail.**

## Example

```text
CGI — DevOps Engineer (4.1 YOE), reported round
12 questions

  CI/CD and Jenkins           5   1hr->20min optimisation, checkout with creds,
                                  shared variables, variable syntax, agents
  Security / CVEs             3   what a CVE is, ones you fixed, 5 tools
  Troubleshooting             2   DB reachable for others but not you,
                                  DB logs stopped
  Docker                      1   multi-stage Dockerfile

CANDIDATE'S OWN ADVICE
  "Mostly CI/CD in depth, write the stages in detail." Treat the Jenkinsfile
  as the main exam, not a side question.
```

```dockerfile
# Multi-stage: build with the toolchain, ship without it.
FROM golang:1.24 AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download                 # cached unless deps change
COPY . .
RUN CGO_ENABLED=0 go build -o /app ./cmd/server

FROM gcr.io/distroless/static:nonroot
COPY --from=build /app /app
USER nonroot
ENTRYPOINT ["/app"]
```

## Interview tips

- The one-hour-to-twenty-minutes question is the best scoring opportunity in the round, and it needs specifics with numbers. Name the levers: parallelise independent stages, cache dependencies and Docker layers, order the Dockerfile so dependency installation is cached above source copying, run only affected tests, use larger or more agents, and move integration tests off the blocking path. Then say which one produced the biggest win and roughly how much. See [reducing Docker image size and build time](../docker/how-do-you-reduce-docker-image-size-and-build-time.md).
- "Only for you" is the whole clue in the database question. It rules out the database, the network path, and the Service, and points at something scoped to your identity or session: your credentials or a rotated secret, your IP not on an allowlist, a per-user database grant, your VPN or proxy, a stale local `kubeconfig` context pointing at the wrong namespace or cluster. Say "the fact that it works for others tells me it is not the database" out loud — that reasoning is what is being graded.
- For shared variables across teams, the expected answer is a Jenkins shared library holding common variables and steps, versioned in Git and referenced with `@Library`, plus folder-level properties or credentials for environment-specific values. Say why: copy-pasted variables across dozens of `Jenkinsfile`s cannot be changed once. See [Jenkins shared libraries](../cicd/how-do-you-use-jenkins-shared-libraries.md).
- On variable syntax, distinguish the layers: `environment {}` at pipeline or stage scope, `params.NAME` for build parameters, `${VAR}` interpolation inside double-quoted Groovy strings versus `$VAR` resolved by the shell inside single quotes, and `withCredentials` for anything secret. The single-versus-double-quote distinction is a common follow-up because it is how credentials leak into build logs. See [Jenkins pipelines](../cicd/what-are-jenkins-pipelines.md) and [preventing secret leaks in CI/CD](../cicd/how-do-you-prevent-and-handle-secret-leaks-in-ci-cd-pipelines.md).
- Write the checkout stage with a credentials binding rather than a token in the URL — `git url: ..., credentialsId: 'github-app'`, or `withCredentials` around the clone. Putting a PAT in a visible string is an automatic mark against you.
- Have two real CVEs ready with the version you moved from and to. Log4Shell, a base-image OpenSSL advisory, or a transitive dependency flagged by your scanner all work. What matters is the process you describe: triage by reachability and exposure, patch or pin, rebuild, redeploy, then verify the scanner is clean. See [prioritising vulnerabilities without blocking delivery](../devsecops/how-do-you-prioritise-vulnerabilities-without-blocking-delivery.md).
- Five CVE tools, comfortably: Trivy, Grype, Snyk, Dependabot or Renovate, and OWASP Dependency-Check — with SonarQube and Amazon Inspector as spares. Group them as image scanners, dependency scanners, and platform scanners so the list sounds structured rather than recited. See [SAST, DAST, IAST, and SCA](../devsecops/what-is-the-difference-between-sast-dast-iast-and-sca.md) and [software bill of materials](../devsecops/what-is-a-software-bill-of-materials-sbom.md).
- For logs that stopped, check the boring causes first and say so: the filesystem is full, the log file was rotated and the process still holds the old descriptor, permissions changed, the log level was raised, or the collector rather than the database is what actually broke. Distinguishing "nothing is writing logs" from "logs are written but not shipped" is the key move. See [troubleshooting SSH failures, high CPU, and disk space](../linux-administration/how-do-you-troubleshoot-ssh-failures-high-cpu-and-disk-space-on-linux-servers.md).
- In the multi-stage Dockerfile, say out loud why each line is where it is: dependency manifests copied before source so the layer caches, a build stage discarded at the end, a minimal non-root runtime image. That commentary is the actual answer. See [what a Dockerfile is](../docker/what-is-dockerfile.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)
- [[How do you integrate SonarQube and quality gates into a pipeline?]] (`#458`): [How do you integrate SonarQube and quality gates into a pipeline?](../cicd/how-do-you-integrate-sonarqube-and-quality-gates-into-a-pipeline.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Interview Experience](./README.md) · [All topics](../README.md)
