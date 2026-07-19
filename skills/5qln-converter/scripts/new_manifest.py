#!/usr/bin/env python3
"""Create an exact 5QLN conversion-manifest scaffold from a source inventory."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


CONSTITUTION = {
    "law": "H = ∞0 | A = K",
    "cycle": "S → G → Q → P → V",
    "equations": {
        "S": "S = ∞0 → ?",
        "G": "G = α ≡ {α'}",
        "Q": "Q = φ ⋂ Ω",
        "P": "P = δE/δV → ∇",
        "V": "V = (L ∩ G → B'') → ∞0'",
    },
    "outputs": "S→X  G→Y  Q→Z  P→A  V→B+B''+∞0'",
    "holographic": "XY := X within Y | X, Y ∈ {S, G, Q, P, V}",
    "completion": "No V without ∞0'",
    "corruption": ["L1", "L2", "L3", "L4", "V∅"],
    "center": "not a sixth phase — coherence only",
}

PHASES = "SGQPV"
LENSES = [lens + parent for parent in PHASES for lens in PHASES]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--title", default="Untitled 5QLN conversion")
    args = parser.parse_args()

    try:
        inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"manifest error: cannot read inventory: {exc}", file=sys.stderr)
        return 2
    units = inventory.get("units")
    if not isinstance(units, list) or not units:
        print("manifest error: inventory has no source units", file=sys.stderr)
        return 2

    manifest = {
        "format_version": "1.0",
        "title": args.title,
        "constitution": CONSTITUTION,
        "lens_notation_version": "literal-v1",
        "source": inventory,
        "attestations": [],
        "document_cell": {
            "S": {
                "authority": "",
                "question": "",
                "x_status": "open",
                "X": "",
            },
            "G": {
                "alpha": "",
                "expressions": [],
                "Y": "",
                "y_status": "candidate",
            },
            "Q": {
                "phi": "",
                "omega": "",
                "Z": "",
                "z_status": "open",
            },
            "P": {
                "energy_map": [],
                "value_map": [],
                "gradient": "",
                "A": "",
            },
            "V": {
                "local": "",
                "global": "",
                "benefit": "",
                "artifact": "",
                "return_question": "",
                "return_status": "open",
            },
        },
        "cells": [],
        "lens_audit": [
            {
                "address": address,
                "lens": address[0],
                "parent": address[1],
                "status": "not_reviewed",
                "reason": "",
            }
            for address in LENSES
        ],
        "traceability": [
            {
                "source_unit_id": unit["id"],
                "primary_cell": None,
                "secondary_cells": [],
                "output_refs": [],
                "preserved": False,
                "note": "",
            }
            for unit in units
        ],
        "derived_insights": [],
        "open_questions": [],
        "completion": {
            "status": "open",
            "benefit": "",
            "artifact": "",
            "return_question": "",
            "return_status": "open",
            "removal_test": "",
        },
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"manifest: {len(units)} traceability rows and 25 lens checks -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
