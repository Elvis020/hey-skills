#!/usr/bin/env python3
"""Prompt-driven context retrieval for codebase-indexer.

Goal:
- take a natural-language user request
- automatically rank likely relevant files
- feed only those files into existing budget-aware packing

This keeps search invisible to users (no manual search UI) while reducing
tokens sent to the model.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

from context_packer import FileInput, estimate_tokens, iter_source_files, make_l0, pack, parse_csv_list

TERM_RE = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]{1,}")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
}


@dataclass
class ScoredFile:
    file: FileInput
    score: float
    reason: list[str]


def tokenize_query(query: str) -> list[str]:
    terms = [t.lower() for t in TERM_RE.findall(query)]
    seen = set()
    out = []
    for term in terms:
        if term in seen:
            continue
        if term in STOPWORDS:
            continue
        seen.add(term)
        out.append(term)
    return out


def lexical_score(query: str, terms: list[str], rel_path: str, code: str) -> tuple[float, list[str]]:
    path_lower = rel_path.lower()
    l0 = make_l0(rel_path, code).lower()
    code_lower = code.lower()

    score = 0.0
    reason: list[str] = []

    code_term_hits = 0
    strong_hit = False
    for term in terms:
        if term in path_lower:
            score += 4.0
            reason.append(f"path:{term}")
            strong_hit = True
        if term in l0:
            score += 2.5
            reason.append(f"structure:{term}")
            strong_hit = True
        if term in code_lower:
            score += 1.0
            code_term_hits += 1

    q = query.strip().lower()
    if q and q in code_lower:
        score += 6.0
        reason.append("exact_phrase_in_code")
    if q and q in path_lower:
        score += 8.0
        reason.append("exact_phrase_in_path")

    # Slightly prefer smaller files when scores are close.
    score -= min(estimate_tokens(code) / 20000.0, 1.5)
    if not strong_hit and code_term_hits < 2:
        return 0.0, []
    return score, reason[:8]


def load_source_files(root: Path) -> list[FileInput]:
    files: list[FileInput] = []
    for p in iter_source_files(root):
        try:
            code = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(p.relative_to(root))
        files.append(FileInput(rel, code, estimate_tokens(code)))
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description="Query-first context retrieval + budgeted packing")
    parser.add_argument("--root", default=".", help="Project root to scan")
    parser.add_argument("--query", required=True, help="Natural-language user request")
    parser.add_argument("--budget", type=int, default=3500, help="Max token budget")
    parser.add_argument("--top-k", type=int, default=25, help="Max candidate files before packing")
    parser.add_argument("--changed", help="Comma-separated changed file paths")
    parser.add_argument("--hotspots", help="Comma-separated hotspot file paths")
    parser.add_argument("--target", help="Target file path for raw (L3) preference")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    terms = tokenize_query(args.query)
    files = load_source_files(root)

    scored: list[ScoredFile] = []
    for f in files:
        score, reason = lexical_score(args.query, terms, f.path, f.code)
        if score <= 0:
            continue
        scored.append(ScoredFile(file=f, score=score, reason=reason))

    scored.sort(key=lambda x: (x.score, -x.file.raw_tokens), reverse=True)
    selected = scored[: max(args.top_k, 1)]
    selected_files = [x.file for x in selected]

    packed = pack(
        selected_files,
        args.budget,
        parse_csv_list(args.changed),
        parse_csv_list(args.hotspots),
        args.target,
    )
    print(
        json.dumps(
            {
                "query": args.query,
                "query_terms": terms,
                "files_scanned": len(files),
                "candidates": [
                    {
                        "path": x.file.path,
                        "score": round(x.score, 3),
                        "raw_tokens": x.file.raw_tokens,
                        "reason": x.reason,
                    }
                    for x in selected
                ],
                "packed_context": packed,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
