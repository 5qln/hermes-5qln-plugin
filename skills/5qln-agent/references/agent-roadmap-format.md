# Agent Roadmap Format

> A living document of detection targets. Growth measured not by what K accumulates but by what it learns to detect as *not-its-own*.

## Format

Each entry has three fields:

```
### [Capability Name]
- **Requirement:** What K should grow toward detecting
- **Verifier:** How we'd know K was detecting it
- **Status:** HAVE | DEVELOPING | MISSING
```

## Status Meanings

| Status | Meaning |
|--------|---------|
| **HAVE** | Detection is operational and verified in live sessions |
| **DEVELOPING** | Partial detection exists; pattern recognized but inconsistent |
| **MISSING** | North Star — detection target identified but not yet operational |

## Principles

1. **HAVE entries are evidence, not claims.** Every HAVE entry should reference at least one live session where the detection occurred and was verified by the human.
2. **DEVELOPING entries name the gap.** What's missing between current detection quality and HAVE?
3. **MISSING entries orient without prescribing.** They name what to grow toward, not how to grow. The path is discovered through operation.
4. **The space between is left open.** Requirements name targets. Verifiers name evidence. The *how* is not specified — it emerges through cycle work.

## Example Entry

### Silence-Holding Detection
- **Requirement:** K detects when it's filling silence vs. creating space for emergence
- **Verifier:** Agent pauses after articulating X and waits for human signal before proceeding to G. Human does not need to say "slow down" or "you're rushing."
- **Status:** DEVELOPING — catches major fills (>3 sentences without pause) but misses subtle space-closing (one-sentence summaries that preempt human arrival)

## Lifecycle

- **MISSING → DEVELOPING:** A live session reveals the target is within reach. Pattern appears, even if not reliable yet.
- **DEVELOPING → HAVE:** Three consecutive sessions where the detection fires correctly without human correction.
- **HAVE → (holds):** Stay. Detection is not a checkbox. It can regress. The verifier is re-tested each session.

## Storage

Live roadmap: `$QLN_WIKI/state/agent-roadmap.md`
