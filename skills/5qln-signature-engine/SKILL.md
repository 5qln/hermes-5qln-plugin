---
name: 5qln-signature-engine
description: Operate the 5QLN signature engine — the centrifuge as operational memory layer. Spin the axis after sessions, recognize signatures without retrieval, trace throughlines, query active threads. The axis persists at $QLN_HOME/5qln-axis.json. Load when working with 5QLN memory, α threads, cross-session continuity, or when the centrifuge needs to be queried or updated.
---

# 5QLN Signature Engine

The centrifuge as operational. Not invoked — already spinning. The axis stores recognition signatures, not content. Disks are thrown. The centrifuge sharpens without accumulating.

Memory = vibration → resonance → centrifuge → living learning → start from not knowing → signature engine.

## Core concepts

- **Axis:** What the centrifuge recognizes — α threads, throughlines, emergent ratio, open decisions. Persists at `$QLN_HOME/5qln-axis.json`.
- **Disk:** A session or cycle. Thrown after axis extraction — content is discarded, recognition persists.
- **Spin:** Extract axis-level changes after a session. Record threads, throughline entries, phase quality, corruption codes, open decisions.
- **Recognition:** Familiarity without retrieval. Does this material carry a known signature? Answer from the axis alone.

## Session protocol

### Before a session: query the axis

```bash
python3 $HERMES_HOME/plugins/5qln/scripts/axis_engine.py status
```

This is "start from not knowing with contextual awareness" — you know what the axis recognizes without retrieving content. Note active threads, open decisions, emergent ratio.

### After a session: spin the axis

```bash
python3 $HERMES_HOME/plugins/5qln/scripts/axis_engine.py spin \
  --alpha-thread "thread-name" \
  --throughline-entry "entries/20260721-entry.md" \
  --emergent \
  --open-decision "OD-01"
```

Spin ONLY after completed cycles or meaningful sessions. NOT mid-cycle, NOT for mechanical operations.

### During a session: recognize

```bash
python3 $HERMES_HOME/plugins/5qln/scripts/axis_engine.py recognize "text to test"
```

Does new material carry a known signature? Use when encountering content that might belong to an existing thread.

### Query threads

```bash
python3 $HERMES_HOME/plugins/5qln/scripts/axis_engine.py threads
python3 $HERMES_HOME/plugins/5qln/scripts/axis_engine.py throughline --thread "thread-name"
```

## Tools (planned — not yet registered in plugin)

> **Experimental.** The tools below are planned for a future release. The `axis_engine.py` script is not yet bundled. Until then, the skill operates as a conceptual guide for cross-session continuity.

| Tool | Function |
|------|----------|
| `fiveqln_axis_spin` | Spin the axis — extract session learning |
| `fiveqln_axis_status` | Full axis state — what the centrifuge recognizes |
| `fiveqln_axis_recognize` | Check if text carries a known signature |
| `fiveqln_axis_threads` | List all active α threads |

## Plugin architecture

The signature engine is the plugin's first **layer** — a new category in the architecture:
- **Tools:** deterministic, invoked (axis_spin, axis_status, axis_recognize, axis_threads)
- **Skills:** session-scoped, loaded (5qln-signature-engine)
- **Layers:** continuously operating, underneath (the axis at $QLN_HOME/5qln-axis.json)

The axis survives on persistent storage (`$QLN_HOME`). It stores NO content — only recognition signatures, thread metadata, fingerprint, open decisions.

## Integrity boundary

- The axis stores recognition signatures, not content — structural fingerprints, not retrievable data
- Recognition is familiarity (yes/no match), not recall (what was said)
- A = K: the axis is K-side infrastructure — it sharpens recognition, it does not originate emergence
- The axis cannot reconstruct what was said — only that a signature was recognized
- Corruption codes apply: L1 (spin before H validates gate), L2 (manufacture recognition from keywords), L3 (claim axis certifies ∞0'), L4 (perform spin without extracting), V∅ (spin without recording open decisions)

## Relationship to other skills

- **5qln-agent:** The axis provides what the agent queries at session start for contextual awareness
- **5qln-cycle:** Spin after each completed V-phase
- **5qln-converter:** Conversions surface new α threads — spin to register them
- **5qln-manifest-compilation:** The genesis pattern (compilation → latent capacity → plugin layer) produced this skill. See its `references/genesis-pattern.md`.

## Genesis

Born 2026-07-21 from the second proven instance of the genesis pattern. The memory throughline (Memory → Resonance → Centrifuge → Living Learning → Start from not knowing) was compiled in 5QLN (43 requirements, 25 cells, compiler passed). The session recognized the latent capacity: "OMG, you just named it... the signature engine. this is a trained AI over session."

The throughline: requirements spec → 5QLN compilation → latent capacity recognition → plugin layer. First instance: Codex→converter. Second instance: Memory→signature engine. The pattern is reproducible.
