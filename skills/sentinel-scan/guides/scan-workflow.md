# Sentinel-Scan Workflow

## 0) Pre-scan

1. Read `.sentinel-ignore` (if present).
2. Read `.codebase-indexer/docs/architecture.md` and `implementation.md` (if present).
3. Build a focused target list:
- `.env*`
- `**/*credentials*`
- `**/*secret*`
- files/dirs called out in index docs

## 1) Quick scan (working tree)

Use executable commands (examples):

```bash
# target discovery
rg --files -g '**/.env*' -g '**/*config*' -g '**/*credentials*' -g '**/*secret*'

# critical token patterns (pcre2 for modern regex)
rg -n --pcre2 'sk-(proj-|svcacct-)?[A-Za-z0-9_-]{48,}'
rg -n --pcre2 'gh[pousr]_[A-Za-z0-9]{36}'
rg -n --pcre2 'AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}'
rg -n --pcre2 'sk_(live|test)_[A-Za-z0-9]{24}'
rg -n --pcre2 '-----BEGIN(?: [A-Z]+)? PRIVATE KEY-----'
```

## 2) Full scan additions

```bash
# broad but still file-based
rg -n --pcre2 '(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*["\'\`][^"\'\`]{8,}["\'\`]'

# common connection strings
rg -n --pcre2 '(postgres|mysql|mongodb(?:\+srv)?|redis)://[^\s]+'
```

## 3) Git history scan

```bash
# size guard
git rev-list --count HEAD

# targeted history search first
git log --all -p -G 'sk-(proj-|svcacct-)?[A-Za-z0-9_-]{48,}'
git log --all -p -G 'gh[pousr]_[A-Za-z0-9]{36}'
git log --all -p -G 'AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}'

# optional deeper env history
git log --all -p --full-history -- '.env*'
```

Guardrails:
- If commits `>500`: warn + prefer targeted history scans.
- If commits `>2000`: require explicit confirmation before full patch-history scan.

## 4) Result handling

For each finding:
- file path
- line number
- matched detector
- masked value (`first4...last4`)
- severity
- suppression status (`[suppressed]` when matched by `.sentinel-ignore`)

## 5) Reporting

Write to `.sentinel/`:
- `security.md`
- `secrets-found.md` (if findings)
- `remediation.md` (if findings)
