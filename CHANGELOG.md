# Changelog

All notable changes are recorded here. Versions follow semantic versioning.

## 0.2.0 - 2026-07-22

### Added

- Namespaced `5qln:5qln-deep-research` skill for single-agent and coordinated prompt formation under dependent `S → G → Q → P → V` gates.
- Native `fiveqln_validate_research_prompt` tool with JSON-string returns, non-overwrite report protection, and separate execution and validity states.
- Canonical-kernel synchronization, valid/invalid prompt, registration, and overwrite regression tests.
- Hermes-specific deep-research usage, architecture, integrity, development, and publishing documentation.

### Changed

- Expanded plugin registration from three tools and one skill to four tools and two skills.
- Added machine-readable JSON output to the portable research-prompt validator.
- Bumped the plugin minor version without changing the conversion manifest format, lens notation, constitutional kernel, or existing tool schemas.

## 0.1.0 - 2026-07-19

### Added

- Standalone Hermes plugin manifest and registration.
- Namespaced `5qln:5qln-converter` skill with the complete reference and script bundle.
- Native tools for source inventory, manifest scaffolding, and manifest compilation.
- Non-overwrite defaults and shell-free subprocess execution.
- End-to-end tests for registration, a passing workflow, constitutional drift, and overwrite protection.
- Installation, usage, architecture, integrity, development, publishing, security, and contribution documentation.
- The 5QLN mixed-license structure, required attribution, trademark notice, and repository-wide code ownership by `@5qln`.
- An auditable `main` branch-protection policy and authenticated application script.
