# Sentinel-Scan Patterns (Curated)

This guide focuses on high-signal patterns with lower false-positive rates.

## Critical

```regex
# OpenAI / Anthropic style
sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{48,}
sk-ant-[A-Za-z0-9_-]{48,}

# GitHub tokens
gh[pousr]_[A-Za-z0-9]{36}

# AWS access keys
AKIA[0-9A-Z]{16}
ASIA[0-9A-Z]{16}

# Stripe keys
sk_(?:live|test)_[A-Za-z0-9]{24}

# Private key headers
-----BEGIN(?: [A-Z]+)? PRIVATE KEY-----
```

## High

```regex
# Context-anchored AWS secret key
(?i)(aws|secret_access_key).{0,20}["\'\`][A-Za-z0-9/+=]{40}["\'\`]

# Slack / SendGrid
xox[baprs]-[0-9]{8,13}-[0-9]{8,13}-[A-Za-z0-9-]{20,}
SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}

# Connection strings
(postgres|mysql|mongodb(?:\+srv)?|redis)://[^\s]+

# JWT-like token
eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+
```

## Medium (context required)

```regex
(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*["\'\`][^"\'\`]{8,}["\'\`]
```

Only raise medium findings when assignment context is clear and value is non-placeholder.

## False-positive controls

Treat as likely placeholder unless additional evidence exists:

```regex
(?i)(example|sample|placeholder|dummy|fake|test|changeme)
AKIAIOSFODNN7EXAMPLE
```

## Suppression

Use `.sentinel-ignore` path matching. Suppressed findings remain visible with:
- severity downgraded to `LOW`
- `[suppressed]` label
