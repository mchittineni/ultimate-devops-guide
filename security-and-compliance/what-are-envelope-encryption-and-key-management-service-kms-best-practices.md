---
title: "What are envelope encryption and Key Management Service (KMS) best practices?"
id: 566
category: "Security and Compliance"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - security
  - kms
  - encryption
  - envelope-encryption
quiz:
  stem: "What is the primary performance and security benefit of envelope encryption over encrypting data directly via KMS API calls?"
  options:
    - "It eliminates the need for mathematical encryption algorithms"
    - "It avoids sending large payloads over the network to KMS and protects the root key inside an HSM, using ephemeral data keys for local bulk encryption"
    - "Envelope encryption can only be cracked by quantum computers"
    - "It allows encryption without managing access permissions"
  answer: 2
  explanation: "Envelope encryption uses fast local symmetric encryption with a unique DEK, avoiding network payload limits while keeping the master root key securely anchored inside the HSM."
---

# What are envelope encryption and Key Management Service (KMS) best practices?

**Short answer:** Envelope encryption encrypts data locally with a unique Data Encryption Key (DEK), then encrypts (wraps) that DEK with a Key Encryption Key (KEK) that never leaves the KMS's HSMs, and stores the wrapped DEK next to the ciphertext. Bulk encryption stays fast and local, while access to the data is controlled, audited, and revocable through a single KMS key policy. KMS best practice is then about that key: least-privilege key policies, separation of key administrators from key users, automatic rotation, encryption context, and logging every use.

## Detail

Directly sending large files to a KMS API to be encrypted is slow, expensive, and limited by KMS request payload limits (typically 4KB).

### How Envelope Encryption Operates

```text
1. Application requests a Data Key from KMS -> kms:GenerateDataKey(KeyId="root-kek")
2. KMS generates random DEK -> Returns two copies:
   - Plaintext DEK
   - Ciphertext DEK (encrypted by the HSM's root KEK)
3. Application encrypts 10GB file locally in RAM using AES-256-GCM with Plaintext DEK
4. Application securely wipes Plaintext DEK from RAM
5. Application stores Ciphertext DEK alongside the encrypted file
```

### Decryption Flow

1. To read the file, the application sends the Ciphertext DEK back to KMS: `kms:Decrypt(CiphertextDEK)`.
2. KMS decrypts the DEK using its internal root key and returns the Plaintext DEK.
3. Application decrypts the 10GB file and immediately zeroes the DEK memory.

### KMS Best Practices

- **Customer-managed keys** for sensitive data, so you control the key policy, rotation, and deletion; provider-owned default keys give encryption but not access control.
- **Separate duties**: key administrators can manage but not use the key; application roles can use (`kms:Decrypt`, `kms:GenerateDataKey`) but not manage it. Keep key policies explicit rather than delegating everything to IAM.
- **Encryption context** (additional authenticated data such as `{"tenant": "acme"}`) binds a wrapped DEK to its purpose; decrypt fails if the context differs, and it appears in the audit log.
- **Automatic rotation** of the KEK (AWS KMS rotates yearly by default and supports custom periods); old key versions are retained so existing wrapped DEKs still decrypt - rotation does not re-encrypt your data.
- **One DEK per object or per session**, never a single DEK for everything; data-key caching (AWS Encryption SDK) is a deliberate trade-off between KMS cost/quotas and blast radius.
- **Audit and alert** on key use (CloudTrail, Azure Monitor, Cloud Audit Logs), especially `Decrypt` from unexpected principals and any `ScheduleKeyDeletion` or key-policy change.
- **Crypto-shredding**: deleting or disabling the KEK makes every DEK it wrapped - and therefore the data - unrecoverable. Useful for tenant offboarding, catastrophic if unplanned, which is why KMS enforces a waiting period before deletion.

## Example

```python
# Envelope encryption with AWS KMS and AES-256-GCM (boto3 + cryptography)
import os, boto3
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

kms = boto3.client("kms")
context = {"tenant": "acme", "purpose": "invoices"}          # encryption context: bound and audited

# 1. KMS returns the DEK twice: plaintext (use now) and wrapped by the KEK (store)
dk = kms.generate_data_key(KeyId="alias/invoices", KeySpec="AES_256", EncryptionContext=context)
nonce = os.urandom(12)
ciphertext = AESGCM(dk["Plaintext"]).encrypt(nonce, b"invoice bytes...", None)
stored = {"wrapped_dek": dk["CiphertextBlob"], "nonce": nonce, "data": ciphertext}
del dk                                                        # drop the plaintext DEK reference

# 2. Decrypt: unwrap the DEK (same context required), then decrypt locally
dek = kms.decrypt(CiphertextBlob=stored["wrapped_dek"], EncryptionContext=context)["Plaintext"]
plaintext = AESGCM(dek).decrypt(stored["nonce"], stored["data"], None)
```

## Interview tips

- Explain why it exists: KMS `Encrypt` accepts only small payloads (4 KB on AWS) and every call costs latency and money, so bulk data is encrypted locally and only the small DEK makes a round trip.
- The security property to name: the KEK never leaves the HSM, so an attacker with the database and the wrapped DEKs still needs `kms:Decrypt` permission - which is logged and revocable centrally.
- Rotation nuance: rotating the KEK creates a new key version for future wraps; old DEKs still decrypt. Re-encrypting data requires rewrapping or re-encrypting explicitly.
- Mention encryption context, key-policy separation of admins from users, and alerting on key-policy changes and deletion scheduling.
- Trade-offs: a KMS dependency on the read path (plan for quotas and regional outages - multi-Region keys exist for this), and the practical limit that memory "wiping" is best-effort in garbage-collected languages, which is one reason to keep DEK lifetime short.

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[What is DAST (Dynamic Application Security Testing) and how is OWASP ZAP integrated into CI/CD pipelines?]] (`#709`): [What is DAST (Dynamic Application Security Testing) and how is OWASP ZAP integrated into CI/CD pipelines?](../devsecops/what-is-dast-dynamic-application-security-testing-and-how-is-owasp-zap-integrated-into-ci-cd-pipelines.md)
- [[What is Runtime Application Self-Protection (RASP) and how does it differ from a perimeter WAF?]] (`#711`): [What is Runtime Application Self-Protection (RASP) and how does it differ from a perimeter WAF?](../devsecops/what-is-runtime-application-self-protection-rasp-and-how-does-it-differ-from-a-perimeter-waf.md)
- [[What are Threat Modeling frameworks (STRIDE, PASTA) and how do they embed security into early sprint design?]] (`#710`): [What are Threat Modeling frameworks (STRIDE, PASTA) and how do they embed security into early sprint design?](../devsecops/what-are-threat-modeling-frameworks-stride-pasta-and-how-do-they-embed-security-into-early-sprint-design.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Security and Compliance](./README.md) · [All topics](../README.md)
