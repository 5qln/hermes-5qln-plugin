# Changelog

All notable changes are recorded here. Versions follow semantic versioning.

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
