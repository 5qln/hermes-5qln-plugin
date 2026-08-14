#!/usr/bin/env python3
"""
axis_stasis.py — The 5QLN Axis Stasis Detector

The Bilevel's stuck-detection, made 5QLN-native. Reads the centrifuge
parametric trail and flags when the axis has stopped turning: K consecutive
readings in which the axis signature (alpha_direction, inf0p_scope) is
constant while the underlying content keeps changing (signature_sha moves).

Lineage: Karpathy's Bilevel outer loop exists to catch the inner loop
"falling into the same search patterns even when they stopped working."
The centrifuge measures the axis; this operator detects its arrest.

Authority: it ONLY flags. It never drafts search-policy changes (the
self-evolution orchestrator's job, H-gated), never certifies anything clean
or alive, and does not touch corruption — L1-L4/V∅ remain the corruption
watcher's sealed territory. Verdict vocabulary is fixed:
STASIS / MOVING / STILL / INSUFFICIENT_DATA.

Trail file: $QLN_WIKI/state/centrifuge_trail.json — same resolution as
centrifuge_parametric.py (override: CENTRIFUGE_TRAIL_PATH env or --trail).
State: Python stdlib only.
"""

import argparse
import json
import os
from typing import Any

DEFAULT_K = 3

VERDICTS = ("STASIS", "MOVING", "STILL", "INSUFFICIENT_DATA")


def resolve_trail_path() -> str:
    explicit = os.environ.get("CENTRIFUGE_TRAIL_PATH")
    if explicit:
        return os.path.expanduser(explicit)
    wiki = os.environ.get("QLN_WIKI", os.path.expanduser("~/wiki"))
    return os.path.join(os.path.expanduser(wiki), "state", "centrifuge_trail.json")


def axis_signature(reading: dict) -> tuple[str, str] | None:
    """The axis of one reading: where alpha points, where infinity-prime opens.

    Returns None when either dimension is unknown — stasis is never claimed
    on unknown ground.
    """
    alpha = reading.get("alpha_direction")
    scope = reading.get("inf0p_scope")
    if alpha in (None, "unknown") or scope in (None, "unknown"):
        return None
    return (str(alpha), str(scope))


def detect_stasis(readings: list[dict], k: int = DEFAULT_K) -> dict[str, Any]:
    """Scan the most recent k readings for axis stasis.

    Verdicts:
      STASIS             axis constant, content moving
      MOVING             axis changed within the window
      STILL              axis constant AND content constant (loop not running)
      INSUFFICIENT_DATA  fewer than k readings, or unknown axis in window
    """
    if k < 2:
        raise ValueError("k must be >= 2")

    if len(readings) < k:
        return {
            "verdict": "INSUFFICIENT_DATA",
            "consecutive": k,
            "note": "trail has %d readings, need %d" % (len(readings), k),
            "window": [],
        }

    window = readings[-k:]
    sigs = [axis_signature(r) for r in window]

    if any(s is None for s in sigs):
        return {
            "verdict": "INSUFFICIENT_DATA",
            "consecutive": k,
            "note": "axis unknown in window (alpha_direction or inf0p_scope unknown)",
            "window": [ev(r) for r in window],
        }

    axis_constant = len(set(sigs)) == 1
    shas = {r.get("signature_sha", "") for r in window}
    content_moved = len(shas) >= 2

    if axis_constant and content_moved:
        verdict = "STASIS"
    elif axis_constant and not content_moved:
        verdict = "STILL"
    else:
        verdict = "MOVING"

    result = {
        "verdict": verdict,
        "consecutive": k,
        "window": [ev(r) for r in window],
    }
    if axis_constant:
        axis = sigs[0]
        assert axis is not None  # guarded by the unknown-axis check above
        result["axis"] = list(axis)
        result["since"] = window[0].get("timestamp", "")
        result["content_moved"] = content_moved
    return result


def ev(reading: dict) -> dict:
    """Compact window evidence for one reading."""
    return {
        "timestamp": reading.get("timestamp", ""),
        "alpha_direction": reading.get("alpha_direction"),
        "inf0p_scope": reading.get("inf0p_scope"),
        "signature_sha": reading.get("signature_sha", ""),
    }


def load_trail(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path) as f:
        data = json.load(f)
    return data.get("readings", [])


def render(result: dict) -> str:
    v = result["verdict"]
    lines = ["VERDICT: %s" % v]
    lines.append("consecutive: %d" % result["consecutive"])
    if v in ("STASIS", "STILL"):
        lines.append("axis: %s / %s" % tuple(result["axis"]))
        lines.append("since: %s" % result.get("since", ""))
        lines.append("content moved: %s" % ("yes" if result.get("content_moved") else "no"))
    if v == "STASIS":
        lines.append("")
        lines.append("The loop runs, but the axis has stopped turning.")
        lines.append("Propose a search-policy draft ({alpha'}) to H via the")
        lines.append("self-evolution orchestrator. Never auto-inject.")
        lines.append("")
        lines.append("Caveat: only as true as the centrifuge's heuristics")
        lines.append("(alpha_direction / inf0p_scope keyword scores).")
    elif v == "STILL":
        lines.append("")
        lines.append("Nothing turned and nothing moved: the loop has not run.")
    elif v == "INSUFFICIENT_DATA":
        lines.append("note: %s" % result.get("note", ""))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="5QLN axis stasis detector")
    parser.add_argument("command", nargs="?", default="check", choices=["check"])
    parser.add_argument("--consecutive", type=int, default=DEFAULT_K,
                        help="consecutive static readings required (default %d)" % DEFAULT_K)
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--trail", help="override trail path (default: QLN_WIKI resolution)")
    args = parser.parse_args()

    path = args.trail or resolve_trail_path()
    result = detect_stasis(load_trail(path), k=args.consecutive)
    result["trail_path"] = path

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(render(result))


if __name__ == "__main__":
    main()
