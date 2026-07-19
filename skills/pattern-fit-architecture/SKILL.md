---
name: pattern-fit-architecture
description: "Use when designing, implementing, or reviewing code that touches persistence boundaries, caching or same-interface wrappers, extension/plugin points, integrations, SDKs, third-party services, legacy code, or messy orchestration. Helps agents consider Repository, Decorator, Plugin, and Facade patterns as evidence-based remedies while avoiding premature abstraction and over-engineering."
---

# Pattern Fit Architecture

Use this skill as a design judgment check during code creation and code review. The goal is not to force patterns into code. The goal is to notice boundary pressure and choose the smallest clear shape that protects the codebase.

## First Principle

Use Repository, Decorator, Plugin, and Facade as remedies, not defaults.

Do not recommend Repository, Decorator, Plugin, Facade, Adapter, Strategy, or similar patterns unless there is concrete evidence of current pain. Prefer the codebase's existing architecture over introducing a new pattern family.

For small codebases, scripts, prototypes, and single-owner modules, favor direct, readable code over abstraction. If the benefit is hypothetical, do not recommend the pattern.

## Fit Test

Before adding or recommending a pattern, name the specific problem it solves:

- Duplicated persistence or integration logic
- Unstable external dependency
- Test isolation pain
- Multiple implementations behind one contract
- Optional behavior layered around an existing operation
- Plugin lifecycle, discovery, or capability variation
- Messy orchestration that callers should not know about
- Boundary ownership that needs a stable local API

Then ask:

- Does this reduce coupling now?
- Does this make the next likely change simpler?
- Does this make tests clearer without multiplying empty mocks?
- Does this hide details callers should not know?
- Does this preserve a stable contract?
- Would a plain function, module, or framework-native convention be clearer?

When in doubt, ask: would this make the next change simpler, or only make the current code look more architectural?

## Pattern Heuristics

### Repository

Use when persistence details need a domain-level boundary.

Good signs:
- Business logic knows too much about SQL, ORM query mechanics, document-store syntax, filesystem layout, or API client details.
- Tests need real persistence for logic that could be isolated.
- The application needs a stable data access API while storage mechanics vary.

Guardrails:
- Prefer domain operations over generic CRUD theater.
- Do not create a repository only because a table/model exists.
- Keep query semantics, transactions, pagination, and consistency rules explicit at the boundary.

### Decorator

Use when optional behavior wraps an existing operation while preserving the same interface.

Good signs:
- Caching, logging, retry, metrics, authorization, tracing, validation, or rate limiting needs to be layered around a stable capability.
- Callers should not care whether they are using the base implementation or the wrapped one.

Guardrails:
- Same interface in, same interface out.
- Preserve semantics unless the new behavior is explicitly part of the contract.
- Make ordering, invalidation, error behavior, and observability clear.

### Plugin

Use when the system needs extensibility, isolation, or runtime/project/vendor-specific behavior.

Good signs:
- Features need to be added or swapped without touching host code.
- Third-party, customer-specific, or deployment-specific behavior needs a narrow contract.
- Failure of one extension should not corrupt the host.

Guardrails:
- Keep the host contract small and explicit.
- Define lifecycle, capabilities, errors, permissions, and version expectations only as far as the use case needs.
- Avoid plugin systems for one-off variation that a simple function or config can handle.

### Facade

Use when unavoidable messy coordination needs a clean local API.

Good signs:
- Callers are spread across low-level SDKs, dynamic loading, legacy seams, multi-step protocols, or orchestration details.
- The complexity is real and cannot be deleted yet.

Guardrails:
- A facade hides incidental complexity; it must not become a miscellaneous service bag.
- Name the facade after the domain capability, not the pattern.
- Keep sharp edges documented at the boundary instead of leaking them into callers.

## Code Creation Workflow

1. Read the surrounding code and identify existing architecture conventions.
2. Identify the volatility or pain: data access, wrapping behavior, extensibility, external integration, legacy complexity, or orchestration.
3. Run the fit test. If no concrete pain exists, keep the implementation direct.
4. Choose the lightest recognizable boundary that solves the named problem.
5. Name the code after domain behavior, not after the pattern.
6. Keep the first version small. Add lifecycle hooks, interfaces, registries, and factories only when the current problem requires them.

## Code Review Workflow

Lead with the observed defect, risk, or maintenance cost. Do not leave review comments that merely say "consider using a Repository/Facade/Decorator/Plugin."

Useful review questions:

- Are database, filesystem, SDK, or network details leaking into business logic?
- Is a wrapper preserving the expected interface and semantics?
- Is caching, retry, logging, or metrics behavior separated from core behavior without hiding important failures?
- Is an extension contract explicit and small enough to maintain?
- Can extension failures be contained?
- Does a facade hide real complexity, or is it collecting unrelated operations?
- Did the abstraction improve testability, or did mocks just multiply?
- Would deleting the abstraction make the code easier to understand?

Only recommend a pattern when the review can point to concrete code and explain why the pattern would reduce risk or simplify the next change.

## Output Expectations

When this skill influences implementation, mention the chosen boundary briefly in the final answer.

When this skill influences a review, include pattern-related findings only when they are actionable. If no pattern is warranted, say nothing or briefly note that direct code is appropriate.
