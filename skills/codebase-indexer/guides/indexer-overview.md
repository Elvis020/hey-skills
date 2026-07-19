# Codebase Indexer Overview

Inspiration reference: [@joshtriedcoding on X](https://x.com/joshtriedcoding/status/2042535715712516284?s=20)

## Big Picture

```mermaid
flowchart LR
    U["User Request"] --> A["Indexer Skill Orchestrator"]
    A --> Q["Query Retrieval (scripts/query_context.py)"]

    Q --> B{"Search Backend"}
    B --> L["Local Backend (default)\nFilesystem + lexical ranking"]
    B -. optional later .-> R["Redis Backend (future)\nVirtual FS style index"]

    L --> S["Top-K Candidate Files"]
    R --> S

    S --> P["Context Packing (scripts/context_packer.py)\nL0/L1/L3 within token budget"]
    A --> D["Delta Summarization (scripts/delta_context.py)\nL2 for updates"]
    D --> P

    P --> C["Compact Context Payload"]
    C --> M["LLM Reasoning / Response"]

    M --> O["Doc Updates (.codebase-indexer/docs/*)\narchitecture, implementation, patterns,\ndecisions, changelog"]
    O --> T["Stats + Savings Reports\nstats/runs.jsonl + savings_report.py"]
```

Plain-text fallback:

```text
User Request
  -> Indexer Skill Orchestrator
    -> Query Retrieval (scripts/query_context.py)
      -> Search Backend
        -> Local Backend (default)
        -> Redis Backend (optional future)
      -> Top-K Candidate Files
        -> Context Packing (scripts/context_packer.py, L0/L1/L3)
    -> Delta Summarization (scripts/delta_context.py, L2 updates)
      -> Context Packing
        -> Compact Context Payload
          -> LLM Reasoning / Response
            -> Doc Updates (.codebase-indexer/docs/*)
              -> Stats + Savings Reports
```

## Request Flow (No Manual Search UI)

```mermaid
sequenceDiagram
    participant User
    participant Skill as Indexer Skill
    participant Retrieve as Query Retrieval
    participant Pack as Context Packer
    participant LLM

    User->>Skill: Ask question / task
    Skill->>Retrieve: Pass natural language query
    Retrieve->>Retrieve: Rank relevant files automatically
    Retrieve-->>Pack: Top-K file set
    Pack->>Pack: Build L0/L1/L3 budgeted context
    Pack-->>LLM: Minimal high-signal context
    LLM-->>Skill: Answer + optional doc updates
    Skill-->>User: Response (no search bar needed)
```

Plain-text fallback:

```text
1) User asks question/task
2) Skill forwards natural-language query
3) Retrieval ranks files automatically
4) Top-K files are packed into budgeted context
5) LLM responds from compact high-signal context
6) Skill returns answer and optionally updates docs
```

## Why This Helps

- Reduces token usage by sending only high-relevance file slices.
- Keeps retrieval invisible to the user (prompt-driven, not UI-driven).
- Supports incremental scale: local backend now, optional virtual-FS backend later, same calling contract.
