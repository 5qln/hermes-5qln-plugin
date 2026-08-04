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
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path
from typing import Any

from skill_common import (
    CODEX_SHA256,
    KERNEL_FILE,
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
# Constitutional kernel seal (ASMA Pillar I)
# ---------------------------------------------------------------------------

def _plugin_root() -> Path:
    """Locate the plugin root from this script's own location.

    verify_skill.py lives at skills/5qln-skill-formation/scripts/.
    The plugin root is four parents up (scripts -> 5qln-skill-formation ->
    skills -> plugin root).
    """
    return Path(__file__).resolve().parents[3]


def _kernel_path(plugin_root: Path | None = None) -> Path:
    """Resolve kernel.txt inside the plugin tree."""
    root = plugin_root if plugin_root is not None else _plugin_root()
    return root / KERNEL_FILE


def _verify_kernel_seal(kernel_path: Path | None = None) -> list[dict[str, object]]:
    """Verify kernel.txt matches the sealed constitutional digest.

    Fail closed: any drift from CODEX_SHA256 is a fatal structural finding.
    A missing kernel.txt is likewise fatal — a verifier that cannot see the
    kernel cannot certify structure as constitutionally bounded.
    """
    path = kernel_path if kernel_path is not None else _kernel_path()
    findings: list[dict[str, object]] = []

    def err(code: str, message: str) -> None:
        findings.append({
            "severity": "error",
            "dimension": "constitution",
            "code": code,
            "location": {"kind": "relative_path", "value": str(path)},
            "message": message,
            "evidence": [],
        })

    if not path.is_file():
        err("SEAL_MISSING", f"kernel file not found: {path}")
        return findings

    try:
        actual = sha256_bytes(path.read_bytes())
    except OSError as exc:
        err("SEAL_UNREADABLE", f"cannot read kernel file: {exc}")
        return findings

    if actual != CODEX_SHA256:
        err("SEAL_DRIFT", f"kernel seal drift: expected {CODEX_SHA256[:16]}…, got {actual[:16]}…")

    return findings


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
# Requirement traceability (Task 10)
# ---------------------------------------------------------------------------

def _verify_requirement_traceability(
    manifest: dict[str, object], conversion_report: dict[str, object]
) -> list[dict[str, object]]:
    """Check every requirement maps to sections, verifiers, and fixtures."""
    findings: list[dict[str, object]] = []
    traces = manifest.get("requirement_traceability", [])

    def err(code: str, msg: str, ptr: str = "$") -> None:
        findings.append({
            "severity": "error", "dimension": "structure", "code": code,
            "location": {"kind": "json_pointer", "value": ptr}, "message": msg, "evidence": [],
        })

    requirement_ids = set()
    fixture_ids = {str(f.get("id", "")) for f in manifest.get("behavioral_fixtures", [])}
    behavioral_reqs = {
        str(r.get("id", "")): r
        for r in manifest.get("contract", {}).get("behavioral_requirements", [])
    }

    for i, tr in enumerate(traces):
        base = f"$/requirement_traceability/{i}"
        rid = str(tr.get("requirement_id", ""))

        if rid in requirement_ids:
            err("REQUIREMENT_DUPLICATE", f"duplicate requirement_id: {rid}", f"{base}/requirement_id")
        requirement_ids.add(rid)

        req_class = str(tr.get("class", ""))
        if req_class == "source":
            if not tr.get("basis_source_unit_ids"):
                err("REQUIREMENT_BASIS", f"source requirement {rid} missing basis_source_unit_ids", base)
            if tr.get("basis_derived_insight_ids"):
                err("SOURCE_CLASS_INVALID", f"source requirement {rid} must have empty derived basis", base)
        elif req_class == "derived":
            if not (tr.get("basis_source_unit_ids") or tr.get("basis_derived_insight_ids")):
                err("REQUIREMENT_BASIS", f"derived requirement {rid} missing basis", base)
        elif req_class == "proposal":
            if tr.get("basis_source_unit_ids") or tr.get("basis_derived_insight_ids"):
                err("SOURCE_CLASS_INVALID", f"proposal {rid} should have empty basis unless extending", base)

        if not tr.get("skill_sections"):
            err("SECTION_MISSING", f"requirement {rid} has no skill_sections", f"{base}/skill_sections")
        if not tr.get("verifier_checks"):
            err("REQUIREMENT_UNMAPPED", f"requirement {rid} has no verifier_checks", f"{base}/verifier_checks")

        # Fixture resolution
        for fid in tr.get("fixture_ids", []):
            if str(fid) not in fixture_ids:
                err("FIXTURE_UNRESOLVED", f"fixture {fid} not declared", f"{base}/fixture_ids")

        # Check behavioral requirement mapping
        if rid in behavioral_reqs:
            br = behavioral_reqs[rid]
            verif = str(br.get("verification", ""))
            if verif == "observed" and not tr.get("fixture_ids"):
                err("FIXTURE_UNRESOLVED", f"observed requirement {rid} has no fixtures", f"{base}/fixture_ids")

    # Check all behavioral requirements have trace rows
    for brid in behavioral_reqs:
        if brid not in requirement_ids:
            err("REQUIREMENT_UNMAPPED", f"behavioral requirement {brid} has no traceability row", "$/contract")

    # 5QLN boundary: S→G→Q→P→V order from conversion report
    if conversion_report:
        cells = conversion_report.get("cells", [])
        if cells:
            phase_order_ok = _check_phase_order(cells)
            if not phase_order_ok:
                err("FORMATION_ORDER", "conversion cell phase order deviates from S→G→Q→P→V")

        # Return is question-bearing
        doc_cell = conversion_report.get("document_cell", {})
        v_phase = doc_cell.get("V", {})
        return_q = str(v_phase.get("return_question", ""))
        if return_q and not return_q.strip().endswith("?"):
            err("RETURN_NOT_QUESTION", "V-phase return must be question-bearing")

    return findings


def _check_phase_order(cells: list) -> bool:
    """Check that cell addresses follow S→G→Q→P→V ordering."""
    phase_order = {"S": 0, "G": 1, "Q": 2, "P": 3, "V": 4}
    last_phase = -1
    for cell in cells:
        addr = str(cell.get("address", ""))
        if len(addr) >= 1 and addr[0] in phase_order:
            current = phase_order[addr[0]]
            if current < last_phase:
                return False
            last_phase = current
    return True


def _verify_section_anchors(manifest: dict[str, object], skill_md_path: Path) -> list[dict[str, object]]:
    """Verify that declared skill_sections resolve to headings in SKILL.md."""
    findings: list[dict[str, object]] = []
    text = skill_md_path.read_text(encoding="utf-8")

    # Extract headings from SKILL.md
    import re
    headings = set()
    for line in text.splitlines():
        m = re.match(r"^(#{1,6})\s+(.+)$", line)
        if m:
            slug = "#" + re.sub(r"[^A-Za-z0-9._~-]+", "-", m.group(2).strip().lower())
            headings.add(slug)

    traces = manifest.get("requirement_traceability", [])
    for i, tr in enumerate(traces):
        for sec in tr.get("skill_sections", []):
            if str(sec) not in headings:
                findings.append({
                    "severity": "error", "dimension": "structure", "code": "SECTION_MISSING",
                    "location": {"kind": "json_pointer", "value": f"$/requirement_traceability/{i}/skill_sections"},
                    "message": f"section anchor '{sec}' not found in SKILL.md", "evidence": [],
                })

    return findings


# ---------------------------------------------------------------------------
# Capability resolution (Task 11)
# ---------------------------------------------------------------------------

def _resolve_capabilities(
    manifest: dict[str, object], capability_snapshot: Path | None
) -> list[dict[str, object]]:
    """Resolve claimed tools and skills against available capabilities."""
    findings: list[dict[str, object]] = []

    def err(code: str, msg: str, ptr: str = "$") -> None:
        findings.append({
            "severity": "error", "dimension": "structure", "code": code,
            "location": {"kind": "json_pointer", "value": ptr}, "message": msg, "evidence": [],
        })

    # If no snapshot provided, external capabilities are unresolved
    snapshot: dict[str, object] = {}
    if capability_snapshot and capability_snapshot.exists():
        try:
            snapshot = json.loads(capability_snapshot.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            err("JSON_INVALID", "capability snapshot unreadable")

    available_tools = set(snapshot.get("tools", []))
    available_skills = set(snapshot.get("skills", []))

    # Check claimed tools
    for i, tool in enumerate(manifest.get("contract", {}).get("claimed_tools", [])):
        name = str(tool.get("name", ""))
        provider = str(tool.get("provider", ""))
        required = tool.get("required", False)

        if provider == "hermes":
            if required and name not in available_tools and capability_snapshot:
                err("TOOL_UNRESOLVED", f"required Hermes tool '{name}' not in snapshot",
                    f"$/contract/claimed_tools/{i}")

    # Check related skills
    for i, skill in enumerate(manifest.get("contract", {}).get("related_skills", [])):
        name = str(skill.get("name", ""))
        provider = str(skill.get("provider", ""))
        required = skill.get("required", False)

        if provider in ("5qln-plugin", "hermes"):
            if required and name not in available_skills and capability_snapshot:
                err("SKILL_UNRESOLVED", f"required skill '{name}' not in snapshot",
                    f"$/contract/related_skills/{i}")

    return findings


# ---------------------------------------------------------------------------
# Behavioral fixture parsing (Task 13)
# ---------------------------------------------------------------------------

def _parse_behavioral_fixtures(
    manifest: dict[str, object], bundle_root: Path | None
) -> list[dict[str, object]]:
    """Validate fixture declarations structurally."""
    findings: list[dict[str, object]] = []

    def err(code: str, msg: str, ptr: str = "$") -> None:
        findings.append({
            "severity": "error", "dimension": "structure", "code": code,
            "location": {"kind": "json_pointer", "value": ptr}, "message": msg, "evidence": [],
        })

    fixtures = manifest.get("behavioral_fixtures", [])
    seen_ids = set()
    required_classes = {
        "positive_trigger", "near_miss_non_trigger",
        "human_attestation_boundary", "q_phase_skip_resistance",
        "missing_context_open_behavior", "removal_test",
    }

    for i, fix in enumerate(fixtures):
        fid = str(fix.get("id", ""))
        fclass = str(fix.get("class", ""))
        base = f"$/behavioral_fixtures/{i}"

        if fid in seen_ids:
            err("FIXTURE_UNRESOLVED", f"duplicate fixture id: {fid}", f"{base}/id")
        seen_ids.add(fid)

        # Verify spec file exists
        if bundle_root:
            spec_path = str(fix.get("spec", {}).get("path", ""))
            if spec_path:
                full = bundle_root / spec_path
                if not full.exists():
                    err("FILE_MISSING", f"fixture spec not found: {spec_path}", f"{base}/spec")

        # Mutation fixtures must have a mutation field
        if fclass == "mutation":
            # Checked by schema validation; additional structural check
            pass

    return findings


# ---------------------------------------------------------------------------
# Observed-run ingestion (Task 14)
# ---------------------------------------------------------------------------

def _ingest_observed_runs(
    manifest: dict[str, object], observation_paths: list[Path]
) -> tuple[str, list[dict[str, object]]]:
    """Ingest and validate behavioral observation records.

    Returns (behavioral_status, findings).
    """
    findings: list[dict[str, object]] = []

    def err(code: str, msg: str, ptr: str = "$") -> None:
        findings.append({
            "severity": "error", "dimension": "behavioral", "code": code,
            "location": {"kind": "json_pointer", "value": ptr}, "message": msg, "evidence": [],
        })

    fixtures = manifest.get("behavioral_fixtures", [])
    if not fixtures:
        return "not_declared", findings

    if not observation_paths:
        return "not_observed", findings

    bundle_sha256 = str(manifest.get("skill", {}).get("bundle_sha256", ""))

    passed = 0
    failed = 0

    for obs_path in observation_paths:
        if not obs_path.exists():
            err("OBSERVATION_INPUT", f"observation file not found: {obs_path}")
            failed += 1
            continue

        try:
            obs = json.loads(obs_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            err("JSON_INVALID", f"observation not valid JSON: {obs_path}")
            failed += 1
            continue

        # Check bundle digest scope
        if obs.get("bundle_sha256") != bundle_sha256:
            err("OBSERVATION_HASH", f"observation bundle digest mismatch: {obs_path}")
            failed += 1
            continue

        # Check fixture reference
        fixture_sha = obs.get("fixture_sha256", "")
        fixture_match = any(
            str(f.get("spec", {}).get("sha256", "")) == fixture_sha
            for f in fixtures
        )
        if not fixture_match:
            err("OBSERVATION_HASH", f"observation fixture_sha256 unrecognized: {obs_path}")
            failed += 1
            continue

        # Check results
        results = obs.get("results", [])
        for r in results:
            if r.get("status") == "pass":
                passed += 1
            else:
                failed += 1

    if failed and not passed:
        return "observed_failed", findings
    elif failed and passed:
        return "observed_mixed", findings
    elif passed:
        return "observed_passed", findings
    return "not_observed", findings


# ---------------------------------------------------------------------------
# Human review evidence (Task 15)
# ---------------------------------------------------------------------------

def _verify_human_review(
    manifest: dict[str, object], bundle_root: Path | None
) -> list[dict[str, object]]:
    """Verify human review evidence scope and presence."""
    findings: list[dict[str, object]] = []

    def err(code: str, msg: str, ptr: str = "$") -> None:
        findings.append({
            "severity": "error", "dimension": "human", "code": code,
            "location": {"kind": "json_pointer", "value": ptr}, "message": msg, "evidence": [],
        })

    hr = manifest.get("human_review", {})
    status = str(hr.get("status", "open"))
    bundle_sha256 = str(manifest.get("skill", {}).get("bundle_sha256", ""))

    if status == "accepted":
        reviewer = hr.get("reviewer")
        if not reviewer:
            err("HUMAN_EVIDENCE_MISSING", "accepted review has no reviewer", "$/human_review/reviewer")

        evidence = hr.get("evidence", [])
        if not evidence:
            err("HUMAN_EVIDENCE_MISSING", "accepted review has no evidence", "$/human_review/evidence")
        else:
            for i, ev in enumerate(evidence):
                # Scope check
                ev_scope = str(ev.get("scope_bundle_sha256", ""))
                if ev_scope != bundle_sha256:
                    err("HUMAN_EVIDENCE_SCOPE",
                        f"evidence scope digest mismatch at evidence/{i}",
                        f"$/human_review/evidence/{i}/scope_bundle_sha256")

                # Source file existence
                if bundle_root:
                    src_path = str(ev.get("source", {}).get("path", ""))
                    if src_path:
                        full = bundle_root / src_path
                        if not full.exists():
                            err("HUMAN_EVIDENCE_MISSING",
                                f"evidence source not found: {src_path}",
                                f"$/human_review/evidence/{i}/source")

    return findings


def _verify_axis_attestation(
    manifest: dict[str, object], *, loop_mode: bool = False
) -> list[dict[str, object]]:
    """Enforce the standing-direction gate for loop mode.

    In loop mode H does not stop every iteration. Instead the loop verifies
    against the centrifuged axis: H's original direction, recorded verbatim
    with a SHA-256 self-check. The axis IS the standing H authority.

    - axis_attestation present + direction hash matches  -> the loop may run
    - absent in loop mode                                -> AXIS_MISSING (fatal)
    - direction hash drift                               -> AXIS_DRIFT (fatal)
    - not loop mode                                      -> informational only
    """
    findings: list[dict[str, object]] = []

    def err(code: str, msg: str, ptr: str = "$") -> None:
        findings.append({
            "severity": "error", "dimension": "constitution", "code": code,
            "location": {"kind": "json_pointer", "value": ptr}, "message": msg, "evidence": [],
        })

    axis = manifest.get("axis_attestation")
    if not isinstance(axis, dict):
        if loop_mode:
            err("AXIS_MISSING", "loop mode requires an axis_attestation (the centrifuged H direction)")
        return findings

    direction = str(axis.get("direction", ""))
    declared = str(axis.get("sha256", ""))
    if not direction.strip():
        err("AXIS_EMPTY", "axis_attestation.direction must be non-empty", "$/axis_attestation/direction")
        return findings

    actual = hashlib.sha256(direction.encode("utf-8")).hexdigest()
    if declared != actual:
        err("AXIS_DRIFT",
            f"axis direction hash drift: declared={declared[:16]}… computed={actual[:16]}…",
            "$/axis_attestation/sha256")

    return findings


def _verify_semantic_authorship(
    manifest: dict[str, object], *, loop_mode: bool = False
) -> list[dict[str, object]]:
    """Enforce ASMA Pillar III: semantic boundaries must be H-originated or H-accepted.

    Every trigger/non-trigger declares authorship:
      - "H"        -> pass (H is the authority; the machine verifies the
                      declaration, never the truth)
      - "K"        -> pass ONLY if human_review carries digest-scoped
                      review_acceptance evidence (H accepted machine-drafted
                      semantics); otherwise GHOST_ORIGINATION
      - "PENDING"  -> unresolved semantic boundary; fail closed
    """
    findings: list[dict[str, object]] = []

    def err(code: str, msg: str, ptr: str = "$") -> None:
        findings.append({
            "severity": "error", "dimension": "human", "code": code,
            "location": {"kind": "json_pointer", "value": ptr}, "message": msg, "evidence": [],
        })

    contract = manifest.get("contract", {})
    semantic_items = list(contract.get("triggers", [])) + list(contract.get("non_triggers", []))
    if not semantic_items:
        return findings

    bundle_sha256 = str(manifest.get("skill", {}).get("bundle_sha256", ""))
    hr = manifest.get("human_review", {})
    accepted_scoped = [
        ev for ev in hr.get("evidence", [])
        if ev.get("kind") == "review_acceptance"
        and str(ev.get("scope_bundle_sha256", "")) == bundle_sha256
    ]

    # Loop mode: a valid centrifuged axis attestation IS the standing H direction.
    # K-authored semantics may run within it without per-iteration human evidence.
    axis_valid = False
    if loop_mode:
        axis_findings = _verify_axis_attestation(manifest, loop_mode=True)
        axis_valid = not axis_findings

    for i, item in enumerate(semantic_items):
        authorship = str(item.get("authorship", "PENDING"))
        item_id = str(item.get("id", f"item/{i}"))
        if authorship == "H":
            continue
        if authorship == "PENDING":
            err("SEMANTIC_AUTHORSHIP_PENDING",
                f"semantic boundary '{item_id}' has unresolved authorship (PENDING)", f"$/contract")
            continue
        if authorship == "K" and not accepted_scoped and not axis_valid:
            err("GHOST_ORIGINATION",
                f"machine-authored semantic boundary '{item_id}' lacks digest-scoped H acceptance evidence",
                f"$/contract")

    return findings

def _verify_return_question_recorded(changelog_path: Path) -> list[dict[str, object]]:
    """Enforce line 8 (No V without ∞0'): a promotion changelog must record a
    return question. A missing changelog, or one without a question-bearing
    return marker, is a V∅ dead-ending.
    """
    findings: list[dict[str, object]] = []

    def err(code: str, msg: str) -> None:
        findings.append({
            "severity": "error", "dimension": "promotion", "code": code,
            "location": {"kind": "relative_path", "value": str(changelog_path)},
            "message": msg, "evidence": [],
        })

    if not changelog_path.is_file():
        err("DEAD_ENDING", f"promotion requires CHANGELOG.md with a recorded return question (∞0'); not found: {changelog_path}")
        return findings

    try:
        text = changelog_path.read_text(encoding="utf-8")
    except OSError as exc:
        err("DEAD_ENDING", f"cannot read CHANGELOG.md: {exc}")
        return findings

    # Return-question markers: the ∞0' glyph, or an explicit return-question heading
    has_return = ("∞0'" in text) or ("return question" in text.lower()) or ("Return Question" in text)
    if not has_return:
        err("DEAD_ENDING", "promotion changelog records no return question (∞0'); line 8 violated")

    return findings


def _inspect_promotion_readiness(
    manifest: dict[str, object], bundle_root: Path | None
) -> list[dict[str, object]]:
    """Inspect promotion readiness for bundled-plugin targets."""
    findings: list[dict[str, object]] = []

    def err(code: str, msg: str, ptr: str = "$") -> None:
        findings.append({
            "severity": "error", "dimension": "promotion", "code": code,
            "location": {"kind": "json_pointer", "value": ptr}, "message": msg, "evidence": [],
        })

    promo = manifest.get("promotion", {})
    target = str(promo.get("target", ""))

    if target != "bundled-plugin":
        return findings

    # Line 8 (No V without ∞0'): the promotion changelog must record a return question.
    findings.extend(_verify_return_question_recorded(_plugin_root() / "CHANGELOG.md"))

    hr = manifest.get("human_review", {})
    if hr.get("status") != "accepted":
        err("PROMOTION_UNAUTHORIZED", "promotion requires accepted human review",
            "$/human_review/status")

    auth_ids = promo.get("authorization_evidence_ids", [])
    if not auth_ids:
        err("PROMOTION_UNAUTHORIZED", "no promotion authorization evidence",
            "$/promotion/authorization_evidence_ids")
    else:
        evidence_ids = {str(e.get("id", "")) for e in hr.get("evidence", [])}
        for aid in auth_ids:
            if str(aid) not in evidence_ids:
                err("PROMOTION_UNAUTHORIZED",
                    f"authorization evidence {aid} not found in human review",
                    "$/promotion/authorization_evidence_ids")

    # Check requested state
    if promo.get("requested_state") != "promotion_requested":
        err("PROMOTION_UNAUTHORIZED",
            "requested_state must be 'promotion_requested' for promotion mode",
            "$/promotion/requested_state")

    return findings

# ---------------------------------------------------------------------------
# Main verifier
# ---------------------------------------------------------------------------

def verify_skill(
    manifest_path: Path,
    *,
    promotion_mode: bool = False,
    loop_mode: bool = False,
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

    # 0. Constitutional kernel seal (ASMA Pillar I) — fail closed
    findings.extend(_verify_kernel_seal())

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

    # 8. Requirement traceability (Task 10)
    findings.extend(_verify_requirement_traceability(manifest, conversion_report))

    # 9. Section anchor resolution in SKILL.md
    if bundle_root is not None:
        skill_md_path = bundle_root / "SKILL.md"
        if skill_md_path.exists():
            findings.extend(_verify_section_anchors(manifest, skill_md_path))

    # 10. Capability resolution (Task 11)
    findings.extend(_resolve_capabilities(manifest, capability_snapshot))

    # 11. Behavioral fixture parsing (Task 13)
    findings.extend(_parse_behavioral_fixtures(manifest, bundle_root))

    # 12. Observed-run ingestion (Task 14)
    behavioral_status, obs_findings = _ingest_observed_runs(manifest, observations or [])
    findings.extend(obs_findings)

    # 13. Human review evidence checks (Task 15)
    findings.extend(_verify_human_review(manifest, bundle_root))

    # 13a. Semantic authorship provenance (ASMA Pillar III)
    findings.extend(_verify_semantic_authorship(manifest, loop_mode=loop_mode))

    # 13b. Loop-mode axis attestation (standing H direction, no per-iteration stop)
    if loop_mode:
        findings.extend(_verify_axis_attestation(manifest, loop_mode=True))

    # 14. Promotion inspection (Task 16)
    promotion_findings = []
    if promotion_mode:
        promotion_findings = _inspect_promotion_readiness(manifest, bundle_root)
        findings.extend(promotion_findings)

    return _build_report(
        manifest_path, manifest, findings, warnings, conversion_report,
        promotion_mode, behavioral_status=behavioral_status,
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
    behavioral_status: str = "not_declared",
) -> dict[str, object]:
    """Assemble the final skill-report-v1."""
    structural_status = "passed" if not findings else "failed"
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
    loop_mode = False
    overwrite = False
    observations: list[Path] = []

    i = 1
    while i < len(args):
        if args[i] == "--report" and i + 1 < len(args):
            report_path = Path(args[i + 1])
            i += 2
        elif args[i] == "--promotion-mode":
            promotion_mode = True
            i += 1
        elif args[i] == "--loop-mode":
            loop_mode = True
            i += 1
        elif args[i] == "--observations":
            # Consume one or more observation JSON paths until the next flag
            j = i + 1
            while j < len(args) and not args[j].startswith("--"):
                observations.append(Path(args[j]))
                j += 1
            i = j
        elif args[i] == "--overwrite":
            overwrite = True
            i += 1
        else:
            print(f"Unknown argument: {args[i]}", file=sys.stderr)
            return 2

    try:
        report = verify_skill(manifest_path, promotion_mode=promotion_mode, loop_mode=loop_mode,
                              observations=observations)
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
