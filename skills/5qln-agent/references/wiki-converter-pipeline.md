# Converter Pipeline — Lessons from First Execution

**Session:** 2026-07-20 — FCF book conversion (274 source units, 81KB)

## Pipeline Steps

```
1. fiveqln_inventory_source  → source-inventory.json (atomic SHA-256 ledger)
2. fiveqln_create_manifest   → conversion-manifest.json (scaffold, 25 lens checks)
3. Semantic conversion       → fill document_cell, attestations, traceability, completion
4. fiveqln_compile_manifest  → compiler-report.json (pass/fail + errors)
```

## Manifest Schema — Critical Field Names

The compiler is strict. Field names must match `references/manifest.md` exactly:

### document_cell.S
- `authority` — who supplied the source and what authority was granted
- `question` — the inquiry or conversion aim
- `X` — the validated spark (one sentence)
- `x_status` — `open` | `candidate` | `attested`

### document_cell.G
- `alpha` — the irreducible pattern
- `expressions` — ARRAY of {alpha'} echoes (NOT `alpha_echoes`)
- `Y` — validated pattern output
- `y_status` — `open` | `candidate` | `validated` (NOT `attested`)

### document_cell.Q
- `phi` — self-nature / direct perception
- `omega` — universal potential
- `Z` — resonant key
- `z_status` — `open` | `candidate` | `attested`

### document_cell.P
- `energy_map` — ARRAY of strings (high/low energy points)
- `value_map` — ARRAY of strings (high/low value points)
- `gradient` — the ∇ (REQUIRED — separate from `A`)
- `A` — flow direction
- `a_status` — `open` | `candidate` | `validated`

### document_cell.V
- `local` — L: what crystallized here (NOT `L`)
- `global` — G: what propagates (NOT `G_global`)
- `benefit` — B: fulfillment + propagation (NOT `B`)
- `artifact` — B'': the artifact reference (NOT `B_double_prime`)
- `return_question` — ∞0'
- `return_status` — `open` | `candidate` | `human-recognized`
- `removal_test` — what fails when grammar is removed

## Common Compiler Errors and Fixes

### SYMBOL_DRIFT — Typographic primes (U+2032)
The manifest scaffold may contain smart quotes in source text. Replace all `\u2032` with ASCII `'` and `\u2033` with `''` before compilation.

### MISSING / EMPTY — Required fields
Every phase in document_cell has specific required fields. Common misses:
- `P.gradient` (separate from `P.A`)
- `G.expressions` as array (not string)
- `V.local` / `V.global` / `V.benefit` / `V.artifact` (not L / G_global / B / B_double_prime)

### STATUS — Invalid status value
- G-phase `y_status`: only `open`, `candidate`, `validated` (NOT `attested`)
- V-phase `return_status`: `open`, `candidate`, `human-recognized`

### TRACE_CELL — Unknown primary cell
Every traceability entry's `primary_cell` must reference an address (e.g., "SS", "QG") that has a corresponding entry in the `cells[]` array. Setting all to "SS" fails unless an SS cell exists.

### LENS_CELL — Used lens has no converted cell
When lens audit entries are marked `used`, the compiler expects a corresponding entry in `cells[]`. Mark unused lenses `released` with a reason instead.

## Conversion Strategy for Large Documents

For a 274-unit book, full per-unit holographic conversion is substantial work:

**Strategy A: Artifact-level only (candidate)** — Fill `document_cell`, release all lenses, accept `candidate` completion. Appropriate for first-pass conversion.

**Strategy B: Full holographic (complete)** — Assign all units to lens addresses, create cells[], map traceability per-unit. Appropriate for training data or formal publication.

A `failed` compilation with honest errors is a valid result. The report IS the deliverable — it surfaces what a full conversion requires.
