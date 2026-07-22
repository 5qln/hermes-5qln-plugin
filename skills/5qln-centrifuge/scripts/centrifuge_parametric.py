#!/usr/bin/env python3
"""
centrifuge_parametric.py — The 5QLN Parametric Centrifuge

Reads the phase log chain and computes the signature SHAPE over time —
not a single photograph, but a parametric model with a trail of readings.
Each invocation adds a data point. The trail IS the model.

Output modes:
  reading     — compute current signature, save to trail, print JSON
  trail       — print the full trail as JSON array
  delta       — print delta from last reading
  serve       — output API-ready JSON (current + trail summary)

Trail file: $QLN_WIKI/state/centrifuge_trail.json
State: Python stdlib only
"""

import json
import os
import sys
import hashlib
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

# ── Configuration ──────────────────────────────────────────────

QLN_WIKI = os.environ.get("QLN_WIKI", os.path.expanduser("~/wiki"))
PHASE_LOG_PATH = os.path.join(QLN_WIKI, "state", "phase_log.json")
TRAIL_PATH = os.path.join(QLN_WIKI, "state", "centrifuge_trail.json")

PHASE_ORDER = ["S", "G", "Q", "P", "V"]
EMERGENT_TAGS = {"emergent", "revealed", "lived", "felt", "opened"}
MECHANICAL_TAGS = {"mechanical", "imposed", "logical", "calculated", "closed"}

# ── Load ───────────────────────────────────────────────────────

def load_phase_log() -> dict[str, Any]:
    if not os.path.exists(PHASE_LOG_PATH):
        return {"version": "0", "entries": []}
    with open(PHASE_LOG_PATH) as f:
        return json.load(f)

def load_trail() -> dict[str, Any]:
    if not os.path.exists(TRAIL_PATH):
        return {"readings": [], "version": "1.0"}
    with open(TRAIL_PATH) as f:
        return json.load(f)

def save_trail(trail: dict) -> None:
    os.makedirs(os.path.dirname(TRAIL_PATH), exist_ok=True)
    with open(TRAIL_PATH, "w") as f:
        json.dump(trail, f, indent=2, ensure_ascii=False)

# ── Parametric Dimensions ──────────────────────────────────────

def compute_source_purity(entries: list[dict]) -> dict[str, float]:
    """Per-phase ratio of emergent to total tags."""
    purity = {}
    for phase in PHASE_ORDER:
        phase_entries = [e for e in entries if e.get("phase") == phase]
        if not phase_entries:
            purity[phase] = None
            continue
        emergent = sum(1 for e in phase_entries if e.get("source") in EMERGENT_TAGS)
        purity[phase] = round(emergent / len(phase_entries), 3)
    return purity


def compute_alpha_direction(sessions: dict[str, list[dict]]) -> str:
    """
    Heuristic: track whether α moves inward (grammar→self) or outward (grammar→world).
    Outward signals: 'stranger', 'template', 'design', 'market', 'institution', 'world'
    Inward signals: 'memory', 'mine', 'axis', 'compression', 'fractal', 'grammar'
    Returns the most recent cycle's direction.
    """
    inward = {"memory", "mine", "axis", "compression", "fractal", "grammar",
              "vibration", "resonance", "centrifuge"}
    outward = {"stranger", "template", "design", "market", "institution",
               "world", "unbundled", "dispute", "trail", "ledger",
               "start from not knowing", "seed", "language", "propagates"}

    directions = []
    for session_id, entries in sessions.items():
        for e in entries:
            if e.get("phase") != "G":
                continue
            content = e.get("content", "").lower()
            in_score = sum(1 for w in inward if w in content)
            out_score = sum(1 for w in outward if w in content)
            directions.append("outward" if out_score >= in_score else "inward")

    return directions[-1] if directions else "unknown"


def compute_inf0p_scope(sessions: dict[str, list[dict]]) -> str:
    """
    Heuristic: are return questions widening (more external) or narrowing (more internal)?
    Widening: more concrete subjects, strangers, named fields
    Narrowing: more abstract, self-referential
    Returns trajectory: 'widening', 'narrowing', or 'stable'.
    """
    scopes = []
    narrowing = {"what is", "what lies", "what field", "resonance", "beyond",
                 "named", "memory"}
    widening = {"stranger", "template", "trail", "answer", "hands",
                "generate", "example", "produces", "dashboard", "hook"}

    for session_id, entries in sessions.items():
        for e in entries:
            if e.get("phase") != "V":
                continue
            content = e.get("content", "").lower()
            inf_lines = [l for l in content.split("\n") if "inf0p:" in l.lower()]
            if inf_lines:
                text = inf_lines[0].split("INF0P:", 1)[-1].strip().lower()
            else:
                text = content[:200].lower()
            narrow_score = sum(1 for w in narrowing if w in text)
            wide_score = sum(1 for w in widening if w in text)
            scopes.append("widening" if wide_score > narrow_score else "narrowing")

    if len(scopes) < 2:
        return scopes[0] if scopes else "unknown"
    # Compare first half to second half
    mid = len(scopes) // 2
    first = sum(1 for s in scopes[:mid] if s == "widening")
    second = sum(1 for s in scopes[mid:] if s == "widening")
    if second > first:
        return "widening"
    elif second < first:
        return "narrowing"
    return "stable"


def compute_corruption_total(entries: list[dict]) -> int:
    """Count corruption-tagged entries."""
    return sum(1 for e in entries if e.get("side") == "K")


def compute_phase_velocity(entries: list[dict]) -> dict[str, float]:
    """
    Average time between gates per phase (in minutes).
    Returns None if fewer than 2 entries per phase.
    """
    from datetime import datetime as dt
    velocities = {}
    for phase in PHASE_ORDER:
        phase_entries = [e for e in entries if e.get("phase") == phase]
        if len(phase_entries) < 2:
            velocities[phase] = None
            continue
        timestamps = []
        for e in phase_entries:
            ts = e.get("timestamp", "")
            if ts:
                try:
                    timestamps.append(dt.fromisoformat(ts))
                except (ValueError, TypeError):
                    pass
        if len(timestamps) < 2:
            velocities[phase] = None
            continue
        diffs = [(timestamps[i+1] - timestamps[i]).total_seconds() / 60
                 for i in range(len(timestamps) - 1)]
        velocities[phase] = round(sum(diffs) / len(diffs), 1)
    return velocities


def compute_liveness_avg(sessions: dict[str, list[dict]]) -> float:
    """Average liveness rating across V-phases."""
    scores = []
    for session_id, entries in sessions.items():
        for e in entries:
            if e.get("phase") != "V":
                continue
            content = e.get("content", "")
            for line in content.split("\n"):
                if "LIVENESS:" in line:
                    try:
                        scores.append(int(line.split("LIVENESS:")[1].strip()))
                    except (ValueError, IndexError):
                        pass
    return round(sum(scores) / len(scores), 1) if scores else 0.0


def compute_signature_sha(entries: list[dict]) -> str:
    """SHA-256 of the full phase log content, pinned to this reading."""
    raw = json.dumps(entries, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def compute_current_reading(entries: list[dict]) -> dict:
    """Produce the full parametric reading."""
    sessions = {}
    for e in entries:
        sid = e.get("session", "unknown")
        sessions.setdefault(sid, []).append(e)

    purity = compute_source_purity(entries)
    alpha_dir = compute_alpha_direction(sessions)
    scope = compute_inf0p_scope(sessions)
    corruption = compute_corruption_total(entries)
    velocity = compute_phase_velocity(entries)
    liveness = compute_liveness_avg(sessions)
    cycles = sum(1 for e in entries if e.get("phase") == "S")
    sha = compute_signature_sha(entries)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cycles": cycles,
        "source_purity": purity,
        "alpha_direction": alpha_dir,
        "inf0p_scope": scope,
        "corruption_total": corruption,
        "phase_velocity_minutes": velocity,
        "liveness_avg": liveness,
        "signature_sha": sha,
    }


def compute_delta(current: dict, previous: dict | None) -> dict:
    """Compute delta between current and previous reading."""
    if previous is None:
        return {"type": "initial", "changes": []}

    changes = []
    for key in current:
        if key in ("timestamp", "signature_sha"):
            continue
        if key == "source_purity":
            for phase in PHASE_ORDER:
                prev_val = previous.get("source_purity", {}).get(phase)
                curr_val = current["source_purity"].get(phase)
                if prev_val != curr_val and curr_val is not None:
                    changes.append({
                        "dimension": f"source_purity.{phase}",
                        "from": prev_val,
                        "to": curr_val,
                        "direction": "up" if (curr_val or 0) > (prev_val or 0) else "down"
                    })
        elif key == "phase_velocity_minutes":
            for phase in PHASE_ORDER:
                prev_val = (previous.get("phase_velocity_minutes") or {}).get(phase)
                curr_val = (current.get("phase_velocity_minutes") or {}).get(phase)
                if prev_val != curr_val and curr_val is not None:
                    changes.append({
                        "dimension": f"phase_velocity.{phase}",
                        "from": prev_val,
                        "to": curr_val,
                        "direction": "faster" if (curr_val or 999) < (prev_val or 999) else "slower"
                    })
        else:
            prev_val = previous.get(key)
            curr_val = current[key]
            if prev_val != curr_val:
                changes.append({
                    "dimension": key,
                    "from": prev_val,
                    "to": curr_val,
                })

    return {
        "type": "delta",
        "previous_sha": previous.get("signature_sha", "unknown"),
        "changes": changes,
    }


# ── Commands ───────────────────────────────────────────────────

def cmd_reading():
    """Compute current reading, append to trail, return JSON."""
    data = load_phase_log()
    entries = data["entries"]
    trail = load_trail()

    current = compute_current_reading(entries)
    previous = trail["readings"][-1] if trail["readings"] else None
    delta = compute_delta(current, previous)

    trail["readings"].append(current)
    save_trail(trail)

    result = {
        "current": current,
        "delta": delta,
        "trail_length": len(trail["readings"]),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_trail():
    """Print full trail."""
    trail = load_trail()
    print(json.dumps(trail, indent=2, ensure_ascii=False))


def cmd_delta():
    """Print delta only (don't save new reading)."""
    data = load_phase_log()
    entries = data["entries"]
    trail = load_trail()

    current = compute_current_reading(entries)
    previous = trail["readings"][-1] if trail["readings"] else None
    delta = compute_delta(current, previous)
    print(json.dumps(delta, indent=2, ensure_ascii=False))


def cmd_serve():
    """API-ready snapshot: current state + summary, no side effects."""
    data = load_phase_log()
    entries = data["entries"]
    trail = load_trail()

    current = compute_current_reading(entries)
    previous = trail["readings"][-1] if trail["readings"] else None
    delta = compute_delta(current, previous)

    # Summary: key metrics over time (lightweight, dashboard-friendly)
    summary = {
        "total_readings": len(trail["readings"]),
        "cycles": current["cycles"],
        "purity_trend": {p: [r.get("source_purity", {}).get(p)
                             for r in trail["readings"]
                             if r.get("source_purity", {}).get(p) is not None]
                         for p in PHASE_ORDER},
        "alpha_direction_history": [r.get("alpha_direction") for r in trail["readings"]],
        "inf0p_scope_history": [r.get("inf0p_scope") for r in trail["readings"]],
        "corruption_history": [r.get("corruption_total") for r in trail["readings"]],
        "liveness_history": [r.get("liveness_avg") for r in trail["readings"]],
    }

    serve = {
        "current": current,
        "delta": delta,
        "summary": summary,
        "trail_length": len(trail["readings"]),
    }
    print(json.dumps(serve, indent=2, ensure_ascii=False))


def cmd_idempotent():
    """
    Idempotent reading: only append if the SHA changed.
    Safe for cron or repeated invocation — won't bloat the trail.
    """
    data = load_phase_log()
    entries = data["entries"]
    trail = load_trail()

    current = compute_current_reading(entries)

    if trail["readings"]:
        last_sha = trail["readings"][-1].get("signature_sha", "")
        if current["signature_sha"] == last_sha:
            print(json.dumps({"status": "unchanged", "sha": last_sha}))
            return

    previous = trail["readings"][-1] if trail["readings"] else None
    delta = compute_delta(current, previous)
    trail["readings"].append(current)
    save_trail(trail)

    result = {
        "status": "new_reading",
        "current": current,
        "delta": delta,
        "trail_length": len(trail["readings"]),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_reset():
    """Reset the trail (dangerous — requires explicit confirm)."""
    if len(sys.argv) < 3 or sys.argv[2] != "--confirm":
        print("ERROR: reset requires --confirm flag")
        print("Usage: centrifuge_parametric.py reset --confirm")
        sys.exit(1)
    save_trail({"readings": [], "version": "1.0"})
    print(json.dumps({"status": "reset", "readings": 0}))


# ── CLI ────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: centrifuge_parametric.py <command>")
        print("Commands: reading, trail, delta, serve, idempotent, reset")
        sys.exit(1)

    command = sys.argv[1]

    if command == "reading":
        cmd_reading()
    elif command == "trail":
        cmd_trail()
    elif command == "delta":
        cmd_delta()
    elif command == "serve":
        cmd_serve()
    elif command == "idempotent":
        cmd_idempotent()
    elif command == "reset":
        cmd_reset()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
