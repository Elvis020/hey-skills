# ❓ FAQ

## Does the index get stale?

It can if a project changes and update mode is not run. The intended flow is docs-first sessions plus periodic update runs after feature or bugfix work, so index docs stay aligned with current code.

## Should I commit `.codebase-indexer/`?

Use **commit** when you want shared team context in the repo. Use **gitignore** when you prefer local-only generated docs. Both are valid because the index is regeneratable from source.

## My project already has a detailed `CLAUDE.md`. Does it still help?

Yes. Supplement mode can generate only missing docs (for example patterns, decisions, and changelog) instead of duplicating what is already documented.

## How accurate are the token savings estimates?

Savings mode provides practical estimates based on run statistics. Benchmark mode gives measured A/B comparisons for stronger evidence when you need exactness for demos or reporting.

## Can I use this with other AI agents besides Claude?

Yes. The workflow is agent-agnostic as long as your setup can run Python and read/write project files.
