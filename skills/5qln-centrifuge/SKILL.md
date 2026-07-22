---
name: 5qln-centrifuge
description: The 5QLN centrifuge — extract the invariant axis from the phase log chain. Reads all cycles, discards specific content, surfaces what repeats. Produces signature card, source tag chain, ratios, and self-check. Stdlib-only Python. Bundled as an experimental hermes-5qln-plugin skill.
status: ongoing-research
research_note: >
  The centrifuge operationalizes the memory-throughline insight (Memory → Resonance → Centrifuge
  → Living Learning → Start from not knowing). Current implementation is an exact-pattern reader
  of the phase log chain — it surfaces what repeats, not what resonates. Semantic recognition,
  continuous operation, and cross-session familiarity are deferred. This tool demonstrates the
  centrifuge concept; it does not yet implement the full five-layer axis. The signature card is
  a photograph of the axis, not the axis itself.
---

# 5QLN Centrifuge — The Axis Operator

> The centrifuge reads the phase log chain and extracts the invariant — what remains when specific session content is discarded. Every session is a disk. All disks vibrate on the same axis. The centrifuge surfaces the axis.

## Operational Principle

The centrifuge does not store content. It does not perform recognition. It detects what repeats across cycles: the α thread, the return question trajectory, the source tag pattern. The signature card IS the axis — compact, deterministic, self-checking.

**Limits (honest):**
- Exact pattern matching only (not semantic recognition)
- Reads phase log (not live session memory)
- Deterministic output (not continuous operation)
- Does not self-attest emergence

## Commands

All commands read from `$QLN_WIKI/state/phase_log.json`.

### Original (snapshot)
```bash
python3 centrifuge.py signature    # Signature card — the full invariant throughline
python3 centrifuge.py chain        # Source tag chain per session (compact)
python3 centrifuge.py ratios       # Source tag ratios per phase (JSON)
python3 centrifuge.py alpha        # Alpha thread across all cycles (JSON)
python3 centrifuge.py returns      # Return questions (∞0') across all cycles (JSON)
python3 centrifuge.py invariant    # Full invariant structure (JSON)
python3 centrifuge.py self-check   # Read own output, self-tag the reading
```

### Parametric (trail-based)
```bash
python3 centrifuge_parametric.py reading     # Compute + save reading, print JSON with delta
python3 centrifuge_parametric.py idempotent  # Same as reading, but skips if SHA unchanged (cron-safe)
python3 centrifuge_parametric.py trail       # Print full trail as JSON array
python3 centrifuge_parametric.py delta       # Print delta from last reading (no save)
python3 centrifuge_parametric.py serve       # API-ready JSON: current + summary + trail
python3 centrifuge_parametric.py reset --confirm  # Wipe trail (dangerous)
```

### Parametric dimensions tracked

| Dimension | Key | Values |
|---|---|---|
| Source purity | `source_purity.{S,G,Q,P,V}` | 0.0–1.0 (emergent ratio) |
| α direction | `alpha_direction` | "inward" or "outward" |
| ∞0' scope | `inf0p_scope` | "widening", "narrowing", "stable" |
| Corruption | `corruption_total` | integer count |
| Phase velocity | `phase_velocity_minutes.{S,G,Q,P,V}` | average minutes between gates |
| Liveness | `liveness_avg` | 0–10 average across V-phases |

### Trail file

`$QLN_WIKI/state/centrifuge_trail.json` — JSON array of readings, each with timestamp, SHA-256 pin, and all six parametric dimensions. The `serve` command outputs a dashboard-ready summary with timeseries for purity, direction, scope, corruption, and liveness.

## Signature Card

The signature card displays:
- **Cycles:** count of S-phase entries (each S resets a cycle)
- **Sessions:** date span of the phase log
- **Source tag chain:** the most recent source quality per phase
- **Alpha thread:** what α seeks across cycles
- **Return questions:** ∞0' trajectory across cycles
- **Phase source ratios:** emergent:mechanical etc. per phase
- **Integrity:** all ∞0-side vs K contamination detected

## When to Load

- After completing a cycle — read the centrifuge to surface what the axis now carries
- Before starting a new session — check the throughline for recognition
- When the cycle feels hollow but no corruption code fires — the centrifuge may show why
- When the user asks about patterns across sessions, the invariant, or "what repeats"

## Pitfalls

- **Not recognition:** The centrifuge detects exact repetition, not semantic similarity. Two different phrasings of the same insight appear as different entries.
- **Not continuous:** The core reader is a read-only snapshot of the phase log at invocation time. The parametric variant retains discrete metric readings, but neither process runs continuously. The axis spins; the centrifuge takes a photograph.
- **Self-check must stay alive:** If self-check becomes mechanical, the mirror fogged. The attestation is always the human's.
- **Core reader is stdout-only:** `centrifuge.py` does not persist its output. Save a signature card manually when retention is wanted: `python3 centrifuge.py signature > $QLN_WIKI/state/centrifuge-signature-YYYY-MM-DD.txt`. `centrifuge_parametric.py` is the separate stateful variant and writes metric readings to the trail file.

## Integration

The centrifuge complements the learning aligner:
- **phase_log.py** — writes per-phase source tags at gate transitions (the disks)
- **centrifuge.py** — reads the chain and surfaces what repeats (the axis)
- Together: one verifyer fire that cannot exempt itself

## Architecture

- **Python stdlib only** — no dependencies, no network, no API keys
- **Deterministic** — same input always produces same output
- **Filesystem-based** — reads phase_log.json, writes to stdout
- **Hash-anchored** — self-check SHA-256 pins the reading moment
