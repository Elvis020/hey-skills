# Phase 2 — Update Mode

Follow these steps after a feature or bugfix. Read templates from `templates/` when updating doc files.

## Step 1: Read Existing Docs

Use **Read** on each file in `.codebase-indexer/docs/`. Understand what is already documented.

## Step 2: Identify What Changed

Prefer the merge-base form to correctly handle merge commits and squash merges:

```bash
git diff --name-only $(git merge-base HEAD HEAD~1)..HEAD
```

Fallback if merge-base fails (simple linear history):

```bash
git diff HEAD~1 --name-only
```

> **Note:** `HEAD~1` breaks on merge commits (returns the second parent diff) and on squash merges (shows the entire branch as one commit). The merge-base form handles both cases correctly.

Note which modules/packages were touched.

## Step 3: Identify Affected Files and Blast Radius

**If `graph_available = true` (`.code-review-graph/graph.db` exists):**

Call the MCP tools instead of Glob/Grep:
1. `get_impact_radius_tool()` — returns the exact set of nodes and files affected by the changes (callers, dependents, inheritors, tests). No manual file scanning needed.
2. `get_review_context_tool()` — returns source snippets for changed areas plus structural review guidance.

This replaces the entire Glob/Grep neighborhood scan and costs ~300 tokens vs. 2,000–8,000 for manual scanning.

**If `graph_available = false`:**

Use signal-first extraction from `guides/signal-first-ir.md` on changed files. Before editing docs, build a compact delta context for each changed file:
1. File path
2. Changed lines/behaviors
3. Nearby control-flow context
4. Impacted functions/modules

Drive doc edits from this delta context. Only read exact raw source when the delta is insufficient to determine a factual doc update.

Then perform a depth-1 impact expansion (no graph tooling required):
1. For each changed source file `X`, identify likely importers/dependents using focused grep (module path, exported symbol names, package import aliases)
2. Add those files as "depth-1 affected" candidates
3. Review only their structure-level context (L0/L1); do not deep-read all transitive neighbors

Use this depth-1 set to avoid stale docs when direct consumers changed implicitly.

Optional helper — suggest these commands to the user (do not run autonomously):
```bash
python3 ~/.claude/skills/codebase-indexer/scripts/delta_context.py --repo . --files <changed-file-1> <changed-file-2>
```
or from a diff pipe:
```bash
git diff -- <changed-file> | python3 ~/.claude/skills/codebase-indexer/scripts/delta_context.py
```

## Step 4: Update Relevant Doc Files

| Changed area | Update these files |
|---|---|
| New module or package | `architecture.md`, `implementation.md` |
| New class / function / endpoint | `implementation.md` (run matching priority, then add to ## Test Coverage with test file or "— no test found") |
| Renamed files or folders | `architecture.md`, `patterns.md` |
| New dependency added | `architecture.md` |
| New naming or code pattern | `patterns.md` |
| Frequent co-change pair emerged from recent commits | `patterns.md` (refresh ## Co-Change Coupling) |
| Security-sensitive finding (secret/debug artifact/risky pattern) | `changelog.md` and optionally `decisions.md` if architectural |
| Architectural decision | `decisions.md` (see step 5) |
| Test file added or removed | Re-map ## Test Coverage in `implementation.md` (see below) |
| Cross-repo import or HTTP call added/removed | Refresh ## Cross-Repo References in `implementation.md` (see below) |
| Changed entry points (startup/router handlers) | Refresh ## Execution Entry Map in `architecture.md` |
| Changed schema/spec/deploy artifacts (`sql`, `prisma`, `openapi`, `docker-compose`) | Refresh ## Multi-Layer Context Artifacts in `architecture.md` |

**Test file added or removed:**

When a test file is added, removed, or modified:
1. Read the changed test file
2. Extract `describe`/`it` block names and import statements
3. Match those against source modules:
   - Import scan: read test file imports to identify which source modules it covers (test → source)
   - Describe/it block names: grep for function/class names that match source module symbols
4. Add new rows for newly covered functions, remove rows pointing to deleted test files

> **Import scan (same mechanism, two directions):** In initial scan Step 4, Claude greps test files for imports of the source file path (source → test). In update mode, Claude reads the changed test file's imports to identify which source modules it covers (test → source). Same signal, opposite traversal direction.

**Cross-repo import or HTTP call changed:**

When imports or HTTP client calls change to/from a workspace repo:
1. Read `../workspace.md` to refresh registry context
2. Re-scan the changed file to identify the new/removed cross-repo references
3. Update ## Cross-Repo References in `implementation.md` — add new rows, remove deleted

If `workspace_available = false` → skip this section entirely.

Apply targeted edits — do not rewrite unaffected sections.

For `patterns.md`, refresh co-change coupling when recent git history indicates new strong file pairs.
Optional helper — suggest to the user (do not run autonomously):
```bash
python3 ~/.claude/skills/codebase-indexer/scripts/coupling_report.py --repo . --max-commits 200 --top 10
```

**Budget-aware update packing (critical):**
- Detailed context for changed files and depth-1 dependents
- Structure-only context for unaffected modules
- Prefer high-risk/high-churn modules when budget is tight
- Keep updates deterministic: the same diff should produce the same doc edit scope

Optional helper — suggest to the user (do not run autonomously):
```bash
python3 ~/.claude/skills/codebase-indexer/scripts/context_packer.py --root . --budget 3000 --changed <csv-paths>
```

## Step 5: Decisions Gate

Ask: **"Did this change involve making or reversing an architectural decision?"**

| Change | Update decisions.md? |
|---|---|
| Added new API endpoint | No |
| Switched REST to GraphQL | **Yes** |
| Fixed a null pointer bug | No |
| Replaced ORM after performance issues | **Yes** — e.g., "chose JOOQ over Hibernate due to N+1 problems" |
| Added a new service module | Only if the structural choice was deliberate |

If yes — read `templates/decisions.md` for the ADR format, then:
1. Run git log inference to populate **Why (inferred):**
   - Scope: `git log --oneline -50 -- <changed_file>` for each file touched by the decision
   - Same quality gate as initial scan: signal words (at minimum — use judgment on related terms): fix, perf, slow, OOM, replace, migrate, because, due to, bottleneck, latency, crash, deprecated, compliance, or issue/PR references (#123, fixes, closes)
   - If no signal found: set to "`— not determinable from git history`"
   - Never hallucinate a reason
2. Append entry to `decisions.md`

If no — skip `decisions.md`.

## Step 6: Append Changelog Entry

Always append a new dated entry to `.codebase-indexer/docs/changelog.md`:

```markdown
## YYYY-MM-DD — [brief description]
- What changed
- Which modules were affected
```

## Step 7: Log Stats

Read `guides/stats-logging.md` and append one entry to `stats/runs.jsonl`, then output the inline savings card.

- `mode`: `"update"`
- `docs_generated`: count of doc files that were actually edited this run
- `docs_skipped`: 0
- `project_files`: reuse the approximate count from the existing `.codebase-indexer/docs/` files (e.g. from `architecture.md` or `implementation.md` scope notes), or from the original scan — do not re-count the whole project
- `tokens_saved_this_run`: `12000` if `graph_available = false`; `17000` if `graph_available = true`
- `tokens_saved_future_est`: `0` — update runs maintain existing savings, they do not create new recurring ones
- `cost_saved_est_usd`: `tokens_saved_this_run / 1_000_000 * 3.0` (future_est is 0 so omit it from the sum)
- `graph_available`: `true` if `.code-review-graph/graph.db` was present and used, `false` otherwise
- `project_root`: absolute project root path
- `tokens_raw_baseline_est`: computed from update baseline table in stats-logging guide
- `tokens_indexer_run_est`: `max(0, tokens_raw_baseline_est - tokens_saved_this_run)`
- `measurement_quality`: `"estimated"` unless exact telemetry is available

Also append the same entry to `<project-root>/.codebase-indexer/savings.jsonl` for project-local savings reports.

## Step 8: Always Generate Savings Reports (Required)

At the end of every successful update run, generate savings outputs by default:
1. Print project-local terminal savings comparison
2. Create a new timestamped HTML report under `.codebase-indexer/reports/`

Run:

```bash
python3 ~/.claude/skills/codebase-indexer/scripts/savings_report.py --project-root . --format both --output .codebase-indexer/reports/codebase-indexer-savings.html --timestamp-html yes
```

This must run for every successful indexer update; do not make it optional.
