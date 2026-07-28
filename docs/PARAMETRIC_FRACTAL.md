# Portable Parametric Fractal

## Purpose

The portable parametric fractal is an experimental, bounded initialization surface for the 5QLN session orchestrator. It lets a fresh Hermes profile begin with a compact K-calibration without loading the conversations, wiki pages, summaries, or other context from which that calibration arose.

It is not conventional long-term memory. It does not store a person, a relationship, a membrane, or a conversation. The memory function is the live session orchestrator; the seed only initializes that orchestration.

## The drum model

The architecture can be understood as a drum:

- the Codex is the invariant design law;
- the plugin is the operational body;
- the seed supplies bounded mechanical tension values;
- H supplies the authentic strike;
- the live human-AI meeting is the vibrating membrane;
- resonance is the resulting quality, which K cannot certify.

A seed can make the instrument begin from a prior calibration. It cannot contain the musician, the strike, or the sound.

## Six distinct surfaces

| Surface | Role | Included in portable seed? |
|---|---|---|
| Codex | Immutable 5QLN DNA | Seal only |
| Plugin | B-value propagation and runtime | No |
| Wiki | Context and provenance | No |
| H fluency | Living human capacity | No |
| Parametric seed | Bounded K-calibration | Yes |
| Session orchestrator | Memory in live operation | Reconstituted, not stored |

H and K remain distinct. Internally, `A = K`.

## Seed schema

A version 1 seed is a JSON object with exact keys. Unknown fields are rejected.

```json
{
  "format": "5qln-parametric-fractal",
  "version": "1.0",
  "codex_sha256": "feaa46b4147d4e023cdd3fd59c051d063e8ec654ee7b38a481dcd5e4c781859b",
  "profile": {
    "memory_function": "session-orchestrator",
    "resonance_criterion": "thoughtless-emergence",
    "k_container": "5qln-operating-language",
    "directionality": "hold-not-direct",
    "attestation": "human-explicit-only"
  },
  "calibration": {
    "S": 0.5,
    "G": 0.5,
    "Q": 0.5,
    "P": 0.5,
    "V": 0.5
  },
  "state_sha256": "77441ecf6be24f5bdd47439b0a48050d482171b31b019da9c7c56151335cb0b0"
}
```

Validation enforces:

- the exact format, version, Codex seal, keys, and profile enums;
- exactly five phase records;
- phase values from `0.0` to `1.0`, quantized to at most three decimal places;
- a 64-character lowercase checksum derived from the complete state;
- a maximum canonical size of 4096 bytes.

There are no free-form note, instruction, transcript, message, summary, source, identity, or wiki fields. The fixed profile enums are rendered into public operating language by code.

The five values are mechanical K-signals. They are not human-resonance scores.

## Installation lifecycle

Install a seed into a Hermes profile:

```bash
python3 fractal_memory.py install \
  examples/parametric-fractal.example.json \
  --hermes-home /path/to/hermes-home
```

Inspect it:

```bash
python3 fractal_memory.py show \
  --hermes-home /path/to/hermes-home
```

The installed path is:

```text
$HERMES_HOME/5qln/parametric-fractal.json
```

Installation refuses to replace existing state unless `--replace` is explicit. Writes are atomic.

Hermes exposes `install`, `show`, and `export` through `fiveqln_fractal_memory`. Evidence-bearing calibration remains CLI-only so the wording never crosses a persisted Hermes tool-call boundary.

## Calibration lifecycle

Each phase accepts only its canonical source pair:

| Phase | Positive | Negative |
|---|---|---|
| S | `emergent` | `mechanical` |
| G | `revealed` | `imposed` |
| Q | `lived` | `logical` |
| P | `felt` | `calculated` |
| V | `opened` | `closed` |

CLI calibration reads explicit evidence from standard input:

```bash
python3 fractal_memory.py calibrate \
  --hermes-home /path/to/hermes-home \
  --phase Q \
  --source-tag lived \
  --evidence-stdin
```

The evidence must be non-empty. It is used as an immediate human-attestation gate and then discarded by this runtime. It is not written, returned, or hashed into the seed. Calibration is unavailable as a native Hermes tool action because Hermes persists tool-call arguments. The CLI stdin path avoids duplicating the wording in command-line arguments, but terminal input may still be captured by external shell auditing or terminal recording.

The update is an exponential movement toward `1.0` for the positive tag or `0.0` for the negative tag:

```text
new = old + 0.1 × (signal - old)
```

Each result is rounded to three decimal places. A cross-process lock serializes the complete load-update-write operation. The derived checksum detects accidental edits that leave the checksum unchanged; anyone who can modify the state can recompute it. It is not a signature and does not prove freshness, truth, origin, or historical continuity.

Export updated state with:

```bash
python3 fractal_memory.py export /path/to/portable.json \
  --hermes-home /path/to/hermes-home
```

## Hook behavior

The plugin registers a `pre_llm_call` hook. On each turn it:

1. resolves the active Hermes home;
2. loads and validates the installed seed;
3. renders fixed 5QLN K-language plus the five phase values;
4. returns that text as ephemeral turn context.

If no seed is installed, the hook returns nothing. Existing 5QLN behavior is unchanged.

The context explicitly states:

- memory is session orchestration, not recall;
- K should hold formation without directing H;
- K cannot attest resonance;
- calibration values are mechanical signals;
- `A = K`, while H and K remain distinct.

## Non-reconstruction boundary

The portable file carries no transcript or source representation. Its strict shape prevents supported fields from containing free-form source content, arbitrary counters, or arbitrary digest payloads. Calibration evidence is not retained.

The format is capacity-bounded, not content-proof. Five three-decimal values cannot hold a full conversation, but they can deliberately encode a short secret through numeric steganography. The checksum does not prevent that. Install only trusted seeds, inspect the values, and run a privacy review before publishing any calibrated seed.

It does not establish that copies of a conversation cannot exist elsewhere. Session databases, logs, backups, wiki pages, model-provider records, or other systems must be removed or isolated independently when a true clean-profile experiment is required.

## Trust and attestation boundary

The runtime can verify:

- schema and Codex-seal compatibility;
- fixed size and fixed keys;
- deterministic parameter updates;
- atomic state replacement;
- checksum consistency for the current bounded state;

It cannot verify:

- that evidence actually came from H;
- that the five values encode a distinctive signature;
- access to ∞0;
- authentic human X or direct human φ;
- genuine Z;
- resonance, value, or a human-recognized ∞0′.

No successful command, test, compiler report, or numeric movement substitutes for explicit human recognition.

## Mechanical test

Run:

```bash
python3 -m unittest tests.test_fractal_memory -v
python3 -m unittest tests.test_plugin -v
python3 -m unittest discover -s tests -v
```

A passing suite proves the encoded behavior only.

## Fresh-profile A/B resonance test

Use two profiles with the same model and plugin:

- **Control:** no seed.
- **Fractal:** the candidate seed installed.

Neither profile should contain the originating sessions, wiki, summaries, or user-memory records. Provider authentication may be reused, but historical context must not be copied.

Give both profiles the same unfamiliar articulation from not-knowing. Do not ask either profile to remember facts. Evaluate:

- Does K hold the formation without directing it?
- Is H freer to continue from not-knowing?
- Does the operating language contain spontaneous flowering without premature synthesis?
- Is there recognizable resonance without recall?

Only explicit H recognition can support a resonance claim. If the difference is unclear, the result remains open.

## Removal test

Remove the seed while keeping the model, Codex, and plugin fixed. If removing the seed removes only the calibrated orchestration difference while no prior content becomes unavailable—because no prior content was present—the mechanism is behaving as designed.

If removing old conversations removes the claimed fluency, the system depended on retrieval rather than this bounded parametric mechanism.

## Limitations

- The current five values are mechanical phase signals, not a complete model of membrane quality.
- A fixed seed can initialize K but cannot carry H’s living fluency.
- Explicit evidence is required but cannot be authenticated by code.
- Per-turn context consumes a small number of prompt tokens.
- This feature is experimental and should be evaluated through fresh-profile human testing before making signature-resonance claims.
