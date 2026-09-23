---
title: "What is Pipeline as Code and how do modern CI systems validate and isolate pipeline runs?"
id: 532
category: "CI/CD"
difficulty: "Beginner"
tags:
  - devops
  - interview-questions
  - cicd
  - pipeline-as-code
  - security
  - github-actions
quiz:
  stem: "What is the primary operational flaw of managing CI pipelines through manual GUI configuration rather than Pipeline as Code?"
  options:
    - "GUI pipelines cannot compile compiled programming languages like C++ or Go"
    - "Pipeline changes are unversioned, lack code review audit trails, and drift silently between environments"
    - "GUI pipelines cannot connect to GitHub or GitLab"
    - "Pipeline as Code requires proprietary paid hardware"
  answer: 2
  explanation: "Manual GUI configurations cannot be reviewed in pull requests, tested on feature branches, or rolled back via git history, making changes error-prone and untraceable."
---

# What is Pipeline as Code and how do modern CI systems validate and isolate pipeline runs?

**Short answer:** Pipeline as Code stores pipeline definitions in version-controlled manifests alongside application code, with modern runners using ephemeral containers, isolated virtual machines, and restricted OIDC tokens to prevent cross-job contamination.

## Detail

Legacy CI setups (freestyle Jenkins jobs, for example) configured builds via GUI checkboxes and hand-edited controller settings, causing unversioned configuration drift and fragile infrastructure.

### Modern Pipeline as Code Principles

1. **Version Controlled & Reviewed**: Changes to build workflows (`.github/workflows/*.yml`, `.gitlab-ci.yml`) go through pull requests, linting, and branch protection.
2. **Ephemeral Isolated Runners**: Each job spawns a fresh VM or unprivileged Kubernetes pod that is destroyed upon job completion. No artifacts, environment variables, or rogue background processes persist to pollute subsequent runs.
3. **Secret Isolation & Least Privilege**:
   - Workflows only receive secrets explicitly requested.
   - Runners use Short-Lived OpenID Connect (OIDC) federated credentials rather than long-lived static AWS/GCP access keys.

### Validating pipeline definitions before they run

Because the pipeline is code, it can be linted and tested like code:

- **Schema and semantic linting**: `actionlint` for GitHub Actions (catches bad expressions, unknown inputs, and shell issues via shellcheck), GitLab's CI Lint (UI or `POST /projects/:id/ci/lint`) to validate `.gitlab-ci.yml` including `include:` expansion, and Jenkins' declarative linter (`jenkins-cli declarative-linter < Jenkinsfile`).
- **Policy checks**: scanners such as `zizmor` or OpenSSF Scorecard flag risky patterns - unpinned actions, `pull_request_target` checking out PR code, overly broad `permissions`.
- **Protected definitions**: CODEOWNERS on `.github/workflows/`, and for privileged pipelines, require that the definition comes from the default branch (for example GitLab pipeline execution policies, which replace the deprecated compliance pipelines, or required workflows in GitHub rulesets) so a PR cannot rewrite the pipeline that judges it.

The trade-off: pipeline-as-code means anyone who can edit the file can change what runs with the pipeline's credentials. Review, CODEOWNERS, and least-privilege tokens are what keep that power in check.

## Example

```yaml
# .github/workflows/lint-workflows.yml - validate pipeline changes in the PR itself
name: lint-workflows
on:
  pull_request:
    paths: [".github/workflows/**"]
permissions:
  contents: read
jobs:
  actionlint:
    runs-on: ubuntu-latest # fresh VM per job, destroyed afterwards
    steps:
      - uses: actions/checkout@v7
        with:
          persist-credentials: false
      - name: Run actionlint
        run: |
          bash <(curl -sSfL https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash)
          ./actionlint -color
```

```bash
# GitLab: validate .gitlab-ci.yml (with includes expanded) before pushing
curl -s --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  --header "Content-Type: application/json" \
  --data "$(jq -n --rawfile c .gitlab-ci.yml '{content: $c}')" \
  "https://gitlab.example.com/api/v4/projects/42/ci/lint" | jq '.valid, .errors'
```

## Interview tips

- Define pipeline as code by its benefits: review, history, rollback, and branch-level testing of pipeline changes.
- Cover validation (linters, CI Lint API, declarative linter) and isolation (ephemeral runners, scoped secrets, OIDC) - the question asks for both.
- Name the risk that comes with it: whoever edits the pipeline file controls its credentials, so protect workflow directories with CODEOWNERS and keep privileged pipelines on protected branches.
- Likely follow-up: "how do you stop a PR from modifying the pipeline that validates it?" - required/compliance pipelines sourced from a protected location, plus secrets that only exist in protected environments.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is the difference between Continuous Delivery and Continuous Deployment?]] (`#511`): [What is the difference between Continuous Delivery and Continuous Deployment?](../core-devops-concepts/what-is-the-difference-between-continuous-delivery-and-continuous-deployment.md)
- [[How do you troubleshoot a GitOps pipeline that will not sync?]] (`#428`): [How do you troubleshoot a GitOps pipeline that will not sync?](../devops-tools-and-automation/how-do-you-troubleshoot-a-gitops-pipeline-that-will-not-sync.md)
- [[What is HashiCorp Vault and how does dynamic secret generation eliminate static credentials?]] (`#631`): [What is HashiCorp Vault and how does dynamic secret generation eliminate static credentials?](../devops-tools-and-automation/what-is-hashicorp-vault-and-how-does-dynamic-secret-generation-eliminate-static-credentials.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to CI/CD](./README.md) · [All topics](../README.md)
