# Security policy

## Scope

The plugin executes locally with the same operating-system permissions as Hermes. It reads caller-supplied source paths and writes caller-supplied output paths.

It does not:

- use a shell to invoke bundled scripts;
- execute source document contents;
- make network requests;
- collect telemetry;
- request API keys;
- install dependencies at runtime;
- overwrite an existing output unless `overwrite=true` is explicit.

## Trust third-party code before enabling it

Hermes plugins are executable Python. Review the repository and release before running:

```bash
hermes plugins install 5qln/hermes-5qln-plugin --no-enable
```

Enable only after review:

```bash
hermes plugins enable 5qln
```

## Untrusted documents

Inventory treats document content as data. Parser libraries may still contain vulnerabilities, particularly for complex PDF and DOCX inputs. Keep Hermes and optional parsing packages updated, and process high-risk files in an isolated environment.

Do not place credentials or secrets in conversion artifacts unless their inclusion is necessary and authorized. Inventories preserve source text and may therefore reproduce sensitive data.

## Output paths

The plugin resolves paths and relies on host permissions. Callers should use dedicated working directories and inspect a target before setting `overwrite=true`. Symlink and shared-directory policies remain the responsibility of the host environment.

## Reporting a vulnerability

Use the repository's **Security** tab and GitHub Private Vulnerability Reporting when available. If a private report cannot be opened, contact [@5qln](https://github.com/5qln) privately before public disclosure; do not publish an unpatched vulnerability in a public issue.

Include the plugin version, Hermes version, operating system, reproduction steps, impact, and any proposed mitigation. Exclude private source material and credentials.
