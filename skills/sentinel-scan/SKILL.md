---
name: sentinel-scan
description: "Scan codebase for leaked secrets, API keys, and sensitive data. Use for security scans and secret detection. Outputs reports to .sentinel/ and uses .codebase-indexer/docs/ as optional scan context."
---

# Sentinel-Scan

Scan the current project for leaked secrets, API keys, and sensitive data, then generate actionable reports.

## Scope and Paths

- **Report output path (authoritative):** `.sentinel/`
- **Optional scan context input:** `.codebase-indexer/docs/`

Sentinel writes only to `.sentinel/`. It may read `.codebase-indexer/docs/` to target high-value files.

## Modes

| Mode | Trigger | Behavior |
|---|---|---|
| `full` | "scan for secrets", "security audit", "rescan" | Working tree + high-value paths + optional git history |
| `quick` | "quick scan", "fast scan" | High-value files only |
| `git-history` | "scan commits", "check git history" | Commit-history focused scan |

## Required Rules

1. Check for `.sentinel-ignore` first and apply suppressions.
2. Read `.codebase-indexer/docs/architecture.md` + `implementation.md` when present.
3. Prefer targeted scanning over full-repo file reads.
4. Never print full secret values; mask as `first4...last4`.
5. Use executable/valid regex search commands (e.g., `rg --pcre2`).
6. Run git history scan only with commit-count guardrails.

## Scan Workflow

1. Pre-scan setup
- Read `.sentinel-ignore` (if present).
- Determine mode (`full`, `quick`, `git-history`).
- If `.codebase-indexer/docs/` exists, collect high-value targets from docs.

2. Targeted file scan
- Always scan `.env*`, known config/credential files, and indexer-identified sensitive paths.
- Run critical patterns first, then high-confidence contextual patterns.

3. Git history scan (mode-dependent)
- `git rev-list --count HEAD` first.
- If `>500`, warn and default to targeted `-G`/`-S` scans.
- If `>2000`, require explicit user confirmation before full patch-history scan.

4. Report generation (`.sentinel/`)
- `security.md`
- `secrets-found.md` (only if findings > 0)
- `remediation.md` (only if findings > 0)

## Severity Guidance

- `CRITICAL`: active secret in tracked file or deploy config
- `HIGH`: secret found in git history or likely-active credential artifact
- `MEDIUM`: unverified credential-like string requiring manual review
- `LOW`: suppressed or placeholder-like hit

## Integration with Codebase Indexer

Use `.codebase-indexer/docs/` only for scan targeting:
- `architecture.md`: config/env locations
- `implementation.md`: modules where credentials are handled
- `patterns.md`: project conventions that affect false positives

Do not write Sentinel reports into `.codebase-indexer/docs/`.
