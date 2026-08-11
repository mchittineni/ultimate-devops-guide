---
title: "How do Kubernetes NetworkPolicies work, and how do you debug one that blocks traffic?"
id: 405
category: "Kubernetes"
difficulty: "Advanced"
tags:
  - devops
  - kubernetes
  - interview-questions
  - network-security
  - devsecops
---

# How do Kubernetes NetworkPolicies work, and how do you debug one that blocks traffic?

**Short answer:** NetworkPolicies are **allow-only and additive**: a Pod selected by no policy accepts everything, a Pod selected by any policy for a direction accepts only what the union of its policies permits, and there is no deny rule and no ordering. So debugging is always the same question - _which policies select this Pod, and does their union allow this exact flow?_ Check that a CNI enforcing policy is actually installed (without one, every policy is silently ignored), then compare the podSelector, the namespaceSelector, the ports, and the direction. The two classic mistakes are forgetting that egress rules need **DNS on UDP and TCP 53**, and assuming policy applies to the reply traffic - it does not, connections are stateful.

## Detail

### The model, precisely

- **Empty policy list = allow all.** Policy is opt-in per Pod, per direction.
- **Once a Pod is selected by a policy with `policyTypes: [Ingress]`, all ingress not explicitly allowed is denied** - and the same independently for egress. This is why `podSelector: {}` with `policyTypes: [Ingress, Egress]` and no rules is the canonical default-deny.
- **Rules are a union, never a precedence chain.** Three policies selecting one Pod produce the sum of their allowances. You cannot write "deny X" - you can only stop allowing it, which means removing or narrowing a policy.
- **`from`/`to` peers are `podSelector`, `namespaceSelector`, or `ipBlock`** - and the AND/OR distinction is where most bugs live. Two selectors inside **one list item** are ANDed (Pods matching this selector _in_ namespaces matching that one); as **separate list items** they are ORed. A single misplaced dash changes the meaning entirely.
- **Selectors match labels, not names.** Use the built-in `kubernetes.io/metadata.name` label to target a namespace by name.
- **Connections are stateful.** Allowing ingress on port 8080 permits the reply on the ephemeral port automatically; you do not write a return rule.
- **`ipBlock` sees post-NAT addresses**, so allowing a Pod CIDR is not the same as allowing Pods, and cluster-external clients may arrive as a node IP.
- **Not everything is covered by the core API**: no layer 7 rules, no policy on node-level traffic in some CNIs, and hostNetwork Pods often escape enforcement. That is why Cilium and Calico add their own CRDs (`CiliumNetworkPolicy`, Calico `NetworkPolicy`/`GlobalNetworkPolicy`) with layer 7, FQDN, and cluster-wide scope.

### Debugging a blocked flow

1. **Confirm enforcement exists.** If the CNI does not implement NetworkPolicy (plain flannel, some managed defaults), every policy is accepted by the API server and enforced by nothing. Conversely, if traffic is blocked and you expected it not to be, something _is_ enforcing.
2. **List the policies that select the destination Pod**, both directions - the destination's ingress rules and the source's egress rules must _both_ allow the flow. Half of the "my policy is right" cases are a default-deny egress on the client side.
3. **Describe them and read the rules as the union.** `kubectl describe networkpolicy` renders them readably; look for `Allowing ingress traffic: <none>` which means default-deny.
4. **Diff the selector against reality.** Run each selector as a query (`kubectl get pods -l role=frontend -n prod`) and confirm it returns the Pods you meant. Then check the namespace label exists.
5. **Check ports and protocol.** `port: 8080` must be the **container port** (or a named port), not the Service port - policy applies to the Pod, so the Service's port mapping is irrelevant. UDP needs its own rule.
6. **Test the flow directly**, Pod IP to Pod IP, to remove Service and DNS from the picture. A `curl` timeout (rather than a connection refused) is the signature of a policy or firewall drop; refused usually means nothing is listening.
7. **Use the CNI's own tooling** - `cilium connectivity test`, `cilium monitor --type drop`, Hubble flow logs, `calicoctl` and Calico's flow logs, or eBPF drop counters. This is the difference between guessing and seeing the drop with a reason.
8. **If you must confirm causality**, delete or narrow the policy in a non-production namespace and re-test. Deleting a policy in production to test a theory is how a security incident starts; if you must, timebox it, announce it, and restore it.

### Rolling policy out without an outage

Start in **audit mode** where the CNI supports it (Cilium's policy audit, Calico's staged policies) so you see what _would_ be dropped before anything is. Otherwise adopt namespace by namespace: label everything, write the allow rules from observed flows (Hubble, flow logs, or a service mesh's telemetry), apply default-deny to one low-risk namespace, watch, then widen. Always ship the DNS egress rule in the same change as any default-deny egress, and remember `kube-apiserver` access, health probes from the kubelet (node IP, not a Pod), and metrics scraping from Prometheus - all three are commonly forgotten and produce confusing failures minutes later.

## Example

```yaml
# Default-deny for the namespace, then the minimum needed to work.
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny, namespace: prod }
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress] # both directions, no rules = deny both
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: checkout-allow, namespace: prod }
spec:
  podSelector:
    matchLabels: { app: checkout }
  policyTypes: [Ingress, Egress]
  ingress:
    - from:
        # AND: pods labelled role=gateway *in* namespaces labelled tier=edge
        - podSelector: { matchLabels: { role: gateway } }
          namespaceSelector: { matchLabels: { tier: edge } }
        # OR (separate item): the ingress controller namespace, any pod
        - namespaceSelector:
            matchLabels: { kubernetes.io/metadata.name: ingress-nginx }
      ports:
        - { protocol: TCP, port: 8080 } # the CONTAINER port, not the Service port
  egress:
    - to: # DNS - ship this with every default-deny egress
        - namespaceSelector:
            matchLabels: { kubernetes.io/metadata.name: kube-system }
      ports:
        - { protocol: UDP, port: 53 }
        - { protocol: TCP, port: 53 }
    - to: # the database, by label
        - podSelector: { matchLabels: { app: postgres } }
      ports:
        - { protocol: TCP, port: 5432 }
```

```bash
# Which policies select this Pod, and what do they actually allow?
kubectl get networkpolicy -n prod -o wide
kubectl describe networkpolicy -n prod checkout-allow | sed -n '/Spec/,$p'

# Do the selectors match what I think they match?
kubectl get pods -n prod -l app=checkout --show-labels
kubectl get ns -l tier=edge

# Test Pod-to-Pod directly: timeout = dropped, refused = nothing listening
kubectl run -it --rm netshoot -n prod --image=nicolaka/netshoot -- \
  curl -sv --connect-timeout 3 10.244.3.17:8080/healthz

# See the drop, with a reason (Cilium)
cilium monitor --type drop | grep 10.244.3.17
hubble observe --to-pod prod/checkout --verdict DROPPED
```

## Interview tips

- Lead with the model - allow-only, additive, no ordering, opt-in per direction. Candidates who describe NetworkPolicy as a firewall with rules and precedence get corrected immediately.
- Say that a policy is enforced by the CNI, not by Kubernetes, and that with a non-enforcing CNI your policies are decorative. It is the first thing to check and it is frequently the answer.
- The DNS rule is the single best detail to volunteer: default-deny egress without UDP and TCP 53 to `kube-system` breaks everything, and the symptom looks nothing like a network policy problem.
- Get the AND/OR of `podSelector` plus `namespaceSelector` right - same list item is AND, separate items are OR. This is the most common real bug and a favourite follow-up.
- Note that the port in a policy is the container port, and that connections are stateful so no return rule is needed.
- Mention audit or staged policy mode for rollout, plus the three forgotten flows: kubelet health probes, Prometheus scrapes, and API server access.
- For deep debugging, name Hubble or Calico flow logs rather than "check the logs" - seeing the drop verdict is what closes these cases. See [how do you design defence in depth for a cloud network](../network-security/how-do-you-design-defence-in-depth-for-a-cloud-network.md).

<!-- BEGIN GENERATED RELATED TOPICS -->
## Related Concepts

- [[Why does a container fail to start with a permission denied error?]] (`#416`): [Why does a container fail to start with a permission denied error?](../docker/why-does-a-container-fail-to-start-with-a-permission-denied-error.md)
- [[How do you run a multi-tenant Kubernetes cluster?]] (`#453`): [How do you run a multi-tenant Kubernetes cluster?](../container-orchestration-advanced/how-do-you-run-a-multi-tenant-kubernetes-cluster.md)
- [[How do you troubleshoot Docker networking between containers?]] (`#415`): [How do you troubleshoot Docker networking between containers?](../docker/how-do-you-troubleshoot-docker-networking-between-containers.md)
<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
