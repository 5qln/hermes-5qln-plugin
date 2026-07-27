"""Verify a skill-v1 formation manifest against the published contract.

Usage:
    python verify_skill.py MANIFEST_PATH [--report PATH] [--promotion-mode]
        [--observations OBS_JSON...] [--capability-snapshot PATH]
        [--overwrite]

Exit codes:
    0 = verifier executed, structural checks passed
    1 = structural or promotion checks failed
    2 = invocation, dependency, or execution failure
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path
from typing import Any

from skill_common import (
    MAX_FILE_BYTES,
    SkillContractError,
    atomic_write_json,
    canonical_json_bytes,
    compute_bundle_sha256,
    inspect_regular_file,
    inventory_bundle,
    sha256_bytes,
    validate_skill_manifest,
)

# ---------------------------------------------------------------------------
# SKILL.md frontmatter parsing (Task 7)
# ---------------------------------------------------------------------------

def parse_skill_frontmatter(text: str) -> tuple[dict[str, object], str]:
    """Parse YAML frontmatter from a SKILL.md file.

    Returns (frontmatter_dict, body_text).
    Raises SkillContractError on any parsing failure.
    """
    if not text.startswith("---"):
        raise SkillContractError(
            "FRONTMATTER_INVALID",
            "SKILL.md must start with YAML frontmatter delimited by ---",
        )

    try:
        import yaml
    except ImportError as exc:
        raise SkillContractError(
            "DEPENDENCY_MISSING",
            "PyYAML is required for strict SKILL.md frontmatter parsing. "
            "Install with: pip install pyyaml",
        ) from exc

    # Find the closing ---
    rest = text[3:]
    end_idx = rest.find("\n---")
    if end_idx == -1:
        raise SkillContractError(
            "FRONTMATTER_INVALID",
            "SKILL.md frontmatter closing --- not found",
        )

    fm_text = rest[:end_idx]
    body = rest[end_idx + 4:]  # skip \n---

    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError as exc:
        raise SkillContractError(
            "FRONTMATTER_INVALID",
            f"SKILL.md frontmatter YAML parse error: {exc}",
        ) from exc

    if not isinstance(fm, dict):
        raise SkillContractError(
            "FRONTMATTER_INVALID",
            "SKILL.md frontmatter must be a YAML mapping",
        )

    return fm, body


def inspect_skill_md(
    path: Path, expected_name: str, target: str
) -> list[dict[str, object]]:
    """Verify SKILL.md frontmatter and body against the contract.

    Returns a list of findings.
    """
    findings: list[dict[str, object]] = []

    def err(code: str, message: str, pointer: str = "$") -> None:
        findings.append({
            "severity": "error",
            "dimension": "structure",
            "code": code,
            "location": {"kind": "relative_path", "value": pointer},
            "message": message,
            "evidence": [],
        })

    try:
        fm, body = parse_skill_frontmatter(path.read_text(encoding="utf-8"))
    except SkillContractError as e:
        err(e.code, e.message, str(path))
        return findings

    # Required fields
    name = fm.get("name")
    if not name or not isinstance(name, str):
        err("SKILL_METADATA_MISSING", "SKILL.md frontmatter missing 'name'", "frontmatter/name")
    elif name != expected_name:
        err("SKILL_NAME_MISMATCH",
            f"SKILL.md name '{name}' does not match directory '{expected_name}'",
            "frontmatter/name")

    desc = fm.get("description")
    if not desc or not isinstance(desc, str):
        err("SKILL_DESCRIPTION", "SKILL.md frontmatter missing 'description'", "frontmatter/description")

    # Non-empty body
    if not body.strip():
        err("SKILL_BODY_EMPTY", "SKILL.md body must not be empty", "body")

    # Trigger detection (prose check, not semantic)
    body_lower = body.lower()
    if "trigger" not in body_lower:
        err("TRIGGER_MISSING", "SKILL.md body missing trigger declaration", "body")
    if "non-trigger" not in body_lower and "non_trigger" not in body_lower:
        err("NON_TRIGGER_MISSING", "SKILL.md body missing non-trigger declaration", "body")

    # Target-specific checks
    if target == "bundled-plugin":
        # Must have version, author, license in frontmatter
        for field in ("version", "author", "license"):
            if field not in fm:
                err("SKILL_METADATA_MISSING",
                    f"bundled-plugin SKILL.md requires '{field}' in frontmatter",
                    f"frontmatter/{field}")

    return findings


# ---------------------------------------------------------------------------
# Bundle integrity checks (Task 8)
# ---------------------------------------------------------------------------

def _verify_bundle_integrity(
    manifest: dict[str, object], bundle_root: Path
) -> list[dict[str, object]]:
    """Check that the manifest inventory matches actual filesystem."""
    findings: list[dict[str, object]] = []

    def err(code: str, message: str, pointer: str = "$") -> None:
        findings.append({
            "severity": "error",
            "dimension": "structure",
            "code": code,
            "location": {"kind": "json_pointer", "value": pointer},
            "message": message,
            "evidence": [],
        })

    try:
        actual_records = inventory_bundle(bundle_root)
    except SkillContractError as e:
        err(e.code, e.message)
        return findings

    # Build actual path → record map
    actual_map: dict[str, dict[str, object]] = {str(r["path"]): r for r in actual_records}

    # Collect all manifest-declared paths
    declared_map: dict[str, dict[str, object]] = {}
    bundle = manifest.get("bundle", {})
    smd = bundle.get("skill_md", {})
    if smd:
        declared_map[str(smd.get("path", ""))] = smd
    for cat in ("references", "scripts", "tests", "fixtures", "provenance"):
        for item in bundle.get(cat, []):
            declared_map[str(item.get("path", ""))] = item

    # Check every declared file exists and hashes match
    for path, declared in declared_map.items():
        if not path:
            continue
        actual = actual_map.get(path)
        if actual is None:
            err("FILE_UNLISTED", f"declared file not found on disk: {path}", f"$/bundle/{path}")
            continue
        if actual["sha256"] != declared.get("sha256"):
            err("HASH_MISMATCH",
                f"hash mismatch for {path}: declared={declared.get('sha256')} actual={actual['sha256']}",
                f"$/bundle/{path}")
        if actual["size_bytes"] != declared.get("size_bytes"):
            err("HASH_MISMATCH",
                f"size mismatch for {path}: declared={declared.get('size_bytes')} actual={actual['size_bytes']}",
                f"$/bundle/{path}")

    # Check no undeclared files exist
    for path in actual_map:
        if path not in declared_map:
            err("FILE_MISSING", f"file on disk not declared in manifest: {path}", f"$/bundle")

    # Verify bundle_sha256
    declared_digest = manifest.get("skill", {}).get("bundle_sha256")
    if declared_digest:
        computed = compute_bundle_sha256(actual_records)
        if computed != declared_digest:
            err("HASH_MISMATCH",
                f"bundle_sha256 mismatch: declared={declared_digest} computed={computed}",
                "$/skill/bundle_sha256")

    return findings


def _check_script_syntax(path: Path) -> list[dict[str, object]]:
    """Syntax-check a script without executing it."""
    findings: list[dict[str, object]] = []

    def err(code: str, message: str) -> None:
        findings.append({
            "severity": "error",
            "dimension": "structure",
            "code": code,
            "location": {"kind": "relative_path", "value": str(path)},
            "message": message,
            "evidence": [],
        })

    suffix = path.suffix.lower()
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        err("READ_FAILED", f"cannot read script: {e}")
        return findings

    if suffix == ".py":
        try:
            ast.parse(text)
        except SyntaxError as e:
            err("SCRIPT_SYNTAX", f"Python syntax error: {e}")
    elif suffix == ".json":
        try:
            json.loads(text)
        except json.JSONDecodeError as e:
            err("JSON_INVALID", f"JSON parse error: {e}")
    elif suffix in (".yaml", ".yml"):
        try:
            import yaml
            yaml.safe_load(text)
        except ImportError:
            err("DEPENDENCY_MISSING", "PyYAML required for YAML syntax check")
        except Exception as e:
            err("SCRIPT_SYNTAX", f"YAML parse error: {e}")
    elif suffix == ".toml":
        try:
            tomllib.loads(text)
        except Exception as e:
            err("SCRIPT_SYNTAX", f"TOML parse error: {e}")
    elif suffix in (".sh", ".bash"):
        # Declared but not executed; basic check only
        if not text.strip():
            err("SCRIPT_SYNTAX", "empty shell script")
    else:
        err("SCRIPT_CHECK_UNSUPPORTED", f"unsupported script type: {suffix}")

    return findings


# ---------------------------------------------------------------------------
# Conversion compiler integration (Task 9)
# ---------------------------------------------------------------------------

def _find_compiler() -> Path:
    """Locate the 5qln_compiler.py script."""
    # Look relative to this script's directory
    here = Path(__file__).resolve().parent
    candidates = [
        here.parent.parent / "5qln-converter" / "scripts" / "5qln_compiler.py",
        here.parent.parent.parent / "5qln-converter" / "scripts" / "5qln_compiler.py",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise SkillContractError(
        "DEPENDENCY_MISSING",
        "cannot locate 5qln_compiler.py; run from within the plugin tree",
    )


def run_conversion_compiler(manifest_path: Path) -> dict[str, object]:
    """Re-run the conversion compiler and return its report.

    Never trusts a stored report — always recompiles fresh.
    """
    compiler = _find_compiler()

    with tempfile.TemporaryDirectory() as td:
        report_path = Path(td) / "compiler-report.json"
        result = subprocess.run(
            [sys.executable, str(compiler), str(manifest_path), "--report", str(report_path)],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if report_path.exists():
            try:
                return json.loads(report_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return {
                    "execution_success": False,
                    "exit_code": result.returncode,
                    "stderr": result.stderr,
                    "error": "compiler produced unparseable report",
                }

        return {
            "execution_success": False,
            "exit_code": result.returncode,
            "stderr": result.stderr,
            "error": "compiler did not produce a report file",
        }


# ---------------------------------------------------------------------------
# Main verifier
# ---------------------------------------------------------------------------

def verify_skill(
    manifest_path: Path,
    *,
    promotion_mode: bool = False,
    observations: list[Path] | None = None,
    capability_snapshot: Path | None = None,
) -> dict[str, object]:
    """Run the full skill-v1 verification pipeline.

    Returns a skill-report-v1 dict.
    """
    findings: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []

    def err(code: str, message: str, pointer: str = "$") -> None:
        findings.append({
            "severity": "error",
            "dimension": "structure",
            "code": code,
            "location": {"kind": "json_pointer", "value": pointer},
            "message": message,
            "evidence": [],
        })

    def warn(code: str, message: str) -> None:
        warnings.append({
            "severity": "warning",
            "dimension": "metadata",
            "code": code,
            "location": {"kind": "relative_path", "value": str(manifest_path)},
            "message": message,
            "evidence": [],
        })

    # 1. Load manifest
    manifest: dict[str, object] = {}
    try:
        text = manifest_path.read_text(encoding="utf-8")
        manifest = json.loads(text)
    except FileNotFoundError:
        raise SkillContractError("FILE_MISSING", f"manifest file not found: {manifest_path}", str(manifest_path))
    except json.JSONDecodeError as e:
        err("JSON_INVALID", f"manifest is not valid JSON: {e}")
        return _build_report(manifest_path, {}, findings, warnings, {}, promotion_mode,
                             execution_success=False)

    # 2. Schema validation
    schema_findings = validate_skill_manifest(manifest)
    findings.extend(schema_findings)

    # 3. Determine bundle root
    bundle_root = manifest_path.parent.resolve()

    # 4. SKILL.md inspection
    if bundle_root is not None:
        skill_md_path = bundle_root / "SKILL.md"
        if skill_md_path.exists():
            skill_name = str(manifest.get("skill", {}).get("name", bundle_root.name))
            target = str(manifest.get("promotion", {}).get("target", "local-skill"))
            findings.extend(inspect_skill_md(skill_md_path, skill_name, target))

        # 5. Bundle integrity
        findings.extend(_verify_bundle_integrity(manifest, bundle_root))

        # 6. Script syntax checks
        for cat in ("scripts",):
            for item in manifest.get("bundle", {}).get(cat, []):
                script_path = bundle_root / str(item["path"])
                if script_path.exists():
                    findings.extend(_check_script_syntax(script_path))

    # 7. Conversion compiler
    conversion_report: dict[str, object] = {}
    prov = manifest.get("provenance", {})
    conv_declared = prov.get("conversion_manifest", {})
    conv_path_str = str(conv_declared.get("path", ""))
    if conv_path_str and bundle_root is not None:
        conv_path = bundle_root / conv_path_str
        if conv_path.exists():
            # Verify declared hash
            actual = inspect_regular_file(bundle_root, conv_path_str)
            if actual["sha256"] != conv_declared.get("sha256"):
                err("CONVERSION_HASH",
                    f"conversion manifest hash mismatch",
                    "$/provenance/conversion_manifest")
            conversion_report = run_conversion_compiler(conv_path)
            if not conversion_report.get("execution_success", True):
                err("CONVERSION_FAILED",
                    f"conversion compiler failure: {conversion_report.get('error', 'unknown')}")
        else:
            err("CONVERSION_MISSING", f"conversion manifest not found: {conv_path_str}")

    return _build_report(
        manifest_path, manifest, findings, warnings, conversion_report, promotion_mode
    )


def _build_report(
    manifest_path: Path,
    manifest: dict[str, object],
    findings: list[dict[str, object]],
    warnings: list[dict[str, object]],
    conversion_report: dict[str, object],
    promotion_mode: bool,
    *,
    execution_success: bool = True,
) -> dict[str, object]:
    """Assemble the final skill-report-v1."""
    structural_status = "passed" if not findings else "failed"
    behavioral_status: str = "not_declared"
    attestation_status: str = "open"
    human_review_status: str = str(manifest.get("human_review", {}).get("status", "open"))
    promotion_state: str = str(manifest.get("promotion", {}).get("requested_state", "draft"))
    promotion_ready = False

    if promotion_mode and structural_status == "passed":
        # Check human review
        if human_review_status == "accepted":
            promotion_state = "human_reviewed"
            hr_evidence = manifest.get("human_review", {}).get("evidence", [])
            if hr_evidence:
                attestation_status = "evidence_present"
                promo = manifest.get("promotion", {})
                if promo.get("requested_state") == "promotion_requested":
                    if promo.get("authorization_evidence_ids"):
                        promotion_state = "promotion_ready"
                        promotion_ready = True

    return {
        "format_version": "skill-report-v1",
        "execution_success": execution_success,
        "structural_status": structural_status,
        "behavioral_status": behavioral_status,
        "attestation_status": attestation_status,
        "human_review_status": human_review_status,
        "promotion_state": promotion_state,
        "promotion_ready": promotion_ready,
        "requested_state": manifest.get("promotion", {}).get("requested_state", "draft"),
        "manifest": {
            "path": str(manifest_path.relative_to(manifest_path.parent.parent))
            if manifest_path.is_absolute() else str(manifest_path),
            "sha256": sha256_bytes(canonical_json_bytes(manifest)),
        },
        "subject": {
            "name": str(manifest.get("skill", {}).get("name", "")),
            "bundle_sha256": str(manifest.get("skill", {}).get("bundle_sha256", "")),
            "contract_sha256": str(manifest.get("skill", {}).get("contract_sha256", "")),
        },
        "findings": sorted(
            findings,
            key=lambda f: (str(f.get("code", "")), str(f.get("location", {}).get("value", "")), str(f.get("message", ""))),
        ),
        "warnings": warnings,
        "conversion_report": conversion_report,
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    args = argv[1:] if argv is not None else sys.argv[1:]

    if not args:
        print("Usage: verify_skill.py MANIFEST_PATH [--report PATH] [--promotion-mode] [--overwrite]", file=sys.stderr)
        return 2

    manifest_path = Path(args[0])
    report_path: Path | None = None
    promotion_mode = False
    overwrite = False

    i = 1
    while i < len(args):
        if args[i] == "--report" and i + 1 < len(args):
            report_path = Path(args[i + 1])
            i += 2
        elif args[i] == "--promotion-mode":
            promotion_mode = True
            i += 1
        elif args[i] == "--overwrite":
            overwrite = True
            i += 1
        else:
            print(f"Unknown argument: {args[i]}", file=sys.stderr)
            return 2

    try:
        report = verify_skill(manifest_path, promotion_mode=promotion_mode)
    except SkillContractError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 2

    if report_path:
        try:
            atomic_write_json(report_path, report, overwrite=overwrite)
        except SkillContractError as exc:
            print(f"Error writing report: {exc}", file=sys.stderr)
            return 2

    # Exit code
    structural_ok = report.get("structural_status") == "passed"
    if promotion_mode:
        return 0 if (structural_ok and report.get("promotion_ready")) else 1
    return 0 if structural_ok else 1


if __name__ == "__main__":
    sys.exit(main())
