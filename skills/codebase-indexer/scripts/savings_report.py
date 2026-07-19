#!/usr/bin/env python3
"""Project-local savings report generator for codebase-indexer.

Outputs:
- terminal summary
- HTML report (tasteful, readable, transparent about estimation quality)
- combined mode for end-of-run defaults (terminal + new timestamped HTML)
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class SavingsEntry:
    date: str
    project: str
    project_root: str
    mode: str
    project_files: int
    graph_available: bool
    docs_generated: int
    docs_skipped: int
    tokens_raw_baseline_est: int
    tokens_indexer_run_est: int
    tokens_saved_this_run: int
    tokens_saved_future_est: int
    cost_saved_est_usd: float
    measurement_quality: str


def parse_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def size_bucket(files: int) -> str:
    if files < 50:
        return "small"
    if files <= 200:
        return "medium"
    if files <= 1000:
        return "large"
    return "xlarge"


def infer_baseline_tokens(project_files: int, mode: str) -> int:
    bucket = size_bucket(project_files)
    if mode in {"full", "supplement"}:
        return {
            "small": 12000,
            "medium": 30000,
            "large": 75000,
            "xlarge": 160000,
        }[bucket]

    # update mode baseline is scoped to changed areas, not full project scans
    return {
        "small": 9000,
        "medium": 22000,
        "large": 42000,
        "xlarge": 70000,
    }[bucket]


def normalize_entry(raw: dict[str, Any], project_root: str, price_per_million: float) -> SavingsEntry:
    project_files = int(raw.get("project_files", 0) or 0)
    mode = str(raw.get("mode", "update"))
    saved_this = int(raw.get("tokens_saved_this_run", 0) or 0)
    saved_future = int(raw.get("tokens_saved_future_est", 0) or 0)

    baseline = raw.get("tokens_raw_baseline_est")
    indexer = raw.get("tokens_indexer_run_est")

    if baseline is None and indexer is not None:
        baseline = int(indexer) + saved_this
    elif baseline is not None:
        baseline = int(baseline)

    if baseline is None:
        baseline = infer_baseline_tokens(project_files, mode)

    if indexer is None:
        indexer = max(0, int(baseline) - saved_this)
    else:
        indexer = int(indexer)

    quality = str(raw.get("measurement_quality", "estimated"))

    cost = raw.get("cost_saved_est_usd")
    if cost is None:
        cost = round((saved_this + saved_future) / 1_000_000 * price_per_million, 4)

    return SavingsEntry(
        date=str(raw.get("date", "")),
        project=str(raw.get("project", Path(project_root).name)),
        project_root=str(raw.get("project_root", project_root)),
        mode=mode,
        project_files=project_files,
        graph_available=bool(raw.get("graph_available", False)),
        docs_generated=int(raw.get("docs_generated", 0) or 0),
        docs_skipped=int(raw.get("docs_skipped", 0) or 0),
        tokens_raw_baseline_est=int(baseline),
        tokens_indexer_run_est=int(indexer),
        tokens_saved_this_run=saved_this,
        tokens_saved_future_est=saved_future,
        cost_saved_est_usd=float(cost),
        measurement_quality=quality,
    )


def fmt_int(n: int) -> str:
    return f"{n:,}"


def fmt_money(n: float) -> str:
    return f"${n:,.2f}"


def scan_docs_inventory(root: Path) -> list[dict[str, Any]]:
    docs_dir = root / ".codebase-indexer/docs"
    if not docs_dir.exists():
        return []
    files = []
    for f in sorted(docs_dir.glob("*.md")):
        stat = f.stat()
        files.append({
            "name": f.name,
            "size_kb": round(stat.st_size / 1024, 1),
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d"),
        })
    return files


def summarize(entries: list[SavingsEntry]) -> dict[str, Any]:
    entries_sorted = sorted(entries, key=lambda e: e.date)
    last = entries_sorted[-1]

    total_saved_this = sum(e.tokens_saved_this_run for e in entries_sorted)
    total_saved_future = sum(e.tokens_saved_future_est for e in entries_sorted)
    total_saved = total_saved_this + total_saved_future
    total_cost = sum(e.cost_saved_est_usd for e in entries_sorted)

    mode_tokens: dict[str, int] = defaultdict(int)
    mode_counts: dict[str, int] = defaultdict(int)
    for e in entries_sorted:
        mode_counts[e.mode] += 1
        mode_tokens[e.mode] += e.tokens_saved_this_run + e.tokens_saved_future_est

    measured_runs = sum(1 for e in entries_sorted if e.measurement_quality == "measured")
    estimated_runs = len(entries_sorted) - measured_runs
    graph_runs = sum(1 for e in entries_sorted if e.graph_available)

    # Efficiency: what % of baseline tokens were avoided across all runs
    total_baseline = sum(e.tokens_raw_baseline_est for e in entries_sorted)
    total_used = sum(e.tokens_indexer_run_est for e in entries_sorted)
    avg_efficiency_pct = round((1 - total_used / max(total_baseline, 1)) * 100)

    # Sessions where update mode ran = real-time savings sessions
    sessions_protected = sum(1 for e in entries_sorted if e.mode == "update")

    # Token-to-pages: ~750 tokens ≈ 1 page of text
    total_pages_saved = max(1, round(total_saved / 750))

    # ROI payback: how many update sessions until index cost is recouped
    # Based on the most recent full/supplement run
    full_mode_runs = [e for e in entries_sorted if e.mode in {"full", "supplement"}]
    payback_sessions: int | None = None
    if full_mode_runs:
        last_full = full_mode_runs[-1]
        if last_full.tokens_saved_future_est > 0:
            payback_sessions = max(1, round(last_full.tokens_indexer_run_est / last_full.tokens_saved_future_est))

    return {
        "runs": len(entries_sorted),
        "period_start": entries_sorted[0].date,
        "period_end": entries_sorted[-1].date,
        "last": last,
        "total_saved_this": total_saved_this,
        "total_saved_future": total_saved_future,
        "total_saved": total_saved,
        "total_cost": total_cost,
        "mode_counts": dict(mode_counts),
        "mode_tokens": dict(mode_tokens),
        "measured_runs": measured_runs,
        "estimated_runs": estimated_runs,
        "graph_runs": graph_runs,
        "recent": entries_sorted[-5:],
        "all_entries": entries_sorted,
        "avg_efficiency_pct": avg_efficiency_pct,
        "sessions_protected": sessions_protected,
        "total_pages_saved": total_pages_saved,
        "payback_sessions": payback_sessions,
    }


def mode_order(mode: str) -> tuple[int, str]:
    preferred = {
        "full": 0,
        "supplement": 1,
        "update": 2,
        "benchmark_measured": 3,
    }
    return (preferred.get(mode, 99), mode)


def terminal_report(summary: dict[str, Any], project_root: str) -> str:
    last: SavingsEntry = summary["last"]
    lines: list[str] = []

    lines.append("Codebase Indexer Savings (Project)")
    lines.append(f"Project            : {last.project}")
    lines.append(f"Path               : {project_root}")
    lines.append(f"Period             : {summary['period_start']} -> {summary['period_end']}")
    lines.append(f"Runs               : {summary['runs']}")
    lines.append(f"Avg efficiency     : {summary['avg_efficiency_pct']}% context reduction")
    lines.append(f"Sessions protected : {summary['sessions_protected']} update run(s)")
    lines.append(f"~Pages saved       : ~{summary['total_pages_saved']} pages of source not loaded")
    lines.append("")

    lines.append("A/B This Run (Raw Rescan vs Indexer)")
    lines.append(f"Raw rescan counterfactual : {fmt_int(last.tokens_raw_baseline_est)} tokens")
    lines.append(f"Indexer path              : {fmt_int(last.tokens_indexer_run_est)} tokens")
    lines.append(f"Saved this run            : {fmt_int(last.tokens_saved_this_run)} tokens")
    lines.append(f"Future est benefit : {fmt_int(last.tokens_saved_future_est)} tokens")
    lines.append(f"Mode / Graph       : {last.mode} / {'yes' if last.graph_available else 'no'}")
    if summary["payback_sessions"] is not None:
        lines.append(f"ROI payback        : ~{summary['payback_sessions']} future sessions to recoup index cost")
    lines.append("")

    lines.append("Cumulative Savings")
    lines.append(f"Saved this-run     : {fmt_int(summary['total_saved_this'])} tokens")
    lines.append(f"Saved future-est   : {fmt_int(summary['total_saved_future'])} tokens")
    lines.append(f"Saved total        : {fmt_int(summary['total_saved'])} tokens")
    lines.append(f"Estimated cost     : {fmt_money(summary['total_cost'])}")
    lines.append("")

    lines.append("Breakdown by Mode")
    all_modes = sorted(summary["mode_counts"].keys(), key=mode_order)
    for mode in all_modes:
        count = summary["mode_counts"].get(mode, 0)
        tokens = summary["mode_tokens"].get(mode, 0)
        lines.append(f"{mode:<18}: x{count:<3} {fmt_int(tokens)} tokens")
    lines.append("")

    lines.append("Measurement Quality")
    lines.append(f"Measured runs      : {summary['measured_runs']}")
    lines.append(f"Estimated runs     : {summary['estimated_runs']}")
    lines.append("Method note        : Counterfactual baseline is estimated unless quality is marked measured.")
    lines.append("")

    lines.append("Recent Runs")
    lines.append("date       mode        files  docs  graph  saved_this   saved_future   quality")
    for e in summary["recent"]:
        lines.append(
            f"{e.date:<10} {e.mode:<11} {e.project_files:>5}  {e.docs_generated:>4}  {'y' if e.graph_available else 'n':>5}  "
            f"{fmt_int(e.tokens_saved_this_run):>10} {fmt_int(e.tokens_saved_future_est):>13}   {e.measurement_quality}"
        )

    return "\n".join(lines)


def mode_bar(value: int, max_value: int) -> str:
    if max_value <= 0:
        return "0%"
    pct = int((value / max_value) * 100)
    return f"{pct}%"


MODE_COLORS = {
    "full": "#3b82f6",
    "supplement": "#d97706",
    "update": "#0e7a66",
    "benchmark_measured": "#7c3aed",
}

MODE_DESCRIPTIONS = {
        "full": "First-time scan — generates all .codebase-indexer/docs/. Savings come in future sessions.",
    "supplement": "Adds missing docs without re-scanning existing ones. Cheaper than full.",
    "update": "Triggered after code changes. Refreshes only affected docs. Saves tokens immediately.",
    "benchmark_measured": "Manual A/B test with exact token counts measured from file sizes.",
}


def html_report(summary: dict[str, Any], project_root: str, docs_inventory: list[dict[str, Any]]) -> str:
    last: SavingsEntry = summary["last"]
    mode_tokens = summary["mode_tokens"]
    max_mode = max(mode_tokens.values()) if mode_tokens else 1

    # A/B visual bar percentages
    ab_baseline = last.tokens_raw_baseline_est
    ab_indexer_pct = int((last.tokens_indexer_run_est / max(ab_baseline, 1)) * 100)
    ab_saved_pct = int((last.tokens_saved_this_run / max(ab_baseline, 1)) * 100)
    ab_future_pct = int((last.tokens_saved_future_est / max(ab_baseline, 1)) * 100)
    ab_remaining_pct = max(0, 100 - ab_indexer_pct - ab_saved_pct - ab_future_pct)

    # Mode contribution bars
    bars = []
    all_modes = sorted(summary["mode_counts"].keys(), key=mode_order)
    for mode in all_modes:
        value = mode_tokens.get(mode, 0)
        pct = mode_bar(value, max_mode)
        color = MODE_COLORS.get(mode, "#6a5e50")
        bars.append(
            f"""
            <div class="bar-row">
              <div class="bar-label">{mode}</div>
              <div class="bar-track"><div class="bar-fill" style="width:{pct};background:{color}"></div></div>
              <div class="bar-value">{fmt_int(value)}</div>
            </div>
            """
        )

    # Full history table rows (all runs, newest first)
    all_rows = []
    for e in reversed(summary["all_entries"]):
        color = MODE_COLORS.get(e.mode, "#6a5e50")
        graph_badge = '<span class="badge badge-graph">graph</span>' if e.graph_available else ""
        quality_badge = f'<span class="badge badge-{"measured" if e.measurement_quality == "measured" else "est"}">{"measured" if e.measurement_quality == "measured" else "est"}</span>'
        all_rows.append(
            f"""<tr>
              <td>{e.date}</td>
              <td><span class="mode-badge" style="background:{color}15;color:{color};border-color:{color}40">{e.mode}</span></td>
              <td class="num">{e.project_files:,}</td>
              <td class="num">{e.docs_generated}</td>
              <td>{graph_badge}</td>
              <td class="num">{fmt_int(e.tokens_raw_baseline_est)}</td>
              <td class="num">{fmt_int(e.tokens_indexer_run_est)}</td>
              <td class="num strong">{fmt_int(e.tokens_saved_this_run)}</td>
              <td class="num">{fmt_int(e.tokens_saved_future_est)}</td>
              <td>{quality_badge}</td>
            </tr>"""
        )
    all_rows_html = "\n".join(all_rows)

    # Docs inventory rows
    docs_rows = ""
    if docs_inventory:
        docs_rows = "\n".join(
            f'<tr><td>{d["name"]}</td><td class="num">{d["size_kb"]} KB</td><td>{d["modified"]}</td></tr>'
            for d in docs_inventory
        )

    # ROI payback note
    payback_html = ""
    if summary["payback_sessions"] is not None:
        payback_html = f'<div class="payback">ROI: Indexing cost recoups after approximately <strong>{summary["payback_sessions"]} future update session{"s" if summary["payback_sessions"] != 1 else ""}</strong>.</div>'

    # Mode explainer rows
    mode_explain_rows = "\n".join(
        f'<tr><td><span class="mode-badge" style="background:{MODE_COLORS.get(m, "#6a5e50")}15;color:{MODE_COLORS.get(m, "#6a5e50")};border-color:{MODE_COLORS.get(m, "#6a5e50")}40">{m}</span></td><td>{desc}</td></tr>'
        for m, desc in MODE_DESCRIPTIONS.items()
    )

    # Docs panel (conditional)
    docs_panel = ""
    if docs_inventory:
        docs_panel = f"""
    <section class="panel">
      <h2>Docs Index ({len(docs_inventory)} files)</h2>
      <p class="panel-note">These are the pre-built index files Claude reads instead of loading raw source code. Each file represents N tokens no longer needed from source files per session.</p>
      <table>
        <thead><tr><th>File</th><th>Size</th><th>Last Updated</th></tr></thead>
        <tbody>{docs_rows}</tbody>
      </table>
    </section>"""

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Codebase Indexer Savings</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #f7f4ef;
      --bg-2: #efe8dd;
      --ink: #1f1a14;
      --muted: #6a5e50;
      --card: rgba(255,255,255,0.72);
      --stroke: rgba(56,44,31,0.14);
      --accent: #0e7a66;
      --accent-soft: rgba(14,122,102,0.18);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: 'IBM Plex Sans', system-ui, sans-serif;
      color: var(--ink);
      background: radial-gradient(1200px 700px at 80% -10%, #e1d2be 0%, transparent 60%),
                  radial-gradient(900px 500px at -10% 10%, #d8e9df 0%, transparent 55%),
                  linear-gradient(180deg, var(--bg), var(--bg-2));
      min-height: 100vh;
      animation: fadein 560ms cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .wrap {{ max-width: 1040px; margin: 36px auto 72px; padding: 0 20px; }}
    .hero {{ margin-bottom: 22px; }}
    h1 {{
      font-family: 'Fraunces', serif;
      font-size: clamp(2rem, 4vw, 3rem);
      line-height: 1.06;
      margin: 0 0 8px;
      letter-spacing: -0.02em;
    }}
    .sub {{ color: var(--muted); font-size: 1rem; }}
    .efficiency-bar {{
      margin-top: 10px;
      font-size: .95rem;
      color: var(--ink);
    }}
    .efficiency-bar strong {{ color: var(--accent); }}
    .efficiency-bar .sep {{ color: var(--stroke); margin: 0 6px; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin: 20px 0 24px;
    }}
    .card {{
      background: var(--card);
      border: 1px solid var(--stroke);
      border-radius: 16px;
      padding: 14px 14px 12px;
      backdrop-filter: blur(6px);
      box-shadow: 0 8px 30px rgba(27,20,13,0.06);
    }}
    .k {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }}
    .v {{ font-size: 1.5rem; font-weight: 600; margin-top: 4px; }}
    .v-sub {{ font-size: .75rem; color: var(--muted); margin-top: 2px; }}
    .card-accent {{ border-color: rgba(14,122,102,0.35); background: rgba(14,122,102,0.06); }}
    .card-accent .v {{ color: var(--accent); }}
    .panel {{
      background: var(--card);
      border: 1px solid var(--stroke);
      border-radius: 18px;
      padding: 18px;
      margin-bottom: 14px;
    }}
    .panel-note {{ color: var(--muted); font-size: .88rem; margin: -6px 0 12px; }}
    h2 {{ font-size: 1.08rem; margin: 0 0 14px; letter-spacing: 0.01em; }}
    /* A/B visual bar */
    .ab-visual {{ margin: 14px 0 10px; }}
    .ab-track {{
      height: 32px;
      border-radius: 8px;
      background: #ece5da;
      overflow: hidden;
      display: flex;
      position: relative;
    }}
    .ab-seg {{
      height: 100%;
      display: flex;
      align-items: center;
      padding: 0 8px;
      font-size: .78rem;
      font-weight: 600;
      white-space: nowrap;
      overflow: hidden;
      transition: width .6s cubic-bezier(0.16,1,0.3,1);
    }}
    .ab-seg-indexer {{ background: #3b82f6; color: #fff; }}
    .ab-seg-saved {{ background: var(--accent); color: #fff; }}
    .ab-seg-future {{ background: rgba(14,122,102,0.45); color: #fff; }}
    .ab-legend {{ display: flex; gap: 14px; margin-top: 8px; flex-wrap: wrap; }}
    .ab-legend-item {{ display: flex; align-items: center; gap: 5px; font-size: .82rem; color: var(--muted); }}
    .ab-legend-dot {{ width: 10px; height: 10px; border-radius: 3px; flex-shrink: 0; }}
    .payback {{
      margin-top: 12px;
      padding: 10px 12px;
      background: rgba(14,122,102,0.08);
      border: 1px solid rgba(14,122,102,0.2);
      border-radius: 10px;
      font-size: .88rem;
    }}
    /* Mode contribution bars */
    .bar-row {{ display: grid; grid-template-columns: 108px 1fr 130px; gap: 10px; align-items: center; margin-bottom: 10px; }}
    .bar-label {{ color: var(--muted); text-transform: uppercase; font-size: 12px; letter-spacing: .08em; }}
    .bar-track {{ height: 10px; border-radius: 999px; background: #ece5da; overflow: hidden; }}
    .bar-fill {{ height: 100%; border-radius: 999px; transition: width .5s cubic-bezier(0.16,1,0.3,1); }}
    .bar-value {{ text-align: right; font-variant-numeric: tabular-nums; font-size: .9rem; }}
    /* Tables */
    table {{ width: 100%; border-collapse: collapse; font-size: .9rem; }}
    th, td {{ text-align: left; padding: 9px 8px; border-bottom: 1px solid var(--stroke); }}
    th {{ color: var(--muted); font-weight: 600; font-size: .78rem; letter-spacing: .06em; text-transform: uppercase; }}
    .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
    .strong {{ font-weight: 600; }}
    .foot {{ color: var(--muted); font-size: .88rem; margin-top: 10px; }}
    /* Badges */
    .mode-badge {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: .78rem;
      font-weight: 600;
      border: 1px solid transparent;
    }}
    .badge {{
      display: inline-block;
      padding: 2px 7px;
      border-radius: 6px;
      font-size: .75rem;
      font-weight: 600;
    }}
    .badge-measured {{ background: #ede9fe; color: #7c3aed; }}
    .badge-est {{ background: #f3f4f6; color: #6b7280; }}
    .badge-graph {{ background: rgba(14,122,102,0.12); color: var(--accent); }}
    /* Explainer collapsible */
    details {{ margin-bottom: 14px; }}
    summary {{
      cursor: pointer;
      padding: 14px 18px;
      background: var(--card);
      border: 1px solid var(--stroke);
      border-radius: 14px;
      font-weight: 600;
      font-size: .95rem;
      list-style: none;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    summary::-webkit-details-marker {{ display: none; }}
    summary::after {{ content: "›"; font-size: 1.2rem; color: var(--muted); transform: rotate(90deg); display: inline-block; transition: transform .2s; }}
    details[open] summary::after {{ transform: rotate(270deg); }}
    details[open] summary {{
      border-radius: 14px 14px 0 0;
      border-bottom-color: transparent;
    }}
    .explainer-body {{
      background: var(--card);
      border: 1px solid var(--stroke);
      border-top: none;
      border-radius: 0 0 14px 14px;
      padding: 16px 18px;
    }}
    .explainer-body p {{ margin: 0 0 10px; font-size: .9rem; color: var(--muted); }}
    .explainer-body table th {{ font-size: .75rem; }}
    .explainer-body table td {{ font-size: .88rem; }}
    /* History toggle */
    .show-all-btn {{
      background: none;
      border: 1px solid var(--stroke);
      border-radius: 8px;
      padding: 6px 14px;
      font-size: .85rem;
      color: var(--muted);
      cursor: pointer;
      margin-top: 10px;
    }}
    .show-all-btn:hover {{ background: rgba(0,0,0,0.04); }}
    #all-history {{ display: none; }}
    #all-history.visible {{ display: table-row-group; }}
    @media (max-width: 900px) {{
      .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .bar-row {{ grid-template-columns: 80px 1fr 90px; }}
    }}
    @media (max-width: 620px) {{
      .grid {{ grid-template-columns: 1fr; }}
    }}
    @keyframes fadein {{ from {{ opacity: 0; transform: translateY(4px); }} to {{ opacity: 1; transform: translateY(0); }} }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <h1>Codebase Savings Report</h1>
      <div class="sub">{last.project} · {project_root} · {summary['period_start']} to {summary['period_end']}</div>
      <div class="efficiency-bar">
        <strong>{summary['avg_efficiency_pct']}% avg context reduction</strong>
        <span class="sep">·</span> ≈{summary['total_pages_saved']:,} pages of source not loaded
        <span class="sep">·</span> {summary['sessions_protected']} update session{"s" if summary["sessions_protected"] != 1 else ""} protected
      </div>
    </div>

    <section class="grid">
      <article class="card"><div class="k">Total Runs</div><div class="v">{summary['runs']}</div></article>
      <article class="card card-accent"><div class="k">Saved This-Run (total)</div><div class="v">{fmt_int(summary['total_saved_this'])}</div><div class="v-sub">tokens</div></article>
      <article class="card"><div class="k">Future Est. Savings</div><div class="v">{fmt_int(summary['total_saved_future'])}</div><div class="v-sub">tokens across future sessions</div></article>
      <article class="card"><div class="k">Estimated Value</div><div class="v">{fmt_money(summary['total_cost'])}</div><div class="v-sub">@ $3/M tokens</div></article>
    </section>

    <details>
      <summary>How the indexer saves tokens</summary>
      <div class="explainer-body">
        <p>The indexer pre-builds <code>.codebase-indexer/docs/</code> index files so Claude reads a compact summary instead of loading raw source code. The <strong>baseline</strong> is what it would cost to answer the same questions by scanning source files directly — a counterfactual estimate based on project size.</p>
        <p><strong>Tokens → pages:</strong> ~750 tokens ≈ 1 page of text. A 20,000-token saving is roughly 27 pages of source code Claude no longer needs to read.</p>
        <table>
          <thead><tr><th>Mode</th><th>What it does</th></tr></thead>
          <tbody>{mode_explain_rows}</tbody>
        </table>
      </div>
    </details>

    <section class="panel">
      <h2>A/B: Last Run — Raw Rescan vs Indexer</h2>
      <div class="ab-visual">
        <div class="ab-track">
          <div class="ab-seg ab-seg-indexer" style="width:{ab_indexer_pct}%">{fmt_int(last.tokens_indexer_run_est)}</div>
          <div class="ab-seg ab-seg-saved" style="width:{ab_saved_pct}%">{'+' + fmt_int(last.tokens_saved_this_run) if last.tokens_saved_this_run > 0 else ''}</div>
          <div class="ab-seg ab-seg-future" style="width:{ab_future_pct}%">{'+' + fmt_int(last.tokens_saved_future_est) if last.tokens_saved_future_est > 0 else ''}</div>
        </div>
        <div class="ab-legend">
          <div class="ab-legend-item"><div class="ab-legend-dot" style="background:#3b82f6"></div>Indexer used: {fmt_int(last.tokens_indexer_run_est)} tokens</div>
          <div class="ab-legend-item"><div class="ab-legend-dot" style="background:var(--accent)"></div>Saved now: {fmt_int(last.tokens_saved_this_run)} tokens</div>
          <div class="ab-legend-item"><div class="ab-legend-dot" style="background:rgba(14,122,102,0.45)"></div>Future est: {fmt_int(last.tokens_saved_future_est)} tokens</div>
          <div class="ab-legend-item"><div class="ab-legend-dot" style="background:#ece5da;border:1px solid #ccc"></div>Baseline: {fmt_int(last.tokens_raw_baseline_est)} tokens total</div>
        </div>
      </div>
      {payback_html}
      <div class="foot">Mode: <b>{last.mode}</b> · Graph: <b>{'yes' if last.graph_available else 'no'}</b> · Quality: <b>{last.measurement_quality}</b>. Baseline is a no-indexer counterfactual unless marked measured.</div>
    </section>

    <section class="panel">
      <h2>Mode Contribution</h2>
      {''.join(bars)}
    </section>

    {docs_panel}

    <section class="panel">
      <h2>Run History</h2>
      <table>
        <thead>
          <tr>
            <th>Date</th><th>Mode</th><th>Files</th><th>Docs</th><th>Graph</th>
            <th>Raw baseline</th><th>Indexer run</th><th>Saved now</th><th>Future est</th><th>Quality</th>
          </tr>
        </thead>
        <tbody id="recent-rows">
          {chr(10).join(all_rows[:5])}
        </tbody>
        <tbody id="all-history">
          {chr(10).join(all_rows[5:])}
        </tbody>
      </table>
      {"" if len(all_rows) <= 5 else f'<button class="show-all-btn" onclick="var el=document.getElementById(&quot;all-history&quot;);el.classList.toggle(&quot;visible&quot;);this.textContent=el.classList.contains(&quot;visible&quot;)?&quot;Show less&quot;:&quot;Show all {len(all_rows)} runs&quot;">Show all {len(all_rows)} runs</button>'}
      <div class="foot">Generated {generated_at}. Estimated values use codebase-indexer sizing heuristics unless quality is <b>measured</b>.</div>
    </section>
  </div>
</body>
</html>
"""


def timestamped_output_path(output_path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return output_path.with_name(f"{output_path.stem}-{stamp}{output_path.suffix}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate project-local codebase-indexer savings report")
    parser.add_argument("--project-root", default=".", help="Project root")
    parser.add_argument("--input", default=".codebase-indexer/savings.jsonl", help="Savings JSONL path (relative to project root unless absolute)")
    parser.add_argument("--format", choices=["terminal", "html", "both"], default="terminal", help="Output format")
    parser.add_argument("--output", default=".codebase-indexer/reports/codebase-indexer-savings.html", help="HTML output path (relative to project root unless absolute)")
    parser.add_argument("--timestamp-html", choices=["yes", "no"], default="yes", help="When writing HTML, append timestamp to filename")
    parser.add_argument("--price-per-million", type=float, default=3.0, help="USD per 1M input tokens")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = root / input_path

    raw_entries = parse_jsonl(input_path)
    if not raw_entries:
        print("No project-local savings data found. Run /codebase-indexer first to log savings.")
        return

    root_str = str(root)
    filtered = [
        e for e in raw_entries
        if str(e.get("project_root", root_str)) == root_str
    ]
    if not filtered:
        print("No savings entries found for this project root.")
        return

    entries = [normalize_entry(e, root_str, args.price_per_million) for e in filtered]
    summary = summarize(entries)

    if args.format == "terminal":
        print(terminal_report(summary, root_str))
        return

    docs_inventory = scan_docs_inventory(root)
    html = html_report(summary, root_str, docs_inventory)
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = root / output_path
    if args.timestamp_html == "yes":
        output_path = timestamped_output_path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    if args.format == "html":
        print(str(output_path))
        return

    # both mode: terminal first, then generated file path
    print(terminal_report(summary, root_str))
    print("")
    print(f"HTML report: {output_path}")


if __name__ == "__main__":
    main()
