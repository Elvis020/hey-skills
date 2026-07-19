#!/usr/bin/env python3
"""Measured A/B benchmark for demo use.

A = raw rescan counterfactual (actual measured tokens across source files)
B = indexer docs path (actual measured tokens across docs index files)

Appends a `benchmark_measured` entry into project-local savings log by default.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Iterable

TOKEN_SPLIT = __import__("re").compile(r"[\s]+|(?<=[{}()[\];,.:=<>!&|?+\-*/^~@#$%\\])|(?=[{}()[\];,.:=<>!&|?+\-*/^~@#$%\\])")

EXCLUDE_DIRS = {
    ".git", ".claude", "_tmp_code-review-graph", "node_modules", "dist", "build", "target", "__pycache__", ".next", ".venv", "venv",
}
SOURCE_EXTS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".go", ".rs", ".java", ".kt", ".swift", ".c", ".cc", ".cpp", ".h", ".hpp", ".cs", ".php",
}
DOC_FILES = [
    ".codebase-indexer/docs/architecture.md",
    ".codebase-indexer/docs/implementation.md",
    ".codebase-indexer/docs/patterns.md",
    ".codebase-indexer/docs/decisions.md",
    ".codebase-indexer/docs/changelog.md",
]


def estimate_tokens(text: str) -> int:
    return len([t for t in TOKEN_SPLIT.split(text) if t])


def iter_source_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        if p.suffix.lower() in SOURCE_EXTS:
            yield p


def read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run measured A/B savings benchmark for this project")
    parser.add_argument("--project-root", default=".", help="Project root")
    parser.add_argument("--output-log", default=".codebase-indexer/savings.jsonl", help="Project-local savings log path")
    parser.add_argument("--append", choices=["yes", "no"], default="yes", help="Append benchmark entry to local savings log")
    parser.add_argument("--price-per-million", type=float, default=3.0, help="USD per 1M input tokens")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()

    source_files = list(iter_source_files(root))
    raw_tokens = 0
    for sf in source_files:
        raw_tokens += estimate_tokens(read_text_safe(sf))

    docs_tokens = 0
    docs_present = 0
    for rel in DOC_FILES:
        p = root / rel
        if p.exists():
            docs_present += 1
            docs_tokens += estimate_tokens(read_text_safe(p))

    docs_mode = "docs_path" if docs_present > 0 else "fallback_raw"
    indexer_tokens = docs_tokens if docs_present > 0 else raw_tokens
    saved_now = max(0, raw_tokens - indexer_tokens)
    cost = round(saved_now / 1_000_000 * args.price_per_million, 4)

    entry = {
        "date": str(date.today()),
        "project": root.name,
        "project_root": str(root),
        "mode": "benchmark_measured",
        "docs_generated": docs_present,
        "docs_skipped": max(0, 5 - docs_present),
        "project_files": len(source_files),
        "tokens_raw_baseline_est": raw_tokens,
        "tokens_indexer_run_est": indexer_tokens,
        "tokens_saved_this_run": saved_now,
        "tokens_saved_future_est": 0,
        "cost_saved_est_usd": cost,
        "graph_available": (root / ".code-review-graph/graph.db").exists(),
        "measurement_quality": "measured",
        "benchmark_note": "Measured A/B: raw source token total vs docs index token total (fallback to raw when docs missing)",
        "indexer_context_mode": docs_mode,
    }

    if args.append == "yes":
        out = Path(args.output_log)
        if not out.is_absolute():
            out = root / out
        append_jsonl(out, entry)

    print(json.dumps(entry, indent=2))


if __name__ == "__main__":
    main()
