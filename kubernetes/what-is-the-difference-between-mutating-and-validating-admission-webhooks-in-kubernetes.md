---
title: "What is the difference between Mutating and Validating Admission Webhooks in Kubernetes?"
id: 524
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - kubernetes
  - security
  - admission-controller
  - webhooks
quiz:
  stem: "In the Kubernetes API request lifecycle, what happens if a Mutating Webhook modifies a Pod manifest?"
  options:
    - "The Pod is instantly written to etcd, skipping Validating webhooks"
    - "The modified Pod manifest must then pass schema validation and all Validating Admission Webhooks before persistence"
    - "The client receives an HTTP 301 redirect to resubmit the request"
    - "The Mutating Webhook terminates the API server process"
  answer: 2
  explanation: "Mutating webhooks execute before validating webhooks. Any modifications made by mutating controllers must pass subsequent schema checks and validating controllers."
---

# What is the difference between Mutating and Validating Admission Webhooks in Kubernetes?

**Short answer:** Both are HTTPS callbacks the API server makes after authentication and authorisation but before an object is persisted to etcd. **Mutating** webhooks run first and may change the object by returning a JSON Patch - injecting a sidecar, adding labels, setting default security contexts. **Validating** webhooks run after all mutation and schema validation, see the final object, and may only allow or deny it. Mutation comes first so that validation judges what will actually be stored. For many cases you no longer need a webhook at all: in-process CEL policies - `ValidatingAdmissionPolicy` (GA in 1.30) and `MutatingAdmissionPolicy` (GA in 1.36) - do the same job without a network hop or a service to keep alive.

## Detail

**Where they sit.**

```text
request -> authentication -> authorisation
        -> mutating admission (built-in plugins, MutatingAdmissionPolicy, mutating webhooks)
        -> schema validation of the result
        -> validating admission (built-in plugins, ValidatingAdmissionPolicy, validating webhooks)
        -> etcd
```

**Mutating webhooks.**

- Receive an `AdmissionReview`, respond with `allowed` plus an optional base64 JSON Patch.
- Run **serially**, and because a later webhook can change what an earlier one saw, `reinvocationPolicy: IfNeeded` lets a webhook be called again after others have mutated the object.
- Must be idempotent - the same request can be admitted more than once (retries, reinvocation, dry runs).
- Examples: Istio and Linkerd sidecar injection, Vault agent injection, cloud identity webhooks, Kyverno `mutate` rules.

**Validating webhooks.**

- Return allow or deny with a message (and optionally warnings); cannot change the object.
- Run **in parallel**, and any single denial rejects the request.
- Examples: OPA Gatekeeper, Kyverno `validate` rules, image-signature verification (for example, Sigstore policy-controller), "images must come from our registry".

**Configuration that matters in both.**

- `rules` and `namespaceSelector`/`objectSelector` narrow what is sent; `matchConditions` (CEL, GA in 1.30) filter further without calling the webhook.
- `failurePolicy: Fail` blocks requests when the webhook is unreachable - secure, but a crashed webhook can stop the cluster, including the Pods that would fix it. `Ignore` keeps the cluster working but silently skips the policy. Exclude `kube-system` and the webhook's own namespace, and run the webhook highly available.
- `timeoutSeconds` (default 10, maximum 30) adds directly to API latency for every matching request.
- `sideEffects: None` is required for dry-run support.

**CEL admission policies as the alternative.** A `ValidatingAdmissionPolicy` or `MutatingAdmissionPolicy` plus its binding is evaluated inside the API server. There is no TLS certificate to rotate, no Deployment to scale, and no availability risk. The trade-off is expressiveness: CEL cannot call external systems (registries, signature services, inventory APIs), so those checks still need webhooks.

## Example

```yaml
# Validating webhook registration: deny un-approved registries, fail closed, skip system namespaces
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata: { name: registry-policy }
webhooks:
  - name: registry.policy.example.com
    admissionReviewVersions: ["v1"]
    sideEffects: None
    failurePolicy: Fail
    timeoutSeconds: 5
    rules:
      - apiGroups: [""]
        apiVersions: ["v1"]
        operations: ["CREATE", "UPDATE"]
        resources: ["pods"]
    namespaceSelector:
      matchExpressions:
        - { key: kubernetes.io/metadata.name, operator: NotIn, values: [kube-system, policy-system] }
    clientConfig:
      service: { name: registry-policy, namespace: policy-system, path: /validate }
      caBundle: LS0t... # CA that signed the webhook's serving certificate
---
# The same intent with no webhook: an in-process CEL policy
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicy
metadata: { name: approved-registry }
spec:
  failurePolicy: Fail
  matchConstraints:
    resourceRules:
      - apiGroups: [""]
        apiVersions: ["v1"]
        operations: ["CREATE", "UPDATE"]
        resources: ["pods"]
  validations:
    - expression: "object.spec.containers.all(c, c.image.startsWith('registry.example.com/'))"
      message: "images must come from registry.example.com"
---
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicyBinding
metadata: { name: approved-registry }
spec:
  policyName: approved-registry
  validationActions: [Deny]
  matchResources:
    namespaceSelector:
      matchExpressions:
        - { key: kubernetes.io/metadata.name, operator: NotIn, values: [kube-system] }
```

```bash
kubectl get mutatingwebhookconfigurations,validatingwebhookconfigurations
kubectl get validatingadmissionpolicies,mutatingadmissionpolicies
# See what mutation did: compare what you sent with what was stored
kubectl apply -f pod.yaml --dry-run=server -o yaml | diff pod.yaml - | head
```

## Interview tips

- Give the order and the reason: mutating first, then schema validation, then validating - so validation judges the final object.
- Contrast the contracts: mutating returns a JSON Patch and runs serially; validating returns allow or deny and runs in parallel.
- Discuss `failurePolicy` as a real trade-off and say how you prevent a self-inflicted outage: HA webhook, namespace exclusions, short timeouts.
- Mention idempotency and `reinvocationPolicy` for mutating webhooks - a common source of double-injected sidecars.
- Show you are current: `ValidatingAdmissionPolicy` and `MutatingAdmissionPolicy` with CEL replace many webhooks, and webhooks remain for checks that need external data.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What are Kubernetes Admission Webhook failure policies and how do you prevent self-locking outage loops?]] (`#628`): [What are Kubernetes Admission Webhook failure policies and how do you prevent self-locking outage loops?](../container-orchestration-advanced/what-are-kubernetes-admission-webhook-failure-policies-and-how-do-you-prevent-self-locking-outage-loops.md)
- [[How does Docker multi-stage building optimize container security and image size?]] (`#513`): [How does Docker multi-stage building optimize container security and image size?](../docker/how-does-docker-multi-stage-building-optimize-container-security-and-image-size.md)
- [[How do you upgrade a production Kubernetes cluster with zero downtime?]] (`#411`): [How do you upgrade a production Kubernetes cluster with zero downtime?](../container-orchestration-advanced/how-do-you-upgrade-a-production-kubernetes-cluster-with-zero-downtime.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
