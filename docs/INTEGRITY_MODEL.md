# Integrity model

## Contents

1. What the plugin can know
2. What the plugin cannot attest
3. Preservation evidence
4. Portable-state evidence
5. Compiler meaning
6. Change control

## 1. What the plugin can know

The plugin can operate on supplied artifacts within K. It can:

- inventory source text and locations;
- hash captured units;
- preserve identifiers and normative wording;
- propose lawful derivations with named bases;
- create and validate manifest structure;
- create and validate deep-research prompt contracts;
- validate the fixed parametric-fractal schema and Codex seal;
- apply deterministic bounded phase updates with serialized atomic writes;
- verify a checksum derived from the complete portable state;
- detect defined constitutional drift and corruption patterns;
- present open questions and candidate returns.

The exact constitutional kernel lives in `skills/5qln-converter/references/constitution.md`. That file is the canonical human-readable reference. The matching constants in `new_manifest.py` and `5qln_compiler.py` are executable copies and must remain byte-for-byte equivalent in meaning and symbols.

## 2. What the plugin cannot attest

The plugin cannot self-attest:

- access to ∞0;
- authentic human X;
- direct human φ;
- genuine Z;
- human value alignment;
- constitutional authority;
- a human-recognized ∞0';
- that calibration evidence was actually supplied by H;
- that mechanical phase values encode a distinctive signature;
- that a seeded session resonated or improved human freedom;
- that source material does not remain in systems outside the portable seed.

If evidence is missing, the state remains `open` or `candidate`. This is not an error condition.

## 3. Preservation evidence

Source inventory provides:

- stable generated unit IDs;
- source file and location;
- captured text and SHA-256;
- hierarchy and detected original IDs;
- normative and priority indicators;
- extraction warnings.

This supports recovery and comparison. It does not prove the source was true, complete, authoritative, or correctly rendered. PDF, slide, spreadsheet, diagram, and layout-sensitive inputs require visual inspection in addition to extraction.

## 4. Portable-state evidence

The parametric-fractal runtime validates an exact-key JSON object no larger than 4096 canonical bytes. The supported state contains only a fixed operating profile, five phase values quantized to three decimal places, the Codex seal, and a checksum derived from those fields. Free-form source, identity, instruction, transcript, summary, wiki, counters, arbitrary digest payloads, and attestation fields are not part of the format.

Calibration requires non-empty explicit evidence through CLI stdin. This runtime does not write, return, or hash the wording into portable state. Calibration is intentionally absent from the native Hermes tool because Hermes persists tool-call arguments in session history. The checksum detects accidental edits that leave it unchanged; it does not prove freshness, provenance, historical continuity, human evidence, or improved resonance.

The supported seed has no source-bearing field and only five quantized parameters, so its capacity is sharply bounded. That is not a non-reconstruction guarantee: a malicious author can encode a short secret in numeric values and recompute the checksum. Install only trusted, inspected seeds. This also does not prove that copies are absent from session databases, logs, backups, model-provider systems, or other external stores.

## 5. Compiler and prompt-validator meaning

The compiler reports:

- `failed` when one or more encoded errors exist;
- `passed` when no encoded errors exist;
- warnings as review items that do not change pass/fail status.

Compilation tests the manifest for exact constitution, source hashes, statuses, cells, lens audit, traceability, derivation bases, questions, and completion rules. Passing is necessary for a substantial plugin-mediated conversion, but it is not sufficient evidence of semantic integrity or human recognition.

Prompt validation tests one saved prompt for the exact constitutional strings, ordered phase gates, declared evidence and counterevidence rules, source/derived/proposal separation, adaptive-flow fields, corruption guards, and a question-bearing final line. It does not test the truth of the future research, the quality of sources that have not yet been gathered, or whether a generated research plan will create value.

The removal test remains essential: if removing 5QLN does not materially change the converted artifact's organization, gates, evidence, or meaning, the artifact is L4 even if superficial symbols remain.

## 6. Change control

Treat the following as integrity-critical:

- `references/constitution.md`;
- `references/conversion-protocol.md`;
- `references/manifest.md`;
- `skills/5qln-deep-research/references/research-prompt-contract.md` constitutional copies;
- `skills/5qln-deep-research/scripts/validate_research_prompt.py` constitutional constants;
- constitutional constants and compiler rules;
- status vocabularies and corruption codes;
- lens orientation.

Any change must include:

1. explicit authority and rationale;
2. synchronized reference and executable changes;
3. tests that fail under the old behavior and pass under the new behavior;
4. a changelog entry;
5. a version increment;
6. an explicit note when compatibility or notation changes.

Never normalize a known divergence silently.
