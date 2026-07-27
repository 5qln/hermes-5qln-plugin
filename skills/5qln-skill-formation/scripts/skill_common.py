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
