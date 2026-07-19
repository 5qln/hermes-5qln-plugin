# Conversion manifest

Use a manifest for substantial, reusable, regulated, implementation-facing, or file-based conversions. The manifest is the deterministic bridge between semantic conversion and compiler verification.

## Required top-level fields

```json
{
  "format_version": "1.0",
  "title": "Converted artifact title",
  "constitution": {},
  "lens_notation_version": "literal-v1",
  "source": {},
  "attestations": [],
  "document_cell": {},
  "cells": [],
  "lens_audit": [],
  "traceability": [],
  "derived_insights": [],
  "open_questions": [],
  "completion": {}
}
```

Create a scaffold with `scripts/new_manifest.py`; do not hand-copy the constitutional block.

## Status vocabulary

Use only:

- question/resonance/return: `open`, `candidate`, `attested` or `human-recognized` where the field permits;
- lens audit: `used`, `released`, `not_applicable`, `not_reviewed`;
- conversion completion: `open`, `candidate`, `complete`;
- traceability: Boolean `preserved` plus explicit output references.

`complete` requires evidence of human attestation for X and Z/value alignment, a non-empty B, B'', and return question, and a human-recognized return. A K-only converter should normally emit `candidate` or `open`.

## Source units

```json
{
  "id": "SRC-0001",
  "kind": "paragraph",
  "text": "...",
  "sha256": "...",
  "source_file": "input.docx",
  "location": "body/paragraph[1]",
  "parent_id": null,
  "original_id": null,
  "priority": null,
  "normative": false,
  "warnings": []
}
```

## Attestations

```json
{
  "type": "X",
  "evidence": "Exact human statement or stable source reference",
  "source_unit_ids": ["SRC-0003"]
}
```

Allowed types: `X`, `Z`, `value`, `constitution`, `return`.

## Document cell

Every phase object must exist and carry its canonical status/output fields. The scaffold shows the exact keys the compiler expects.

## Converted cells

```json
{
  "address": "QG",
  "lens": "Q",
  "parent": "G",
  "parent_equation": "G = α ≡ {α'}",
  "parent_target": "Y",
  "source_unit_ids": ["SRC-0010"],
  "formation": {
    "S": "...",
    "G": "...",
    "Q": "...",
    "P": "...",
    "V": "..."
  },
  "domain_items": ["REQ-01"],
  "evidence": ["..."],
  "guards": ["L4"]
}
```

## Lens audit

Include exactly 25 entries. Under `literal-v1`, the first address character is `lens` and the second is `parent`. A `released` or `not_applicable` entry requires a reason; this prevents both omission and forced L4 depth.

## Traceability

Every source unit must have at least one traceability entry:

```json
{
  "source_unit_id": "SRC-0010",
  "primary_cell": "QG",
  "secondary_cells": [],
  "output_refs": ["section-3.2"],
  "preserved": true,
  "note": "Normative wording retained verbatim"
}
```

## Derived insights

Every insight needs a non-empty basis:

```json
{
  "id": "DER-001",
  "text": "...",
  "basis_source_unit_ids": ["SRC-0010", "SRC-0014"],
  "basis_constitution": ["G = α ≡ {α'}"],
  "status": "derived"
}
```

## Completion

```json
{
  "status": "candidate",
  "benefit": "...",
  "artifact": "path or artifact identity",
  "return_question": "... ?",
  "return_status": "candidate",
  "removal_test": "What materially fails when the grammar is removed"
}
```

The return question must end as a real question, not a summary with punctuation attached.
