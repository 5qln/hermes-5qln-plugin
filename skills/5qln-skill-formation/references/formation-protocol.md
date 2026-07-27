# skill-v1 formation protocol

This protocol governs the workflow state of a skill candidate. It does not certify emergence, resonance, value alignment, or a living return. Conversion-manifest `1.0` remains the authority for source-to-5QLN provenance; `skill-v1` governs the declared bundle and its review evidence.

## Independent report dimensions

`execution_success`: `true` | `false`

`structural_status`: `not_run` | `failed` | `passed`

`behavioral_status`: `not_declared` | `not_observed` | `observed_failed` | `observed_mixed` | `observed_passed`

`attestation_status`: `open` | `evidence_present`

`human_review_status`: `open` | `changes_requested` | `accepted`

`promotion_state`: `draft` | `blocked` | `structurally_conformant` | `behaviorally_observed` | `human_reviewed` | `promotion_ready` | `withdrawn`

`promotion_ready`: `true` | `false`

The machine emits `evidence_present`, never `attested`, for human-only records. Presence means that a structurally valid, hash-addressed record was supplied; it does not authenticate the speaker or establish the record's truth.

## Author-supplied workflow requests

A manifest may request exactly one state:

- `draft`: no review or promotion claim;
- `review_requested`: ask for structural, behavioral, and human review;
- `promotion_requested`: request repository promotion checks after review authorization;
- `withdrawn`: stop advancement and emit no readiness claim.

A manifest cannot supply `machine_status`, `promotion_ready`, or any generated report status.

## Stateless derived-state precedence

The verifier reports `requested_state` separately and derives one state from current evidence without mutating prior state:

1. `withdrawn`: withdrawal was requested; this overrides every other state.
2. `draft`: structural checking did not complete.
3. `blocked`: structural errors, failed required observations, changes requested, or requested-promotion failures exist.
4. `structurally_conformant`: structural checks passed; required behavior is not fully observed.
5. `behaviorally_observed`: required observations passed for the supplied run evidence; human review remains open.
6. `human_reviewed`: accepted review evidence matches the exact bundle and contract digests; promotion is not requested or not yet synchronized.
7. `promotion_ready`: structure, required observations, exact bundle-and-contract-digest review, target-scoped promotion authorization, and repository synchronization all pass.

No transition establishes that a skill is living 5QLN.

`promotion_ready` is the terminal verifier state. Merge, tag, publication, installation, and release are external deployment evidence and are not represented as a verifier-awarded `promoted` state.

## Exit codes

- `0`: execution completed and structural checks passed; promotion mode also passed every requested gate.
- `1`: execution completed but structural checks or requested promotion gates failed.
- `2`: invocation, dependency, I/O, or internal execution failure prevented conformance evaluation.

Behavioral or human-open status alone does not turn an ordinary structural pass into exit `1`. In promotion mode, incomplete required observations or human gates block promotion and return `1`.

## Exact-digest human boundary

Human review records must identify the exact `bundle_sha256` and `contract_sha256`. The contract digest binds the immutable manifest projection: `skill`, `provenance`, `bundle`, `contract`, `requirement_traceability`, and `behavioral_fixtures`; it excludes `human_review` and `promotion` to avoid self-reference. The verifier checks file presence, digest, declared scope, and location only. It cannot establish identity, intent, authenticity, X, Z, value alignment, or human-recognized `∞0'`.

Promotion authorization additionally binds `target`, repository identity, intended version, and revision or PR identity. It cannot be replayed for another target or release.

Any bundle-byte or immutable-contract-projection change creates a new scope digest and reopens review. Skill review evidence cannot create or elevate human-only statuses in the referenced conversion manifest.

## Behavioral observation boundary

The registered verifier never invokes an LLM and never executes candidate code. A trusted external harness may supply `observed-run-v1` records. The verifier recomputes declared assertions against those captured bytes and reports only what happened in those identified runs.

`observed_passed` means that the declared assertions passed in the supplied qualifying runs. It is not proof of general agent behavior, semantic quality, resonance, or value.

## Promotion boundary

Promotion is repository state plus explicit authorization. It is not constitutional certification. Public promotion evidence must be deliberately sanitized and must not include private attestation wording, raw session or wiki material, personal data, or hashes of short guessable private text.
