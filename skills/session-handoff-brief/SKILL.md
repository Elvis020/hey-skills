---
name: session-handoff-brief
description: "Turn current work into a concise next-session handoff. Use when the user wants a clean status recap, where work stopped, open blockers, and the smallest useful next steps."
---

# Session Handoff Brief

## Overview

Use this skill when the current work needs to be handed off cleanly to a later session or another person. The output should be short, factual, and easy to resume from.

## When To Use

- The user asks for a handoff summary, session recap, or "where did we stop?" brief.
- A multi-step task needs a clear checkpoint before pausing.
- The work is likely to continue in a later session and needs a stable restart point.

## Workflow

1. Capture the current objective in one line.
2. Summarize what is done.
3. Summarize what remains.
4. List blockers or open questions.
5. State the next 1-3 actions in priority order.
6. Note any important files, commands, or environment details needed to resume.

## Output Format

Return:
- objective
- completed
- pending
- blockers
- next steps
- resume notes

## Guardrails

- Keep it concise.
- Do not over-explain the background.
- Do not invent progress that was not confirmed.
- If the work is still ambiguous, say so plainly.
