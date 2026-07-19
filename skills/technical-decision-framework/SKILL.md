---
name: technical-decision-framework
description: "Guide technical tradeoff decisions for build, stack, and scope"
---

# Technical Decision Framework

## Overview
Use this skill to evaluate technical choices that affect architecture, delivery speed, maintainability, or product risk. Apply it when deciding build vs buy, choosing a stack, weighing monoliths against microservices, refactoring versus rewriting, adding dependencies, scoping an MVP, optimizing performance, or documenting a decision for later review.

## Architecture Review Mode
Use a stricter lens when the decision affects shared systems, long-lived data, external contracts, or team coordination.

- Ask for the blast radius before optimizing for elegance.
- Prefer the option that preserves reversibility and keeps future migration paths open.
- Treat vendor lock-in, public APIs, shared databases, and cross-team dependencies as one-way door candidates.
- Default to the smallest architecture that can ship now and survive the next growth step.

## Decision Workflow

1. Define the decision clearly.
   - State the options.
   - Identify the deadline or trigger.
   - Name the real problem, not the proxy debate.

2. Ask the five questions.
   - What is the cost of being wrong?
   - What is the cost of waiting?
   - Who is affected?
   - What is the simplest version that works?
   - Could we ship in 48 hours?

3. Classify reversibility.
   - Treat reversible decisions as fast, low-ceremony calls.
   - Treat one-way decisions as high-stakes and slow down.
   - Prefer choices that preserve future options.

4. Apply the time horizon.
   - Judge the choice at 10 minutes, 10 months, and 10 years.
   - Favor short-term speed for throwaway work.
   - Favor long-term maintainability for durable products.

5. Pick the default when evidence is weak.
   - Buy solved problems unless the work is a core differentiator.
   - Prefer boring, proven tech unless there is a clear need.
   - Keep a monolith until organizational scale truly demands services.
   - Refactor incrementally before considering a rewrite.
   - Optimize only after measuring a real bottleneck.
   - Cut scope aggressively for v1.

6. Make the decision reversible in implementation.
   - Use modular boundaries.
   - Avoid unnecessary vendor lock-in and framework-specific coupling.
   - Keep data migrations and interfaces simple where possible.

7. Document the outcome.
   - Record context, choice, trade-offs, status, and revisit date.
   - Revisit only when inputs change, not because the team is bored.

## Recommended Output
When asked for a recommendation, respond with:
- Recommendation: the decision to make.
- Why: the main reasons.
- Reversibility: whether it is a two-way or one-way door.
- Risks: what could go wrong.
- Next step: the smallest action that advances the decision.
- Revisit trigger: what future change would justify revisiting it.

## Quick Defaults
- Build vs buy: buy unless it is core to the product.
- Tech stack: choose boring, well-supported tools first.
- Monolith vs microservices: start with a monolith unless team coordination is the real bottleneck.
- Refactor vs rewrite: refactor incrementally by default.
- Optimize vs wait: measure first, then optimize the bottleneck.
- Scope: ship the smallest version that delivers value.

## Decision Note Template
Use this format for important calls:
- Date:
- Context:
- Decision:
- Trade-offs:
- Status:
- Revisit when:

## Reference
- [Example prompts](references/example-prompts.md) for quick ways to trigger the skill in real work.
