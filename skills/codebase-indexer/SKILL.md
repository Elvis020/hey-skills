---
name: codebase-indexer
description: "Use when opening an existing codebase for the first time, or after completing a feature or bugfix — generates and maintains .codebase-indexer/docs/ index files so the agent does not re-scan the whole codebase each session."
---

# Codebase Indexer

Scan a project once, write five lean doc files to `.codebase-indexer/docs/`, and read them every future session instead of re-scanning the whole codebase. After each feature or bugfix, update only what changed.

Default behavior policy:
- Savings reporting is automatic after every successful index/update run (terminal + timestamped HTML).
- Benchmarking is explicit/manual only (`/codebase-indexer benchmark ...`) and never auto-runs.

## Mode Detection

Before executing any mode, check for workspace context:

```
../workspace.md exists?
  ├─ yes → workspace_available = true. Read `guides/multi-repo.md` before executing the chosen mode.
  └─ no  → workspace_available = false
```

Then detect index docs presence:

```
`.codebase-indexer/docs/` exists?
  ├─ yes → Signal present?
  │          ├─ yes → Phase 2: Update Mode
  │          └─ no  → Ask: "Re-index from scratch, or update from recent changes?"
  └─ no  → Comprehensive AGENTS.md or equivalent project instructions exists?
             ├─ yes → Supplement Mode (gap docs only)
             └─ no  → Phase 1: Initial Indexing (all 5 docs)
```

Before entering indexing/update modes, check savings-report intent:

```
User asks "/codebase-indexer benchmark" (or "benchmark raw vs indexer")?
  ├─ yes → Benchmark Mode (measured A/B, project-local, then terminal/HTML report)
  └─ no  → continue
```

Then check savings-report intent:

```
User asks "/codebase-indexer savings" (or "show savings")?
  ├─ yes → Savings Mode (project-local report, no indexing)
  └─ no  → continue mode detection below
```

**In all modes:** Check for `.code-review-graph/graph.db` in the project root.
- If present → `graph_available = true`. Read `guides/graph-integration.md` before executing the chosen mode.
- If absent → `graph_available = false`. Proceed with Glob/Grep as normal.

**In all modes (signal-first):** Read `guides/signal-first-ir.md` and prefer AST-first, tiered summaries for code understanding.
- If AST/IR extraction is feasible in the current environment → use it for structure/control-flow extraction before raw file reads.
- If AST/IR extraction is not feasible → emulate the same tiers with focused Grep/Read and continue.

**Phase 2 signals:** user says "update docs", "re-index", "update", or just finished a feature/bugfix.

**Comprehensive AGENTS.md or equivalent project instructions:** A AGENTS.md or equivalent project instructions that already documents architecture, directory structure, key abstractions, and conventions. Read it and judge — if it covers what `architecture.md` and `implementation.md` would contain, use Supplement Mode.

## Execution

| Mode | Read this guide |
|------|----------------|
| Benchmark request | Read `guides/stats-report.md` and run measured A/B benchmark (`benchmark_measured`) with requested output mode |
| Savings report request | Read `guides/stats-report.md` and generate project-local terminal or HTML comparison |
| No `.codebase-indexer/docs/`, no comprehensive AGENTS.md or equivalent project instructions | Read `guides/initial-scan.md` — generate all 5 docs |
| No `.codebase-indexer/docs/`, comprehensive AGENTS.md or equivalent project instructions exists | Read `guides/initial-scan.md` Step 0 — generate gap docs only (`patterns.md`, `decisions.md`, `changelog.md`) |
| `.codebase-indexer/docs/` exists, update after changes | Read `guides/update-mode.md` and follow it |

Both guides reference templates in `templates/` — read those when generating or updating doc files.

## File Map

```
<agent-skills-directory>/codebase-indexer/
  SKILL.md                        ← you are here
  guides/
    initial-scan.md               ← Phase 1: full scan steps
    update-mode.md                ← Phase 2: diff-based update steps
    signal-first-ir.md            ← AST-first/tiered extraction + budgeted context packing
    gitignore-rules.md            ← .gitignore handling
    graph-integration.md          ← how to use code-review-graph MCP tools when available
    multi-repo.md                 ← cross-repo workspace detection and lookup
    stats-logging.md              ← how to append a run entry to stats/runs.jsonl
    stats-report.md               ← how to summarize stats when user asks
  templates/
    architecture.md               ← template for .codebase-indexer/docs/architecture.md
    implementation.md             ← template for .codebase-indexer/docs/implementation.md
    patterns.md                   ← template for .codebase-indexer/docs/patterns.md
    decisions.md                  ← template for .codebase-indexer/docs/decisions.md
    changelog.md                  ← template for .codebase-indexer/docs/changelog.md
    workspace.md                  ← template for workspace.md registry
  scripts/
    context_packer.py             ← deterministic L0/L1/L3 budget-aware context packing
    delta_context.py              ← deterministic L2-style diff summarization
    query_context.py              ← prompt-driven retrieval + packing (auto file selection)
    coupling_report.py            ← git co-change file coupling report for hidden dependency signals
    savings_report.py             ← project-local savings report generator (terminal or HTML)
  stats/
    runs.jsonl                    ← append-only log of every indexer run (auto-created)
```

**Stats and Savings (always-on):** After every successful run, append entries to global/project-local logs, print a terminal savings comparison, and generate a new timestamped HTML savings report in `.codebase-indexer/reports/`. Savings reporting is required at end-of-run, not optional.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Generating all 5 docs when a comprehensive AGENTS.md or equivalent project instructions exists | Run Step 0 — supplement mode generates only 3 gap docs |
| Auto-running `git diff` without checking AGENTS.md or equivalent project instructions policies | Suggest the command to the user; never run autonomously unless project allows it |
| Writing indexer docs into project-owned `docs/` | Always use `.codebase-indexer/docs/` to avoid collisions |
| Using `git diff HEAD~1` on merge or squash commits | Use `git diff --name-only $(git merge-base HEAD HEAD~1)..HEAD` |
| Re-scanning the full codebase in Update Mode | If graph available, use `get_impact_radius_tool`; else scope to changed files and direct neighbors |
| Reading raw source for every file in initial scan | Use signal-first IR/tiered extraction first; only drill into raw code for unresolved ambiguity |
| Sending equal detail for all files in update mode | Use budget-aware packing: changed/hotspot files detailed, others structure-only |
| Duplicating `.gitignore` entry | Always read first, append only if absent |
| Rewriting whole doc files on update | Edit only the sections corresponding to changed modules |
| Adding ADR for every change | Gate on "was this an architectural decision?" — most changes are not |
| Scanning `node_modules`, `target/`, `dist/` | Exclude build artifacts from all globs |
| Using a flat `tokens_saved_est` number regardless of project size | Use `tokens_saved_future_est` scaled by `project_files` per the table in stats-logging.md |
| Inventing details not found in scan | Say "not determinable from scan" rather than guessing |
| Updating docs after every small change | Update at natural checkpoints — before commit, before PR, or when explicitly asked |
| Running `scripts/context_packer.py` or `scripts/delta_context.py` autonomously | Suggest the command to the user — do not run shell scripts without being asked |
| Treating savings reporting as optional | Always run end-of-run savings generation (terminal + timestamped HTML) after successful indexing/update |
