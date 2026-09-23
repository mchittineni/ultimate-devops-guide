---
title: "How Does AWS KMS Envelope Encryption Work and How Is It Audited with CloudTrail?"
id: 732
category: "AWS Engineering"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - aws-engineering
  - kms
  - encryption
  - cloudtrail
quiz:
  stem: "In AWS KMS envelope encryption, where is the encrypted Data Encryption Key (DEK) stored after data has been encrypted?"
  options:
    - "It is stored permanently in the AWS KMS hardware security module (HSM) database."
    - "It is stored alongside the encrypted data itself (e.g., in S3 metadata or the volume header)."
    - "It is stored in AWS Systems Manager Parameter Store."
    - "It must be discarded and cannot be saved anywhere."
  answer: 2
  explanation: "The encrypted DEK is stored alongside the encrypted ciphertext data. Because it is securely encrypted under the KMS Key, it can be safely stored anywhere without risking data exposure."
---

# How Does AWS KMS Envelope Encryption Work and How Is It Audited with CloudTrail?

**Short answer:** Envelope encryption encrypts plaintext data using a unique Data Encryption Key (DEK), and encrypts the DEK under a root AWS KMS Key (KMS key). KMS never stores or transmits the plaintext DEK, and every key generation, encryption, and decryption API call is logged immutably in AWS CloudTrail.

## Detail

### The Architectural Problem KMS Solves

Encrypting large datasets (gigabytes of S3 objects or EBS volumes) directly via cryptographic network calls to a Key Management Service creates severe network latency and throughput bottlenecks. KMS rate limits would be quickly exhausted.

**Envelope Encryption** solves this by decoupling key management from bulk data encryption.

### Step-by-Step Envelope Encryption Workflow

1. **Key Generation Request**:
   - The application calls AWS KMS: `GenerateDataKey(KeyId="arn:aws:kms:...", KeySpec="AES_256")`.
2. **KMS Response**:
   - KMS returns two items:
     - **Plaintext Data Key (DEK)**: Used immediately in memory to encrypt the data.
     - **Encrypted Data Key (Ciphertext DEK)**: Encrypted under the customer's KMS Key.
3. **Data Encryption**:
   - The application encrypts the file/data locally using the plaintext DEK with an authenticated cipher (AES-256-GCM). In practice use the **AWS Encryption SDK** or a service integration rather than hand-rolling this - it handles the message format, encryption context, and optional data key caching.
4. **Memory Hygiene & Storage**:
   - The plaintext DEK is permanently erased from memory.
   - The **encrypted DEK is stored alongside the ciphertext data** (e.g., in the S3 object metadata header).
5. **Decryption Process**:
   - When reading data, the application extracts the encrypted DEK and sends it to KMS: `Decrypt(CiphertextBlob=encryptedDEK)`.
   - KMS validates IAM permissions and key policies, decrypts the DEK, and returns the plaintext DEK.
   - The application decrypts the data locally, then immediately wipes the plaintext DEK from memory.

```text
[Application] ──► Call KMS: GenerateDataKey()
                       │
       ┌───────────────┴───────────────┐
       ▼                               ▼
[Plaintext DEK]                 [Encrypted DEK]
       │                               │
       ▼ (Encrypt Data Locally)         │
[Ciphertext Data] ──────────────┬──────┘
                                ▼
         [Stored Together in S3 / EBS / DynamoDB]
```

### Auditing and Compliance via CloudTrail

Every interaction with AWS KMS generates an immutable event in AWS CloudTrail:

- **`kms:GenerateDataKey`**: Logs when an encrypted resource was created.
- **`kms:Decrypt`**: Logs every time an IAM role, EC2 instance, or user accessed and decrypted an encrypted asset.
- **Encryption Context**: Non-secret key-value pairs passed during KMS calls (e.g., `{"department": "finance"}`), cryptographically bound to the ciphertext as additional authenticated data - decryption fails without the same context - and recorded in CloudTrail, so each `Decrypt` event shows which object or tenant it was for. Key policies can require specific context values with `kms:EncryptionContext:` conditions.

**Trade-offs.** KMS request quotas and per-request charges still apply to every `GenerateDataKey`/`Decrypt`; S3 Bucket Keys and SDK data key caching reduce both, at the cost of a coarser audit trail (fewer, broader KMS events). CloudTrail records the KMS call, not which bytes were read, so pair it with S3 data events when you need object-level access logs.

### Real-World Production Scenario

A financial application stores customer tax documents in Amazon S3. The app requests a DEK from KMS, encrypts the PDF in memory, attaches the encrypted DEK to the S3 object metadata, and discards the plaintext key. During a SOC 2 audit, security engineers verify every document decryption event over the past year by querying `kms:Decrypt` calls in CloudTrail using Athena.

## Example

```bash
# Envelope encryption by hand, to show the mechanism (use the AWS Encryption SDK in real code)
aws kms generate-data-key --key-id alias/tax-docs --key-spec AES_256 \
  --encryption-context department=finance,doc=tax-2026-0042 > dk.json
jq -r .Plaintext dk.json | base64 -d > dek.bin            # plaintext DEK: memory only
jq -r .CiphertextBlob dk.json | base64 -d > dek.enc       # store next to the data

openssl enc -aes-256-cbc -pbkdf2 -in tax.pdf -out tax.pdf.enc -pass file:dek.bin  # demo cipher only
shred -u dek.bin                                          # discard the plaintext key

# Decrypt: KMS checks IAM + key policy + the SAME encryption context, then returns the DEK
aws kms decrypt --ciphertext-blob fileb://dek.enc \
  --encryption-context department=finance,doc=tax-2026-0042 \
  --query Plaintext --output text | base64 -d > dek.bin
```

```sql
-- Audit: who decrypted finance documents last quarter? (Athena over the CloudTrail table)
SELECT eventtime, useridentity.arn, sourceipaddress,
       json_extract_scalar(requestparameters, '$.encryptionContext.doc') AS doc
FROM cloudtrail_logs
WHERE eventsource = 'kms.amazonaws.com'
  AND eventname = 'Decrypt'
  AND json_extract_scalar(requestparameters, '$.encryptionContext.department') = 'finance'
  AND eventtime >= '2026-07-01'
ORDER BY eventtime DESC;
```

## Interview tips

- Explain why envelope encryption is necessary: encrypting large files directly over KMS network calls is slow and hits API rate limits.
- Clarify that AWS KMS never stores or caches the plaintext data encryption key; it only stores the root KMS Key.
- Mention Encryption Context as an additional authenticated data (AAD) parameter logged in CloudTrail, and that key policies can require it.
- Note the terminology: AWS now says "KMS key" rather than "customer master key (CMK)".

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?]] (`#407`): [How do you troubleshoot a Pod stuck waiting for a PersistentVolumeClaim?](../kubernetes/how-do-you-troubleshoot-a-pod-stuck-waiting-for-a-persistentvolumeclaim.md)
- [[What is Cloud Computing?]] (`#21`): [What is Cloud Computing?](../cloud-platforms/what-is-cloud-computing.md)
- [[What is Google Cloud Platform (GCP)?]] (`#24`): [What is Google Cloud Platform (GCP)?](../cloud-platforms/what-is-google-cloud-platform-gcp.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to AWS Engineering](./README.md) · [All topics](../README.md)
