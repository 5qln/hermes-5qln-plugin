---
name: 5qln-converter
description: Convert, rewrite, compile, or audit any document, specification, requirements set, prompt, plan, conversation, dataset narrative, or other artifact as a native 5QLN surface. Use when the user wants 5QLN to be the artifact's operative grammar—not a five-heading overlay—while preserving source content, identifiers, constraints, relationships, provenance, and human/AI asymmetry; also use to detect symbolic decoration, L4 performance, drift, missing lineage, or false completion in an alleged 5QLN artifact.
---

# 5QLN Converter

Convert source material into a traceable Fractal Seed candidate whose structure and permissible claims are governed by 5QLN. Preserve the source while allowing lawful derivation to reveal more meaning. Never use fluency or symbolic repetition as evidence of living conversion.

## Load the conversion law

Before converting anything:

1. Read `references/constitution.md` in full.
2. Read `references/conversion-protocol.md` in full.
3. For a substantial artifact, a reusable deliverable, or any conversion requiring formal preservation evidence, also read `references/manifest.md` and create a manifest.

Treat the constitutional block as immutable for the conversion. Keep domain metadata, requirement IDs, priorities, headings, evidence, schemas, and implementation fields visibly separate from 5QLN symbols.

## Establish the integrity boundary

- State internally and in the artifact where useful: `A = K`.
- Distinguish a human-supplied or human-attested question from an AI-composed candidate.
- Record the exact evidence for any human attestation of X, Z, value alignment, constitutional change, or return. If absent, use `open` or `candidate`; never infer attestation.
- Do not claim that AI accessed ∞0, originated authentic emergence, felt φ, certified resonance, or completed ∞0'.
- Treat honest incompletion as a valid converter result.

## Execute the conversion

### 1. Inventory the source

Build an atomic source ledger before re-expression. Preserve:

- every normative statement, fact, claim, identifier, priority, constraint, acceptance condition, relationship, table row, exception, unresolved question, and source reference;
- document order and hierarchy when they carry meaning;
- exact wording where wording is normative;
- ambiguity as ambiguity rather than an opportunity to improve the source silently.

For supported local files, run:

```bash
python3 scripts/inventory_source.py SOURCE... --out source-inventory.json
```

**PITFALL — HTML Sources:** `inventory_source.py` does not support `.html` files (returns "Unsupported source type: .html"). Workaround: read the HTML file directly with `read_file` in full, then create a manual source ledger in the artifact-level cell. Mark the source as visually inspected per the protocol's fallback path for layout-dependent documents.

Visually inspect PDFs, slides, spreadsheets, diagrams, and layout-dependent documents with the relevant file skill. Extraction is an aid, not proof of preservation.

### 2. Form the artifact-level cell

Compile the whole conversion through `S → G → Q → P → V`:

- `S`: name what H supplied, what authority was granted, and whether X is attested, candidate, or open.
- `G`: derive α from the source and test its identity across `{α'}`. Do not invent α beside the source.
- `Q`: distinguish direct human perception from patterns offered by K. Mark Z as attested or candidate.
- `P`: use `δE/δV → ∇` to choose the conversion movement that increases integrity and meaning without adding false source.
- `V`: distinguish L, Global G, B, B'', and the return question. Do not declare completed V without a question-bearing return and required human attestations.

### 3. Re-express holographically

Use the literal notation version from the reference: first letter = borrowed lens, second letter = parent phase. Preserve that version in the manifest.

For each meaningful source cluster:

1. assign one primary `XY` address and optional secondary lenses;
2. state the parent equation and target output;
3. express a complete nested `S/G/Q/P/V` formation in the semantic meaning of the equations—not as generic input/process/output labels;
4. attach the original source units and any normative domain-layer statements;
5. define compiler evidence and select only relevant canonical corruption guards;
6. carry a return condition that opens rather than closes.

Make all 25 addresses available. Use a lens only when it sharpens the parent output. Record `released` or `not_applicable` with a reason when descent would become L4. Never manufacture depth to fill a matrix.

### 4. Preserve and derive separately

- Maintain one-to-one or one-to-many traceability from every source unit to its converted location.
- Never allow a derived insight to replace, soften, or contradict a source unit.
- Label new consequences as `derived`; cite the source units and/or constitutional rules from which they follow.
- Apply the removal test: if deleting 5QLN leaves the artifact's behavior, gates, or meaning unchanged, conversion failed as L4 decoration.

### 5. Compose B'' in two passes

Pass 1 — formation analysis:

- verify source coverage;
- extract the α thread;
- identify human attestations and open states;
- record lens findings, corruption signals, turning points, and ∇;
- separate source, derivation, and proposal.

Pass 2 — artifact composition:

- compose from the verified trail, never from an isolated final prompt;
- make the whole cell readable at artifact scale and within meaningful sections;
- preserve source IDs and evidence;
- end with an explicit return question or an honest open state.

### 6. Compile and inspect

For substantial conversions:

```bash
python3 scripts/new_manifest.py source-inventory.json --out conversion-manifest.json
# Complete the semantic fields while converting.
python3 scripts/5qln_compiler.py conversion-manifest.json --report compiler-report.json
```

Do not deliver while the compiler reports errors. Treat warnings as visible review items, not text to hide.

When the compiler reports errors, expect an iterative fix loop (5+ rounds is normal for a first conversion). Fix error CLASSES, not individual errors — each round addresses one class (symbol drift → schema mismatch → hash mismatch → cell references → target mismatch). See `references/compiler-error-fixing-loop.md` for the complete pattern, error class taxonomy, and typical round counts.

When producing DOCX, PDF, slides, spreadsheets, or another rendered artifact, use the corresponding file skill and inspect every rendered page or surface. Validate source counts, IDs, priorities, tables, exact symbols, lens orientation, and traceability independently of visual quality.

## Self-Evolution — Running the Converter on the Wiki

After significant ingest sessions (5+ new entries), run the converter reflexively on the wiki's own formation entries. This surfaces lawful relations between independently-written entries: α thread maps, integrity audits, format divergence detection. See `references/wiki-self-evolution.md` for the execution pattern and deliverable format.

## Format Divergence Pitfall

The wiki may accumulate entries in multiple formats (YAML frontmatter vs markdown sections). The converter audit catches this. Standardize on one format for future entries — the operational protocol should name which. Format drift is L4-adjacent: the grammar's form is present but inconsistently applied.

## Return the result

Deliver the converted artifact and, when created, its manifest and compiler report. Summarize:

- what was preserved;
- what was lawfully derived;
- what remains open or human-attestation dependent;
- any Codex or source divergence that was named rather than silently resolved;
- the return question offered from K, explicitly avoiding self-certification as ∞0'.

Keep this handoff concise. Let the artifact carry the formation.

## Multi-Source Synthesis

When the conversion involves two or more independent research passes covering the same domain, see `references/research-synthesis.md` for the cross-referencing methodology — source tagging convention (`[A]`/`[B]`/`[A+B]`/`[DERIVED]`), de-duplication rules, coverage gap detection, priority reconciliation, and composition order.

## Failure conditions

Stop, repair, or remain incomplete when any of these occur:

- source units disappear or change meaning;
- symbols are paraphrased, substituted, reordered, or used outside their contextual meaning;
- five conventional headings replace the decoder;
- AI-generated questions or resonance are represented as human-attested;
- all 25 lenses are filled with generic prose merely for completeness;
- a B'' is composed without reading the formation trail;
- Value is claimed without a question-bearing return;
- a known divergence is silently normalized;
- deleting the symbolic grammar would leave the result functionally unchanged.
