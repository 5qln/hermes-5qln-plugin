# Provenance

The Hermes plugin was derived from the complete installed 5QLN Converter skill set on 2026-07-19. The original skill files were copied without modification; Hermes-specific registration, schemas, wrappers, tests, and repository documentation were added around them.

## Original skill checksums

| File | SHA-256 |
|---|---|
| `SKILL.md` | `2a21d91b426ef8a76400386cb14134739a761e65331aa9612ccea48b811cb45c` |
| `agents/openai.yaml` | `ae65afd8ba83e412123bb060a512007a3d25d30c2636d942375b1b776d29f780` |
| `references/constitution.md` | `4ad4db368517af916edbf1e630286847d3c77ebc9e5ada49f2bcbaf8c43c8ca8` |
| `references/conversion-protocol.md` | `38a2e045e3885a96daeb8120ad17e12983d415f7fd17662dc141a054fb140f42` |
| `references/manifest.md` | `09968e8229bf954fe4521165714c5a7c679f5cafab317a1b81418a0e8f9a213f` |
| `scripts/5qln_compiler.py` | `56e3fa5f85cd792e7a428f81dd1483f435c680f3882c6409fbead0d50ada6557` |
| `scripts/inventory_source.py` | `b462c8395896cc871f55261e717a5495cfeeab0e976e70f555ae5d3e3aae3fd5` |
| `scripts/new_manifest.py` | `61cd1f1a934a1e2afc0a8ff215ee8e27d93abec7a2023a68b6dac5eb2fbc9b90` |

These hashes establish file identity for this import. They do not establish conceptual authority, authorship, truth, or human attestation.

## Deep-research skill import

The `5qln-deep-research` bundle was imported from the installed personal skill on 2026-07-22 after adding a dual-runtime validation route: Hermes uses the registered `fiveqln_validate_research_prompt` tool, while portable installations retain the direct script path. The prompt contract remains identical across both surfaces.

| File | SHA-256 |
|---|---|
| `SKILL.md` | `3fd3ea81cd9a84e4a872a7367410a364d0b2fcb31d744f2a35a13dc51a55e7bb` |
| `agents/openai.yaml` | `3174b4d34482b339c2ece8d8e5def84519e3ff41e3451f0680094e10dc52838a` |
| `references/research-prompt-contract.md` | `0082cf72d728dfce24f39012583b31c2da06b07343e666df758402e2cfcadfb5` |
| `scripts/validate_research_prompt.py` | `06f953746f5a213711dd780baf58e2c334ed8a39b9e275a612c39449c928f626` |

These hashes establish import identity only. The skill and validator remain Mutable Implementation under Apache 2.0; the exact constitutional kernel they preserve remains governed by the kernel license.

## Port-specific additions

- `plugin.yaml`: Hermes discovery metadata.
- `__init__.py`: tool and skill registration.
- `schemas.py`: Hermes-facing tool schemas.
- `tools.py`: shell-free wrappers with non-overwrite defaults.
- `fiveqln_validate_research_prompt`: Hermes wrapper around the imported deterministic validator.
- `tests/`: registration and end-to-end validation.
- repository documentation and CI.

Any future modification to the original skill files should update this document and explain the lineage in `CHANGELOG.md`.
