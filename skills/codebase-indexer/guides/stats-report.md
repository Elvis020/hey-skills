# Savings Report

Use this guide when the user asks for savings visibility, especially:
- `/codebase-indexer savings`
- `/codebase-indexer savings terminal`
- `/codebase-indexer savings html`
- `/codebase-indexer benchmark`
- `/codebase-indexer benchmark terminal`
- `/codebase-indexer benchmark html`
- `/codebase-indexer benchmark both`
- "show savings", "token savings report", "did this help"
- "benchmark raw vs indexer", "measured A/B"

Default scope is **current project only**.

Note: savings reporting is also generated automatically at the end of every successful indexer run (terminal + timestamped HTML). This guide also covers on-demand re-generation.

---

## Data source (project-local)

Read:

```
<project-root>/.codebase-indexer/savings.jsonl
```

Each line is one JSON object from successful indexing runs.

If file is missing or empty, tell the user:
> "No project-local savings logged yet. Run /codebase-indexer to create your first savings record."

---

## Output modes

### Terminal mode (default)

Show a compact, confidence-aware comparison:

```
Codebase Indexer Savings (Project)
Project            : <name>
Path               : <abs path>
Period             : <first_date> -> <last_date>
Runs               : <n>

A/B This Run (Raw Rescan vs Indexer)
Raw rescan counterfactual : <tokens>
Indexer path              : <tokens>
Saved this run     : <tokens>
Future est benefit : <tokens>
Mode / Graph       : <mode> / <yes|no>

Cumulative Savings
Saved this-run     : <tokens>
Saved future-est   : <tokens>
Saved total        : <tokens>
Estimated cost     : $<cost>

Breakdown by Mode
full               : x<n> <tokens>
supplement         : x<n> <tokens>
update             : x<n> <tokens>

Measurement Quality
Measured runs      : <n>
Estimated runs     : <n>
Method note        : Estimated values follow codebase-indexer sizing heuristics.
```

### HTML mode

Generate:

```
<project-root>/.codebase-indexer/reports/codebase-indexer-savings-YYYYMMDD-HHMMSS.html
```

Requirements:
- polished, legible visual summary
- clear baseline vs indexer comparison cards
- mode contribution chart
- recent runs table
- explicit methodology/quality footnote

---

## Recommended helper script

Use:

```bash
python3 scripts/savings_report.py --project-root . --format terminal
python3 scripts/savings_report.py --project-root . --format html
python3 scripts/savings_report.py --project-root . --format both --output .codebase-indexer/reports/codebase-indexer-savings.html --timestamp-html yes
```

If HTML mode is requested, return the output path.

---

## Benchmark intent mapping

Treat benchmark phrases as command intents:

- `/codebase-indexer benchmark` -> measured benchmark + terminal report
- `/codebase-indexer benchmark terminal` -> measured benchmark + terminal report
- `/codebase-indexer benchmark html` -> measured benchmark + HTML report path
- `/codebase-indexer benchmark both` -> measured benchmark + terminal + HTML path

Implementation sequence:
1. Run measured benchmark (`savings_benchmark.py`) and append entry.
2. Render via savings report (`savings_report.py`) in requested format.

If no output mode is specified, default to terminal.

---

## Measured A/B Benchmark (demo-safe)

When the user wants a true measured comparison (not heuristic estimate), run:

```bash
python3 scripts/savings_benchmark.py --project-root . --append yes
python3 scripts/savings_report.py --project-root . --format both --output .codebase-indexer/reports/codebase-indexer-savings.html --timestamp-html yes
```

This writes a `benchmark_measured` row to the project-local log where:
- `tokens_raw_baseline_est` is measured from source files
- `tokens_indexer_run_est` is measured from docs index files (or falls back to raw when docs are missing)
- `measurement_quality` is `measured`
- `indexer_context_mode` is:
  - `docs_path` when docs exist
  - `fallback_raw` when docs are absent (expected saved-now ~= 0)

Use this mode in live demos when you need hard A/B evidence.

---

## Accuracy and trust rules

1. Never present estimates as exact telemetry.
2. Always include measurement quality (`measured` vs `estimated`).
3. Show both:
   - raw-rescan counterfactual baseline
   - indexer path
   - savings this run
   - future estimated savings
4. Keep project scope strict: only entries whose `project_root` matches current root.
5. If comparison fields are missing in legacy rows, compute deterministic fallbacks and label them estimated.
