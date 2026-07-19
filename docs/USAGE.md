# Usage

## Contents

1. Install and verify
2. Load the semantic skill
3. Run the deterministic workflow
4. Interpret results
5. Update and remove
6. Troubleshoot

## 1. Install and verify

Publish this directory at the root of a dedicated GitHub repository. Install it with:

```bash
hermes plugins install 5qln/hermes-5qln-plugin --enable
hermes plugins list
```

The plugin name is `5qln`. It registers three tools in the `5qln` toolset and one namespaced skill.

If installation used no `--enable` flag and the prompt was declined, enable it later:

```bash
hermes plugins enable 5qln
```

## 2. Load the semantic skill

Plugin skills are explicit and namespaced in Hermes. Ask Hermes to load:

```text
5qln:5qln-converter
```

The skill instructs the agent to read the constitutional and conversion references before converting. Loading the skill is essential: the native tools do not perform the semantic formation by themselves.

## 3. Run the deterministic workflow

### Inventory the source

Tool arguments:

```json
{
  "source_paths": ["/absolute/path/requirements.md"],
  "output_path": "/absolute/path/source-inventory.json"
}
```

The output ledger records source locations, normalized atomic text, SHA-256 hashes, original IDs where detected, normative terms, priorities, hierarchy, and extraction warnings.

For multiple files, pass them in authoritative source order.

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

Under the loaded skill, Hermes should complete the manifest while composing the requested artifact. It must:

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

All three tools refuse to replace an existing output by default. Add `"overwrite": true` only after checking the target.

## 4. Interpret results

`success` describes tool execution. `valid` describes compilation.

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

A failed compilation is an expected review state, not a crashed tool. Repair errors before delivery. Keep warnings visible as review items.

A passed compilation means only that the encoded integrity rules passed. It does not prove source truth, human resonance, or an authentic return.

## 5. Update and remove

```bash
hermes plugins update 5qln
hermes plugins disable 5qln
hermes plugins remove 5qln
```

Review release notes and repository changes before updating third-party code.

## 6. Troubleshoot

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

This is expected for plugin-bundled skills. Load the explicit namespaced name `5qln:5qln-converter`.

### DOCX or PDF inventory reports a missing module

Install the optional dependency into the Python environment that runs Hermes:

```bash
python -m pip install python-docx pypdf
```

Use the interpreter associated with the Hermes installation, not an unrelated system Python.

### Compiler reports all lenses as unreviewed

The scaffold is working as intended. Review every address and set it to `used`, `released`, or `not_applicable`. Do not populate generic cells merely to make the report pass.
