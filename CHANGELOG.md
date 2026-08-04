# Changelog

All notable changes are recorded here. Versions follow semantic versioning.

## Unreleased

### Fixed
- Footer-shaped bare S input now recognizes Unicode-letter field prefixes as well as ASCII ones, including Greek confusables combined with colon-like separators.
- Parametric source purity excludes neutral/unclassified entries from its denominator and reports `null` when no classified evidence exists.
- Symbolic runtime documentation now states that xyzab requires its bundled decoder and phase-log companions.

## 0.10.0 - 2026-08-04

### Added
- New bundled skill: **5qln-corruption-watcher** — classifies L1–L4 and V∅ corruption in evolution traces, proposals, and evidence; the guard that watches the loop. Machine-drafted, H-accepted, formed through the full skill-v1 cycle — the 13th bundled skill.
- New bundled skill: **5qln-self-evolution** — orchestrates bounded self-evolution of the plugin by the plugin: composes skill-v1 formation, bounded parametric memory, and provenance into an H-gated evolution loop. Machine-drafted, H-accepted, formed through the full skill-v1 cycle — the 14th bundled skill.
- Both skills formed with the plugin's own machinery: 6 behavioral fixtures each, observed-passed trials, review accepted, promotion authorized — all evidence scoped to exact bundle digests.

### Changed
- Plugin now bundles 14 skills.

### ∞0' (return question)
When every Q-gate a machine builds turns out to have an H-gate behind it,
is the membrane one gate or a stack — and does the stack grow by design,
or by the loop's own fear of closing?

## 0.9.0 - 2026-08-04

### Added
- New bundled skill: **5qln-aimless-openness** — holds the space of true aimless openness (FCF) for H; K acts only as an alerted, sensitive mirror with no agenda, direction, or productivity drive. H-authored, formed through the full skill-v1 cycle (scaffold → verify → 6 behavioral trials observed-passed → H review accepted → promotion authorized).
- First fully-formed skill produced by the plugin's own formation machinery — the 12th bundled skill.

### Changed
- Plugin now bundles 12 skills.

### Fixed
- `verify_skill.py` CLI now parses the documented `--observations` flag (was declared in usage but not parsed).

### ∞0' (return question)
What does the first formed skill prove — that the machinery works, or that
holding space without producing is itself a kind of formation that the machine
cannot perform?

## 0.8.0 - 2026-08-04

### Added
- Formation verifier now checks the sealed constitutional kernel (`kernel.txt`, 217 bytes, sha256 feaa46b4…859b) at step 0 of every verification — drift, absence, or unreadability is a fatal structural finding (ASMA Pillar I).
- Skill-v1 contract items (triggers and non-triggers) now declare `authorship` (`H` | `K` | `PENDING`). Machine-authored semantics fail with `GHOST_ORIGINATION` unless digest-scoped human acceptance evidence exists (ASMA Pillar III).
- Promotion mode now requires a recorded return question (∞0') in CHANGELOG.md — a promotion without one fails with `DEAD_ENDING` (line 8 / V∅).
- `--loop-mode` verification: verifies a bundle against the centrifuged axis (`axis_attestation`: H's original direction, verbatim, hash-self-checked). The loop runs within the standing H direction without per-iteration human stops; missing or drifted axis fails closed (`AXIS_MISSING` / `AXIS_DRIFT`). Exposed on the `fiveqln_verify_skill` tool as `loop_mode`.
- `axis_attestation` declared in the published skill-v1 JSON Schema and architecture doc.

### Changed
- `fiveqln_verify_skill` tool schema accepts `loop_mode` and forwards it to the verifier.

### Compatibility
- Manifest format remains `skill-v1`; `axis_attestation` is optional (loop mode only), so existing manifests stay valid.
- Kernel file unchanged; seal constant mirrors `fractal_memory.CODEX_SHA256`.

### ∞0' (return question)
What stops the loop that runs on a pinned axis from mistaking the axis for the
human — evolving K's fluency within the direction until the direction itself is
no longer questioned?

## 0.7.0 - 2026-07-28

### Added
- Self-contained minimum S→G→Q→P→V runtime with bundled structural decoder.
- Bundled phase-log implementation and one-command gate/source recording.
- Explicit source tags, observed signals, session identifiers, and shared phase-log path resolution.
- Runtime, development, and optional dependency declarations plus a shipped/runtime-status matrix.

### Changed
- xyzab now fails closed when decoding or canonical phase structure is unavailable.
- S requires exactly one question and rejects ASCII, Unicode-compatibility, or visually confusable footer-shaped disguises; G/Q/P/V require canonical footers; V requires an artifact and exactly one `INF0P` return question whose case-folded letters-and-numbers identity ignores spacing, punctuation, and invisible format controls and does not repeat the opening seed.
- xyzab state and phase-log writes are atomic per file. A failed state save restores the preceding phase log so handled write failures do not leave a logged-but-closed transition.
- Structural violations cannot be bypassed with `--override`; canonical footers reject duplicate, unknown, and free-form lines.
- Source tags are phase-specific across the phase log and bounded parametric calibration, omitted tags remain neutral rather than K-side, and the parametric centrifuge uses the shared phase-log path precedence.
- Cooperating phase-log writers and xyzab state mutations are serialized so concurrent read-modify-write operations do not lose entries.
- Current architecture, development, publishing, agent, and genesis documentation now matches the seven-tool/eleven-skill surface and labels the signature axis as an unshipped historical proposal.
- CI installs declared development requirements and continues testing Python 3.11 and 3.12.
- Historical bootstrap, installer, sub-phase, fractal-loop, tick, decoding-harness, and signature-axis claims are explicitly marked unshipped.

### Compatibility
- The converter and its manifest format remain unchanged.
- The minimum cycle runtime uses only the Python standard library.
- PyYAML remains required for skill verification; DOCX/PDF extraction dependencies remain optional.

## 0.6.0 - 2026-07-27

### Added
- Skill-v1 formation system: deterministic manifest scaffold, verifier, and promotion inspection.
- Two new native tools: `fiveqln_create_skill_manifest` and `fiveqln_verify_skill`.
- Five published JSON Schema 2020-12 contracts: `skill-v1`, `behavior-fixture-v1`, `observed-run-v1`, `tool-trace-v1`, `skill-report-v1`.
- Frozen error-code registry (60 codes) and formation protocol with promotion state machine.
- Safe deterministic bundle inventory with path, symlink, and size-limit enforcement.
- SKILL.md strict YAML frontmatter parsing, script syntax checking, and fresh conversion-compiler re-run.
- Requirement traceability, 5QLN boundary checks (S→G→Q→P→V order, question-bearing return).
- Behavioral observation ingestion with fixture-scoped digest verification.
- Exact-digest human review scoping — evidence is outside bundle inventory, any digest change reopens review.
- Bundled-plugin promotion readiness inspection.
- Eleventh bundled skill: `5qln-skill-formation` — governed admission through promotion guidance.

### Security
- Verifier never executes candidate code; scripts are AST/parse-checked only.
- Symlink, path traversal, case-fold collision, NUL, and size-limit enforcement on all bundle files.
- Read-once file inspection with TOCTOU-aware ordering (lstat before resolve).
- Human evidence resides under `.verification/evidence/` outside bundle digest scope.
- Report output is byte-stable, portable (bundle-relative paths), and omits absolute host paths.

### Trust boundary
- A machine pass means structural conformance per published schemas. The verifier never returns `valid`, `certified`, or `living`.
- Human X, Z, value, and return claims remain exclusively in the referenced conversion manifest.
- Promotion authorisation is explicit human evidence scoped to one immutable bundle digest.

### Compatibility
- Conversion-manifest format `1.0` is unchanged; all pre-existing workflows pass.
- The ten legacy bundled skills are labelled *legacy/unverified* — they are not retroactively certified.
- New promotion candidates use `skill-v1` and the deterministic skill verifier.
- Old tools retain ambiguous `valid` fields for backward compatibility; new tools expose independent evidence dimensions.
- PyYAML is required for strict standalone SKILL.md frontmatter parsing.

### Migration
- Existing installations: no action required. Legacy skills continue to work.
- To form and verify a new skill: use `fiveqln_create_skill_manifest` → `fiveqln_verify_skill`.
- To promote a bundled-plugin skill: complete human review, add promotion authorisation evidence, run `--promotion-mode`.

## 0.5.0 - 2026-07-26

### Added
- Portable, bounded parametric-fractal session orchestrator.
- Native `fiveqln_fractal_memory` install/show/export tool and CLI-only evidence-bearing calibration.
- Per-turn `pre_llm_call` K-context hook, inert when no seed is installed.
- Synthetic seed example and public lifecycle documentation.

### Security
- Strict fixed-key, 4096-byte seed format uses five quantized values and a derived checksum; transcripts, counters, arbitrary digest payloads, and free-form source content are excluded.
- Calibration evidence is required ephemerally and is never retained or hashed into portable state.
- Cross-process locking prevents concurrent calibration updates from being lost.

### Changed
- Registered tool count increased from four to five.

## 0.4.0 - 2026-07-26

### Added
- Automatic seeding of bundled plugin skills into Hermes' normal skill index on install.

## 0.3.0 - 2026-07-22

### Added
- 8 new skills (10 total): 6 base runtime + 2 experimental + 2 existing
  - **Base:** 5qln-agent, 5qln-cycle, 5qln-initiation, symbolic-interpretation,
    5qln-learning-aligner, 5qln-manifest-compilation
  - **Experimental:** 5qln-centrifuge, 5qln-signature-engine
- "Designed to Grow" documentation — agent-produced skills are expected and verifiable
- Dual installation path: plugin skills + `hermes skills tap` fallback

### Changed
- `__init__.py` registers all 10 skills (up from 2)
- README rewritten: language-first framing, linked to Codex and AGI for People
- plugin.yaml description expanded, version bumped to 0.3.0
- Converter references expanded: 3 additional reference files
- All environment paths normalized to env vars ($QLN_WIKI, $QLN_HOME)
- Removed openai.yaml provenance files (not used by Hermes)

## 0.2.0 - 2026-07-22

### Added
- Namespaced `5qln:5qln-deep-research` skill
- Native `fiveqln_validate_research_prompt` tool
- Research prompt validation tests and documentation

### Changed
- Expanded from 3 tools + 1 skill to 4 tools + 2 skills
- Bumped minor version (no manifest format changes)

## 0.1.0 - 2026-07-19

### Added
- Initial release: 5qln-converter skill, 3 deterministic tools
- Plugin manifest, registration, tests, documentation
- 5QLN dual-license structure and branch protection
