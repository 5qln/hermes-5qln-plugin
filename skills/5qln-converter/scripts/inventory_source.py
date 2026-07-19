#!/usr/bin/env python3
"""Extract source artifacts into an atomic, hash-addressed preservation ledger."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ID_RE = re.compile(r"^\s*([A-Z][A-Z0-9]{0,7}-\d{1,5})\b")
PRIORITY_RE = re.compile(r"\[(P\d+)\]")
NORMATIVE_RE = re.compile(r"\b(SHALL|MUST|SHALL NOT|MUST NOT)\b", re.IGNORECASE)
LIST_RE = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


class Inventory:
    def __init__(self) -> None:
        self.units: list[dict[str, Any]] = []
        self.sources: list[dict[str, Any]] = []
        self.warnings: list[str] = []

    def add_unit(
        self,
        *,
        kind: str,
        text: str,
        source_file: str,
        location: str,
        parent_id: str | None = None,
        warnings: list[str] | None = None,
    ) -> str | None:
        if not text or not text.strip():
            return None
        value = text.strip()
        unit_id = f"SRC-{len(self.units) + 1:04d}"
        original_match = ID_RE.match(value)
        priority_match = PRIORITY_RE.search(value)
        unit = {
            "id": unit_id,
            "kind": kind,
            "text": value,
            "sha256": sha256_text(value),
            "source_file": source_file,
            "location": location,
            "parent_id": parent_id,
            "original_id": original_match.group(1) if original_match else None,
            "priority": priority_match.group(1) if priority_match else None,
            "normative": bool(NORMATIVE_RE.search(value)),
            "warnings": list(warnings or []),
        }
        self.units.append(unit)
        return unit_id

    def add_source(self, path: Path, warnings: list[str] | None = None) -> None:
        raw = path.read_bytes()
        self.sources.append(
            {
                "path": str(path.resolve()),
                "file_name": path.name,
                "suffix": path.suffix.lower(),
                "size_bytes": len(raw),
                "sha256": sha256_bytes(raw),
                "warnings": list(warnings or []),
            }
        )


def flush_paragraph(
    inventory: Inventory,
    buffer: list[str],
    source_file: str,
    location: str,
    parent_id: str | None,
) -> None:
    if buffer:
        inventory.add_unit(
            kind="paragraph",
            text="\n".join(buffer),
            source_file=source_file,
            location=location,
            parent_id=parent_id,
        )
        buffer.clear()


def inventory_text(path: Path, inventory: Inventory, markdown: bool = False) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    buffer: list[str] = []
    paragraph_no = 0
    heading_stack: dict[int, str] = {}
    current_parent: str | None = None

    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", stripped) if markdown else None
        if heading_match:
            paragraph_no += 1
            flush_paragraph(
                inventory,
                buffer,
                path.name,
                f"paragraph[{paragraph_no}]",
                current_parent,
            )
            level = len(heading_match.group(1))
            parent = heading_stack.get(level - 1)
            heading_id = inventory.add_unit(
                kind="heading",
                text=heading_match.group(2),
                source_file=path.name,
                location=f"line[{line_no}]",
                parent_id=parent,
            )
            if heading_id:
                heading_stack[level] = heading_id
                for old_level in [value for value in heading_stack if value > level]:
                    del heading_stack[old_level]
                current_parent = heading_id
            continue

        if not stripped:
            paragraph_no += 1
            flush_paragraph(
                inventory,
                buffer,
                path.name,
                f"paragraph[{paragraph_no}]",
                current_parent,
            )
            continue

        if LIST_RE.match(line):
            paragraph_no += 1
            flush_paragraph(
                inventory,
                buffer,
                path.name,
                f"paragraph[{paragraph_no}]",
                current_parent,
            )
            inventory.add_unit(
                kind="list_item",
                text=LIST_RE.sub("", line, count=1),
                source_file=path.name,
                location=f"line[{line_no}]",
                parent_id=current_parent,
            )
            continue

        buffer.append(line)

    paragraph_no += 1
    flush_paragraph(
        inventory,
        buffer,
        path.name,
        f"paragraph[{paragraph_no}]",
        current_parent,
    )


def iter_docx_blocks(document: Any) -> Iterable[Any]:
    from docx.document import Document as DocumentType
    from docx.oxml.ns import qn
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    if not isinstance(document, DocumentType):
        raise TypeError("Expected python-docx Document")
    parent_element = document.element.body
    for child in parent_element.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, document)
        elif child.tag == qn("w:tbl"):
            yield Table(child, document)


def inventory_docx(path: Path, inventory: Inventory) -> None:
    try:
        from docx import Document
        from docx.table import Table
        from docx.text.paragraph import Paragraph
    except ImportError as exc:
        raise RuntimeError("DOCX extraction requires python-docx") from exc

    doc = Document(path)
    heading_stack: dict[int, str] = {}
    current_parent: str | None = None
    paragraph_no = 0
    table_no = 0

    for block in iter_docx_blocks(doc):
        if isinstance(block, Paragraph):
            text = block.text.strip()
            if not text:
                continue
            paragraph_no += 1
            style_name = block.style.name if block.style is not None else ""
            heading_match = re.match(r"Heading\s+(\d+)", style_name or "")
            if heading_match:
                level = int(heading_match.group(1))
                parent = heading_stack.get(level - 1)
                heading_id = inventory.add_unit(
                    kind="heading",
                    text=text,
                    source_file=path.name,
                    location=f"body/paragraph[{paragraph_no}]",
                    parent_id=parent,
                )
                if heading_id:
                    heading_stack[level] = heading_id
                    for old_level in [value for value in heading_stack if value > level]:
                        del heading_stack[old_level]
                    current_parent = heading_id
            else:
                kind = "list_item" if block._p.pPr is not None and block._p.pPr.numPr is not None else "paragraph"
                inventory.add_unit(
                    kind=kind,
                    text=text,
                    source_file=path.name,
                    location=f"body/paragraph[{paragraph_no}]",
                    parent_id=current_parent,
                )
        elif isinstance(block, Table):
            table_no += 1
            for row_no, row in enumerate(block.rows, start=1):
                values = [" ".join(cell.text.split()) for cell in row.cells]
                inventory.add_unit(
                    kind="table_row",
                    text=" | ".join(values),
                    source_file=path.name,
                    location=f"body/table[{table_no}]/row[{row_no}]",
                    parent_id=current_parent,
                )


def inventory_pdf(path: Path, inventory: Inventory) -> list[str]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("PDF extraction requires pypdf") from exc

    warnings = ["PDF text extraction is linear; visually inspect layout, tables, and diagrams."]
    reader = PdfReader(path)
    for page_no, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
        if len(paragraphs) <= 1:
            paragraphs = [line.strip() for line in text.splitlines() if line.strip()]
        for part_no, paragraph in enumerate(paragraphs, start=1):
            inventory.add_unit(
                kind="pdf_text",
                text=paragraph,
                source_file=path.name,
                location=f"page[{page_no}]/block[{part_no}]",
                warnings=["Verify against rendered page."],
            )
    return warnings


def inventory_csv(path: Path, inventory: Inventory, delimiter: str = ",") -> None:
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        reader = csv.reader(handle, delimiter=delimiter)
        for row_no, row in enumerate(reader, start=1):
            inventory.add_unit(
                kind="table_row",
                text=" | ".join(row),
                source_file=path.name,
                location=f"row[{row_no}]",
            )


def inventory_json(path: Path, inventory: Inventory) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        for index, (key, value) in enumerate(data.items(), start=1):
            inventory.add_unit(
                kind="json_item",
                text=json.dumps({key: value}, ensure_ascii=False, sort_keys=True),
                source_file=path.name,
                location=f"top_level[{index}]/{key}",
            )
    elif isinstance(data, list):
        for index, value in enumerate(data, start=1):
            inventory.add_unit(
                kind="json_item",
                text=json.dumps(value, ensure_ascii=False, sort_keys=True),
                source_file=path.name,
                location=f"item[{index}]",
            )
    else:
        inventory.add_unit(
            kind="json_value",
            text=json.dumps(data, ensure_ascii=False),
            source_file=path.name,
            location="root",
        )


def process(path: Path, inventory: Inventory) -> None:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(path)
    suffix = path.suffix.lower()
    source_warnings: list[str] = []
    if suffix in {".md", ".markdown"}:
        inventory_text(path, inventory, markdown=True)
    elif suffix in {".txt", ".rst", ".log"}:
        inventory_text(path, inventory, markdown=False)
    elif suffix == ".docx":
        inventory_docx(path, inventory)
    elif suffix == ".pdf":
        source_warnings.extend(inventory_pdf(path, inventory))
    elif suffix in {".csv", ".tsv"}:
        inventory_csv(path, inventory, delimiter="\t" if suffix == ".tsv" else ",")
    elif suffix == ".json":
        inventory_json(path, inventory)
    else:
        raise ValueError(f"Unsupported source type: {suffix or '<none>'}")
    inventory.add_source(path, source_warnings)
    inventory.warnings.extend(f"{path.name}: {warning}" for warning in source_warnings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="+", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--compact", action="store_true", help="Write compact JSON")
    args = parser.parse_args()

    inventory = Inventory()
    try:
        for source in args.sources:
            process(source, inventory)
    except Exception as exc:
        print(f"inventory error: {exc}", file=sys.stderr)
        return 2

    kinds: dict[str, int] = {}
    priorities: dict[str, int] = {}
    original_ids: list[str] = []
    for unit in inventory.units:
        kinds[unit["kind"]] = kinds.get(unit["kind"], 0) + 1
        if unit["priority"]:
            priorities[unit["priority"]] = priorities.get(unit["priority"], 0) + 1
        if unit["original_id"]:
            original_ids.append(unit["original_id"])

    payload = {
        "format_version": "1.0",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "sources": inventory.sources,
        "units": inventory.units,
        "summary": {
            "source_count": len(inventory.sources),
            "unit_count": len(inventory.units),
            "kinds": kinds,
            "priorities": priorities,
            "original_id_count": len(original_ids),
            "unique_original_id_count": len(set(original_ids)),
        },
        "warnings": inventory.warnings,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=None if args.compact else 2) + "\n",
        encoding="utf-8",
    )
    print(f"inventory: {len(inventory.units)} units from {len(inventory.sources)} source(s) -> {args.out}")
    if inventory.warnings:
        print(f"warnings: {len(inventory.warnings)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
