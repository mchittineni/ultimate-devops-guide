---
title: "How do you troubleshoot a Kubernetes Service that has no endpoints?"
id: 403
category: "Kubernetes"
difficulty: "Intermediate"
tags:
  - devops
  - kubernetes
  - interview-questions
  - network-security
---

# How do you troubleshoot a Kubernetes Service that has no endpoints?

**Short answer:** Walk the chain in one direction - **Service selector → Pod labels → Pod readiness → port names and numbers → kube-proxy → NetworkPolicy → Service type**. An empty `EndpointSlice` has only three possible causes: no Pod matches the selector, matching Pods are not `Ready`, or the container port does not exist. `kubectl get endpointslices` plus `kubectl describe svc` narrows it in two commands, and the classic culprit is a label typo or a failing readiness probe.

## Detail

### The chain, in the order to check it

1. **Are there endpoints at all?**

   ```bash
   kubectl get endpointslices -l kubernetes.io/service-name=checkout -o wide
   ```

   Empty means the Service is not the problem in a routing sense - nothing has been selected. Populated means the selector works and your problem is further out (port, network policy, node, or client side).

2. **Selector versus Pod labels.** Compare `spec.selector` on the Service with the Pods' actual labels. `app: checkout` does not match `app: checkout-api`, and the mismatch is invisible until you diff them. Run the selector as a query - `kubectl get pods -l app=checkout` - and if it returns nothing, you have found the bug. Also check the **namespace**: a Service only ever selects Pods in its own namespace.

3. **Readiness.** A Pod is added to the endpoints only when it is `Ready`. A failing readiness probe therefore produces a healthy-looking Pod and an empty Service. `kubectl get pods` showing `1/1` but `READY 0/1` on the container, or events showing `Readiness probe failed`, is the answer. See [how do liveness, readiness, and startup probes differ](./how-do-liveness-readiness-and-startup-probes-differ.md).

4. **Ports.** Three fields must line up: the container's `containerPort`, the Service's `targetPort`, and the Service's `port` that clients use. When `targetPort` is a **name** (`targetPort: http`), the container must declare a port with exactly that name - a rename in the Deployment silently empties the Service. Also confirm the protocol (`TCP` vs `UDP`) and that the application listens on `0.0.0.0`, not `127.0.0.1` - a process bound to loopback is unreachable from outside the Pod even with perfect Kubernetes configuration.

5. **Headless and manual cases.** `clusterIP: None` gives DNS records per Pod and no virtual IP - correct for StatefulSets, wrong if you expected load balancing. A Service with **no selector** never gets endpoints automatically; something must create the `EndpointSlice` (that is the pattern for pointing at an external address, alongside `type: ExternalName`).

6. **Then the data path.** With endpoints present but traffic failing: test from inside the cluster first (`kubectl run -it --rm debug --image=nicolaka/netshoot`), hitting the Pod IP directly, then the Service ClusterIP, then the Service DNS name. Whichever hop fails names the layer - Pod IP failing is the application or the container port; ClusterIP failing with a working Pod IP points at kube-proxy or CNI; DNS failing points at CoreDNS. See [how do you debug DNS resolution failures inside a Kubernetes cluster](./how-do-you-debug-dns-resolution-failures-inside-a-kubernetes-cluster.md).

7. **NetworkPolicy.** A default-deny policy in the namespace silently drops traffic that Kubernetes otherwise routes correctly - endpoints look perfect, connections time out. See [how do Kubernetes NetworkPolicies work, and how do you debug one that blocks traffic](./how-do-kubernetes-networkpolicies-work-and-how-do-you-debug-one-that-blocks-traffic.md).

### When the problem is external reachability

If the Service works inside the cluster but not from outside, the issue is the Service **type** and what sits in front of it:

- `ClusterIP` is cluster-internal only - reaching it from your laptop was never going to work; that is what `port-forward`, an Ingress, or a LoadBalancer is for.
- `NodePort` needs the node's security group or firewall to allow the port (30000-32767) and needs a node that is actually reachable.
- `LoadBalancer` requires a cloud controller; `EXTERNAL-IP` stuck on `<pending>` means no controller, no available public subnet or tag, or exhausted quota. Read the Service's events - the cloud provider writes the failure there.
- Health checks matter twice: the cloud load balancer has its own, separate from the readiness probe, and a failing load-balancer health check produces 502s with healthy Pods.

See [how do you expose an application running in Kubernetes to the outside world](./how-do-you-expose-an-application-running-in-kubernetes-to-the-outside-world.md).

## Example

```bash
# 1. The two commands that solve most cases
kubectl describe svc checkout -n prod | sed -n '/Selector/,/Endpoints/p'
kubectl get endpointslices -l kubernetes.io/service-name=checkout -n prod -o wide

# 2. Run the Service's own selector as a query - does it match anything?
kubectl get pods -n prod -l app=checkout --show-labels
# No resources found  <- the selector is wrong, or the Pods are elsewhere

# 3. Ready, or just Running? Only Ready Pods become endpoints.
kubectl get pods -n prod -l app=checkout -o wide
kubectl describe pod -n prod checkout-7d9f... | grep -A5 'Readiness'

# 4. Walk the hops from inside the cluster
kubectl run -it --rm netshoot -n prod --image=nicolaka/netshoot -- bash
  curl -sv 10.244.3.17:8080/healthz     # Pod IP     -> app + containerPort
  curl -sv 10.96.71.4:80/healthz        # ClusterIP  -> kube-proxy / CNI
  curl -sv http://checkout/healthz      # DNS name   -> CoreDNS + search path
```

```yaml
# The port triangle that must line up - and the named-port trap
apiVersion: v1
kind: Service
metadata: { name: checkout }
spec:
  selector: { app: checkout } # MUST equal the Pod template labels, same namespace
  ports:
    - name: http
      port: 80 # what clients call
      targetPort: http # a NAME here must exist on the container below
      protocol: TCP
---
# Deployment excerpt
spec:
  template:
    metadata:
      labels: { app: checkout } # rename this and the Service empties silently
    spec:
      containers:
        - name: api
          ports:
            - name: http # the name targetPort refers to
              containerPort: 8080 # what the process actually listens on (0.0.0.0)
          readinessProbe: # failing here = no endpoints, healthy-looking Pod
            httpGet: { path: /healthz, port: http }
```

## Interview tips

- Answer with the chain, in order, and say up front that an empty endpoint list has exactly three causes: selector mismatch, Pods not Ready, or a wrong port. That structure is the whole point of the question.
- Name the readiness probe explicitly. It is the most common real cause and the one candidates forget, because the Pod looks fine.
- Mention the named-`targetPort` trap and the `0.0.0.0` versus `127.0.0.1` bind. Both are things you only know from having debugged them.
- Use the hop-by-hop test (Pod IP → ClusterIP → DNS name) to show you isolate layers instead of changing YAML hopefully.
- Have the external-access branch ready: `ClusterIP` is internal, `<pending>` external IP means no cloud controller or no capacity, and the load balancer's health check is separate from the readiness probe.
- Close with `kubectl get endpointslices` rather than the deprecated `kubectl get endpoints` - EndpointSlice is the current API and using it signals you are current. See [what is a Service in Kubernetes](./what-is-a-service-in-kubernetes.md).

---

[⬅ Back to Kubernetes](./README.md) · [All topics](../README.md)
