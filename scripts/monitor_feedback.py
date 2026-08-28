"""
Qubeessaa AI — Feedback Monitor
================================
Reads user_feedback.json and produces a human-readable report covering:

  - Overall accept / reject counts
  - Top accepted corrections  (candidates to promote to common_words)
  - Top rejected corrections  (candidates to investigate / blacklist)
  - High-volume REVIEW candidates flagged by the live app
  - Corrections that hit the feedback boost cap (freq boost >= 5000)
  - Reject-rate anomalies  (corrections rejected > 30 % of the time)
  - Full chronological history (optional, --history flag)

Usage
-----
    python scripts/monitor_feedback.py
    python scripts/monitor_feedback.py --top 20
    python scripts/monitor_feedback.py --history
    python scripts/monitor_feedback.py --export report.txt

Arguments
---------
  --top N        Show top N entries per section  (default: 10)
  --history      Print full correction history at the end
  --export FILE  Save the report to a text file as well as printing it
  --json FILE    Path to user_feedback.json  (default: user_feedback.json)
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


# ── constants ──────────────────────────────────────────────────────────────
MAX_FEEDBACK_BOOST = 5_000   # must match _MAX_FEEDBACK_BOOST in spell_checker_ml.py
REJECT_RATE_THRESHOLD = 0.30  # flag if rejects / total >= 30 %
DEFAULT_FEEDBACK_PATH = Path(__file__).parent.parent / "user_feedback.json"


# ── helpers ────────────────────────────────────────────────────────────────

def load_feedback(path: Path) -> dict:
    if not path.exists():
        print(f"[warn] {path} not found — no feedback recorded yet.")
        return {"feedback": {}, "history": []}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def parse_pairs(feedback: dict) -> dict:
    """
    Returns a dict of:
        (original, corrected) -> {"accepts": int, "rejects": int}
    Reject keys are stored as  "rejected:original->corrected".
    """
    pairs: dict = defaultdict(lambda: {"accepts": 0, "rejects": 0})
    for key, count in feedback.items():
        if key.startswith("rejected:"):
            real_key = key[len("rejected:"):]
            if "->" in real_key:
                orig, corr = real_key.split("->", 1)
                pairs[(orig, corr)]["rejects"] = count
        elif "->" in key:
            orig, corr = key.split("->", 1)
            pairs[(orig, corr)]["accepts"] = count
    return dict(pairs)


def reject_rate(data: dict) -> float:
    total = data["accepts"] + data["rejects"]
    return data["rejects"] / total if total else 0.0


def fmt_pair(orig: str, corr: str) -> str:
    return f"'{orig}' → '{corr}'"


def divider(char: str = "─", width: int = 60) -> str:
    return char * width


# ── report sections ────────────────────────────────────────────────────────

def section_summary(pairs: dict, history: list) -> str:
    total_accepts = sum(v["accepts"] for v in pairs.values())
    total_rejects = sum(v["rejects"] for v in pairs.values())
    total_events  = total_accepts + total_rejects
    unique_pairs  = len(pairs)
    history_count = len(history)

    first_event = history[0]["timestamp"][:10] if history else "n/a"
    last_event  = history[-1]["timestamp"][:10] if history else "n/a"

    lines = [
        divider("═"),
        "  Qubeessaa AI — Feedback Report",
        f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        divider("═"),
        f"  Total feedback events : {total_events:,}",
        f"  Accepted              : {total_accepts:,}",
        f"  Rejected              : {total_rejects:,}",
        f"  Unique correction pairs: {unique_pairs:,}",
        f"  History entries       : {history_count:,}",
        f"  Date range            : {first_event}  →  {last_event}",
        divider(),
    ]
    return "\n".join(lines)


def section_top_accepted(pairs: dict, top_n: int) -> str:
    ranked = sorted(pairs.items(), key=lambda x: x[1]["accepts"], reverse=True)
    lines = [
        "",
        f"  TOP {top_n} MOST ACCEPTED CORRECTIONS",
        f"  (Consider adding highly-accepted words to common_words in spell_checker_ml.py)",
        divider(),
    ]
    for (orig, corr), data in ranked[:top_n]:
        bar = "█" * min(data["accepts"], 30)
        lines.append(
            f"  {fmt_pair(orig, corr):<35}  "
            f"✓ {data['accepts']:>4}  ✗ {data['rejects']:>4}  {bar}"
        )
    return "\n".join(lines)


def section_top_rejected(pairs: dict, top_n: int) -> str:
    ranked = sorted(pairs.items(), key=lambda x: x[1]["rejects"], reverse=True)
    top = [(k, v) for k, v in ranked if v["rejects"] > 0][:top_n]
    if not top:
        return "\n  TOP REJECTED: no rejections recorded yet.\n"
    lines = [
        "",
        f"  TOP {top_n} MOST REJECTED CORRECTIONS",
        f"  (These corrections are wrong — investigate and consider blacklisting)",
        divider(),
    ]
    for (orig, corr), data in top:
        rr = reject_rate(data)
        flag = "  ⚠ HIGH REJECT RATE" if rr >= REJECT_RATE_THRESHOLD else ""
        lines.append(
            f"  {fmt_pair(orig, corr):<35}  "
            f"✓ {data['accepts']:>4}  ✗ {data['rejects']:>4}  "
            f"({rr:.0%} rejected){flag}"
        )
    return "\n".join(lines)


def section_anomalies(pairs: dict) -> str:
    anomalies = [
        (k, v) for k, v in pairs.items()
        if reject_rate(v) >= REJECT_RATE_THRESHOLD and v["rejects"] >= 3
    ]
    if not anomalies:
        return "\n  ANOMALIES: none detected.\n"
    lines = [
        "",
        "  REJECT-RATE ANOMALIES  (>= 30% rejection, >= 3 rejects)",
        "  These corrections are likely wrong and need attention.",
        divider(),
    ]
    for (orig, corr), data in sorted(anomalies, key=lambda x: reject_rate(x[1]), reverse=True):
        rr = reject_rate(data)
        lines.append(f"  {fmt_pair(orig, corr):<35}  reject rate: {rr:.0%}  "
                     f"(✓{data['accepts']} / ✗{data['rejects']})")
    return "\n".join(lines)


def section_boost_cap(pairs: dict) -> str:
    capped = [
        (k, v) for k, v in pairs.items()
        if v["accepts"] * 100 >= MAX_FEEDBACK_BOOST
    ]
    if not capped:
        return "\n  BOOST CAP: no corrections have hit the boost cap yet.\n"
    lines = [
        "",
        f"  BOOST-CAP REACHED  (accepted >= {MAX_FEEDBACK_BOOST // 100}x)",
        f"  These words have maximum frequency boost. No further boost is applied.",
        f"  Consider permanently adding them to common_words.",
        divider(),
    ]
    for (orig, corr), data in sorted(capped, key=lambda x: x[1]["accepts"], reverse=True):
        lines.append(f"  {fmt_pair(orig, corr):<35}  accepted {data['accepts']}x  "
                     f"(boost cap: {MAX_FEEDBACK_BOOST:,})")
    return "\n".join(lines)


def section_promote_suggestions(pairs: dict) -> str:
    """Words accepted >= 5x with zero rejects — safe to promote."""
    promotable = [
        (k, v) for k, v in pairs.items()
        if v["accepts"] >= 5 and v["rejects"] == 0
    ]
    if not promotable:
        return "\n  PROMOTE SUGGESTIONS: none qualify yet (need >=5 accepts, 0 rejects).\n"
    lines = [
        "",
        "  PROMOTE TO common_words  (accepted >= 5x, never rejected)",
        "  Add these to self.common_words in spell_checker_ml.py with freq >= 7000.",
        divider(),
    ]
    for (orig, corr), data in sorted(promotable, key=lambda x: x[1]["accepts"], reverse=True):
        lines.append(f"  '{corr}'   — accepted {data['accepts']}x from '{orig}'")
    return "\n".join(lines)


def section_history(history: list) -> str:
    if not history:
        return "\n  HISTORY: empty.\n"
    lines = [
        "",
        f"  FULL CORRECTION HISTORY  ({len(history)} entries)",
        divider(),
        f"  {'Timestamp':<22} {'Original':<18} {'Corrected':<18} {'Action'}",
        f"  {'─'*22} {'─'*18} {'─'*18} {'─'*8}",
    ]
    for entry in history:
        ts   = entry.get("timestamp", "")[:19]
        orig = entry.get("original", "")[:16]
        corr = entry.get("corrected", "")[:16]
        act  = "✓ accepted" if entry.get("accepted") else "✗ rejected"
        lines.append(f"  {ts:<22} {orig:<18} {corr:<18} {act}")
    return "\n".join(lines)


# ── main ───────────────────────────────────────────────────────────────────

def build_report(data: dict, top_n: int, include_history: bool) -> str:
    feedback = data.get("feedback", {})
    history  = data.get("history", [])
    pairs    = parse_pairs(feedback)

    parts = [
        section_summary(pairs, history),
        section_top_accepted(pairs, top_n),
        section_top_rejected(pairs, top_n),
        section_anomalies(pairs),
        section_boost_cap(pairs),
        section_promote_suggestions(pairs),
    ]
    if include_history:
        parts.append(section_history(history))

    parts.append("\n" + divider("═") + "\n")
    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Qubeessaa AI — Feedback Monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--top",     type=int, default=10, metavar="N",
                        help="Show top N entries per section (default: 10)")
    parser.add_argument("--history", action="store_true",
                        help="Print full correction history")
    parser.add_argument("--export",  type=str, default=None, metavar="FILE",
                        help="Save report to FILE as well as printing it")
    parser.add_argument("--json",    type=str,
                        default=str(DEFAULT_FEEDBACK_PATH), metavar="FILE",
                        help="Path to user_feedback.json")
    args = parser.parse_args()

    data   = load_feedback(Path(args.json))
    report = build_report(data, args.top, args.history)

    print(report)

    if args.export:
        export_path = Path(args.export)
        export_path.write_text(report, encoding="utf-8")
        print(f"Report saved to: {export_path}")


if __name__ == "__main__":
    main()
