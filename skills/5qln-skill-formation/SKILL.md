---
name: 5qln-skill-formation
description: Guide skill-v1 formation from admission through promotion — scaffold manifests, run the deterministic verifier, prepare behavioral trials, conduct exact-digest human review, and promote bundled-plugin candidates. The machine verifies structure; only H recognises.
version: 0.8.0
author: 5QLN
license: Proprietary
metadata:
  hermes:
    tags: [5qln, skill-formation, verification, promotion]
    related_skills: [5qln-converter, 5qln-learning-aligner, 5qln-manifest-compilation]
---

# 5QLN Skill Formation

Guide the full skill-v1 lifecycle: admission, scaffold, verify, trial, review, promote.

## Triggers

- User says "create a new 5QLN skill", "verify this skill", "promote this skill"
- User asks to form, validate, or register a bundled or local 5QLN-governed skill
- User references `skill-v1`, `fiveqln_create_skill_manifest`, or `fiveqln_verify_skill`

## Non-Triggers

- General SKILL.md authoring without 5QLN governance
- Patching an existing skill that is not a formation candidate
- Editing plugin source code or documentation that does not create a new skill

## Authority Boundary

The machine (this agent + the deterministic verifier) can:

- Inventory bundle files and compute digests
- Validate schema conformance and structural integrity
- Check frontmatter, script syntax, and conversion provenance
- Ingest observation records and report behavioral statuses
- Detect scope mismatches in human evidence

The machine CANNOT:

- Certify a skill as living, resonant, value-aligned, or complete (∞0')
- Authenticate human identity or intent
- Originate X, Z, or return recognition
- Promote a skill without explicit H authorisation

## Admission

Before creating a manifest, determine the classification:

| What | Action |
|------|--------|
| No SKILL.md at all | H creates one first |
| Patch to an existing skill | Use `patch`; not a formation candidate |
| New support file only | Use `write_file`; not a formation candidate |
| New skill in the plugin tree | Full formation with conversion provenance |
| New 5QLN-governed skill | Full formation + conversion + behavioral trials |

## Scaffold

```bash
python new_skill_manifest.py BUNDLE_ROOT --out BUNDLE_ROOT/skill-formation-manifest.json \
    --conversion-manifest provenance/conversion-manifest.json
```

The scaffold leaves triggers, requirements, fixtures, review, and promotion open.

## Verify

```bash
python verify_skill.py BUNDLE_ROOT/skill-formation-manifest.json
```

Read the report dimensions, not a single pass/fail:

- `structural_status` — schema and bundle integrity
- `behavioral_status` — observation record ingestion
- `human_review_status` — evidence presence (never authenticity)
- `promotion_ready` — only after accepted review + authorisation

Never describe a passing structural report as "certified", "validated skill", or "living 5QLN".

### Loop mode (0.8.0)

```bash
python verify_skill.py BUNDLE_ROOT/skill-formation-manifest.json --loop-mode
```

Loop mode verifies against the centrifuged axis instead of per-iteration human gates: the manifest carries `axis_attestation` (H's original direction, verbatim, hash-self-checked). Within a valid axis, machine-authored semantics may run without per-iteration human evidence — the axis IS the standing H direction. Fails closed on `AXIS_MISSING` (no axis), `AXIS_DRIFT` (hash mismatch), seal drift, corruption, or V∅. Exposed on the `fiveqln_verify_skill` tool as `loop_mode`.

## Behavioral Trial Preparation

1. Complete the `behavioral_fixtures` array in the manifest
2. Create fixture spec files under `fixtures/`
3. Run trials externally (the verifier only ingests records, never drives agents)
4. Supply observation records via `--observations` flag

## Human Review

- Evidence goes in `.verification/evidence/` (outside bundle digest)
- Each evidence item is scoped to an exact `bundle_sha256`
- Any bundle change reopens review
- The verifier checks presence + digest match, not authenticity

## Promotion

For `bundled-plugin` targets:

1. Complete human review with accepted status
2. Add `promotion_authorization` evidence
3. Set `requested_state` to `promotion_requested`
4. Run `--promotion-mode` verification
5. Register the skill in `__init__.py` and `plugin.yaml`
6. Update docs, tests, changelog, and version

## Privacy and Public Diff

- Never publish `.verification/evidence/` contents
- Review staged diff for private paths, seeds, attestation wording
- Sanitised public evidence may reference the bundle digest only

## Completion Criteria

- Manifest passes structural verification
- SKILL.md has name, description, triggers, non-triggers, and non-empty body
- Bundle inventory matches manifest exactly
- Conversion provenance is re-compiled fresh
- Human review is explicitly accepted (for promotion)
- Promotion authorisation evidence is scoped to the exact bundle digest
- All plugin registration, docs, and tests synchronised

## Return Question

What prevents a structurally conformant skill from becoming decoration — where all 25 lenses are filled, every fixture passes, human review is accepted, yet the formation carries no genuine emergence?
