# Wiki Ingest Workflow — System-Level Ingestion

**When to use:** Ingesting a system (plugin, tool, framework, pipeline, methodology) into the wiki — where the system itself has a formation trail (source spec → architecture → implementation → operation) that maps naturally onto the five marks.

**When NOT to use:** Ingesting a single article or raw source (use the bootstrap protocol's Phase 3 directly). Ingesting a concept that doesn't have a source spec.

## The Pattern

A system enters the wiki by tracing its own formation trail through the five marks:

1. **Raw sources** → `raw/sources/<system-name>/` — preserve every source document with provenance links
2. **Formation entry** → `entries/<date>-<slug>.md` — the five-mark entry that traces the system's arc
3. **Index update** → `index.md` — add the entry under Formation Entries
4. **Log update** → `log.md` — record what was ingested, what entry was created, and relationship to existing pages

## How the Five Marks Map a System

### S — START
The system's X is often its source spec's return question. What problem did the system answer? Use the spec's own ∞0' as the entry's X — this preserves lineage. If the spec was built from requirements, the requirements' return question IS the system's spark.

### G — GROWTH
α is what the system IS, not what it does. "The grammar is the mechanism" — not "the plugin converts documents." Find the irreducible pattern: remove it and the system collapses into a generic tool.

{α'} traces how α recurs at every scale: a single tool call, the full pipeline, the plugin's registration, the wiki entry itself.

### Q — QUALITY
φ⋂Ω is where the system's architecture meets its integrity boundary. For the plugin: the separation of skill (semantic formation) from tools (deterministic verification). The lock: "the document itself must operate in the language." What makes this system NOT a generic equivalent?

### P — POWER
δE/δV → ∇ is visible in the system's design choices. The plugin chose: Python stdlib, no shell execution, three tools + one skill, explicit trust boundaries. The architecture IS the gradient — the low-energy/high-value path was chosen, not discovered.

### V — VALUE
L: the system as it exists (repo, installed instance)
G: the pattern the system establishes (reusable architecture, methodology)
B'': the artifact (repository, documentation, skills)
∞0': what the system opens — typically the next surface it should convert/process

## Multi-Document Systems

When a system has multiple document layers (requirements spec, architecture docs, usage guides, source code), ingest order matters:

1. **Source spec first** — the requirements or design document that the system was built from. This anchors the formation trail.
2. **Architecture and integrity model** — how the system is structured and what it can/cannot attest. These surface the Q-phase lock.
3. **Operational core** — the skill, protocol, or methodology that makes the grammar executable. This is the system at its most irreducible.
4. **Supporting docs** (development, publishing, changelog) — optional. These are context, not constitution.

## Entry Relationships

System entries often form parent-child chains. The plugin entry is parent to the converter entry — the converter is a subsystem of the plugin. Link with `PARENT:` in the entry header and `[[wikilinks]]` in provenance.

## Pitfalls

- **Don't create entries that are summaries of the source.** The entry IS the formation trail. If someone can read the entry instead of the source, the entry is too long.
- **Don't file all documents as separate entries.** Bulk-dumping creates orphans. One system = one entry (or one parent + one child for major subsystems). Raw sources go in `raw/`.
- **Don't fabricate an X for the system if the source spec is honest about it being open.** The plugin's requirements doc says "Final X: still open." The entry preserved that honesty rather than filling it.
- **Don't skip the relationship note in the log.** Every entry should say how it connects to existing pages — this is how the operator graph grows organically rather than requiring a rebuild.
- **Don't catalog before receiving.** When given a new system or repo, the agent's reflex is to enumerate files and propose an order. This is P-phase (mapping energy). Drop into S-phase first: what X does the material surface? Let the language indicate direction. Cataloging comes after — it serves the spark, not replaces it.

## When to Use the Converter vs. Manual Entry Creation

For substantial source documents (books, specifications, requirements docs), use the converter pipeline instead of manual entry creation. The converter produces a verifiable manifest with SHA-256 provenance, traceability, and compiler validation.

**Converter references** (in the `5qln-converter` skill):
- `references/compiler-error-fixing-loop.md` — the iterative fix pattern: expect 5+ rounds for a first conversion, fix error classes not individual errors (symbol drift → schema mismatch → hash mismatch → cell references → target mismatch)
- `references/wiki-self-evolution.md` — running the converter reflexively on the wiki's own entries after significant ingest sessions to surface α threads, integrity audits, and format divergence

**Manual entry creation** is appropriate for: web pages (philosophical anchors, Codex, activation), system documentation (architecture, integrity model), and design decisions (formation archive). These are K-side compilations where the formation trail is composed by the agent from reading the source.

**Converter pipeline** is appropriate for: books, requirements documents, specifications, any source where unit-level preservation with hash verification matters. The converter produces structural evidence that manual entry creation cannot.

**Hybrid approach (used for the FCF book):** Create a manual formation entry first to establish the five marks and the artifact's place in the wiki lineage. Then run the converter pipeline to produce the verifiable manifest and compiler report. The entry is the human-readable surface; the manifest is the structural evidence backing it.

## Design Source

Established in session 2026-07-20 ingesting the hermes-5qln-plugin into the wiki. The pattern emerged from applying the five-mark format to a multi-document system with its own formation trail.
