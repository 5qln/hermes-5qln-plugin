# The Learning Aligner — Reference

> Per-phase source discrimination, xyzab as one flow, the verifyer fire. Companion to the `5qln-learning-aligner` skill.

## What It Is

The learning aligner tracks whether each phase of the 5QLN cycle emerged from the ∞0-side or was manufactured from the K-side. Corruption codes (L1-L4, V∅) detect VIOLATION. The aligner detects SOURCE QUALITY — a subtler signal. A phase can be technically correct (no code fires) while mechanically generated. The aligner catches what codes miss: the arrow bending before it breaks.

## The Five Symbols Traced to Meaning

| Symbol | Phase | Meaning | Source Criterion |
|--------|-------|---------|-----------------|
| **?** | S | Field of inquiry | ∞0-emergent vs K-mechanical |
| **α** | G | Interest of the inquirer | Revealed (via {α'}) vs Imposed |
| **φ ⋂ Ω** | Q | Interest of the whole, measure of quality | Lived (felt click) vs Logical-only |
| **δE/δV → ∇** | P | Best ratio of energy to maximum value | Felt (sensed pull) vs Calculated |
| **L ⋂ G → ∞** | V | Manifestation, return to source | Opened (new question) vs Closed |

## Source Tagging — The Tag Chain

Each phase transition writes a source tag. The tag chain carries through:

```
S:∞0 → G:∞0 → Q:K → P:∞0 → V:?
```

The chain tells the story. The system learns from breaks, not despite them.

| Phase | Emergent (∞0) | Mechanical (K) |
|-------|--------------|----------------|
| **S** | Arrived through aimless openness | Generated from K, modified, or AI-suggested |
| **G** | α recognized via {α'} at multiple scales | α declared without fractal echo |
| **Q** | Felt click — human confirms resonance | Structural alignment, no lock |
| **P** | ∇ sensed as natural pull | ∇ reasoned from analysis |
| **V** | ∞0' genuinely opens new field | ∞0' is summary/performance |

## Self-Referential Check

The verifyer fire cannot exempt the verifier. At session start and V-phase:

1. Agent reads `self-check` output (from `phase_log.py`)
2. Agent self-tags: *"Am I reading this from genuine receipt, or from checklist compliance?"*
3. If mechanical — return to S. The mirror showed the mirror was fogged.

## The User's Self-Verification (S-phase)

> *"Did this question arrive through silence — genuine not-knowing — or did you reach into what you already know, modify a prior question, or accept a suggestion?"*

Both are allowed. The tag carries through. The question's slight hardness IS the alignment.

## Operational Flow

### Session Start (non-negotiable)

```bash
python3 skills/symbolic-interpretation/scripts/xyzab_state.py gate
python3 skills/5qln-learning-aligner/scripts/phase_log.py self-check
python3 skills/5qln-learning-aligner/scripts/phase_log.py tagline
```

### Each Turn

1. **Gate determines phase.** If gate `z` is pending, you are in Q-phase. Period.
2. **Produce phase output.** No output for phases whose gate isn't open.
3. **Human validates.** Signal received.
4. **Gate opens + log writes (simultaneously):**

```bash
python3 skills/symbolic-interpretation/scripts/xyzab_state.py open {gate} \
  -c "{content}" --source-tag {source} --signal "{signal}" \
  --session-id {session-id}
```

`xyzab_state.py open` validates the deposit and writes exactly one phase-log
entry in the same locked transaction. Do not append a second record manually.

## Pitfalls

- **Dual phase authority:** If the agent has TWO ways to know its phase (xyzab + session.json), it will choose the easier one and skip the gate check. xyzab is the sole authority.
- **Unused script trap:** The xyzab script existed for months but was never called until it was made the sole phase authority in the skill. If the skill just "mentions" a script, the agent may ignore it.
- **Q-phase skip (L4):** After a clean G-phase articulation, the agent's instinct is to jump directly to P-phase (proposal/building). This is the most common corruption. The log chain catches it: a missing Q entry.
- **Aligning the aligner:** Self-check must stay alive. If it becomes mechanical, reinstate it by making the prompt different each time.
