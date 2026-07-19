---
name: understand-dashboard-lite
description: "Launch the existing Understand Anything dashboard for a lite-generated graph without duplicating the dashboard package"
---

# /understand-dashboard-lite

Launch the existing dashboard UI for a project analyzed with `/understand-lite`.

This is intentionally a thin wrapper around `/understand-dashboard`.

Why:

- the dashboard package is shared infrastructure, not a small isolated widget
- it depends on `@understand-anything/core` schema, types, and search behavior
- reusing it keeps lite cheap without forking the UI/runtime layer

## Instructions

1. Resolve the project directory from `$ARGUMENTS`, or fall back to the current working directory.

2. Verify that `$PROJECT_ROOT/.understand-anything/knowledge-graph.json` exists.
   - If it does not, tell the user to run `/understand-lite` first.

3. Launch the standard `/understand-dashboard` flow for the same project directory.
   - Use the same plugin-root resolution, dependency install, and Vite launch behavior as `/understand-dashboard`.
   - Pass the resolved project directory through unchanged.

4. In the final message, make clear that:
   - the lite graph is being viewed in the shared dashboard
   - this is reuse, not a separate copied dashboard package

## Notes

- The current lite path deliberately shares the main dashboard because the UI is tightly coupled to the core graph model and loaders.
- If we later need materially different lite-only UX, we can add a mode flag before considering a full UI fork.
