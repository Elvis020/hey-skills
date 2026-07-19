#!/usr/bin/env python3
"""Deterministic, budget-aware context packing for codebase-indexer.

This helper mirrors the signal-first guide:
- L0: structure only (imports + declarations)
- L1: compressed behavior (adds control flow signals)
- L3: raw source for explicit target file when it fits budget

No external dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

EXCLUDE_DIRS = {
    ".git",
    "_tmp_code-review-graph",
    ".claude",
    ".codebase-indexer",
    ".minimax",
    "node_modules",
    "dist",
    "build",
    "target",
    "__pycache__",
    ".next",
    ".venv",
    "venv",
}

SOURCE_EXTS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".py", ".go", ".rs", ".java", ".kt", ".swift",
    ".c", ".cc", ".cpp", ".h", ".hpp", ".cs", ".php",
}

DECL_PATTERNS = [
    re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_][\w$]*)"),
    re.compile(r"^\s*(?:export\s+)?class\s+([A-Za-z_][\w$]*)"),
    re.compile(r"^\s*(?:export\s+)?interface\s+([A-Za-z_][\w$]*)"),
    re.compile(r"^\s*(?:export\s+)?type\s+([A-Za-z_][\w$]*)"),
    re.compile(r"^\s*(?:export\s+)?enum\s+([A-Za-z_][\w$]*)"),
    re.compile(r"^\s*def\s+([A-Za-z_][\w]*)\s*\("),
    re.compile(r"^\s*class\s+([A-Za-z_][\w]*)\b"),
    re.compile(r"^\s*func\s+([A-Za-z_][\w]*)\s*\("),
    re.compile(r"^\s*fn\s+([A-Za-z_][\w]*)\s*\("),
]

IMPORT_PATTERNS = [
    re.compile(r"^\s*import\s+.*"),
    re.compile(r"^\s*from\s+\S+\s+import\s+.*"),
    re.compile(r"^\s*use\s+.*"),
]

CONTROL_PATTERNS = [
    (re.compile(r"\bif\b"), "IF"),
    (re.compile(r"\bswitch\b|\bmatch\b"), "SWITCH"),
    (re.compile(r"\bfor\b|\bwhile\b"), "LOOP"),
    (re.compile(r"\breturn\b"), "RET"),
    (re.compile(r"\bthrow\b|\braise\b|\bpanic!\b"), "THROW"),
    (re.compile(r"\btry\b|\bcatch\b|\bexcept\b"), "TRY"),
]

TOKEN_SPLIT = re.compile(r"[\s]+|(?<=[{}()[\];,.:=<>!&|?+\-*/^~@#$%\\])|(?=[{}()[\];,.:=<>!&|?+\-*/^~@#$%\\])")


@dataclass
class FileInput:
    path: str
    code: str
    raw_tokens: int


@dataclass
class Entry:
    path: str
    layer: str
    text: str
    tokens: int
    is_target: bool = False


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


def make_l0(rel_path: str, code: str) -> str:
    imports = []
    decls = []
    for line in code.splitlines():
        for ip in IMPORT_PATTERNS:
            if ip.match(line):
                imports.append(line.strip())
                break
        for pat in DECL_PATTERNS:
            m = pat.match(line)
            if m:
                name = m.group(1)
                kind = "CLASS" if "class" in line else "FN"
                if "interface" in line or "type" in line or "enum" in line:
                    kind = "TYPE"
                decls.append(f"{kind}:{name}")
                break
    imports = imports[:8]
    decls = decls[:20]
    body = []
    if imports:
        body.append("USE:[" + ", ".join(imports) + "]")
    body.extend(decls)
    return rel_path + "\n" + "\n".join(body)


def make_l1(rel_path: str, code: str) -> str:
    lines = [rel_path]
    for raw in code.splitlines():
        line = raw.strip()
        if not line:
            continue
        if any(p.match(line) for p in IMPORT_PATTERNS):
            lines.append("USE:" + line[:120])
            continue
        decl_hit = None
        for pat in DECL_PATTERNS:
            m = pat.match(line)
            if m:
                decl_hit = m.group(1)
                break
        if decl_hit:
            prefix = "CLASS" if line.startswith("class ") or " class " in line else "FN"
            if "interface" in line or "type " in line or "enum " in line:
                prefix = "TYPE"
            lines.append(f"OUT {prefix}:{decl_hit}")
            continue
        for cp, tag in CONTROL_PATTERNS:
            if cp.search(line):
                short = re.sub(r"\s+", " ", line)
                lines.append(f"{tag}:{short[:100]}")
                break
    # Deduplicate while keeping order
    dedup = []
    seen = set()
    for item in lines:
        if item in seen:
            continue
        dedup.append(item)
        seen.add(item)
    return "\n".join(dedup[:140])


def parse_csv_list(raw: str | None) -> set[str]:
    if not raw:
        return set()
    return {x.strip() for x in raw.split(",") if x.strip()}


def pack(files: list[FileInput], budget: int, changed: set[str], hotspots: set[str], target: str | None) -> dict:
    entries: list[Entry] = []
    total = 0

    target_file = None
    if target:
        for f in files:
            if f.path == target or f.path.endswith(target):
                target_file = f
                break

    if target_file:
        if target_file.raw_tokens <= int(budget * 0.6):
            e = Entry(target_file.path, "L3", target_file.code, target_file.raw_tokens, True)
        else:
            l1 = make_l1(target_file.path, target_file.code)
            e = Entry(target_file.path, "L1", l1, estimate_tokens(l1), True)
        entries.append(e)
        total += e.tokens

    for f in files:
        if target_file and f.path == target_file.path:
            continue
        l0 = make_l0(f.path, f.code)
        t = estimate_tokens(l0)
        entries.append(Entry(f.path, "L0", l0, t))
        total += t

    if total > budget:
        kept = [e for e in entries if e.is_target]
        used = sum(e.tokens for e in kept)
        for e in entries:
            if e.is_target:
                continue
            if used + e.tokens <= budget:
                kept.append(e)
                used += e.tokens
        entries = kept
        total = used

    def priority(e: Entry) -> tuple[int, int]:
        f = next((x for x in files if x.path == e.path), None)
        raw = f.raw_tokens if f else 0
        p = 0
        if e.path in changed:
            p += 4
        if e.path in hotspots:
            p += 2
        return (p, raw)

    upgrade_candidates = [e for e in entries if not e.is_target and e.layer == "L0"]
    upgrade_candidates.sort(key=priority, reverse=True)

    for e in upgrade_candidates:
        f = next((x for x in files if x.path == e.path), None)
        if not f:
            continue
        l1 = make_l1(f.path, f.code)
        t1 = estimate_tokens(l1)
        delta = t1 - e.tokens
        if total + delta <= budget:
            e.layer = "L1"
            e.text = l1
            e.tokens = t1
            total += delta

    return {
        "budget": budget,
        "total_tokens": total,
        "files_at_l0": sum(1 for e in entries if e.layer == "L0"),
        "files_at_l1": sum(1 for e in entries if e.layer == "L1"),
        "files_at_l3": sum(1 for e in entries if e.layer == "L3"),
        "target_file": target_file.path if target_file else None,
        "entries": [
            {
                "path": e.path,
                "layer": e.layer,
                "tokens": e.tokens,
                "is_target": e.is_target,
                "preview": "\\n".join(e.text.splitlines()[:20]),
            }
            for e in entries
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Budget-aware context packer for codebase-indexer")
    parser.add_argument("--root", default=".", help="Project root to scan")
    parser.add_argument("--budget", type=int, default=4000, help="Max token budget")
    parser.add_argument("--changed", help="Comma-separated changed file paths")
    parser.add_argument("--hotspots", help="Comma-separated hotspot file paths")
    parser.add_argument("--target", help="Target file path for raw (L3) preference")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files: list[FileInput] = []
    for p in iter_source_files(root):
        try:
            code = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(p.relative_to(root))
        files.append(FileInput(rel, code, estimate_tokens(code)))

    out = pack(files, args.budget, parse_csv_list(args.changed), parse_csv_list(args.hotspots), args.target)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
