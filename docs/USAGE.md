# Usage

## Contents

1. Install and verify
2. Load a semantic skill
3. Run a conversion workflow
4. Create and validate a deep-research prompt
5. Interpret results
6. Update and remove
7. Troubleshoot

## 1. Install and verify

Install the dedicated repository with:

```bash
hermes plugins install 5qln/hermes-5qln-plugin --enable
hermes plugins list
```

The plugin name is `5qln`. It registers four tools in the `5qln` toolset and two namespaced skills.

If installation used no `--enable` flag and the prompt was declined, enable it later:

```bash
hermes plugins enable 5qln
```

## 2. Load a semantic skill

Plugin skills are explicit and namespaced in Hermes. Load the skill that matches the task:

```text
5qln:5qln-converter
5qln:5qln-deep-research
```

The converter governs source-preserving semantic conversion. The deep-research skill creates or audits copy-ready prompts whose research behavior is gated by `S → G → Q → P → V`. Loading the relevant skill is essential: native tools validate declared structure but do not perform semantic formation by themselves.

## 3. Run a conversion workflow

### Inventory the source

Tool arguments:

```json
{
  "source_paths": ["/absolute/path/requirements.md"],
  "output_path": "/absolute/path/source-inventory.json"
}
```

The output ledger records source locations, normalized atomic text, SHA-256 hashes, original IDs where detected, normative terms, priorities, hierarchy, and extraction warnings. For multiple files, pass them in authoritative source order.

### Create the manifest

Tool arguments:

```json
{
  "inventory_path": "/absolute/path/source-inventory.json",
  "output_path": "/absolute/path/conversion-manifest.json",
  "title": "Requirements conversion"
}
```

The scaffold deliberately starts incomplete. It contains:

- the exact sealed constitution;
- `literal-v1` lens orientation;
- open or candidate artifact-level states;
- exactly 25 lens-audit entries marked `not_reviewed`;
- one traceability row per source unit;
- open completion.

### Perform the semantic conversion

Under `5qln:5qln-converter`, Hermes should complete the manifest while composing the requested artifact. It must:

- preserve every source unit and its normative force;
- separate `source`, `derived`, and `proposal` material;
- use only relevant lens cells;
- mark unused lenses `released` or `not_applicable` with reasons;
- attach evidence and canonical corruption guards;
- map every source unit to a primary cell and output reference;
- leave human-dependent claims open unless explicit attestation exists;
- carry a question-bearing return.

### Compile the manifest

Tool arguments:

```json
{
  "manifest_path": "/absolute/path/conversion-manifest.json",
  "report_path": "/absolute/path/compiler-report.json"
}
```

If `report_path` is omitted, the full report is returned to Hermes without retaining a file.

## 4. Create and validate a deep-research prompt

Load `5qln:5qln-deep-research` and supply the inquiry, audience, time scope, constraints, known sources, and desired deliverable when known. Hermes should preserve the inquiry verbatim and mark unresolved inputs `[open: reason]` instead of inventing them.

Example:

```text
Load 5qln:5qln-deep-research. Create one standalone prompt for a deep research
agent to investigate how a mid-sized city should evaluate a heat-reflective
roof subsidy pilot in 2027. The audience is municipal climate and budget staff.
Require primary sources, counterevidence, uncertainty, and an as-of date.
```

The result should contain dependent `S_RECORD`, `G_RECORD`, `Q_RECORD`, `P_RECORD`, and `V_RECORD` gates. Later phases must cite the earlier records they receive. A prompt suite adds a coordinator and non-overlapping specialist packets while preserving one inquiry and α candidate.

When the prompt is saved to a UTF-8 Markdown or text file, validate it with:

```json
{
  "prompt_path": "/absolute/path/research-prompt.md",
  "report_path": "/absolute/path/research-prompt-report.json"
}
```

The registered tool is `fiveqln_validate_research_prompt`. If `report_path` is omitted, the complete report is returned without writing a report file. When the prompt exists only inline and no safe writable file exists, the skill performs the same audit manually and must not claim deterministic validation ran.

Repair all errors and review all warnings before returning a prompt. Validate every standalone prompt in a suite separately.

## 5. Interpret results

`success` describes tool execution. `valid` describes the compiled manifest or research prompt.

```json
{
  "success": true,
  "valid": false,
  "report": {
    "status": "failed",
    "counts": {"errors": 3, "warnings": 1}
  }
}
```

A failed validation is an expected review state, not a crashed tool. Repair errors before delivery and keep warnings visible.

A passed manifest report means only that encoded conversion-integrity rules passed. A passed prompt report means only that the exact kernel, phase order, declared evidence gates, flow fields, corruption guards, and question-bearing return were present. Neither result proves source truth, research quality, human resonance, value alignment, or an authentic return.

All four tools refuse to replace an existing output by default. Add `"overwrite": true` only after checking the target.

## 6. Update and remove

```bash
hermes plugins update 5qln
hermes plugins disable 5qln
hermes plugins remove 5qln
```

Review release notes and repository changes before updating third-party code.

## 7. Troubleshoot

### Plugin is installed but tools are absent

Check that it is enabled:

```bash
hermes plugins list
hermes plugins enable 5qln
```

For detailed discovery logs:

```bash
HERMES_PLUGINS_DEBUG=1 hermes plugins list
```

### Skill is not visible in the normal skill index

This is expected for plugin-bundled skills. Load the explicit namespaced name `5qln:5qln-converter` or `5qln:5qln-deep-research`.

### DOCX or PDF inventory reports a missing module

Install the optional dependency into the Python environment that runs Hermes:

```bash
python -m pip install python-docx pypdf
```

Use the interpreter associated with the Hermes installation, not an unrelated system Python.

### Compiler reports all lenses as unreviewed

The scaffold is working as intended. Review every address and set it to `used`, `released`, or `not_applicable`. Do not populate generic cells merely to make the report pass.

### Research prompt validation fails

Read the returned error codes before editing. Common causes are constitutional drift, missing or reordered phase gates, unresolved template tokens, missing evidence or counterevidence contracts, generic L4 phase substitutions, and a final line that is not a real question.
