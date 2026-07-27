# skill-v1 error-code registry

Each code has one stable meaning. Existing conversion-compiler findings remain nested as `CONVERSION/<existing-code>` and are not renamed. None of the codes below adds a constitutional corruption code beyond L1, L2, L3, L4, and V∅.

## Execution and schema

### `READ_FAILED`
- Severity: error
- Condition: a required input cannot be read.
- Path: affected invocation field or relative file.
- Repair: restore access or supply the correct file.
- Boundary: no conformance result is issued.

### `JSON_INVALID`
- Severity: error
- Condition: required JSON bytes cannot be parsed.
- Path: affected JSON file.
- Repair: provide valid UTF-8 JSON.
- Boundary: parse failure proves nothing about the candidate.

### `SCHEMA_VERSION`
- Severity: error
- Condition: `format_version` is unsupported.
- Path: `/format_version`.
- Repair: use the exact published format identifier.
- Boundary: versions are not silently upgraded.

### `SCHEMA_TYPE`
- Severity: error
- Condition: a value has the wrong JSON type.
- Path: offending JSON pointer.
- Repair: use the type required by the schema.
- Boundary: structural only.

### `SCHEMA_MISSING`
- Severity: error
- Condition: a required field is absent.
- Path: missing field pointer.
- Repair: add the field without inventing evidence.
- Boundary: missing human evidence must remain open.

### `SCHEMA_ENUM`
- Severity: error
- Condition: a value is outside its closed vocabulary.
- Path: offending JSON pointer.
- Repair: use an allowed value or change the format version.
- Boundary: no fuzzy normalization.

### `SCHEMA_EXTRA`
- Severity: error
- Condition: an unknown field occurs in a closed object.
- Path: extra field pointer.
- Repair: remove it or define it in a future format.
- Boundary: author fields cannot smuggle machine status.

### `DEPENDENCY_MISSING`
- Severity: error
- Condition: an exact parser required for verification is unavailable.
- Path: dependency name.
- Repair: install the documented dependency in an isolated environment.
- Boundary: the verifier fails closed rather than approximating.

## Filesystem and bundle

### `PATH_INVALID`
- Severity: error
- Condition: a declared path violates relative POSIX rules.
- Path: path field.
- Repair: use a normalized relative POSIX path.
- Boundary: no host-dependent normalization.

### `PATH_ESCAPE`
- Severity: error
- Condition: a path resolves outside the bundle root.
- Path: path field.
- Repair: move the file inside the bundle.
- Boundary: prevents traversal across the file boundary.

### `SYMLINK_FORBIDDEN`
- Severity: error
- Condition: a candidate bundle member is a symlink.
- Path: symlink path.
- Repair: replace it with an inventoried regular file.
- Boundary: targets are never followed.

### `FILE_TYPE_FORBIDDEN`
- Severity: error
- Condition: a FIFO, socket, device, or other non-regular member exists.
- Path: filesystem member.
- Repair: remove the special file.
- Boundary: only captured regular bytes are verified.

### `FILE_MISSING`
- Severity: error
- Condition: a declared file is absent.
- Path: declared file.
- Repair: restore it or refresh the manifest.
- Boundary: absence is not inferred as intentional release.

### `FILE_UNLISTED`
- Severity: error
- Condition: a regular bundle file is omitted from inventory.
- Path: actual file.
- Repair: refresh the scaffold.
- Boundary: hidden content cannot bypass the digest.

### `FILE_DUPLICATE`
- Severity: error
- Condition: a path is listed more than once.
- Path: duplicate record.
- Repair: retain one category-correct record.
- Boundary: every byte has one inventory identity.

### `PATH_CASE_COLLISION`
- Severity: error
- Condition: distinct paths collide under Unicode case-folding.
- Path: colliding paths.
- Repair: rename one path.
- Boundary: protects cross-platform portability.

### `FILE_CATEGORY`
- Severity: error
- Condition: an inventoried path is in the wrong bundle category.
- Path: file record.
- Repair: move or recategorize it.
- Boundary: category semantics remain explicit.

### `HASH_MISMATCH`
- Severity: error
- Condition: captured bytes do not match declared SHA-256.
- Path: file record.
- Repair: refresh the manifest or restore approved bytes.
- Boundary: any bundle change reopens review.

### `SIZE_LIMIT`
- Severity: error
- Condition: a defined file, total, count, depth, observed-run, or report bound is exceeded.
- Path: bounded object.
- Repair: reduce the artifact or use a future explicit format.
- Boundary: bounded verification prevents resource abuse.

## Skill contract

### `FRONTMATTER_INVALID`
- Severity: error
- Condition: delimiters or YAML mapping are invalid.
- Path: `SKILL.md` frontmatter.
- Repair: provide strict valid YAML at byte zero.
- Boundary: malformed YAML is never approximated.

### `SKILL_NAME_MISMATCH`
- Severity: error
- Condition: directory, manifest, and frontmatter names differ.
- Path: skill name surfaces.
- Repair: make all three exact.
- Boundary: one skill has one identity.

### `SKILL_DESCRIPTION`
- Severity: error
- Condition: description is absent, empty, or over 1024 characters.
- Path: frontmatter description.
- Repair: provide concise trigger-focused text.
- Boundary: does not prove trigger quality.

### `SKILL_BODY_EMPTY`
- Severity: error
- Condition: no body follows frontmatter.
- Path: `SKILL.md`.
- Repair: add an operational body.
- Boundary: body presence is structural only.

### `SKILL_METADATA_MISSING`
- Severity: conditional error or warning
- Condition: target-required peer metadata is absent.
- Path: frontmatter.
- Repair: add version, author, license, tags, or related skills as required.
- Boundary: bundled-plugin rules are stricter than local skill rules.

### `SECTION_MISSING`
- Severity: error
- Condition: a required heading or declared anchor is absent or ambiguous.
- Path: `SKILL.md` anchor.
- Repair: add one unique section.
- Boundary: heading presence does not prove semantic quality.

### `TRIGGER_MISSING`
- Severity: error
- Condition: no explicit positive trigger maps to the skill body.
- Path: contract triggers.
- Repair: declare when the skill must load.
- Boundary: marker observed, not behavior proven.

### `NON_TRIGGER_MISSING`
- Severity: error
- Condition: no explicit counter-trigger maps to the skill body.
- Path: contract non-triggers.
- Repair: declare when the skill must not load.
- Boundary: actual restraint requires observation.

### `COMPLETION_MISSING`
- Severity: error
- Condition: completion criteria are absent or unmapped.
- Path: completion contract.
- Repair: add checkable criteria.
- Boundary: criteria do not self-award completion.

### `RELATED_SKILL_DRIFT`
- Severity: error
- Condition: manifest and frontmatter related-skill sets disagree.
- Path: related skills.
- Repair: synchronize declarations.
- Boundary: resolution is checked separately.

### `TOOL_UNRESOLVED`
- Severity: error or warning by required flag
- Condition: a claimed tool cannot be resolved from an allowed surface.
- Path: claimed tool.
- Repair: register it, provide a hashed capability snapshot, or mark it optional.
- Boundary: plausible names are not evidence.

### `SKILL_UNRESOLVED`
- Severity: error or warning by required flag
- Condition: a related skill cannot be resolved.
- Path: related skill.
- Repair: supply or correct the declaration.
- Boundary: current-profile discovery is not universal authority.

### `SCRIPT_SYNTAX`
- Severity: error
- Condition: a supported script fails syntax parsing.
- Path: script.
- Repair: correct syntax.
- Boundary: parsing never executes candidate code.

### `SCRIPT_CHECK_UNSUPPORTED`
- Severity: warning
- Condition: no exact safe parser exists for a script type.
- Path: script.
- Repair: provide trusted CI evidence or a supported declarative form.
- Boundary: unsupported checks never pass silently.

## Provenance, traceability, and human boundary

### `CONVERSION_MISSING`
- Severity: error
- Condition: referenced conversion manifest is absent.
- Path: provenance conversion path.
- Repair: include the artifact.
- Boundary: skill verification cannot replace formation provenance.

### `CONVERSION_HASH`
- Severity: error
- Condition: conversion-manifest bytes do not match the declared digest.
- Path: provenance conversion record.
- Repair: restore bytes or refresh the skill manifest.
- Boundary: stored reports are not trusted.

### `CONVERSION_FAILED`
- Severity: error
- Condition: a fresh existing-compiler run reports errors.
- Path: nested conversion report.
- Repair: repair the conversion manifest.
- Boundary: a pass remains structural evidence only.

### `FORMATION_ORDER`
- Severity: error
- Condition: required S→G→Q→P→V structure is absent or contradicted.
- Path: conversion document cell.
- Repair: restore ordered formation without manufacturing attestations.
- Boundary: optional phase logs cannot repair it.

### `REQUIREMENT_DUPLICATE`
- Severity: error
- Condition: a requirement identifier repeats.
- Path: requirement rows.
- Repair: give each requirement one stable ID.
- Boundary: prevents ambiguous authority.

### `REQUIREMENT_UNMAPPED`
- Severity: error
- Condition: a requirement lacks a skill section or verifier mapping.
- Path: traceability row.
- Repair: add resolvable mappings.
- Boundary: mapping presence is not semantic proof.

### `REQUIREMENT_BASIS`
- Severity: error
- Condition: source or derived requirement lacks a resolvable basis.
- Path: basis fields.
- Repair: cite source units or derived insights.
- Boundary: proposals remain non-normative.

### `SOURCE_CLASS_INVALID`
- Severity: error
- Condition: source, derived, and proposal constraints are collapsed or contradicted.
- Path: requirement class and bases.
- Repair: separate the classes and their authority.
- Boundary: derivation cannot rewrite source.

### `CHECK_UNRESOLVED`
- Severity: error
- Condition: a named static verifier check is not implemented.
- Path: verifier check reference.
- Repair: implement or remove the claim.
- Boundary: names do not prove checks ran.

### `FIXTURE_UNRESOLVED`
- Severity: error
- Condition: a fixture reference is missing or duplicated.
- Path: fixture ID.
- Repair: supply one matching fixture.
- Boundary: declarations are not observations.

### `HUMAN_EVIDENCE_MISSING`
- Severity: error
- Condition: accepted review or promotion authorization lacks required hashed evidence.
- Path: human review.
- Repair: keep status open or supply explicit evidence.
- Boundary: the machine does not originate evidence.

### `HUMAN_EVIDENCE_SCOPE`
- Severity: error
- Condition: review evidence has the wrong bundle or contract digest, promotion evidence has the wrong target/repository/version/revision scope, or skill evidence attempts to create X, Z, value, or return outside conversion provenance.
- Path: evidence scope.
- Repair: scope review to the exact bundle and contract bytes; scope promotion authorization to one repository target and intended release; keep human-only conversion claims separate.
- Boundary: presence is not authenticity.

### `PUBLIC_EVIDENCE_FORBIDDEN`
- Severity: error when directly detectable
- Condition: public bundled evidence contains a forbidden private field or path.
- Path: public evidence.
- Repair: replace it with a sanitized public record.
- Boundary: this guard is not a complete privacy proof.

### `STATUS_ELEVATION`
- Severity: error
- Condition: claimed state exceeds available machine, observation, or human evidence.
- Path: status field.
- Repair: lower the requested state or supply proper evidence.
- Boundary: manifests cannot self-award conformance.

### `RETURN_NOT_QUESTION`
- Severity: error
- Condition: candidate return is not question-bearing.
- Path: conversion completion return.
- Repair: provide a real open question.
- Boundary: syntax does not establish a living return.

### `REMOVAL_TEST_VAGUE`
- Severity: promotion error or draft warning
- Condition: no concrete behavior or gate is lost when 5QLN is removed.
- Path: removal test.
- Repair: identify the behavior and associated fixture.
- Boundary: human judgment of importance remains open.

## Fixtures, observations, and promotion

### `FIXTURE_SCHEMA`
- Severity: error
- Condition: a fixture violates its closed schema.
- Path: fixture.
- Repair: conform to `behavior-fixture-v1`.
- Boundary: a valid fixture is only a test declaration.

### `FIXTURE_CLASS_MISSING`
- Severity: promotion error
- Condition: a required bundled-promotion fixture class is absent.
- Path: behavioral fixtures.
- Repair: declare the missing class.
- Boundary: observation remains separate.

### `ASSERTION_INVALID`
- Severity: error
- Condition: assertion kind and value do not form an allowed pair.
- Path: assertion.
- Repair: use the closed deterministic vocabulary.
- Boundary: arbitrary evaluators are forbidden.

### `OBSERVATION_HASH`
- Severity: error
- Condition: run artifacts do not match declared digests.
- Path: observed run.
- Repair: restore or regenerate trusted run evidence.
- Boundary: stale or altered runs are not evidence.

### `OBSERVATION_INPUT`
- Severity: error
- Condition: observed input does not match the fixture input.
- Path: run input digest.
- Repair: rerun the exact fixture.
- Boundary: near matches are inapplicable.

### `OBSERVATION_INSUFFICIENT`
- Severity: warning or promotion blocker
- Condition: qualifying runs do not meet minimum policy.
- Path: fixture observation policy.
- Repair: provide more qualifying runs.
- Boundary: absence remains open.

### `OBSERVATION_FAILED`
- Severity: warning
- Condition: a deterministic assertion fails against supplied run bytes.
- Path: fixture assertion and run.
- Repair: inspect the candidate or revise an unjustified assertion through review.
- Boundary: one run does not prove general behavior.

### `REGISTRATION_DRIFT`
- Severity: promotion error
- Condition: requested bundled skill registration surfaces disagree.
- Path: repository registration files.
- Repair: synchronize exact names and tests.
- Boundary: registration is not discoverability or aliveness.

### `DOCS_DRIFT`
- Severity: promotion error
- Condition: counts, lists, usage, or proof-boundary docs are stale.
- Path: documentation.
- Repair: synchronize public documentation.
- Boundary: docs must not inflate claims.

### `VERSION_DRIFT`
- Severity: promotion error
- Condition: plugin version and changelog are inconsistent.
- Path: release metadata.
- Repair: use one intended compatible version and note migration.
- Boundary: versioning does not certify formation.

### `PROMOTION_UNAUTHORIZED`
- Severity: error
- Condition: promotion is requested without exact-digest authorization evidence.
- Path: promotion authorization IDs.
- Repair: keep the candidate in review or supply explicit authorization.
- Boundary: machine evidence cannot cross this gate.
