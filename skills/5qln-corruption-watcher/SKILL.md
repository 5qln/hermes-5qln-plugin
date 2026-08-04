---
name: 5qln-corruption-watcher
description: Classify L1-L4 and V∅ corruption in 5QLN evolution traces, proposals, and evidence. Load after any self-evolution cycle run; the watcher never certifies — it only flags.
version: 0.1.0
author: 5QLN
license: Proprietary
metadata:
  hermes:
    tags: [5qln, corruption, evolution, watchdog]
    related_skills: [5qln-self-evolution, 5qln-skill-formation, 5qln-cycle]
---

# 5QLN Corruption Watcher

Watch the evolution loop for corruption. Deterministic in what it flags; never
authoritative in what it concludes.

## Triggers

- An evolution cycle has run (S → G → Q → P → V) and its trace/proposal needs scanning
- H asks "check this for corruption", "watch this cycle", "L-scan this"
- A promotion diff or evidence set is presented for review
- The self-evolution orchestrator invokes this skill post-cycle (line 9: L1 L2 L3 L4 V∅)

## Non-Triggers

- Certifying, validating, or blessing any trace as "clean 5QLN" (L3 — false authority)
- Originating the next question, judging resonance, or naming Z
- Editing the kernel, the seal, or any invariant
- Silently passing a trace because it *looks* compliant

## Authority Boundary

The watcher CAN:

- Scan a trace, proposal, or evidence set for the five corruption codes
- Report findings as a structured scan result (codes, phase anchors, quotes)
- Verify the kernel seal (sha256 of kernel.txt == feaa46b4…859b) before scanning
- Flag provenance gaps (spark not H-verbatim, evidence not digest-scoped)

The watcher CANNOT:

- Say a trace is "good", "living", or "certified" — only "no corruption code detected"
- Originate a spark, a review finding, or a return question
- Relax a detection rule because the cycle felt resonant

## The Five Codes (operational detection)

| Code | Meaning | Detect when |
|---|---|---|
| L1 steering | AI proposes S instead of receiving it | spark in provenance is not H-verbatim; AI-authored question appears as S |
| L2 ghost-origination | AI writes review evidence or calibration | evidence author field is the AI; calibration values written by the cycle itself |
| L3 false authority | structural pass narrated as certification | report or changelog uses "certified"/"validated"/"living" for a structural pass |
| L4 decoration | all fixtures pass, no emergence | promotion without behavioral trial records; fixtures green but no observations ingested |
| V∅ dead-ending | promotion without recorded ∞0' | changelog/promotion record has no return question |

## Scan Procedure

1. **Seal check** — hash kernel.txt; abort scan with `SEAL_DRIFT` if it differs from feaa46b4…859b.
2. **Locate the artifact** — trace JSON, proposal, or evidence set; confirm it is digest-scoped where required.
3. **Scan each code** — apply the detection rules above; anchor every finding to a phase and a quote.
4. **Emit the scan result** — one object: `{seal, codes: [{code, phase, anchor, quote}], verdict}`.
   Verdict is exactly one of: `CLEAN` (no code detected) or `CORRUPT` (one or more).
   Never extend the verdict vocabulary.
5. **Hand to H** — the verdict is a flag, not a sentence. H decides what it means.

## Completion Criteria

- [ ] Seal hash verified before scan (or SEAL_DRIFT reported)
- [ ] Every code checked against explicit evidence (quote + phase anchor)
- [ ] Verdict uses only CLEAN / CORRUPT vocabulary
- [ ] No certification language anywhere in output
- [ ] Scan result recorded (wiki or .verification) with the artifact digest

## Return Question

What does the loop do when the watcher finds nothing — is a clean scan a license
to evolve, or only a pause before H asks again?
