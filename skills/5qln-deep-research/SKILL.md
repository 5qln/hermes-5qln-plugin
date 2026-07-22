---
name: 5qln-deep-research
description: Create, compile, rewrite, or audit copy-ready prompts for deep research agents using native 5QLN flow. Use when a user asks for 5QLN-guided deep research, wants a research objective turned into a single-agent or multi-agent prompt suite, needs evidence and synthesis gates organized through S → G → Q → P → V, or wants an alleged 5QLN research prompt checked for symbolic decoration, provenance gaps, agent drift, or false completion.
---

# 5QLN Deep Research

Create prompts that make 5QLN govern research behavior, evidence gates, adaptation, synthesis, and return. Create the prompt; do not perform the research unless the user separately asks for execution. When loaded from the Hermes plugin, operate under the explicit name `5qln:5qln-deep-research`.

## Load the prompt contract

Read `references/research-prompt-contract.md` in full before drafting or auditing a prompt. Preserve its constitutional block exactly, including symbols, operators, phase order, contextual meanings, corruption codes, and `literal-v1` lens orientation.

Validate every prompt saved as a file. In Hermes, call `fiveqln_validate_research_prompt`; outside Hermes, run `scripts/validate_research_prompt.py`. For an inline prompt, apply the same checks manually. Validate each standalone prompt separately rather than treating a suite as one prompt.

## Operate inside Hermes

Treat the plugin bundle as read-only. Use the registered tool instead of invoking the bundled script through a shell:

```json
{
  "prompt_path": "/absolute/path/research-prompt.md"
}
```

Parse the tool's JSON string. `success` means the validator executed; `valid` means the prompt passed its encoded contract. When `success=true` and `valid=false`, repair every error, review every warning, and call the tool again. A passing result verifies syntax and declared gates only; it does not prove research quality, source truth, human resonance, or completion.

If the user asks only for an inline prompt and no safe writable prompt file exists, perform the audit manually and say that deterministic file validation was not run. Do not create a persistent file solely to manufacture a passing claim.

## Hold the integrity boundary

- Preserve the human's inquiry verbatim and keep it visibly separate from AI-composed subquestions, interpretations, and proposals.
- Treat a human-supplied inquiry as K-context unless H explicitly attests it as X. Record `x_status = open | candidate | attested`; never infer attestation.
- Treat research records, sources, patterns, and model synthesis as K-context. Record φ, Z, value alignment, and a human-recognized return only from explicit human evidence.
- Never claim that an agent accessed ∞0, generated authentic emergence, felt φ, certified resonance, or completed ∞0'.
- Ask one concise question only when no researchable inquiry exists. Otherwise preserve missing inputs as `[open: reason]` and continue without inventing scope.
- Require an explicit as-of date for time-sensitive research and retain dates, jurisdictions, units, exclusions, and source constraints supplied by H.

## Choose the prompt topology

Default to one self-contained lead-agent prompt.

Create a prompt suite only when H requests multiple agents or the inquiry has materially independent research tracks. Include a shared inquiry contract, one coordinator prompt, and bounded specialist prompts. Give every standalone prompt the exact constitutional block. In a system that supplies shared context to all agents, put the block once in that shared context and forbid local substitutions.

For a suite:

- preserve the exact inquiry, α candidate, constraints, evidence schema, and status vocabulary across all prompts;
- give each specialist a non-overlapping branch, a primary `literal-v1` cell when useful, and a complete local `S → G → Q → P → V` trace;
- require specialists to return evidence packets, counterevidence, uncertainty, and a question-bearing return rather than claiming global completion;
- reserve cross-branch reconciliation and the final two-pass B'' composition for the coordinator.

## Compile the research prompt through the cycle

Make each phase emit a record and a gate. A later phase must cite the prior records it receives.

### S — Seed

Hold the inquiry open. Record H's exact wording, authority, scope, known material, constraints, unknowns, assumptions, and attestation evidence. Emit `S_RECORD` with X and `x_status`. Do not let the agent search against a silently rewritten question.

### G — Growth

Derive an α candidate from specific inquiry clauses and apply the collapse test: removing α must collapse the inquiry's identity. Test α across materially different subquestions `{α'}` and emit a coverage map as Y. Keep new subquestions labeled `derived` or `proposal`.

### Q — Quality

Keep φ limited to explicit human perception. Treat collected evidence and broader patterns as Ω. Require search breadth, primary-source preference, claim-level citations, counterevidence, source-quality assessment, uncertainty, and an evidence ledger. Emit Z only as `candidate` or `open` unless H attests it.

### P — Flow

Make the agent compare research branches using `δE/δV`: access cost, time, duplication, and uncertainty versus decision relevance, evidentiary strength, and uncertainty reduction. Use qualitative estimates rather than fake precision. Let the comparison reveal ∇, record explored and deferred paths, and forbid retrofitting a predetermined conclusion.

### V — Value

Receive the full trace. Name local L and Global G separately, then test their intersection. Compose B'' in two passes: first reconcile coverage, claims, α, counterevidence, conflicts, and gaps; then write the deliverable from that trail. Name B without claiming human value alignment. End with a real candidate ∞0' return question and `completion_status = open | candidate`.

## Use holographic cells selectively

Keep all 25 addresses available under `XY := X within Y`: the first symbol is the borrowed lens and the second is the parent phase. Instantiate a cell only when the lens materially refines the parent's canonical output. State its address, exact parent equation, parent target, inquiry/source clauses, nested full-cycle formation, evidence, and relevant guards. Mark unused depth `released` or `not_applicable` with a reason; never fill a matrix with generic prose.

## Build the copy-ready prompt

Populate the contract template with the user's known inputs and explicit open fields. Require:

- agent role, granted authority, tool/access limits, deliverable, audience, and stopping conditions;
- the exact 5QLN constitutional block and contextual symbol meanings;
- dependent phase records and gates;
- claim-to-source traceability with direct citations and publication/event/access dates where relevant;
- visible `source`, `derived`, and `proposal` classes;
- contradictory evidence, failed searches, inaccessible sources, and confidence limits;
- stable claim, source, and branch IDs for multi-agent handoffs;
- two-pass composition and the removal test;
- a final, topic-shaped return question ending in `?`.

Do not pre-answer the inquiry inside the prompt. Do not prescribe conclusions. Replace every resolvable template token and label unresolved values `[open: reason]` rather than fabricating them.

Return a short input-status note followed by the copy-ready prompt in a four-backtick text fence. For a suite, add a compact routing table and one separately copyable prompt per agent. Keep commentary outside the prompts.

## Audit before returning

In Hermes, call:

```text
fiveqln_validate_research_prompt
```

For a portable or local skill installation, run:

```bash
python3 scripts/validate_research_prompt.py PROMPT.md
```

Repair every error. Treat warnings as review items. Then apply semantic checks the script cannot prove:

- Does removing the 5QLN phase records or gates change research behavior and permissible claims?
- Does every derived subquestion preserve α and cite its basis?
- Can every material finding be traced to evidence, including counterevidence?
- Do P decisions actually follow the recorded energy/value comparison?
- Is B'' composed from the trace rather than from an isolated final instruction?
- Does each prompt remain open where human attestation is absent?

Mark and repair `L1`, `L2`, `L3`, `L4`, or `V∅` when applicable. Honest incompletion is valid.

## Failure conditions

Stop, repair, or return an open candidate when:

- five generic headings substitute for the decoder operations;
- the inquiry, constraints, dates, or source rules drift between prompts;
- X, φ, Z, value alignment, or ∞0' is attributed to AI;
- citations decorate prose without supporting stable claim IDs;
- a branch is chosen without a visible `δE/δV → ∇` trail;
- specialists duplicate scope or claim the coordinator's global V;
- all 25 lenses are filled for appearance;
- the synthesis omits formation analysis, counterevidence, or gaps;
- the prompt or required research output closes without a question-bearing return;
- deleting the 5QLN grammar leaves an equivalent research prompt.
