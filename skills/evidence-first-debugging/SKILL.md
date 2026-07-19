---
name: evidence-first-debugging
description: "Use when debugging any bug, error, or unexpected behavior. Use BEFORE proposing fixes. Use when you catch yourself assuming code behavior without reading it."
---

# Evidence-First Debugging

## Overview

You cannot analyze what you haven't read. Every claim about code behavior must cite actual source.

**The Iron Law:**
```
NO ANALYSIS WITHOUT EVIDENCE. NO EVIDENCE WITHOUT READING.
```

Assumptions are bugs in your debugging process.

## Gate 1: Mandatory First Steps

**HARD GATE: Complete ALL steps with proof before ANY analysis.**

| Step | Action | Proof Required |
|------|--------|----------------|
| 1 | **Read the error** | Quote exact error message/stack trace in code block |
| 2 | **Reproduce** | Show the command/action that triggers it |
| 3 | **Read the crash site** | Use Read tool on file:line from stack trace, cite it |
| 4 | **Check recent changes** | Run `git diff` or `git log --oneline -10`, show output |

**You cannot proceed until all 4 steps have proof in your output.**

## Bug Type Classification

After Gate 1, classify and select localization strategy:

| Bug Type | Signals | Strategy |
|----------|---------|----------|
| **Runtime Error** | Stack trace, exception thrown | **Stack Trace** - read each file in stack, bottom to top |
| **Logic Bug** | Runs but wrong output | **Data Flow** - trace input through code, find where value diverges |
| **Integration** | Works alone, fails with other component | **Boundary Check** - read both sides of interface, compare contracts |
| **Performance** | Slow, timeout, memory | **Profiling** - add timing/logging at bottlenecks, measure |
| **Build/Config** | Won't compile, start, deploy | **Env Diff** - compare working vs broken env/config/deps |

## Reading Up the Stack

When tracing a bug, read EACH level:

```
1. Read crash site (file:line from error) → cite code
2. Find what calls that function → Read caller file → cite code
3. Find what calls the caller → Read that file → cite code
4. Continue until you find where bad data originates
```

**At each level, output:**
- File path and line number
- The relevant code snippet (quoted from Read tool)
- What this level contributes to the bug

## Hypothesis Tracking

Before proposing ANY fix, state explicitly:

```
Hypothesis #[N]: [What you think is wrong]
Evidence: [File:line citations supporting this]
Test: [How you'll verify]
```

## Loop Detection & Escape

**After 2 failed hypotheses:**
1. STOP proposing fixes
2. List what you tried and why each failed
3. Read 3 NEW files you haven't examined
4. Ask: "What haven't I looked at?"

**After 3 failed hypotheses:**
- Widen scope: check callers, config, environment
- Read files OUTSIDE the immediate area

**After 4 failed hypotheses:**
- STOP completely
- Ask user: "I've tried X, Y, Z. What am I missing?"

## Evidence Requirements

| Claim Type | Required Evidence |
|------------|-------------------|
| "The error says..." | Exact quote in code block |
| "This function does X..." | File:line citation + quoted code |
| "A calls B which calls C..." | Each file read with Read tool, call sites cited |
| "The value comes from..." | Traced path with citation at each step |
| "This changed recently..." | Git diff/log output shown |

## Forbidden Patterns

| Pattern | Why Wrong | Do Instead |
|---------|-----------|------------|
| "This probably calls..." | Guessing | Read the file, cite the call |
| "I assume this returns..." | Not verified | Read the function, quote return |
| "Based on the function name..." | Names lie | Read implementation |
| "This should work because..." | Assumption | Verify with evidence |
| "Let me try one more thing" | Looping | Read new files instead |

## Red Flags - STOP Immediately

If you catch yourself:
- Describing code you haven't read THIS SESSION
- Proposing a fix before completing Gate 1
- Using "probably", "likely", "should", "assume" about code
- Suggesting same fix with minor variations
- Skipping files in the stack trace
- Not quoting the actual error message

**ALL of these mean: STOP. Return to Gate 1.**

## Self-Check Before Any Fix

```
□ Have I quoted the exact error?
□ Have I read every file in the stack trace?
□ Can I cite file:line for my hypothesis?
□ Is this a new approach, not a repeat?
□ Have I tracked my hypothesis number?
```

If any box is unchecked, do not propose a fix.

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "I know what this function does" | You know what you *think* it does. Read it. |
| "The name tells me enough" | Names lie. Implementations don't. |
| "I'll check if my fix works first" | You'll waste time. Read first. |
| "This is obviously the problem" | Obvious ≠ correct. Cite evidence. |
| "I've seen this pattern before" | This codebase may differ. Read THIS code. |
| "Let me try one more thing" | 2+ tries = read new files instead. |
| "I don't need to read the whole file" | You need enough context. Err on reading more. |
