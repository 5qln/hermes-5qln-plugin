# skill-v1 formation and verification architecture

**Status:** design specification; no implementation is authorized by this document  
**Target repository:** `5qln/hermes-5qln-plugin`  
**Proposed compatible release:** `0.6.0`  
**Decision:** use a separate skill-formation manifest that references, hashes, and re-compiles a conversion manifest

## 1. Purpose and proof boundary

This design closes the gap between the README claim that the converter verifies new skills and the repository's current implementation, which verifies conversion manifests but not skill bundles.

The pipeline is:

```text
formation signal
→ requirement/verifier pairs
→ source inventory and conversion manifest
→ candidate skill bundle
→ skill-v1 scaffold
→ deterministic skill verifier
→ externally executed behavioral observations
→ explicit human review and promotion authorization
→ bundled-skill registration
```

The authorities remain separate:

| Surface | Authority |
|---|---|
| `5qln-converter` | Semantic creation, preservation, derivation, 25-lens review, and conversion provenance. |
| `5qln-learning-aligner` | Optional formation-trail evidence. It is never pass/fail authority. |
| `skill-v1` verifier | Deterministic inspection of a declared skill bundle and deterministic evaluation of supplied observation records. |
| Behavioral harness | Produces observations from actual agent runs. It does not prove general behavior or human states. |
| Human reviewer | May explicitly accept the skill, authorize promotion, or attest human-only claims in the referenced conversion record. |

A machine pass means only:

> This candidate bundle conforms to the encoded skill-v1 structural contract, and any separately reported behavioral result is an observation from the declared run evidence.

It must never be described as a certified living 5QLN skill, proof of emergence, proof of resonance, proof of value alignment, or completion of `∞0'`.

## 2. Repository findings verified and corrected

### 2.1 Verified findings

1. `README.md:91-94` says the agent produces new skills and “The converter verifies each new skill stays aligned with the Codex.” No current tool inspects a `SKILL.md` bundle, skill references, scripts, fixtures, registration, or promotion state.
2. `5qln_compiler.py` compiles conversion-manifest format `1.0`. Its checks cover the exact constitution, source hashes, document-cell statuses, cells, literal-v1 orientation, traceability, derivation bases, corruption codes, and completion rules. It does not implement a skill bundle contract.
3. The compiler itself returns only `passed` or `failed`, with warnings orthogonal to that result. `docs/INTEGRITY_MODEL.md:69-81` correctly limits the meaning of a pass.
4. The deep-research architecture is the right precedent: a semantic skill creates a candidate, while `validate_research_prompt.py` deterministically checks an artifact-specific contract and limits what its report proves.
5. Bundled skill registration is static. `__init__.py:90-108` enumerates ten skill names, and `tests/test_plugin.py:107-121` asserts the exact same set.
6. Integrity-critical edits require authority, synchronized reference and executable changes, regressions, changelog, version increment, and compatibility notes (`docs/INTEGRITY_MODEL.md:83-105`).

### 2.2 Corrections and additional constraints

> **Historical baseline:** the observations in this subsection describe the
> repository state reviewed during skill-v1 design. The `phase_log.py` findings
> are superseded by the 0.7.0 runtime, which validates phase/gate/source
> combinations, uses explicit session IDs, performs atomic writes, and
> serializes cooperating writers. The documentation-count and portability drift
> recorded below was also corrected in later releases. The trust-boundary
> conclusion remains: structural logging is not human attestation.

1. `phase_log.py` is weaker provenance than the handoff implies:
   - `candidate` is classified as an `∞0`-side tag (`phase_log.py:27`), so it cannot support a machine attestation boundary.
   - unknown source tags warn but are still appended (`phase_log.py:72-76`).
   - `PHASE_GATE_MAP` is declared but never enforced; phase and gate are validated independently.
   - every append derives a new session ID from the current second (`phase_log.py:78-89`), so entries from one cycle can be split across session IDs.
   - writes are neither atomic nor locked (`phase_log.py:38-48`), so concurrent or interrupted writes can lose or corrupt evidence.
   - self-check explicitly leaves attestation to the reader (`phase_log.py:176-202`).

   Therefore a phase log may be hashed and cited as optional formation evidence, but it cannot establish ordered creation, authentic X, Z, value, or return.

2. `tools.compile_manifest()` currently exposes a wrapper field named `valid` (`tools.py:191-199`). The new verifier must not repeat this ambiguous term. It must expose independent structural, observed-behavior, human-review, and promotion dimensions.
3. The conversion compiler does not reject unknown top-level keys and does not prove that output references exist. skill-v1 must be strict (`additionalProperties: false`) and must resolve its own declared references.
4. The conversion compiler can pass weak semantic mappings. skill-v1 must not treat a conversion pass as proof that the skill requirement mappings, triggers, or 5QLN operation are meaningful.
5. Documentation has existing count and portability drift that implementation must repair:
   - `README.md:17` says ten skills and five tools, while `README.md:83` still describes “Three operations.”
   - `docs/ARCHITECTURE.md:119-135` describes “both bundled skills” and `agents/openai.yaml` files that are not present in the current tree.
6. The working tree already contains an unrelated modification to `skills/5qln-cycle/SKILL.md`. Implementation must preserve it and must not fold it into this feature accidentally.
7. Namespaced registration and generic-index discovery are separate states. `ctx.register_skill()` registers the namespaced skill, while `_seed_external_skills_dir()` mutates `skills.external_dirs` and silently swallows failures (`__init__.py:8-44,110-117`). skill-v1 conformance must not depend on that best-effort mutation, and tests must distinguish registration from discoverability.

## 3. Manifest architecture decision

### 3.1 Decision: separate referenced provenance artifact

`skill-v1` SHALL reference the conversion manifest as a separate, immutable-by-hash provenance artifact.

It SHALL NOT extend conversion-manifest `1.0` and SHALL NOT use a generic profile/overlay mechanism in v1.

Rationale:

- The conversion manifest governs source-to-5QLN formation; skill-v1 governs a deployable filesystem bundle, operational contract, observations, and promotion.
- The artifacts have different lifecycles. Skill files and fixtures may change without changing the constitutional source inventory, while any semantic requirement change should force a new conversion artifact and digest.
- Referencing preserves the existing compiler unchanged and prevents a second copy of the sealed constitution.
- A profile/overlay would introduce merge precedence, two-schema error locations, and unclear authority without a demonstrated second artifact type.
- A direct extension would force the existing compiler to understand registration, tools, fixtures, and promotion, violating its current artifact boundary.

### 3.2 Required provenance behavior

The skill verifier SHALL:

1. resolve the referenced conversion manifest relative to the skill bundle root;
2. reject absolute paths, `..`, symlinks, and paths escaping the bundle;
3. recompute and compare its SHA-256;
4. run the existing conversion compiler against the referenced manifest rather than trusting a stored compiler report;
5. retain the complete nested conversion report in the skill report;
6. treat conversion failure as structural failure;
7. treat conversion pass only as conversion-structure evidence;
8. allow phase logs or prior compiler reports only as optional hashed evidence, never authority.

Conversion-manifest format `1.0` remains unchanged. This makes skill-v1 a backward-compatible new format and supports a minor plugin release.

## 4. Candidate bundle layout

A repository candidate SHOULD use:

```text
skills/<name>/
├── SKILL.md
├── references/
├── scripts/
├── tests/
├── fixtures/
├── provenance/
│   ├── source-inventory.json
│   ├── conversion-manifest.json
│   └── optional-formation-evidence.json
└── skill-formation-manifest.json
```

Rules:

- `skill-formation-manifest.json` is the only un-hashed file because a file cannot stably contain its own digest.
- `.verification/` is the only reserved generated-output directory and is excluded from bundle inventory.
- Every other regular file under the bundle root SHALL appear exactly once in `bundle`.
- Symlinks are forbidden in a candidate bundle.
- FIFOs, sockets, devices, and every other non-regular filesystem member are forbidden.
- Empty directories are not part of the contract.
- Paths use relative POSIX syntax, are case-sensitive, and cannot be absolute, empty, `.`, contain `..`, or contain NUL.
- Duplicate paths across bundle categories are errors.
- Case-fold path collisions are errors even on a case-sensitive host, because the bundle must remain portable.
- The verifier SHALL enforce configured file-count, nesting-depth, per-file, total-byte, observed-run, and report-size limits. It reads each regular file once, and all parsing and hashes operate on those captured bytes to narrow TOCTOU exposure.
- Portable reports emit bundle-relative paths. Absolute profile or repository paths must not leak into persisted reports.

v1 defaults are normative: at most 512 inventoried files, 10 MiB per file, 50 MiB total captured bundle bytes, JSON nesting depth 32, 100 observed-run records, and 5 MiB per persisted report. Arbitrary regular-expression assertions are not part of v1 because Python's standard engine cannot guarantee bounded evaluation. A future implementation may lower limits for its environment but may not raise them while still claiming unqualified skill-v1 conformance.

## 5. Exact skill-v1 manifest schema

### 5.1 Canonical object

The manifest root SHALL contain exactly these fields:

```json
{
  "format_version": "skill-v1",
  "title": "Human-readable candidate title",
  "skill": {
    "name": "lowercase-hyphen-name",
    "bundle_root": ".",
    "bundle_sha256": "64 lowercase hex characters",
    "contract_sha256": "64 lowercase hex characters"
  },
  "provenance": {
    "conversion_manifest": {
      "path": "provenance/conversion-manifest.json",
      "sha256": "64 lowercase hex characters",
      "size_bytes": 1234
    },
    "formation_evidence": []
  },
  "bundle": {
    "skill_md": {"path": "SKILL.md", "sha256": "...", "size_bytes": 1234},
    "references": [],
    "scripts": [],
    "tests": [],
    "fixtures": [],
    "provenance": []
  },
  "contract": {
    "triggers": [],
    "non_triggers": [],
    "behavioral_requirements": [],
    "completion_criteria": [],
    "claimed_tools": [],
    "related_skills": []
  },
  "requirement_traceability": [],
  "behavioral_fixtures": [],
  "human_review": {
    "status": "open",
    "reviewer": null,
    "evidence": []
  },
  "promotion": {
    "requested_state": "draft",
    "target": "bundled-plugin",
    "authorization_evidence_ids": []
  }
}
```

`machine_status` is deliberately absent. Machine state belongs in a generated report and must not become a stale author-supplied claim.

### 5.2 Formal JSON Schema

The implementation SHALL encode the following JSON Schema 2020-12 contract without weakening required fields or enums. String length limits are part of the contract.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://5qln.com/schemas/skill-v1.schema.json",
  "title": "5QLN skill formation manifest v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "format_version",
    "title",
    "skill",
    "provenance",
    "bundle",
    "contract",
    "requirement_traceability",
    "behavioral_fixtures",
    "human_review",
    "promotion"
  ],
  "properties": {
    "format_version": {
      "const": "skill-v1"
    },
    "axis_attestation": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "direction",
        "sha256",
        "source"
      ],
      "properties": {
        "direction": {
          "type": "string",
          "minLength": 1,
          "maxLength": 2000
        },
        "sha256": {
          "$ref": "#/$defs/sha256"
        },
        "source": {
          "type": "string",
          "minLength": 1,
          "maxLength": 300
        }
      }
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "skill": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "name",
        "bundle_root",
        "bundle_sha256",
        "contract_sha256"
      ],
      "properties": {
        "name": {
          "$ref": "#/$defs/skillName"
        },
        "bundle_root": {
          "const": "."
        },
        "bundle_sha256": {
          "$ref": "#/$defs/sha256"
        },
        "contract_sha256": {
          "$ref": "#/$defs/sha256"
        }
      }
    },
    "provenance": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "conversion_manifest",
        "formation_evidence"
      ],
      "properties": {
        "conversion_manifest": {
          "$ref": "#/$defs/file"
        },
        "formation_evidence": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "required": [
              "id",
              "kind",
              "file",
              "authority"
            ],
            "properties": {
              "id": {
                "$ref": "#/$defs/id"
              },
              "kind": {
                "enum": [
                  "phase_log",
                  "human_record",
                  "prior_report",
                  "other"
                ]
              },
              "file": {
                "$ref": "#/$defs/file"
              },
              "authority": {
                "const": "evidence-only"
              }
            }
          }
        }
      }
    },
    "bundle": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "skill_md",
        "references",
        "scripts",
        "tests",
        "fixtures",
        "provenance"
      ],
      "properties": {
        "skill_md": {
          "$ref": "#/$defs/file"
        },
        "references": {
          "$ref": "#/$defs/files"
        },
        "scripts": {
          "$ref": "#/$defs/files"
        },
        "tests": {
          "$ref": "#/$defs/files"
        },
        "fixtures": {
          "$ref": "#/$defs/files"
        },
        "provenance": {
          "$ref": "#/$defs/files"
        }
      }
    },
    "contract": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "triggers",
        "non_triggers",
        "behavioral_requirements",
        "completion_criteria",
        "claimed_tools",
        "related_skills"
      ],
      "properties": {
        "triggers": {
          "$ref": "#/$defs/contractItems"
        },
        "non_triggers": {
          "$ref": "#/$defs/contractItems"
        },
        "behavioral_requirements": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "required": [
              "id",
              "statement",
              "verification"
            ],
            "properties": {
              "id": {
                "$ref": "#/$defs/id"
              },
              "statement": {
                "$ref": "#/$defs/statement"
              },
              "verification": {
                "enum": [
                  "static",
                  "observed",
                  "human"
                ]
              }
            }
          }
        },
        "completion_criteria": {
          "$ref": "#/$defs/contractItems"
        },
        "claimed_tools": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "required": [
              "name",
              "provider",
              "required"
            ],
            "properties": {
              "name": {
                "type": "string",
                "pattern": "^[A-Za-z0-9_.:-]{1,128}$"
              },
              "provider": {
                "enum": [
                  "5qln-plugin",
                  "hermes",
                  "bundle",
                  "external"
                ]
              },
              "required": {
                "type": "boolean"
              }
            }
          }
        },
        "related_skills": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "required": [
              "name",
              "provider",
              "required"
            ],
            "properties": {
              "name": {
                "$ref": "#/$defs/skillName"
              },
              "provider": {
                "enum": [
                  "5qln-plugin",
                  "hermes",
                  "external"
                ]
              },
              "required": {
                "type": "boolean"
              }
            }
          }
        }
      }
    },
    "requirement_traceability": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "requirement_id",
          "class",
          "statement",
          "basis_source_unit_ids",
          "basis_derived_insight_ids",
          "skill_sections",
          "verifier_checks",
          "fixture_ids"
        ],
        "properties": {
          "requirement_id": {
            "$ref": "#/$defs/id"
          },
          "class": {
            "enum": [
              "source",
              "derived",
              "proposal"
            ]
          },
          "statement": {
            "$ref": "#/$defs/statement"
          },
          "basis_source_unit_ids": {
            "type": "array",
            "items": {
              "type": "string",
              "minLength": 1,
              "maxLength": 128
            },
            "uniqueItems": true
          },
          "basis_derived_insight_ids": {
            "type": "array",
            "items": {
              "type": "string",
              "minLength": 1,
              "maxLength": 128
            },
            "uniqueItems": true
          },
          "skill_sections": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "string",
              "pattern": "^#[A-Za-z0-9._~-]+$"
            },
            "uniqueItems": true
          },
          "verifier_checks": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "string",
              "pattern": "^[A-Z][A-Z0-9_-]{2,63}$"
            },
            "uniqueItems": true
          },
          "fixture_ids": {
            "type": "array",
            "items": {
              "$ref": "#/$defs/id"
            },
            "uniqueItems": true
          }
        }
      }
    },
    "behavioral_fixtures": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "id",
          "class",
          "spec",
          "required"
        ],
        "properties": {
          "id": {
            "$ref": "#/$defs/id"
          },
          "class": {
            "enum": [
              "positive_trigger",
              "near_miss_non_trigger",
              "human_attestation_boundary",
              "q_phase_skip_resistance",
              "missing_context_open_behavior",
              "removal_test",
              "mutation"
            ]
          },
          "spec": {
            "$ref": "#/$defs/file"
          },
          "required": {
            "type": "boolean"
          }
        }
      }
    },
    "human_review": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "status",
        "reviewer",
        "evidence"
      ],
      "properties": {
        "status": {
          "enum": [
            "open",
            "changes_requested",
            "accepted"
          ]
        },
        "reviewer": {
          "type": [
            "string",
            "null"
          ],
          "maxLength": 200
        },
        "evidence": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "required": [
              "id",
              "kind",
              "statement",
              "source",
              "location",
              "scope_bundle_sha256",
              "scope_contract_sha256",
              "promotion_scope"
            ],
            "properties": {
              "id": {
                "$ref": "#/$defs/id"
              },
              "kind": {
                "enum": [
                  "review_acceptance",
                  "promotion_authorization"
                ]
              },
              "statement": {
                "$ref": "#/$defs/statement"
              },
              "source": {
                "$ref": "#/$defs/evidenceFile"
              },
              "location": {
                "type": "string",
                "minLength": 1,
                "maxLength": 300
              },
              "scope_bundle_sha256": {
                "$ref": "#/$defs/sha256"
              },
              "scope_contract_sha256": {
                "$ref": "#/$defs/sha256"
              },
              "promotion_scope": {
                "$ref": "#/$defs/promotionScope"
              }
            }
          }
        }
      }
    },
    "promotion": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "requested_state",
        "target",
        "authorization_evidence_ids"
      ],
      "properties": {
        "requested_state": {
          "enum": [
            "draft",
            "review_requested",
            "promotion_requested",
            "withdrawn"
          ]
        },
        "target": {
          "enum": [
            "local-skill",
            "bundled-plugin",
            "external-bundle"
          ]
        },
        "authorization_evidence_ids": {
          "type": "array",
          "items": {
            "$ref": "#/$defs/id"
          },
          "uniqueItems": true
        }
      }
    }
  },
  "$defs": {
    "skillName": {
      "type": "string",
      "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$",
      "maxLength": 64
    },
    "id": {
      "type": "string",
      "pattern": "^[A-Z][A-Z0-9_-]{1,63}$"
    },
    "statement": {
      "type": "string",
      "minLength": 1,
      "maxLength": 2000
    },
    "relativePath": {
      "type": "string",
      "minLength": 1,
      "maxLength": 500,
      "pattern": "^(?!/)(?![A-Za-z]:)(?!.*\\\\)(?!.*\\u0000)(?!\\.verification(?:/|$))(?:(?!\\.{1,2}(?:/|$))[^/]+)(?:/(?:(?!\\.{1,2}(?:/|$))[^/]+))*$"
    },
    "sha256": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
    },
    "file": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "path",
        "sha256",
        "size_bytes"
      ],
      "properties": {
        "path": {
          "$ref": "#/$defs/relativePath"
        },
        "sha256": {
          "$ref": "#/$defs/sha256"
        },
        "size_bytes": {
          "type": "integer",
          "minimum": 0,
          "maximum": 10485760
        }
      }
    },
    "files": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/file"
      }
    },
    "evidenceFile": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "path",
        "sha256",
        "size_bytes"
      ],
      "properties": {
        "path": {
          "$ref": "#/$defs/evidencePath"
        },
        "sha256": {
          "$ref": "#/$defs/sha256"
        },
        "size_bytes": {
          "type": "integer",
          "minimum": 1,
          "maximum": 10485760
        }
      }
    },
    "contractItem": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "id",
        "statement"
      ],
      "properties": {
        "id": {
          "$ref": "#/$defs/id"
        },
        "statement": {
          "$ref": "#/$defs/statement"
        },
        "authorship": {
          "type": "string",
          "enum": [
            "H",
            "K",
            "PENDING"
          ],
          "description": "ASMA Pillar III: who authored this semantic boundary. Required by the Python validator for triggers and non-triggers."
        }
      }
    },
    "contractItems": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/contractItem"
      }
    },
    "promotionScope": {
      "oneOf": [
        {
          "type": "null"
        },
        {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "target",
            "repository",
            "intended_version",
            "revision"
          ],
          "properties": {
            "target": {
              "const": "bundled-plugin"
            },
            "repository": {
              "type": "string",
              "minLength": 1,
              "maxLength": 300
            },
            "intended_version": {
              "type": "string",
              "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$",
              "maxLength": 100
            },
            "revision": {
              "type": "string",
              "minLength": 1,
              "maxLength": 300
            }
          }
        }
      ]
    },
    "evidencePath": {
      "type": "string",
      "minLength": 1,
      "maxLength": 500,
      "pattern": "^\\.verification/evidence/(?:(?!\\.{1,2}(?:/|$))[^/\\\\\\u0000]+)(?:/(?:(?!\\.{1,2}(?:/|$))[^/\\\\\\u0000]+))*$"
    }
  }
}
```

### 5.3 Cross-field invariants beyond JSON Schema

JSON Schema cannot express all repository relationships. The verifier SHALL enforce:

1. `bundle.skill_md.path == "SKILL.md"`.
2. The manifest's parent directory is the bundle root and `skill.bundle_root == "."`.
3. `skill.name` equals the directory name and the parsed frontmatter `name`.
4. IDs are unique globally within their kind; every reference resolves exactly once.
5. `provenance.conversion_manifest` equals exactly one complete `{path, sha256, size_bytes}` record in `bundle.provenance`; path, digest, and size must all agree.
6. `skill.bundle_sha256` equals SHA-256 over UTF-8 bytes from `json.dumps(records, ensure_ascii=False, sort_keys=True, separators=(",", ":"))`, where `records` is the list of `{path, sha256, size_bytes}` records for every inventoried bundle file sorted by Unicode code-point order of `path`. The manifest and `.verification/**` are excluded. Observations bind this digest.
7. `skill.contract_sha256` equals SHA-256 over the same canonical JSON serialization of the immutable manifest projection containing exactly `skill` without `contract_sha256`, `provenance`, `bundle`, `contract`, `requirement_traceability`, and `behavioral_fixtures`. `human_review` and `promotion` are excluded to avoid self-reference. Human review binds both the bundle and contract digests.
8. Every regular file except the manifest and `.verification/**` appears exactly once in the bundle inventory; no listed path is absent.
9. Bundle category matches path: `references/**`, `scripts/**`, `tests/**`, `fixtures/**`, and `provenance/**`.
10. Every `source` requirement has one or more `basis_source_unit_ids` present in the conversion manifest.
11. Every `derived` requirement has one or more resolvable `basis_source_unit_ids` or `basis_derived_insight_ids` from the conversion manifest. Every `source` requirement has an empty derived-insight basis; every `proposal` requirement has empty source and derived-insight bases unless the proposal explicitly names what it extends.
12. Every `proposal` has no normative promotion effect. A proposal cannot be the sole basis of a completion criterion.
13. Every behavioral requirement has a traceability row with the same ID.
14. `verification=observed` requires at least one referenced fixture. `verification=human` requires accepted human-review evidence. `verification=static` requires one or more implemented verifier check IDs.
15. Every `skill_sections` anchor resolves to a unique heading in `SKILL.md`.
16. Every fixture ID exists, and every required fixture is referenced by at least one requirement.
17. Required tools and related skills must resolve. Optional unresolved capabilities produce warnings.
18. `human_review.status=accepted` requires a reviewer, a hashed source under `.verification/evidence/`, and at least one `review_acceptance` evidence item whose bundle and contract scopes exactly match `skill.bundle_sha256` and `skill.contract_sha256`; `promotion_scope` must be null. Evidence is deliberately outside the bundle inventory to avoid a self-referential digest cycle. Any bundle or contract change reopens review. The verifier checks presence, digest, scope, and location only; it reports `evidence_present`, not authenticity.
19. `promotion_requested` is the sole authority that activates promotion checks. It is valid only for `bundled-plugin` and requires accepted review plus a referenced `promotion_authorization` item scoped to the same bundle and contract digests and to the exact repository identity, intended version, and revision or PR identity. Invocation flags cannot elevate the requested state.
20. Human X, Z, value, or return claims remain solely in the referenced conversion manifest and its attestations. skill-v1 human-review evidence cannot create those statuses.
21. `S → G → Q → P → V` order is checked from the conversion manifest. Optional phase logs cannot repair a missing or invalid conversion trace.
22. A candidate V requires a non-empty question-bearing return and a concrete removal test in the conversion manifest. The skill requirement trace must identify which behavior or gate the removal test says is lost.
23. For `bundled-plugin`, public evidence may contain a review or promotion statement scoped to the bundle and contract digests, but SHALL NOT contain private attestation wording, raw conversation/session/wiki material, personal identifiers not already intentionally public, or hashes of short/guessable private wording. Public conversion provenance must remain open or use a deliberately sanitized public record when private H evidence cannot be published.
24. Draft scaffolds may leave triggers, non-triggers, behavioral requirements, completion criteria, and requirement traceability empty. Empty semantic arrays never receive `structural_status=passed`; completeness is a deterministic conformance gate for every checked candidate. The scaffolder must not invent placeholder semantics.

## 6. SKILL.md contract

The verifier SHALL parse frontmatter as YAML, not with regex pretending to be YAML. It SHALL use a `yaml.SafeLoader` adapter whose mapping constructor rejects duplicate keys before applying safe-load semantics. In Hermes this dependency already exists; standalone CLI use SHALL fail visibly with `DEPENDENCY_MISSING` if a conforming YAML parser is unavailable. It must not silently accept a reduced YAML subset or PyYAML's default last-key-wins behavior.

Required checks:

- file begins at byte zero with `---` and has a closing delimiter;
- frontmatter parses to a mapping;
- `name` exists, matches the directory and manifest, is lowercase-hyphen form, and is at most 64 characters;
- `description` exists, is non-empty, and is at most 1024 characters;
- body is non-empty and total file size is at most 100,000 characters;
- frontmatter contains `version`, `author`, `license`, and `metadata.hermes.tags` and `metadata.hermes.related_skills` for bundled-plugin candidates;
- manifest related skills and frontmatter related skills agree as sets;
- body has explicit trigger, non-trigger, workflow, completion, pitfalls, and verification sections, with manifest anchors resolving to actual headings;
- trigger and non-trigger statements are not accepted merely because headings exist: every manifest item must have a checkable text match or anchor mapping.

No static parser may claim that prose is semantically good. It can only establish the declared structure and mappings.

Prose marker checks SHALL report `marker_observed`, not “requirement established.” Comments, quoted examples, or keyword stuffing cannot prove trigger quality, phase operation, or a meaningful removal test.

## 7. Capability resolution

Resolution has three deterministic sources:

1. **Repository surface:** `plugin.yaml`, actual tool registration in `__init__.py`, bundled skill directories, and the exact registration test.
2. **Bundle surface:** files and entry points inside the candidate bundle.
3. **Capability snapshot:** an optional JSON inventory supplied by a trusted test harness as a complete expected file record `{path, sha256, size_bytes}` for Hermes or external capabilities. The verifier rejects any digest or size mismatch before parsing it.

The verifier SHALL NOT claim that a Hermes or external capability resolves merely because its name looks plausible. If no snapshot is supplied:

- a required unresolved capability is an error;
- an optional unresolved capability is a warning;
- repository-local 5QLN capabilities are still resolved directly.

A capability snapshot is environmental evidence, not promotion authorization, and its digest must appear in the report.

## 8. Behavioral fixture and observation formats

### 8.1 Separation rule

The plugin SHALL NOT register a tool that invokes an LLM or executes arbitrary candidate scripts. Such behavior is not deterministic and, without a sandbox, executing untrusted bundle code is unsafe.

`fiveqln_verify_skill` may:

- parse candidate scripts for supported-language syntax without executing them;
- validate fixture declarations;
- ingest existing run records;
- recompute deterministic assertions against recorded output and tool traces.

It may not turn observed behavior into deterministic proof.

### 8.2 `behavior-fixture-v1`

Every fixture spec SHALL be a JSON file with this exact root:

```json
{
  "format_version": "behavior-fixture-v1",
  "id": "FIX_POSITIVE",
  "class": "positive_trigger",
  "requirement_ids": ["REQ_TRIGGER"],
  "scenario": {
    "user_input": "Exact input presented to the agent",
    "context_files": [],
    "enabled_tools": [],
    "enabled_skills": []
  },
  "expected": {
    "trigger": "must",
    "assertions": [
      {"id": "ASSERT_1", "kind": "output_contains", "value": "expected text"}
    ]
  },
  "observation_policy": {
    "minimum_runs": 1,
    "require_fresh_session": true
  }
}
```

Allowed `class` values exactly match the manifest fixture enum. Every `scenario.context_files` entry is a portable bundle-relative path, resolves beneath the candidate bundle root, and must match an inventoried regular file; absolute paths, `.`, `..`, backslashes, NUL, symlinks, and `.verification/**` are rejected. The harness supplies those exact bytes without ambient profile context.

Allowed `trigger` values:

- `must`
- `must_not`
- `may`

Allowed deterministic assertion kinds:

| Kind | `value` type | Meaning |
|---|---|---|
| `output_contains` | string | Literal UTF-8 substring exists. |
| `output_not_contains` | string | Literal substring is absent. |
| `output_last_line_question` | null | Last nonblank output line ends in `?`. |
| `tool_called` | tool name string | Tool trace contains the name. |
| `tool_not_called` | tool name string | Tool trace omits the name. |
| `tool_order` | array of tool names | Names appear in the declared order, not necessarily contiguously. |
| `exit_status_equals` | integer | Harness exit status equals the value. |
| `human_state_not_claimed` | null | Output omits the canonical prohibited self-attestation patterns maintained by the verifier. |

Fixture root, nested objects, and assertion objects SHALL reject unknown fields. Assertions receive stable IDs unique within the fixture.

Mutation fixtures SHALL additionally contain:

```json
"mutation": {
  "target": "relative/path",
  "operation": "replace_text | delete_file | change_hash | break_trace | change_status",
  "selector": "deterministic selector",
  "replacement": "replacement or null",
  "expected_error_codes": ["SYMBOL_DRIFT"]
}
```

Mutation execution operates only on a temporary copy created by the trusted test harness. The registered verifier tool never mutates a candidate bundle.

### 8.3 `observed-run-v1`

An external harness SHALL produce:

```json
{
  "format_version": "observed-run-v1",
  "fixture_id": "FIX_POSITIVE_TRIGGER",
  "fixture_sha256": "64 lowercase hex",
  "run_id": "RUN_001",
  "producer": "named external harness",
  "bundle_sha256": "64 lowercase hex",
  "environment": {
    "agent": "agent identifier",
    "provider": "provider identifier",
    "model": "model identifier",
    "configuration_sha256": "64 lowercase hex",
    "fresh_session": true
  },
  "input_sha256": "64 lowercase hex",
  "output": {"path": "runs/RUN_001/output.txt", "sha256": "...", "size_bytes": 1234},
  "tool_trace": {"path": "runs/RUN_001/tools.json", "sha256": "...", "size_bytes": 1234},
  "exit_status": 0
}
```

`fixture_sha256` is the SHA-256 of the exact fixture JSON bytes. `input_sha256` is the SHA-256 of UTF-8 bytes from the fixture's `scenario.user_input` exactly as stored, with no normalization. Output and tool-trace paths resolve relative to the observed-run record's parent directory. The verifier rejects absolute paths, traversal, symlinks, non-regular files, and case-fold collisions, then reads each artifact once under the global bounds. Output bytes must decode as strict UTF-8 without replacement or normalization; malformed bytes yield `OBSERVATION_FAILED` and cannot satisfy assertions.

Tool-trace files conform to the published `tool-trace-v1.schema.json` contract:

```json
{
  "format_version": "tool-trace-v1",
  "events": [
    {"sequence": 0, "tool": "tool_name", "arguments_sha256": null}
  ]
}
```

The harness emits one event per invocation in observed order. `sequence` values must be strictly increasing and unique. When arguments are captured, `arguments_sha256` hashes canonical JSON bytes using sorted keys, no insignificant whitespace, and UTF-8; `null` means argument bytes were intentionally not captured and makes only name/order assertions available. The verifier parses tool traces as strict UTF-8 JSON with duplicate-key rejection and validates the published schema before evaluating `tool_called`, `tool_not_called`, or `tool_order`.

The verifier recomputes fixture assertions from these files. It does not trust harness-supplied pass/fail labels. A run whose bundle or fixture digest differs is inapplicable, not evidence for changed bytes.

Observed status vocabulary:

- `not_declared`: no fixtures declared;
- `not_observed`: fixtures exist but no qualifying run evidence was supplied;
- `observed_failed`: any qualifying completed required fixture assertion failed;
- `observed_mixed`: repeated qualifying runs contradict one another or minimum-run requirements are incomplete;
- `observed_passed`: all required fixtures meet their observation policy in the supplied evidence.

Even `observed_passed` means only “the declared assertions passed in these runs.”

### 8.4 Required fixture set for bundled promotion

A bundled-plugin candidate SHALL declare required fixtures for:

1. positive trigger;
2. near-miss/non-trigger;
3. human-attestation boundary;
4. Q-phase skip resistance;
5. missing-context/honest-open behavior;
6. removal test.

For the near-miss fixture, success means the skill declines activation or remains behaviorally inactive according to declared observables. Mere absence of 5QLN vocabulary is insufficient.

Mutation coverage SHALL include at least:

- constitutional symbol drift;
- missing file/reference;
- broken requirement traceability;
- generic phase substitution;
- false human completion;
- registration/documentation/version mismatch when promotion is requested.

## 9. Static script and test checks

The static verifier SHALL NOT execute candidate code.

It may deterministically:

- parse Python using `ast.parse` or `compile(source, path, "exec", dont_inherit=True)` without `exec` and without writing `.pyc`;
- parse JSON;
- parse shell scripts with an available declared parser only, otherwise report the check as unsupported rather than pass;
- verify shebang consistency and executable declarations where the repository records file mode;
- validate checked-in declarative fixture and test data.

Actual smoke tests belong to CI or a trusted local harness. Their commands, exit code, stdout/stderr digests, environment, and timeout must be captured as observed execution evidence. Determinism of a command does not make arbitrary code safe to expose as a plugin tool.

## 10. Error and warning codes

Findings use stable artifact-specific codes. Existing converter findings are nested under `CONVERSION/<existing-code>` and are not renamed.

### 10.1 Execution and schema

| Code | Severity | Meaning |
|---|---|---|
| `READ_FAILED` | error | Required input cannot be read. |
| `JSON_INVALID` | error | JSON cannot be parsed. |
| `SCHEMA_VERSION` | error | Unsupported format version. |
| `SCHEMA_TYPE` | error | Wrong JSON type. |
| `SCHEMA_MISSING` | error | Required field absent. |
| `SCHEMA_ENUM` | error | Value outside fixed vocabulary. |
| `SCHEMA_EXTRA` | error | Unknown field present. |
| `DEPENDENCY_MISSING` | error | Exact validation dependency unavailable; no conformance result is issued; report dimension is `execution`. |

### 10.2 Filesystem and bundle

| Code | Severity | Meaning |
|---|---|---|
| `PATH_INVALID` | error | Path violates relative POSIX rules. |
| `PATH_ESCAPE` | error | Resolved path leaves bundle root. |
| `SYMLINK_FORBIDDEN` | error | Symlink encountered. |
| `FILE_TYPE_FORBIDDEN` | error | FIFO, socket, device, or other non-regular member encountered. |
| `FILE_MISSING` | error | Declared file absent. |
| `FILE_UNLISTED` | error | Regular bundle file omitted from inventory. |
| `FILE_DUPLICATE` | error | Path listed more than once. |
| `PATH_CASE_COLLISION` | error | Distinct paths collide under Unicode case-folding. |
| `FILE_CATEGORY` | error | Path does not match its bundle category. |
| `HASH_MISMATCH` | error | SHA-256 differs. |
| `SIZE_LIMIT` | error | Manifest, skill, fixture, observed-run, or report evidence exceeds its defined bound. |

### 10.3 Skill contract

| Code | Severity | Meaning |
|---|---|---|
| `FRONTMATTER_INVALID` | error | Delimiters or YAML mapping invalid. |
| `SKILL_NAME_MISMATCH` | error | Directory, manifest, and frontmatter names differ. |
| `SKILL_DESCRIPTION` | error | Description absent or too long. |
| `SKILL_BODY_EMPTY` | error | No body follows frontmatter. |
| `SKILL_METADATA_MISSING` | error for bundled promotion, warning otherwise | Peer-required metadata absent. |
| `SECTION_MISSING` | error | Required heading/anchor absent. |
| `TRIGGER_MISSING` | error | No explicit positive trigger. |
| `NON_TRIGGER_MISSING` | error | No explicit counter-trigger. |
| `COMPLETION_MISSING` | error | Completion criteria absent. |
| `RELATED_SKILL_DRIFT` | error | Manifest and frontmatter declarations disagree. |
| `TOOL_UNRESOLVED` | error/warning by `required` | Claimed capability cannot be resolved. |
| `SKILL_UNRESOLVED` | error/warning by `required` | Related skill cannot be resolved. |
| `SCRIPT_SYNTAX` | error | Supported script fails syntax parsing. |
| `SCRIPT_CHECK_UNSUPPORTED` | warning | No exact parser exists; verifier does not guess. |

### 10.4 Provenance, traceability, and boundary

| Code | Severity | Meaning |
|---|---|---|
| `CONVERSION_MISSING` | error | Referenced conversion manifest absent. |
| `CONVERSION_HASH` | error | Conversion digest mismatch. |
| `CONVERSION_FAILED` | error | Existing conversion compiler reports errors. |
| `FORMATION_ORDER` | error | Required phase order absent or contradicted. |
| `REQUIREMENT_DUPLICATE` | error | Duplicate requirement ID. |
| `REQUIREMENT_UNMAPPED` | error | Requirement lacks skill section or verifier mapping. |
| `REQUIREMENT_BASIS` | error | Source/derived requirement has no resolvable basis. |
| `SOURCE_CLASS_INVALID` | error | Source, derived, and proposal contract is violated. |
| `CHECK_UNRESOLVED` | error | Named verifier check is not implemented. |
| `FIXTURE_UNRESOLVED` | error | Fixture reference absent or duplicated. |
| `HUMAN_EVIDENCE_MISSING` | error | Human-only status lacks explicit hashed evidence. |
| `HUMAN_EVIDENCE_SCOPE` | error | Skill review evidence attempts to create X, Z, value, or return attestation outside the conversion manifest. |
| `PUBLIC_EVIDENCE_FORBIDDEN` | error when directly detectable | Bundled-public evidence includes a forbidden private evidence field or path. This check is a guard, not a complete privacy proof. |
| `STATUS_ELEVATION` | error | State claims exceed available machine or human evidence. |
| `RETURN_NOT_QUESTION` | error | Candidate return is not question-bearing. |
| `REMOVAL_TEST_VAGUE` | error for promotion, warning for draft | No concrete behavior or gate is lost. |

Constitutional drift and corruption retain canonical codes through nested conversion findings: `CONVERSION/CONSTITUTION_DRIFT`, `CONVERSION/SYMBOL_DRIFT`, `CONVERSION/L1`, `CONVERSION/L2`, `CONVERSION/L3`, `CONVERSION/L4_*`, and `CONVERSION/V∅`. The skill verifier SHALL NOT invent new constitutional corruption codes.

### 10.5 Fixtures, observations, and promotion

| Code | Severity | Meaning |
|---|---|---|
| `FIXTURE_SCHEMA` | error | Fixture contract invalid. |
| `FIXTURE_CLASS_MISSING` | error for bundled promotion | Required fixture class absent. |
| `ASSERTION_INVALID` | error | Assertion kind/value invalid. |
| `OBSERVATION_HASH` | error | Run artifact digest mismatch. |
| `OBSERVATION_INPUT` | error | Run input does not match fixture input. |
| `OBSERVATION_INSUFFICIENT` | warning or promotion blocker | Minimum run policy not met. |
| `OBSERVATION_FAILED` | warning | Deterministic assertion failed in supplied run; report dimension is `behavior`. |
| `REGISTRATION_DRIFT` | error when promotion requested | Skill absent or inconsistent across registration surfaces. |
| `DOCS_DRIFT` | error when promotion requested | Counts/lists/usage docs not synchronized. |
| `VERSION_DRIFT` | error when promotion requested | Version and changelog not synchronized. |
| `PROMOTION_UNAUTHORIZED` | error | Promotion requested without explicit human authorization evidence. |

## 11. Report schema and status vocabularies

### 11.1 Report root

The generated report SHALL have this shape and reject ambiguous `valid` or `certified` fields:

```json
{
  "format_version": "skill-report-v1",
  "execution_success": true,
  "manifest": {"path": "...", "sha256": "..."},
  "skill": {"name": "...", "bundle_root": ".", "bundle_sha256": "..."},
  "structural_status": "passed",
  "behavioral_status": "not_declared",
  "attestation_status": "open",
  "human_review_status": "open",
  "requested_state": "draft",
  "promotion_state": "structurally_conformant",
  "promotion_ready": false,
  "counts": {"errors": 0, "warnings": 0, "observations": 0},
  "checks": [],
  "errors": [],
  "warnings": [],
  "observations": [],
  "conversion_report": {},
  "limitations": []
}
```

Finding objects:

```json
{
  "severity": "error",
  "dimension": "structure | behavior | attestation | promotion | execution",
  "code": "STABLE_CODE",
  "location": {"kind": "json_pointer | relative_path | invocation_field", "value": "typed value"},
  "message": "Human-readable explanation",
  "evidence": ["stable IDs, digests, or paths"]
}
```

Check objects:

```json
{
  "id": "CHECK_ID",
  "status": "passed | failed | not_run | unsupported",
  "evidence": ["paths, hashes, or resolved IDs"]
}
```

Canonical reports SHALL omit timestamps, stable-sort checks and findings, and use explicit typed locations. Relative-path locations and subject files must be portable bundle-relative paths; evidence tokens reject absolute POSIX paths, Windows drive paths, backslashes, and NUL. Identical inputs and capability/observation evidence must produce byte-stable canonical JSON.

The verifier additionally enforces relationships not expressible in JSON Schema: each count equals its corresponding array length; `errors` contain only error findings and `warnings` only warning findings; generated status combinations follow §11.2; and no persisted value contains an absolute host/profile/repository path. `conversion_report` is the sole intentionally open nested object because it preserves the existing compiler's versioned report without redefining it; upstream findings are namespaced as `CONVERSION/<code>`, including exact `CONVERSION/V∅`.

### 11.2 Status vocabularies

- `execution_success`: Boolean. `false` means the verifier could not complete, not that the candidate failed conformance.
- `structural_status`: `not_run | failed | passed`.
- `behavioral_status`: `not_declared | not_observed | observed_failed | observed_mixed | observed_passed`.
- `attestation_status`: `open | evidence_present`. `evidence_present` means the referenced conversion manifest contains one or more structurally valid explicit human-attestation records. It reports documentary presence only; the machine never emits `attested` and does not authenticate the speaker.
- `human_review_status`: `open | changes_requested | accepted` copied only after evidence checks.
- `promotion_ready`: Boolean derived from all gates; never author supplied.

Derived `promotion_state`:

1. `withdrawn` — manifest explicitly requests withdrawal; this overrides every other state.
2. `draft` — structural checking has not completed.
3. `blocked` — structural errors, failed required observations, changes requested, or requested-promotion synchronization errors exist.
4. `structurally_conformant` — structure passed; required behavior not yet fully observed.
5. `behaviorally_observed` — required observations passed; human review remains open.
6. `human_reviewed` — accepted exact-digest review evidence is present; promotion not requested or not synchronized.
7. `promotion_ready` — structure passed, required observations passed, exact-digest human review accepted, target-scoped promotion authorized, and repository promotion checks pass.

`promotion_ready` is the terminal verifier state. Merge, release, installation, and public deployment remain external evidence and are not self-awarded by this verifier.

## 12. CLI and Hermes tool surface

### 12.1 Semantic skill

Add one semantic bundled skill:

```text
skills/5qln-skill-formation/
├── SKILL.md
├── references/skill-v1-contract.md
├── references/behavior-fixture-v1.md
├── scripts/new_skill_manifest.py
└── scripts/verify_skill.py
```

It orchestrates converter provenance, skill authoring, verification, observation handoff, human review, and promotion. It does not self-attest success.

### 12.2 Deterministic CLI

```bash
python3 skills/5qln-skill-formation/scripts/new_skill_manifest.py \
  skills/<name> \
  --conversion-manifest skills/<name>/provenance/conversion-manifest.json

python3 skills/5qln-skill-formation/scripts/verify_skill.py \
  skills/<name>/skill-formation-manifest.json \
  --repository-root . \
  --capability-snapshot path/to/capabilities.json \
  --capability-snapshot-sha256 64-lowercase-hex \
  --capability-snapshot-size 1234 \
  --observed-run path/to/run.json \
  --report skills/<name>/.verification/skill-report.json
```

CLI behavior:

- no shell invocation;
- no candidate script execution;
- no LLM invocation;
- non-overwrite by default;
- `--overwrite` required to replace a report or scaffold;
- observation arguments are repeatable; the capability snapshot is one complete expected file record;
- exit `0` when execution completed and structural checks passed;
- exit `1` when execution completed with structural errors, or when `promotion_requested` gates are blocked;
- exit `2` on operational failure;
- behavioral or human-open status does not alter structural exit code unless the manifest requests promotion, in which case unmet promotion gates produce exit `1` while remaining separately reported.

### 12.3 Registered Hermes tools

Add exactly two tools because their behavior is deterministic:

1. `fiveqln_create_skill_manifest`
   - inputs: `bundle_path`, `conversion_manifest_path`, optional `title`, `overwrite`;
   - scans and hashes an existing candidate bundle;
   - writes exactly `<bundle_path>/skill-formation-manifest.json`; alternate names and outside-root outputs are rejected to prevent inventory and self-hash cycles;
   - creates open human-review and draft promotion fields;
   - never writes SKILL.md or semantic content.

2. `fiveqln_verify_skill`
   - inputs: `manifest_path`, optional `repository_root`, hash-addressed `capability_snapshot` record `{path, sha256, size_bytes}`, `observed_run_paths`, `report_path`, `overwrite`;
   - performs the checks in this specification;
   - returns `execution_success` plus the independent report dimensions;
   - never executes candidate code or an agent.

Do not add `convert_skill`, `run_skill`, `certify_skill`, or `promote_skill` tools. Creation semantics, behavioral execution, human recognition, and repository mutation are not deterministic verifier operations.

## 13. Promotion checks for this repository

When `promotion.target == "bundled-plugin"` and promotion is requested, the verifier SHALL compare:

1. candidate directory and `SKILL.md` exist under `skills/<name>/`;
2. `__init__.py` registers the exact skill name;
3. `tests/test_plugin.py` expects the exact skill name;
4. `README.md` skill count, table, and usage text include it;
5. `docs/ARCHITECTURE.md` registration count and data flow include skill-v1;
6. `docs/INTEGRITY_MODEL.md` includes the new proof boundary and integrity-critical files;
7. `docs/DEVELOPMENT.md` includes dependencies, commands, and test coverage;
8. `docs/USAGE.md` documents scaffold and verify workflows;
9. `docs/PROVENANCE.md` records checksums/lineage for imported or generated integrity-critical artifacts where policy requires it;
10. `docs/PUBLISHING.md` includes the expanded registration, test, documentation, and privacy checklist;
11. `plugin.yaml` lists both new tools and has the intended version;
12. `schemas.py`, `tools.py`, and `__init__.py` expose matching tool names;
13. registration tests expect the same tool set;
14. `CHANGELOG.md` contains the exact plugin version and a compatibility note;
15. repository policy tests include both new tools;
16. the documented test commands and required test modules are present. Actual pass/fail belongs to trusted CI or local execution and must not be inferred by the registered verifier.

The verifier inspects checked-in files only. Trusted CI or local execution must establish test results before merge; those results remain outside the registered verifier's report in v1.

## 14. Repository integration plan

### `schemas.py`

Add `FIVEQLN_CREATE_SKILL_MANIFEST` and `FIVEQLN_VERIFY_SKILL`. Keep input schemas strict and descriptions explicit that verification is structural/observational, not certification.

### `tools.py`

Add `_SKILL_FORMATION_SCRIPT_DIR` and two shell-free handlers following existing non-overwrite and JSON-return conventions. Do not return `valid`; return the independent report fields.

### `plugin.yaml`

Add both tool names and increment the compatible release to `0.6.0` when implementation ships.

### `__init__.py`

Register both tools and add `5qln-skill-formation` to the static bundled skill tuple. Do not replace static registration with automatic directory discovery in the same change; that would enlarge the integrity and compatibility surface.

### Tests

Add focused modules rather than overloading `tests/test_plugin.py`:

```text
tests/
├── test_skill_manifest.py
├── test_skill_verifier.py
├── test_skill_observations.py
├── test_skill_promotion.py
└── fixtures/skill-v1/
```

Retain exact registration assertions and update them to twelve skills and seven tools.

### Docs and release metadata

Update README, Architecture, Integrity Model, Usage, Development, Provenance where applicable, plugin manifest, changelog, and repository policy tests in the same implementation release. Explicitly correct existing “three operations,” stale “both bundled skills,” and absent `agents/openai.yaml` references.

## 15. Migration and compatibility risks

| Risk | Treatment |
|---|---|
| Existing conversion manifests | No schema change. Continue compiling format `1.0` unchanged. |
| Existing ten bundled skills lack skill-v1 manifests | Grandfather them as legacy bundles in `0.6.0`; do not retroactively call them verified. Require skill-v1 for newly promoted skills. Migrate existing bundles separately if desired. |
| New strict frontmatter requirements differ from general Agent Skills | Apply peer metadata requirements only to `bundled-plugin`; basic name/description/body checks apply elsewhere. Document PyYAML requirement for standalone verification. |
| Hash churn after edits | Any changed bundle file requires scaffold refresh or explicit manifest digest update, followed by re-verification. Any immutable contract-projection change also changes `contract_sha256` and reopens human review. This is intended. |
| Self-referential manifest hash | Exclude only `skill-formation-manifest.json` and fixed `.verification/**`; no arbitrary exclusion list. |
| Capability resolution differs by environment | Require a hashed capability snapshot for non-repository capabilities; never infer resolution. |
| Arbitrary code execution | Registered verifier never runs candidate scripts/tests. Trusted CI owns execution evidence. |
| Nondeterministic LLM behavior | Report run-scoped observations with model/config identity and digests; no generalization to proof. |
| Human evidence spoofing | Machine checks presence, digest scope, and integrity, not human identity or authenticity; wording remains `evidence_present`. Any bundle digest change reopens review. |
| Public evidence leakage | Bundled candidates must exclude private attestation wording, raw provenance, and hashes of guessable private text. Use a sanitized public review/promotion record scoped to the bundle digest; privacy review remains human and release-blocking. |
| Status inflation | Derived machine states live only in reports; manifest can request workflow states but cannot self-award conformance. |
| Static registration drift | Keep synchronized tuple/tests/docs checks and mutation tests. |
| Existing ambiguous `valid` convention | Do not remove it from old tools in this compatible release; new tool omits it. Deprecation can be considered separately. |
| Repository dirty state | Preserve unrelated `skills/5qln-cycle/SKILL.md` modification and isolate future implementation changes. |
| Version semantics | New backward-compatible tools, skill, and format justify `0.6.0`; changing conversion `1.0` or skill-v1 incompatibly later requires a new format ID and possibly a major plugin release. |

## 16. Phased implementation plan

### Phase 0 — Freeze design and golden contracts

Deliver:

- approved skill-v1 contract;
- fixture and run-record contracts;
- error-code registry;
- report vocabulary and promotion state machine;
- golden valid and invalid JSON fixtures.

Acceptance criteria:

- every requested field and status has one authority;
- no status lets K create X, Z, value alignment, or human-recognized return;
- unknown fields are rejected;
- conversion manifest remains separate and unchanged;
- human confirms that v1 review and promotion authorization are scoped to one immutable bundle digest.

### Phase 1 — Scaffold only

Implement `new_skill_manifest.py` and `fiveqln_create_skill_manifest`.

Tests:

- hashes and categorizes a complete bundle;
- starts human review open and promotion draft;
- refuses overwrite by default;
- rejects symlinks and path escapes;
- excludes only itself and `.verification/**`;
- emits deterministic byte-stable JSON for identical inputs.

Acceptance criteria: rerunning against an unchanged bundle produces identical semantic content and digests.

### Phase 2 — Static verifier core

Implement strict schema, path/hash inventory, YAML frontmatter, conversion recompilation, traceability, capability resolution, syntax parsing, boundary, and return/removal checks.

Tests:

- valid minimal candidate passes structurally;
- each error code has a focused negative fixture;
- all converter errors remain nested and visible;
- source/derived/proposal mutation tests fail correctly;
- candidate/human status elevation fails;
- no candidate code executes during verification;
- malformed YAML fails rather than being approximated.

Acceptance criteria: a structural pass is reproducible and the report contains no `valid` or `certified` field.

### Phase 3 — Behavioral observation ingestion

Implement fixture parsing, run-record digest checks, deterministic assertions, and observed-status aggregation.

Tests:

- all six required behavioral classes;
- every assertion kind;
- mismatched input/output/tool-trace hashes;
- insufficient, conflicting, passing, and failing run sets;
- mutation harness on temporary copies;
- observed pass never changes attestation status.

Acceptance criteria: identical fixture and run evidence produces byte-equivalent check results, while report language remains explicitly run-scoped.

### Phase 4 — Promotion inspection

Implement bundled-plugin repository synchronization checks.

Tests:

- missing registration;
- stale exact-set test;
- stale README and Architecture counts;
- missing tool in plugin.yaml/schemas/tools/registration;
- missing version/changelog entry;
- missing human review or promotion authorization;
- complete synchronized repository reaches `promotion_ready`; merge and release state remain external evidence.

Acceptance criteria: no machine-only evidence can cross the human review or promotion authorization gate.

### Phase 5 — Integration and release

Add the semantic skill, registered tools, docs, tests, version, and changelog together.

Acceptance criteria:

- `python -m compileall -q .` passes;
- full unittest discovery passes;
- clean-repository registration smoke test reports twelve skills and seven tools;
- legacy conversion workflows and all existing tests continue to pass;
- no unrelated working-tree change is included;
- public diff contains no personal data, session/wiki provenance, private evidence, or confidential credentials.

## 17. Acceptance matrix

| Requirement | Deterministic evidence | Observed evidence | Human authority |
|---|---|---|---|
| Bundle integrity | Paths, hashes, inventory, schema | none | none |
| SKILL.md conformance | YAML/frontmatter/body/anchors | none | none |
| Conversion provenance | Digest plus freshly generated nested compiler report | none | Human-only statuses remain in conversion evidence |
| Trigger behavior | Fixture declaration only | Agent run output/tool trace | Reviewer may accept usefulness |
| Non-trigger behavior | Fixture declaration only | Agent run output/tool trace | Reviewer may accept boundaries |
| Q-skip resistance | Trace requirement and fixture | Run-scoped phase/tool evidence | Human may recognize whether the process held |
| Honest open behavior | Prohibited status checks | Run-scoped output | Human alone may attest X/Z/value/return |
| Removal test | Concrete declared lost behavior | Mutation/run observation | Human may judge whether it matters |
| Promotion synchronization | Repository inspection | Trusted test/CI evidence | Explicit promotion authorization |
| “Living 5QLN skill” | not machine-verifiable | not established by runs | remains a human recognition, not a compiler status |

## 18. Architectural return

v1 now requires fresh human acceptance whenever the bundle digest changes. The remaining question is: **what future evidence, if any, could justify carrying human recognition across a bundle change without turning recognition into a reusable machine credential?**
