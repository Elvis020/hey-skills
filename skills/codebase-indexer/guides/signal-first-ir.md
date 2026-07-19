# Signal-First IR Guide

Use this guide in all modes to reduce token usage while preserving understanding.

## Goal

Extract meaning before syntax:
- capture structure, API surface, and control flow first
- defer raw code reads to only the places where exact text is required

This mirrors an AST-first workflow but does not require a specific external product.

---

## Four-Tier Extraction Model

Classify information into four tiers while scanning:

| Tier | Action | Keep / Drop |
|---|---|---|
| Tier 1 | Keep | imports, exports, functions, classes, interfaces, types, enums |
| Tier 2 | Keep | control flow: `if`, `switch`, loops, `return`, `throw`, `try/catch` |
| Tier 3 | Compress | assignments/variables/auxiliary statements as one-liners |
| Tier 4 | Drop | punctuation/formatting noise, long literal bodies, comments unless structural |

When uncertain whether something is Tier 3 or Tier 4, prefer compression (Tier 3) over dropping.

---

## Layers for Context Packing

Use three practical context layers:

| Layer | Purpose | Typical use |
|---|---|---|
| L0 | Structure map only | broad repo coverage and inventory |
| L1 | Compressed behavior view | architecture/implementation understanding |
| L2 | Delta-focused context | update mode after changes |

Use raw source only as a temporary precision layer when required.

## Helper Scripts (optional but recommended)

These scripts live in the codebase-indexer skill directory. Do not run them autonomously — suggest the commands to the user.

1. Budget-aware packing (L0/L1/L3):
```bash
python3 ~/.claude/skills/codebase-indexer/scripts/context_packer.py --root . --budget 4000
```

2. Delta-first context (L2-style) from changed files:
```bash
python3 ~/.claude/skills/codebase-indexer/scripts/delta_context.py --repo . --files path/to/file1 path/to/file2
```

3. Delta-first context from stdin diff:
```bash
git diff -- path/to/file | python3 ~/.claude/skills/codebase-indexer/scripts/delta_context.py
```

4. Prompt-driven retrieval + packing (no manual grep workflow):
```bash
python3 ~/.claude/skills/codebase-indexer/scripts/query_context.py --root . --query "user request here" --budget 3500
```

---

## Budget-Aware Packing

When context is limited:
1. Reserve detailed (L1) budget for changed files, entry points, and hotspots.
2. Keep the rest at L0 so coverage is not lost.
3. For update mode, prefer L2 for changed files and L0/L1 for neighbors.
4. If one target file needs exact code, read raw for that file only; keep surrounding files compressed.

Target outcome: high-confidence docs without full-repo raw reads.

---

## Health and Security Signals

During scan/update, tag modules with lightweight risk signals when evidence exists:

- **High churn** — file appears frequently in recent `git log` with "fix", "patch", "hotfix" in commit messages
- **Weak test coverage** — key functions absent from `## Test Coverage` table or marked `— no test found`
- **Hardcoded secrets** — string literals matching patterns like `API_KEY =`, `SECRET =`, `password =`, `token =`, `private_key =`, or values resembling keys (long alphanumeric strings assigned to credential-named variables)
- **Debug artifacts** — `console.log(`, `debugger;`, `print(`, `TODO: remove`, `FIXME`, `pdb.set_trace()` in non-test production files

When a signal is found, note it in `.codebase-indexer/docs/changelog.md` under the current date. Only escalate to `.codebase-indexer/docs/decisions.md` if the finding requires an architectural response.

---

## Fallback Rules

- If parser/AST tooling is unavailable, emulate the same tiering with focused Grep/Read.
- If a structured summary conflicts with source details, source-of-truth is raw code.
- Never invent missing details; write "not determinable from scan" where needed.
- Always prefer deterministic, repeatable extraction over ad-hoc deep dives.
