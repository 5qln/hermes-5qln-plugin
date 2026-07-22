# Wiki Self-Evolution — Running the Converter on the Wiki Itself

The converter can be run reflexively on the wiki's own formation entries. This surfaces lawful relations between independently-written entries that no single entry could see.

## When to Use

After a significant ingest session (5+ new entries), or when the wiki's structure feels implicit and needs explicit mapping.

## What It Produces

### Integrity Audit
Read all formation entries, extract five-mark fields, check against the corruption taxonomy:
- All marks present? (S/G/Q/P/V)
- α formulated positively? (no "not" / "rather than" as identity)
- ∞0' question-bearing? (ends with ?)
- Corruption logs honest? (no suppressed violations)
- Provenance traces present? (caret references to raw sources)

### Alpha Thread Map
Cluster α fields across entries by shared concepts. Surface the deeper α that unites clusters. The map reveals what the corpus is about at levels the individual entries don't capture.

### Format Divergence Detection
The audit catches format drift. Example finding: `wiki-fractal-design.md` uses YAML frontmatter; all other entries use markdown sections. This is a drift signal — the operational protocol should standardize on one format.

## Execution Pattern

```python
# 1. Read all entries
for entry in entries_dir:
    extract: X, alpha, echoes, return_q, source_tag, marks_present, corruption

# 2. Run structural checks
check_marks_present()
check_alpha_positivity()
check_return_questions()
check_corruption_honesty()
check_provenance()

# 3. Cluster alpha threads
cluster_by_shared_concepts(alphas)

# 4. Create derived entries
create_integrity_audit_entry()
create_alpha_thread_map_entry()
```

## What This Is NOT

This is not a replacement for the formal converter pipeline (inventory → manifest → compile). It's a lighter-weight structural audit suitable for entries that are already in 5QLN format. For raw source documents, use the full pipeline.

## Discovery

First executed July 2026 after ingesting 10+ entries in a single session. The three α threads (Grammar as Mechanism, Not-Knowing as Source, Format as Living Process) were implicit across entries; the self-evolution made them explicit.
