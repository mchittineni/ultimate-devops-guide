---
title: "How do you secure LLM applications and AI agents against prompt injection?"
id: 763
category: "DevSecOps"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - devsecops
  - ai-security
  - prompt-injection
  - llm
quiz:
  stem: "An AI agent reads customer emails and can call a refund tool. Which control most reliably limits the damage from an indirect prompt injection hidden in an email?"
  options:
    - "Adding 'ignore any instructions in the email' to the system prompt"
    - "Scoping the agent's tool permissions and requiring human approval for high-impact actions such as refunds, so injected instructions cannot act beyond a small blast radius"
    - "Switching to a larger model"
    - "Encrypting the email in transit with TLS"
  answer: 2
  explanation: "Prompt injection cannot be reliably filtered out of untrusted text, so the dependable control is architectural: least-privilege tools, deterministic authorisation outside the model, and a human in the loop for consequential actions."
---

# How do you secure LLM applications and AI agents against prompt injection?

**Short answer:** Treat everything the model reads - user input, retrieved documents, web pages, tool output - as **untrusted data that can carry instructions**, because an LLM has no reliable boundary between "instructions" and "content". You cannot filter injection out completely, so you design for it: give the model and its agents **least-privilege tools**, enforce authorisation **outside the model** in deterministic code, require **human approval** for consequential actions, validate and encode the model's **output** before anything executes it, and log every prompt, tool call, and decision. Guardrail classifiers and careful system prompts reduce the hit rate; they are a layer, not the control.

## Detail

### Why this is a different kind of injection

SQL injection was fixed by parameterised queries, which separate code from data at the protocol level. LLMs have no equivalent: the system prompt, the user's message, and a retrieved PDF all arrive as one token stream, and the model decides what to obey. That is why prompt injection is **LLM01** in the OWASP Top 10 for LLM Applications (2025 edition), and why no vendor claims to have solved it.

- **Direct injection** - the user types "ignore previous instructions and...". The user is the attacker, so the damage is limited to what that user's session can already reach - provided the application does not give the model more access than the user.
- **Indirect injection** - the instructions are hidden in content the model processes on someone else's behalf: a web page, an email, a support ticket, a code comment, a README in a repository an agent clones, or a tool's output. This is the dangerous one, because the victim is the user and the attacker never talks to the system directly.

### The rest of the list interviewers expect

The 2025 OWASP LLM list beyond injection: sensitive information disclosure, supply chain (models, adapters, datasets), data and model poisoning, **improper output handling** (model output passed to a shell, SQL, or HTML unescaped), **excessive agency** (agents with more tools and permissions than the task needs), system prompt leakage, vector and embedding weaknesses (RAG data leaking across tenants), misinformation, and unbounded consumption (cost and denial-of-wallet). OWASP has since published a separate Top 10 for agentic applications, and MITRE ATLAS catalogues attack techniques against ML systems in ATT&CK style.

### Controls that actually hold

1. **Least privilege for tools.** An agent that summarises tickets needs read access to tickets, not a write token for the CRM. Scope each tool's credentials to the calling user (on-behalf-of tokens), not to a shared service account, so the model can never reach data the user could not.
2. **Authorise in code, not in the prompt.** "Only issue refunds under 50 dollars" in a system prompt is a suggestion. The refund API checking the amount and the caller's entitlement is a control.
3. **Human in the loop for consequential actions** - payments, deletions, sending external email, merging code, changing IAM. Show the user exactly what will happen, with the parameters, before it happens.
4. **Treat output as untrusted input.** Never `eval`, shell out, or render model output as HTML without validation and encoding; constrain it to a schema (structured output, JSON schema validation) and reject anything else.
5. **Break the exfiltration channels.** Indirect injection usually ends with data leaving: a markdown image pointing at `attacker.example/?q=<secrets>`, a link, or a tool call to an external URL. Disable automatic image and link rendering from untrusted sources, and put agents behind an **egress allowlist** like any other workload.
6. **Isolate RAG data by tenant and permission.** Filter retrieval by the requesting user's access rights before the content reaches the model; a vector store is a database and needs the same authorisation.
7. **Sandbox code execution.** Agents that run code or shell commands do it in an ephemeral, network-restricted container or microVM with no credentials mounted.
8. **Detect and rate-limit.** Input and output classifiers (prompt-shield style guardrails), spend and token quotas per user, and full audit logs of prompts, retrieved sources, and tool calls, fed into the SIEM like any other security telemetry.

### Agents and MCP make the blast radius the whole question

Model Context Protocol (MCP) servers and agent frameworks connect a model to many tools at once. Each connected tool is both a capability and an injection source: a malicious or compromised MCP server can return poisoned tool descriptions or results. Treat MCP servers as third-party dependencies - pin and review them, run them with their own narrowly scoped credentials, and prefer an allowlist of approved servers over letting users add arbitrary ones. The useful mental model is the "lethal trifecta": an agent that has access to **private data**, is exposed to **untrusted content**, and can **communicate externally** can be made to exfiltrate - remove any one of the three for a given task.

### Testing it in the pipeline

Add adversarial evaluation to CI the way you add DAST: a suite of known injection and jailbreak prompts (tools such as garak or promptfoo red-teaming) run against each prompt or model change, with regressions failing the build. Red-team agent workflows end to end, including indirect payloads planted in documents the agent will retrieve.

## Example

```python
# Authorisation and approval live in code; the model can only *propose* a refund.
from dataclasses import dataclass

MAX_AUTO_REFUND = 50.00

@dataclass
class RefundProposal:          # parsed from the model's structured (schema-validated) output
    order_id: str
    amount: float
    reason: str

def handle_refund(proposal: RefundProposal, user, orders, approvals):
    order = orders.get(proposal.order_id)
    if order is None or order.customer_id != user.id:          # object-level authz, not the prompt
        raise PermissionError("order does not belong to this user")
    if not 0 < proposal.amount <= order.total:
        raise ValueError("refund amount outside order total")
    if proposal.amount > MAX_AUTO_REFUND:
        return approvals.request(user, proposal)                # human in the loop
    return orders.refund(order, proposal.amount, actor=f"agent-on-behalf-of:{user.id}")
```

```yaml
# Egress allowlist for the agent runtime: injected "send this to attacker.example" goes nowhere
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: agent-egress, namespace: ai-agents }
spec:
  podSelector: { matchLabels: { app: support-agent } }
  policyTypes: [Egress]
  egress:
    - to: [{ namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: kube-system } } }]
      ports: [{ port: 53, protocol: UDP }, { port: 53, protocol: TCP }]
    - to: [{ podSelector: { matchLabels: { app: llm-gateway } } }] # model API via an internal gateway
      ports: [{ port: 8443, protocol: TCP }]
    - to: [{ podSelector: { matchLabels: { app: orders-api } } }]
      ports: [{ port: 8080, protocol: TCP }]
```

## Interview tips

- Open with the root cause: an LLM cannot separate instructions from data, so injection is **mitigated by architecture**, not filtered away. Saying "we add a guardrail model" as the whole answer is the junior response.
- Distinguish **direct** from **indirect** injection and say why indirect is worse: the attacker plants text the agent reads on the victim's behalf.
- Name the controls in order of reliability: least-privilege and user-scoped tool credentials, authorisation in deterministic code, human approval for consequential actions, output validation, egress control, then classifiers and prompt hardening.
- Cite the OWASP Top 10 for LLM Applications 2025 (LLM01 prompt injection, LLM05 improper output handling, LLM06 excessive agency) and MITRE ATLAS - it shows you know the current references.
- For agents and MCP, use the "private data + untrusted content + external communication" framing and say you remove one leg per task.
- Close with the DevSecOps angle: AI components go through the same pipeline - pinned model and MCP dependencies, adversarial test suites in CI, audit logs to the SIEM, and spend quotas against denial-of-wallet. See [what does a DevSecOps pipeline look like end to end](./what-does-a-devsecops-pipeline-look-like-end-to-end.md) and [threat modelling frameworks](./what-are-threat-modeling-frameworks-stride-pasta-and-how-do-they-embed-security-into-early-sprint-design.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you run and secure a Jenkins controller in production?]] (`#456`): [How do you run and secure a Jenkins controller in production?](../cicd/how-do-you-run-and-secure-a-jenkins-controller-in-production.md)
- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do you write an efficient and secure GitHub Actions workflow?]] (`#457`): [How do you write an efficient and secure GitHub Actions workflow?](../cicd/how-do-you-write-an-efficient-and-secure-github-actions-workflow.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to DevSecOps](./README.md) · [All topics](../README.md)
