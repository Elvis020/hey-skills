#!/usr/bin/env python3
"""Create deterministic delta-first context summaries from git diff output.

Input:
- stdin unified diff, OR
- --repo + --files to run `git diff HEAD -- <files...>`

Output:
- JSON with file/hunk summaries (L2-equivalent context)
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path

HUNK_HEADER = re.compile(r"^@@ -\d+,?\d* \+(\d+),?(\d*) @@")
FN_HINT = re.compile(r"\b(?:function|def|class|interface|type|enum|fn|func)\s+([A-Za-z_][\w$]*)")


@dataclass
class HunkSummary:
    start_line: int
    end_line: int
    changed: list[str]
    control_signals: list[str]
    function_scope: str | None


@dataclass
class FileSummary:
    file: str
    hunks: list[HunkSummary]


def control_tags(line: str) -> list[str]:
    tags = []
    s = line.strip()
    if re.search(r"\bif\b", s):
        tags.append("IF")
    if re.search(r"\bswitch\b|\bmatch\b", s):
        tags.append("SWITCH")
    if re.search(r"\bfor\b|\bwhile\b", s):
        tags.append("LOOP")
    if re.search(r"\breturn\b", s):
        tags.append("RET")
    if re.search(r"\bthrow\b|\braise\b|\bpanic!\b", s):
        tags.append("THROW")
    if re.search(r"\btry\b|\bcatch\b|\bexcept\b", s):
        tags.append("TRY")
    return tags


def summarize_unified_diff(diff_text: str) -> list[FileSummary]:
    files: dict[str, list[HunkSummary]] = {}
    current_file = None
    current_hunk: HunkSummary | None = None

    for raw in diff_text.splitlines():
        if raw.startswith("+++ b/"):
            current_file = raw[6:]
            files.setdefault(current_file, [])
            current_hunk = None
            continue

        hm = HUNK_HEADER.match(raw)
        if hm:
            if not current_file:
                continue
            start = int(hm.group(1))
            length = int(hm.group(2) or "1")
            current_hunk = HunkSummary(
                start_line=start,
                end_line=start + max(length - 1, 0),
                changed=[],
                control_signals=[],
                function_scope=None,
            )
            files[current_file].append(current_hunk)
            continue

        if not current_hunk:
            continue

        if raw.startswith(("+", "-")) and not raw.startswith(("+++", "---")):
            line = raw[1:].strip()
            if not line:
                continue
            if len(current_hunk.changed) < 12:
                current_hunk.changed.append(line[:180])
            for tag in control_tags(line):
                if tag not in current_hunk.control_signals:
                    current_hunk.control_signals.append(tag)
            if current_hunk.function_scope is None:
                m = FN_HINT.search(line)
                if m:
                    current_hunk.function_scope = m.group(1)

        elif raw.startswith(" ") and current_hunk.function_scope is None:
            m = FN_HINT.search(raw[1:])
            if m:
                current_hunk.function_scope = m.group(1)

    return [FileSummary(file=f, hunks=h) for f, h in files.items() if h]


def read_diff_from_git(repo: Path, files: list[str]) -> str:
    cmd = ["git", "diff", "HEAD", "--", *files]
    proc = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True, check=False)
    return proc.stdout


def main() -> None:
    parser = argparse.ArgumentParser(description="Build delta-first context from unified diff")
    parser.add_argument("--repo", help="Repo path for git diff mode")
    parser.add_argument("--files", nargs="*", help="Changed files for git diff mode")
    args = parser.parse_args()

    if args.repo and args.files:
        diff_text = read_diff_from_git(Path(args.repo).resolve(), args.files)
    else:
        import sys

        diff_text = sys.stdin.read()

    summaries = summarize_unified_diff(diff_text)
    print(json.dumps({"files": [asdict(s) for s in summaries]}, indent=2))


if __name__ == "__main__":
    main()
