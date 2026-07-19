# Logging Sucks Guidance Mapping

This reference adapts ideas from https://loggingsucks.com into concrete coding-agent rules.

## Principle Mapping
- "Logs are optimized for writing, not querying": enforce stable JSON keys and query-first schemas.
- "One wide event per request": prefer canonical event emission over scattered line logs.
- "OTel is delivery, not design": instrumentation quality still depends on event design.
- "High-cardinality and high-dimensionality are useful": keep important identifiers and business context, with privacy controls.
- "Tail sampling": always keep what matters, sample low-value happy-path traffic.

## Sensitive Data Denylist
Never log:
- Access tokens, refresh tokens, API keys, client secrets, cookies, session IDs.
- Passwords, OTPs, private keys, auth codes, raw authorization headers.
- Full personal payloads when not required for debugging.

## Safe Alternatives
- `user_id` -> `user_id_hash`.
- `email` -> redacted domain or hash.
- provider error object -> selected safe fields (`code`, `status`, `kind`).
- request body -> explicit allowlisted keys only.

## Production Logging Defaults
- `debug` disabled by default.
- Structured logs only.
- Single canonical event per request.
- Tail sampling enabled.
- Security/audit events unsampled.

## Review Checklist
- Can one query explain a failure without grep across many lines?
- Does every event include correlation fields?
- Are sensitive fields absent or transformed?
- Are errors classified and actionable?
- Is noise reduced versus previous behavior?
