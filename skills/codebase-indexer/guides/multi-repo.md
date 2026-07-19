# Multi-Repo Intelligence Guide

When a workspace contains multiple related repositories, this guide enables cross-repo lookup during indexing.

## Workspace Setup

Place `workspace.md` in the parent directory of all related repos:

```
~/projects/
  workspace.md          ← one level up from all repos
  auth-service/
  payment-service/
  api-gateway/
```

Format is plain markdown — agent-agnostic, no tool-specific syntax.

## Workspace Format

```markdown
# Workspace: myapp

| repo | path | description |
|---|---|---|
| auth-service | ./auth-service | JWT auth, token validation |
| payment-service | ./payment-service | Stripe integration |
| api-gateway | ./api-gateway | Entry point, routing |

Paths are relative to workspace.md.
```

## Detection

At scan time, check for `../workspace.md` relative to the project root:
- If present → set `workspace_available = true`
- If absent → skip cross-repo features entirely (no error)

## How Cross-Repo Lookup Works

1. **Detect cross-repo calls** — HTTP clients, package imports from workspace namespace, gRPC stubs, service references
2. **Match against registry** — look up the target service in workspace.md
3. **Point at that repo's index docs** — reference the target repo's `.codebase-indexer/docs/` folder for structural info

Example output in `implementation.md`:

```
## Cross-Repo References
| Call | Target Repo | Target Docs |
|---|---|---|
| `authService.verifyToken()` | auth-service | ../auth-service/.codebase-indexer/docs/implementation.md |
| Stripe API | payment-service | ../payment-service/.codebase-indexer/docs/architecture.md |
```

## Limitations

- Docs are only as fresh as the last index run per repo
- Detection is heuristic — may miss indirect references
- No real-time sync between repos

## What Happens When Workspace Is Absent

The ## Cross-Repo References section is entirely omitted from generated docs. No errors, no fallback — just silent skip.
