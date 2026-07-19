#!/usr/bin/env python3
"""Replay a feature stack against a subject repo and compare indexer scenarios.

This script is intentionally benchmark-oriented, not product runtime code.
It measures:
- full-session replay cost across checkpoints
- incremental update-mode cost across changed commits

The subject repo is expected to provide:
- CLAUDE.md
- docs/patterns.md
- docs/decisions.md
- docs/changelog.md
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

TOKEN_SPLIT = re.compile(r"[\s]+|(?<=[{}()[\];,.:=<>!&|?+\-*/^~@#$%\\])|(?=[{}()[\];,.:=<>!&|?+\-*/^~@#$%\\])")
EXCLUDE_DIRS = {
    ".git",
    ".claude",
    "_tmp_code-review-graph",
    "node_modules",
    "dist",
    "build",
    "target",
    "__pycache__",
    ".next",
    ".venv",
    "venv",
    ".codebase-indexer",
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
    ".properties",
    ".yml",
    ".yaml",
    ".sql",
    ".xml",
    ".gradle",
}
DOC_FILES_V1 = [
    "architecture.md",
    "implementation.md",
    "patterns.md",
    "decisions.md",
    "changelog.md",
]
DOC_FILES_LATEST = [
    "patterns.md",
    "decisions.md",
    "changelog.md",
]
IGNORED_CHANGED_FILES = {
    ".version",
    "docs/changelog.md",
}


@dataclass
class ScenarioCheckpoint:
    checkpoint: str
    commit: str
    description: str
    project_files: int
    raw_tokens: int
    docs_tokens: int
    tokens_saved: int
    savings_pct: float
    prep_ms: int
    benchmark_ms: int
    docs_present: int
    docs_files: list[str]


@dataclass
class UpdateBenchmarkRow:
    checkpoint: str
    commit: str
    description: str
    changed_files: list[str]
    changed_file_count: int
    delta_scan_tokens: int
    v1_total_tokens: int
    latest_total_tokens: int
    latest_saved_vs_v1: int
    latest_saved_pct_vs_v1: float


def run(cmd: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def estimate_tokens(text: str) -> int:
    return len([tok for tok in TOKEN_SPLIT.split(text) if tok])


def iter_source_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in SOURCE_EXTS:
            yield path


def measure_raw(root: Path) -> tuple[int, int]:
    files = list(iter_source_files(root))
    total = sum(estimate_tokens(read_text(path)) for path in files)
    return len(files), total


def clear_index(root: Path) -> None:
    idx = root / ".codebase-indexer"
    if idx.exists():
        shutil.rmtree(idx)


def extract_section(md: str, heading: str) -> str:
    pattern = re.compile(rf"^## {re.escape(heading)}\n", re.M)
    match = pattern.search(md)
    if not match:
        return ""
    start = match.start()
    next_match = re.compile(r"^## ", re.M).search(md, match.end())
    end = next_match.start() if next_match else len(md)
    return md[start:end].strip() + "\n"


def copy_file(src: Path, dest: Path) -> None:
    ensure_dir(dest.parent)
    shutil.copy2(src, dest)


def build_v1_docs(root: Path, claude_rel: Path, docs_rel: Path) -> list[str]:
    clear_index(root)
    docs_dir = root / ".codebase-indexer" / "docs"
    ensure_dir(docs_dir)

    claude = read_text(root / claude_rel)
    patterns = read_text(root / docs_rel / "patterns.md")
    decisions = read_text(root / docs_rel / "decisions.md")
    changelog = read_text(root / docs_rel / "changelog.md")

    architecture_parts = [
        "# Architecture\n",
        extract_section(claude, "Project Overview"),
        extract_section(claude, "Build & Development Commands"),
        extract_section(claude, "Architecture"),
        extract_section(claude, "Database"),
        extract_section(claude, "Security & Authentication"),
        extract_section(claude, "Architecture Diagrams"),
    ]
    implementation_parts = [
        "# Implementation\n",
        extract_section(claude, "Testing Strategy"),
        extract_section(claude, "Development Workflow"),
        extract_section(claude, "Common Patterns"),
        extract_section(claude, "Important Implementation Notes"),
    ]

    (docs_dir / "architecture.md").write_text(
        "\n".join(part for part in architecture_parts if part.strip()) + "\n",
        encoding="utf-8",
    )
    (docs_dir / "implementation.md").write_text(
        "\n".join(part for part in implementation_parts if part.strip()) + "\n",
        encoding="utf-8",
    )
    (docs_dir / "patterns.md").write_text(patterns, encoding="utf-8")
    (docs_dir / "decisions.md").write_text(decisions, encoding="utf-8")
    (docs_dir / "changelog.md").write_text(changelog, encoding="utf-8")
    return DOC_FILES_V1


def build_latest_docs(root: Path, docs_rel: Path) -> list[str]:
    clear_index(root)
    docs_dir = root / ".codebase-indexer" / "docs"
    ensure_dir(docs_dir)
    for name in DOC_FILES_LATEST:
        copy_file(root / docs_rel / name, docs_dir / name)
    return DOC_FILES_LATEST


def measure_docs(root: Path) -> tuple[int, int, list[str]]:
    docs_dir = root / ".codebase-indexer" / "docs"
    if not docs_dir.exists():
        return 0, 0, []
    files = sorted(path for path in docs_dir.iterdir() if path.is_file() and path.suffix == ".md")
    total = sum(estimate_tokens(read_text(path)) for path in files)
    return len(files), total, [path.name for path in files]


def measure_scenario(
    root: Path,
    checkpoint: str,
    commit: str,
    description: str,
    scenario: str,
    claude_rel: Path,
    docs_rel: Path,
) -> ScenarioCheckpoint:
    project_files, raw_tokens = measure_raw(root)
    t0 = time.perf_counter()
    if scenario == "raw_unindexed":
        clear_index(root)
        docs_files: list[str] = []
    elif scenario == "v1_full_index":
        docs_files = build_v1_docs(root, claude_rel, docs_rel)
    elif scenario == "latest_supplement":
        docs_files = build_latest_docs(root, docs_rel)
    else:
        raise ValueError(f"Unknown scenario: {scenario}")
    prep_ms = int((time.perf_counter() - t0) * 1000)

    t1 = time.perf_counter()
    docs_present, docs_tokens, measured_files = measure_docs(root)
    benchmark_ms = int((time.perf_counter() - t1) * 1000)
    if scenario == "raw_unindexed":
        docs_tokens = raw_tokens
        docs_present = 0
        measured_files = []

    tokens_saved = max(0, raw_tokens - docs_tokens)
    savings_pct = round((tokens_saved / raw_tokens * 100.0), 2) if raw_tokens else 0.0
    return ScenarioCheckpoint(
        checkpoint=checkpoint,
        commit=commit,
        description=description,
        project_files=project_files,
        raw_tokens=raw_tokens,
        docs_tokens=docs_tokens,
        tokens_saved=tokens_saved,
        savings_pct=savings_pct,
        prep_ms=prep_ms,
        benchmark_ms=benchmark_ms,
        docs_present=docs_present,
        docs_files=measured_files if measured_files else docs_files,
    )


def changed_source_files_for_commit(root: Path, commit: str) -> list[str]:
    lines = run(["git", "show", "--pretty=", "--name-only", commit], cwd=root).splitlines()
    out: list[str] = []
    for rel in lines:
        rel = rel.strip()
        if not rel or rel in IGNORED_CHANGED_FILES:
            continue
        path = root / rel
        if not path.exists() or not path.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in SOURCE_EXTS:
            continue
        out.append(rel)
    return sorted(dict.fromkeys(out))


def tokens_for_files(root: Path, rel_paths: list[str]) -> int:
    return sum(estimate_tokens(read_text(root / rel_path)) for rel_path in rel_paths)


def build_update_benchmark(
    root: Path,
    commits: list[tuple[str, str, str]],
    session_results: dict,
) -> dict:
    rows: list[UpdateBenchmarkRow] = []
    v1_docs_lookup = {
        checkpoint["checkpoint"]: checkpoint["docs_tokens"]
        for checkpoint in session_results["v1_full_index"]["checkpoints"]
    }
    latest_docs_lookup = {
        checkpoint["checkpoint"]: checkpoint["docs_tokens"]
        for checkpoint in session_results["latest_supplement"]["checkpoints"]
    }

    for checkpoint, commit, description in commits[1:]:
        changed_files = changed_source_files_for_commit(root, commit)
        delta_tokens = tokens_for_files(root, changed_files)
        v1_total = v1_docs_lookup[checkpoint] + v1_docs_lookup["base"] + delta_tokens
        latest_total = latest_docs_lookup[checkpoint] + delta_tokens
        saved = v1_total - latest_total
        saved_pct = round((saved / v1_total * 100.0), 2) if v1_total else 0.0
        rows.append(
            UpdateBenchmarkRow(
                checkpoint=checkpoint,
                commit=commit,
                description=description,
                changed_files=changed_files,
                changed_file_count=len(changed_files),
                delta_scan_tokens=delta_tokens,
                v1_total_tokens=v1_total,
                latest_total_tokens=latest_total,
                latest_saved_vs_v1=saved,
                latest_saved_pct_vs_v1=saved_pct,
            )
        )

    v1_total_all = sum(row.v1_total_tokens for row in rows)
    latest_total_all = sum(row.latest_total_tokens for row in rows)
    saved_all = v1_total_all - latest_total_all
    return {
        "example_name": "Incremental update-mode benchmark",
        "example_prompt": "A maintainer updates the index after each replayed feature commit instead of rescanning the repo every time.",
        "rows": [asdict(row) for row in rows],
        "aggregate": {
            "v1_total_tokens": v1_total_all,
            "latest_total_tokens": latest_total_all,
            "latest_saved_vs_v1": saved_all,
            "latest_saved_pct_vs_v1": round((saved_all / v1_total_all * 100.0), 2) if v1_total_all else 0.0,
        },
        "interpretation": [
            "This benchmark isolates ongoing maintenance cost after the initial index exists.",
            "v1 is modeled as a broad re-read that keeps paying for a larger docs context.",
            "latest is modeled as supplement/update behavior: keep the smaller docs set and add only changed source scope.",
            "This benchmark shows why diff-aware maintenance matters beyond the first scan.",
        ],
    }


def build_html(summary: dict) -> str:
    rows = []
    for scenario in summary["scenarios"].values():
        for checkpoint in scenario["checkpoints"]:
            rows.append(
                "<tr>"
                f"<td>{scenario['label']}</td>"
                f"<td>{checkpoint['checkpoint']}</td>"
                f"<td><code>{checkpoint['commit'][:8]}</code></td>"
                f"<td class='num'>{checkpoint['project_files']}</td>"
                f"<td class='num'>{checkpoint['raw_tokens']:,}</td>"
                f"<td class='num'>{checkpoint['docs_tokens']:,}</td>"
                f"<td class='num'>{checkpoint['tokens_saved']:,}</td>"
                f"<td class='num'>{checkpoint['savings_pct']:.2f}%</td>"
                f"<td class='num'>{checkpoint['docs_present']}</td>"
                f"<td>{', '.join(checkpoint['docs_files']) if checkpoint['docs_files'] else 'none'}</td>"
                "</tr>"
            )

    cards = []
    for key, scenario in summary["scenarios"].items():
        aggregate = scenario["aggregate"]
        cards.append(
            "<section class='card {klass}'>"
            f"<h3>{scenario['label']}</h3>"
            f"<p>{scenario['description']}</p>"
            f"<div class='metric'><span>Total tokens used</span><strong>{aggregate['total_docs_tokens']:,}</strong></div>"
            f"<div class='metric'><span>Total tokens saved vs raw</span><strong>{aggregate['saved_vs_raw']:,}</strong></div>"
            f"<div class='metric'><span>Savings rate</span><strong>{aggregate['saved_pct_vs_raw']:.2f}%</strong></div>"
            f"<div class='metric'><span>Avg docs/session</span><strong>{aggregate['avg_docs_tokens']:,}</strong></div>"
            "</section>".format(klass="best" if key == summary["best_scenario_key"] else "")
        )

    update = summary["update_benchmark"]
    update_rows = []
    for row in update["rows"]:
        update_rows.append(
            "<tr>"
            f"<td>{row['checkpoint']}</td>"
            f"<td><code>{row['commit'][:8]}</code></td>"
            f"<td>{row['description']}</td>"
            f"<td class='num'>{row['changed_file_count']}</td>"
            f"<td class='num'>{row['delta_scan_tokens']:,}</td>"
            f"<td class='num'>{row['v1_total_tokens']:,}</td>"
            f"<td class='num'>{row['latest_total_tokens']:,}</td>"
            f"<td class='num'>{row['latest_saved_vs_v1']:,}</td>"
            f"<td class='num'>{row['latest_saved_pct_vs_v1']:.2f}%</td>"
            "</tr>"
        )

    methodology = "".join(f"<li>{item}</li>" for item in summary["methodology"])
    why_best = "".join(f"<li>{item}</li>" for item in summary["scenarios"][summary["best_scenario_key"]]["why_best"])
    update_notes = "".join(f"<li>{item}</li>" for item in update["interpretation"])
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Codebase Indexer Benchmark</title>
  <style>
    :root {{ --bg:#f6f1e8; --ink:#1f2937; --muted:#6b7280; --card:#fffdf8; --line:#e5dccd; --accent:#0f766e; --accent2:#c2410c; }}
    body {{ font-family: Georgia, serif; background: linear-gradient(180deg,#f8f3ea 0%,#efe4d1 100%); color:var(--ink); margin:0; }}
    .wrap {{ max-width: 1180px; margin: 0 auto; padding: 32px 24px 56px; }}
    h1,h2,h3 {{ margin: 0 0 12px; line-height:1.1; }}
    p,li {{ font-size: 16px; line-height: 1.5; }}
    .hero {{ background: rgba(255,253,248,0.86); border:1px solid var(--line); border-radius: 24px; padding: 28px; box-shadow: 0 20px 50px rgba(0,0,0,0.07); }}
    .grid {{ display:grid; grid-template-columns: repeat(auto-fit,minmax(240px,1fr)); gap:16px; margin: 24px 0; }}
    .card {{ background: var(--card); border:1px solid var(--line); border-radius: 20px; padding: 20px; }}
    .card.best {{ border-color: var(--accent); box-shadow: 0 0 0 2px rgba(15,118,110,0.15); }}
    .metric {{ display:flex; justify-content:space-between; gap:12px; padding:8px 0; border-top:1px solid var(--line); }}
    .metric:first-of-type {{ border-top:none; }}
    .metric span {{ color:var(--muted); }}
    .metric strong {{ font-size: 20px; }}
    table {{ width:100%; border-collapse: collapse; background: rgba(255,253,248,0.92); border:1px solid var(--line); border-radius: 18px; overflow:hidden; }}
    th,td {{ padding: 12px 10px; border-bottom:1px solid var(--line); text-align:left; font-size:14px; vertical-align:top; }}
    th {{ background:#f2e8d8; }}
    td.num {{ text-align:right; font-variant-numeric: tabular-nums; }}
    .two {{ display:grid; grid-template-columns: 1.2fr 1fr; gap:20px; margin-top:24px; }}
    .badge {{ display:inline-block; padding:6px 10px; background:#ddf4ef; color:#0f766e; border-radius:999px; font-size:12px; letter-spacing:0.04em; text-transform:uppercase; }}
    .accent {{ color: var(--accent2); font-weight: bold; }}
    .foot {{ margin-top:20px; color:var(--muted); font-size:13px; }}
    @media (max-width: 900px) {{ .two {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <span class="badge">Measured A/B Replay</span>
      <h1>Codebase Indexer Benchmark</h1>
      <p>Benchmark date: {summary['generated_at']}<br />Commit range replayed: <code>{summary['commit_range'][0][:8]}</code> -> <code>{summary['commit_range'][-1][:8]}</code><br />Indexer v1 SHA: <code>{summary['v1_sha'][:8]}</code> · Latest SHA: <code>{summary['latest_sha'][:8]}</code></p>
      <p>This report includes both the headline compression benchmark and the incremental maintenance benchmark.</p>
    </section>

    <div class="grid">
      {''.join(cards)}
    </div>

    <div class="two">
      <section class="card">
        <h2>Why {summary['scenarios'][summary['best_scenario_key']]['label']} won</h2>
        <ul>{why_best}</ul>
      </section>
      <section class="card">
        <h2>Methodology</h2>
        <ul>{methodology}</ul>
      </section>
    </div>

    <section class="card" style="margin-top:24px;">
      <h2>Benchmark 1: Full-Session Replay</h2>
      <table>
        <thead>
          <tr>
            <th>Scenario</th>
            <th>Checkpoint</th>
            <th>Commit</th>
            <th>Files</th>
            <th>Raw tokens</th>
            <th>Scenario tokens</th>
            <th>Saved</th>
            <th>Saved %</th>
            <th>Docs</th>
            <th>Indexed files</th>
          </tr>
        </thead>
        <tbody>
          {''.join(rows)}
        </tbody>
      </table>
    </section>

    <section class="card" style="margin-top:24px;">
      <h2>Benchmark 2: Incremental Update-Mode Example</h2>
      <p><span class="accent">Example:</span> {update['example_prompt']}</p>
      <div class="grid">
        <section class="card">
          <h3>v1 update workload</h3>
          <div class="metric"><span>Total tokens</span><strong>{update['aggregate']['v1_total_tokens']:,}</strong></div>
        </section>
        <section class="card best">
          <h3>latest update workload</h3>
          <div class="metric"><span>Total tokens</span><strong>{update['aggregate']['latest_total_tokens']:,}</strong></div>
          <div class="metric"><span>Saved vs v1</span><strong>{update['aggregate']['latest_saved_vs_v1']:,}</strong></div>
          <div class="metric"><span>Saved % vs v1</span><strong>{update['aggregate']['latest_saved_pct_vs_v1']:.2f}%</strong></div>
        </section>
      </div>
      <table>
        <thead>
          <tr>
            <th>Checkpoint</th>
            <th>Commit</th>
            <th>Change</th>
            <th>Changed files</th>
            <th>Delta scan tokens</th>
            <th>v1 total</th>
            <th>latest total</th>
            <th>Saved</th>
            <th>Saved %</th>
          </tr>
        </thead>
        <tbody>
          {''.join(update_rows)}
        </tbody>
      </table>
      <ul>{update_notes}</ul>
    </section>

    <p class="foot">Interpretation rule: token counts here are measured context-size proxies using one shared tokenizer heuristic across all scenarios.</p>
  </div>
</body>
</html>
"""


def parse_commit_arg(raw: str) -> tuple[str, str, str]:
    parts = raw.split(":", 2)
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("Expected --commit label:sha:description")
    return parts[0], parts[1], parts[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replay a feature stack and compare indexer scenarios")
    parser.add_argument("--repo-src", required=True, help="Path to the subject repository")
    parser.add_argument("--work-dir", required=True, help="Scratch directory used for the replay worktree")
    parser.add_argument("--report-dir", required=True, help="Directory for benchmark JSON and HTML output")
    parser.add_argument("--base", required=True, help="Base commit before replayed changes")
    parser.add_argument(
        "--commit",
        action="append",
        default=[],
        type=parse_commit_arg,
        help="Checkpoint as label:sha:description. Repeat for each replay commit.",
    )
    parser.add_argument("--v1-sha", required=True, help="Indexer v1 reference SHA used in the report")
    parser.add_argument("--latest-sha", required=True, help="Indexer latest reference SHA used in the report")
    parser.add_argument("--claude-path", default="CLAUDE.md", help="Path to CLAUDE.md within the subject repo")
    parser.add_argument("--docs-dir", default="docs", help="Path to docs directory within the subject repo")
    parser.add_argument("--json-name", default="benchmark-summary.json", help="JSON output filename")
    parser.add_argument("--html-name", default="benchmark-report.html", help="HTML output filename")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_src = Path(args.repo_src).resolve()
    work_dir = Path(args.work_dir).resolve()
    report_dir = Path(args.report_dir).resolve()
    worktree = work_dir / "repo-replay"
    json_out = report_dir / args.json_name
    html_out = report_dir / args.html_name
    claude_rel = Path(args.claude_path)
    docs_rel = Path(args.docs_dir)

    commits = [("base", args.base, "Base before replay")] + list(args.commit)
    scenarios = {
        "raw_unindexed": {
            "label": "No index",
            "description": "Raw source only. No .codebase-indexer docs present.",
        },
        "v1_full_index": {
            "label": "Indexer v1",
            "description": "Full five-doc index at every checkpoint.",
        },
        "latest_supplement": {
            "label": "Indexer latest",
            "description": "Supplement behavior using patterns, decisions, and changelog only.",
        },
    }

    ensure_dir(work_dir)
    ensure_dir(report_dir)
    if worktree.exists():
        shutil.rmtree(worktree)
    run(["git", "worktree", "add", "--detach", str(worktree), args.base], cwd=repo_src)

    try:
        results = {
            key: {
                "label": value["label"],
                "description": value["description"],
                "checkpoints": [],
            }
            for key, value in scenarios.items()
        }

        for scenario_key in scenarios:
            checkpoint = measure_scenario(
                worktree,
                *commits[0],
                scenario_key,
                claude_rel,
                docs_rel,
            )
            results[scenario_key]["checkpoints"].append(asdict(checkpoint))

        for checkpoint_label, commit_sha, description in commits[1:]:
            run(["git", "cherry-pick", "--keep-redundant-commits", commit_sha], cwd=worktree)
            for scenario_key in scenarios:
                checkpoint = measure_scenario(
                    worktree,
                    checkpoint_label,
                    commit_sha,
                    description,
                    scenario_key,
                    claude_rel,
                    docs_rel,
                )
                results[scenario_key]["checkpoints"].append(asdict(checkpoint))

        total_raw = sum(cp["raw_tokens"] for cp in results["raw_unindexed"]["checkpoints"])
        for scenario in results.values():
            total_docs = sum(cp["docs_tokens"] for cp in scenario["checkpoints"])
            saved = total_raw - total_docs
            scenario["aggregate"] = {
                "total_raw_tokens": total_raw,
                "total_docs_tokens": total_docs,
                "saved_vs_raw": saved,
                "saved_pct_vs_raw": round((saved / total_raw * 100.0), 2) if total_raw else 0.0,
                "avg_docs_tokens": round(total_docs / len(scenario["checkpoints"])),
                "avg_savings_pct": round(
                    sum(cp["savings_pct"] for cp in scenario["checkpoints"]) / len(scenario["checkpoints"]),
                    2,
                ),
            }

        best_key = min(results.keys(), key=lambda key: results[key]["aggregate"]["total_docs_tokens"])
        results[best_key]["why_best"] = [
            "It keeps the smallest repeated context surface across all checkpoints.",
            "It avoids carrying large documentation payloads when supplement behavior is enough.",
            "It wins most clearly when the repo already has strong architectural guidance elsewhere.",
        ]
        results["v1_full_index"].setdefault(
            "why_best",
            [
                "It still beats raw source because compact docs are cheaper than rereading the whole codebase.",
                "It carries more repeated doc weight than the latest supplement-style approach.",
            ],
        )
        results["raw_unindexed"].setdefault(
            "why_best",
            ["This is the control group and therefore the most expensive repeated context path."],
        )

        summary = {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S GMT"),
            "base_commit": args.base,
            "commit_range": [item[1] for item in commits],
            "v1_sha": args.v1_sha,
            "latest_sha": args.latest_sha,
            "scenarios": results,
            "best_scenario_key": best_key,
            "methodology": [
                "Checked out a clean detached worktree at the commit immediately before the replayed feature stack.",
                "Replayed identical commits across all scenarios.",
                "Used one token-estimation heuristic consistently across source and docs.",
                "Separated full-session replay from incremental maintenance workload.",
            ],
        }
        summary["update_benchmark"] = build_update_benchmark(worktree, commits, results)

        json_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        html_out.write_text(build_html(summary), encoding="utf-8")
        print(json.dumps({"json": str(json_out), "html": str(html_out)}, indent=2))
    finally:
        try:
            run(["git", "worktree", "remove", "--force", str(worktree)], cwd=repo_src)
        except subprocess.CalledProcessError:
            pass


if __name__ == "__main__":
    main()
