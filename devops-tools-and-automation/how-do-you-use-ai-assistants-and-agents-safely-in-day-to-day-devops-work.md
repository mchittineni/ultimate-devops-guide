---
title: "How do you use AI assistants and agents safely in day-to-day DevOps work?"
id: 804
category: "DevOps Tools and Automation"
difficulty: "Intermediate"
tags:
  - devops
  - devops-tools-and-automation
  - interview-questions
  - ai-assisted-development
  - llm
  - mcp
  - least-privilege
quiz:
  stem: "Your team pilots an AI agent connected to the production EKS cluster through an MCP server. Which setup is the safest starting point?"
  options:
    - "Bind the agent's ServiceAccount to cluster-admin so it can fix incidents without waiting for a human"
    - "Give the agent a read-only identity (for example the built-in view ClusterRole, which excludes Secrets) and route any change through a pull request and the normal GitOps review"
    - "Let the agent run kubectl with an engineer's personal kubeconfig so actions are attributed to a person"
    - "Allow write access but tell the model in its system prompt never to delete anything"
  answer: 2
  explanation: "Start with least privilege: read-only access the agent can use for diagnosis, and every state change going through the same PR, plan and approval gates as human changes. Prompt instructions are not a security control, and shared personal credentials destroy the audit trail."
---

# How do you use AI assistants and agents safely in day-to-day DevOps work?

**Short answer:** Use AI where it is fast and checkable - scaffolding Terraform and Helm, explaining errors and logs, drafting runbooks and tests, triaging failed pipelines - and keep judgment and accountability with engineers. The safety comes from the same gates you apply to human work: generated code goes through pull requests, `terraform plan`, linters, policy checks and tests; agents connected to real systems (often through **MCP** servers) start with **read-only, least-privilege identities**; every state change is human-approved and audited; and no secrets or customer data go into prompts outside approved tools.

## Detail

**Where AI genuinely helps.**

- **Scaffolding and refactoring** - a new Terraform module modelled on an existing one, Helm values for another environment, a GitHub Actions workflow, a Python script for a one-off migration.
- **Explaining** - an unfamiliar error, a 300-line stack trace, a Kubernetes event stream, an IAM policy.
- **Triage** - summarising a failed CI job's log tail into a likely cause, or condensing an incident channel into a timeline.
- **Documentation** - runbooks, READMEs, architecture decision records, postmortem drafts.
- **Review** - a second pair of eyes on a diff, flagging missing timeouts or over-broad IAM.

The pattern is the same throughout: the output is cheap to verify. Experienced engineers gain the most, because they can spot when it is wrong.

**Where it goes wrong.**

- **Confident hallucination** - invented provider arguments, non-existent CLI flags, deprecated APIs, or package names that do not exist (which attackers can register, so a hallucinated dependency becomes a supply-chain risk).
- **Data leakage** - pasting secrets, account IDs, customer data or internal architecture into tools the company has not approved.
- **Over-privileged agents** - an agent with write access to a cluster or cloud account can do in seconds what a mistaken engineer does in minutes, and it is non-deterministic.
- **Prompt injection** - an agent that reads logs, issues, web pages or pull request text can be steered by instructions hidden in that content. Treat everything an agent reads as untrusted input.

**Agents and MCP.** The Model Context Protocol is an open standard for connecting AI applications to tools and data: an MCP server exposes operations (query a cluster, read CloudWatch metrics, search Grafana, open a pull request) that an agent can call. That makes agents useful during incidents and dangerous if scoped badly. The controls:

1. **Identity per agent**, never an engineer's personal credentials, so actions are attributable.
2. **Read-only first.** In Kubernetes, the built-in `view` ClusterRole allows reading most objects but not Secrets. In AWS, prefer a narrowly scoped custom policy or `ViewOnlyAccess` over `ReadOnlyAccess`, which can also read data such as S3 objects.
3. **Writes go through the normal path.** The agent proposes a change as a pull request; CI runs `terraform plan`, policy checks and tests; a human approves; Argo CD or the pipeline applies it. No direct `kubectl apply` or `terraform apply` by the agent.
4. **Human approval for anything destructive or irreversible**, enforced by the tool configuration, not by instructions in a prompt.
5. **Audit** - log every tool call the agent makes, alongside CloudTrail and Kubernetes audit logs.

**Verification is not optional.** Treat AI output as a draft from a fast but unreliable colleague: `terraform validate`, `tflint`, Checkov or similar, a reviewed plan, tests, and checking arguments against the official provider or API documentation. Review IAM policies and network rules line by line yourself.

**Policy and measurement.** Use the tools your organisation has approved, follow its data-handling rules, and measure value with something concrete - time to triage a failed pipeline, hours saved on a module, incident timeline accuracy - rather than impressions.

## Example

```yaml
# A read-only identity for an AI agent / MCP server inside the cluster.
# The built-in "view" ClusterRole reads most resources but NOT Secrets.
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ai-agent-readonly
  namespace: ops-agents
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: ai-agent-view
subjects:
  - kind: ServiceAccount
    name: ai-agent-readonly
    namespace: ops-agents
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: view
```

```bash
# Prove the boundary before connecting anything to it
SA=system:serviceaccount:ops-agents:ai-agent-readonly
kubectl auth can-i list pods -A --as="$SA"            # yes
kubectl auth can-i get secrets -n payments --as="$SA" # no
kubectl auth can-i delete pods -n payments --as="$SA" # no
kubectl auth can-i patch deployments -A --as="$SA"    # no

# And the gate every AI-generated IaC change still passes through
terraform fmt -check && terraform validate && tflint && checkov -d .
terraform plan -out=tfplan   # a human reviews this plan in the pull request
```

## Interview tips

- Give a balanced answer. "AI will replace DevOps" and "I don't use it because it hallucinates" are both weak; the strong answer is deliberate use with verification.
- Name concrete uses with a measured outcome, for example "pipeline-failure triage went from about 25 to 10 minutes".
- Expect "would you give an agent write access to production?" - the answer is read-only first, with changes proposed through PRs and GitOps, and human approval for anything destructive.
- Mention prompt injection when agents read logs, tickets or web content. Few candidates do, and it is the most realistic agent-specific risk.
- Say what you never paste into a prompt: secrets, credentials, customer data, and anything your company's policy excludes.
- A common weak answer treats a system-prompt instruction ("never delete anything") as a safeguard. Controls belong in identity and permissions, not in the prompt.

**Telling it as a STAR story** - an adaptable example, labelled as such; use your own facts:

- **Situation:** "Our team spent hours each week triaging failed CI pipelines and on-call alerts, and engineers were already trying AI assistants with no guardrails."
- **Task:** "I proposed a six-month plan to adopt AI tools safely and show measurable value."
- **Action:** "First I rolled out an approved coding assistant for Terraform and Helm, with the rule that generated code goes through the usual PR, plan, tflint and Checkov gates. Next I added a CI step that sends a failed job's log tail to an LLM and posts a likely cause as a PR comment - advisory only, with no repository write access. Then I piloted MCP servers for Kubernetes and CloudWatch, bound to a read-only IAM role and the `view` ClusterRole, so on-call engineers could query cluster state during incidents. Restarts, scaling and IaC changes stayed human-approved through GitOps. I tracked time to triage and engineer feedback monthly."
- **Result:** "Median pipeline-failure triage fell from about 25 to 10 minutes, and because every write still went through review, we had no AI-caused incidents."

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[How do you design CI/CD for a microservices architecture?]] (`#400`): [How do you design CI/CD for a microservices architecture?](../cicd/how-do-you-design-ci-cd-for-a-microservices-architecture.md)
- [[What is DevOps?]] (`#1`): [What is DevOps?](../core-devops-concepts/what-is-devops.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevOps Tools and Automation](./README.md) · [All topics](../README.md)
