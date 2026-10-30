---
title: "How do you authenticate API clients with OAuth 2.0 and OIDC at the API gateway?"
id: 765
category: "API Gateway and Service Mesh"
difficulty: "Intermediate"
tags:
  - devops
  - interview-questions
  - api-gateway-and-service-mesh
  - oauth2
  - oidc
  - jwt
quiz:
  stem: "A gateway validates a JWT access token's signature and expiry. Which additional check prevents a token issued for a different API by the same identity provider from being accepted?"
  options:
    - "Checking that the token is base64-encoded"
    - "Validating the audience (`aud`) claim against this API's identifier, along with the issuer (`iss`)"
    - "Checking the token length"
    - "Requiring the token in a query parameter"
  answer: 2
  explanation: "Signature and expiry prove the token is genuine and current, not that it was meant for you. Without an audience check, any valid token from the same issuer - for any API - is accepted."
---

# How do you authenticate API clients with OAuth 2.0 and OIDC at the API gateway?

**Short answer:** The identity provider (Entra ID, Okta, Auth0, Keycloak, Cognito) issues **access tokens**; the gateway **validates** them on every request and forwards a verified identity downstream. For JWT access tokens that means checking the **signature** against the issuer's JWKS (cached, with `kid`-based key rotation), the **issuer**, the **audience**, **expiry and not-before** with small clock skew, the allowed **algorithm**, and the **scopes** the route requires. Pick the grant by client type: **authorization code with PKCE** for browser and mobile apps acting for a user, **client credentials** for service-to-service, and the **device authorization grant** for TVs and CLIs - never the deprecated implicit or password grants. The gateway handles coarse authorisation (valid token, right scope); **object-level** checks ("does this order belong to this user?") stay in the service.

## Detail

### OAuth 2.0 versus OIDC, in one breath

OAuth 2.0 is **delegated authorisation**: a client obtains an access token to call an API. OpenID Connect adds **authentication** on top: an **ID token** that tells the _client_ who the user is. The rule people get wrong: the API and the gateway validate the **access token**; the ID token is for the client application and should never be sent to an API as a bearer credential.

### Choosing the grant

| Client                                 | Grant                                  | Notes                                                                                 |
| -------------------------------------- | -------------------------------------- | ------------------------------------------------------------------------------------- |
| Browser SPA, mobile app                | Authorization code + **PKCE**          | PKCE stops intercepted codes being redeemed; for SPAs a backend-for-frontend is safer |
| Server-side web app                    | Authorization code (+ PKCE)            | Confidential client; tokens stay on the server                                        |
| Service-to-service, batch jobs         | **Client credentials**                 | Prefer `private_key_jwt` or mTLS client auth over a shared secret                     |
| CLI, smart TV                          | Device authorization grant             | User approves on another device                                                       |
| Workload already holding another token | Token exchange (RFC 8693) / federation | e.g. a CI OIDC token exchanged for a cloud or API token                               |
| ~~Implicit, password (ROPC)~~          | Do not use                             | Removed by the OAuth 2.0 Security BCP (RFC 9700) and the OAuth 2.1 draft              |

### What the gateway must validate

1. **Signature**, using keys from the issuer's `jwks_uri`, selected by the token's `kid`. Cache the JWKS and refresh on an unknown `kid`, so key rotation does not cause an outage.
2. **Algorithm allowlist** (for example `RS256`/`ES256` only). Never accept `alg: none`, and never let the token's header choose an HMAC algorithm when you hold an RSA public key - the classic algorithm-confusion bug.
3. **`iss`** equals your expected issuer exactly.
4. **`aud`** contains this API's identifier - without it, a token minted for any other API at the same IdP works here.
5. **`exp`/`nbf`** with a small leeway (30-60 s); keep access tokens short-lived (5-60 minutes).
6. **Scopes or roles** required for this route (`orders:read` for `GET`, `orders:write` for `POST`).

**JWT versus opaque tokens.** JWTs validate locally and scale, but cannot be revoked before expiry - hence short lifetimes. Opaque tokens require **introspection** (RFC 7662) on each request (cache the result briefly), which adds latency but gives instant revocation. Many gateways support both.

### Passing identity downstream

After validation, the gateway forwards either the original token (so services can re-validate - defence in depth) or a set of trusted headers such as `x-user-id` and `x-scopes`. If you use headers, **strip any client-supplied copies first**, and make sure services are reachable only through the gateway or mesh, otherwise anyone can forge them. Inside a mesh, workload mTLS identifies the calling _service_; the token identifies the _user_ - authorise on both.

### Hardening beyond bearer tokens

A bearer token works for whoever holds it. Sender-constrained tokens bind it to a key the client holds: **DPoP** (RFC 9449) at the application layer, or **mTLS-bound tokens** (RFC 8705) for service clients. They are worth it for high-value APIs, open banking (FAPI profiles), and anywhere token theft from logs or browsers is a realistic threat.

### Failure modes interviewers probe

- IdP outage or JWKS endpoint unreachable: cached keys keep the gateway working; with opaque tokens, introspection becomes a hard dependency on the request path.
- Clock skew on gateway nodes rejecting fresh tokens - run NTP and allow small leeway.
- Tokens in URLs (`?access_token=`) leaking into logs and `Referer` headers - accept only the `Authorization` header.
- Overly broad scopes or a single "api" audience for everything, which makes the token a skeleton key.

## Example

```yaml
# Envoy Gateway: JWT validation on the route, then a required scope (per-method scopes
# can live on separate HTTPRoutes/policies, or in the service)
apiVersion: gateway.envoyproxy.io/v1alpha1
kind: SecurityPolicy
metadata: { name: orders-jwt, namespace: orders }
spec:
  targetRefs:
    - { group: gateway.networking.k8s.io, kind: HTTPRoute, name: orders }
  jwt:
    providers:
      - name: corp-idp
        issuer: https://login.example.com/
        audiences: ["api://orders"]
        remoteJWKS: { uri: https://login.example.com/.well-known/jwks.json }
        claimToHeaders:
          - { claim: sub, header: x-user-id } # gateway sets it; client-supplied copies are overwritten
  authorization:
    defaultAction: Deny
    rules:
      - name: require-orders-scope
        action: Allow
        principal:
          jwt:
            provider: corp-idp
            scopes: ["orders:write"] # a valid token WITHOUT this scope is denied with 403
```

```bash
# Service-to-service: client credentials grant, then call the API through the gateway
TOKEN=$(curl -s https://login.example.com/oauth2/token \
  -d grant_type=client_credentials -d scope=orders:write \
  -u "$CLIENT_ID:$CLIENT_SECRET" | jq -r .access_token)

# Inspect the claims the gateway will check (decoding is not validating)
cut -d. -f2 <<<"$TOKEN" | tr '_-' '/+' | base64 -d 2>/dev/null | jq '{iss, aud, exp, scope}'

curl -s -o /dev/null -w '%{http_code}\n' -H "Authorization: Bearer $TOKEN" \
  -X POST https://api.example.com/v1/orders -d '{}'      # 200/201; a token without the scope -> 403
```

## Interview tips

- Separate the roles first: the IdP issues, the gateway validates, the service makes object-level decisions. Then distinguish the access token (for APIs) from the ID token (for the client).
- Match grants to clients - authorization code with PKCE for user-facing apps, client credentials for services, device flow for CLIs - and say implicit and password grants are deprecated (RFC 9700, OAuth 2.1).
- List the validation checks in order and stress **audience**, the one most often missing, plus an algorithm allowlist to stop `alg: none` and algorithm-confusion attacks.
- Explain the JWT trade-off: local validation and scale versus no early revocation, mitigated by short lifetimes; opaque tokens plus introspection when revocation matters.
- Mention header spoofing when forwarding identity, and that services must not be reachable around the gateway.
- For senior roles, add sender-constrained tokens (DPoP, mTLS-bound) and how the gateway behaves when the IdP is down. See [what is API security](./what-is-api-security.md), [what is an API gateway](./what-is-an-api-gateway.md), and [the difference between an API gateway and a service mesh](./what-is-the-difference-between-an-api-gateway-and-a-service-mesh-and-how-do-they-work-together.md).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How does OpenID Connect (OIDC) eliminate long-lived cloud credentials in CI/CD pipelines?]] (`#533`): [How does OpenID Connect (OIDC) eliminate long-lived cloud credentials in CI/CD pipelines?](../cicd/how-does-openid-connect-oidc-eliminate-long-lived-cloud-credentials-in-ci-cd-pipelines.md)
- [[What are the benefits of DevOps?]] (`#2`): [What are the benefits of DevOps?](../core-devops-concepts/what-are-the-benefits-of-devops.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to API Gateway and Service Mesh](./README.md) · [All topics](../README.md)
