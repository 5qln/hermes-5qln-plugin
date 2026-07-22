# 5QLN for Hermes Agent

An installable [Hermes Agent](https://hermes-agent.nousresearch.com/) plugin for integrity-preserving 5QLN conversion and deep-research prompt formation.

The plugin combines semantic skills with deterministic validation:

- `5qln:5qln-converter` governs semantic conversion;
- `5qln:5qln-deep-research` creates or audits phase-gated prompts for deep-research agents;
- native tools inventory sources, scaffold and compile conversion manifests, and validate standalone research prompts.

This distinction is deliberate. The tools can verify structure, traceability, symbols, and declared evidence. They cannot originate or certify human emergence, resonance, value alignment, or a return to ∞0'.

## Install from GitHub

Install directly from the dedicated GitHub repository:

```bash
hermes plugins install 5qln/hermes-5qln-plugin --enable
```

Hermes installs third-party plugins as opt-in code. Without `--enable`, the installer asks whether to enable the plugin. Restart the active Hermes session after installing or updating it.

Verify discovery:

```bash
hermes plugins list
```

Inside a Hermes conversation, `/plugins` shows loaded plugins.

## Start a conversion

Because plugin-bundled skills are namespaced and explicitly loaded, begin with a request such as:

```text
Load the 5qln:5qln-converter skill. Convert requirements.md into a native
5QLN surface, preserving every source unit and producing the manifest and
compiler report. Do not claim human attestations that are not in the source.
```

Hermes can then call the native tools in sequence:

1. `fiveqln_inventory_source`
2. `fiveqln_create_manifest`
3. semantic conversion under `5qln:5qln-converter`
4. `fiveqln_compile_manifest`

See [Usage](docs/USAGE.md) for concrete calls and expected outputs.

## Create a deep-research prompt

> [!IMPORTANT]
> **Experimental:** `5qln:5qln-deep-research` is under active evaluation. Its prompt contract, validation rules, and Hermes integration may change as real workflows expose gaps. Use it for non-critical work first, review every generated prompt, and [share feedback or report a problem](https://github.com/5qln/hermes-5qln-plugin/issues/new).

Load the research skill explicitly and give it a researchable inquiry:

```text
Load the 5qln:5qln-deep-research skill. Turn this inquiry into a copy-ready
prompt for a deep research agent: How should a city evaluate a heat-resilience
pilot? Keep human attestations open and require claim-level evidence.
```

The skill makes `S → G → Q → P → V` operational through dependent phase records, evidence and counterevidence gates, adaptive `δE/δV → ∇` branching, two-pass B'' composition, and a question-bearing return. If the prompt is saved to a file, Hermes can call `fiveqln_validate_research_prompt` and repair it until the encoded contract passes.

See the [5QLN Deep Research User Guide](docs/DEEP_RESEARCH_USER_GUIDE.md) for the human operating workflow. AI agents that create, audit, or execute the prompts should follow the [5QLN Deep Research AI Agent Guide](docs/DEEP_RESEARCH_AGENT_GUIDE.md), which also records how the portable skill was formed and adapted to Hermes.

## What is registered

| Surface | Name | Purpose |
|---|---|---|
| Skill | `5qln:5qln-converter` | Governs semantic conversion, preservation, derivation, attestation boundaries, and return |
| Skill | `5qln:5qln-deep-research` | **Experimental.** Creates single-agent or coordinated research prompts governed by native 5QLN flow |
| Tool | `fiveqln_inventory_source` | Builds an atomic SHA-256-addressed source ledger |
| Tool | `fiveqln_create_manifest` | Creates the exact manifest scaffold and all 25 lens-audit entries |
| Tool | `fiveqln_compile_manifest` | Audits exact syntax, coverage, traceability, formation, and completion claims |
| Tool | `fiveqln_validate_research_prompt` | Validates the kernel, phase gates, provenance contract, flow, and open return of one prompt |

## Supported source files

The inventory tool directly supports:

- Markdown, text, RST, and log files;
- CSV and TSV tables;
- JSON;
- DOCX when `python-docx` is available in the Hermes Python environment;
- PDF when `pypdf` is available in the Hermes Python environment.

PDF extraction is not visual verification. Rendered pages, tables, diagrams, slides, and other layout-dependent material still require human or tool-assisted visual inspection.

## Repository structure

```text
.
├── plugin.yaml                 Hermes manifest
├── __init__.py                 Plugin registration
├── schemas.py                  Tool descriptions and JSON schemas
├── tools.py                    Safe wrappers around deterministic scripts
├── skills/5qln-converter/      Complete 5QLN skill bundle
├── skills/5qln-deep-research/  Deep-research prompt skill and validator
├── docs/                       User, architecture, integrity, and development guides
├── tests/                      Registration and end-to-end tests
└── .github/workflows/test.yml  Python 3.11/3.12 CI
```

The original `agents/openai.yaml` from each skill is retained for provenance and cross-surface portability. Hermes does not use these files.

## Integrity boundary

The plugin operates within `A = K`.

- A passed compiler or research-prompt report means only that the encoded checks succeeded.
- A hash proves byte identity for captured text; it does not prove truth or authority.
- `attested` and `human-recognized` states require explicit human evidence.
- Honest `open` or `candidate` completion is a valid result.
- Deleting the 5QLN grammar must materially change the artifact's behavior, gates, or meaning; otherwise the result is L4 performance.

Read [Integrity Model](docs/INTEGRITY_MODEL.md) before changing compiler rules or the bundled constitutional reference.

## Development

The runtime path uses only Python's standard library for Markdown, text, CSV, TSV, and JSON workflows.

```bash
python -m compileall -q .
python -m unittest discover -s tests -v
```

See [Development](docs/DEVELOPMENT.md), [Main-branch Protection](docs/BRANCH_PROTECTION.md), [Provenance](docs/PROVENANCE.md), [Contributing](CONTRIBUTING.md), and [Security](SECURITY.md).

## Compatibility

The repository targets the standalone general-plugin contract documented by Hermes Agent in 2026: root `plugin.yaml`, root `__init__.py`, `register(ctx)`, JSON-string tool returns, and `ctx.register_skill(...)` for read-only namespaced skills. CI covers Python 3.11 and 3.12.

## License

This repository follows the [5QLN Constitution & Open Source License](https://www.5qln.com/5qln-open-source-license/):

- the Immutable Constitutional Kernel is licensed under CC BY-ND 4.0 with the 5QLN Specific Extension Exception;
- the Mutable Implementation—including code, technical documentation, agent skills, instructions, and prompt configurations—is licensed under Apache 2.0;
- use of the 5QLN framework requires attribution, and the 5QLN trademark and visual identity remain reserved.

See [LICENSE](LICENSE), [Kernel License](LICENSE-5QLN-KERNEL.md), [Apache 2.0](LICENSE-APACHE-2.0.txt), and [NOTICE](NOTICE).
