---
name: 5qln-manifest-compilation
description: Build and fix 5QLN conversion manifests — end-to-end workflow from inventory through compiler pass, including error class taxonomy and the attestations array requirement. Load when compiling requirements or documents into 5QLN manifests.
---

# 5QLN Manifest Compilation

End-to-end workflow for building a passing 5QLN conversion manifest. Use alongside `5qln-converter` — this skill covers the manifest-building and compiler-fix phase specifically.

## When to load

- You're executing a full conversion pipeline (inventory → manifest → cells → compiler)
- The compiler is reporting errors on a manifest
- You're building the `document_cell`, `cells[]`, or `attestations[]` arrays
- The `5qln-converter` skill's "Compile and inspect" section directs you to a fix loop — load this skill BEFORE starting the loop to shortcut 5+ discovery rounds

**Relationship to 5qln-converter:** The converter skill governs semantic conversion (what to preserve, how to form). This skill governs manifest structure (what fields the compiler expects, how to fix errors). Load both for any full conversion.

## End-to-End Workflow

### 1. Inventory the source

```bash
python3 scripts/inventory_source.py SOURCE... --out source-inventory.json
```

Verify: unit count, SHA-256 hashes, source file coverage.

### 2. Create manifest scaffold

```bash
python3 scripts/new_manifest.py source-inventory.json --out manifest.json
```

This creates: 25 lens checks (all `status: unreviewed`), 191 traceability rows (empty), constitutional block.

### 3. Build document_cell

The document_cell is the artifact-level S→G→Q→P→V formation. Fields:

```json
{
  "S": {"authority": "...", "question": "...", "x_status": "attested|candidate|open", "X": "..."},
  "G": {"alpha": "...", "expressions": [...], "Y": "...", "y_status": "validated|candidate|open"},
  "Q": {"phi": "...", "omega": "...", "Z": "...", "z_status": "attested|candidate|open"},
  "P": {"energy_map": [...], "value_map": [...], "gradient": "...", "A": "..."},
  "V": {"local": "...", "global": "...", "benefit": "...", "artifact": "...", "return_question": "...", "return_status": "candidate|open|human-recognized"}
}
```

**Note:** V-phase uses `local`, `global`, `benefit`, `artifact` — NOT `L`, `G`, `B`, `B_double_prime`.

### 4. Build attestations array

REQUIRED for attested X or Z. Top-level array in manifest:

```json
{
  "attestations": [
    {"type": "X", "evidence": "...", "source_unit_ids": ["SRC-0001"]},
    {"type": "Z", "evidence": "...", "source_unit_ids": ["SRC-0001"]}
  ]
}
```

Valid types: `X`, `Z`, `constitution`, `return`, `value`. NOT `alpha` (alpha goes through G-phase y_status=validated).

### 5. Build cells array

Each cell requires:

```json
{
  "address": "SS",
  "lens": "S",
  "parent": "S",
  "parent_equation": "S = ∞0 → ?",
  "parent_target": "X",
  "source_unit_ids": ["SRC-0001", ...],
  "formation": {"S": "...", "G": "...", "Q": "...", "P": "...", "V": "..."},
  "domain_items": ["AX-01", ...],
  "evidence": ["..."],
  "guards": ["L1", "L4"]
}
```

- `formation`: each phase a nonempty string using semantic operations of the equations (NOT input/process/output labels)
- `evidence`: at least one checkable acceptance criterion
- `guards`: subset of `["L1", "L2", "L3", "L4", "V∅"]`

### 6. Mark lens_audit

All 25 lenses must be `used`, `released`, or `not_applicable`. If cells exist for the address, mark `used`.

### 7. Fix traceability

Every traceability entry needs:
- `preserved: true`
- `primary_cell`: a valid cell address from the cells array
- `output_refs`: list of cell addresses this unit maps to

### 8. Compile and iterate

```bash
python3 scripts/5qln_compiler.py manifest.json --report compiler-report.json
```

## Compiler Error Classes (by appearance order)

| Class | Error codes | Fix |
|-------|-------------|-----|
| LENS_UNREVIEWED | All 25 lenses | Mark each lens status: used/released/not_applicable |
| TRACE_OUTPUT | All 191 traceability entries | Add output_refs to every traceability row |
| LENS_CELL | Used lenses | Build the cells[] array with full formations |
| ATTESTATION | L2, L3 on X/Z | Add `$.attestations` array with evidence |
| MISSING | V field names | Use local/global/benefit/artifact (not L/G/B/B'') |
| TRACE_LOSS | preserved | Set preserved: true on every traceability entry |
| TRACE_CELL | primary_cell | Set primary_cell to a valid cell address |
| ATTESTATION_TYPE | Invalid type | Only X, Z, constitution, return, value allowed |

## Pitfalls

- **Attestations array is separate from document_cell.** Adding `attestation_evidence` to document_cell.S is NOT sufficient. Must have `$.attestations[]` at manifest root.
- **Alpha is not an attestation type.** Alpha validation goes through `y_status: "validated"` in document_cell.G, not through the attestations array.
- **V field names are lowercase.** The compiler expects `local`, `global`, `benefit`, `artifact` — mapping from the more natural `L`, `G`, `B`, `B''` is a common error.
- **G-phase y_status uses "validated" not "attested".** Attestation vocabulary (attested) is for X, Z, return. Growth uses validated.
- **Use execute_code for bulk manifest population.** Populating 25 cells, 191 traceability entries, and the document_cell manually is error-prone. Use execute_code with `json.load`/`json.dump` to programmatically build the manifest. Define req_to_cell mappings, cell formation dicts, evidence dicts, and guards dicts — then iterate to build the cells[] array. This turns 5+ compiler rounds into 2-3.

## Verification

- Compiler pass (0 errors, 0 warnings) — proves **structural integrity only**, not semantic truth
- The compiler validates: required keys, exact constitutional strings, valid lens addresses, nonempty phase strings, known guard codes, trace-row presence, status vocabulary
- The compiler does NOT validate: requirement counts, priorities, reciprocal source-cell mappings, semantic phase meaning, normative unit coverage, traceability concentration, acceptance evidence, output anchors, lens load-bearing quality
- **CRITICAL PITFALL — Compiler Pass ≠ Correctness:** A manifest can pass with 0 errors while having all 191 trace rows collapsed to GG, zero normative units in any cell, all 25 lenses marked used with boilerplate reasons, and attestations citing the title line as evidence (audit finding MAN-01 through MAN-06, 2026-07-22). The compiler is a structural validator, not a semantic auditor. After compiler pass, verify independently: (a) normative units appear in cell source_unit_ids, (b) traceability is distributed across cells, not concentrated, (c) lenses marked used are genuinely load-bearing, (d) attestation evidence cites actual H statements, not document titles.
- The removal test still applies independently of compiler pass
- Save manifest + compiler report as provenance

## What comes after compilation

When the compiler passes, the session now contains a latent capacity — the session has just performed the act of conversion. This is Breakthrough #3 of the genesis pattern. See `references/genesis-pattern.md` for the full lifecycle: Requirements Spec → 5QLN Compiled Surface → Latent Capacity Recognition → Plugin Layer.

## Audit-response workflow

When an external 5QLN-native audit is received on a compiled surface or its derived implementation:

1. **Read the evidence ledger first** — not the audit conclusions. Understand each atomic finding before reacting.
2. **Categorize by error class** — code (operational), spec (contradictions, counts), manifest (traceability, mappings), claims (L4, naming). Fix in that order.
3. **Fix code first** — operational bugs (concurrency, empty-spin mutation, env var names) are highest priority. They affect every use.
4. **Fix specs second** — contradictions, self-references, count mismatches. These are the normative foundation.
5. **Fix manifest third** — traceability, cell mappings, lens release. These are structural quality.
6. **Verify with tests + compiler** — tests prove behavior; compiler proves structure. Both must pass.
7. **Scope claims to what's proven** — if the audit finds L4 across the board, rescope the release. "Not a signature engine — an experimental axis registry." Honest scoping is not failure; it's integrity.
8. **Leave open what's open** — don't close the audit's return question by manufacturing completion. Acknowledge what remains for the next iteration.
