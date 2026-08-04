"""Safe, deterministic filesystem primitives for skill-v1 formation tools.

No candidate-code execution. No symlink following. Read-once hashing.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

MAX_FILES = 512
MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_TOTAL_BYTES = 50 * 1024 * 1024
MAX_DEPTH = 32

# The sealed 5QLN constitutional kernel: 217 bytes, immutable.
# If kernel.txt drifts from this digest, every downstream verification
# must fail closed. Mirrors fractal_memory.CODEX_SHA256.
CODEX_SHA256 = "feaa46b4147d4e023cdd3fd59c051d063e8ec654ee7b38a481dcd5e4c781859b"
KERNEL_FILE = "kernel.txt"

_EXCLUDED_PATHS: tuple[str, ...] = (
    "skill-formation-manifest.json",
)

_EXCLUDED_PREFIXES: tuple[str, ...] = (
    ".verification/",
)


class SkillContractError(Exception):
    """A deterministic, code-labelled structural error. Never carries AI judgement."""

    def __init__(self, code: str, message: str, path: str | None = None) -> None:
        super().__init__(f"[{code}] {message}" + (f" at {path}" if path else ""))
        self.code = code
        self.message = message
        self.path = path


# ---------------------------------------------------------------------------
# Deterministic serialisation
# ---------------------------------------------------------------------------

def canonical_json_bytes(value: object) -> bytes:
    """Produce stable, sorted, no-whitespace UTF-8 JSON bytes."""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    """Return 64-char lowercase hex SHA-256 digest."""
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Path safety
# ---------------------------------------------------------------------------

def normalize_relative_path(value: str) -> str:
    """Validate and normalise a bundle-relative POSIX path.

    Rejects absolute paths, ``..``, ``.``, backslashes, NUL, empty strings,
    and any path inside the reserved ``.verification/`` prefix.
    """
    if not value or value == ".":
        raise SkillContractError("PATH_INVALID", "path must not be empty or '.'", value)

    if value.startswith("/") or "\\" in value:
        raise SkillContractError("PATH_ESCAPE", "absolute path or backslash rejected", value)

    if "\x00" in value:
        raise SkillContractError("PATH_ESCAPE", "NUL byte rejected", value)

    if value.startswith(".verification/") or value.startswith(".verification"):
        raise SkillContractError("PATH_INVALID", "reserved .verification prefix rejected", value)

    # Normalize multi-slash and check for dot segments
    parts: list[str] = []
    for part in value.split("/"):
        if part in ("", "."):
            raise SkillContractError("PATH_INVALID", "empty or '.' path segment", value)
        if part == "..":
            raise SkillContractError("PATH_ESCAPE", "'..' path segment rejected", value)
        parts.append(part)

    return "/".join(parts)


# ---------------------------------------------------------------------------
# File inspection (read-once)
# ---------------------------------------------------------------------------

def inspect_regular_file(root: Path, relative: str) -> dict[str, object]:
    """Read a regular file once and return its path, size, and SHA-256.

    The file at ``root / relative`` must exist as a regular file (no symlinks,
    no FIFOs, no sockets, no devices).  Returns a dict with keys ``path``,
    ``sha256``, and ``size_bytes``.
    """
    import stat

    normalized = normalize_relative_path(relative)
    full = root / normalized

    # lstat the unresolved path to detect symlinks and non-regular files
    # BEFORE resolving
    try:
        st = full.lstat()
    except FileNotFoundError:
        raise SkillContractError("FILE_MISSING", "file not found", normalized)

    if stat.S_ISLNK(st.st_mode):
        raise SkillContractError("SYMLINK_FORBIDDEN", "symlinks not allowed in bundle", normalized)
    if not stat.S_ISREG(st.st_mode):
        raise SkillContractError(
            "FILE_TYPE_FORBIDDEN",
            f"non-regular file type 0o{st.st_mode:o}",
            normalized,
        )

    if st.st_size > MAX_FILE_BYTES:
        raise SkillContractError(
            "SIZE_LIMIT",
            f"file size {st.st_size} exceeds limit {MAX_FILE_BYTES}",
            normalized,
        )

    # Now resolve to check it's inside the bundle root
    resolved = full.resolve()
    resolved_root = root.resolve()
    if not str(resolved).startswith(str(resolved_root) + os.sep) and resolved != resolved_root:
        raise SkillContractError("PATH_ESCAPE", "path escapes bundle root", normalized)

    data = full.read_bytes()
    return {
        "path": normalized,
        "sha256": sha256_bytes(data),
        "size_bytes": len(data),
    }


# ---------------------------------------------------------------------------
# Bundle inventory
# ---------------------------------------------------------------------------

def _should_exclude(relative: str) -> bool:
    if relative in _EXCLUDED_PATHS:
        return True
    for prefix in _EXCLUDED_PREFIXES:
        if relative.startswith(prefix):
            return True
    return False


def inventory_bundle(root: Path) -> list[dict[str, object]]:
    """Walk *root* and return a sorted list of file records.

    Fixed exclusions: the manifest itself (``skill-formation-manifest.json``)
    and anything under ``.verification/``.  Every other regular file is
    inventoried.  Symlinks, non-regular files, path escapes, case-fold
    collisions, depth, total-byte, and file-count limits are enforced.
    """
    records: list[dict[str, object]] = []
    seen_lower: dict[str, str] = {}
    total_bytes = 0
    resolved_root = root.resolve()

    for dirpath_str, _dirnames, filenames in os.walk(str(root)):
        dirpath = Path(dirpath_str)
        depth = len(dirpath.relative_to(root).parts) if dirpath != root else 0
        if depth > MAX_DEPTH:
            raise SkillContractError(
                "SIZE_LIMIT",
                f"depth {depth} exceeds limit {MAX_DEPTH}",
                str(dirpath.relative_to(root)),
            )

        for fname in filenames:
            if len(records) >= MAX_FILES:
                raise SkillContractError(
                    "SIZE_LIMIT",
                    f"file count exceeds limit {MAX_FILES}",
                )

            full = dirpath / fname
            rel = str(full.relative_to(root))

            if _should_exclude(rel):
                continue

            normalized = normalize_relative_path(rel)

            # Case-fold collision check
            lower = normalized.lower()
            if lower in seen_lower and seen_lower[lower] != normalized:
                raise SkillContractError(
                    "PATH_CASE_COLLISION",
                    f"case-fold collision: {seen_lower[lower]} vs {normalized}",
                    normalized,
                )
            seen_lower[lower] = normalized

            info = inspect_regular_file(root, normalized)
            records.append(info)
            total_bytes += int(info["size_bytes"])

            if total_bytes > MAX_TOTAL_BYTES:
                raise SkillContractError(
                    "SIZE_LIMIT",
                    f"total bytes {total_bytes} exceeds limit {MAX_TOTAL_BYTES}",
                )

    records.sort(key=lambda r: str(r["path"]))
    return records


def compute_bundle_sha256(files: list[dict[str, object]]) -> str:
    """Compute the bundle digest over the sorted file records.

    Uses canonical JSON of ``[{path, sha256, size_bytes}, ...]`` sorted by path
    (already sorted by ``inventory_bundle``).
    """
    return sha256_bytes(canonical_json_bytes(files))


# ---------------------------------------------------------------------------
# Atomic output
# ---------------------------------------------------------------------------

def atomic_write_json(
    path: Path, payload: object, overwrite: bool = False
) -> None:
    """Write *payload* as canonical JSON to *path* atomically.

    If *overwrite* is ``False`` and *path* exists, raise ``SkillContractError``
    with code ``FILE_DUPLICATE``.
    """
    if path.exists() and not overwrite:
        raise SkillContractError(
            "FILE_DUPLICATE",
            "output file already exists; use overwrite=True to replace",
            str(path),
        )

    parent = path.parent
    if not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)

    data = canonical_json_bytes(payload)
    fd, tmp = tempfile.mkstemp(dir=str(parent), prefix=".tmp-", suffix=".json")
    try:
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(tmp, str(path))


# ---------------------------------------------------------------------------
# Strict manifest validation
# ---------------------------------------------------------------------------

def _require_type(value: object, expected: type, pointer: str) -> None:
    if not isinstance(value, expected):
        raise SkillContractError(
            "SCHEMA_TYPE",
            f"expected {expected.__name__} at {pointer}, got {type(value).__name__}",
            pointer,
        )


def _require_object(value: object, pointer: str) -> dict:
    _require_type(value, dict, pointer)
    return value  # type: ignore[return-value]


def _require_string(value: object, pointer: str, *, pattern: str | None = None,
                    min_len: int = 0, max_len: int | None = None) -> str:
    _require_type(value, str, pointer)
    s: str = value  # type: ignore[assignment]
    if min_len and len(s) < min_len:
        raise SkillContractError("SCHEMA_TYPE", f"string too short at {pointer}", pointer)
    if max_len is not None and len(s) > max_len:
        raise SkillContractError("SCHEMA_TYPE", f"string too long at {pointer}", pointer)
    if pattern:
        import re
        if not re.fullmatch(pattern, s):
            raise SkillContractError("SCHEMA_TYPE", f"string does not match pattern at {pointer}", pointer)
    return s


def _require_array(value: object, pointer: str, *, min_items: int = 0) -> list:
    _require_type(value, list, pointer)
    lst: list = value  # type: ignore[assignment]
    if len(lst) < min_items:
        raise SkillContractError("SCHEMA_MISSING", f"array has fewer than {min_items} items at {pointer}", pointer)
    return lst


def _require_exact_keys(value: object, required: set[str], optional: set[str],
                        pointer: str) -> dict:
    obj = _require_object(value, pointer)
    allowed = required | optional
    actual = set(obj.keys())
    missing = required - actual
    if missing:
        raise SkillContractError(
            "SCHEMA_MISSING",
            f"missing required keys {sorted(missing)} at {pointer}",
            pointer,
        )
    extra = actual - allowed
    if extra:
        raise SkillContractError(
            "SCHEMA_EXTRA",
            f"unknown keys {sorted(extra)} at {pointer}",
            pointer,
        )
    return obj


_ID_PATTERN = r"^[A-Z][A-Z0-9_-]{1,63}$"
_SHA256_PATTERN = r"^[0-9a-f]{64}$"
_SKILL_NAME_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
_STATEMENT_MAX = 2000


def _check_id(value: object, pointer: str) -> str:
    return _require_string(value, pointer, pattern=_ID_PATTERN)


def _check_sha256(value: object, pointer: str) -> str:
    return _require_string(value, pointer, pattern=_SHA256_PATTERN)


def _check_skill_name(value: object, pointer: str) -> str:
    s = _require_string(value, pointer, max_len=64)
    import re
    if not re.fullmatch(_SKILL_NAME_PATTERN, s):
        raise SkillContractError("SCHEMA_TYPE", f"invalid skill name at {pointer}", pointer)
    return s


def _check_statement(value: object, pointer: str) -> str:
    return _require_string(value, pointer, min_len=1, max_len=_STATEMENT_MAX)


def _check_relative_path(value: object, pointer: str) -> str:
    s = _require_string(value, pointer, min_len=1, max_len=500)
    try:
        return normalize_relative_path(s)
    except SkillContractError:
        raise SkillContractError("PATH_INVALID", f"invalid relative path at {pointer}", pointer)


def _check_file(value: object, pointer: str) -> dict:
    obj = _require_exact_keys(value, {"path", "sha256", "size_bytes"}, set(), pointer)
    _check_relative_path(obj["path"], f"{pointer}/path")
    _check_sha256(obj["sha256"], f"{pointer}/sha256")
    _require_type(obj["size_bytes"], int, f"{pointer}/size_bytes")
    if not (0 <= obj["size_bytes"] <= MAX_FILE_BYTES):
        raise SkillContractError("SIZE_LIMIT", f"size_bytes out of range at {pointer}", pointer)
    return obj


def _check_files(value: object, pointer: str) -> list:
    arr = _require_array(value, pointer)
    for i, item in enumerate(arr):
        _check_file(item, f"{pointer}/{i}")
    return arr


def _check_evidence_file(value: object, pointer: str) -> dict:
    obj = _require_exact_keys(value, {"path", "sha256", "size_bytes"}, set(), pointer)
    s = _require_string(obj["path"], f"{pointer}/path", min_len=1, max_len=500)
    if not s.startswith(".verification/evidence/"):
        raise SkillContractError("PATH_INVALID", f"evidence path must start with .verification/evidence/ at {pointer}", pointer)
    _check_sha256(obj["sha256"], f"{pointer}/sha256")
    return obj


def _check_contract_items(value: object, pointer: str) -> list:
    arr = _require_array(value, pointer)
    for i, item in enumerate(arr):
        obj = _require_exact_keys(item, {"id", "statement"}, set(), f"{pointer}/{i}")
        _check_id(obj["id"], f"{pointer}/{i}/id")
        _check_statement(obj["statement"], f"{pointer}/{i}/statement")
    return arr


_SEMANTIC_AUTHORSHIP_VALUES = ("H", "K", "PENDING")


def _check_semantic_contract_items(value: object, pointer: str) -> list:
    """Validate trigger/non-trigger items, which must declare authorship.

    ASMA Pillar III: the semantic boundary (what the skill is for, what it
    refuses) must carry an authorship declaration. The verifier enforces
    presence and vocabulary; it cannot verify the truth of the declaration.
    """
    arr = _require_array(value, pointer)
    for i, item in enumerate(arr):
        obj = _require_exact_keys(item, {"id", "statement", "authorship"}, set(), f"{pointer}/{i}")
        _check_id(obj["id"], f"{pointer}/{i}/id")
        _check_statement(obj["statement"], f"{pointer}/{i}/statement")
        authorship = obj.get("authorship")
        if authorship not in _SEMANTIC_AUTHORSHIP_VALUES:
            raise SkillContractError(
                "SCHEMA_ENUM",
                f"authorship must be one of {list(_SEMANTIC_AUTHORSHIP_VALUES)}",
                f"{pointer}/{i}/authorship",
            )
    return arr


def validate_skill_manifest(payload: object) -> list[dict[str, object]]:
    """Validate a skill-v1 manifest against the published contract.

    Returns a list of finding dicts, stable-sorted by (code, path, message).
    An empty list means structural conformance per the published schema.
    """
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
        obj = _require_object(payload, "$")
    except SkillContractError as e:
        err(e.code, e.message, "$")
        return findings

    # Top-level keys
    try:
        root = _require_exact_keys(
            obj,
            {"format_version", "title", "skill", "provenance", "bundle",
             "contract", "requirement_traceability", "behavioral_fixtures",
             "human_review", "promotion"},
            {"axis_attestation"},
            "$",
        )
    except SkillContractError as e:
        err(e.code, e.message, "$")
        return findings

    # format_version
    if root.get("format_version") != "skill-v1":
        err("SCHEMA_VERSION", "format_version must be 'skill-v1'", "$/format_version")

    # axis_attestation (loop mode standing direction — optional, validated when present)
    axis = root.get("axis_attestation")
    if axis is not None:
        try:
            ax = _require_exact_keys(
                axis, {"direction", "sha256", "source"}, set(), "$/axis_attestation"
            )
            _require_string(ax.get("direction"), "$/axis_attestation/direction", min_len=1, max_len=2000)
            _check_sha256(ax.get("sha256"), "$/axis_attestation/sha256")
            _require_string(ax.get("source"), "$/axis_attestation/source", min_len=1, max_len=300)
        except SkillContractError as e:
            err(e.code, e.message, e.path or "$/axis_attestation")

    # title
    try:
        _require_string(root.get("title"), "$/title", min_len=1, max_len=200)
    except SkillContractError as e:
        err(e.code, e.message, e.path or "$/title")

    # skill
    try:
        skill = _require_exact_keys(
            root.get("skill"),
            {"name", "bundle_root", "bundle_sha256", "contract_sha256"},
            set(),
            "$/skill",
        )
        _check_skill_name(skill.get("name"), "$/skill/name")
        if skill.get("bundle_root") != ".":
            err("SCHEMA_ENUM", "bundle_root must be '.'", "$/skill/bundle_root")
        _check_sha256(skill.get("bundle_sha256"), "$/skill/bundle_sha256")
        _check_sha256(skill.get("contract_sha256"), "$/skill/contract_sha256")
    except SkillContractError as e:
        err(e.code, e.message, e.path or "$/skill")

    # provenance
    try:
        prov = _require_exact_keys(
            root.get("provenance"),
            {"conversion_manifest", "formation_evidence"},
            set(),
            "$/provenance",
        )
        _check_file(prov.get("conversion_manifest"), "$/provenance/conversion_manifest")
        evidence = _require_array(prov.get("formation_evidence"), "$/provenance/formation_evidence")
        for i, item in enumerate(evidence):
            ev = _require_exact_keys(
                item, {"id", "kind", "file", "authority"}, set(),
                f"$/provenance/formation_evidence/{i}",
            )
            _check_id(ev.get("id"), f"$/provenance/formation_evidence/{i}/id")
            if ev.get("kind") not in ("phase_log", "human_record", "prior_report", "other"):
                err("SCHEMA_ENUM", f"invalid kind at $/provenance/formation_evidence/{i}/kind")
            _check_file(ev.get("file"), f"$/provenance/formation_evidence/{i}/file")
            if ev.get("authority") != "evidence-only":
                err("SCHEMA_ENUM", f"authority must be 'evidence-only' at $/provenance/formation_evidence/{i}/authority")
    except SkillContractError as e:
        err(e.code, e.message, e.path or "$/provenance")

    # bundle
    try:
        bundle = _require_exact_keys(
            root.get("bundle"),
            {"skill_md", "references", "scripts", "tests", "fixtures", "provenance"},
            set(),
            "$/bundle",
        )
        _check_file(bundle.get("skill_md"), "$/bundle/skill_md")
        for cat in ("references", "scripts", "tests", "fixtures", "provenance"):
            _check_files(bundle.get(cat), f"$/bundle/{cat}")
        if bundle.get("skill_md", {}).get("path") != "SKILL.md":
            err("FILE_CATEGORY", "skill_md.path must be 'SKILL.md'", "$/bundle/skill_md/path")
    except SkillContractError as e:
        err(e.code, e.message, e.path or "$/bundle")

    # contract
    try:
        contract = _require_exact_keys(
            root.get("contract"),
            {"triggers", "non_triggers", "behavioral_requirements",
             "completion_criteria", "claimed_tools", "related_skills"},
            set(),
            "$/contract",
        )
        _check_semantic_contract_items(contract.get("triggers"), "$/contract/triggers")
        _check_semantic_contract_items(contract.get("non_triggers"), "$/contract/non_triggers")
        _check_contract_items(contract.get("completion_criteria"), "$/contract/completion_criteria")

        breqs = _require_array(contract.get("behavioral_requirements"), "$/contract/behavioral_requirements")
        for i, br in enumerate(breqs):
            bro = _require_exact_keys(
                br, {"id", "statement", "verification"}, set(),
                f"$/contract/behavioral_requirements/{i}",
            )
            _check_id(bro.get("id"), f"$/contract/behavioral_requirements/{i}/id")
            _check_statement(bro.get("statement"), f"$/contract/behavioral_requirements/{i}/statement")
            if bro.get("verification") not in ("static", "observed", "human"):
                err("SCHEMA_ENUM", f"invalid verification at $/contract/behavioral_requirements/{i}/verification")

        tools = _require_array(contract.get("claimed_tools"), "$/contract/claimed_tools")
        for i, t in enumerate(tools):
            to = _require_exact_keys(
                t, {"name", "provider", "required"}, set(),
                f"$/contract/claimed_tools/{i}",
            )
            _require_string(to.get("name"), f"$/contract/claimed_tools/{i}/name", max_len=128)
            if to.get("provider") not in ("5qln-plugin", "hermes", "bundle", "external"):
                err("SCHEMA_ENUM", f"invalid provider at $/contract/claimed_tools/{i}/provider")
            _require_type(to.get("required"), bool, f"$/contract/claimed_tools/{i}/required")

        skills = _require_array(contract.get("related_skills"), "$/contract/related_skills")
        for i, s in enumerate(skills):
            so = _require_exact_keys(
                s, {"name", "provider", "required"}, set(),
                f"$/contract/related_skills/{i}",
            )
            _check_skill_name(so.get("name"), f"$/contract/related_skills/{i}/name")
            if so.get("provider") not in ("5qln-plugin", "hermes", "external"):
                err("SCHEMA_ENUM", f"invalid provider at $/contract/related_skills/{i}/provider")
            _require_type(so.get("required"), bool, f"$/contract/related_skills/{i}/required")
    except SkillContractError as e:
        err(e.code, e.message, e.path or "$/contract")

    # requirement_traceability
    try:
        traces = _require_array(root.get("requirement_traceability"), "$/requirement_traceability")
        for i, tr in enumerate(traces):
            tro = _require_exact_keys(
                tr,
                {"requirement_id", "class", "statement", "basis_source_unit_ids",
                 "basis_derived_insight_ids", "skill_sections", "verifier_checks", "fixture_ids"},
                set(),
                f"$/requirement_traceability/{i}",
            )
            _check_id(tro.get("requirement_id"), f"$/requirement_traceability/{i}/requirement_id")
            if tro.get("class") not in ("source", "derived", "proposal"):
                err("SCHEMA_ENUM", f"invalid class at $/requirement_traceability/{i}/class")
            _check_statement(tro.get("statement"), f"$/requirement_traceability/{i}/statement")
            for field in ("basis_source_unit_ids", "basis_derived_insight_ids"):
                arr = _require_array(tro.get(field), f"$/requirement_traceability/{i}/{field}")
                for j, sid in enumerate(arr):
                    _require_string(sid, f"$/requirement_traceability/{i}/{field}/{j}", min_len=1, max_len=128)
            sects = _require_array(tro.get("skill_sections"), f"$/requirement_traceability/{i}/skill_sections", min_items=1)
            for j, sec in enumerate(sects):
                _require_string(sec, f"$/requirement_traceability/{i}/skill_sections/{j}",
                                pattern=r"^#[A-Za-z0-9._~-]+$")
            checks = _require_array(tro.get("verifier_checks"), f"$/requirement_traceability/{i}/verifier_checks", min_items=1)
            for j, chk in enumerate(checks):
                _require_string(chk, f"$/requirement_traceability/{i}/verifier_checks/{j}",
                                pattern=r"^[A-Z][A-Z0-9_-]{2,63}$")
            fids = _require_array(tro.get("fixture_ids"), f"$/requirement_traceability/{i}/fixture_ids")
            for j, fid in enumerate(fids):
                _check_id(fid, f"$/requirement_traceability/{i}/fixture_ids/{j}")
    except SkillContractError as e:
        err(e.code, e.message, e.path or "$/requirement_traceability")

    # behavioral_fixtures
    try:
        fixs = _require_array(root.get("behavioral_fixtures"), "$/behavioral_fixtures")
        for i, fix in enumerate(fixs):
            fo = _require_exact_keys(
                fix, {"id", "class", "spec", "required"}, set(),
                f"$/behavioral_fixtures/{i}",
            )
            _check_id(fo.get("id"), f"$/behavioral_fixtures/{i}/id")
            allowed_classes = {
                "positive_trigger", "near_miss_non_trigger",
                "human_attestation_boundary", "q_phase_skip_resistance",
                "missing_context_open_behavior", "removal_test", "mutation",
            }
            if fo.get("class") not in allowed_classes:
                err("SCHEMA_ENUM", f"invalid fixture class at $/behavioral_fixtures/{i}/class")
            _check_file(fo.get("spec"), f"$/behavioral_fixtures/{i}/spec")
            _require_type(fo.get("required"), bool, f"$/behavioral_fixtures/{i}/required")
    except SkillContractError as e:
        err(e.code, e.message, e.path or "$/behavioral_fixtures")

    # human_review
    try:
        hr = _require_exact_keys(
            root.get("human_review"),
            {"status", "reviewer", "evidence"},
            set(),
            "$/human_review",
        )
        if hr.get("status") not in ("open", "changes_requested", "accepted"):
            err("SCHEMA_ENUM", "invalid human_review status", "$/human_review/status")
        rev = hr.get("reviewer")
        if rev is not None:
            _require_string(rev, "$/human_review/reviewer", max_len=200)
        ev = _require_array(hr.get("evidence"), "$/human_review/evidence")
        for i, eitem in enumerate(ev):
            eo = _require_exact_keys(
                eitem,
                {"id", "kind", "statement", "source", "location",
                 "scope_bundle_sha256", "scope_contract_sha256", "promotion_scope"},
                set(),
                f"$/human_review/evidence/{i}",
            )
            _check_id(eo.get("id"), f"$/human_review/evidence/{i}/id")
            if eo.get("kind") not in ("review_acceptance", "promotion_authorization"):
                err("SCHEMA_ENUM", f"invalid evidence kind at $/human_review/evidence/{i}/kind")
            _check_statement(eo.get("statement"), f"$/human_review/evidence/{i}/statement")
            _check_evidence_file(eo.get("source"), f"$/human_review/evidence/{i}/source")
            _require_string(eo.get("location"), f"$/human_review/evidence/{i}/location", min_len=1, max_len=300)
            _check_sha256(eo.get("scope_bundle_sha256"), f"$/human_review/evidence/{i}/scope_bundle_sha256")
            _check_sha256(eo.get("scope_contract_sha256"), f"$/human_review/evidence/{i}/scope_contract_sha256")
            if eo.get("promotion_scope") not in ("local", "bundled", "external"):
                err("SCHEMA_ENUM", f"invalid promotion_scope at $/human_review/evidence/{i}/promotion_scope")
    except SkillContractError as e:
        err(e.code, e.message, e.path or "$/human_review")

    # promotion
    try:
        promo = _require_exact_keys(
            root.get("promotion"),
            {"requested_state", "target", "authorization_evidence_ids"},
            set(),
            "$/promotion",
        )
        if promo.get("requested_state") not in ("draft", "review_requested", "promotion_requested", "withdrawn"):
            err("SCHEMA_ENUM", "invalid requested_state", "$/promotion/requested_state")
        if promo.get("target") not in ("local-skill", "bundled-plugin", "external-bundle"):
            err("SCHEMA_ENUM", "invalid promotion target", "$/promotion/target")
        auth_ids = _require_array(promo.get("authorization_evidence_ids"), "$/promotion/authorization_evidence_ids")
        for i, aid in enumerate(auth_ids):
            _check_id(aid, f"$/promotion/authorization_evidence_ids/{i}")
    except SkillContractError as e:
        err(e.code, e.message, e.path or "$/promotion")

    findings.sort(key=lambda f: (str(f["code"]), str(f.get("location", {}).get("value", "")), str(f["message"])))
    return findings
