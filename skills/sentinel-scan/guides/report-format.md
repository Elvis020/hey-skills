# Sentinel-Scan Report Format

## Required outputs

- `.sentinel/security.md`
- `.sentinel/secrets-found.md` (if findings)
- `.sentinel/remediation.md` (if findings)

## Masking rule (authoritative)

Always mask detected values as:
- `first4...last4`

Never print full raw secrets.

## Minimum finding fields

- `id`
- `severity`
- `file`
- `line`
- `detector`
- `masked_value`
- `status` (`active` | `suppressed`)

## Severity buckets

- `CRITICAL`
- `HIGH`
- `MEDIUM`
- `LOW`
