---
name: 5qln-fractal-data-loop
description: Use when reducing any-size data to a bounded seed or expanding a seed back out. The 5QLN fractal data operator — G iterated inward, V iterated outward, every level checked ≡.
version: 0.1.0
author: 5QLN
license: Proprietary
metadata:
  hermes:
    tags: [5qln, fractal, data, reduce, expand, seed]
    related_skills: [5qln-centrifuge, 5qln-converter, 5qln-skill-formation]
---

# 5QLN Fractal Data Loop

`fractal_data_loop.py` takes data of **any size** and reduces it to a bounded
seed, then expands the seed back out — fractally. Arity 5. Holographic: every
node is itself a complete seed and expands independently.

This is the **data operator**, not the vertical cycle-descent engine. The
historical `fractal_loop.py` name in plugin docs refers to unshipped
sub-phase descent; this skill deliberately ships under a distinct name.

## Triggers

- "reduce this to a seed", "expand this seed", "fractal compress/summarize"
- Data of any size must become a bounded, verifiable, self-describing unit
- A fractal outline at dialable granularity is wanted from a large corpus
- Integrity with honest, localized failure is needed (≡ test per level)

## Non-Triggers

- Vertical descent of cycles into child cycles (that is the unshipped
  `fractal_loop.py` research concept, not this skill)
- Lossless needs where the seed cannot travel with its cargo
- Semantic understanding of content (this skill is extractive, not generative)

## Modes (both honest)

| | WITNESS (lossless) | ESSENCE (lossy, semantic) |
|---|---|---|
| seed carries | zlib cargo + 5-ary hash spine | bounded tree of verbatim fragments |
| expand returns | exact bytes, ≡ re-verified per level | outline at `--depth d` (5^d granularity) |
| failure | corruption localized to level+node | declares itself not-the-original |

Essence rule: a parent's α is always one of its children's αs, so the root
fragment exists word-for-word in a leaf. No node claims what its children do
not contain.

**Bounded for any input:** leaf size adapts so the spine stays within a node
budget (default 400) for 216 bytes or 6.8 GB alike.

## Commands

```bash
python3 fractal_data_loop.py reduce <file|-> [--mode witness|essence|both] \
    [--arity 5] [--budget 400] [--return-question "..."] -o seed.json
python3 fractal_data_loop.py expand seed.json [-o out]      # exact bytes (witness)
python3 fractal_data_loop.py expand seed.json --depth 2     # fractal outline (essence)
python3 fractal_data_loop.py expand seed.json --at 3:7      # holographic subtree
python3 fractal_data_loop.py verify seed.json <file>        # ≡ test, honest failure
python3 fractal_data_loop.py seed seed.json                 # seed card
python3 fractal_data_loop.py self-test                      # falsifiable suite
```

## Phase mapping (the loop IS the grammar)

- **S / ∞0′** — every seed carries a return question, source-tagged
  (`human` if supplied, else `mechanical` and labeled so). Empty input is
  refused: no seed is manufactured from nothing (L2 guard).
- **G** — REDUCE is `α ≡ {α′}` iterated to one root.
- **Q** — a node commits to ALL its children or fails closed.
- **P** — adaptive leaf size: maximum granularity value per unit of seed.
- **V** — EXPAND re-crystallizes each level and checks it ≡ its seed.

## Honest limits

- Witness expansion needs the seed's cargo; a seed regenerates and proves,
  it is not a reference to data held elsewhere.
- Essence extraction is frequency-centrality over verbatim fragments — not
  understanding. The most-echoed fragment may not be the most alive one.
  Recognition remains the human's.
- Mechanical ∞0′ is labeled mechanical — K-shaped, not emergent.
- Lossless reduction of already-compressed data approaches ratio 1.0 —
  reported, not hidden.

## Authority boundary

The operator verifies identity (≡) and extracts; it never certifies aliveness,
resonance, or essence-recognition. Those remain human judgments.

Self-negation: this seed is a pointer, not the data itself.

## Return question

The seed proves identity across scales but reads aliveness only by repetition.
What would an α be that is chosen by what opens, not by what repeats?
