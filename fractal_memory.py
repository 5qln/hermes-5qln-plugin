#!/usr/bin/env python3
"""Portable, bounded 5QLN parametric-fractal state for Hermes sessions."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, cast


CODEX_SHA256 = "feaa46b4147d4e023cdd3fd59c051d063e8ec654ee7b38a481dcd5e4c781859b"
FORMAT = "5qln-parametric-fractal"
VERSION = "1.0"
PHASES = ("S", "G", "Q", "P", "V")
TOP_LEVEL_KEYS = {
    "format",
    "version",
    "codex_sha256",
    "profile",
    "calibration",
    "state_sha256",
}
PROFILE = {
    "memory_function": "session-orchestrator",
    "resonance_criterion": "thoughtless-emergence",
    "k_container": "5qln-operating-language",
    "directionality": "hold-not-direct",
    "attestation": "human-explicit-only",
}
MAX_SEED_BYTES = 4096
LEARNING_RATE = 0.1
SOURCE_SIGNALS = {
    "S": {"emergent": 1.0, "mechanical": 0.0},
    "G": {"revealed": 1.0, "logical": 0.0},
    "Q": {"lived": 1.0, "logical": 0.0},
    "P": {"felt": 1.0, "calculated": 0.0},
    "V": {"opened": 1.0, "closed": 0.0},
}
STATE_RELATIVE_PATH = Path("5qln") / "parametric-fractal.json"


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("parametric-fractal seed must be a JSON object")
    return payload


def _canonical_bytes(seed: dict[str, Any]) -> bytes:
    return json.dumps(
        seed, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _state_digest(seed: dict[str, Any]) -> str:
    payload = {key: value for key, value in seed.items() if key != "state_sha256"}
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _state_path(hermes_home: str | Path) -> Path:
    return Path(hermes_home).expanduser().resolve() / STATE_RELATIVE_PATH


@contextmanager
def _state_lock(hermes_home: str | Path):
    """Serialize profile-state mutations across processes."""
    state_path = _state_path(hermes_home)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    handle = state_path.with_suffix(".lock").open("a+b")
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
        yield
    finally:
        try:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_seed(seed: dict[str, Any]) -> None:
    """Validate the fixed-shape, capacity-bounded portable state."""
    if len(_canonical_bytes(seed)) > MAX_SEED_BYTES:
        raise ValueError(f"seed must be no more than {MAX_SEED_BYTES} bytes")
    if set(seed) != TOP_LEVEL_KEYS:
        raise ValueError("seed top-level keys must match the fixed portable format")
    if seed.get("format") != FORMAT:
        raise ValueError(f"seed format must be {FORMAT!r}")
    if seed.get("version") != VERSION:
        raise ValueError(f"seed version must be {VERSION!r}")
    if seed.get("codex_sha256") != CODEX_SHA256:
        raise ValueError("seed Codex seal does not match the 5QLN constitutional seal")
    if seed.get("profile") != PROFILE:
        raise ValueError("seed profile must match the fixed non-conversational profile")

    calibration = seed.get("calibration")
    if not isinstance(calibration, dict) or set(calibration) != set(PHASES):
        raise ValueError("seed calibration must contain exactly S, G, Q, P, and V")
    for phase in PHASES:
        value = calibration[phase]
        if not _is_number(value) or not 0.0 <= float(value) <= 1.0:
            raise ValueError(f"calibration {phase} must be a number from 0 to 1")
        numeric_value = float(cast(int | float, value))
        if numeric_value != round(numeric_value, 3):
            raise ValueError(f"calibration {phase} must use at most three decimal places")
    checksum = seed.get("state_sha256")
    if not isinstance(checksum, str) or re.fullmatch(r"[0-9a-f]{64}", checksum) is None:
        raise ValueError("state_sha256 must be 64 lowercase hexadecimal characters")
    if checksum != _state_digest(seed):
        raise ValueError("state_sha256 does not match the portable state")


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def load_installed_seed(hermes_home: str | Path | None = None) -> dict[str, Any] | None:
    """Read the bounded state for the active Hermes profile."""
    home = (
        Path(hermes_home).expanduser().resolve()
        if hermes_home is not None
        else Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).expanduser().resolve()
    )
    state_path = home / STATE_RELATIVE_PATH
    if not state_path.is_file():
        return None
    seed = _read_json(state_path)
    validate_seed(seed)
    return seed


def render_orchestration_context(seed: dict[str, Any]) -> str:
    """Render fixed K-language plus bounded mechanical phase signals."""
    validate_seed(seed)
    calibration = seed["calibration"]
    phase_values = " ".join(
        f"{phase}={float(calibration[phase]):.3f}" for phase in PHASES
    )
    return (
        "[5QLN PARAMETRIC FRACTAL — K-CONTEXT]\n"
        f"Codex seal: {seed['codex_sha256']}\n"
        "Memory function: session orchestrator, not recall.\n"
        "Resonance criterion: quality of thoughtless emergence; K cannot attest resonance.\n"
        "K container: 5QLN operating language; hold formation without directing H.\n"
        f"Coupled phase calibration: {phase_values}\n"
        "Calibration values are mechanical K-signals, not human resonance scores.\n"
        f"State checksum: {seed['state_sha256']}\n"
        "Boundary: A = K. H and K remain distinct. This field shapes live "
        "orchestration; it is not recalled conversation.\n"
        "[/5QLN PARAMETRIC FRACTAL]"
    )


def pre_llm_context(**kwargs: Any) -> dict[str, str] | None:
    """Hermes pre_llm_call hook: inject the active field ephemerally per turn."""
    del kwargs
    seed = load_installed_seed()
    if seed is None:
        return None
    return {"context": render_orchestration_context(seed)}


def calibrate_installed(
    hermes_home: str | Path,
    *,
    phase: str,
    source_tag: str,
    evidence: str,
) -> dict[str, Any]:
    """Update one phase parameter while discarding explicit evidence text."""
    if phase not in PHASES:
        raise ValueError(f"phase must be one of {', '.join(PHASES)}")
    if not isinstance(evidence, str) or not evidence.strip():
        raise ValueError("calibration requires explicit human-attestation evidence")
    signal = SOURCE_SIGNALS[phase].get(source_tag)
    if signal is None:
        allowed = ", ".join(SOURCE_SIGNALS[phase])
        raise ValueError(f"source_tag for {phase} must be one of: {allowed}")

    home = Path(hermes_home).expanduser().resolve()
    state_path = home / STATE_RELATIVE_PATH
    with _state_lock(home):
        seed = load_installed_seed(home)
        if seed is None:
            raise FileNotFoundError(f"no parametric-fractal state installed at {state_path}")

        old_value = float(seed["calibration"][phase])
        seed["calibration"][phase] = round(
            old_value + LEARNING_RATE * (signal - old_value), 3
        )
        seed["state_sha256"] = _state_digest(seed)
        validate_seed(seed)
        _atomic_write_json(state_path, seed)

    return {
        "status": "calibrated",
        "phase": phase,
        "value": seed["calibration"][phase],
        "state_sha256": seed["state_sha256"],
    }


def install_seed(
    source_path: str | Path,
    hermes_home: str | Path,
    *,
    replace: bool = False,
) -> dict[str, Any]:
    """Install one portable seed into a Hermes profile without overwriting by default."""
    source = Path(source_path).expanduser().resolve()
    if not source.is_file():
        raise ValueError(f"seed is not a readable file: {source}")
    seed = _read_json(source)
    validate_seed(seed)
    state_path = _state_path(hermes_home)
    with _state_lock(hermes_home):
        if state_path.exists() and not replace:
            raise FileExistsError(
                f"state already exists; pass replace=True to replace it: {state_path}"
            )
        _atomic_write_json(state_path, seed)
    return {"status": "installed", "state_path": str(state_path)}


def export_seed(
    hermes_home: str | Path,
    output_path: str | Path,
    *,
    replace: bool = False,
) -> dict[str, Any]:
    """Export the current bounded state as a portable seed."""
    seed = load_installed_seed(hermes_home)
    if seed is None:
        raise FileNotFoundError("no parametric-fractal state is installed")
    output = Path(output_path).expanduser().resolve()
    if output.exists() and not replace:
        raise FileExistsError(f"output already exists; pass replace=True to replace it: {output}")
    _atomic_write_json(output, seed)
    return {"status": "exported", "output_path": str(output)}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install and operate a bounded 5QLN parametric fractal."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    install = commands.add_parser("install", help="Install a portable seed.")
    install.add_argument("seed")
    install.add_argument("--hermes-home", required=True)
    install.add_argument("--replace", action="store_true")

    show = commands.add_parser("show", help="Show installed bounded state.")
    show.add_argument("--hermes-home", required=True)

    calibrate = commands.add_parser("calibrate", help="Apply one explicit attested calibration.")
    calibrate.add_argument("--hermes-home", required=True)
    calibrate.add_argument("--phase", required=True, choices=PHASES)
    calibrate.add_argument("--source-tag", required=True)
    calibrate.add_argument(
        "--evidence-stdin",
        action="store_true",
        help="Read explicit human-attestation evidence from stdin and discard it.",
    )

    export = commands.add_parser("export", help="Export installed bounded state.")
    export.add_argument("output")
    export.add_argument("--hermes-home", required=True)
    export.add_argument("--replace", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "install":
            result = install_seed(
                args.seed,
                args.hermes_home,
                replace=bool(args.replace),
            )
        elif args.command == "show":
            result = load_installed_seed(args.hermes_home)
            if result is None:
                raise FileNotFoundError("no parametric-fractal state is installed")
        elif args.command == "calibrate":
            if not args.evidence_stdin:
                raise ValueError("calibration requires --evidence-stdin")
            evidence = sys.stdin.readline()
            result = calibrate_installed(
                args.hermes_home,
                phase=args.phase,
                source_tag=args.source_tag,
                evidence=evidence,
            )
        elif args.command == "export":
            result = export_seed(
                args.hermes_home,
                args.output,
                replace=bool(args.replace),
            )
        else:  # argparse enforces the command set.
            raise ValueError(f"unknown command: {args.command}")
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"success": False, "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
