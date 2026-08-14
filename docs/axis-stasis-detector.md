# Axis Stasis Detector — User Guide

## What it is

An alarm for the axis. The centrifuge measures where the 5QLN axis points;
this detector watches that trail and tells you when the axis has stopped
turning while the cycle keeps running — a loop that works, but repeats its
own direction. It is the machine half of Karpathy's Bilevel idea: the level
that notices "the search keeps doing the same thing."

## How to use it

Ask the agent, in plain words:

- "check the axis"
- "run the stasis check"

The agent runs:

```bash
python3 skills/5qln-centrifuge/scripts/axis_stasis.py check
```

## What you'll see — one of four words

| Verdict | What it means | What to do |
|---|---|---|
| **STASIS** | The axis did not move for the last K readings, while new work happened | The alarm. You decide what it means |
| **MOVING** | The axis changed | Nothing |
| **STILL** | Nothing moved and no new work happened | The loop simply hasn't run |
| **INSUFFICIENT_DATA** | Not enough readings to judge | Wait for more cycles |

## What STASIS means — and what is yours to decide

The detector **flags. It never changes anything by itself.** If you want to
act on a STASIS: ask the agent to draft a search-policy change. It drafts —
**you approve** — and only then does anything get injected. Automatic
injection is exactly what this design refuses (it is the known failure of the
Bilevel: the loop rewriting itself with nobody watching).

## Honest limits

- The detector is only as true as the centrifuge's heuristics (word-based
  direction measures). Treat STASIS as a reason to look, not as proof.
- It does not touch corruption. Corruption stays the corruption watcher's job.

## Where it lives

Shipped in the 5QLN plugin (0.12.0): `skills/5qln-centrifuge/scripts/axis_stasis.py`,
with 13 unit tests in `test_axis_stasis.py` next to it.
