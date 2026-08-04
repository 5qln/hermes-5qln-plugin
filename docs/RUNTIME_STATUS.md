# Runtime Status

This document separates shipped executable behavior from operational guidance and
future work. A skill description is not evidence that its backend exists.

## Shipped minimum cycle engine

| Component | Path | Runtime status |
|---|---|---|
| xyzab phase authority | `skills/symbolic-interpretation/scripts/xyzab_state.py` | Enforces x→y→z→a→b and fails closed when structure is invalid |
| structural decoder | `skills/symbolic-interpretation/scripts/decoding.py` | Bundled; standard library only |
| transition/source log | `skills/5qln-learning-aligner/scripts/phase_log.py` | Bundled; written automatically by successful `xyzab open` |
| centrifuge | `skills/5qln-centrifuge/scripts/centrifuge.py` | Bundled exact-pattern reader; reports no data until transitions exist |

A successful gate opening records its transition in the phase log. The gate
command accepts `--source-tag`, `--signal`, and `--session-id`; omitted source
tags are recorded as neutral `unclassified` entries, never inferred or counted
as K-side corruption. Explicit tags are restricted to the documented pair for
their phase. `--override` can record a human review reason on structurally valid
content, but it cannot bypass canonical footer, artifact, or return checks.

Both state files use atomic replacement. Gate opening appends the log before
saving xyzab state so log-write failure leaves the gate shut; if the subsequent
state save fails, the command restores the previous phase log and reports the
error. An advisory phase-log lock serializes appends and xyzab state mutations,
so rollback cannot erase another cooperating writer's entry. Atomic replacement
protects each file independently; the runtime does not claim filesystem-wide
multi-file atomicity across an uncatchable process or power loss.

State resolution is explicit and shared:

1. `$PHASE_LOG_PATH`, when set;
2. `$QLN_WIKI/state/phase_log.json`, when `$QLN_WIKI` is set;
3. `$HERMES_HOME/5qln/phase_log.json` otherwise.

xyzab state remains at `$XYZAB_STATE_DIR/xyzab_state.json`, defaulting to
`~/.5qln/xyzab_state.json`.

## Shipped independent capabilities

- Converter and compiler tools
- Deep-research prompt validator
- Bounded parametric-fractal state and inert-until-seeded hook
- Skill-v1 manifest creator and verifier

The parametric fractal is independent of xyzab and the phase log. It does not
replace them and is not evidence that a cycle has occurred.

## Shipped skill-v1 formation gates (0.8.0)

The skill-v1 verifier (`verify_skill.py`, exposed as `fiveqln_verify_skill`)
enforces four constitutional gates at runtime:

| Gate | Code | Behavior |
|---|---|---|
| Kernel seal | `SEAL_DRIFT` / `SEAL_MISSING` / `SEAL_UNREADABLE` | Every verification hashes `kernel.txt` (217 bytes, sha256 `feaa46b4…859b`) first; drift or absence is fatal |
| Semantic authorship | `GHOST_ORIGINATION` / `SEMANTIC_AUTHORSHIP_PENDING` | Triggers and non-triggers declare `authorship` (`H`/`K`/`PENDING`); machine-authored semantics require digest-scoped human acceptance evidence |
| V∅ return | `DEAD_ENDING` | Promotion mode requires a recorded return question (∞0') in CHANGELOG.md |
| Loop mode | `AXIS_MISSING` / `AXIS_DRIFT` | `--loop-mode` verifies against `axis_attestation` (H's original direction, verbatim, hash-self-checked); the loop runs without per-iteration human stops, and fails closed if the axis is absent or drifted |

The verifier checks structure and digest scope; it never certifies a skill as
living, resonant, or complete — that recognition remains with H.

## Not shipped

The following names remain research or historical concepts and are not executable
plugin dependencies:

- `sub_phase_loop.py`
- `fractal_loop.py`
- `tick.py`
- `verify_decoding.py`
- `axis_engine.py`
- native `fiveqln_axis_*` tools

The `5qln-signature-engine` skill is a conceptual guide. No persistent signature
axis is installed by this repository.

## Python dependencies

| File | Scope |
|---|---|
| `requirements.txt` | Runtime: PyYAML for skill verification |
| `requirements-dev.txt` | Tests/schema validation: jsonschema plus runtime requirements |
| `requirements-optional.txt` | DOCX/PDF extraction: python-docx and pypdf |

All minimum cycle-engine scripts use only the standard library. Registered tools
run with the same Python interpreter that runs Hermes. Do not assume a separate
plugin-local virtual environment is used.

## Integrity boundary

The runtime verifies ordering, required fields, explicit source classification,
and durable record structure. It cannot verify emergence, resonance, aliveness,
or human attestation. Those remain human judgments.
