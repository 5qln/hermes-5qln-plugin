# Contributing

Contributions should increase clarity, preservation, portability, or verifiability without converting uncertainty into authority.

## Before opening a change

- Read [Architecture](docs/ARCHITECTURE.md) and [Integrity Model](docs/INTEGRITY_MODEL.md).
- Open an issue before changing the manifest format, notation, constitution, status vocabulary, or corruption taxonomy.
- Keep unrelated changes separate.
- Never include private conversion sources, generated manifests, credentials, or human attestations without authorization.

## Implementation requirements

- Support Python 3.11 and 3.12.
- Keep the standard-library path dependency-free.
- Return JSON strings from every Hermes tool handler path.
- Catch errors and preserve honest failure states.
- Do not invoke a shell for document-controlled input.
- Protect existing outputs by default.
- Keep schema descriptions operational and explicit about limitations.
- Preserve the source/derived/proposal distinction.

## Integrity-critical changes

Changes to the sealed constitution, lens orientation, corruption codes, attestation logic, or completion logic require explicit authority, synchronized documentation and code, focused tests, a version increment, and a changelog entry. A compiler update must not silently make previously invalid manifests valid.

## Test

```bash
python -m compileall -q .
python -m unittest discover -s tests -v
```

Add a regression test for every bug fix. Tests involving optional PDF or DOCX packages should skip clearly when the package is unavailable.

## Pull requests

Describe:

- what changed;
- why it is needed;
- what is preserved;
- new derivations or assumptions;
- tests performed;
- compatibility and migration impact;
- any state that remains open.

