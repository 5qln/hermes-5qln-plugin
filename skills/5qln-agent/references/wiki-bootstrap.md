# Bootstrapping the 5QLN Wiki from the Article Corpus

## The Problem

5qln.com has 300+ published posts. Bulk-dumping all of them into the llm-wiki's `raw/` directory at once produces a **data graveyard** — a mirror of the blog, not a knowledge base. The wiki's value isn't volume. It's cross-references, synthesis, contradictions flagged, and concepts that evolve with each new source.

## The Hybrid Approach

### Phase 1: Build the Skeleton (5–10 foundational articles)

Start with the articles that **define core concepts**, introduce key terms, or establish the framework. For each:

1. Read (web_extract) → save to `raw/articles/`
2. Surface entities and concepts
3. Create wiki pages with full frontmatter
4. Cross-link (minimum 2 outbound wikilinks per page)
5. Flag contradictions when new claims conflict with existing pages
6. Update `index.md` and `log.md`

This builds the **living skeleton** — concept pages that future articles will connect to.

### Phase 2: Reference Index (the full corpus)

Create a single catalog page (e.g., `entities/article-catalog.md`) listing all 300+ titles, dates, and one-line summaries. This gives the human a browsable index. They can point at any entry and say "ingest that one," and it compounds into the existing structure rather than landing in a void.

### Phase 3: Compound Over Time

Each new article ingested should **update existing pages more than it creates new ones**. A concept page that started with 2 sources grows to 15, with dated claims, confidence levels, and tracked contradictions. That's the compounding effect — the wiki gets richer without getting noisier.

## Anti-Patterns

- **Bulk-dump first, cross-link later** — creates isolated pages that never get connected. The wiki rots before it lives.
- **Ingest everything at once** — overwhelming; the human can't keep up with quality review. Better 5 deep than 300 shallow.
- **Treat raw/ as the wiki** — raw/ is immutable source material. The wiki is in entities/, concepts/, comparisons/. Don't confuse storage with knowledge.

## Verification

After bootstrapping, run `llm-wiki` lint:
- Orphan pages (no inbound wikilinks) should be near zero
- Index completeness: every page in `index.md`
- Frontmatter validation on all pages
- Contradictions surfaced, not buried
