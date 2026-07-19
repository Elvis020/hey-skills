---
name: understand-lite-diff
description: "Build a cheap diff overlay for a lite-generated graph so the shared dashboard can highlight changed and affected nodes"
---

# /understand-lite-diff

Write `.understand-anything/diff-overlay.json` for a repo analyzed with `/understand-lite`.

This reuses the shared dashboard's existing diff visualization without invoking the heavier `/understand-diff` workflow.

## Instructions

1. Resolve `PROJECT_ROOT`.
   - If `$ARGUMENTS` contains a path-like token, use it.
   - Otherwise use the current working directory.

2. Resolve `BASE_REF`.
   - If `$ARGUMENTS` contains a second non-flag token, treat it as the git base ref.
   - Otherwise default to the working tree against `HEAD` plus untracked files.

3. Verify that `$PROJECT_ROOT/.understand-anything/knowledge-graph.json` exists.
   - If it does not, tell the user to run `/understand-lite` first.

4. Resolve `PLUGIN_ROOT` using the same search order as `/understand-lite`.

5. Build the lite diff overlay:
   ```bash
   node "$PLUGIN_ROOT/skills/understand-lite/build-lite-diff.mjs" \
     "$PROJECT_ROOT" \
     "$PROJECT_ROOT/.understand-anything/knowledge-graph.json" \
     "$PROJECT_ROOT/.understand-anything/diff-overlay.json" \
     "$BASE_REF"
   ```

6. Report:
   - how many changed files were detected
   - how many changed nodes were mapped
   - how many affected nodes were found

7. Tell the user they can open `/understand-dashboard-lite` for the same repo to view the diff overlay visually.

## Notes

- This is intentionally structural and cheap.
- It follows graph edges to build a 1-hop blast radius from changed nodes.
