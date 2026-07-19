# Phase 1 — Initial Indexing

Follow these steps in order. Read templates from `templates/` when generating each doc file.

## Step 0: Check for Existing CLAUDE.md (Dedup Gate)

Read `CLAUDE.md` if it exists. Ask yourself: does it already document architecture, directory structure, key abstractions, state management, routing, and conventions?

**If yes (comprehensive CLAUDE.md) → Supplement Mode:**
- Skip generating `.codebase-indexer/docs/architecture.md` and `.codebase-indexer/docs/implementation.md` — they would duplicate what CLAUDE.md already covers and create two sources of truth that will drift.
- Only generate: `.codebase-indexer/docs/patterns.md`, `.codebase-indexer/docs/decisions.md`, `.codebase-indexer/docs/changelog.md`
- Tell the user: "CLAUDE.md already covers architecture and implementation. Generating only gap docs: patterns, decisions, changelog."
- Jump to Step 3 (generating only the 3 gap files), then continue from Step 4.

**If no CLAUDE.md, or it's minimal → Full Mode:**
- Proceed with all steps below and generate all 5 docs.

---

## Step 1: Detect Project Type

Check for project manifests (use Glob/Read):

| Manifest | Stack |
|----------|-------|
| `package.json` | Node.js / JavaScript / TypeScript |
| `pom.xml` | Maven / Java |
| `build.gradle` / `build.gradle.kts` | Gradle / Java / Kotlin |
| `go.mod` | Go |
| `requirements.txt` / `pyproject.toml` / `setup.py` | Python |
| `Cargo.toml` | Rust |
| `*.csproj` / `*.sln` | .NET / C# |
| `composer.json` | PHP |

Multiple manifests = polyglot/monorepo — note all detected stacks.

## Step 2: Scan the Codebase

Use **signal-first extraction** from `guides/signal-first-ir.md`:

1. Generate a structure-first view (L0-equivalent) for broad file coverage
2. Generate a behavior view (L1-equivalent) for entry points, core modules, and hotspots
3. Fall back to targeted Glob/Grep/Read only when details are not determinable from the structured view

Then use **Glob** and **Grep** (not Bash find/ls) to fill any remaining gaps:

| What to find | How |
|---|---|
| Directory structure (3 levels max) | `Glob **/*` then collapse paths |
| Entry points | `Grep` for `main`, `app`, `index`, `server`, `Application` |
| Key abstractions | `Grep` for `class`, `interface`, `export`, `func`, `def` |
| Config files | `Glob` for `*.env*`, `*.config.*`, `application.yml`, `application.properties` |
| External deps | Read manifest + lockfile (`package-lock.json`, `go.sum`, `pom.xml` deps) |
| Routing / API | `Grep` for `@GetMapping`, `router.get`, `app.get`, `path=` |
| Test files | `Glob` for `**/*.test.*`, `**/*.spec.*`, `**/__tests__/**`, `**/test/**` |
| Multi-layer artifacts | `Glob` for `**/*.sql`, `**/schema.prisma`, `**/openapi*.{yaml,yml,json}`, `**/docker-compose*.{yaml,yml}` |

Apply the four-tier model from `guides/signal-first-ir.md` to all extracted content. If details matter for docs correctness (e.g., dependency names, endpoint paths), read the exact source line before writing docs.

**Execution Entry Map (required):**

Build a compact map of executable entry points and public ingress points for `architecture.md`.
Search for stack-specific bootstrap markers, including:
- `main(`, `if __name__ == "__main__":`, `app.listen(`, `server.listen(`
- `@app.route`, `@router.get`, `@router.post`, `router.get(`, `router.post(`
- `@GetMapping`, `@PostMapping`, `@RequestMapping`, `public static void main`
- `export default function` for framework entry handlers

For each confirmed entry point, capture:
1. Path + symbol
2. Entry type (`CLI`, `HTTP`, `Worker`, `Scheduler`, or `Unknown`)
3. One-line note describing role

Only include entries confirmed from source; do not infer missing handlers.

**Multi-layer context artifacts (required):**

Capture non-code artifacts that shape behavior:
1. Database schema: `*.sql`, `schema.prisma`
2. API contracts: `openapi*.yaml|yml|json`
3. Runtime topology: `docker-compose*.yaml|yml`

Record these in `architecture.md` under "Multi-Layer Context Artifacts" with location and why they matter.
If absent, write "`— not found in scan`" for that artifact class.

**Git co-change coupling (recommended for patterns):**

Use recent git history to capture files that frequently evolve together. This reveals hidden dependencies useful for onboarding and safer edits.

Optional helper — suggest to the user (do not run autonomously):
```bash
python3 ~/.claude/skills/codebase-indexer/scripts/coupling_report.py --repo . --max-commits 400 --top 20
```

When available, populate "Co-Change Coupling (Git History)" in `patterns.md` with top high-signal pairs.
If history is unavailable/shallow, write "`— not determinable from git history`".

**Test Discovery Matching Priority:**

When mapping source modules to test files, use this priority ladder (stop at first match):

1. **Graph query** — if graph is available, call `query_graph_tool(pattern="tests_for", target=<function_name>)` for each key function
2. **Exact name match** — `auth.ts` → `auth.test.ts` or `auth.spec.ts`
3. **Substring match** — target name contained in test filename (e.g., `UserService.ts` → `user.test.ts`)
4. **Import scan** — grep test files for imports of the source file path (source → test)
5. **Fallback** — mark as "`— no test found`"

> **Import scan (same mechanism, two directions):** In initial scan Step 4, Claude greps test files for imports of the source file path (source → test). In update mode, Claude reads the changed test file's imports to identify which source modules it covers (test → source). Same signal, opposite traversal direction.

**Exclude:** `node_modules`, `.git`, `build/`, `dist/`, `target/`, `__pycache__`

Use patterns like `**/*.{ts,js,go,java,py,rs}` to limit scan depth.

**Budget-aware packing (large or polyglot projects):**

When project size is large or polyglot:
1. Prioritize detailed extraction (L1-equivalent) for: entry points, externally facing modules, and high-change files
2. Use structure-only extraction (L0-equivalent) for peripheral modules
3. Keep total context bounded; do not let one large file starve coverage of the rest of the project
4. If one target file requires exact code, read raw source only for that target and keep surrounding context in compact form

Optional helper — suggest this command to the user (do not run autonomously):
```bash
python3 ~/.claude/skills/codebase-indexer/scripts/context_packer.py --root . --budget 4000
```
Use the JSON output to decide which files get detailed review (L1) versus structure-only (L0) before writing docs.

**Step 2.5: Cross-Repo Detection (if workspace_available = true)**

If workspace is available, detect cross-repo calls:
1. Grep for imports from workspace namespace, HTTP calls to known services, gRPC stubs
2. Read `../workspace.md` to get the workspace registry
3. Match the target against the registry (repo name or description)
4. Record the target repo path and its `.codebase-indexer/docs/` location
5. If no match found → omit from cross-repo references (don't guess)

If `workspace_available = false` → skip this step entirely.

## Step 3: Generate Doc Files

Write all five files under `.codebase-indexer/docs/` in the project root:

1. Read `templates/architecture.md` → write `.codebase-indexer/docs/architecture.md`
2. Read `templates/implementation.md` → write `.codebase-indexer/docs/implementation.md`
3. Read `templates/patterns.md` → write `.codebase-indexer/docs/patterns.md`
4. Read `templates/decisions.md` → write `.codebase-indexer/docs/decisions.md`
5. Read `templates/changelog.md` → write `.codebase-indexer/docs/changelog.md`

**When generating `implementation.md`:**
- Populate the ## Test Coverage table using the test discovery results from Step 2
- Map each key function/module found in the scan to its test file using the matching priority
- Mark unmapped modules with "`— no test found`"
- If `workspace_available = true`, populate ## Cross-Repo References from Step 2.5 results
- If `workspace_available = false`, omit ## Cross-Repo References entirely

**When generating `decisions.md`:**
- For each ADR entry, run git log inference to populate **Why (inferred):**
- Scope: `git log --oneline -50 -- <architectural_file>` per relevant file
- Quality gate (critical): Only infer "why" when git log contains signal words (at minimum — use judgment on related terms): fix, perf, slow, OOM, replace, migrate, because, due to, bottleneck, latency, crash, deprecated, compliance, or issue/PR references (#123, fixes, closes)
- If no signal found: set to "`— not determinable from git history`"
- Never hallucinate a reason — only record evidence that exists in the log

Do not invent information — if something cannot be determined from the scan, say so explicitly.

## Step 4: Update .gitignore

Read `guides/gitignore-rules.md` and follow it.

## Step 5: Install Auto-Update Rules in CLAUDE.md

This is critical — it makes future doc updates automatic without re-invoking the skill.

1. Read `templates/claude-md-rules.md` to get the rules block.
2. Check if a `CLAUDE.md` exists in the project root.
   - If it exists: read it. If it already contains "Codebase Index" section, skip. Otherwise **append** the rules block to the end.
   - If it does not exist: **create** `CLAUDE.md` with the rules block.
3. Never duplicate — always check before writing.

After this step, Claude will automatically read docs at session start and update them after every feature/bugfix — no manual skill invocation needed.

## Step 6: Report

Tell the user:
- Which project type was detected
- Which files were created
- That CLAUDE.md now has auto-update rules installed
- One sentence summary (e.g., "Spring Boot REST API with 4 service modules and PostgreSQL.")
- Recommended setting (one-time): if `settings.json` does not already have `"ENABLE_TOOL_SEARCH": "true"`, mention it to the user:
  > "Tip: add `\"ENABLE_TOOL_SEARCH\": \"true\"` to your `~/.claude/settings.json` — defers unused tool schemas and cuts per-turn context by ~25k tokens."
  Only mention this once, during initial scan. Do not repeat in update mode.

## Step 7: Log Stats

Read `guides/stats-logging.md` and append one entry to `stats/runs.jsonl`, then output the inline savings card.

- `mode`: `"full"` if all 5 docs were generated, `"supplement"` if only 3 gap docs were generated
- `docs_generated`: count of files actually written this run
- `docs_skipped`: 2 if supplement mode, 0 if full mode
- `project_files`: approximate source file count from Step 2 scan (exclude node_modules, dist, etc.)
- `tokens_saved_this_run`: `0` for full, `6000` for supplement
- `tokens_saved_future_est`: use the project_files scale table in stats-logging.md for full; `35000` for supplement
- `cost_saved_est_usd`: `(tokens_saved_this_run + tokens_saved_future_est) / 1_000_000 * 3.0`
- `graph_available`: `true` if `.code-review-graph/graph.db` was present
- `project_root`: absolute project root path
- `tokens_raw_baseline_est`: computed from project size table in stats-logging guide
- `tokens_indexer_run_est`: `max(0, tokens_raw_baseline_est - tokens_saved_this_run)`
- `measurement_quality`: `"estimated"` unless exact telemetry is available

Also append the same entry to `<project-root>/.codebase-indexer/savings.jsonl` for project-local savings reports.

## Step 8: Always Generate Savings Reports (Required)

At the end of every successful indexing run, generate savings outputs by default:
1. Print project-local terminal savings comparison
2. Create a new timestamped HTML report under `.codebase-indexer/reports/`

Run:

```bash
python3 ~/.claude/skills/codebase-indexer/scripts/savings_report.py --project-root . --format both --output .codebase-indexer/reports/codebase-indexer-savings.html --timestamp-html yes
```

This must run for every successful indexer run; do not make it optional.
