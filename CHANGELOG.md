# Changelog

All notable changes are recorded here. Versions follow semantic versioning.

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
