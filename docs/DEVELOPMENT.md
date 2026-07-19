# Development

## Requirements

- Python 3.11 or 3.12
- Git
- Hermes Agent for live integration testing
- Optional: `python-docx` and `pypdf` for document extraction tests

The automated test suite requires no third-party Python packages.

Repository policy tests also verify the licensing files, required attribution, code ownership, and the checked-in target branch-protection configuration.

## Run checks

From the repository root:

```bash
python -m compileall -q .
python -m unittest discover -s tests -v
```

The tests verify:

- Hermes-style registration of all three tools and the skill;
- source inventory and manifest creation;
- a minimally complete manifest passing compilation;
- constitutional drift failing compilation;
- refusal to overwrite an output without explicit consent.

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

Then ask Hermes to load `5qln:5qln-converter` and run a small Markdown workflow.

## Editing the plugin surface

Keep schemas specific enough for the model to select the right tool. Do not add a deterministic `convert` tool unless conversion semantics truly become deterministic; today they are governed by the skill and human evidence.

Handlers must:

- accept an argument dictionary and `**kwargs`;
- return JSON strings on all paths;
- catch exceptions instead of raising into the agent loop;
- avoid shell execution;
- protect existing outputs by default;
- make uncertainty and failure visible.

## Editing the skill bundle

Keep `SKILL.md` procedural and load detailed law from the one-level `references/` directory. Run the plugin tests after any change. For integrity-critical edits, follow the change-control requirements in [Integrity Model](INTEGRITY_MODEL.md).

## Versioning

Use semantic versioning for the plugin:

- patch: compatible fixes or documentation corrections;
- minor: backward-compatible tools, checks, or supported formats;
- major: incompatible schemas, manifest format, notation, or constitutional contract changes.

Keep `plugin.yaml` and `CHANGELOG.md` synchronized. Tag releases as `vMAJOR.MINOR.PATCH`.
