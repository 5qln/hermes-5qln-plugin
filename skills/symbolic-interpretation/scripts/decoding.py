#!/usr/bin/env python3
"""Canonical structural decoder for the bundled 5QLN cycle runtime.

This module verifies form only. It cannot attest emergence, resonance, source
quality, or human recognition. It intentionally uses only Python's standard
library so the cycle engine remains self-contained.
"""

from __future__ import annotations

import unicodedata
from typing import Iterable, Mapping, Optional


VERSION = "2026-07-28.1"
CODEX_HASH = "feaa46b4147d4e023cdd3fd59c051d063e8ec654ee7b38a481dcd5e4c781859b"

PHASE_FOOTER_SPEC = {
    "S": {
        "required": ["X"],
        "optional": [],
    },
    "G": {
        "required": ["ALPHA", "SEEKS"],
        "optional": [],
    },
    "Q": {
        "required": ["PHI", "OMEGA", "ALIGNMENT", "EXTENT"],
        "optional": ["Z"],
    },
    "P": {
        "required": ["VALUE_MAX", "ENERGY", "A"],
        "optional": [],
    },
    "V": {
        "required": ["L", "B2", "INF0P", "LIVENESS"],
        "optional": [],
    },
}

KNOWN_FIELDS = {
    key
    for spec in PHASE_FOOTER_SPEC.values()
    for key in (*spec["required"], *spec["optional"])
}
VALID_ALIGNMENTS = {"natural", "partial", "none", "forced"}


def normalize_question(value: str) -> str:
    """Canonicalize a question for conservative non-repetition checks."""
    normalized = unicodedata.normalize("NFKC", value).casefold()
    # Only letters and numbers carry identity in this deliberately conservative
    # signature. This removes spacing, punctuation, symbols, format controls,
    # and other invisible characters so cosmetic Unicode cannot make the
    # opening question look new.
    return "".join(
        char
        for char in normalized
        if unicodedata.category(char)[0] in {"L", "N"}
    )


def _is_single_terminal_question(value: str) -> bool:
    normalized = unicodedata.normalize("NFKC", value).strip()
    return normalized.endswith("?") and normalized.count("?") == 1


def looks_like_footer_shape(value: str) -> bool:
    """Recognize canonical and visually confusable ``FIELD:`` prefixes."""
    normalized = unicodedata.normalize("NFKC", value).lstrip()
    if not normalized or not (
        "A" <= normalized[0] <= "Z" or "a" <= normalized[0] <= "z"
    ):
        return False
    index = 1
    while index < len(normalized) and (
        "A" <= normalized[index] <= "Z"
        or "a" <= normalized[index] <= "z"
        or normalized[index].isdigit()
        or normalized[index] == "_"
    ):
        index += 1
    while index < len(normalized) and normalized[index].isspace():
        index += 1
    if index >= len(normalized):
        return False
    separator = normalized[index]
    name = unicodedata.name(separator, "")
    return (
        separator in {":", "։"}
        or "COLON" in name
        or "RATIO" in name
        or "TWO DOT" in name
    )


def parse_footer_with_violations(
    content: str,
) -> tuple[Optional[dict[str, str]], list[str]]:
    """Parse footer fields and report duplicate, unknown, or prose lines."""
    if not isinstance(content, str) or not content.strip():
        return None, []

    fields: dict[str, str] = {}
    violations: list[str] = []
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if ":" not in line:
            violations.append(f"non-footer line: {line}")
            continue
        raw_key, value = line.split(":", 1)
        raw_key = raw_key.strip()
        key = raw_key.upper()
        value = value.strip()
        if raw_key != key:
            violations.append(f"field names must be uppercase: {raw_key or '<empty>'}")
            continue
        if key not in KNOWN_FIELDS:
            violations.append(f"unknown field {key or '<empty>'}")
            continue
        if key in fields:
            violations.append(f"duplicate field {key}")
            continue
        fields[key] = value
    return fields or None, violations


def parse_footer(content: str) -> Optional[dict[str, str]]:
    """Return recognized ``KEY: value`` footer fields, or ``None``."""
    fields, violations = parse_footer_with_violations(content)
    return None if violations else fields


def _require_integer_range(
    fields: Mapping[str, str], key: str, low: int, high: int, violations: list[str]
) -> None:
    if key not in fields or not fields[key].strip():
        return
    try:
        value = int(fields[key])
    except ValueError:
        violations.append(f"{key} must be an integer from {low} to {high}")
        return
    if not low <= value <= high:
        violations.append(f"{key} must be an integer from {low} to {high}")


def check_fields(
    phase: str,
    fields: Mapping[str, str],
    seed: Optional[str] = None,
    required_keys: Optional[Iterable[str]] = None,
) -> tuple[list[str], list[str]]:
    """Validate canonical phase fields and return ``(violations, warnings)``."""
    phase = phase.upper()
    violations: list[str] = []
    warnings: list[str] = []

    if phase not in PHASE_FOOTER_SPEC:
        return [f"unknown phase '{phase}'"], warnings
    if not isinstance(fields, Mapping):
        return ["phase fields must be a mapping"], warnings

    required = list(required_keys or PHASE_FOOTER_SPEC[phase]["required"])
    allowed = set(required) | set(PHASE_FOOTER_SPEC[phase]["optional"])
    for key in fields:
        if key not in allowed:
            violations.append(f"field {key} is not valid for phase {phase}")
    for key in required:
        value = fields.get(key)
        if not isinstance(value, str) or not value.strip():
            violations.append(f"missing {key}")

    x_value = fields.get("X")
    if (
        isinstance(x_value, str)
        and x_value.strip()
        and not _is_single_terminal_question(x_value)
    ):
        violations.append("X must be a question ending with ?")

    alignment = fields.get("ALIGNMENT")
    if isinstance(alignment, str) and alignment.strip():
        normalized = alignment.strip().lower()
        if normalized not in VALID_ALIGNMENTS:
            violations.append(
                "ALIGNMENT must be one of: " + ", ".join(sorted(VALID_ALIGNMENTS))
            )
        elif normalized in {"none", "forced"} and "Z" in fields:
            violations.append("Z must be omitted when ALIGNMENT is none or forced")

    _require_integer_range(fields, "EXTENT", 0, 10, violations)
    _require_integer_range(fields, "LIVENESS", 0, 10, violations)

    return_value = fields.get("INF0P")
    if isinstance(return_value, str) and return_value.strip():
        normalized_return = unicodedata.normalize("NFKC", return_value.strip())
        if not _is_single_terminal_question(normalized_return):
            violations.append("INF0P must be a return question ending with ?")
        if seed:
            normalized_seed = normalize_question(seed)
            normalized_candidate = normalize_question(normalized_return)
            if normalized_candidate == normalized_seed:
                violations.append("INF0P must not repeat the cycle opening question")

    return violations, warnings
