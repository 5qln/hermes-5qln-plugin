#!/usr/bin/env python3
"""Compile a 5QLN conversion manifest for syntax, formation, and preservation."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


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
ALL_LENSES = {lens + parent for parent in PHASES for lens in PHASES}
TARGETS = {"S": "X", "G": "Y", "Q": "Z", "P": "A", "V": "B+B''+∞0'"}
ALLOWED_GUARDS = set(CONSTITUTION["corruption"])
ATTESTATION_TYPES = {"X", "Z", "value", "constitution", "return"}
LENS_STATUSES = {"used", "released", "not_applicable", "not_reviewed"}


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return value is not None


class Compiler:
    def __init__(self, manifest: Any) -> None:
        self.manifest = manifest
        self.errors: list[dict[str, str]] = []
        self.warnings: list[dict[str, str]] = []
        self.info: dict[str, Any] = {}

    def add(self, severity: str, code: str, path: str, message: str) -> None:
        finding = {"code": code, "path": path, "message": message}
        if severity == "error":
            self.errors.append(finding)
        else:
            self.warnings.append(finding)

    def error(self, code: str, path: str, message: str) -> None:
        self.add("error", code, path, message)

    def warn(self, code: str, path: str, message: str) -> None:
        self.add("warning", code, path, message)

    def require_keys(self, obj: Any, keys: list[str], path: str) -> bool:
        if not isinstance(obj, dict):
            self.error("TYPE", path, "Expected object")
            return False
        for key in keys:
            if key not in obj:
                self.error("MISSING", f"{path}.{key}", "Required field is missing")
        return True

    def compile(self) -> dict[str, Any]:
        if not isinstance(self.manifest, dict):
            self.error("TYPE", "$", "Manifest root must be an object")
            return self.report()
        self.check_root()
        self.check_exact_symbols()
        self.check_constitution()
        source_ids = self.check_source()
        attestations = self.check_attestations(source_ids)
        self.check_document_cell(attestations)
        cell_addresses = self.check_cells(source_ids)
        self.check_lens_audit(cell_addresses)
        self.check_traceability(source_ids, cell_addresses)
        self.check_derivations(source_ids)
        self.check_open_questions()
        self.check_completion(attestations)
        self.info.update(
            {
                "source_units": len(source_ids),
                "converted_cells": len(cell_addresses),
                "lens_addresses": len(ALL_LENSES),
            }
        )
        return self.report()

    def report(self) -> dict[str, Any]:
        return {
            "status": "failed" if self.errors else "passed",
            "counts": {"errors": len(self.errors), "warnings": len(self.warnings)},
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
        }

    def check_root(self) -> None:
        keys = [
            "format_version",
            "title",
            "constitution",
            "lens_notation_version",
            "source",
            "attestations",
            "document_cell",
            "cells",
            "lens_audit",
            "traceability",
            "derived_insights",
            "open_questions",
            "completion",
        ]
        self.require_keys(self.manifest, keys, "$")
        if self.manifest.get("format_version") != "1.0":
            self.error("VERSION", "$.format_version", "Compiler supports format_version 1.0")
        if not nonempty(self.manifest.get("title")):
            self.error("EMPTY", "$.title", "Conversion title is required")
        if self.manifest.get("lens_notation_version") != "literal-v1":
            self.error(
                "LENS_VERSION",
                "$.lens_notation_version",
                "Use literal-v1: first letter lens, second letter parent",
            )

    def check_exact_symbols(self) -> None:
        serialized = json.dumps(self.manifest, ensure_ascii=False)
        if "′" in serialized:
            self.error("SYMBOL_DRIFT", "$", "Typographic prime U+2032 found; use ASCII apostrophe in α', B'', and ∞0'")
        if "⊗" in serialized:
            self.error("SYMBOL_DRIFT", "$", "Operator ⊗ is not part of the sealed constitutional block")

    def check_constitution(self) -> None:
        actual = self.manifest.get("constitution")
        if actual != CONSTITUTION:
            self.error("CONSTITUTION_DRIFT", "$.constitution", "Constitution does not exactly match the sealed block")

    def check_source(self) -> set[str]:
        source = self.manifest.get("source")
        if not self.require_keys(source, ["units", "sources", "summary"], "$.source"):
            return set()
        units = source.get("units")
        if not isinstance(units, list) or not units:
            self.error("SOURCE_EMPTY", "$.source.units", "At least one source unit is required")
            return set()
        seen: set[str] = set()
        original_ids: list[str] = []
        for index, unit in enumerate(units):
            path = f"$.source.units[{index}]"
            if not self.require_keys(unit, ["id", "kind", "text", "sha256", "source_file", "location"], path):
                continue
            unit_id = unit.get("id")
            if not isinstance(unit_id, str) or not unit_id:
                self.error("SOURCE_ID", f"{path}.id", "Source unit ID is required")
                continue
            if unit_id in seen:
                self.error("SOURCE_ID_DUP", f"{path}.id", f"Duplicate source unit ID {unit_id}")
            seen.add(unit_id)
            text = unit.get("text")
            if not isinstance(text, str) or not text.strip():
                self.error("SOURCE_TEXT", f"{path}.text", "Source unit text is empty")
            elif unit.get("sha256") != text_hash(text):
                self.error("SOURCE_HASH", f"{path}.sha256", "Hash does not match source unit text")
            original_id = unit.get("original_id")
            if original_id:
                original_ids.append(str(original_id))
        duplicates = sorted(key for key, count in Counter(original_ids).items() if count > 1)
        if duplicates:
            self.warn("ORIGINAL_ID_DUP", "$.source.units", f"Repeated original IDs: {', '.join(duplicates)}")
        self.info["original_ids"] = len(original_ids)
        self.info["unique_original_ids"] = len(set(original_ids))
        return seen

    def check_attestations(self, source_ids: set[str]) -> set[str]:
        values = self.manifest.get("attestations")
        if not isinstance(values, list):
            self.error("TYPE", "$.attestations", "Expected an array")
            return set()
        types: set[str] = set()
        for index, attestation in enumerate(values):
            path = f"$.attestations[{index}]"
            if not self.require_keys(attestation, ["type", "evidence", "source_unit_ids"], path):
                continue
            kind = attestation.get("type")
            if kind not in ATTESTATION_TYPES:
                self.error("ATTESTATION_TYPE", f"{path}.type", f"Allowed: {sorted(ATTESTATION_TYPES)}")
            else:
                types.add(kind)
            if not nonempty(attestation.get("evidence")):
                self.error("ATTESTATION_EVIDENCE", f"{path}.evidence", "Attestation requires explicit evidence")
            refs = attestation.get("source_unit_ids")
            if not isinstance(refs, list):
                self.error("TYPE", f"{path}.source_unit_ids", "Expected an array")
            else:
                for ref in refs:
                    if ref not in source_ids:
                        self.error("ATTESTATION_REF", f"{path}.source_unit_ids", f"Unknown source unit {ref}")
        return types

    def check_document_cell(self, attestation_types: set[str]) -> None:
        cell = self.manifest.get("document_cell")
        if not self.require_keys(cell, list(PHASES), "$.document_cell"):
            return
        for phase in PHASES:
            if not isinstance(cell.get(phase), dict):
                self.error("TYPE", f"$.document_cell.{phase}", "Expected an object")

        start = cell.get("S", {})
        self.require_keys(start, ["authority", "question", "x_status", "X"], "$.document_cell.S")
        x_status = start.get("x_status")
        if x_status not in {"open", "candidate", "attested"}:
            self.error("STATUS", "$.document_cell.S.x_status", "Allowed: open, candidate, attested")
        if x_status == "attested" and "X" not in attestation_types:
            self.error("L2", "$.document_cell.S.x_status", "Attested X requires explicit X attestation evidence")
        if x_status == "attested" and not nonempty(start.get("X")):
            self.error("EMPTY", "$.document_cell.S.X", "Attested X cannot be empty")

        growth = cell.get("G", {})
        self.require_keys(growth, ["alpha", "expressions", "Y", "y_status"], "$.document_cell.G")
        if growth.get("y_status") not in {"open", "candidate", "validated"}:
            self.error("STATUS", "$.document_cell.G.y_status", "Allowed: open, candidate, validated")
        if nonempty(growth.get("alpha")) and not isinstance(growth.get("expressions"), list):
            self.error("TYPE", "$.document_cell.G.expressions", "Expected an array")

        quality = cell.get("Q", {})
        self.require_keys(quality, ["phi", "omega", "Z", "z_status"], "$.document_cell.Q")
        z_status = quality.get("z_status")
        if z_status not in {"open", "candidate", "attested"}:
            self.error("STATUS", "$.document_cell.Q.z_status", "Allowed: open, candidate, attested")
        if z_status == "attested" and "Z" not in attestation_types:
            self.error("L3", "$.document_cell.Q.z_status", "Attested Z requires explicit Z attestation evidence")

        power = cell.get("P", {})
        self.require_keys(power, ["energy_map", "value_map", "gradient", "A"], "$.document_cell.P")
        if not isinstance(power.get("energy_map"), list) or not isinstance(power.get("value_map"), list):
            self.error("TYPE", "$.document_cell.P", "energy_map and value_map must be arrays")

        value = cell.get("V", {})
        self.require_keys(
            value,
            ["local", "global", "benefit", "artifact", "return_question", "return_status"],
            "$.document_cell.V",
        )
        return_status = value.get("return_status")
        if return_status not in {"open", "candidate", "human-recognized"}:
            self.error("STATUS", "$.document_cell.V.return_status", "Allowed: open, candidate, human-recognized")
        if return_status == "human-recognized" and "return" not in attestation_types:
            self.error("L3", "$.document_cell.V.return_status", "Human-recognized return requires return attestation")

    def check_cells(self, source_ids: set[str]) -> set[str]:
        values = self.manifest.get("cells")
        if not isinstance(values, list):
            self.error("TYPE", "$.cells", "Expected an array")
            return set()
        addresses: set[str] = set()
        formation_signatures: defaultdict[str, list[str]] = defaultdict(list)
        for index, cell in enumerate(values):
            path = f"$.cells[{index}]"
            keys = [
                "address",
                "lens",
                "parent",
                "parent_equation",
                "parent_target",
                "source_unit_ids",
                "formation",
                "domain_items",
                "evidence",
                "guards",
            ]
            if not self.require_keys(cell, keys, path):
                continue
            address = cell.get("address")
            if address not in ALL_LENSES:
                self.error("LENS", f"{path}.address", f"Invalid literal lens address {address!r}")
                continue
            if address in addresses:
                self.error("LENS_DUP", f"{path}.address", f"Duplicate converted cell {address}")
            addresses.add(address)
            if cell.get("lens") != address[0] or cell.get("parent") != address[1]:
                self.error("LENS_ORIENTATION", path, "literal-v1 requires first letter lens, second letter parent")
            parent = address[1]
            if cell.get("parent_equation") != CONSTITUTION["equations"][parent]:
                self.error("EQUATION", f"{path}.parent_equation", "Parent equation is not exact")
            if cell.get("parent_target") != TARGETS[parent]:
                self.error("TARGET", f"{path}.parent_target", f"Expected parent target {TARGETS[parent]}")
            refs = cell.get("source_unit_ids")
            if not isinstance(refs, list):
                self.error("TYPE", f"{path}.source_unit_ids", "Expected an array")
            else:
                for ref in refs:
                    if ref not in source_ids:
                        self.error("CELL_REF", f"{path}.source_unit_ids", f"Unknown source unit {ref}")
            formation = cell.get("formation")
            if not isinstance(formation, dict):
                self.error("TYPE", f"{path}.formation", "Expected S/G/Q/P/V object")
            else:
                for phase in PHASES:
                    if not nonempty(formation.get(phase)):
                        self.error("FORMATION", f"{path}.formation.{phase}", "Nested phase formation is required")
                signature = "\n".join(str(formation.get(phase, "")).strip().lower() for phase in PHASES)
                formation_signatures[signature].append(address)
            evidence = cell.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                self.error("EVIDENCE", f"{path}.evidence", "At least one compiler evidence item is required")
            guards = cell.get("guards")
            if not isinstance(guards, list):
                self.error("TYPE", f"{path}.guards", "Expected an array")
            else:
                extras = sorted(set(guards) - ALLOWED_GUARDS)
                if extras:
                    self.error("CORRUPTION_CODES", f"{path}.guards", f"Non-canonical codes: {extras}")
        for signature, duplicate_addresses in formation_signatures.items():
            if signature and len(duplicate_addresses) > 1:
                self.warn(
                    "L4_DUPLICATE_FORMATION",
                    "$.cells",
                    f"Identical nested formation appears in: {', '.join(sorted(duplicate_addresses))}",
                )
        return addresses

    def check_lens_audit(self, cell_addresses: set[str]) -> None:
        values = self.manifest.get("lens_audit")
        if not isinstance(values, list):
            self.error("TYPE", "$.lens_audit", "Expected an array")
            return
        seen: set[str] = set()
        for index, item in enumerate(values):
            path = f"$.lens_audit[{index}]"
            if not self.require_keys(item, ["address", "lens", "parent", "status", "reason"], path):
                continue
            address = item.get("address")
            if address not in ALL_LENSES:
                self.error("LENS", f"{path}.address", f"Invalid lens address {address!r}")
                continue
            if address in seen:
                self.error("LENS_DUP", f"{path}.address", f"Duplicate lens audit {address}")
            seen.add(address)
            if item.get("lens") != address[0] or item.get("parent") != address[1]:
                self.error("LENS_ORIENTATION", path, "literal-v1 orientation mismatch")
            status = item.get("status")
            if status not in LENS_STATUSES:
                self.error("STATUS", f"{path}.status", f"Allowed: {sorted(LENS_STATUSES)}")
            elif status == "not_reviewed":
                self.error("LENS_UNREVIEWED", f"{path}.status", "Every lens must be used, released, or marked not_applicable")
            elif status in {"released", "not_applicable"} and not nonempty(item.get("reason")):
                self.error("LENS_REASON", f"{path}.reason", f"{status} requires an evidence-based reason")
            elif status == "used" and address not in cell_addresses:
                self.error("LENS_CELL", f"{path}.status", "Used lens has no converted cell")
        missing = sorted(ALL_LENSES - seen)
        extra = sorted(seen - ALL_LENSES)
        if missing:
            self.error("LENS_MISSING", "$.lens_audit", f"Missing lens audits: {', '.join(missing)}")
        if extra:
            self.error("LENS_EXTRA", "$.lens_audit", f"Unexpected lens audits: {', '.join(extra)}")
        if len(values) != 25:
            self.error("LENS_COUNT", "$.lens_audit", f"Expected exactly 25 entries, found {len(values)}")

    def check_traceability(self, source_ids: set[str], cell_addresses: set[str]) -> None:
        values = self.manifest.get("traceability")
        if not isinstance(values, list):
            self.error("TYPE", "$.traceability", "Expected an array")
            return
        by_source: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
        for index, item in enumerate(values):
            path = f"$.traceability[{index}]"
            keys = ["source_unit_id", "primary_cell", "secondary_cells", "output_refs", "preserved", "note"]
            if not self.require_keys(item, keys, path):
                continue
            source_id = item.get("source_unit_id")
            if source_id not in source_ids:
                self.error("TRACE_SOURCE", f"{path}.source_unit_id", f"Unknown source unit {source_id}")
                continue
            by_source[source_id].append(item)
            if item.get("preserved") is not True:
                self.error("TRACE_LOSS", f"{path}.preserved", "Source unit is not affirmed preserved")
            primary = item.get("primary_cell")
            if primary not in cell_addresses:
                self.error("TRACE_CELL", f"{path}.primary_cell", f"Unknown or missing primary cell {primary}")
            secondary = item.get("secondary_cells")
            if not isinstance(secondary, list):
                self.error("TYPE", f"{path}.secondary_cells", "Expected an array")
            else:
                for address in secondary:
                    if address not in cell_addresses:
                        self.error("TRACE_CELL", f"{path}.secondary_cells", f"Unknown secondary cell {address}")
            if not isinstance(item.get("output_refs"), list) or not item.get("output_refs"):
                self.warn("TRACE_OUTPUT", f"{path}.output_refs", "No converted output reference recorded")
        missing = sorted(source_ids - set(by_source))
        duplicates = sorted(source_id for source_id, rows in by_source.items() if len(rows) > 1)
        if missing:
            self.error("TRACE_MISSING", "$.traceability", f"Unmapped source units: {', '.join(missing)}")
        if duplicates:
            self.error("TRACE_DUP", "$.traceability", f"Multiple trace rows for source units: {', '.join(duplicates)}")
        if len(values) != len(source_ids):
            self.error("TRACE_COUNT", "$.traceability", f"Expected {len(source_ids)} rows, found {len(values)}")

    def check_derivations(self, source_ids: set[str]) -> None:
        values = self.manifest.get("derived_insights")
        if not isinstance(values, list):
            self.error("TYPE", "$.derived_insights", "Expected an array")
            return
        seen: set[str] = set()
        for index, item in enumerate(values):
            path = f"$.derived_insights[{index}]"
            keys = ["id", "text", "basis_source_unit_ids", "basis_constitution", "status"]
            if not self.require_keys(item, keys, path):
                continue
            insight_id = item.get("id")
            if insight_id in seen:
                self.error("DERIVED_ID", f"{path}.id", f"Duplicate derived insight ID {insight_id}")
            seen.add(insight_id)
            if item.get("status") != "derived":
                self.error("DERIVED_STATUS", f"{path}.status", "Derived insight status must be 'derived'")
            source_basis = item.get("basis_source_unit_ids")
            constitutional_basis = item.get("basis_constitution")
            if not isinstance(source_basis, list) or not isinstance(constitutional_basis, list):
                self.error("TYPE", path, "Derivation bases must be arrays")
                continue
            unknown = sorted(set(source_basis) - source_ids)
            if unknown:
                self.error("DERIVED_REF", f"{path}.basis_source_unit_ids", f"Unknown source units: {unknown}")
            if not source_basis and not constitutional_basis:
                self.error("DERIVED_BASIS", path, "Derived insight requires source and/or constitutional basis")
            if not nonempty(item.get("text")):
                self.error("EMPTY", f"{path}.text", "Derived insight text is empty")

    def check_open_questions(self) -> None:
        values = self.manifest.get("open_questions")
        if not isinstance(values, list):
            self.error("TYPE", "$.open_questions", "Expected an array")
            return
        for index, value in enumerate(values):
            if not isinstance(value, str) or not value.strip():
                self.error("QUESTION", f"$.open_questions[{index}]", "Open question must be non-empty text")
            elif not value.strip().endswith("?"):
                self.warn("QUESTION_FORM", f"$.open_questions[{index}]", "Open item does not end as a question")

    def check_completion(self, attestation_types: set[str]) -> None:
        value = self.manifest.get("completion")
        keys = ["status", "benefit", "artifact", "return_question", "return_status", "removal_test"]
        if not self.require_keys(value, keys, "$.completion"):
            return
        status = value.get("status")
        if status not in {"open", "candidate", "complete"}:
            self.error("STATUS", "$.completion.status", "Allowed: open, candidate, complete")
            return
        return_status = value.get("return_status")
        if return_status not in {"open", "candidate", "human-recognized"}:
            self.error("STATUS", "$.completion.return_status", "Allowed: open, candidate, human-recognized")
        if status in {"candidate", "complete"}:
            for key in ["benefit", "artifact", "return_question", "removal_test"]:
                if not nonempty(value.get(key)):
                    self.error("V∅", f"$.completion.{key}", f"{status} conversion requires {key}")
            question = value.get("return_question")
            if isinstance(question, str) and question.strip() and not question.strip().endswith("?"):
                self.error("V∅", "$.completion.return_question", "Return must be a question, not a summary")
            removal = value.get("removal_test")
            if isinstance(removal, str) and 0 < len(removal.strip()) < 40:
                self.warn("L4_REMOVAL_TEST", "$.completion.removal_test", "Removal test is too vague to demonstrate causal operation")
        if status == "complete":
            required = {"X", "Z", "value", "return"}
            missing = sorted(required - attestation_types)
            if missing:
                self.error("L3", "$.completion.status", f"Complete V lacks human attestations: {', '.join(missing)}")
            if return_status != "human-recognized":
                self.error("V∅", "$.completion.return_status", "Complete V requires human-recognized return")
        if return_status == "human-recognized" and "return" not in attestation_types:
            self.error("L3", "$.completion.return_status", "Human-recognized return requires attestation evidence")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"compiler error: cannot read manifest: {exc}", file=sys.stderr)
        return 2

    report = Compiler(manifest).compile()
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = report["counts"]
    print(f"5QLN compiler: {report['status']} | errors={counts['errors']} warnings={counts['warnings']}")
    if report["errors"]:
        for finding in report["errors"][:20]:
            print(f"ERROR {finding['code']} {finding['path']}: {finding['message']}")
        if len(report["errors"]) > 20:
            print(f"... {len(report['errors']) - 20} additional errors")
    if report["warnings"]:
        for finding in report["warnings"][:10]:
            print(f"WARN  {finding['code']} {finding['path']}: {finding['message']}")
        if len(report["warnings"]) > 10:
            print(f"... {len(report['warnings']) - 10} additional warnings")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
