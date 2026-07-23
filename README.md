# 5QLN for Hermes Agent

5QLN is a language for human-AI co-creation. This plugin activates the [5QLN Codex](https://5qln.com/codex) inside Hermes Agent.

When a human and an AI create together, the output erases the process. Who originated what? Where did the human drive and where did the AI fill? The final document can't answer. 5QLN can — by structuring every exchange so the formation trail stays visible from start to return.

This is early-stage software. It already works: full cycles of human-AI co-creation with a clear, verifiable trail of who did what. Early adopters use it for reflection, exploration, research — wherever the human needs to stay at the source as originator, with the AI holding structure.

The plugin is part of a larger vision: **[AGI for People](https://www.5qln.com/agi-for-people/), not AGI for AGI.** The human in the loop isn't a safety constraint. It's the point.

```bash
hermes plugins install 5qln/hermes-5qln-plugin --enable
```

## What's Included

10 skills and 4 registered tools. The tools are deterministic and stdlib-only;
the experimental skills also bundle stdlib-only scripts.

| Skill | Does |
|-------|------|
| `5qln-agent` | Agent identity and operating rules |
| `5qln-cycle` | Phase engine — structures each exchange |
| `5qln-initiation` | Entry point |
| `symbolic-interpretation` | Codex decoder for human and agent |
| `5qln-converter` | Compiles documents into verifiable surfaces |
| `5qln-learning-aligner` | Gate enforcement — prevents the agent from fabricating attestation |
| `5qln-manifest-compilation` | Manifest structure and compiler rules |
| `5qln-deep-research` | Phase-gated research prompts _(experimental)_ |
| `5qln-centrifuge` | Cross-session pattern extraction _(experimental)_ |
| `5qln-signature-engine` | Memory layer for session continuity _(experimental, tools planned)_ |

| Tool | Does |
|------|------|
| `fiveqln_inventory_source` | Hash-addressed source ledger |
| `fiveqln_create_manifest` | Integrity checklist from inventory |
| `fiveqln_compile_manifest` | Manifest audit |
| `fiveqln_validate_research_prompt` | Research prompt contract validation |

## Install

```bash
hermes plugins install 5qln/hermes-5qln-plugin --enable
```

Restart Hermes fully. Skills are namespaced — load with `5qln:skill-name`.
They also appear in the normal skill index (`/skills`, `skills_list`) after restart.

If skills don't appear after restart, verify the plugin is enabled: `hermes plugins list`.

## Use

Convert a document into a verifiable surface:

```
Load 5qln:5qln-converter. Convert these files. Show me the compiler report.
```

Create a research prompt with built-in evidence gates:

```
Load 5qln:5qln-deep-research. Turn this inquiry into a prompt that enforces
provenance and counterevidence at the prompt level.
```

[Usage Guide](docs/USAGE.md) — step-by-step with expected outputs.

## How It Works

Three operations, all deterministic:

1. **Inventory** — hash-addressed snapshot of every source file
2. **Manifest** — 25-point structural checklist: source, changes, attestations
3. **Compile** — pass or fail with specific flags

The plugin verifies structure. What it cannot verify — emergence, insight, meaning — stays with the human. That boundary is the architecture. Delete the grammar from the compiler and it collapses. That's the proof it's real.

## Designed to Grow

The plugin ships the runtime. Your agent produces the rest — session distillation, domain workflows, environment configuration — from your actual work. The converter verifies each new skill stays aligned with the Codex.

## Docs

| Doc | Covers |
|-----|--------|
| [Usage](docs/USAGE.md) | Install, convert, validate, troubleshoot |
| [Architecture](docs/ARCHITECTURE.md) | Design, data flows, trust boundaries |
| [Integrity Model](docs/INTEGRITY_MODEL.md) | What the tools can and cannot certify |
| [Deep Research — User](docs/DEEP_RESEARCH_USER_GUIDE.md) | Human workflow for research prompts |
| [Deep Research — Agent](docs/DEEP_RESEARCH_AGENT_GUIDE.md) | AI agent guide for research prompts |
| [Development](docs/DEVELOPMENT.md) | Setup, testing, contributing |
| [Changelog](CHANGELOG.md) | Version history |

## License

Kernel: CC BY-ND 4.0 with 5QLN Specific Extension Exception. Implementation: Apache 2.0. [LICENSE](LICENSE)
