---
title: "How do you integrate SonarQube and quality gates into a pipeline?"
id: 458
category: "CI/CD"
difficulty: "Intermediate"
tags:
  - devops
  - cicd
  - interview-questions
  - devsecops
  - devops-metrics-and-kpis
---

# How do you integrate SonarQube and quality gates into a pipeline?

**Short answer:** Run the analysis **after the tests produce a coverage report** (Sonar reads coverage; it does not generate it), send the results to the server with the scanner for your build tool, then **wait for the quality gate and fail the build if it fails** - that last step is the one teams skip, which turns Sonar into a dashboard nobody reads. Concretely: `mvn verify` produces JaCoCo output, `mvn sonar:sonar` uploads it with a project key and a token from your secret store, and `waitForQualityGate abortPipeline: true` (Jenkins) or `sonar-scanner -Dsonar.qualitygate.wait=true` blocks until the server has computed the gate. Configure the gate on **new code** rather than the whole codebase - "no new bugs, no new vulnerabilities, coverage on new code above 80%, duplicated lines on new code below 3%" - because a gate on total coverage in a legacy repository is either unreachable or meaningless. And run it on the **pull request**, so the feedback arrives before merge, not after.

## Detail

### Code quality versus code coverage

Interviewers separate these deliberately. **Coverage** is a measurement of your tests: what percentage of lines or branches executed during the test run. **Quality** is a measurement of the code: bugs, vulnerabilities, security hotspots, code smells, duplication, complexity, and maintainability rating. High coverage with terrible quality is common (tests that execute code without asserting anything); good quality with no coverage is also common. Sonar reports both, but it only _computes_ quality - coverage arrives as an imported report from JaCoCo, Cobertura, `coverage.py`, `lcov`, or `opencover`. If coverage shows 0% in Sonar, the almost-certain cause is a missing or mis-pathed report file, not a scanner bug.

### The clean-as-you-code model, and why the gate should target new code

The **default gate ("Sonar way")** is deliberately new-code-focused:

| Condition                                       | Threshold |
| ----------------------------------------------- | --------- |
| New issues (bugs, vulnerabilities, code smells) | 0         |
| Coverage on new code                            | ≥ 80%     |
| Duplicated lines on new code                    | ≤ 3%      |
| Security hotspots reviewed                      | 100%      |

The reasoning is practical: a five-year-old codebase might sit at 20% coverage, and a gate demanding 80% overall blocks everything, so teams disable it. Gating only what the change introduces is achievable on day one and drags the codebase upwards over time. Define the **new code period** (previous version, number of days, or a reference branch) so "new" is unambiguous.

### Where it goes in the pipeline

```text
checkout ─> build ─> unit tests + coverage report ─> SonarQube analysis
                                                        │
                                                   upload to server
                                                        │
                                              server computes the gate
                                                        │
                                   pipeline WAITS ──> pass: continue
                                                  └─> fail: stop, do not publish an image
```

Two ordering rules people get wrong: analysis must come **after** tests (no coverage otherwise), and the gate check must be a **blocking** step. The gate is computed asynchronously on the server, so the scanner returning 0 means "uploaded successfully", not "passed". Without an explicit wait you have a pipeline that always goes green.

### PR analysis versus branch analysis

- **On a pull request**: pass `sonar.pullrequest.key`, `.branch`, and `.base` (or let the CI integration set them). Sonar then analyses only the changed code and posts a decoration on the PR - inline comments plus a pass/fail check that can be a required status check in branch protection. This is where the value is: the developer sees it before merge.
- **On the main branch**: the full analysis that keeps the project's rating, coverage trend, and new-code baseline current.
- The frequent question _"is it better to run on every push or on every pull request?"_ - PR analysis for feedback and enforcement, plus main-branch analysis after merge for the baseline. Running a full scan on every push to every feature branch is expensive and mostly noise; if you do run per-push, scope it and cache.

### Practical configuration

- **Server-side gate, not pipeline-side thresholds.** Define the gate once in SonarQube and let every project inherit it. Encoding thresholds in each `Jenkinsfile` means fifty different standards.
- **Token from a secret store**, scoped to analysis (`Execute Analysis` permission), never a personal admin token in the repo.
- **Correct scanner per stack**: `sonar-maven-plugin` / `sonarqube` Gradle plugin (they know your module layout and coverage paths), `dotnet sonarscanner begin/end` for .NET (the begin/end wrapper is mandatory - a plain CLI scan of a .NET solution produces poor results), and `sonar-scanner` CLI with `sonar-project.properties` for JS/Python/Go.
- **Exclusions with intent**: generated code, vendored dependencies, and migrations should be excluded (`sonar.exclusions`); test code should be declared as tests (`sonar.test.inclusions`), not excluded, or you lose useful analysis. Do not exclude a package because it fails the gate.
- **Cache the scanner and the analysis cache** in CI to keep the step from dominating build time.
- **Editions matter**: branch and PR analysis and some languages require Developer Edition or above; Community Edition analyses only the main branch. SonarCloud/SonarQube Cloud is the hosted option. Knowing this stops you promising something the licence does not include.

### SonarQube is not a security scanner

Sonar finds a class of security-relevant bugs (injection patterns, hardcoded secrets, unsafe deserialisation) - it is SAST-adjacent - but it does **not** cover dependency vulnerabilities, container image CVEs, or IaC misconfiguration. A complete pipeline pairs it with SCA (Snyk, Dependabot, OWASP Dependency-Check), image scanning (Trivy, Grype), IaC scanning (Checkov, tfsec), and secret scanning (gitleaks). Saying that boundary out loud is what distinguishes someone who has built a pipeline from someone who has installed a plugin.

### When a developer asks you to remove the gate because it is slow

This comes up as a scenario question and it is really about judgement. The answer is not "no" and not "yes": find out _why_ it is slow and fix that - run analysis in parallel with other independent stages, scope PR analysis to changed code, cache dependencies and the scanner, move the full scan off the PR path to post-merge or nightly - then, if a genuine emergency needs a bypass, make it an explicit, audited, time-boxed override with an owner and a follow-up, not a silent deletion of the stage. Removing the check without addressing the cause is how quality gates die everywhere.

## Example

```groovy
// Jenkins: analysis after tests, then a BLOCKING gate
pipeline {
  agent { label 'linux' }
  environment { SONAR_TOKEN = credentials('sonar-token') }
  stages {
    stage('Build & test') {
      steps { sh 'mvn -B clean verify' }          // JaCoCo report produced here
      post { always { junit 'target/surefire-reports/*.xml' } }
    }
    stage('SonarQube analysis') {
      steps {
        withSonarQubeEnv('sonar-prod') {           // injects host URL + token
          sh '''mvn -B sonar:sonar \
                 -Dsonar.projectKey=acme_payments \
                 -Dsonar.coverage.jacoco.xmlReportPaths=target/site/jacoco/jacoco.xml \
                 -Dsonar.exclusions=**/generated/**,**/migrations/** \
                 -Dsonar.qualitygate.wait=false'''  // wait handled by the step below
        }
      }
    }
    stage('Quality gate') {
      steps {
        timeout(time: 10, unit: 'MINUTES') {
          // THE step teams omit - without it the pipeline is always green
          waitForQualityGate abortPipeline: true
        }
      }
    }
    stage('Build & push image') {                  // only reached if the gate passed
      steps { sh 'make image push' }
    }
  }
}
```

```yaml
# GitHub Actions: PR decoration plus a blocking gate, no analysis before tests
jobs:
  quality:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 } # Sonar needs full history for new-code detection
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: "21", cache: maven }
      - run: mvn -B verify # tests + coverage FIRST
      - name: SonarQube analysis and gate
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: https://sonar.example.com
        run: |
          mvn -B sonar:sonar \
            -Dsonar.projectKey=acme_payments \
            -Dsonar.coverage.jacoco.xmlReportPaths=target/site/jacoco/jacoco.xml \
            -Dsonar.qualitygate.wait=true \
            -Dsonar.qualitygate.timeout=600
```

```properties
# sonar-project.properties - for the CLI scanner (JS/Python/Go)
sonar.projectKey=acme_web
sonar.sources=src
sonar.tests=src
sonar.test.inclusions=**/*.test.ts,**/*.spec.ts
sonar.exclusions=**/node_modules/**,**/dist/**,**/*.generated.ts
sonar.javascript.lcov.reportPaths=coverage/lcov.info
sonar.python.coverage.reportPaths=coverage.xml
sonar.newCode.referenceBranch=main
```

```bash
# Verify from the outside - useful when "the gate passes but shouldn't"
curl -s -u "$SONAR_TOKEN:" \
  "https://sonar.example.com/api/qualitygates/project_status?projectKey=acme_payments" \
  | jq '.projectStatus | {status, conditions: [.conditions[] | {metricKey, status, actualValue}]}'
# coverage showing 0? the report path is wrong - check the file exists where you said
ls -l target/site/jacoco/jacoco.xml
```

## Interview tips

- Lead with the ordering rule: tests first (they produce coverage), then analysis, then a **blocking** gate check. Then say the thing most candidates miss - the scanner exits 0 on upload, so without an explicit wait the gate never fails a build.
- Distinguish code quality from code coverage crisply, and note that Sonar imports coverage rather than producing it. "0% coverage in Sonar" is a report-path problem.
- Explain the new-code gate and why it beats an absolute threshold on a legacy codebase - achievable on day one, ratchets upwards, does not get disabled. Quote the Sonar way defaults if you can.
- Say the gate lives on the **server** so every project inherits one standard, not in each `Jenkinsfile`.
- Recommend PR analysis with decoration and a required status check for feedback before merge, plus main-branch analysis for the baseline. That answers the every-push-versus-every-PR question directly.
- Mention edition limits (branch/PR analysis needs Developer Edition or SonarCloud) and stack-specific scanners, especially the `dotnet sonarscanner begin/end` wrapper. Both signal hands-on use.
- Draw the boundary: Sonar is not dependency scanning, image scanning, or IaC scanning - name the companions.
- For "a developer wants the slow scan removed", answer with diagnosis and parallelisation first, then a time-boxed audited exception if genuinely needed - never a silent deletion. See [what does a DevSecOps pipeline look like end to end](../devsecops/what-does-a-devsecops-pipeline-look-like-end-to-end.md), [SAST, DAST, IAST, and SCA](../devsecops/what-is-the-difference-between-sast-dast-iast-and-sca.md), [speeding up a slow CI/CD pipeline](./how-do-you-speed-up-a-slow-ci-cd-pipeline.md), and [how do you deal with flaky tests](./how-do-you-deal-with-flaky-tests-in-a-ci-pipeline.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you manage build artefacts with Nexus or Artifactory?]] (`#460`): [How do you manage build artefacts with Nexus or Artifactory?](../devops-tools-and-automation/how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md)
- [[How do you rotate secrets without downtime?]] (`#429`): [How do you rotate secrets without downtime?](../devsecops/how-do-you-rotate-secrets-without-downtime.md)
- [[What do you need to know about Maven as a DevOps engineer?]] (`#461`): [What do you need to know about Maven as a DevOps engineer?](../devops-tools-and-automation/what-do-you-need-to-know-about-maven-as-a-devops-engineer.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
