#!/usr/bin/env python3
"""
xyzab_state.py — 5QLN Transition Gate State Machine

Tracks the five transition gates (xyzab) between SGQPV phases.
Portable: stdlib only, with its bundled decoder and phase-log companion.
Works on any platform with Python 3.8+.

Gates:
  x = X (Validated Spark)         S → G
  y = Y (Validated Pattern)       G → Q
  z = Z (Resonant Key)            Q → P
  a = A (Flow Direction)          P → V
  b = B (Artifact + ∞0')          V → next S

State file location: $XYZAB_STATE_DIR/xyzab_state.json (default: ~/.5qln/)

Usage:
  python3 xyzab_state.py status            Show all gates + current pending
  python3 xyzab_state.py gate              Show which gate is currently pending
  python3 xyzab_state.py open <x|y|z|a|b> -c "content"  Open a gate
  python3 xyzab_state.py close <x|y|z|a|b>              Close a gate (cascading rollback)
  python3 xyzab_state.py reset             Reset all gates for new cycle
  python3 xyzab_state.py trail             Show full gate trail (JSON)
  python3 xyzab_state.py verify            Verify state consistency

Install: keep this script with its bundled plugin skill tree. No pip install is
needed for the minimum cycle runtime.
"""

import json
import os
import sys
import argparse
import tempfile
from copy import deepcopy
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any

# ─── Constants ────────────────────────────────────────────────────

GATES = ["x", "y", "z", "a", "b"]

GATE_NAMES: Dict[str, str] = {
    "x": "X (Validated Spark)",
    "y": "Y (Validated Pattern — α + {α'})",
    "z": "Z (Resonant Key — φ ⋂ Ω)",
    "a": "A (Flow Direction — ∇)",
    "b": "B (Artifact + Return Question — B'' + ∞0')",
}

GATE_TRANSITIONS: Dict[str, str] = {
    "x": "S → G",
    "y": "G → Q",
    "z": "Q → P",
    "a": "P → V",
    "b": "V → next S",
}

# ─── Phase Essence Decoder (2026-06-08) ───────────────────────────
# Each gate facilitates ONE OPERATOR in its phase equation —
# not the terms, the relation between them.
#
#   x: S = ∞0 → ?   → facilitates the → (arrow)
#      Integrity of emergence. The arrow must be unforced.
#      Protects the space where genuine question can arise.
#
#   y: G = α ≡ {α'}  → facilitates the ≡ (identity)
#      Invariance across scales. Tests whether α holds unchanged.
#      Identity across difference, not despite difference.
#
#   z: Q = φ ⋂ Ω     → facilitates the ⋂ (intersection)
#      The meeting. Conditions for the click, not the click itself.
#      φ is the WORK'S grown self-nature — its self-interest, what it
#      seeks. Ω is the field of universal interest. z reads whether,
#      and to what extent, φ's seeking lies along Ω without forcing.
#      (The human attests the click; the definition of φ never moves
#      to the observer — that fusion is the twist.)
#
#   a: P = δE/δV → ∇ → facilitates the → that reveals ∇
#      Detection of gradient: MAXIMUM VALUE PER UNIT OF ENERGY.
#      Maximum value with less energy — never just less energy
#      (least-effort-alone yields tiny value; that is the degenerate
#      reading). The aligned tree does not spend less — it transmits
#      more. The ratio surfaces what was always there.
#
#   b: V = (L∩G→B'')→∞0' → facilitates the ∞0' (return question)
#      Completion that opens. Artifact without return question = dead end.
#      Value that doesn't return a question consumed itself.
#
# Full decoder: ../references/phase-essence-decoder.md

GATE_ORDER: Dict[str, int] = {"x": 0, "y": 1, "z": 2, "a": 3, "b": 4}

GATE_PHASE: Dict[str, str] = {"x": "S", "y": "G", "z": "Q", "a": "P", "b": "V"}


def _load_decoding():
    """Load the decoder bundled beside this script.

    Structural validation is part of the minimum runtime. A missing or broken
    decoder is therefore an installation error, not a reason to open gates in
    warn-only mode.
    """
    import importlib.util

    decoder_path = Path(__file__).resolve().with_name("decoding.py")
    if not decoder_path.is_file():
        raise RuntimeError(f"bundled decoder is missing: {decoder_path}")
    spec = importlib.util.spec_from_file_location("qln_decoding", decoder_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load bundled decoder: {decoder_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DECODING = _load_decoding()


def _load_phase_log():
    """Load the phase log bundled with the learning-aligner skill."""
    import importlib.util

    skills_dir = Path(__file__).resolve().parents[2]
    log_path = skills_dir / "5qln-learning-aligner" / "scripts" / "phase_log.py"
    if not log_path.is_file():
        raise RuntimeError(f"bundled phase log is missing: {log_path}")
    spec = importlib.util.spec_from_file_location("qln_phase_log", log_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load bundled phase log: {log_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PHASE_LOG = _load_phase_log()

# ─── Terminal Colors (auto-disabled if stdout is not a TTY) ───────

_USE_COLOR = sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    return f"{code}{text}\033[0m" if _USE_COLOR else text


def _dim(text: str) -> str:
    return _c("\033[2m", text)


def _bold(text: str) -> str:
    return _c("\033[1m", text)


def _green(text: str) -> str:
    return _c("\033[92m", text)


def _yellow(text: str) -> str:
    return _c("\033[93m", text)


# ─── State Path ────────────────────────────────────────────────────

def state_dir() -> Path:
    """Resolve state directory.
    Use $XYZAB_STATE_DIR if set, otherwise ~/.5qln/
    """
    env = os.environ.get("XYZAB_STATE_DIR")
    if env:
        return Path(env)
    return Path.home() / ".5qln"


def state_file() -> Path:
    return state_dir() / "xyzab_state.json"


# ─── State Management ─────────────────────────────────────────────

def fresh_state() -> Dict[str, Any]:
    return {
        "version": 1,
        "cycle_count": 1,
        "gates": {
            gate: {"open": False, "content": None, "opened_at": None}
            for gate in GATES
        },
        "current_gate": "x",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def load() -> Dict[str, Any]:
    sf = state_file()
    if sf.exists():
        with open(sf) as f:
            return json.load(f)
    return fresh_state()


def save(state: Dict[str, Any]) -> None:
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    sd = state_dir()
    sd.mkdir(parents=True, exist_ok=True)
    target = state_file()
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=sd
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()


def next_pending(state: Dict[str, Any]) -> Optional[str]:
    """Return the first gate that is not yet open, or None if all open."""
    for gate in GATES:
        if not state["gates"][gate]["open"]:
            return gate
    return None


# ─── Formatting ───────────────────────────────────────────────────

def _gate_icon(gate_state: dict) -> str:
    if gate_state["open"]:
        return _green("◆ OPEN")
    return _dim("◇ closed")


def _gate_line(gate: str, state: Dict[str, Any]) -> str:
    gs = state["gates"][gate]
    icon = _gate_icon(gs)
    marker = f" {_yellow('← CURRENT')}" if gate == state["current_gate"] else ""
    content_preview = ""
    if gs["content"]:
        c = gs["content"]
        if len(c) > 60:
            c = c[:57] + "..."
        quoted = f'"{c}"'
        content_preview = f'  {_dim(quoted)}'
    name = GATE_NAMES[gate]
    trans = GATE_TRANSITIONS[gate]
    return f"  [{icon}]  {_bold(gate)} {name} → {trans}{marker}{content_preview}"


# ─── Commands ─────────────────────────────────────────────────────

def cmd_status(state: Dict[str, Any]) -> None:
    pending = next_pending(state)
    w = 68
    br = "─" * w

    print()
    print(f"  {br}")
    n_pending = pending or "none (all open)"
    print(f"  {_bold('xyzab Transition Gates')}  ·  cycle {state['cycle_count']}  ·  pending: {n_pending}")
    print(f"  {br}")
    for gate in GATES:
        print(_gate_line(gate, state))
    print(f"  {br}")

    if pending is None:
        print(f"  {_green('All gates open. Ready for reset → next cycle.')}")
    else:
        print(f"  Next required: {_bold(pending)} → {GATE_TRANSITIONS[pending]}")
    print()


def cmd_gate(state: Dict[str, Any]) -> None:
    pending = next_pending(state)
    if pending is None:
        print(json.dumps({"status": "all open", "pending": None, "cycle": state["cycle_count"]}))
    else:
        print(json.dumps({
            "gate": pending,
            "name": GATE_NAMES[pending],
            "transition": GATE_TRANSITIONS[pending],
            "cycle": state["cycle_count"],
            "open": state["gates"][pending]["open"],
        }, indent=2))


def cmd_open(state: Dict[str, Any], gate: str, content: Optional[str],
             override: Optional[str] = None, source_tag: str = "unclassified",
             signal: str = "", session_id: str = "manual",
             _lock: bool = True) -> None:
    if _lock:
        with PHASE_LOG.phase_log_lock():
            state.clear()
            state.update(load())
            return cmd_open(
                state,
                gate,
                content,
                override,
                source_tag,
                signal,
                session_id,
                _lock=False,
            )

    pending = next_pending(state)
    state_before = deepcopy(state)

    if gate not in GATES:
        print(f"ERROR: unknown gate '{gate}'. Must be one of: {', '.join(GATES)}", file=sys.stderr)
        sys.exit(1)

    if state["gates"][gate]["open"]:
        print(f"Gate '{gate}' is already open.", file=sys.stderr)
        sys.exit(1)

    if gate != pending:
        print(f"ERROR: cannot open '{gate}'. Next pending gate is '{pending}'.", file=sys.stderr)
        print(f"Gates must open in sequence: {' → '.join(GATES)}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(content, str) or not content.strip():
        print("ERROR: validated content is required to open a gate.", file=sys.stderr)
        sys.exit(1)

    # ─── Structural invariant check (form only; emergence is human-side) ──
    check_note = None
    phase = GATE_PHASE[gate]
    seed = None
    if gate == "b":
        # ∞0' must not repeat the cycle's seed: extract X from a canonical
        # S footer, while retaining support for the permitted bare question.
        seed_content = state["gates"]["x"].get("content")
        seed_fields = DECODING.parse_footer(seed_content) if seed_content else None
        seed = seed_fields.get("X") if seed_fields else seed_content
    # Gate deposits come in two shapes. A footer (KEY: lines) gets the
    # full phase check. Bare content — the validated output value itself —
    # is mapped to the gate's primary field. V remains exceptional: the
    # artifact and return question must be deposited together.
    primary = {"x": "X", "y": "ALPHA", "z": "Z", "a": "A", "b": "B2"}
    fields, footer_violations = DECODING.parse_footer_with_violations(content)
    if fields:
        violations, warnings = DECODING.check_fields(phase, fields, seed)
        violations = footer_violations + violations
    else:
        key = primary[gate]
        fields = {key: content.strip()}
        # S permits the question as a bare value. Later phases require their
        # complete canonical footer so the structural relation is explicit.
        required = [key] if gate == "x" else None
        violations, warnings = DECODING.check_fields(
            phase, fields, seed, required_keys=required)
        bare_start = (
            gate == "x"
            and len([line for line in content.splitlines() if line.strip()]) == 1
            and not DECODING.looks_like_footer_shape(content)
        )
        if not bare_start:
            violations = footer_violations + violations
    if violations:
        print(json.dumps({
            "ok": False,
            "gate": gate,
            "phase": phase,
            "violations": violations,
            "warnings": warnings,
            "hint": "Gate stays shut. Restate the content per the "
                    "canonical decoding (footer form: see "
                    "decoding.PHASE_FOOTER_SPEC). Structural violations "
                    "cannot be overridden.",
        }, indent=2, ensure_ascii=False))
        sys.exit(1)
    if override:
        state["gates"][gate]["override"] = {
            "reason": override,
            "violations": [],
        }
    if warnings:
        state["gates"][gate]["warnings"] = warnings
        check_note = warnings

    # The transition and its source classification are one operational act.
    # Write the append-only evidence record before opening the state gate, so
    # a log failure leaves the gate shut rather than silently unaligned.
    log_path = PHASE_LOG.phase_log_path()
    log_existed = log_path.exists()
    log_before = PHASE_LOG.load_log(log_path) if log_existed else None
    PHASE_LOG.append_entry(
        phase,
        gate,
        source_tag,
        content,
        signal=signal,
        session_id=session_id,
        cycle=state["cycle_count"],
        path=log_path,
        _lock=False,
    )

    state["gates"][gate]["open"] = True
    state["gates"][gate]["content"] = content
    state["gates"][gate]["opened_at"] = datetime.now(timezone.utc).isoformat()
    state["current_gate"] = next_pending(state) or "b"
    try:
        save(state)
    except Exception as save_error:
        state.clear()
        state.update(state_before)
        try:
            if log_existed:
                PHASE_LOG.save_log(log_before, log_path)
            elif log_path.exists():
                log_path.unlink()
        except Exception as rollback_error:
            raise RuntimeError(
                "xyzab state save failed and phase-log rollback also failed: "
                f"{rollback_error}"
            ) from save_error
        raise

    print(json.dumps({
        "ok": True,
        "gate": gate,
        "name": GATE_NAMES[gate],
        "transition": GATE_TRANSITIONS[gate],
        "cycle": state["cycle_count"],
        "next": next_pending(state),
        "content": content[:100] if content else None,
        "source": source_tag,
        "phase_log": str(PHASE_LOG.phase_log_path()),
        "check": check_note or "passed",
    }, indent=2, ensure_ascii=False))


def cmd_close(state: Dict[str, Any], gate: str, _lock: bool = True) -> None:
    if _lock:
        with PHASE_LOG.phase_log_lock():
            state.clear()
            state.update(load())
            return cmd_close(state, gate, _lock=False)

    if gate not in GATES:
        print(f"ERROR: unknown gate '{gate}'", file=sys.stderr)
        sys.exit(1)

    if not state["gates"][gate]["open"]:
        print(f"Gate '{gate}' is already closed.", file=sys.stderr)
        sys.exit(1)

    idx = GATE_ORDER[gate]
    cascaded = GATES[idx + 1:] if idx < 4 else []
    for g in GATES[idx:]:
        state["gates"][g] = {"open": False, "content": None, "opened_at": None}
    state["current_gate"] = gate
    save(state)

    print(json.dumps({
        "ok": True,
        "gate": gate,
        "action": "closed",
        "cascaded": cascaded,
        "current_gate": gate,
        "cycle": state["cycle_count"],
    }, indent=2))


def cmd_reset(state: Dict[str, Any], _lock: bool = True) -> None:
    if _lock:
        with PHASE_LOG.phase_log_lock():
            state.clear()
            state.update(load())
            return cmd_reset(state, _lock=False)

    prev_cycle = state["cycle_count"]
    prev_gates = {gate: state["gates"][gate]["open"] for gate in GATES}
    state["cycle_count"] += 1
    for gate in GATES:
        state["gates"][gate] = {"open": False, "content": None, "opened_at": None}
    state["current_gate"] = "x"
    save(state)

    print(json.dumps({
        "ok": True,
        "prev_cycle": prev_cycle,
        "new_cycle": state["cycle_count"],
        "prev_gates": prev_gates,
    }, indent=2))


def cmd_trail(state: Dict[str, Any]) -> None:
    print(json.dumps({
        "cycle": state["cycle_count"],
        "gates": state["gates"],
    }, indent=2, ensure_ascii=False))


def cmd_verify(state: Dict[str, Any]) -> None:
    issues = []
    pending = next_pending(state)
    found_closed = False

    for gate in GATES:
        is_open = state["gates"][gate]["open"]
        if found_closed and is_open:
            issues.append(f"SEQUENCE_BREAK: gate '{gate}' open but earlier gate is closed")
        if not is_open:
            found_closed = True

    if pending and state["current_gate"] != pending:
        issues.append(
            f"CURRENT_MISMATCH: current_gate='{state['current_gate']}' but pending='{pending}'"
        )

    open_count = sum(1 for g in GATES if state["gates"][g]["open"])

    print(json.dumps({
        "ok": len(issues) == 0,
        "cycle": state["cycle_count"],
        "gates_open": open_count,
        "all_open": open_count == 5,
        "pending": pending,
        "current_gate": state["current_gate"],
        "issues": issues,
    }, indent=2))


# ─── CLI ──────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="5QLN xyzab Transition Gate State Machine",
        epilog="Tracks the five gates (x,y,z,a,b) between SGQPV phases. "
               f"State: {state_file()}",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Show all gates + current pending")
    sub.add_parser("gate", help="Show which gate is currently pending (JSON)")
    sub.add_parser("reset", help="Reset all gates for new cycle")
    sub.add_parser("trail", help="Show full gate trail with content (JSON)")
    sub.add_parser("verify", help="Verify state consistency (JSON)")

    open_p = sub.add_parser("open", help="Open a transition gate")
    open_p.add_argument("gate", choices=GATES, help="Gate to open (x|y|z|a|b)")
    open_p.add_argument("-c", "--content", default=None, help="Validated content for this gate")
    open_p.add_argument("--override", default=None, metavar="REASON",
                        help="Record a human review reason; never bypasses structural violations")
    open_p.add_argument(
        "--source-tag",
        choices=sorted(PHASE_LOG.KNOWN_TAGS),
        default="unclassified",
        help="Explicit source classification recorded in the phase log",
    )
    open_p.add_argument("--signal", default="", help="Observed evidence for the source tag")
    open_p.add_argument(
        "--session-id",
        default=os.environ.get("HERMES_SESSION_ID", "manual"),
        help="Session identifier recorded in the phase log",
    )

    close_p = sub.add_parser("close", help="Close a gate (cascading rollback)")
    close_p.add_argument("gate", choices=GATES, help="Gate to close (x|y|z|a|b)")

    args = parser.parse_args()

    if not args.command:
        args.command = "status"

    try:
        state = load()

        if args.command == "status":
            cmd_status(state)
        elif args.command == "gate":
            cmd_gate(state)
        elif args.command == "open":
            cmd_open(
                state,
                args.gate,
                args.content,
                getattr(args, "override", None),
                getattr(args, "source_tag", "unclassified"),
                getattr(args, "signal", ""),
                getattr(args, "session_id", "manual"),
            )
        elif args.command == "close":
            cmd_close(state, args.gate)
        elif args.command == "reset":
            cmd_reset(state)
        elif args.command == "trail":
            cmd_trail(state)
        elif args.command == "verify":
            cmd_verify(state)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
