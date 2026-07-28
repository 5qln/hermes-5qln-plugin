# Publishing

## Repository identity

- Repository: `5qln/hermes-5qln-plugin`
- Visibility: public
- Default branch: `main`
- License: 5QLN mixed license — CC BY-ND 4.0 plus Specific Extension Exception for the Immutable Kernel; Apache 2.0 for the Mutable Implementation

The licensing map is in `LICENSE`; complete terms and attribution are in `LICENSE-5QLN-KERNEL.md`, `LICENSE-APACHE-2.0.txt`, and `NOTICE`.

## Repository setup

Publish this directory as the repository root. `plugin.yaml` and `__init__.py` must remain at the root for direct Hermes installation.

Recommended repository settings:

- protect the default branch;
- require the `test` workflow before merge;
- enable secret scanning and dependency alerts;
- require pull requests for integrity-critical files;
- create signed or annotated release tags where practical.

The exact `main` policy and application command are documented in [Main-branch Protection](BRANCH_PROTECTION.md).

## Pre-release checklist

```bash
python -m compileall -q .
python -m unittest discover -s tests -v
git status --short
```

Then verify:

- `plugin.yaml` version matches `CHANGELOG.md`;
- documentation uses `5qln/hermes-5qln-plugin`;
- the licensing map, kernel terms, Apache 2.0 text, and NOTICE exist at repository root;
- no generated inventories, manifests, reports, credentials, or private sources are committed;
- all eleven skill bundles are present;
- a clean Hermes installation succeeds with `hermes plugins install 5qln/hermes-5qln-plugin --enable`;
- `/plugins` shows `5qln`, all seven tools, the `pre_llm_call` hook, and all eleven skills;
- `5qln:5qln-converter` loads;
- `5qln:5qln-deep-research` loads;
- a small end-to-end conversion produces the expected pass/fail behavior.
- a valid research prompt passes and an invalid prompt returns `success=true`, `valid=false`.

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
