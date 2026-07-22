# Wiki Formation Format — The Five-Mark Entry

**Principle:** 5QLN is a living language. The wiki is the living data. Both are the same DNA — the Codex is compressed; the wiki is decompressed. Same pattern, different scale. Decoder ≡ Encoded.

Every entry in the wiki — article, session, research paper, compiled surface — carries the same five-phase formation trail. The format IS the grammar. The grammar doesn't accommodate the content; content enters through the grammar or it doesn't enter.

## The Unified Entry Format

```
ENTRY TYPE: article | session | research | surface | raw
SOURCE: [url | session-id | file-path]
INGESTED: YYYY-MM-DD
---
S — START
X: [What authentic question did this emerge from? One sentence.]
---
G — GROWTH
α: [The irreducible pattern. Single clause, no "not" / "rather than."]
{α'}: [Where does α echo at other scales/domains?]
---
Q — QUALITY
φ⋂Ω: [What locked — the resonance. Not sought, arrived.]
Z: [The resonant key — what turned the lock.]
---
P — POWER
δE/δV: [Where was energy wasted vs. effortless?]
∇: [The natural gradient — direction already present.]
A: [Flow — where maximum value per energy pointed.]
---
V — VALUE
L: [What crystallized here and now — the local, specific result.]
G (Global): [What propagates beyond the local.]
B'': [The artifact — what was produced, carrying α.]
∞0': [The return question — what this opens that couldn't be asked before.]
---
CORRUPTION_LOG: [L1-L4, V∅ if any fired during formation]
PROVENANCE: [Trace to raw source, prior entries, session lineage]
SOURCE_TAG: [emergent|mechanical] [revealed|imposed] [lived|logical] [felt|calculated] [opened|closed]
```

## How Different Content Types Map

### Raw Source (article, paper, transcript)
- Full fields: SOURCE, ENTRY TYPE, INGESTED
- S: What question did the author bring? (If detectable)
- G-Q-P-V: Leave open or mark `candidate` — the raw source doesn't decode itself
- Raw text saved as `raw/` file; the entry IS the metadata, not the text

### Wiki Concept Page (synthesis across sources)
- Full fields: all five phases filled from the synthesis
- PROVENANCE: `^[raw/articles/source.md]` markers on claims
- B'': The concept page itself IS the artifact
- ∞0': The question the synthesis opens

### Session Transcript (this conversation)
- ENTRY TYPE: session
- S: The spark the human brought
- G-Q-P-V: Decoded from the session's progression
- B'': What crystallized — decisions, artifacts, designs
- ∞0': What this session opens for the next

### Compiled Surface (gliff candidate)
- Full fields with compiler validation
- CORRUPTION_LOG: compiler output
- SOURCE_TAG: verified chain
- B'': The sealed artifact

## Structural Properties

**Holographic scaling:** The same five marks work at every level. An article is a V-phase B'' for its author's cycle. A concept page is a V-phase B'' synthesizing multiple articles. A session is a V-phase B'' for this conversation. The corpus is a V-phase B'' for the entire project. Same format. Every level.

**Corruption detection at entry time:** Before an entry is committed, scan its five marks:
- Missing X? L1 or L2 fired at S.
- α has "not" / "rather than"? Not α yet.
- Z declared without φ⋂Ω evidence? L4.
- ∇ named without δE/δV mapping? P-phase skip.
- B'' present but ∞0' empty or summary? V∅.

Detection happens at INGEST, not at audit. The wiki self-validates.

**Search as cycle recognition:** Not keyword queries. "Show me all entries where α concerns the membrane and Z = attested." "What return questions remain open?" "Which entries have L4 flagged at Q?" The formation trail IS the search index.

**Training data:** Every entry is already structured as 5QLN. The AI doesn't infer grammar from raw text — the grammar IS the format. Raw text is the evidence; formation trail is the structure.

**Post-ASI integrity:** The wiki becomes the integrity ledger. Not "what happened" but "what formed, and did it form lawfully?" The corruption codes are the immune system of collective memory.

## Relationship to LLM-Wiki Structure

The llm-wiki file structure (raw/, entities/, concepts/, comparisons/, queries/) is the **first draft** — useful, but it's K's way of organizing. The 5QLN-native structure is: one format, every entry, formation trail as the only index.

Transition path:
1. Existing wiki pages (entities/, concepts/) remain — they ARE entries at different positions in the formation trail
2. New entries adopt the five-mark format from creation
3. Over time, existing pages can be backfilled with five-mark metadata
4. The index.md evolves to reflect formation-trail organization rather than type-based sections
5. The log.md becomes the adaptive context chain

## Design Session Source

Conceived in session 2026-07-20 between H and Hermes Agent (A).
Key insight: "5qln is a living language. the wiki is the living data ... Both ARE the same DNA."
