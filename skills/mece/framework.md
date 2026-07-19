# MECE Framework Reference

## What is MECE?

**MECE** (pronounced "me-see") stands for **Mutually Exclusive, Collectively Exhaustive**. It is a principle for organizing information into categories that:

1. **Do not overlap** — every item belongs to exactly one category
2. **Leave no gaps** — every possible item is covered by some category

## Origins

Created by **Barbara Minto** at McKinsey & Company in the late 1960s as part of the **Minto Pyramid Principle**. It became the foundational problem-structuring tool across management consulting — McKinsey, Bain, and BCG have used it for 60+ years.

The insight: most flawed thinking comes from either **counting something twice** (overlap) or **missing something entirely** (gap). MECE eliminates both.

## The Two Tests

### Test 1: Mutual Exclusivity

Ask: "Can any item belong to more than one category?"

**Passing example — Customer segments by revenue:**
```
├── Enterprise (>$100K ARR)
├── Mid-Market ($10K–$100K ARR)
├── SMB ($1K–$10K ARR)
└── Free (<$1K ARR)
```
Clear numeric boundaries. No customer fits two tiers.

**Failing example — Sales channels:**
```
├── Digital sales
├── Retail sales
└── B2B sales
```
A B2B sale can be digital. A retail sale can be digital. These overlap.

### Test 2: Collective Exhaustiveness

Ask: "Is there anything that doesn't fit into any category?"

**Passing example — Content types:**
```
├── Text (articles, docs, comments)
├── Media (images, video, audio)
├── Data (spreadsheets, CSVs, JSON)
└── Interactive (forms, polls, quizzes)
```

**Failing example — Trip packing list:**
```
├── Clothes
├── Shoes
└── Toiletries
```
What about electronics? Documents? Medications? Not exhaustive.

## Common Patterns That Break MECE

### 1. Same thing, different name
"User authentication" in one section, "login flow" in another. Same concept, counted twice.

### 2. Mixed abstraction levels
```
├── Frontend (layer)
├── Backend (layer)
├── Performance (concern)      ← different dimension
└── Security (concern)         ← different dimension
```
Mixing "by layer" with "by concern" guarantees overlap — security applies to both frontend and backend.

### 3. Implicit "Other" bucket
If your categories need an "Other/Miscellaneous" to work, the decomposition is incomplete. Decompose "Other" further or redefine categories.

### 4. Time-based vs. function-based mixing
```
├── Phase 1 features
├── Core features              ← overlaps with Phase 1
└── Nice-to-haves
```
"Core features" and "Phase 1 features" likely overlap. Pick one dimension: by phase OR by priority.

### 5. Overlapping ownership
```
├── Team A: User management + billing
├── Team B: Billing + reporting         ← billing is in two teams
└── Team C: Analytics
```

## How to Fix Non-MECE Structures

1. **Pick one dimension per level.** Don't mix "by team", "by feature", and "by timeline" at the same tier.
2. **Use clean boundaries.** Numeric ranges, boolean conditions, or explicit definitions.
3. **Apply the placement test.** Take 5-10 real items and try to place each in exactly one category. If you hesitate, the boundary is blurry.
4. **Apply the reverse test.** Start with your categories and ask "what's NOT in here?" If something obvious is missing, you're not exhaustive.
5. **Go one level deeper.** If a category is too broad, decompose it into sub-categories that are themselves MECE.

## MECE and AI/LLM Work

MECE is especially valuable when working with AI because:

- **AI amplifies ambiguity.** A vague prompt produces vague output. A MECE-structured prompt produces structured, complete output.
- **AI can't read your mind.** If your spec has gaps, the AI won't fill them — it'll either skip them or hallucinate. MECE catches gaps before generation.
- **AI duplicates what you duplicate.** If your instructions describe the same thing twice under different names, the AI will build it twice. MECE deduplicates.
- **Validation scales.** You can apply MECE to 5 requirements or 500. The test is the same: overlap? gap? fix.

## When to Apply MECE

| Context | Apply MECE to... |
|---------|-------------------|
| Product specs / PRDs | Feature categories, user stories, acceptance criteria |
| API design | Endpoint groups, error categories, permission scopes |
| Architecture | Module boundaries, service responsibilities, data ownership |
| State management | Actions, state slices, event types |
| Testing | Test categories, scenario coverage, edge case lists |
| Roadmaps | Phases, workstreams, priority tiers |
| Org design | Team responsibilities, ownership boundaries |
| Strategy docs | Market segments, competitive dimensions, risk categories |
| Prompt engineering | Instruction sections, constraint categories, output specifications |

## When NOT to Apply MECE

- **Creative brainstorming.** Early ideation benefits from messy, overlapping thinking. Apply MECE after, to structure the results.
- **Narrative writing.** Stories, blog posts, and marketing copy follow rhetorical structure, not logical decomposition.
- **Exploratory research.** When you don't yet know the categories, forcing MECE too early constrains discovery.

MECE is a **structuring tool**, not a thinking tool. Think freely first, then structure with MECE.
