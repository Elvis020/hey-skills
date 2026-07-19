# Stats Logging

After every successful run (any mode), append one entry to both stats logs and output an inline savings card to the user.

## Log file locations

```
~/.claude/skills/codebase-indexer/stats/runs.jsonl
<project-root>/.codebase-indexer/savings.jsonl
```

Create files if they do not exist. Never overwrite — always append.

- Global log (`~/.claude/.../runs.jsonl`) supports cross-project intelligence.
- Project log (`.codebase-indexer/savings.jsonl`) powers `/codebase-indexer savings` and HTML export for the current repo.

---

## Entry format

One JSON object per line (JSONL). Fields:

| Field | Type | Description |
|---|---|---|
| `date` | string | ISO date of the run, e.g. `"2026-03-13"` |
| `project` | string | Basename of the working directory, e.g. `"event-mapper-v2"` |
| `project_root` | string | Absolute root path of the project (strict project-local filtering key) |
| `mode` | string | `"full"`, `"supplement"`, `"update"`, or `"benchmark_measured"` (manual A/B demo run) |
| `docs_generated` | number | Count of doc files written this run |
| `docs_skipped` | number | Count of doc files skipped (2 for supplement, 0 otherwise) |
| `project_files` | number | Approximate number of source files in the project (exclude node_modules, dist, etc.) |
| `tokens_raw_baseline_est` | number | Estimated tokens for comparable no-index/raw-code workflow |
| `tokens_indexer_run_est` | number | Estimated tokens consumed by codebase-indexer run |
| `tokens_saved_this_run` | number | Tokens saved during this specific run |
| `tokens_saved_future_est` | number | Tokens saved per future session by having docs available |
| `cost_saved_est_usd` | number | Dollar estimate: `(tokens_saved_this_run + tokens_saved_future_est) / 1_000_000 * 3.0` |
| `graph_available` | boolean | `true` if `.code-review-graph/graph.db` was present and used |
| `measurement_quality` | string | `"measured"` if exact telemetry exists, else `"estimated"` |

---

## Token savings estimates

### `full` mode
- `tokens_saved_this_run`: `0`
- `tokens_saved_future_est`: scale by project size:
  | `project_files` | `tokens_saved_future_est` |
  |---|---|
  | < 50 | `8000` |
  | 50–200 | `20000` |
  | 200–1000 | `45000` |
  | 1000+ | `90000` |

### `supplement` mode
- `tokens_saved_this_run`: `6000`
- `tokens_saved_future_est`: `35000`

### `update` mode
- `tokens_saved_this_run`:
  | `graph_available` | `tokens_saved_this_run` |
  |---|---|
  | false | `12000` |
  | true | `17000` |
- `tokens_saved_future_est`: `0`

### Cost estimate formula
```
cost_saved_est_usd = round((tokens_saved_this_run + tokens_saved_future_est) / 1_000_000 * 3.0, 4)
```

---

## Baseline-vs-Indexer Comparison Fields

To prevent user guesswork, always log explicit comparison numbers.

### `tokens_raw_baseline_est`
Estimated tokens for comparable no-index/raw workflow.

- For `full` and `supplement`:
  | `project_files` | `tokens_raw_baseline_est` |
  |---|---|
  | < 50 | `12000` |
  | 50–200 | `30000` |
  | 200–1000 | `75000` |
  | 1000+ | `160000` |

- For `update`:
  | `project_files` | `tokens_raw_baseline_est` |
  |---|---|
  | < 50 | `9000` |
  | 50–200 | `22000` |
  | 200–1000 | `42000` |
  | 1000+ | `70000` |

### `tokens_indexer_run_est`
```
tokens_indexer_run_est = max(0, tokens_raw_baseline_est - tokens_saved_this_run)
```

### `measurement_quality`
- Use `"measured"` only when exact run token telemetry is available.
- Otherwise use `"estimated"` and keep formulas deterministic.

---

## How to append

1. Read both files first (they may not exist — that's fine).
2. Append the same JSON object to:
   - global log: `~/.claude/skills/codebase-indexer/stats/runs.jsonl`
   - project log: `<project-root>/.codebase-indexer/savings.jsonl`
3. If either file does not exist, create it with the new entry as the first line.

---

## Inline savings card (required after every run)

After logging, output a `concord-index-summary` JSON block.

Output exactly this (fill in values, no extra text around the block):

```concord-index-summary
{"project":"<project>","mode":"<mode>","project_files":<project_files>,"docs_generated":<docs_generated>,"tokens_saved_this_run":<tokens_saved_this_run>,"tokens_saved_future_est":<tokens_saved_future_est>,"cost_saved_est_usd":<cost_saved_est_usd>}
```

Immediately after the block, print a one-line comparison receipt:

```
Comparison: raw baseline ~<tokens_raw_baseline_est> tokens vs indexer ~<tokens_indexer_run_est> tokens -> saved now <tokens_saved_this_run> tokens.
```

---

## Example entries

```json
{"date":"2026-03-14","project":"fastapi-backend","project_root":"/work/fastapi-backend","mode":"full","docs_generated":5,"docs_skipped":0,"project_files":312,"tokens_raw_baseline_est":75000,"tokens_indexer_run_est":75000,"tokens_saved_this_run":0,"tokens_saved_future_est":45000,"cost_saved_est_usd":0.135,"graph_available":false,"measurement_quality":"estimated"}
{"date":"2026-03-14","project":"fastapi-backend","project_root":"/work/fastapi-backend","mode":"update","docs_generated":2,"docs_skipped":0,"project_files":312,"tokens_raw_baseline_est":42000,"tokens_indexer_run_est":25000,"tokens_saved_this_run":17000,"tokens_saved_future_est":0,"cost_saved_est_usd":0.051,"graph_available":true,"measurement_quality":"estimated"}
```

---

## What NOT to log

- Runs that failed or were abandoned mid-way
- Dry runs or planning-only sessions where no files were written
