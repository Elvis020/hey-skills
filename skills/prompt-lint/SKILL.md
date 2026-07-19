---
name: prompt-lint
description: "Audit a prompt for token waste and suggest a leaner rewrite. Use when you want detailed feedback on a prompt before sending it."
---

The user wants to audit a prompt for token efficiency. Your job is to:

1. Ask them to paste the prompt they want to review (if they haven't already)
2. Analyse it for:
   - Polite openers that add no information (can you please, could you, I was wondering...)
   - Context re-explanation that the agent already has from session memory
   - Vague openers that delay the actual ask (so basically, just a quick one...)
   - Hedge phrases that weaken the instruction (I think maybe, if possible, not sure if...)
   - Closing filler (thanks in advance, hope that makes sense, let me know what you think)
   - Unnecessary backstory or justification the agent doesn't need to complete the task
   - Word count vs information density

3. Produce output in this exact format:

---
**Prompt Audit**

**Issues found:**
- [bullet per issue with a one-line explanation of why it wastes tokens]

**Rewritten prompt:**
```
[lean rewrite — same intent, fewer words]
```

**Word count:** [original] → [rewritten] words
**What was cut:** [brief summary of what was removed and why it wasn't needed]
---

Keep the rewrite faithful to the user's intent. Do not change the ask — only strip waste.
After the audit, offer one tip they can apply to all future prompts based on the most common pattern you spotted.
