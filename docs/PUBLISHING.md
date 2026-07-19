# Publishing

## Repository identity

- Repository: `5qln/hermes-5qln-plugin`
- Visibility: public
- Default branch: `main`
- License: not selected

Public visibility is not itself a software license. Until the owner adds a license, downstream users should not assume permission to reuse, modify, or redistribute the source beyond applicable law.

## Repository setup

Publish this directory as the repository root. `plugin.yaml` and `__init__.py` must remain at the root for direct Hermes installation.

Recommended repository settings:

- protect the default branch;
- require the `test` workflow before merge;
- enable secret scanning and dependency alerts;
- require pull requests for integrity-critical files;
- create signed or annotated release tags where practical.

## Pre-release checklist

```bash
python -m compileall -q .
python -m unittest discover -s tests -v
git status --short
```

Then verify:

- `plugin.yaml` version matches `CHANGELOG.md`;
- documentation uses `5qln/hermes-5qln-plugin`;
- the license decision is recorded; when a license is selected, its text exists at repository root;
- no generated inventories, manifests, reports, credentials, or private sources are committed;
- the full skill bundle is present;
- a clean Hermes installation succeeds with `hermes plugins install 5qln/hermes-5qln-plugin --enable`;
- `/plugins` shows `5qln` and all three tools;
- `5qln:5qln-converter` loads;
- a small end-to-end conversion produces the expected pass/fail behavior.

## Release

1. Update `CHANGELOG.md` and `plugin.yaml`.
2. Merge only after CI and integrity review pass.
3. Tag the commit `vMAJOR.MINOR.PATCH`.
4. Create a GitHub release summarizing changes, compatibility, migrations, and known limitations.
5. Reinstall from the public repository in a clean Hermes environment.

Users then install with:

```bash
hermes plugins install 5qln/hermes-5qln-plugin --enable
```
