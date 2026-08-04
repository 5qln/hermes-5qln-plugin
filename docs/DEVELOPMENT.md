# Development

## Requirements

- Python 3.11 or 3.12
- Git
- Hermes Agent for live integration testing
- Optional: `python-docx` and `pypdf` for document extraction tests

Install the declared test dependencies with
`python -m pip install -r requirements-dev.txt`. The file includes the required
runtime dependency and schema-validation dependency used by the full suite.

Repository policy tests also verify the licensing files, required attribution, code ownership, and the checked-in target branch-protection configuration.

## Run checks

From the repository root:

```bash
python -m compileall -q .
python -m unittest tests.test_fractal_memory -v
python -m unittest tests.test_plugin -v
python -m unittest discover -s tests -v
```

The tests verify:

- Hermes-style registration of all seven tools, the pre-LLM hook, and all fourteen skills;
- strict fixed-shape seed validation and the 4096-byte bound;
- seed installation, calibration, export, and evidence non-retention;
- source inventory and manifest creation;
- a minimally complete manifest passing compilation;
- constitutional drift failing compilation;
- valid and invalid deep-research prompt review states;
- synchronization of the research contract with the canonical constitution;
- refusal to overwrite an output or report without explicit consent.

## Test in a Hermes project

For a trusted local checkout, expose the repository as a project plugin:

```bash
mkdir -p .hermes/plugins
ln -s /absolute/path/hermes-5qln-plugin .hermes/plugins/5qln
HERMES_ENABLE_PROJECT_PLUGINS=true hermes plugins enable 5qln
HERMES_ENABLE_PROJECT_PLUGINS=true hermes
```

Project plugins execute code from the checkout. Use this only with a repository you trust.

Verify in the session:

```text
/plugins
```

Then ask Hermes to load `5qln:5qln-converter` and run a small Markdown workflow. Load `5qln:5qln-deep-research`, create a file-based prompt, and call `fiveqln_validate_research_prompt` for the research path.

For a clean parametric-fractal smoke test, use a separate Hermes home and the synthetic seed:

```bash
PROFILE=$(mktemp -d /tmp/5qln-profile.XXXXXX)
mkdir -p "$PROFILE/plugins"
ln -s /absolute/path/hermes-5qln-plugin "$PROFILE/plugins/5qln"
HERMES_HOME="$PROFILE" hermes plugins enable 5qln --no-allow-tool-override
HERMES_HOME="$PROFILE" hermes plugins list --plain --no-bundled
python3 /absolute/path/hermes-5qln-plugin/fractal_memory.py install \
  /absolute/path/hermes-5qln-plugin/examples/parametric-fractal.example.json \
  --hermes-home "$PROFILE"
python3 /absolute/path/hermes-5qln-plugin/fractal_memory.py show \
  --hermes-home "$PROFILE"
```

This proves plugin discovery and portable state mechanics, not human resonance. See [Portable Parametric Fractal](PARAMETRIC_FRACTAL.md) for the clean-profile A/B protocol.

## Editing the plugin surface

Keep schemas specific enough for the model to select the right tool. Do not add a deterministic `convert` or `research` tool unless those semantics truly become deterministic; today they are governed by skills and human evidence. Validation tools may check only their declared contracts.

Handlers must:

- accept an argument dictionary and `**kwargs`;
- return JSON strings on all paths;
- catch exceptions instead of raising into the agent loop;
- avoid shell execution;
- protect existing outputs by default;
- make uncertainty and failure visible.

## Editing the skill bundles

Keep each `SKILL.md` procedural and load detailed contracts from the one-level `references/` directory. Keep the deep-research kernel synchronized with the canonical converter constitution. Run the plugin tests after any change. For integrity-critical edits, follow the change-control requirements in [Integrity Model](INTEGRITY_MODEL.md).

## Versioning

Use semantic versioning for the plugin:

- patch: compatible fixes or documentation corrections;
- minor: backward-compatible tools, checks, or supported formats;
- major: incompatible schemas, manifest format, notation, or constitutional contract changes.

Keep `plugin.yaml` and `CHANGELOG.md` synchronized. Tag releases as `vMAJOR.MINOR.PATCH`.
