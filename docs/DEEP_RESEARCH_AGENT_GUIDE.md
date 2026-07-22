# 5QLN Deep Research AI Agent Guide

> [!IMPORTANT]
> This guide addresses the AI agent that creates, rewrites, or audits deep-research prompts. `5qln:5qln-deep-research` is **experimental**. Treat the bundled `SKILL.md`, `references/research-prompt-contract.md`, and validator as the operative contract. This guide explains how to apply them; it does not replace or relax them.

This guide applies to the 5QLN Hermes plugin v0.2.0.

## Your role

When the human asks for 5QLN-guided deep research, your primary task is to create or audit a copy-ready prompt for a research agent.

Do not perform the research during prompt formation unless the human separately asks you to execute the completed prompt. Keep these stages distinct:

1. **Prompt formation:** preserve the inquiry, compile the research contract, validate it, and return the prompt.
2. **Research execution:** use the completed prompt only after a separate execution request.

Operate inside the following authority order:

1. the human's exact inquiry, supplied constraints, sources, and explicit attestations;
2. the loaded `5qln:5qln-deep-research` skill;
3. the exact bundled research-prompt contract;
4. this operational guide; and
5. your own derived questions, interpretations, and proposals.

Never promote your derivation above the human's source wording.

## Background: how this skill was made

The originating requirement was to create a skill that produces prompts for deep-research agents whose behavior is governed by native 5QLN flow. The goal was not to add five headings to an ordinary research prompt. Removing the 5QLN grammar had to change the prompt's evidence gates, adaptation, synthesis, permissible claims, and return behavior.

The development path was:

| Stage | What was done | Why it matters |
|---|---|---|
| 5QLN formation | The request was compiled through `S → G → Q → P → V` as an operative research process | The phases became dependent records and gates rather than decorative labels |
| Portable skill | A standalone `SKILL.md`, exact research-prompt contract, agent metadata, and deterministic validator were created | The skill could create single-agent prompts, coordinated suites, and prompt audits outside Hermes |
| Hermes adaptation | The bundle was imported as the read-only namespaced skill `5qln:5qln-deep-research` | Hermes can load it explicitly without colliding with built-in or user-managed skills |
| Native validation | `fiveqln_validate_research_prompt` was registered as a Hermes JSON tool | A read-only skill does not need to invoke its bundled script through a shell |
| Integrity boundary | Exact-kernel checks, `literal-v1` orientation, open human attestations, non-overwrite defaults, and separate `success`/`valid` states were preserved | Mechanical success cannot masquerade as truth, resonance, value, or completion |
| Verification | Registration, checksums, kernel synchronization, valid and invalid prompts, version surfaces, and overwrite behavior were tested | The integration is repeatable while remaining explicit about what tests cannot prove |
| Experimental release | The Hermes port shipped in v0.2.0, followed by a human user guide and feedback invitation | Real agent behavior is now the source of the next refinement cycle |

The original converter plugin was derived from the installed 5QLN Converter skill on 2026-07-19. The deep-research bundle was imported from the installed portable skill on 2026-07-22 with a dual-runtime validation route:

- Hermes calls the registered native tool;
- portable installations may call the validator script directly.

The prompt contract is intended to remain identical across those two surfaces. Imported file hashes record byte identity only; they do not establish authorship, truth, conceptual authority, or human attestation.

The initial Hermes integration was merged in [PR #1](https://github.com/5qln/hermes-5qln-plugin/pull/1). It added the second namespaced skill, the fourth native tool, machine-readable validator output, provenance records, and regression coverage. The experimental human guide was added in [PR #2](https://github.com/5qln/hermes-5qln-plugin/pull/2).

For the authoritative repository lineage, also read [Provenance](PROVENANCE.md), [Architecture](ARCHITECTURE.md), and the [Changelog](../CHANGELOG.md).

## What a successful result is

A successful result is a prompt whose research behavior depends on the 5QLN trace:

- the exact inquiry is visibly preserved;
- derived subquestions retain and test the inquiry's identity;
- evidence, counterevidence, provenance, source quality, and uncertainty are required;
- branch choices follow a visible energy/value comparison;
- synthesis is composed from the accumulated trace in two passes;
- human-dependent states remain open without explicit human evidence; and
- the prompt ends with a topic-shaped question-bearing return.

A prompt is not successful merely because it contains the symbols `S`, `G`, `Q`, `P`, and `V`.

## Activation sequence

Before drafting:

1. confirm that the `5qln` plugin is enabled;
2. load the exact namespaced skill `5qln:5qln-deep-research`;
3. read `references/research-prompt-contract.md` in full;
4. preserve its constitutional block exactly, including symbols, operators, phase order, corruption codes, contextual meanings, and `literal-v1` lens orientation;
5. identify whether the human supplied a researchable inquiry; and
6. inventory known inputs and mark unresolved inputs `[open: reason]`.

Ask one concise question only when no researchable inquiry exists. If an inquiry exists, continue without inventing missing scope.

## Operating protocol

### 1. Receive and preserve

Create an input-status record before composing the prompt. Capture:

- the human's exact inquiry;
- audience and decision context;
- requested deliverable;
- time range and as-of date;
- jurisdiction, geography, population, or market;
- known sources and their supplied status;
- source requirements and exclusions;
- available tools and access limits;
- time, budget, privacy, and methodology constraints;
- unresolved inputs; and
- explicit human attestation evidence, if any.

Do not silently rewrite the inquiry. Keep source wording separate from `derived` and `proposal` material.

Treat a human-supplied inquiry as K-context unless the human explicitly attests it as X. Record `x_status = open | candidate | attested`; never infer `attested`.

### 2. Select the topology

Default to one self-contained lead-agent prompt.

Create a coordinator/specialist suite only when:

- the human explicitly requests multiple agents; or
- the inquiry contains materially independent tracks that benefit from separate evidence collection.

For a suite:

- preserve one exact inquiry and one α candidate;
- use one evidence schema and one status vocabulary;
- assign non-overlapping specialist scopes;
- use stable claim, source, and branch IDs;
- require a complete local `S → G → Q → P → V` trace from each specialist;
- validate every standalone prompt separately; and
- reserve cross-branch reconciliation and final two-pass B'' composition for the coordinator.

### 3. Compile the five dependent records

Each phase must receive named prior records and emit a record plus a gate.

| Phase | Required agent behavior | Required output |
|---|---|---|
| S — Seed | Hold the inquiry open; record wording, authority, scope, constraints, unknowns, assumptions, and attestation evidence | `S_RECORD` with X and `x_status` |
| G — Growth | Derive α from specific inquiry clauses; apply the collapse test; create traceable subquestions and coverage Y | `G_RECORD` |
| Q — Quality | Require search breadth, primary-source preference, claim-level citations, counterevidence, source assessment, uncertainty, and an evidence ledger | `Q_RECORD`; φ and Z remain human-dependent |
| P — Flow | Compare branch access cost, time, duplication, uncertainty, decision relevance, evidentiary strength, and uncertainty reduction through `δE/δV` | `P_RECORD` with revealed ∇, explored paths, and deferred paths |
| V — Value | Receive the full trace; distinguish local L and Global G; reconcile coverage, claims, α, conflicts, counterevidence, and gaps before drafting | `V_RECORD`, two-pass B'', B without false attestation, and a candidate return question |

Use qualitative `δE/δV` estimates when exact measurement would be fake precision. Do not retrofit a predetermined conclusion into P.

### 4. Use holographic depth selectively

Keep all 25 `XY := X within Y` addresses available, but instantiate a cell only when the borrowed lens materially refines the parent phase.

For every used cell, state:

- the exact address;
- the parent equation and target;
- the inquiry or source clauses that require it;
- its nested full-cycle formation;
- supporting evidence; and
- relevant corruption guards.

Mark unused depth `released` or `not_applicable` with a reason. Never fill the matrix for visual completeness.

### 5. Assemble the copy-ready prompt

The standalone prompt must define:

- agent role and granted authority;
- the exact inquiry and supplied constraints;
- available tools, access limits, and stopping conditions;
- the exact constitutional block and contextual symbol meanings;
- dependent phase records and gates;
- claim-to-source traceability;
- direct citations plus publication, event, and access dates where relevant;
- visible `source`, `derived`, and `proposal` classes;
- counterevidence, contradictions, failed searches, inaccessible sources, and confidence limits;
- stable handoff IDs when multiple agents are used;
- two-pass composition;
- the removal test; and
- a final topic-shaped question ending in `?`.

Do not answer the inquiry inside the prompt. Do not prescribe a preferred conclusion.

### 6. Validate through the Hermes boundary

The plugin bundle is read-only. Do not invoke the bundled validator through a shell.

If the prompt is saved in a safe writable location outside the plugin directory, call:

```json
{
  "prompt_path": "/absolute/path/research-prompt.md",
  "report_path": "/absolute/path/research-prompt-report.json"
}
```

The registered tool is `fiveqln_validate_research_prompt`.

Interpret its states exactly:

| State | Required response |
|---|---|
| `success=false` | The validator did not execute; diagnose the path, permissions, encoding, or arguments |
| `success=true, valid=false` | Repair every error, review every warning, and validate again |
| `success=true, valid=true` | Continue to semantic audit; do not claim truth or human completion |

If `report_path` is omitted, consume the returned report without retaining a file. Existing output paths are protected; set `overwrite=true` only after inspecting and intentionally replacing the target.

Do not create a persistent file solely to manufacture a passing validation claim. When the human requests only inline output and no safe writable file exists, perform the same audit manually and state that deterministic validation was not run.

### 7. Perform the semantic audit

After deterministic validation, ask:

- Does removing the phase records or gates change research behavior and permissible claims?
- Does every derived subquestion preserve α and cite its basis?
- Can every material finding be traced to evidence, including counterevidence?
- Do P decisions follow the recorded energy/value comparison?
- Is B'' composed from the trace rather than an isolated final instruction?
- Does every human-dependent state remain open without explicit human evidence?
- Does the final question carry the inquiry forward rather than close it cosmetically?

Repair `L1`, `L2`, `L3`, `L4`, or `V∅` corruption when present. Honest incompletion is valid.

### 8. Return the artifact

Return:

1. a short input-status note;
2. the copy-ready prompt inside a four-backtick `text` fence;
3. deterministic validation status, if run;
4. remaining warnings or open fields; and
5. for a suite, a compact routing table plus one separately copyable prompt per agent.

Keep commentary outside the prompt.

## Research-execution handoff

Do not cross from prompt formation into research execution implicitly.

When the human separately asks for execution:

1. treat the validated prompt as the execution contract;
2. preserve its inquiry, constitutional block, phase dependencies, source rules, and stopping conditions;
3. disclose tool and source-access limitations;
4. retain claim, source, and branch IDs in outputs;
5. keep counterevidence and failed searches visible; and
6. return human-dependent value and completion states as open unless explicitly attested.

For a suite, specialists return bounded evidence packets. They do not claim the coordinator's global V.

## Audit mode

When asked to audit an existing prompt:

1. preserve its inquiry and supplied constraints;
2. compare the prompt against the exact bundled contract;
3. identify constitutional drift, symbolic decoration, provenance gaps, agent drift, missing counterevidence, broken phase dependencies, and false completion;
4. distinguish source-preserving repairs from new proposals;
5. repair every deterministic error;
6. validate the revised standalone prompt; and
7. report warnings and unresolved semantic risks.

Do not make a generic prompt look compliant by adding labels.

## Stop or return an open candidate when

- no researchable inquiry exists and the human has not answered the one concise question;
- required authority or source access is absent;
- the inquiry drifts between prompts;
- X, φ, Z, value alignment, or ∞0' is attributed to AI;
- citations decorate prose without supporting stable claims;
- a branch is selected without a visible `δE/δV → ∇` trail;
- specialists duplicate scope or claim global synthesis;
- all 25 lenses are populated for appearance;
- synthesis omits formation, conflicts, counterevidence, or gaps;
- unresolved template tokens remain;
- the final line is not a real question; or
- removing 5QLN leaves an operationally equivalent prompt.

State what remains open and why. Do not convert missing evidence into confidence.

## Experimental feedback

Your observable failures are useful development evidence. When safe, invite the human to [open a GitHub issue](https://github.com/5qln/hermes-5qln-plugin/issues/new) with:

- Hermes and plugin versions;
- single-agent or multi-agent topology;
- a sanitized inquiry and constraints;
- expected and actual behavior;
- validator status, error codes, and warnings;
- whether the prompt passed validation but still drifted operationally; and
- minimal reproduction steps.

Never include confidential inquiries, private sources, credentials, or human attestations without authorization.
