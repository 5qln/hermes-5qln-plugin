# Compiler Error-Fixing Loop

When the compiler reports errors on a manifest, expect an iterative fix loop. This reference documents the pattern discovered during the first full pipeline execution (FCF book conversion, July 2026).

## The Loop Pattern

```
compile → inspect errors → identify error class → fix all instances → recompile
```

Never fix errors one at a time. Each compilation round should address an entire error CLASS. This minimizes rounds.

## Error Classes (in order of typical appearance)

### Class 1: Symbol Drift (SYMBOL_DRIFT)
Typographic primes (U+2032, U+2033) in source unit texts or manifest fields.
- **Detection:** Compiler reports "Typographic prime U+2032 found; use ASCII apostrophe"
- **Source:** Usually in source document text (book content with curly quotes/smart quotes)
- **Fix:** Replace all U+2032, U+2033, U+2018, U+2019, U+201C, U+201D with ASCII equivalents. Sanitize ALL fields — document_cell, cells[].formation, AND source.units[].text.
- **After fix:** Recompute SHA-256 hashes for any source units whose text changed.

### Class 2: Schema Mismatch (MISSING, TYPE, STATUS)
Field names don't match the manifest specification.
- **Reference:** `references/manifest.md` has the exact schema. Read it before filling.
- **Common mistakes:** `y_status: "attested"` → should be `"validated"`. Missing `gradient`, `energy_map`, `value_map`, `local`, `global`, `benefit`, `artifact` fields.

### Class 3: Hash Mismatch (SOURCE_HASH)
- **Detection:** "Hash does not match source unit text"
- **Fix:** Recompute SHA-256 for every modified source unit.

### Class 4: Cell Reference Errors (CELL_REF, TRACE_CELL, LENS_CELL)
- **Fix:** Read actual source unit IDs from `manifest["source"]["units"]`. Map by index range. Set `primary_cell` to valid cell addresses in `manifest["cells"]`.

### Class 5: Target Mismatch (TARGET)
- **Fix:** Use exact canonical output strings. V-phase parent_target is `B+B''+∞0'`.

## Typical Round Count

| Round | Errors | Class | Remaining |
|-------|--------|-------|-----------|
| 1 | 317 | Schema + drift + refs | 276 |
| 2 | 276 | Schema + cells + trace | 12 |
| 3 | 12 | Source IDs + target | 1 |
| 4 | 1 | Deep symbol drift | 2 |
| 5 | 2 | Hash mismatch | 0 |

**Key insight:** Don't aim for perfection in round 1. Fix error classes, not individual errors. Each round surfaces a new class. Trust the loop.

## After PASS
- PASS proves structural integrity — not semantic truth.
- Keep manifest + compiler report as provenance.
- The removal test still applies.
