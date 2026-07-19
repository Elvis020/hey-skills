# 🧬 Evolution

A versioned timeline of how `codebase-indexer` evolved from its fork baseline.

## Version History

| Version | What Was Added |
|:--:|:--|
| v1 | One-shot scanner -> five docs + CLAUDE.md rules |
| v2 | Auto-update mode - diff-based refresh |
| v3 | Changelog and ADR tracking |
| v4 | Graph-aware blast radius |
| v5 | Signal-first IR - four-tier extraction |
| v6 | Token savings visibility |
| v7 | HTML savings report |
| v8 | Multi-repo workspace registry |
| v9 | Test coverage docs |
| v10 | AI-inferred "why" from git logs |

## Fork Boundary

**Stamped baseline:** original fork stopped at **v1**.

## What Makes This Fork Different

This fork extends the baseline with v2-v10 capabilities:

- Incremental updates (not full rescans every time)
- Graph-aware impact radius for smarter refresh scope
- Signal-first, tiered extraction (L0-L3)
- Measurable savings and benchmark reporting
- Multi-repo awareness and workspace registry
- Test coverage documentation support
- AI-inferred decision rationale ("why") from git history
