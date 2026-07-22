# Converter Pipeline — Execution Notes

Learned from the first live converter run (FCF Book, session 2026-07-20). The converter pipeline is: inventory → manifest scaffold → semantic conversion → compile.

## Step-by-step

### 1. Inventory (`fiveqln_inventory_source`)
- Pass absolute source paths and an output path
- Produces: `source-inventory.json` with SHA-256 hashes for every source unit
- Know the unit count before proceeding — it determines traceability scale

### 2. Manifest scaffold (`fiveqln_create_manifest`)
- Pass the inventory path, output path, and a title
- Produces: `conversion-manifest.json` with 274 traceability rows and 25 lens audit entries
- All traceability rows start with `primary_cell: null` — must be filled during semantic conversion
- All lens audit entries start as `not_reviewed` — must be set to `used`, `released`, or `not_applicable`

### 3. Semantic conversion (manual, via script)
The compiler expects exact field names. Key schema requirements learned from failures:

**Document cell fields:**
- `S`: `authority`, `question`, `X`, `x_status` (values: open | candidate | attested)
- `G`: `alpha`, `expressions` (array), `Y`, `y_status` (values: open | candidate | validated — NOT "attested")
- `Q`: `phi`, `omega`, `Z`, `z_status` (values: open | candidate | attested)
- `P`: `energy_map` (array), `value_map` (array), `gradient`, `A`, `a_status`
- `V`: `local`, `global`, `benefit`, `artifact`, `return_question`, `return_status`, `removal_test`

**Cells array:** Each `used` lens audit entry needs a corresponding cell in `cells[]` with:
- `address`: two-letter lens address (e.g., "SS", "GG")
- `lens`, `parent`, `parent_equation`, `parent_target` (must match the phase — VV expects `B+B''+∞0'`)
- `source_unit_ids`: array of valid source unit IDs from the inventory
- `formation`: nested S/G/Q/P/V descriptions
- `domain_items`, `evidence`, `guards`

**Traceability:** Every source unit needs `primary_cell` set to a valid two-letter address that exists in `cells[]`. Unknown cell addresses fail. Use a mapping by index range (first 50 → SS, next 100 → GG, etc.) for book-level conversions.

**Attestations:** Array of `{type, evidence, source_unit_ids}` for X, Z, value, constitution, return.

**Completion:** `{status, benefit, artifact, return_question, return_status, removal_test}`.

### 4. Compile (`fiveqln_compile_manifest`)
- Pass manifest path and report path
- Common failures and their fixes:

| Error | Cause | Fix |
|-------|-------|-----|
| `SYMBOL_DRIFT: U+2032` | Typographic primes in source unit texts or manifest fields | Replace all U+2032/U+2033 with ASCII apostrophes, then recompute SHA-256 hashes for affected source units |
| `SOURCE_HASH: mismatch` | Source unit text was edited without recomputing hash | `hashlib.sha256(text.encode('utf-8')).hexdigest()` for each changed unit |
| `MISSING: required field` | Wrong field name in document_cell | See field table above; `y_status` uses "validated" not "attested" |
| `CELL_REF: unknown source unit` | Cell references a source ID that doesn't exist | Use actual IDs from `manifest.source.units[].id` — never guess |
| `TRACE_CELL: unknown primary cell` | Traceability references a cell address not in `cells[]` | Ensure the address exists in cells array |
| `LENS_CELL: used lens has no converted cell` | Lens audit marked `used` but no backing cell in `cells[]` | Either create the cell or mark the lens `released` |
| `TARGET: expected parent target` | VV cell's parent_target is wrong | VV expects `B+B''+∞0'` (with ASCII primes) |

### Scale strategy for books/large documents
For book-level conversions (100+ source units), use 5 phase-level cells (SS, GG, QQ, PP, VV) and release the remaining 20 lenses with a reason. Chapter-level conversions can populate more lenses later. This keeps the conversion honest (not all 25 lenses are meaningfully used for a single book) while satisfying the compiler's structural requirements.

### Removal test
Every completed conversion needs a removal test: "If 5QLN is removed from this artifact, what materially fails?" For the FCF book: the formation trail tracing how philosophy birthed grammar is lost. Holographic scaling becomes invisible. The conversion reverts to a book summary.

## Honest incompletion
The compiler reporting errors is NOT failure — it's the converter doing its job. A `candidate` completion with named open questions is valid. Never fabricate cells or attestations just to make the report pass. The compiler is the immune system; suppressing its signals is L4.
