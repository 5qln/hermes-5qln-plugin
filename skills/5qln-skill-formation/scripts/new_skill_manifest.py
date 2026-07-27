"""Scaffold a new skill-v1 formation manifest from a candidate bundle directory.

Usage:
    python new_skill_manifest.py BUNDLE_ROOT --out PATH
        [--conversion-manifest RELATIVE_PATH] [--overwrite]

The scaffold produces a structurally valid but intentionally incomplete
manifest.  Human-dependent fields (triggers, requirements, fixtures, review,
promotion) are left open or empty.
"""

from __future__ import annotations

import sys
from pathlib import Path

from skill_common import (
    SkillContractError,
    atomic_write_json,
    compute_bundle_sha256,
    inspect_regular_file,
    inventory_bundle,
    sha256_bytes,
)

_CATEGORY_PREFIXES: dict[str, str] = {
    "references": "references/",
    "scripts": "scripts/",
    "tests": "tests/",
    "fixtures": "fixtures/",
    "provenance": "provenance/",
}


def _categorise(records: list[dict[str, object]]) -> dict[str, object]:
    """Sort bundle records into their declared categories."""
    skill_md: dict[str, object] | None = None
    bins: dict[str, list[dict[str, object]]] = {k: [] for k in _CATEGORY_PREFIXES}

    for rec in records:
        path = str(rec["path"])
        if path == "SKILL.md":
            skill_md = rec
            continue
        placed = False
        for cat, prefix in _CATEGORY_PREFIXES.items():
            if path.startswith(prefix):
                bins[cat].append(rec)
                placed = True
                break
        if not placed:
            # Files at root that aren't SKILL.md go to references by default
            bins["references"].append(rec)

    if skill_md is None:
        raise SkillContractError("FILE_MISSING", "SKILL.md not found in bundle root")

    result: dict[str, object] = {"skill_md": skill_md}
    for cat in _CATEGORY_PREFIXES:
        result[cat] = bins[cat]
    return result


def build_manifest(
    bundle_root: Path, conversion_manifest: str
) -> dict[str, object]:
    """Build an intentionally incomplete skill-v1 manifest scaffold.

    The scaffold infers only machine-determinable facts: bundle inventory,
    digests, and file metadata.  All human-dependent fields (triggers,
    requirements, behavioral fixtures, review, promotion) are left open.
    """
    root = bundle_root.resolve()
    if not root.is_dir():
        raise SkillContractError("FILE_MISSING", "bundle root is not a directory", str(root))

    # Inventory every regular file (with safety checks)
    records = inventory_bundle(root)

    # Categorise
    bundle = _categorise(records)

    # Compute the bundle digest
    bundle_sha256 = compute_bundle_sha256(records)

    # Inspect the conversion manifest
    conv_info = inspect_regular_file(root, conversion_manifest)

    # Compute contract digest over the contract section (all empty at scaffold time)
    contract = {
        "triggers": [],
        "non_triggers": [],
        "behavioral_requirements": [],
        "completion_criteria": [],
        "claimed_tools": [],
        "related_skills": [],
    }
    contract_sha256 = sha256_bytes(
        __import__("json").dumps(
            contract, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    )

    # Derive skill name from directory name
    skill_name = root.name

    return {
        "format_version": "skill-v1",
        "title": f"{skill_name} (scaffold)",
        "skill": {
            "name": skill_name,
            "bundle_root": ".",
            "bundle_sha256": bundle_sha256,
            "contract_sha256": contract_sha256,
        },
        "provenance": {
            "conversion_manifest": conv_info,
            "formation_evidence": [],
        },
        "bundle": bundle,
        "contract": contract,
        "requirement_traceability": [],
        "behavioral_fixtures": [],
        "human_review": {
            "status": "open",
            "reviewer": None,
            "evidence": [],
        },
        "promotion": {
            "requested_state": "draft",
            "target": "local-skill",
            "authorization_evidence_ids": [],
        },
    }


def main(argv: list[str] | None = None) -> int:
    """Minimal CLI entry point.  Returns 0 on success, 2 on invocation failure."""
    args = argv[1:] if argv is not None else sys.argv[1:]

    if len(args) < 2:
        print("Usage: new_skill_manifest.py BUNDLE_ROOT --out PATH [--conversion-manifest PATH] [--overwrite]", file=sys.stderr)
        return 2

    bundle_root = Path(args[0])
    out_path: Path | None = None
    conversion_manifest = "provenance/conversion-manifest.json"
    overwrite = False

    i = 1
    while i < len(args):
        if args[i] == "--out" and i + 1 < len(args):
            out_path = Path(args[i + 1])
            i += 2
        elif args[i] == "--conversion-manifest" and i + 1 < len(args):
            conversion_manifest = args[i + 1]
            i += 2
        elif args[i] == "--overwrite":
            overwrite = True
            i += 1
        else:
            print(f"Unknown argument: {args[i]}", file=sys.stderr)
            return 2

    if out_path is None:
        print("--out PATH is required", file=sys.stderr)
        return 2

    try:
        manifest = build_manifest(bundle_root, conversion_manifest)
        atomic_write_json(out_path, manifest, overwrite=overwrite)
    except SkillContractError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
