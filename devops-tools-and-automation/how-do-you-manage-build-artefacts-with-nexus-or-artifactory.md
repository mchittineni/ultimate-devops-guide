---
title: "How do you manage build artefacts with Nexus or Artifactory?"
id: 460
category: "DevOps Tools and Automation"
difficulty: "Intermediate"
tags:
  - devops
  - devops-tools-and-automation
  - interview-questions
  - cicd
  - devsecops
---

# How do you manage build artefacts with Nexus or Artifactory?

**Short answer:** An artefact repository is the system of record for everything your build produces and consumes. Both Nexus Repository and JFrog Artifactory organise it the same way, with three repository types: **hosted** (your own artefacts - releases and snapshots), **remote/proxy** (a caching pull-through of a public registry such as Maven Central, npm, or Docker Hub), and **group/virtual** (one URL that resolves across several repositories, so clients have a single endpoint). The operating rules that matter: **build once, publish an immutable versioned artefact, and promote that same artefact between environments** rather than rebuilding per stage; keep **release repositories immutable** while snapshots are mutable and aggressively cleaned; proxy every public registry so builds do not depend on the internet or on Docker Hub rate limits; and put scanning (Xray, or Trivy/Grype in the pipeline) plus retention policies on top, because an unmanaged repository grows without bound and becomes the place vulnerable dependencies hide.

## Detail

### The three repository types

| Type                | What it is                                     | Example use                                                                             |
| ------------------- | ---------------------------------------------- | --------------------------------------------------------------------------------------- |
| **Hosted**          | Storage you write to                           | `maven-releases`, `maven-snapshots`, `docker-internal`, `npm-private`, `raw-installers` |
| **Remote (proxy)**  | Cache in front of an upstream registry         | `maven-central`, `npm-registry`, `docker-hub`, `pypi`, `nuget.org`                      |
| **Group (virtual)** | Aggregates several repositories behind one URL | `maven-all` = releases + snapshots + central; clients configure one URL                 |

Ordering inside a group matters: put hosted repositories **before** proxies so an internal artefact wins over a same-named public one - the basic mitigation for **dependency confusion** attacks, alongside scoping your namespaces and refusing to resolve internal package names from public registries.

Both products are multi-format: Maven, npm, PyPI, NuGet, Go, Helm, Docker/OCI, Debian/RPM, and generic "raw". One system for every ecosystem is the main argument for having one at all.

### Why proxy public registries

- **Build reliability** - Maven Central or Docker Hub having a bad day stops being your outage.
- **Rate limits** - anonymous Docker Hub pulls are throttled; a proxy makes it one pull per artefact per repository instead of one per build.
- **Speed** - the cache is in your region, next to your runners.
- **Visibility and control** - you get an inventory of every external dependency you consume, and a single place to block a compromised version.
- **Air-gapped or regulated environments** - the proxy (or an offline import) is the only path in.

### Releases versus snapshots, and immutability

`1.9.0` is a release: published once, never overwritten, and safe to reference in a deployment. `1.9.0-SNAPSHOT` is a moving target that gets a new timestamped build on every publish. Configure `maven-releases` to reject redeployment (Nexus "Disable redeploy") so nobody can change what `1.9.0` means after it has been tested - that single setting prevents a whole class of "the artefact in prod is not the artefact we tested" incidents. Snapshots need a retention policy (keep N per version, delete after X days) or they will consume most of your storage.

For containers the equivalent discipline is **deploying by digest** (`registry.example.com/api@sha256:...`) rather than a mutable tag, with immutable tag rules enabled where the registry supports it.

### Build once, promote

```text
CI build  ──> publish api:1.9.0 (+ SBOM, + signature) to docker-staging
                       │
              scan / integration tests / approval
                       │
                       └── promote (copy/move, same digest) ──> docker-prod
                                                                    │
                                     dev / staging / prod all deploy THIS digest
```

Promotion is a metadata operation - copy or move the same bits between repositories, or add a property/label - never a rebuild. Environment differences live in configuration, not in a differently-compiled artefact. This is what makes "it worked in staging" a diagnosable statement.

Artifactory adds **build info** (the build's name, number, VCS revision, dependencies, and environment) captured by the JFrog CLI, which gives you the dependency graph per build and makes "which builds contain this vulnerable library?" a query. That traceability is the strongest reason teams choose it over a plain registry.

### Security layer

- **Xray** (Artifactory) or **IQ Server** (Nexus) scan artefacts and their transitive dependencies continuously, can **block downloads** of a known-bad version at the repository level, and enforce licence policy. In the pipeline, pair with Trivy/Grype for images and an SCA tool for source dependencies. The frequently-asked distinction: Xray scans what is _in the repository_ (including things built months ago, rescanned when a new CVE lands); a pipeline scanner checks what you are building _now_. You want both.
- **Authentication and permissions**: SSO/LDAP, per-repository read/write/delete, service accounts per pipeline with deploy-only rights. Never give CI delete permission on a release repository.
- **Signing and provenance**: publish an SBOM and a signature (cosign for OCI, GPG for Maven/RPM) alongside the artefact and verify at deploy or admission time.
- **Retention and cleanup**: policies by age, download count, and count-per-version; unreferenced Docker layers reclaimed by garbage collection. Storage growth is the most common operational complaint and the easiest to fix with policy.

### GitHub repository versus artefact repository

A frequently-asked comparison. Git holds **source** - text, diffed, branched, reviewed, history preserved forever. An artefact repository holds **binaries** - compiled, immutable, versioned, checksum-addressed, cleaned up on a retention policy. Storing binaries in Git bloats clones and defeats diffing; storing source in an artefact repository loses everything Git is for. `.git` LFS is a partial exception for large assets, not a replacement.

### Running it well

Both products are stateful: plan for storage growth (object storage backends are the norm now), back up the blob store **and** the metadata database together, keep them consistent, and rehearse a restore. Put a CDN or regional replicas in front of it for geographically distributed teams, and monitor storage, GC runs, upstream proxy health, and download latency - because when the artefact repository is slow, every pipeline in the company is slow.

## Example

```xml
<!-- Maven: one group URL for reads, explicit hosted repos for writes -->
<settings>
  <mirrors>
    <mirror>
      <id>nexus</id>
      <mirrorOf>*</mirrorOf>  <!-- everything resolves through the proxy -->
      <url>https://nexus.example.com/repository/maven-all/</url>
    </mirror>
  </mirrors>
  <servers>
    <server><id>maven-releases</id><username>${env.NEXUS_USER}</username>
            <password>${env.NEXUS_TOKEN}</password></server>
  </servers>
</settings>
```

```bash
# npm, pip, Docker - the same pattern, one endpoint each
npm config set registry https://nexus.example.com/repository/npm-all/
npm config set @acme:registry https://nexus.example.com/repository/npm-private/  # scope internal
pip config set global.index-url https://nexus.example.com/repository/pypi-all/simple
docker login registry.example.com   # a Docker-format repository in Nexus/Artifactory
```

```bash
# Build once, capture build info, scan, then PROMOTE the same digest
jf rt docker-push registry.example.com/docker-staging/api:1.9.0 \
  docker-staging --build-name=api --build-number="$CI_BUILD"
jf rt build-collect-env api "$CI_BUILD"
jf rt build-publish api "$CI_BUILD"           # dependency graph + VCS revision recorded

jf xr build-scan api "$CI_BUILD" --fail=true  # block on policy violations

# promotion is metadata, not a rebuild
jf rt build-promote api "$CI_BUILD" docker-prod --status=Released --copy=true

DIGEST=$(crane digest registry.example.com/docker-prod/api:1.9.0)
helm upgrade --install api ./chart --set image.digest="$DIGEST"   # deploy by digest
```

```bash
# Nexus equivalents and hygiene checks
curl -u "$U:$T" -X POST "https://nexus.example.com/service/rest/v1/components?repository=raw-installers" \
  -F "raw.directory=/tools" -F "raw.asset1=@tool-1.9.0.tgz" -F "raw.asset1.filename=tool-1.9.0.tgz"

# is a release repository actually immutable?
curl -s -u "$U:$T" "https://nexus.example.com/service/rest/v1/repositories/maven/hosted/maven-releases" \
  | jq '.storage.writePolicy'          # expect: ALLOW_ONCE

# where is the storage going?
curl -s -u "$U:$T" "https://nexus.example.com/service/rest/v1/status/check" | jq .
```

## Interview tips

- Name the three repository types - hosted, remote/proxy, group/virtual - and give an example of each. That is the exact question ("what repository types does it have?") and answering it crisply sets the tone.
- Volunteer the group-ordering detail: hosted before proxy, so internal artefacts win, and connect it to dependency confusion. Very few candidates make that link.
- State the release-versus-snapshot rule and the immutability setting that enforces it. Then extend it to containers: deploy by digest, not by a mutable tag.
- Say "build once, promote the same artefact" and explain that promotion is a metadata operation. It is the core practice the question is really about.
- Give three concrete reasons to proxy public registries - reliability, Docker Hub rate limits, and an inventory of everything you consume. The rate-limit answer always lands.
- Distinguish repository scanning (Xray/IQ, continuous, catches CVEs published after the build) from pipeline scanning (this build, now). Recommend both.
- Answer the Git-versus-artefact-repository comparison in terms of source versus binaries, diffing versus checksums, permanent history versus retention policy.
- Mention operational reality: storage growth needs retention policies and GC, and backups must cover blobs and metadata together. See [how do you consolidate a sprawling DevOps toolchain](./how-do-you-consolidate-a-sprawling-devops-toolchain.md), [what is a Software Bill of Materials](../devsecops/what-is-a-software-bill-of-materials-sbom.md), [signing and verifying container images](../devsecops/how-do-you-sign-and-verify-container-images.md), and [promoting a release across dev, staging, and production](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Tools and Automation](./README.md) · [All topics](../README.md)
