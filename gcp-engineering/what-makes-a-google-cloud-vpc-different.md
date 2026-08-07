---
title: "What makes a Google Cloud VPC different?"
id: 209
category: "GCP Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - gcp-engineering
  - interview-questions
---

# What makes a Google Cloud VPC different?

**Short answer:** A GCP VPC is a global resource: one VPC spans every region, with regional subnets inside it, and instances in different regions communicate over Google's backbone without peering or gateways. Firewall rules are global and target resources by service account or network tag rather than by subnet, and Shared VPC lets many projects run workloads on a network owned by one host project.

## Detail

**Global VPC changes multi-region design.** In AWS or Azure you would peer per-region networks; in GCP you add a subnet in the new region and routing works. That removes a common source of complexity - and it means an overly permissive firewall rule is global in effect, so rule discipline matters more.

**Firewall rules target identity, not addresses.** A rule can apply to instances with a given network tag or, better, running as a specific service account (`targetServiceAccounts`). Service-account targeting is preferable because tags can be added by anyone who can edit an instance, whereas changing its service account requires IAM permission. Rules have priorities, and the implied rules are deny-all ingress and allow-all egress - hierarchical firewall policies at the organisation or folder level then enforce non-overridable baselines.

**Shared VPC is the standard enterprise pattern.** A host project owns the network; service projects attach and run workloads in designated subnets. Network administration stays with the platform team while application teams keep their own projects, quotas, and IAM. The alternative, VPC Network Peering, is non-transitive and has quota limits; Network Connectivity Center/hub-and-spoke handles the larger topologies.

**Private Google Access and Private Service Connect.** Private Google Access lets instances without external IPs reach Google APIs via internal routing. Private Service Connect goes further, giving Google APIs or a third party's service a private IP endpoint inside your VPC - the equivalent of AWS PrivateLink or Azure private endpoints, and the way to remove public paths to managed services.

**Egress needs explicit design.** Instances without external IPs require Cloud NAT for outbound internet access; Cloud NAT is regional, needs port allocation planning (default static allocation can exhaust ports on chatty workloads), and logs should be enabled for investigation. For inspection, route egress through a firewall appliance or use Secure Web Proxy.

**Load balancing is unusually capable.** The global external Application Load Balancer uses a single anycast IP with backends in multiple regions, steering users to the nearest healthy backend - no DNS-based failover required, which is a genuine differentiator when comparing providers.

## Example

```bash
# One global VPC, regional subnets, and a firewall rule targeting a service account
gcloud compute networks create vpc-prod --subnet-mode=custom

gcloud compute networks subnets create sn-prod-euw1 \
  --network=vpc-prod --region=europe-west1 --range=10.70.0.0/20 \
  --secondary-range=pods=10.71.0.0/16,services=10.72.0.0/20 \
  --enable-private-ip-google-access --enable-flow-logs

gcloud compute networks subnets create sn-prod-usc1 \
  --network=vpc-prod --region=us-central1 --range=10.80.0.0/20 \
  --enable-private-ip-google-access --enable-flow-logs

# Only the checkout service account may receive traffic from the LB health checkers
gcloud compute firewall-rules create allow-lb-to-checkout \
  --network=vpc-prod --direction=INGRESS --action=ALLOW --rules=tcp:8080 \
  --source-ranges=35.191.0.0/16,130.211.0.0/22 \
  --target-service-accounts=checkout@payments-prod.iam.gserviceaccount.com

# Egress for instances with no external IP
gcloud compute routers create rtr-euw1 --network=vpc-prod --region=europe-west1
gcloud compute routers nats create nat-euw1 --router=rtr-euw1 --region=europe-west1 \
  --auto-allocate-nat-external-ips --nat-all-subnet-ip-ranges --enable-logging
```

## Interview tips

- "The VPC is global, subnets are regional" is the headline difference - say it first.
- Firewall rules targeting service accounts rather than tags is the security-savvy detail.
- Expect: "how do many teams share a network?" - Shared VPC with host and service projects, and note peering is non-transitive.

---

[⬅ Back to GCP Engineering](./README.md) · [All topics](../README.md)
