---
title: "What do you need to know about Maven as a DevOps engineer?"
id: 461
category: "DevOps Tools and Automation"
difficulty: "Beginner"
tags:
  - devops
  - devops-tools-and-automation
  - interview-questions
  - cicd
---

# What do you need to know about Maven as a DevOps engineer?

**Short answer:** Maven is a **convention-driven build tool** for the JVM: `pom.xml` in the project root declares coordinates (`groupId:artifactId:version`), dependencies, plugins, and modules, and Maven runs a fixed **lifecycle** whose phases execute in order - `validate → compile → test → package → verify → install → deploy`. Running a phase runs every phase before it, which is why `mvn install` compiles, tests, and packages on the way. Dependencies resolve from the **local repository** (`~/.m2/repository`) first, then from the remote repositories configured in the POM or `~/.m2/settings.xml` (in practice your Nexus/Artifactory proxy). For CI purposes the things you actually need are: `mvn -B verify` as the pipeline command (not `install`), the local repository cached or mounted so builds do not re-download the internet, credentials and the repository mirror in `settings.xml` rather than the POM, and `mvn deploy` publishing an immutable versioned artefact to your artefact repository.

## Detail

### The lifecycle, and what each phase gives you

| Phase      | What happens                                                                      | Typical CI relevance                     |
| ---------- | --------------------------------------------------------------------------------- | ---------------------------------------- |
| `validate` | Project structure is correct                                                      |                                          |
| `compile`  | Sources → `target/classes`                                                        |                                          |
| `test`     | **Unit** tests via Surefire; fails the build                                      | Publish `target/surefire-reports/*.xml`  |
| `package`  | Produces the `.jar`/`.war` in `target/`                                           | The artefact                             |
| `verify`   | **Integration** tests via Failsafe, plus checks (JaCoCo coverage, enforcer rules) | **This is the phase CI should run**      |
| `install`  | Copies the artefact into `~/.m2/repository`                                       | Only useful for local multi-module work  |
| `deploy`   | Uploads to the remote repository                                                  | The publish step, on release builds only |

There are three lifecycles: `default` (above), `clean`, and `site`. `mvn clean verify` is the standard CI invocation - clean so nothing stale survives, `verify` so integration tests and coverage gates run. Using `install` in CI is a common smell: it writes to a shared local repository, which creates cross-build interference on a static agent and hides missing dependency declarations.

`mvn install` specifically: runs everything up to and including packaging and verification, then places the artefact in the local repository so other local projects can resolve it. It does **not** talk to your artefact repository - that is `deploy`.

### `pom.xml`: what a DevOps engineer reads in it

- **Coordinates** - `groupId`, `artifactId`, `version`, `packaging`. `1.9.0-SNAPSHOT` is mutable and re-published on every build; `1.9.0` is a release and must never be overwritten.
- **`<dependencies>`** with **scopes** that change what ships: `compile` (default, in the artefact), `provided` (needed to compile, supplied by the container - the classic servlet-API case), `runtime`, `test` (not in the artefact), `system`, `import`. A dependency in the wrong scope is why a JAR is either bloated or broken at runtime.
- **`<dependencyManagement>`** - declares versions **without** adding dependencies, so child modules inherit consistent versions. This is the tag interviewers ask about: it centralises version decisions, and combined with a BOM (`<scope>import</scope>`, e.g. `spring-boot-dependencies`) it aligns dozens of transitive versions at once.
- **`<modules>`** - the multi-module (aggregator) layout; `-pl`/`-am` build a subset and its dependencies, which is how you avoid rebuilding a whole monorepo.
- **`<properties>`** - versions and toggles, overridable from the command line with `-D`.
- **`<build><plugins>`** - Surefire, Failsafe, JaCoCo, Spring Boot repackage, `maven-enforcer-plugin` (ban duplicate/vulnerable versions), `versions-maven-plugin` (bump versions in CI), `maven-release-plugin` or a CI-driven tagging flow.
- **`<profiles>`** - conditional configuration; useful, but beware of profiles that change the artefact's content, which breaks build-once-promote-many.

`pom.xml` lives at the project root, and every module of a multi-module build has its own with a `<parent>` reference.

### Dependency resolution and the two problems it causes

Resolution order is local repository → remote repositories (mirrored to your proxy). Transitive dependencies come in automatically, and conflicts are settled by **nearest definition wins** - the shortest path in the dependency tree, not the highest version. That produces the two recurring CI failures:

1. **A version you did not choose.** `mvn dependency:tree -Dverbose` shows what won and what was omitted; pin it in `dependencyManagement` or exclude the offender.
2. **Non-reproducible builds.** Ranges and `SNAPSHOT` dependencies resolve differently over time. Pin exact versions, and for anything security-relevant use `-Dmaven.repo.local` plus a proxy so you can say precisely what you consumed.

### Making Maven behave in CI

- **`-B` (batch mode)** and `--no-transfer-progress` so logs are readable, plus `-e` when debugging.
- **Cache `~/.m2/repository`** - a BuildKit cache mount, an Actions cache keyed on a hash of the POMs, or a persistent volume. Without it, dependency download dominates every build. Do **not** cache your own `SNAPSHOT`s, or you will resolve a stale one.
- **`mvn -o` (offline)** after a `dependency:go-offline` step gives a hermetic, fast build and catches accidental new dependencies.
- **`settings.xml` holds the mirror and credentials**, injected from the secret store at runtime - never credentials in `pom.xml`, which is committed.
- **`-T 1C`** for parallel module builds, `-pl module -am` to build only what changed in a multi-module repository, and `-Dmaven.test.skip` never in CI (use `-DskipTests` at most, and only for the image-build stage after tests already ran).
- **Publish once**: `mvn deploy` on the release build only, to an immutable release repository, with the version derived from a tag rather than edited by hand.

### Gradle, and being fair about it

Gradle solves the same problem with a programmable DSL (Groovy/Kotlin), incremental tasks, a build cache, and a daemon - typically much faster on large multi-module builds, at the cost of build logic that can become a program nobody understands. Maven's rigidity is its feature: `mvn verify` means the same thing in every Java repository you will ever touch. Say that trade-off rather than picking a side, and mention that in CI the practical difference is mostly caching strategy (`~/.m2` versus `~/.gradle` plus a remote build cache).

## Example

```bash
# The commands that matter in a pipeline
mvn -B clean verify                       # compile, unit + integration tests, coverage gate
mvn -B verify -pl services/api -am        # only this module and its dependencies
mvn -B -T 1C clean verify                 # one thread per CPU core
mvn -B dependency:go-offline              # warm the cache, then build hermetically
mvn -B -o verify                          # offline: no surprise downloads
mvn -B deploy -DskipTests                 # publish (release builds only; tests already ran)

# Diagnosing dependency problems
mvn dependency:tree -Dverbose -Dincludes=com.fasterxml.jackson.core
mvn dependency:analyze                    # declared-but-unused / used-but-undeclared
mvn help:effective-pom                    # what the POM really is after inheritance + profiles
mvn versions:display-dependency-updates
```

```xml
<!-- The three tags that come up most: dependencyManagement, scope, plugins -->
<project>
  <parent>
    <groupId>com.acme</groupId><artifactId>platform-parent</artifactId><version>4.2.0</version>
  </parent>
  <artifactId>payments-api</artifactId>
  <version>1.9.0</version>          <!-- release: immutable once deployed -->

  <dependencyManagement>            <!-- versions only; children inherit consistency -->
    <dependencies>
      <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-dependencies</artifactId>
        <version>3.3.4</version>
        <type>pom</type><scope>import</scope>   <!-- a BOM: aligns dozens of versions -->
      </dependency>
    </dependencies>
  </dependencyManagement>

  <dependencies>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-web</artifactId>  <!-- no version: managed above -->
    </dependency>
    <dependency>
      <groupId>jakarta.servlet</groupId><artifactId>jakarta.servlet-api</artifactId>
      <version>6.0.0</version><scope>provided</scope>   <!-- container supplies it -->
    </dependency>
  </dependencies>

  <build><plugins>
    <plugin>   <!-- coverage report that SonarQube will import -->
      <groupId>org.jacoco</groupId><artifactId>jacoco-maven-plugin</artifactId>
      <version>0.8.12</version>
      <executions>
        <execution><goals><goal>prepare-agent</goal></goals></execution>
        <execution><id>report</id><phase>verify</phase><goals><goal>report</goal></goals></execution>
      </executions>
    </plugin>
  </plugins></build>
</project>
```

```dockerfile
# syntax=docker/dockerfile:1
# The Maven-specific CI optimisation: cache ~/.m2 outside the layer
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /src
COPY pom.xml .
COPY services/api/pom.xml services/api/
RUN --mount=type=cache,target=/root/.m2 mvn -B dependency:go-offline
COPY . .
RUN --mount=type=cache,target=/root/.m2 mvn -B -o verify -DskipTests=false

FROM eclipse-temurin:21-jre-alpine
COPY --from=build /src/services/api/target/api.jar /app/api.jar
ENTRYPOINT ["java","-jar","/app/api.jar"]
```

## Interview tips

- Recite the lifecycle in order and state the rule that running a phase runs everything before it. Then answer the classic directly: `mvn install` builds, tests, packages, and puts the artefact in `~/.m2`; it does **not** publish to your artefact repository - that is `deploy`.
- Say `mvn clean verify` is what CI should run, and explain why `install` in CI is a smell (shared local repository, hidden missing declarations).
- Know where `pom.xml` lives (project root, one per module with a `<parent>`) - it is asked verbatim.
- Explain `dependencyManagement` as versions-without-dependencies and mention BOM imports. That is the "dependency management tag" question answered properly.
- Explain scopes with the `provided` servlet-API example, since scope mistakes are the usual cause of a JAR that runs locally and fails in the container.
- Give the transitive-conflict rule - nearest definition wins, not highest version - and name `mvn dependency:tree -Dverbose` as the diagnostic.
- For "what happens during a build - how does it fetch dependencies?", walk local repository → configured remote → your Nexus/Artifactory mirror, and note that `settings.xml` (not the POM) holds the mirror and credentials.
- Volunteer the CI optimisations: cache `~/.m2` keyed on the POMs, `-B`, `-T 1C`, `-pl -am` for multi-module, and go-offline for hermetic builds. See [how do you manage build artefacts with Nexus or Artifactory](./how-do-you-manage-build-artefacts-with-nexus-or-artifactory.md), [speeding up a slow CI/CD pipeline](../cicd/how-do-you-speed-up-a-slow-ci-cd-pipeline.md), [integrating SonarQube and quality gates](../cicd/how-do-you-integrate-sonarqube-and-quality-gates-into-a-pipeline.md), and [how does Docker layer caching work](../docker/how-does-docker-layer-caching-work.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[What is CI/CD Pipeline?]] (`#16`): [What is CI/CD Pipeline?](../cicd/what-is-ci-cd-pipeline.md)
- [[What is Jenkins?]] (`#17`): [What is Jenkins?](../cicd/what-is-jenkins.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Tools and Automation](./README.md) · [All topics](../README.md)
