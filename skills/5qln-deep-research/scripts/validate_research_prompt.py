#!/usr/bin/env python3
"""Validate a generated standalone 5QLN deep-research prompt."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_EXACT = (
    "LAW:         H = ∞0 | A = K",
    "CYCLE:       S → G → Q → P → V",
    "S = ∞0 → ?",
    "G = α ≡ {α'}",
    "Q = φ ⋂ Ω",
    "P = δE/δV → ∇",
    "V = (L ∩ G → B'') → ∞0'",
    "OUTPUTS:     S→X  G→Y  Q→Z  P→A  V→B+B''+∞0'",
    "HOLOGRAPHIC: XY := X within Y | X, Y ∈ {S, G, Q, P, V}",
    "COMPLETION:  No V without ∞0'",
    "CORRUPTION:  L1 L2 L3 L4 V∅",
    "CENTER:      not a sixth phase — coherence only",
    "MASTER:   (H = ∞0 | A = K) × (S → G → Q → P → V) = B'' → ∞0'",
    "CREATIVE: ∞0 → X → α → Y → φ → Z → ∇ → A → B → ∞0'",
)

PHASE_MARKERS = (
    "[S — Seed",
    "[G — Growth",
    "[Q — Quality",
    "[P — Flow",
    "[V — Value",
)

REQUIRED_GROUPS = {
    "inquiry provenance": ("Inquiry exact", "inquiry_exact"),
    "human/AI boundary": ("working inside K", "inside K", "A = K"),
    "X status": ("x_status",),
    "alpha collapse test": ("collapse test",),
    "phi boundary": ("phi_status", "φ only", "φ limited"),
    "Z status": ("z_status",),
    "claim evidence": ("claim-evidence", "claim_evidence"),
    "counterevidence": ("counterevidence", "contradiction_ledger", "contradictory evidence"),
    "source/derived/proposal separation": ("`source`", "source / `derived` / `proposal`"),
    "energy/value comparison": ("delta_E", "δE"),
    "gradient": ("gradient_nabla", "∇"),
    "two-pass composition": ("Pass 1", "formation analysis"),
    "local value": ("local_L", "Local L", "Name L"),
    "global propagation": ("global_G", "Global G"),
    "return status": ("return_status",),
    "completion status": ("completion_status",),
    "removal test": ("removal test", "Removal test"),
    "corruption guards": ("L1 Closing", "L1 "),
}

L4_SUBSTITUTIONS = (
    "S = input",
    "G = processing",
    "Q = QA",
    "P = execution",
    "V = output",
)


def contains_any(text: str, needles: tuple[str, ...]) -> bool:
    lowered = text.casefold()
    return any(needle.casefold() in lowered for needle in needles)


def last_content_line(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    while lines and lines[-1].strip() in {"```", "````", "~~~~"}:
        lines.pop()
    return lines[-1].strip() if lines else ""


def validate(text: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for exact in REQUIRED_EXACT:
        if exact not in text:
            errors.append(f"CONSTITUTION_DRIFT: missing exact text: {exact}")

    positions = [text.find(marker) for marker in PHASE_MARKERS]
    for marker, position in zip(PHASE_MARKERS, positions):
        if position < 0:
            errors.append(f"PHASE_MISSING: {marker}")
    if all(position >= 0 for position in positions) and positions != sorted(positions):
        errors.append("PHASE_ORDER: phases must appear as S → G → Q → P → V")

    for label, needles in REQUIRED_GROUPS.items():
        if not contains_any(text, needles):
            errors.append(f"CONTRACT_MISSING: {label}")

    for phrase in L4_SUBSTITUTIONS:
        if phrase.casefold() in text.casefold():
            errors.append(f"L4_PERFORMING: generic phase substitution found: {phrase}")

    unresolved = re.findall(r"\{\{[^{}]+\}\}", text)
    if unresolved:
        preview = ", ".join(dict.fromkeys(unresolved[:5]))
        errors.append(f"UNRESOLVED_TEMPLATE: replace template tokens: {preview}")

    if "literal-v1" not in text:
        warnings.append("LENS_VERSION: declare literal-v1 when holographic addresses may be used")
    if not contains_any(text, ("publication date", "publication_date")):
        warnings.append("SOURCE_DATES: require publication dates")
    if not contains_any(text, ("event date", "event_date")):
        warnings.append("EVENT_DATES: distinguish event dates when relevant")
    if not contains_any(text, ("primary source", "primary and")):
        warnings.append("SOURCE_QUALITY: state a primary-source preference")
    if not contains_any(text, ("failed search", "failed_search")):
        warnings.append("SEARCH_GAPS: require failed searches or inaccessible-source gaps")

    final_line = last_content_line(text)
    if not final_line.endswith("?"):
        errors.append("V_EMPTY: the last nonblank prompt line must be a real return question ending in ?")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate one generated standalone 5QLN deep-research prompt."
    )
    parser.add_argument("prompt", type=Path, help="UTF-8 Markdown or text prompt")
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Emit one machine-readable JSON result instead of human-readable lines.",
    )
    args = parser.parse_args()

    try:
        text = args.prompt.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"ERROR READ: {exc}", file=sys.stderr)
        return 2

    errors, warnings = validate(text)
    valid = not errors
    if args.json_output:
        print(
            json.dumps(
                {
                    "format_version": "1.0",
                    "status": "passed" if valid else "failed",
                    "valid": valid,
                    "counts": {"errors": len(errors), "warnings": len(warnings)},
                    "errors": errors,
                    "warnings": warnings,
                },
                ensure_ascii=False,
            )
        )
    else:
        status = "PASS" if valid else "FAIL"
        print(
            f"5QLN research prompt validator: {status} | "
            f"errors={len(errors)} warnings={len(warnings)}"
        )
        for item in errors:
            print(f"ERROR {item}")
        for item in warnings:
            print(f"WARN  {item}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
