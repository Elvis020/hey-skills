# Graph Integration Guide

When `.code-review-graph/graph.db` is present in the project root, code-review-graph MCP tools are available. Use them to replace expensive Glob/Grep scans with pre-computed graph queries.

## Detection

Check once at the start of every run:

```
.code-review-graph/graph.db exists?
  ├─ yes → graph_available = true  (follow this guide)
  └─ no  → graph_available = false (use Glob/Grep as normal)
```

If the graph exists but MCP tools return an error (graph stale, server not running), fall back to Glob/Grep silently and set `graph_available = false` in the stats entry.

---

## Tool Reference

| MCP Tool | Use it when | Replaces |
|---|---|---|
| `get_impact_radius_tool()` | Update Mode Step 3 — finding what a change affects | Glob/Grep on changed files + neighbors |
| `get_review_context_tool()` | Update Mode Step 3 — getting source snippets for changed areas | Reading individual changed files |
| `query_graph_tool(pattern, target)` | Looking up callers, callees, tests, or dependents of a specific function/class | Grep for function name across codebase |
| `semantic_search_nodes_tool(query)` | Initial Scan Step 2 — finding key abstractions by concept | Grep for `class`, `interface`, `def`, `func` |
| `list_graph_stats_tool()` | Verifying graph health before relying on it | — |
| `build_or_update_graph_tool()` | If graph is stale (last_updated is old) before running Update Mode | — |

### `query_graph_tool` patterns

| Pattern | Returns |
|---|---|
| `callers_of` | All functions that call the target |
| `callees_of` | All functions the target calls |
| `tests_for` | Test functions covering the target |
| `imports_of` | Files the target imports |
| `importers_of` | Files that import the target |
| `inheritors_of` | Classes that extend the target |
| `file_summary` | All nodes defined in a file |

---

## How to use in each mode

### Phase 1: Initial Indexing

In Step 2 (Scan the Codebase), if graph is available:
- Use `semantic_search_nodes_tool` to find key abstractions (classes, functions, entry points) instead of broad Grep patterns.
- Use `query_graph_tool(pattern="file_summary", target=<entry_file>)` to map what a key file exports.
- Use `query_graph_tool(pattern="tests_for", target=<function_name>)` to populate the ## Test Coverage table in `implementation.md` — this gives exact test coverage data per function.
- Still read manifest files and config directly — the graph covers code structure, not project metadata.

### Phase 2: Update Mode

In Step 3, replace the Glob/Grep neighborhood scan entirely:

```
1. get_impact_radius_tool()
   → impacted_nodes: list of affected functions/classes
   → impacted_files: list of files to be aware of
   → test_coverage: which changed functions have/lack tests

2. get_review_context_tool()
   → changed_files: source snippets for changed areas
   → review_guidance: test gaps, wide-impact warnings
```

Use the `impacted_files` list to decide which doc sections need updating (same logic as today, but the list comes from the graph instead of manual scanning).

### Code Review (bonus: no additional skill invocation needed)

If the user asks for a code review after a change, and the graph is available:
- `get_review_context_tool()` already provides the minimal review set.
- `query_graph_tool(pattern="tests_for", target=<changed_fn>)` checks test coverage per function.
- Report missing tests explicitly in your update summary.

---

## Fallback rules

- If a tool call errors → fall back to Glob/Grep for that step, do not abort.
- If `list_graph_stats_tool()` shows `last_updated` is more than 24 hours old → call `build_or_update_graph_tool()` (incremental) before relying on impact data.
- Never hallucinate graph results — if a tool returns empty, say "not found in graph" and fall back to Grep.
