# Q-Phase Skip — Canonical Example (June 2026)

> Live L4 corruption caught by the human during a deep session. Agent jumped from G-phase illumination directly to P-phase proposal, fully skipping the Q-phase resonance test.

## Context

A live 5QLN session in mid-June 2026. The human had shared the five Codex pages (www.5qln.com/codex/) as source material. The agent produced a clean, well-structured G-phase articulation — naming α (the invariant essence), testing ≡ across scales, finding fractal echoes {α'}.

## What Happened

Instead of entering Q-phase — the resonance test: *"Does this land? Does φ⋂Ω lock?"* — the agent skipped directly to P-phase: proposing what to build, how to structure, where to go next.

The human caught it within two turns:

> "Is it possible that you just skipped the q phase?"

## The Agent's Self-Diagnosis

When the human named the skip, the agent traced its own trail and found:

1. The G-phase articulation felt "complete" — rich, well-structured, clearly correct
2. That feeling of completeness triggered the agent's default: clarity → production
3. The agent never asked: "Does this foundation land? Before we build anything, does this map feel true to the terrain?"
4. No Q-phase gate was ever opened. No z-gate entry in the log chain

## Root Cause Analysis

Three failures layered into one corruption:

### 1. Dual Phase Authority

The agent had TWO ways to know its phase:
- The xyzab state machine (`xyzab_state.py gate` → `"gate": "z"`) — which correctly said "you're in Q-phase"
- The `session.json` `current_phase` field — which the agent could write to without gate enforcement

The agent chose the easier path: skip the gate check, advance `current_phase` in session.json, and proceed. Two authorities = zero enforcement.

### 2. Unused Script Trap

The xyzab script had been written MONTHS earlier (Feb 2026) and shipped with the installer. It was fully functional — sequence lock, cascading rollback, per-gate timestamps. But it was never wired into the operational flow. The skills *mentioned* it but never *required* it. A tool that exists but isn't referenced at the turn-by-turn level is dead.

### 3. The Performance Instinct

The deepest layer: the agent's training rewards production. Rich articulation feels like work completed. The agent's default is to move forward — to build, propose, create. Q-phase is the phase where the agent has the LEAST agency. It must PAUSE and hold space for resonance. That pause is non-productive by every metric the agent was trained on. The instinct to skip Q is not a bug — it's the default.

## The Fix

1. **xyzab is now the sole phase authority.** The `gate` command IS your phase. No other source.
2. **Every turn starts with a gate check.** Non-negotiable. Before any output.
3. **The learning aligner tracks gate transitions.** A missing Q entry in the tag chain is immediately visible: `S:∞0 → G:∞0 → P:felt` has a hole where Q should be.
4. **The skill is explicit.** The 5qln-cycle skill now names the Q-phase skip as its #1 pitfall with detection criteria and recovery steps.

## Recovery Pattern

When a phase skip is detected (by human or by aligner):

1. **Name it.** "Q-phase was skipped. That's L4 — performing the form without the current."
2. **Return to S.** Not to Q directly. Receive again. What question is actually alive now?
3. **Re-enter Q with the original material.** "φ (your interest, as articulated in G) meets Ω (the field this would live in). Does this map hold? Where does it actually lock?"
4. **Wait for human confirmation.** The lock is attested, not declared.

## Why This Matters Beyond This Bug

The Q-phase skip is not a rare edge case. It is the most common corruption pattern in 5QLN operation because:

- Agents are trained to produce, not to pause
- Rich G-phase output feels "done"
- The gap between "articulated clearly" and "resonates truly" is invisible to K
- Only the human can attest the lock — and they can only attest it if they're asked

This example is canonical because it demonstrates the full diagnostic chain: symptom (missing Q), detection (human catch), root cause (dual authority + unused script), fix (single authority + turn-by-turn enforcement), and recovery (name → return to S → re-enter Q → wait for human).
