---
name: logging-best-practices
description: "Design and review application logging using wide events/canonical log lines, high-cardinality structured fields, and strict sensitive-data controls. Use when adding logs, debugging production incidents, reducing log noise/cost, or refactoring auth/API/error logging."
---

# Logging Best Practices

## Overview
Apply a production-first logging model inspired by https://loggingsucks.com: emit fewer but wider events, optimize for queryability, and never leak secrets or personal data.

## Core Rules
- Log events, not print statements.
- Prefer one canonical event per request/service hop over many fragmented lines.
- Log structured JSON (stable keys), never ad-hoc strings.
- Include correlation identifiers on every event (`request_id`, `trace_id`, `service`, `version`).
- Add business context needed for incident triage (outcome, latency, actor/category, feature flags, dependency status).
- Never log secrets, tokens, credentials, raw cookies, authorization headers, refresh/access tokens, private keys, or full personal payloads.
- Redact or hash sensitive fields before logging.
- Keep error logs actionable: include error class/code and operation stage, not raw internal dumps.

## Wide Event Schema
Use this baseline schema and extend per domain:

```json
{
  "timestamp": "ISO-8601",
  "event": "checkout.request",
  "service": "payroll-app",
  "version": "git_sha_or_app_version",
  "request_id": "req_xxx",
  "trace_id": "trace_xxx",
  "outcome": "success|error",
  "status_code": 200,
  "duration_ms": 123,
  "actor": {
    "type": "user|system",
    "id_hash": "sha256(...)"
  },
  "context": {
    "route": "/api/...",
    "feature_flags": { "flag_name": true }
  },
  "error": {
    "kind": "ValidationError",
    "code": "invalid_input",
    "retriable": false
  }
}
```

## Sampling Policy
Apply tail sampling to control cost:
- Always keep: errors, exceptions, 5xx, slow requests above p99 threshold, security-relevant events.
- Usually keep: rollout/experiment traffic and VIP/internal support sessions.
- Random sample the rest at low rate (for example `1-5%`).
- Keep the sampling decision deterministic when needed (based on request hash) for reproducibility.

## Security Guardrails
Before finalizing any logging change:
- Verify no secret-bearing fields are present in new log payloads.
- Replace raw identifiers with hashed or truncated forms when possible.
- Avoid sending provider tokens to client-visible logs or client session payloads.
- Ensure production log level disables verbose debug dumps by default.
- Prefer explicit safe metadata extraction over logging unknown objects.

## Implementation Workflow
1. Identify noisy or fragmented logs in the request path.
2. Define one canonical event shape for that path.
3. Add context progressively during request processing.
4. Emit once at completion (success or failure).
5. Add tail sampling rules.
6. Run a leak-check review for sensitive fields.
7. Verify queries answer incident questions quickly (who, what failed, where, impact).

## Output Expectations
When using this skill in a code review or refactor, return:
- A concise risk list of sensitive logging exposures.
- Proposed canonical event schema changes.
- Concrete file-level edits to replace noisy logs.
- Sampling and retention recommendation.
- A short “safe in production” checklist result.

## References
- Read [logging-sucks-guidance](references/logging-sucks-guidance.md) for principle mapping and practical checklists.
