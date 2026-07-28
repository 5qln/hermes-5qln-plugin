#!/usr/bin/env python3
"""Persistent phase-transition source log for the 5QLN learning aligner.

The log records what an operator or human classified at each transition. It
never infers emergence or resonance. Python standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


VERSION = 1
PHASES = ("S", "G", "Q", "P", "V")
GATES = ("x", "y", "z", "a", "b")
GATE_PHASE = dict(zip(GATES, PHASES))
INFINITY_ZERO_TAGS = {"emergent", "revealed", "lived", "felt", "opened"}
PHASE_SOURCE_TAGS = {
    "S": {"emergent", "mechanical", "unclassified"},
    "G": {"revealed", "imposed", "unclassified"},
    "Q": {"lived", "logical", "unclassified"},
    "P": {"felt", "calculated", "unclassified"},
    "V": {"opened", "closed", "unclassified"},
}
KNOWN_TAGS = set().union(*PHASE_SOURCE_TAGS.values())


def phase_log_path() -> Path:
    """Resolve the log path without relying on the removed installer repo."""
    explicit = os.environ.get("PHASE_LOG_PATH")
    if explicit:
        return Path(explicit).expanduser()
    wiki = os.environ.get("QLN_WIKI")
    if wiki:
        return Path(wiki).expanduser() / "state" / "phase_log.json"
    hermes_home = Path(os.environ.get("HERMES_HOME", "~/.hermes")).expanduser()
    return hermes_home / "5qln" / "phase_log.json"


def empty_log() -> dict[str, Any]:
    return {"version": VERSION, "entries": []}


def load_log(path: Optional[Path] = None) -> dict[str, Any]:
    target = path or phase_log_path()
    if not target.exists():
        return empty_log()
    data = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
        raise ValueError(f"invalid phase log structure: {target}")
    return data


def save_log(data: dict[str, Any], path: Optional[Path] = None) -> None:
    """Atomically replace the phase log."""
    target = path or phase_log_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()


@contextmanager
def phase_log_lock(path: Optional[Path] = None):
    """Serialize phase-log transactions with an OS-released advisory lock."""
    target = path or phase_log_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    lock_path = target.with_name(f".{target.name}.lock")
    handle = lock_path.open("a+b")
    try:
        if os.name == "nt":
            import msvcrt

            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"0")
                handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield target
        finally:
            if os.name == "nt":
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    finally:
        handle.close()


def source_side(source: str) -> Optional[str]:
    if source == "unclassified":
        return None
    return "∞0" if source in INFINITY_ZERO_TAGS else "K"


def append_entry(
    phase: str,
    gate: str,
    source: str,
    content: str,
    *,
    signal: str = "",
    session_id: str = "manual",
    cycle: int = 1,
    path: Optional[Path] = None,
    _lock: bool = True,
) -> dict[str, Any]:
    """Append one explicit transition record and return it."""
    if _lock:
        with phase_log_lock(path):
            return append_entry(
                phase,
                gate,
                source,
                content,
                signal=signal,
                session_id=session_id,
                cycle=cycle,
                path=path,
                _lock=False,
            )

    phase = phase.upper()
    gate = gate.lower()
    source = source.strip().lower()
    content = content.strip()
    session_id = session_id.strip() or "manual"

    if phase not in PHASES:
        raise ValueError(f"phase must be one of: {', '.join(PHASES)}")
    if gate not in GATES:
        raise ValueError(f"gate must be one of: {', '.join(GATES)}")
    if GATE_PHASE[gate] != phase:
        raise ValueError(f"gate {gate} belongs to phase {GATE_PHASE[gate]}, not {phase}")
    if source not in KNOWN_TAGS:
        raise ValueError("unknown source tag: " + source)
    if source not in PHASE_SOURCE_TAGS[phase]:
        raise ValueError(f"source tag {source} is not valid for phase {phase}")
    if not content:
        raise ValueError("content is required")
    if cycle < 1:
        raise ValueError("cycle must be at least 1")

    record = {
        "session": session_id,
        "cycle": cycle,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase": phase,
        "gate": gate,
        "source": source,
        "side": source_side(source),
        "content": content,
        "signal": signal.strip(),
    }
    data = load_log(path)
    data["version"] = VERSION
    data["entries"].append(record)
    save_log(data, path)
    return record


def filtered_entries(data: dict[str, Any], session_id: Optional[str]) -> list[dict[str, Any]]:
    entries = data["entries"]
    if session_id:
        return [entry for entry in entries if entry.get("session") == session_id]
    return entries


def tagline(entries: list[dict[str, Any]]) -> str:
    return " → ".join(
        f"{entry.get('phase', '?')}:{entry.get('source', 'unclassified')}"
        for entry in entries
    )


def summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    by_phase: dict[str, dict[str, int]] = {}
    for phase in PHASES:
        counts = Counter(
            entry.get("source", "unclassified")
            for entry in entries
            if entry.get("phase") == phase
        )
        if counts:
            by_phase[phase] = dict(sorted(counts.items()))
    return {
        "entries": len(entries),
        "sessions": sorted({entry.get("session", "manual") for entry in entries}),
        "sources_by_phase": by_phase,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="5QLN phase transition source log")
    commands = parser.add_subparsers(dest="command", required=True)

    append_parser = commands.add_parser("append", help="Append a transition record")
    append_parser.add_argument("phase", choices=PHASES)
    append_parser.add_argument("gate", choices=GATES)
    append_parser.add_argument("source", choices=sorted(KNOWN_TAGS))
    append_parser.add_argument("-c", "--content", required=True)
    append_parser.add_argument("-s", "--signal", default="")
    append_parser.add_argument("--session-id", default=os.environ.get("HERMES_SESSION_ID", "manual"))
    append_parser.add_argument("--cycle", type=int, default=1)

    for command in ("chain", "tagline", "summary", "self-check"):
        command_parser = commands.add_parser(command)
        command_parser.add_argument("--session-id", default=None)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        if args.command == "append":
            record = append_entry(
                args.phase,
                args.gate,
                args.source,
                args.content,
                signal=args.signal,
                session_id=args.session_id,
                cycle=args.cycle,
            )
            print(json.dumps({"ok": True, "entry": record}, ensure_ascii=False))
            return

        entries = filtered_entries(load_log(), args.session_id)
        if args.command == "chain":
            print(json.dumps(entries, indent=2, ensure_ascii=False))
        elif args.command == "tagline":
            print(tagline(entries))
        else:
            payload = summary(entries)
            if args.command == "self-check":
                payload["boundary"] = (
                    "This report summarizes explicit source tags; it does not attest aliveness."
                )
            print(json.dumps(payload, indent=2, ensure_ascii=False))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
