---
title: "How do you build a CI/CD pipeline in Azure DevOps?"
id: 485
category: "Azure Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - azure-engineering
  - interview-questions
  - cicd
  - devsecops
---

# How do you build a CI/CD pipeline in Azure DevOps?

**Short answer:** Use a **YAML pipeline** committed to the repository - `azure-pipelines.yml` with `trigger`, `pool`, `variables`, and `stages → jobs → steps`. Structure it as a build stage that produces a versioned artefact (or pushes an image to ACR) and then one deploy stage per environment, each targeting an **Environment** object so you get **approvals, gates, and deployment history** in one place. Secrets come from a **variable group linked to Azure Key Vault**, and connections to Azure come from a **service connection using workload identity federation** rather than a service principal secret. Agents are either **Microsoft-hosted** (clean VM per job, no maintenance, no private network access) or **self-hosted** (your VMs or a container/Kubernetes pool - needed when the pipeline must reach private endpoints or you want caching and bigger machines). The reason YAML over the classic editor: the pipeline is versioned with the code, reviewable in a pull request, branch-aware, and templatable across repositories - none of which is true of a UI-defined classic pipeline.

## Detail

### YAML versus classic - the question that always comes up

|                                 | YAML pipeline                                  | Classic (UI) pipeline                  |
| ------------------------------- | ---------------------------------------------- | -------------------------------------- |
| Definition lives in             | The repository, versioned with the code        | The Azure DevOps project database      |
| Code review                     | Yes - it is a pull request                     | No                                     |
| Branch-aware                    | Each branch can have its own version           | One definition for all branches        |
| Templates and reuse             | `extends` and `template` across repositories   | Task groups only                       |
| Rollback of the pipeline itself | `git revert`                                   | Manual history in the UI               |
| Deleted by accident             | Recoverable from Git                           | Needs an audit-log restore             |
| Release-specific features       | Environments, approvals, gates (all available) | Classic Release has the older gates UI |

That last row answers a related question - _"a team member deleted the pipeline; how do you recreate it and prevent it recurring?"_ With YAML the definition is in the repository, so recreating it is pointing a new pipeline at the existing file; prevention is branch protection on the file plus restricting who can delete pipeline definitions. With a classic pipeline you are relying on the audit log and someone's memory, which is the strongest practical argument for YAML.

### Structure: stages, jobs, steps

```text
pipeline
└── stage (Build)                     -> a boundary with its own approvals/conditions
    └── job (linux)                   -> runs on one agent; jobs in a stage run in PARALLEL
        └── step (task or script)     -> runs sequentially within the job
└── stage (Deploy_Dev)  dependsOn: Build
└── stage (Deploy_Prod) dependsOn: Deploy_Dev, condition: succeeded()
```

Jobs within a stage run **in parallel** by default (bounded by your parallel-job licences), which is the answer to "can you run multiple jobs in parallel from a single pipeline?" - yes, and you can also use a **matrix** strategy to fan one job across configurations, or `dependsOn` to serialise where needed. A **deployment job** (`deployment:` with a `strategy:`) is the special kind that targets an Environment and gives you `runOnce`, `rolling`, or `canary` strategies with `preDeploy`/`deploy`/`routeTraffic`/`postRouteTraffic`/`on: failure` hooks.

### Variables, variable groups, and Key Vault

- **Inline `variables:`** for non-secret pipeline values.
- **Variable groups** (Library) for values shared across pipelines, scoped and permissioned - the answer to "what is a variable group?" and to "how do you manage shared variables when every team wants them?" A group can be linked to a **Key Vault**, so secrets are fetched at run time and never stored in Azure DevOps.
- **Secret variables** are masked in logs and not passed to scripts as environment variables automatically - you must map them explicitly with `env:`, which is a common stumbling block.
- **Runtime parameters** (`parameters:`) are typed, appear in the run dialogue, and can drive template expansion - stronger than variables for anything that changes the pipeline's shape.
- **Output variables** pass values between jobs and stages: `echo "##vso[task.setvariable variable=tag;isOutput=true]$SHA"` in a job, then reference `dependencies.<Job>.outputs['<step>.tag']` in the next. That syntax is asked directly ("how do you reference a variable output from a previous stage?").
- **Secure files** for certificates and keystores, and **service connections** for anything that authenticates outwards.

### Environments, approvals, and gates

An **Environment** is the deployment target abstraction (a Kubernetes namespace, a VM resource group, or just a logical name). Attaching a deployment job to an environment gives you: **approval checks** (named approvers, with a timeout), **branch control** (only `main` may deploy here), **business hours** checks, **Azure Monitor alert gates** (block if an alert is firing), **invoke REST API** gates for a change-management system, and **exclusive lock** so two runs cannot deploy at once. Deployment history per environment is what auditors ask for.

That is also how you answer the scenario _"the production pipeline is blocked on missing approvals and the stakeholders are unreachable"_: the correct action is to follow the documented break-glass process - an on-call approver group rather than a single person, with the emergency approval recorded - not to bypass the check. Then fix the design: approver **groups**, timeouts with escalation, and business-hours awareness so this stops recurring.

### Service connections: federated, not secrets

A **service connection** is how the pipeline authenticates to Azure, ACR, Kubernetes, or a third party. Historically it held a **service principal client secret** that expired every year and broke deployments at the worst moment. Use **workload identity federation** instead: the connection trusts Azure DevOps as an OIDC issuer for a specific project and pipeline, so there is no secret to rotate and no secret to leak. Scope each connection to a subscription or resource group, restrict it to specific pipelines, and require approval for use in others. That is also the answer to "how are authentication and networking established between a pipeline and Key Vault?" - a federated service connection with an RBAC role assignment on the vault, and, if the vault is private, a self-hosted agent inside the network or a private endpoint the agent can reach.

### Agents

|                        | Microsoft-hosted                   | Self-hosted                                       |
| ---------------------- | ---------------------------------- | ------------------------------------------------- |
| Maintenance            | None                               | Yours (OS, tools, disk)                           |
| State between jobs     | **Clean VM every job**             | Persists unless you clean it                      |
| Private network access | No                                 | **Yes** - the reason most enterprises need them   |
| Caching                | Pipeline caching only              | Local caches, warm dependencies                   |
| Cost                   | Free minutes then per-parallel-job | Your compute, plus a cheaper parallel-job licence |
| Speed                  | Fixed size, cold start             | Bigger machines, warm caches                      |

Self-hosted agents in a **Kubernetes** or container pool give you clean-per-job isolation with private network access - the best of both. Whatever you choose, keep them ephemeral where possible and never run a self-hosted agent that a fork's pull request can reach.

### The rest of the toolchain

- **Azure Artifacts** for packages (NuGet, npm, Maven, Python, Universal) with upstream sources acting as a pull-through proxy - the answer to "what is Azure Artifacts?" and where CI output that is a _package_ belongs.
- **Build artefacts versus pipeline artefacts**: pipeline artefacts are the modern, faster mechanism (backed by different storage, better for large files and cross-stage handoff); build artefacts are the legacy path. Prefer `PublishPipelineArtifact`.
- **Azure Boards** for work items, linked automatically to commits and builds - which is where the traceability from work item to deployment comes from.
- **Deployment groups** (classic) for agent-based deployment to a set of VMs; environments with VM resources are the YAML equivalent.
- **Pipeline caching** (`Cache@2`) keyed on a lockfile hash for dependency restore.
- **Templates** in a shared repository, consumed with `extends:` - and note that an `extends` template can **enforce** steps a consumer cannot remove, which is how a platform team guarantees a security scan runs in every pipeline.

### Templating for fifty applications

The "one reusable pipeline for 50 applications" question is answered with templates: a shared repository holding `templates/build-deploy.yml` with typed `parameters`, consumed by each application's `azure-pipelines.yml` in a few lines, tagged and versioned so upgrades are deliberate. Use `extends` for the enforcing outer shape and `template` includes for reusable step blocks, and keep the parameter surface small.

## Example

```yaml
# azure-pipelines.yml - build once, deploy per environment, approvals on the environment
trigger:
  branches: { include: [main] }
  paths: { include: ["services/payments/*"] } # monorepo: only build what changed
pr:
  branches: { include: [main] }

parameters:
  - name: deployToProd
    type: boolean
    default: true

variables:
  - group: payments-common # variable group (Library)
  - group: payments-kv # variable group LINKED TO KEY VAULT: secrets fetched at run time
  - name: imageRepo
    value: payments

stages:
  - stage: Build
    jobs:
      - job: build
        pool: { vmImage: ubuntu-24.04 } # Microsoft-hosted: clean VM per job
        steps:
          - task: Cache@2
            inputs:
              key: 'maven | "$(Agent.OS)" | **/pom.xml'
              path: $(HOME)/.m2/repository
          - script: mvn -B verify
            displayName: Build and test
          - task: PublishTestResults@2
            inputs: { testResultsFiles: "**/surefire-reports/TEST-*.xml" }
            condition: always()
          - task: Docker@2
            inputs:
              containerRegistry: acr-federated # service connection (workload identity)
              repository: $(imageRepo)
              command: buildAndPush
              tags: $(Build.SourceVersion)
          - script: echo "##vso[task.setvariable variable=tag;isOutput=true]$(Build.SourceVersion)"
            name: meta # output variable, consumed by later stages

  - stage: Deploy_Dev
    dependsOn: Build
    variables:
      tag: $[ stageDependencies.Build.build.outputs['meta.tag'] ] # cross-stage reference
    jobs:
      - deployment: dev
        environment: payments-dev # Environment object: history + checks
        pool: { vmImage: ubuntu-24.04 }
        strategy:
          runOnce:
            deploy:
              steps:
                - task: HelmDeploy@0
                  inputs:
                    connectionType: Kubernetes Service Connection
                    kubernetesServiceConnection: aks-dev
                    command: upgrade
                    chartType: FilePath
                    chartPath: charts/payments
                    arguments: --install --atomic --set image.tag=$(tag)

  - stage: Deploy_Prod
    dependsOn: Deploy_Dev
    condition: and(succeeded(), eq(${{ parameters.deployToProd }}, true))
    jobs:
      - deployment: prod
        environment: payments-prod # approvals, branch control, exclusive lock live HERE
        pool: { name: self-hosted-linux } # self-hosted: reaches the private AKS endpoint
        strategy:
          canary:
            increments: [10, 50]
            deploy:
              steps:
                - template: templates/deploy-canary.yml
                  parameters: { tag: $(tag) }
            on:
              failure:
                steps:
                  - script: helm rollback payments --wait
```

```yaml
# Secret handling: masked variables are NOT automatically in the script environment
- script: |
    curl -sS -H "Authorization: Bearer $TOKEN" https://api.example.com/deploy
  env:
    TOKEN: $(kv-api-token) # explicit mapping - required for secret variables
  displayName: Notify deployment API
```

```yaml
# A platform-owned template that consumers cannot strip steps out of
# templates/secure-pipeline.yml (in a shared repository, tagged v3)
parameters:
  - name: service
    type: string
  - name: buildSteps
    type: stepList
    default: []
stages:
  - stage: Build
    jobs:
      - job: build
        steps:
          - ${{ parameters.buildSteps }} # the consumer's steps
          - task: CredScan@3 # enforced: the consumer cannot remove these
          - task: SdtReport@2

# consumer repository - five lines, and every guardrail is inherited
# extends:
#   template: templates/secure-pipeline.yml@platform
#   parameters:
#     service: payments
#     buildSteps: [ { script: mvn -B verify } ]
```

```bash
# Useful CLI operations
az pipelines run --name payments --branch main
az pipelines runs show --id 4412 --query '[status,result,finishTime]'
az pipelines variable-group list --project acme --query '[].[id,name,type]' -o table
# who approved the last production deployment? (audit question)
az devops invoke --area distributedtask --resource environmentdeploymentrecords \
  --route-parameters project=acme environmentId=7 --api-version 7.1-preview
```

## Interview tips

- Recommend YAML and justify it in one line: the pipeline is versioned with the code, reviewable in a pull request, branch-aware, and templatable. Then give the deleted-pipeline consequence - YAML is recoverable from Git, a classic definition is not.
- Get the hierarchy right and note that **jobs in a stage run in parallel** while steps in a job are sequential. That answers "can more than two stages/jobs run at once?" correctly.
- Name the three secret mechanisms and their order of preference: variable group linked to **Key Vault**, secure files, and inline secret variables. Add the gotcha that secret variables must be mapped with `env:` to reach a script.
- Explain **Environments** as where approvals, branch control, gates, and deployment history live - not as a folder name. Then answer the unreachable-approver scenario with a break-glass on-call approver **group** and a recorded emergency approval, plus fixing the design afterwards.
- Recommend **workload identity federation** on service connections over a service principal secret, and say why: nothing to rotate, nothing to leak, and no annual expiry outage.
- Compare hosted and self-hosted agents on the axis that actually decides it - private network access - and mention Kubernetes-based self-hosted pools as clean-per-job with private reach.
- Know the output-variable syntax for passing values between stages; it is asked verbatim.
- Prefer **pipeline artefacts** over build artefacts and be able to say why (faster, better for large files and cross-stage handoff).
- For fifty applications, answer with a shared, versioned template repository consumed via `extends`, and mention that an `extends` template can enforce steps a consumer cannot remove. See [how do you scale CI/CD across many services and teams](../cicd/how-do-you-scale-ci-cd-across-many-services-and-teams.md), [consuming Azure Key Vault secrets from AKS and Azure Pipelines](./how-do-you-consume-azure-key-vault-secrets-from-aks-and-azure-pipelines.md), [architecting an end-to-end production DevOps project on Azure](./how-do-you-architect-an-end-to-end-production-devops-project-on-azure.md), and [promoting a release across dev, staging, and production](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md).

---

[⬅ Back to Azure Engineering](./README.md) · [All topics](../README.md)
