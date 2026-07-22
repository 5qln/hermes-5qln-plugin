# 5QLN Deep Research User Guide

> [!IMPORTANT]
> `5qln:5qln-deep-research` is an **experimental skill**. Its prompt contract, validation rules, and Hermes integration may change as they are tested on real research workflows. Use it for non-critical work first, review every generated prompt, and [share feedback or report a problem](https://github.com/5qln/hermes-5qln-plugin/issues/new).

This guide applies to the 5QLN Hermes plugin v0.2.0.

## What the skill does

The skill turns a researchable inquiry into a copy-ready prompt governed by the native 5QLN flow `S → G → Q → P → V`. It can create:

- one self-contained prompt for a lead research agent;
- a coordinated prompt suite for materially independent research tracks; or
- an audit and repair of an existing 5QLN research prompt.

The skill creates or audits the prompt. It does not perform the research unless you separately ask an agent to execute the finished prompt.

A typical workflow is:

1. give Hermes the inquiry and any known constraints;
2. load `5qln:5qln-deep-research`;
3. review the generated input-status note and prompt;
4. save the prompt outside the read-only plugin bundle;
5. validate and repair it;
6. send the complete prompt to the deep research agent that will execute it.

## Install and verify

Install and enable the plugin:

```bash
hermes plugins install 5qln/hermes-5qln-plugin --enable
hermes plugins list
```

Restart the active Hermes session after installing or updating the plugin. Inside a conversation, `/plugins` shows loaded plugins.

The skill is namespaced. Always load it by its full name:

```text
5qln:5qln-deep-research
```

## Quick start

Give Hermes a researchable inquiry and ask for a standalone prompt:

```text
Load the 5qln:5qln-deep-research skill.

Create one standalone prompt for a deep research agent to investigate how a
mid-sized city should evaluate a heat-reflective roof subsidy pilot in 2027.

Audience: municipal climate and budget staff.
Deliverable: a decision memo with an evidence ledger.
Requirements: prefer primary sources; include counterevidence, uncertainty,
publication and event dates, and an explicit as-of date.

Preserve my inquiry, mark unresolved inputs [open: reason], and do not pre-answer
it. Return the input-status note and copy-ready prompt. Save the prompt to a new
writable file outside the plugin bundle, validate it with
fiveqln_validate_research_prompt, repair all errors, and show any warnings.
```

Hermes should return a short input-status note followed by a separately copyable prompt. Review both before using the prompt.

## Supply useful inputs

Only the inquiry is essential. More context usually produces a better-bounded prompt.

| Input | What to provide |
|---|---|
| Inquiry | The exact question the research should investigate |
| Audience | Who will use the result and what they need to decide |
| Deliverable | Memo, report, comparison, evidence map, recommendation options, or another format |
| Time scope | Historical range, forecast horizon, and an as-of date for time-sensitive work |
| Geography | Relevant country, jurisdiction, market, organization, or population |
| Source rules | Required sources, preferred primary sources, exclusions, languages, and access limits |
| Constraints | Time, budget, tools, privacy, methodology, or policy constraints |
| Known material | Seed sources or facts to treat as supplied context rather than independently verified truth |
| Topology | One lead agent, or a coordinator plus bounded specialists |

Do not invent missing scope merely to fill the prompt. The skill should retain unresolved values as `[open: reason]`.

## Choose one agent or a prompt suite

Use one lead-agent prompt by default. It is easier to operate, validate, and keep coherent.

Ask for a suite when the inquiry has materially independent tracks that can be researched without duplicating work. For example:

```text
Load 5qln:5qln-deep-research. Create a coordinator prompt and three bounded
specialist prompts for the inquiry below. Separate the tracks into regulation,
technical evidence, and implementation economics. Preserve one exact inquiry,
one alpha candidate, one evidence schema, and stable claim and source IDs across
the suite. Validate every standalone prompt separately.

Inquiry: [paste the exact inquiry]
```

A suite should include a shared inquiry contract, a coordinator prompt, and non-overlapping specialist packets. Specialists return evidence packets and open questions; the coordinator performs cross-branch reconciliation and the final two-pass composition.

## Understand the generated flow

The five records are dependent gates, not decorative headings.

| Record | Research behavior it governs |
|---|---|
| `S_RECORD` | Preserves the exact inquiry, authority, scope, constraints, unknowns, and attestation status |
| `G_RECORD` | Derives the alpha candidate and traceable subquestions without silently rewriting the inquiry |
| `Q_RECORD` | Defines evidence breadth, source quality, citations, counterevidence, uncertainty, and the evidence ledger |
| `P_RECORD` | Compares branch energy and value, records explored and deferred paths, and makes adaptation visible |
| `V_RECORD` | Reconciles the full trace, composes the deliverable in two passes, and ends with an open return question |

Later records should cite the earlier records they receive. Removing the records and gates should materially change the research behavior; otherwise the prompt is only wearing 5QLN terminology.

## Validate and repair the prompt

Save each standalone prompt as a UTF-8 Markdown or text file in a writable location outside the plugin directory. Then call `fiveqln_validate_research_prompt`:

```json
{
  "prompt_path": "/absolute/path/research-prompt.md",
  "report_path": "/absolute/path/research-prompt-report.json"
}
```

`report_path` is optional. If omitted, Hermes returns the complete report without retaining a report file. Output files are protected from replacement by default; use a new path, or add `"overwrite": true` only after checking the existing target.

Interpret the two top-level states separately:

| Result | Meaning |
|---|---|
| `success=false` | The validator could not execute; fix the file, path, permissions, or tool input |
| `success=true, valid=false` | Validation ran and found contract errors; repair every error and review every warning |
| `success=true, valid=true` | The encoded structural and integrity checks passed |

A valid report does not prove that sources are true, the research will be high quality, or a human recognizes resonance, value alignment, or completion. It verifies the encoded prompt contract only.

When the prompt exists only inline and no safe writable file exists, ask Hermes to audit it manually. Hermes should state that deterministic file validation was not run.

## Run the finished prompt

Copy the complete validated prompt into the agent that will perform the research. Keep the constitutional block, inquiry, phase gates, evidence schema, and stopping conditions intact.

For a multi-agent suite:

1. give the shared contract to every agent;
2. give each specialist only its assigned packet and authorized sources;
3. preserve stable claim, source, and branch IDs in every handoff;
4. return specialist evidence packets to the coordinator;
5. let only the coordinator claim global reconciliation—and keep human-dependent completion open.

If the same Hermes agent will execute the prompt, make that a separate instruction after prompt creation and validation.

## Audit an existing prompt

The skill can inspect and repair an existing prompt:

```text
Load 5qln:5qln-deep-research. Audit the prompt at
/absolute/path/research-prompt.md for constitutional drift, symbolic decoration,
provenance gaps, agent drift, unsupported completion, missing counterevidence,
and broken S → G → Q → P → V dependencies. Preserve the original inquiry,
repair all errors, validate the revised file, and report remaining warnings.
```

## Troubleshoot

### The skill is not listed

Plugin-bundled skills may not appear in the normal skill index. Load the exact namespaced name `5qln:5qln-deep-research`.

### The validator reports constitutional or phase errors

Do not patch the prompt with generic headings. Reload the skill, preserve the exact constitutional block, and repair the missing record, gate, evidence, flow, or return behavior identified by the error code.

### The validator refuses to write the report

Choose a new `report_path`, or inspect the existing file before intentionally setting `"overwrite": true`.

### Hermes still uses an older skill version

Update the plugin and restart the active session:

```bash
hermes plugins update 5qln
```

## Experimental limits and feedback

This skill is under active evaluation. In particular, feedback is useful on:

- whether the generated prompt improves research behavior rather than adding ceremony;
- clarity of the input-status note and phase records;
- single-agent versus coordinator/specialist routing;
- usefulness of validator errors and warnings;
- compatibility with different deep research agents and source-access patterns; and
- cases where validation passes but the operational prompt still drifts or underperforms.

[Open a GitHub issue](https://github.com/5qln/hermes-5qln-plugin/issues/new) and include, when safe:

- Hermes and plugin versions;
- single-agent or multi-agent mode;
- a sanitized inquiry and constraints;
- expected and actual behavior;
- validator status and error codes; and
- minimal reproduction steps.

Do not post confidential inquiries, private source material, credentials, or human attestations without authorization.
