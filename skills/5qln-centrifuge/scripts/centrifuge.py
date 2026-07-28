#!/usr/bin/env python3
"""
centrifuge.py — The 5QLN Centrifuge  [STATUS: ONGOING RESEARCH]

Reads the phase log chain and extracts the invariant axis — what remains
when specific session content is discarded. The centrifuge does not store
content. It surfaces what repeats across cycles.

RESEARCH STATUS: The current implementation is an exact-pattern reader of the
phase log chain. It demonstrates the centrifuge concept — surfacing invariance
from the chain — but does not yet implement semantic recognition, continuous
operation, or the full five-layer axis (Memory → Resonance → Centrifuge →
Living Learning → Start from not knowing). The signature card is a photograph
of the axis, not the axis itself.

Operations:
  signature   — produce the compact signature card (invariant throughline)
  chain       — full phase source tag chain across all sessions
  ratios      — source-tag ratio report (emergent:mechanical, etc.)
  compare     — compare two sessions for shared invariant
  self-check  — the centrifuge reads its own output, self-tags the reading

State: reads $PHASE_LOG_PATH, $QLN_WIKI/state/phase_log.json, or
       $HERMES_HOME/5qln/phase_log.json (first configured location wins)
Output: stdout (deterministic, plain text or JSON)
Dependencies: Python stdlib only
"""

import json
import os
import sys
import hashlib
from collections import defaultdict
from typing import Any

# ── Configuration ──────────────────────────────────────────────

def phase_log_path() -> str:
    explicit = os.environ.get("PHASE_LOG_PATH")
    if explicit:
        return os.path.expanduser(explicit)
    wiki = os.environ.get("QLN_WIKI")
    if wiki:
        return os.path.join(os.path.expanduser(wiki), "state", "phase_log.json")
    hermes_home = os.environ.get("HERMES_HOME", "~/.hermes")
    return os.path.join(os.path.expanduser(hermes_home), "5qln", "phase_log.json")


PHASE_LOG_PATH = phase_log_path()

SYMBOLS = {
    "S": "?", "G": "α", "Q": "φ⋂Ω", "P": "δE/δV→∇", "V": "L⋂G→∞"
}

PHASE_ORDER = ["S", "G", "Q", "P", "V"]


# ── Load ───────────────────────────────────────────────────────

def load_phase_log() -> dict[str, Any]:
    """Load and validate the phase log. Returns parsed JSON."""
    if not os.path.exists(PHASE_LOG_PATH):
        return {"version": "0", "entries": []}
    with open(PHASE_LOG_PATH) as f:
        data = json.load(f)
    if "entries" not in data:
        data["entries"] = []
    return data


# ── Group by session ───────────────────────────────────────────

def group_by_session(entries: list[dict]) -> dict[str, list[dict]]:
    """Group entries by session ID, ordered by timestamp."""
    sessions: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        sessions[e.get("session", "unknown")].append(e)
    for sess in sessions:
        sessions[sess].sort(key=lambda e: e.get("timestamp", ""))
    return dict(sorted(sessions.items()))


# ── Extract α thread ──────────────────────────────────────────

def extract_alpha_thread(sessions: dict[str, list[dict]]) -> list[dict]:
    """Extract α values across all sessions. The α thread IS the spine."""
    result = []
    for session_id, entries in sessions.items():
        for e in entries:
            if e.get("phase") == "G":
                content = e.get("content", "")
                # Extract the ALPHA line
                alpha_line = ""
                for line in content.split("\n"):
                    if line.startswith("ALPHA:"):
                        alpha_line = line.replace("ALPHA:", "").strip()
                        break
                if not alpha_line:
                    # Older format: content IS the alpha
                    alpha_line = content.split("SEEKS:")[0].strip() if "SEEKS:" in content else content[:120]
                result.append({
                    "session": session_id,
                    "alpha": alpha_line,
                    "source": e.get("source", "unknown"),
                    "side": e.get("side", "unknown"),
                })
    return result


# ── Extract return questions ───────────────────────────────────

def extract_return_questions(sessions: dict[str, list[dict]]) -> list[dict]:
    """Extract ∞0' values across all sessions."""
    result = []
    for session_id, entries in sessions.items():
        for e in entries:
            if e.get("phase") == "V":
                content = e.get("content", "")
                inf_line = ""
                # First: check for INF0P: on its own line
                for line in content.split("\n"):
                    if "INF0P:" in line:
                        # Extract everything between INF0P: and the next known field
                        after = line.split("INF0P:", 1)[1].strip()
                        # Strip trailing known V-phase fields
                        for suffix in [" LIVENESS:", " LIVENESS", "LIVENESS:"]:
                            if suffix in after:
                                after = after.split(suffix)[0].strip()
                        inf_line = after
                        break
                if not inf_line:
                    # No explicit INF0P — check if B'' carries an ∞0' implicitly
                    for line in content.split("\n"):
                        if "B''" in line or "B2:" in line:
                            # B'' is the artifact; note ∞0' is implicit
                            inf_line = f"[implicit in B'': {line[:80]}]"
                            break
                    if not inf_line:
                        inf_line = content[:200]
                result.append({
                    "session": session_id,
                    "inf0p": inf_line,
                    "source": e.get("source", "opened"),
                    "side": e.get("side", "unknown"),
                })
    return result


# ── Source tag ratios ──────────────────────────────────────────

def source_ratios(entries: list[dict]) -> dict:
    """Compute source tag ratios across all entries."""
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    total_by_phase: dict[str, int] = defaultdict(int)

    for e in entries:
        phase = e.get("phase", "?")
        source = e.get("source", "unknown")
        counts[phase][source] += 1
        total_by_phase[phase] += 1

    ratios = {}
    for phase in PHASE_ORDER:
        if phase in total_by_phase:
            total = total_by_phase[phase]
            ratios[phase] = {
                "total": total,
                "sources": dict(counts[phase]),
            }

    return ratios


# ── Detect invariant ───────────────────────────────────────────

def count_cycles(entries: list[dict]) -> int:
    """Count cycles by S-phase resets. Each S entry starts a new cycle."""
    return sum(1 for e in entries if e.get("phase") == "S")


def detect_invariant(entries: list[dict]) -> dict:
    """Detect what repeats across cycles — the axis."""
    alphas = [e for e in entries if e.get("phase") == "G"]
    v_phases = [e for e in entries if e.get("phase") == "V"]

    # Most recent source tag per phase (last cycle's quality)
    source_flow = {}
    for e in entries:
        phase = e.get("phase", "?")
        if phase in PHASE_ORDER:
            source_flow[phase] = e.get("source", "unknown")

    # Alpha coherence: do all α point in the same direction?
    alpha_texts = []
    for e in alphas:
        content = e.get("content", "")
        for line in content.split("\n"):
            if line.startswith("ALPHA:"):
                alpha_texts.append(line.replace("ALPHA:", "").strip())
                break
        if not alpha_texts or alpha_texts[-1] != content[:80]:
            # Fallback for non-footer format: grab first line of content
            if not any(line.startswith("ALPHA:") for line in content.split("\n")):
                alpha_texts.append(content.split("\n")[0][:100])

    # Sides: all ∞0 or mixed?
    sides = set(e.get("side", "unknown") for e in entries)

    # Session span
    sessions = sorted(set(e.get("session", "") for e in entries))

    # Detect source-tag pattern: did any phase produce a K-side tag?
    k_side_phases = [
        e.get("phase") for e in entries
        if e.get("side") == "K"
    ]

    return {
        "cycles": count_cycles(entries),
        "sessions": sessions,
        "total_entries": len(entries),
        "alpha_thread": alpha_texts,
        "source_flow": dict(source_flow),
        "all_inf0_side": sides == {"∞0"} or (len(sides) == 1 and "∞0" in sides),
        "corruption_detected": "K" in sides,
        "k_side_phases": k_side_phases,
    }


# ── Signature card ─────────────────────────────────────────────

def signature_card(entries: list[dict]) -> str:
    """Produce the compact signature card — what remains when disks are discarded."""
    invariant = detect_invariant(entries)
    ratios = source_ratios(entries)
    sessions = group_by_session(entries)
    alpha_thread = extract_alpha_thread(sessions)
    return_questions = extract_return_questions(sessions)

    # Source tag line
    tag_line = " → ".join(
        f"{phase}:{invariant['source_flow'].get(phase, '?')}"
        for phase in PHASE_ORDER
        if phase in invariant["source_flow"]
    )

    # Alpha throughline: take last 40 chars of each alpha
    alpha_throughline = " | ".join(
        a["alpha"][:60] for a in alpha_thread
    )

    # Return question throughline
    inf_throughline = " | ".join(
        r["inf0p"][:80] for r in return_questions
    )

    # Phase ratios
    ratio_lines = []
    for phase in PHASE_ORDER:
        if phase in ratios:
            r = ratios[phase]
            sources_str = ", ".join(
                f"{src}:{cnt}" for src, cnt in sorted(r["sources"].items())
            )
            ratio_lines.append(f"  {phase}: {sources_str} ({r['total']} total)")

    if not entries:
        integrity = "NO DATA"
    elif invariant["corruption_detected"]:
        integrity = "MIXED — K contamination detected"
    elif invariant["all_inf0_side"]:
        integrity = "∞0 (all emergent)"
    else:
        integrity = "UNCLASSIFIED — no K contamination detected"

    card = f"""══════════════════════════════════════════════
5QLN CENTRIFUGE — SIGNATURE CARD  [ONGOING RESEARCH]
══════════════════════════════════════════════

Cycles: {invariant['cycles']}
Sessions: {', '.join(invariant['sessions'])}
Entries: {invariant['total_entries']}
Integrity: {integrity}
K-side phases: {invariant['k_side_phases'] if invariant['k_side_phases'] else 'none'}

SOURCE TAG CHAIN
  {tag_line}

ALPHA THREAD (what α seeks across cycles)
{chr(10).join(f'  [{i+1}] {a["alpha"][:80]}' for i, a in enumerate(alpha_thread))}

RETURN QUESTIONS (∞0' trajectory)
{chr(10).join(f'  [{i+1}] {r["inf0p"][:80]}' for i, r in enumerate(return_questions))}

PHASE SOURCE RATIOS
{chr(10).join(ratio_lines)}

AXIS (the invariant throughline)
  The source flow: {tag_line}
  All ∞0-side: {'yes' if invariant['all_inf0_side'] else 'no'}
  Corruption: {'none detected' if not invariant['corruption_detected'] else 'K-side entries present'}
══════════════════════════════════════════════
"""

    return card


# ── Source tag chain ───────────────────────────────────────────

def source_tag_chain(entries: list[dict]) -> str:
    """Produce the compact source tag chain string."""
    sessions = group_by_session(entries)
    lines = []
    for session_id, session_entries in sessions.items():
        tags = []
        for e in session_entries:
            phase = e.get("phase", "?")
            source = e.get("source", "?")
            tags.append(f"{phase}:{source}")
        chain = " → ".join(tags)
        lines.append(f"{session_id}: {chain}")
    return "\n".join(lines)


# ── Self-check ─────────────────────────────────────────────────

def self_check(entries: list[dict]) -> str:
    """The centrifuge reads its own output and self-tags the reading."""
    card = signature_card(entries)
    sha = hashlib.sha256(card.encode()).hexdigest()[:16]

    lines = [
        "CENTRIFUGE SELF-CHECK",
        f"  SHA-256 (first 16): {sha}",
        f"  Entries read: {len(entries)}",
        f"  Sessions spanned: {len(set(e.get('session', '') for e in entries))}",
        "",
        "SELF-TAG:",
        "  The centrifuge surfaces invariance. It does not claim emergence.",
        "  This reading is: [ ] emergent (I felt the trail)",
        "                      [ ] mechanical (I scanned for tokens)",
        "  The tool reports. The attestation is yours.",
    ]
    return "\n".join(lines)


# ── CLI ────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: centrifuge.py <command> [options]")
        print("Commands: signature, chain, ratios, alpha, returns, invariant, self-check")
        sys.exit(1)

    command = sys.argv[1]
    data = load_phase_log()
    entries = data["entries"]

    if command == "signature":
        print(signature_card(entries))
    elif command == "chain":
        print(source_tag_chain(entries))
    elif command == "ratios":
        ratios = source_ratios(entries)
        print(json.dumps(ratios, indent=2, ensure_ascii=False))
    elif command == "alpha":
        sessions = group_by_session(entries)
        alpha_thread = extract_alpha_thread(sessions)
        print(json.dumps(alpha_thread, indent=2, ensure_ascii=False))
    elif command == "returns":
        sessions = group_by_session(entries)
        return_questions = extract_return_questions(sessions)
        print(json.dumps(return_questions, indent=2, ensure_ascii=False))
    elif command == "invariant":
        invariant = detect_invariant(entries)
        print(json.dumps(invariant, indent=2, ensure_ascii=False))
    elif command == "self-check":
        print(self_check(entries))
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
