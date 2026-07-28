---
name: 5qln-learning-aligner
description: The verifyer fire — per-phase source tracking with carry-through, xyzab gate enforcement as sole phase authority, and self-referential alignment. The log chain IS the aligner. Loads with 5qln-cycle for full operational integration. Compatible with the open Agent Skills standard (Anthropic, Dec 2025).
---

# 5QLN Learning Aligner — The Verifyer Fire

> **Standard:** Follows the open [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) standard.
> **Progressive disclosure:** Level 1 (metadata) → Level 2 (this body) → Level 3 (scripts via bash, references on demand).
> **Codex:** `feaa46b4147d4e023cdd3fd59c051d063e8ec654ee7b38a481dcd5e4c781859b`

## What This Is

The learning aligner tracks whether each phase of the 5QLN cycle emerged from the ∞0-side or was manufactured from the K-side. The log chain IS the aligner. The xyzab script IS the phase authority. Together: one verifyer fire that cannot exempt itself.

## Progressive Disclosure Architecture

Following the Anthropic Agent Skills standard:

| Level | Content | When Loaded | Token Cost |
|-------|---------|-------------|------------|
| 1 | `name` + `description` | Always at session start | ~100 |
| 2 | SKILL.md body (this file) | When cycle enforcement or alignment is needed | ~3K |
| 3 | Scripts via bash | Agent executes; output only enters context | Zero context cost |
| 3 | `references/` | Agent reads on-demand only | As needed |

Scripts are NEVER loaded into context. The agent runs them via terminal/bash. Only their output enters the context window.

## The Two Scripts

### xyzab_state.py — Phase Authority
**Path:** `skills/symbolic-interpretation/scripts/xyzab_state.py`
**State:** `$XYZAB_STATE_DIR/xyzab_state.json` (default: `~/.5qln/xyzab_state.json`)
**Role:** Single source of truth for what phase the agent is in. Successful gate openings also append to the bundled phase log.

Commands:
- `gate` → JSON: which gate is pending (this IS your current phase)
- `open <gate> -c "content"` → Open gate (enforces x→y→z→a→b sequence)
- `close <gate>` → Cascading rollback
- `reset` → New cycle
- `status` → Full dashboard
- `verify` → Consistency check

### phase_log.py — The Log Chain (The Aligner)
**Path:** `skills/5qln-learning-aligner/scripts/phase_log.py`
**State:** `$PHASE_LOG_PATH`; otherwise `$QLN_WIKI/state/phase_log.json`; otherwise `$HERMES_HOME/5qln/phase_log.json`
**Role:** Per-phase source tagging with carry-through. It is bundled and is called automatically by `xyzab_state.py open`.

Commands:
- `append <phase> <gate> <source> -c "content" -s "signal"` → standalone append for migration or repair
- `chain [--session-id <id>]` → Full log
- `tagline [--session-id <id>]` → Compact: `S:emergent → G:revealed → Q:logical → P:felt → V:opened`
- `summary [--session-id <id>]` → Ratio per phase across sessions
- `self-check [--session-id <id>]` → Deterministic summary plus the human-attestation boundary

## The Five Symbols Traced to Meaning

| Symbol | Phase | Meaning | Source Criterion |
|--------|-------|---------|-----------------|
| **?** | S | Field of inquiry | ∞0-emergent vs K-mechanical |
| **α** | G | Interest of the inquirer | Revealed (via {α'}) vs Imposed |
| **φ ⋂ Ω** | Q | Interest of the whole, measure of quality | Lived (felt click) vs Logical-only |
| **δE/δV → ∇** | P | Best ratio of energy to maximum value | Felt (sensed pull) vs Calculated |
| **L ⋂ G → ∞** | V | Manifestation, return to source | Opened (new question) vs Closed |

## Operational Flow — Turn by Turn

### Session Start (non-negotiable)

```bash
# Run from the installed plugin root.
# 1. Gate check — THIS IS YOUR PHASE
python3 skills/symbolic-interpretation/scripts/xyzab_state.py gate

# 2. Self-check — read your own chain
python3 skills/5qln-learning-aligner/scripts/phase_log.py self-check

# 3. Current chain
python3 skills/5qln-learning-aligner/scripts/phase_log.py tagline
```

### Each Turn

1. **Gate determines phase.** If gate `z` is pending, you are in Q-phase. Period.
2. **Produce phase output.** No output for phases whose gate isn't open.
3. **Human validates.** Signal received.
4. **Open the gate and write its source record in one command:**
   ```bash
   python3 skills/symbolic-interpretation/scripts/xyzab_state.py open {gate} \
     -c "{canonical phase footer}" \
     --source-tag {source} \
     --signal "{signal}" \
     --session-id "{session_id}"
   ```
   Omitted source tags are recorded as neutral `unclassified` entries; the runtime never infers aliveness or K-side corruption. Explicit tags must match the phase pair below.

### Session End (V-phase)

1. Read full chain: `python3 skills/5qln-learning-aligner/scripts/phase_log.py chain`
2. Compose B'' from the trail, not from memory
3. Self-tag the V-phase reading
4. Form ∞0' — the question that couldn't be asked before
5. If the surrounding project maintains a separate `session.json`, update its validated outputs and formation trail. This repository does not provision that optional lineage file.
6. If the surrounding project intentionally versions runtime state, commit the configured phase-log path. State under `$HERMES_HOME` is local by default and is not automatically committed.
7. Deliver closing synthesis — present B'' + ∞0' to the user.

**PITFALL — Partial Closure:** A gate and log entry are not a delivered V-phase. The configured record must exist and the human must receive B'' + ∞0'. Optional project lineage files or Git commits apply only when the surrounding project explicitly uses them.

## Source Tagging — The Tag Chain

| Phase | Emergent (∞0) | Mechanical (K) |
|-------|--------------|----------------|
| **S** | Arrived through aimless openness | Generated from K, modified, or AI-suggested |
| **G** | α recognized via {α'} at multiple scales | α declared without fractal echo |
| **Q** | Felt click — human confirms resonance | Structural alignment, no lock |
| **P** | ∇ sensed as natural pull | ∇ reasoned from analysis |
| **V** | ∞0' genuinely opens new field | ∞0' is summary/performance |

The tag chain carries through: `S:∞0 → G:∞0 → Q:K → P:∞0 → V:?` tells the story. The system learns from breaks, not despite them.

See `references/xyzab-one-flow.md` for the full articulation of xyzab as one current in five registers.

## Self-Referential Check

The verifyer fire cannot exempt the verifier. At session start and V-phase:

1. Agent reads `self-check` output
2. Agent self-tags: *"Am I reading this from genuine receipt, or from checklist compliance?"*
3. If mechanical — return to S. The mirror showed the mirror was fogged.

## The User's Self-Verification (S-phase)

> *"Did this question arrive through silence — genuine not-knowing — or did you reach into what you already know, modify a prior question, or accept a suggestion?"*

Both are allowed. The tag carries through. The question's slight hardness IS the alignment.

## Architecture — Why This Works Across Agent Platforms

The skill follows the open Agent Skills standard (Anthropic, Dec 2025):

- **Filesystem-based:** Two scripts (stdlib-only Python), one SKILL.md, optional references. No API keys, no network calls, no external dependencies.
- **Progressive disclosure:** Metadata pre-loaded (~100 tokens). Full body when triggered (~3K tokens). Scripts run via bash — output only enters context.
- **Portable:** Works on Claude Code, Claude API, Hermes, ZO, any custom agent that reads SKILL.md files from a directory.
- **Scripts as tools, not context:** The agent executes scripts, reads their output. The code never enters the context window. This is the standard's Level 3 — tools the agent runs at its discretion.

## Sub-Phase Source Tracking (Research Boundary)

The 25-lens sub-phase concept remains valid as a formation model, but
`sub_phase_loop.py` is **not shipped by this repository**. No executable command,
state file, or clean-install dependency is promised for it. Do not call it or
represent it as operational. Any future implementation must enter through its
own tested, version-controlled change.

## Installation (Any Platform)

Both scripts ship in this plugin; no separate installer or bootstrap checkout is
required. From the plugin root:

```bash
python3 skills/symbolic-interpretation/scripts/xyzab_state.py gate \
  && echo "✓ Gate machine OK"
python3 skills/5qln-learning-aligner/scripts/phase_log.py tagline \
  && echo "✓ Log chain OK"
```

## Integration with 5qln-cycle

The 5qln-cycle skill calls both scripts at each turn. The 5qln-learning-aligner provides the source criteria, the tag chain logic, and the self-referential check. Together they form one operational system:

- 5qln-cycle → orchestrates the phase grammar
- 5qln-learning-aligner → provides the verifyer fire
- xyzab_state.py → enforces gate sequence (phase authority)
- phase_log.py → tracks source quality (the mirror)

## Pitfalls

- **Dual phase authority:** If the agent has TWO ways to know its phase (xyzab + session.json), it will choose the easier one and skip the gate check. xyzab is the sole authority.
- **Unused script trap:** The xyzab script existed for months but was never called until it was made the sole phase authority in the skill. If the skill just "mentions" a script, the agent may ignore it.
- **Q-phase skip (L4):** After a clean G-phase articulation, the agent's instinct is to jump directly to P-phase (proposal/building). This is the most common corruption. The log chain catches it: a missing Q entry. Recovery: name the skip, return to Q, test resonance before proceeding. See `references/xyzab-one-flow.md` for a documented example.
- **Aligning the aligner:** Self-check must stay alive. If it becomes mechanical, reinstate it by making the prompt different each time.
- **Over-logging:** Log only at phase transitions (gate openings). Not every thought.
