---
name: understand-lite
description: "Build a low-token, deterministic structural knowledge graph for a repo using cheap scanning and import resolution, then save it in .understand-anything/ for the dashboard. Use when the user wants a lighter alternative to /understand, wants to analyze a repo cheaply, or mainly needs codebase structure rather than rich LLM-authored summaries."
---

# /understand-lite

Generate a lightweight structural graph for a codebase with minimal token usage.

This skill is intentionally cheaper than `/understand`:

- no batch LLM file analysis
- no LLM architecture phase
- no LLM tour-writing phase
- no function/class nodes in v1
- no domain or knowledge graph generation

It favors deterministic scan + import resolution and produces a dashboard-compatible `knowledge-graph.json`.

## What It Produces

Writes:

- `$PROJECT_ROOT/.understand-anything/knowledge-graph.json`
- `$PROJECT_ROOT/.understand-anything/meta.json`
- `$PROJECT_ROOT/.understand-anything/config.json`

The graph is structural and high-level:

- one node per file
- import edges between files when deterministically resolvable
- simple category layers (`Code`, `Config`, `Docs`, `Data & Contracts`, `Infrastructure`)
- simple guided tour based on README, entry points, major code directories, infra files, and large files

## Instructions

1. Resolve `PROJECT_ROOT`.
   - If `$ARGUMENTS` contains a non-flag token, treat it as the target directory.
   - Otherwise use the current working directory.
   - Verify it exists and is a directory. If not, stop with an error.

2. Resolve the plugin root using the same search order as `/understand`.
   - Prefer `${CLAUDE_PLUGIN_ROOT}`
   - Then `~/.understand-anything-plugin`
   - Then the symlink-resolved personal skill paths
   - Then common clone-based install roots

   Use:
   ```bash
   SKILL_REAL=$(realpath ~/.agents/skills/understand-lite 2>/dev/null || readlink -f ~/.agents/skills/understand-lite 2>/dev/null || echo "")
   SELF_RELATIVE=$([ -n "$SKILL_REAL" ] && cd "$SKILL_REAL/../.." 2>/dev/null && pwd || echo "")
   COPILOT_SKILL_REAL=$(realpath ~/.copilot/skills/understand-lite 2>/dev/null || readlink -f ~/.copilot/skills/understand-lite 2>/dev/null || echo "")
   COPILOT_SELF_RELATIVE=$([ -n "$COPILOT_SKILL_REAL" ] && cd "$COPILOT_SKILL_REAL/../.." 2>/dev/null && pwd || echo "")

   PLUGIN_ROOT=""
   for candidate in \
     "${CLAUDE_PLUGIN_ROOT}" \
     "$HOME/.understand-anything-plugin" \
     "$SELF_RELATIVE" \
     "$COPILOT_SELF_RELATIVE" \
     "$HOME/.opencode/understand-anything/understand-anything-plugin" \
     "$HOME/.pi/understand-anything/understand-anything-plugin" \
     "$HOME/understand-anything/understand-anything-plugin"; do
     if [ -n "$candidate" ] && [ -f "$candidate/package.json" ] && [ -d "$candidate/skills" ]; then
       PLUGIN_ROOT="$candidate"
       break
     fi
   done

   if [ -z "$PLUGIN_ROOT" ]; then
     echo "Error: Cannot find the understand-anything plugin root."
     exit 1
   fi
   ```

3. Ensure the core package is built.
   ```bash
   if [ ! -f "$PLUGIN_ROOT/packages/core/dist/index.js" ]; then
     cd "$PLUGIN_ROOT" && (pnpm install --frozen-lockfile 2>/dev/null || pnpm install) && pnpm --filter @understand-anything/core build
   fi
   ```
   If `pnpm` is missing, stop and tell the user to install Node.js >= 22 and pnpm >= 10.

4. Create working directories.
   ```bash
   mkdir -p "$PROJECT_ROOT/.understand-anything/intermediate"
   mkdir -p "$PROJECT_ROOT/.understand-anything/tmp"
   ```

5. If `.understand-anything/.understandignore` does not exist, generate a starter one with the existing script, but do not block on manual review in this lite flow.
   ```bash
   PLUGIN_ROOT="$PLUGIN_ROOT" node "$PLUGIN_ROOT/skills/understand/generate-ignore.mjs" "$PROJECT_ROOT"
   ```

6. Run the deterministic scan.
   ```bash
   node "$PLUGIN_ROOT/skills/understand/scan-project.mjs" \
     "$PROJECT_ROOT" \
     "$PROJECT_ROOT/.understand-anything/intermediate/scan-result.json"
   ```

7. Build the deterministic import map.
   Create `$PROJECT_ROOT/.understand-anything/tmp/import-map-input.json` with:
   ```json
   {
     "projectRoot": "<PROJECT_ROOT>",
     "files": <scan-result.files>
   }
   ```

   Then run:
   ```bash
   node "$PLUGIN_ROOT/skills/understand/extract-import-map.mjs" \
     "$PROJECT_ROOT/.understand-anything/tmp/import-map-input.json" \
     "$PROJECT_ROOT/.understand-anything/intermediate/import-map.json"
   ```

8. Build the lite graph.
   ```bash
  node "$PLUGIN_ROOT/skills/understand-lite/build-lite-graph.mjs" \
    "$PROJECT_ROOT" \
    "$PROJECT_ROOT/.understand-anything/intermediate/scan-result.json" \
    "$PROJECT_ROOT/.understand-anything/intermediate/import-map.json" \
    "$PROJECT_ROOT/.understand-anything/knowledge-graph.json" \
    "$PROJECT_ROOT/.understand-anything/meta.json" \
    "$PROJECT_ROOT/.understand-anything/config.json"
  ```

9. Report the result to the user:
   - number of files scanned
   - number of nodes and edges in the graph
   - whether `.codebase-indexer/docs/architecture.md` was present and used as description input
   - explain that this is a structural, low-token graph

10. If the graph was written successfully, automatically launch the `/understand-dashboard-lite` skill for the same `PROJECT_ROOT`.
   - Pass the resolved project path as the dashboard argument.
   - Only launch the dashboard after `knowledge-graph.json` exists.
   - If dashboard launch fails, tell the user the lite graph was still generated successfully.

11. In the final success message, say both:
   - the low-token structural graph is ready
   - the dashboard is opening from that generated graph

## Notes

- Prefer this skill when token budget matters more than rich semantic summaries.
- This skill does not replace `/understand` for deep domain graphs, function/class-level explanations, or richer LLM-authored onboarding.
- If the repo already has `.codebase-indexer/docs/architecture.md`, the lite graph builder uses that as a cheap description source before falling back to README parsing.
