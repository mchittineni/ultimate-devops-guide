---
title: "What is Bicep and how does it compare to ARM templates?"
id: 203
category: "Azure Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - azure-engineering
  - interview-questions
---

# What is Bicep and how does it compare to ARM templates?

**Short answer:** Bicep is a domain-specific language that transpiles to ARM JSON. Same engine, same API coverage, same deployment semantics - but far less verbose, with real modules, type checking, and automatic dependency inference. For Azure-only infrastructure it has effectively replaced hand-written ARM templates; Terraform remains the choice when you manage more than Azure.

## Detail

| Aspect           | ARM JSON                          | Bicep                                  |
| ---------------- | --------------------------------- | -------------------------------------- |
| Readability      | verbose, heavy expression syntax  | concise, IDE tooling and type checking |
| Dependencies     | manual `dependsOn`                | inferred from references               |
| Modularity       | nested/linked templates           | first-class `module` with registries   |
| State            | none - Azure holds resource state | same                                   |
| API coverage     | day-one                           | day-one (same resource providers)      |
| Loops/conditions | awkward `copy` blocks             | `for` and `if` expressions             |

**No state file, and that matters.** Both Bicep and ARM deploy against Azure's own view of resources, so there is nothing to lock, corrupt, or reconcile. The trade-off is a weaker preview: `what-if` is good but less trustworthy than `terraform plan`, and there is no equivalent of Terraform's dependency graph output.

**Deployment modes are a real hazard.** `Incremental` (the default) leaves resources not present in the template untouched. `Complete` **deletes** anything in the resource group that the template does not declare. Complete mode gives true declarative convergence and is how you eliminate drift, but running it against a resource group containing anything managed elsewhere is a way to cause an outage. Know the difference and always `what-if` first.

**Modules and the registry.** A platform team publishes reviewed modules to an Azure Container Registry (`br:acme.azurecr.io/bicep/modules/webapp:1.2.0`), and application teams reference them by version. Microsoft's Azure Verified Modules provide a maintained, opinionated baseline that saves writing the common ones. This is the same "golden path" idea as Terraform modules or CDK constructs.

**Deployment stacks are the newer capability worth naming:** a stack manages a set of resources as one unit with `denySettings` (blocking out-of-band changes) and a clean delete of everything the stack owns - closing the gap with Terraform's lifecycle management.

**Choosing honestly.** Bicep wins on Azure-only estates, day-one API coverage, and no state to operate. Terraform wins when Azure is one of several providers, when you want the strongest plan/policy gate, or when the team's existing skills and modules are in HCL. Using both for the same resources is the mistake.

## Example

```bicep
targetScope = 'resourceGroup'

@description('Environment short name')
@allowed(['dev', 'test', 'prod'])
param env string
param location string = resourceGroup().location

var tags = { environment: env, owner: 'platform', costCenter: 'cc-4471' }

// Consume a versioned module from the shared registry - the golden path
module plan 'br:acme.azurecr.io/bicep/modules/app-service-plan:1.4.0' = {
  name: 'plan-${env}'
  params: {
    name: 'asp-checkout-${env}-weu'
    location: location
    sku: env == 'prod' ? 'P1v3' : 'B1'
    tags: tags
  }
}

resource site 'Microsoft.Web/sites@2023-12-01' = {
  name: 'app-checkout-${env}-weu'
  location: location
  tags: tags
  identity: { type: 'SystemAssigned' } // no secrets; RBAC to Key Vault instead
  properties: {
    serverFarmId: plan.outputs.id // dependency inferred, no dependsOn needed
    httpsOnly: true
    siteConfig: {
      minTlsVersion: '1.2'
      ftpsState: 'Disabled'
      healthCheckPath: '/healthz'
    }
  }
}

output hostname string = site.properties.defaultHostName
```

```bash
az deployment group what-if --resource-group rg-checkout-prod-weu \
  --template-file main.bicep --parameters env=prod   # always preview first
```

## Interview tips

- "Bicep transpiles to ARM - same engine, better authoring experience" is the one-line answer.
- Incremental versus Complete mode is the trap; volunteering it shows you have deployed for real.
- Expect: "Bicep or Terraform?" - decide by whether Azure is your only provider, and mention module registries either way.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is Cloud Computing?]] (`#21`): [What is Cloud Computing?](../cloud-platforms/what-is-cloud-computing.md)
- [[What are the different types of cloud services?]] (`#25`): [What are the different types of cloud services?](../cloud-platforms/what-are-the-different-types-of-cloud-services.md)
- [[How do you choose a cloud provider for a new workload?]] (`#281`): [How do you choose a cloud provider for a new workload?](../cloud-platforms/how-do-you-choose-a-cloud-provider-for-a-new-workload.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Azure Engineering](./README.md) · [All topics](../README.md)
