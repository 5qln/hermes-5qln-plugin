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

## Port-specific additions

- `plugin.yaml`: Hermes discovery metadata.
- `__init__.py`: tool and skill registration.
- `schemas.py`: Hermes-facing tool schemas.
- `tools.py`: shell-free wrappers with non-overwrite defaults.
- `tests/`: registration and end-to-end validation.
- repository documentation and CI.

Any future modification to the original skill files should update this document and explain the lineage in `CHANGELOG.md`.

