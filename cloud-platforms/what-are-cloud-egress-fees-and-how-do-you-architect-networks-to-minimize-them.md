---
title: "What are Cloud Egress fees and how do you architect networks to minimize them?"
id: 547
category: "Cloud Platforms"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - cloud
  - networking
  - cost-optimization
  - egress
quiz:
  stem: "Why does routing traffic to Amazon S3 through a VPC Gateway Endpoint reduce cloud expenditure compared to using a NAT Gateway?"
  options:
    - "S3 charges a monthly fee for every bucket accessed over the internet"
    - "Gateway Endpoints are free and route traffic over the internal AWS network, avoiding NAT Gateway hourly and per-GB processing charges"
    - "NAT Gateways automatically compress files to half their size"
    - "VPC Endpoints reduce S3 storage tier prices automatically"
  answer: 2
  explanation: "Traffic destined for S3 through a NAT Gateway incurs both NAT per-GB processing fees and public network traversal costs. VPC Gateway Endpoints are free and route privately."
---

# What are Cloud Egress fees and how do you architect networks to minimize them?

**Short answer:** Inbound data transfer is free on the major clouds, but data leaving a zone, a region, or the provider is billed per GB - and managed hops such as NAT gateways add their own processing charges on top. You minimize it by keeping traffic private and local: gateway/private endpoints instead of NAT for cloud APIs, zone-aware routing for chatty services, CDN caching for public delivery, compression, and placing data and compute in the same region.

## Detail

**The pricing ladder (AWS list prices as an order of magnitude; always check the current price list for your region).**

| Path                          | Typical charge                                              |
| ----------------------------- | ----------------------------------------------------------- |
| Within one AZ, private IPs    | Free                                                        |
| Between AZs in one region     | About $0.01/GB in each direction                            |
| Between regions               | About $0.02/GB, higher in some geographies                  |
| To the internet               | About $0.09/GB for the first tier, falling with volume      |
| Through a NAT gateway         | About $0.045/GB processing, in addition to any transfer fee |
| Through an interface endpoint | About $0.01/GB plus an hourly charge per AZ                 |

AWS includes the first 100 GB/month of internet egress free, and GCP and Azure have similar free tiers. All three waive egress fees for customers migrating out of the cloud on request, and the EU Data Act is pushing switching charges towards zero - but day-to-day egress is still charged.

**Architectural levers.**

1. **Gateway endpoints for S3 and DynamoDB.** Free, route over the AWS network, and remove NAT processing charges - usually the single biggest quick win.
2. **Interface endpoints (PrivateLink)** for other AWS APIs (ECR, CloudWatch Logs, STS). They cost money, but for high-volume traffic such as image pulls they are cheaper than NAT per GB.
3. **Zone-aware routing.** Kafka rack awareness, Kubernetes topology-aware routing, and keeping consumers near brokers cut inter-AZ traffic without giving up multi-AZ resilience.
4. **CDN for public delivery.** CloudFront, Azure Front Door, or Cloud CDN cache near users; origin-to-CDN transfer is free or discounted on the same provider.
5. **Compression and format.** Compressed, columnar formats (Parquet with zstd) reduce every byte you move.
6. **Keep data gravity in mind.** Process data in the region where it lives; cross-region replication and multi-cloud analytics are where egress bills explode.

**Trade-off.** Pinning traffic to one zone saves money but reduces resilience; aggressive caching adds staleness. Make the choice per traffic path, and measure with cost allocation data (AWS Cost and Usage Report data-transfer line items, VPC Flow Logs) before optimizing.

## Example

```bash
# Free S3 gateway endpoint: S3 traffic from private subnets stops traversing the NAT gateway
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-0abc1234 \
  --vpc-endpoint-type Gateway \
  --service-name com.amazonaws.eu-west-1.s3 \
  --route-table-ids rtb-0priv1 rtb-0priv2 rtb-0priv3
```

```yaml
# Kubernetes: prefer same-zone endpoints to cut inter-AZ transfer (Kubernetes 1.33+)
apiVersion: v1
kind: Service
metadata:
  name: orders
spec:
  selector:
    app: orders
  ports:
    - port: 80
      targetPort: 8080
  trafficDistribution: PreferClose
```

## Interview tips

- Know the ladder: intra-AZ free, inter-AZ small but per direction, inter-region more, internet most - and NAT processing on top.
- Name the S3/DynamoDB gateway endpoint as the first fix; it is free and commonly missed.
- Show you measure before you optimize: find the top data-transfer line items and the flows behind them.
- Acknowledge the resilience trade-off of zone affinity rather than recommending single-AZ everything.
- Mention that providers waive exit egress on request, but that does not help with ongoing cross-cloud traffic.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How Do AWS Transit Gateway and VPC Peering Compare for Enterprise Interconnectivity?]] (`#729`): [How Do AWS Transit Gateway and VPC Peering Compare for Enterprise Interconnectivity?](../aws-engineering/how-do-aws-transit-gateway-and-vpc-peering-compare-for-enterprise-interconnectivity.md)
- [[How Do Azure Virtual Network NAT Gateways Prevent SNAT Port Exhaustion?]] (`#740`): [How Do Azure Virtual Network NAT Gateways Prevent SNAT Port Exhaustion?](../azure-engineering/how-do-azure-virtual-network-nat-gateways-prevent-snat-port-exhaustion.md)
- [[How Does Google Cloud Shared VPC Enable Network Centralization Across Projects?]] (`#745`): [How Does Google Cloud Shared VPC Enable Network Centralization Across Projects?](../gcp-engineering/how-does-google-cloud-shared-vpc-enable-network-centralization-across-projects.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Cloud Platforms](./README.md) · [All topics](../README.md)
