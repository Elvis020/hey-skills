#!/usr/bin/env python3
"""Generate a git co-change coupling report for codebase-indexer.

Uses commit file co-occurrence to highlight hidden dependencies:
- files that are frequently changed together
- a coupling score (Jaccard overlap over commit sets)

No external dependencies.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

EXCLUDE_DIRS = {
    ".git",
    ".minimax",
    "node_modules",
    "dist",
    "build",
    "target",
    "__pycache__",
    ".next",
    ".venv",
    "venv",
    ".codebase-indexer",
    ".claude",
}

SOURCE_EXTS = {
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".py",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".swift",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".php",
}


@dataclass(frozen=True)
class PairScore:
    a: str
    b: str
    cochange_commits: int
    a_commits: int
    b_commits: int
    jaccard: float


def run_git_log(repo: Path, max_commits: int) -> str:
    cmd = [
        "git",
        "log",
        f"-n{max_commits}",
        "--name-only",
        "--pretty=format:__COMMIT__",
    ]
    proc = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True, check=False)
    return proc.stdout


def is_source_file(path: str) -> bool:
    p = Path(path)
    if any(part in EXCLUDE_DIRS for part in p.parts):
        return False
    return p.suffix.lower() in SOURCE_EXTS


def parse_commits(log_text: str) -> list[set[str]]:
    commits: list[set[str]] = []
    current: set[str] = set()
    for line in log_text.splitlines():
        s = line.strip()
        if s == "__COMMIT__":
            if current:
                commits.append(current)
            current = set()
            continue
        if not s or s.startswith("Merge "):
            continue
        if is_source_file(s):
            current.add(s)
    if current:
        commits.append(current)
    return commits


def score_pairs(commits: list[set[str]]) -> tuple[list[PairScore], Counter[str]]:
    file_freq: Counter[str] = Counter()
    pair_freq: defaultdict[tuple[str, str], int] = defaultdict(int)

    for files in commits:
        for f in files:
            file_freq[f] += 1
        ordered = sorted(files)
        for i in range(len(ordered)):
            for j in range(i + 1, len(ordered)):
                pair_freq[(ordered[i], ordered[j])] += 1

    out: list[PairScore] = []
    for (a, b), n in pair_freq.items():
        union = file_freq[a] + file_freq[b] - n
        jaccard = (n / union) if union > 0 else 0.0
        out.append(
            PairScore(
                a=a,
                b=b,
                cochange_commits=n,
                a_commits=file_freq[a],
                b_commits=file_freq[b],
                jaccard=jaccard,
            )
        )
    out.sort(key=lambda x: (x.jaccard, x.cochange_commits, x.a, x.b), reverse=True)
    return out, file_freq


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate file coupling report from git history")
    parser.add_argument("--repo", default=".", help="Repository path")
    parser.add_argument("--max-commits", type=int, default=400, help="How many recent commits to scan")
    parser.add_argument("--min-pair-count", type=int, default=2, help="Minimum co-change commits for a pair")
    parser.add_argument("--min-jaccard", type=float, default=0.2, help="Minimum Jaccard score")
    parser.add_argument("--top", type=int, default=30, help="Max pairs to return")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    log_text = run_git_log(repo, args.max_commits)
    commits = parse_commits(log_text)
    pairs, file_freq = score_pairs(commits)

    filtered = [
        p
        for p in pairs
        if p.cochange_commits >= args.min_pair_count and p.jaccard >= args.min_jaccard
    ][: max(1, args.top)]

    payload = {
        "repo": str(repo),
        "max_commits": args.max_commits,
        "commits_scanned": len(commits),
        "source_files_observed": len(file_freq),
        "pairs": [
            {
                "file_a": p.a,
                "file_b": p.b,
                "cochange_commits": p.cochange_commits,
                "file_a_commits": p.a_commits,
                "file_b_commits": p.b_commits,
                "jaccard": round(p.jaccard, 4),
            }
            for p in filtered
        ],
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
