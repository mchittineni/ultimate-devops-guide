---
title: "What are Confidential Computing and Enclaves (AWS Nitro Enclaves, AMD SEV) and how do they protect data in use?"
id: 699
category: "Advanced DevOps & Cloud"
difficulty: "Advanced"
tags:
  - devops
  - interview-questions
  - security
  - confidential-computing
  - nitro-enclaves
  - encryption
quiz:
  stem: "Which security state does Confidential Computing specifically protect that standard disk and network encryption cannot?"
  options:
    - "Data at rest stored on SSDs"
    - "Data in transit across fiber optic cables"
    - "Data in use actively executing inside computer RAM and CPU caches"
    - "Data stored in offline tape archives"
  answer: 3
  explanation: "Disk encryption protects data at rest; TLS protects data in transit. Confidential Computing encrypts memory at the hardware level, protecting 'data in use' while being processed by the CPU."
---

# What are Confidential Computing and Enclaves (AWS Nitro Enclaves, AMD SEV) and how do they protect data in use?

**Short answer:** Confidential computing protects data _in use_ by running the computation inside a hardware-isolated trusted execution environment (TEE) whose memory the host operating system, hypervisor, and cloud operator cannot read. Its second half is **remote attestation**: the hardware produces a signed measurement of exactly what code is running, and a key service releases secrets only to an environment whose measurement matches policy. The trade-off is a smaller, harder-to-debug runtime and a trust shift onto the CPU vendor's hardware and firmware.

## Detail

**The gap it closes.** Disk and object encryption protect data at rest; TLS protects it in transit. While a process is working on the data it sits in plaintext in RAM and CPU caches, where a compromised hypervisor, a malicious insider with host access, or a memory-dump attack can read it. Confidential computing closes that third state.

**Two families of TEE**

| Model                             | Examples                                                               | Isolation boundary                                          | What you run                                     |
| --------------------------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------ |
| **Confidential VM**               | AMD SEV-SNP, Intel TDX (Azure/GCP confidential VMs, EC2 with SEV-SNP)  | The whole VM; memory encrypted with a per-VM key in the CPU | An ordinary, unmodified guest OS and application |
| **Enclave** (process or VM-sized) | Intel SGX (process enclaves), AWS Nitro Enclaves (isolated sibling VM) | A carved-out region or VM with no host access               | A minimal, purpose-built application             |

AWS Nitro Enclaves are isolated by the Nitro hypervisor rather than by memory encryption: the enclave is a separate VM carved from a parent EC2 instance's CPU and memory, with **no persistent storage, no external networking, and no interactive access** - its only channel is a local vsock to the parent. Confidential VMs, by contrast, look like normal VMs, which makes adoption easy but leaves a much larger trusted code base (the whole guest OS).

**Attestation is the part that makes it useful.** Isolation alone only protects data you somehow got into the enclave. Attestation lets a relying party verify - cryptographically, before handing over any secret - that the environment is genuine hardware running an approved image. With Nitro Enclaves, the enclave requests a signed attestation document containing platform configuration register (PCR) measurements of the enclave image; AWS KMS key policies can use condition keys such as `kms:RecipientAttestation:ImageSha384` so that `Decrypt` succeeds only for that exact image. The same pattern exists with Azure Attestation and GCP's confidential computing attestation.

**Typical uses:** processing card data or private keys, multi-party analytics where no party may see the others' raw data, protecting ML model weights or inference inputs, and meeting regulatory demands to exclude the cloud operator from the trust boundary.

**Limitations to state honestly**

- **Side channels** - TEEs have a long history of microarchitectural attacks (speculative execution, cache timing); vendors patch via microcode and firmware, so TCB versions must be tracked and attestation policy must reject outdated ones.
- **You still trust the CPU vendor** and its attestation infrastructure.
- **Operational cost** - enclaves are hard to debug (no shell, limited logging), images must be rebuilt and re-measured on every change, and key policies must be updated with new measurements.
- **It protects confidentiality, not correctness** - a bug in the code inside the enclave still leaks data through its legitimate outputs.

## Example

```bash
# Build an enclave image from a container, run it, and read its measurements
nitro-cli build-enclave --docker-uri tokenizer:1.4 --output-file tokenizer.eif
# -> prints PCR0/PCR1/PCR2 hashes of the image

nitro-cli run-enclave --eif-path tokenizer.eif --cpu-count 2 --memory 2048
nitro-cli describe-enclaves
```

```json
{
  "Sid": "DecryptOnlyFromApprovedEnclaveImage",
  "Effect": "Allow",
  "Principal": { "AWS": "arn:aws:iam::123456789012:role/tokenizer-parent" },
  "Action": "kms:Decrypt",
  "Resource": "*",
  "Condition": {
    "StringEqualsIgnoreCase": {
      "kms:RecipientAttestation:ImageSha384": "<PCR0 value from nitro-cli build-enclave>"
    }
  }
}
```

## Interview tips

- Name the three states of data and say plainly that confidential computing is about the third - data in use.
- Distinguish confidential VMs (lift-and-shift, large trusted base) from enclaves (small trusted base, more engineering). Asking which the interviewer means is a good sign.
- Attestation-gated key release is the mechanism that matters; describe the KMS condition on the image measurement.
- Volunteer the limitations - side channels, vendor trust, and the debugging burden - rather than presenting it as absolute protection.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does OpenID Connect (OIDC) eliminate long-lived cloud credentials in CI/CD pipelines?]] (`#533`): [How does OpenID Connect (OIDC) eliminate long-lived cloud credentials in CI/CD pipelines?](../cicd/how-does-openid-connect-oidc-eliminate-long-lived-cloud-credentials-in-ci-cd-pipelines.md)
- [[How do you secure CI/CD runners against supply-chain attacks and untrusted pull requests?]] (`#538`): [How do you secure CI/CD runners against supply-chain attacks and untrusted pull requests?](../cicd/how-do-you-secure-ci-cd-runners-against-supply-chain-attacks-and-untrusted-pull-requests.md)
- [[What are SLSA (Supply-chain Levels for Software Artifacts) frameworks and how do they verify build integrity?]] (`#539`): [What are SLSA (Supply-chain Levels for Software Artifacts) frameworks and how do they verify build integrity?](../cicd/what-are-slsa-supply-chain-levels-for-software-artifacts-frameworks-and-how-do-they-verify-build-integrity.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Advanced DevOps & Cloud](./README.md) · [All topics](../README.md)
