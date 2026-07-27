"""Published contract tests for skill-v1 formation artifacts."""

from __future__ import annotations

import json
import importlib.util
import re
import unittest
from pathlib import Path

HAS_JSONSCHEMA = importlib.util.find_spec("jsonschema") is not None


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_ROOT = ROOT / "skills" / "5qln-skill-formation" / "references"
SCHEMA_FILES = {
    "skill-v1.schema.json": "skill-v1",
    "behavior-fixture-v1.schema.json": "behavior-fixture-v1",
    "observed-run-v1.schema.json": "observed-run-v1",
    "tool-trace-v1.schema.json": "tool-trace-v1",
    "skill-report-v1.schema.json": "skill-report-v1",
}
STATUS_VOCABULARY = {
    "structural_status": {"not_run", "failed", "passed"},
    "behavioral_status": {
        "not_declared",
        "not_observed",
        "observed_failed",
        "observed_mixed",
        "observed_passed",
    },
    "attestation_status": {"open", "evidence_present"},
    "human_review_status": {"open", "changes_requested", "accepted"},
    "promotion_state": {
        "draft",
        "blocked",
        "structurally_conformant",
        "behaviorally_observed",
        "human_reviewed",
        "promotion_ready",
        "withdrawn",
    },
}


EXPECTED_ERROR_CODES = {
    "ASSERTION_INVALID",
    "CHECK_UNRESOLVED",
    "COMPLETION_MISSING",
    "CONVERSION_FAILED",
    "CONVERSION_HASH",
    "CONVERSION_MISSING",
    "DEPENDENCY_MISSING",
    "DOCS_DRIFT",
    "FILE_CATEGORY",
    "FILE_DUPLICATE",
    "FILE_MISSING",
    "FILE_TYPE_FORBIDDEN",
    "FILE_UNLISTED",
    "FIXTURE_CLASS_MISSING",
    "FIXTURE_SCHEMA",
    "FIXTURE_UNRESOLVED",
    "FORMATION_ORDER",
    "FRONTMATTER_INVALID",
    "HASH_MISMATCH",
    "HUMAN_EVIDENCE_MISSING",
    "HUMAN_EVIDENCE_SCOPE",
    "JSON_INVALID",
    "NON_TRIGGER_MISSING",
    "OBSERVATION_FAILED",
    "OBSERVATION_HASH",
    "OBSERVATION_INPUT",
    "OBSERVATION_INSUFFICIENT",
    "PATH_CASE_COLLISION",
    "PATH_ESCAPE",
    "PATH_INVALID",
    "PROMOTION_UNAUTHORIZED",
    "PUBLIC_EVIDENCE_FORBIDDEN",
    "READ_FAILED",
    "REGISTRATION_DRIFT",
    "RELATED_SKILL_DRIFT",
    "REMOVAL_TEST_VAGUE",
    "REQUIREMENT_BASIS",
    "REQUIREMENT_DUPLICATE",
    "REQUIREMENT_UNMAPPED",
    "RETURN_NOT_QUESTION",
    "SCHEMA_ENUM",
    "SCHEMA_EXTRA",
    "SCHEMA_MISSING",
    "SCHEMA_TYPE",
    "SCHEMA_VERSION",
    "SCRIPT_CHECK_UNSUPPORTED",
    "SCRIPT_SYNTAX",
    "SECTION_MISSING",
    "SIZE_LIMIT",
    "SKILL_BODY_EMPTY",
    "SKILL_DESCRIPTION",
    "SKILL_METADATA_MISSING",
    "SKILL_NAME_MISMATCH",
    "SKILL_UNRESOLVED",
    "SOURCE_CLASS_INVALID",
    "STATUS_ELEVATION",
    "SYMLINK_FORBIDDEN",
    "TOOL_UNRESOLVED",
    "TRIGGER_MISSING",
    "VERSION_DRIFT",
}

def iter_object_schemas(value: object, pointer: str = "$"):
    if isinstance(value, dict):
        if value.get("type") == "object" and "properties" in value:
            yield pointer, value
        for key, child in value.items():
            yield from iter_object_schemas(child, f"{pointer}/{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_object_schemas(child, f"{pointer}/{index}")


class SkillSchemaContractTests(unittest.TestCase):
    def load_schema(self, filename: str) -> dict:
        return json.loads((REFERENCE_ROOT / filename).read_text(encoding="utf-8"))

    def test_published_schemas_are_valid_json_and_closed_at_root(self) -> None:
        for filename, format_version in SCHEMA_FILES.items():
            with self.subTest(filename=filename):
                payload = self.load_schema(filename)
                self.assertEqual(
                    payload["$schema"],
                    "https://json-schema.org/draft/2020-12/schema",
                )
                self.assertEqual(payload["type"], "object")
                self.assertIs(payload["additionalProperties"], False)
                self.assertEqual(payload["properties"]["format_version"]["const"], format_version)

    def test_architecture_embeds_the_exact_published_skill_schema(self) -> None:
        architecture = (ROOT / "design" / "SKILL_V1_ARCHITECTURE.md").read_text(encoding="utf-8")
        section = architecture.split("### 5.2 Formal JSON Schema", 1)[1].split(
            "### 5.3 Cross-field invariants", 1
        )[0]
        embedded = json.loads(section.split("```json", 1)[1].split("```", 1)[0])
        self.assertEqual(embedded, self.load_schema("skill-v1.schema.json"))

    def test_every_declared_object_with_properties_rejects_unknown_fields(self) -> None:
        for filename in SCHEMA_FILES:
            payload = self.load_schema(filename)
            for pointer, schema in iter_object_schemas(payload):
                with self.subTest(filename=filename, pointer=pointer):
                    self.assertIs(
                        schema.get("additionalProperties"),
                        False,
                        f"{filename} leaves {pointer} open",
                    )

    def test_conversion_report_is_the_only_intentionally_open_object(self) -> None:
        open_objects: list[tuple[str, str]] = []
        for filename in SCHEMA_FILES:
            payload = self.load_schema(filename)

            def visit(value: object, pointer: str = "$") -> None:
                if isinstance(value, dict):
                    if value.get("type") == "object" and "additionalProperties" not in value:
                        open_objects.append((filename, pointer))
                    for key, child in value.items():
                        visit(child, f"{pointer}/{key}")
                elif isinstance(value, list):
                    for index, child in enumerate(value):
                        visit(child, f"{pointer}/{index}")

            visit(payload)

        self.assertEqual(
            open_objects,
            [("skill-report-v1.schema.json", "$/properties/conversion_report")],
        )

    def test_skill_manifest_has_no_author_supplied_machine_status(self) -> None:
        payload = self.load_schema("skill-v1.schema.json")
        properties = payload["properties"]
        self.assertNotIn("machine_status", properties)
        self.assertEqual(
            properties["promotion"]["properties"]["requested_state"]["enum"],
            ["draft", "review_requested", "promotion_requested", "withdrawn"],
        )

    def test_behavior_fixture_uses_the_frozen_class_vocabulary(self) -> None:
        payload = self.load_schema("behavior-fixture-v1.schema.json")
        fixture_classes = set(payload["properties"]["class"]["enum"])
        self.assertEqual(
            fixture_classes,
            {
                "positive_trigger",
                "near_miss_non_trigger",
                "human_attestation_boundary",
                "q_phase_skip_resistance",
                "missing_context_open_behavior",
                "removal_test",
                "mutation",
            },
        )

    def test_report_schema_keeps_evidence_dimensions_independent(self) -> None:
        payload = self.load_schema("skill-report-v1.schema.json")
        properties = payload["properties"]
        for field, vocabulary in STATUS_VOCABULARY.items():
            self.assertEqual(set(properties[field]["enum"]), vocabulary)
        self.assertNotIn("valid", properties)
        self.assertNotIn("certified", properties)
        self.assertNotIn("living", properties)

    def test_draft_manifest_can_leave_semantic_arrays_empty(self) -> None:
        payload = self.load_schema("skill-v1.schema.json")
        properties = payload["properties"]
        self.assertNotIn(
            "minItems",
            properties["contract"]["properties"]["behavioral_requirements"],
        )
        self.assertNotIn("minItems", properties["requirement_traceability"])
        self.assertNotIn("minItems", payload["$defs"]["contractItems"])

    def test_review_scope_binds_bundle_and_contract_digests(self) -> None:
        payload = self.load_schema("skill-v1.schema.json")
        skill = payload["properties"]["skill"]
        self.assertIn("contract_sha256", skill["required"])
        evidence = payload["properties"]["human_review"]["properties"]["evidence"]["items"]
        self.assertIn("scope_bundle_sha256", evidence["required"])
        self.assertIn("scope_contract_sha256", evidence["required"])
        self.assertIn("promotion_scope", evidence["required"])

    def test_observed_run_binds_the_exact_fixture(self) -> None:
        payload = self.load_schema("observed-run-v1.schema.json")
        self.assertIn("fixture_sha256", payload["required"])
        self.assertIn("fixture_sha256", payload["properties"])

    def test_fixture_contract_excludes_backtracking_regex(self) -> None:
        payload = self.load_schema("behavior-fixture-v1.schema.json")
        kinds = {
            branch["properties"]["kind"]["const"]
            for branch in payload["$defs"]["assertion"]["oneOf"]
        }
        self.assertNotIn("output_regex", kinds)

    def test_report_state_is_stateless_and_ends_at_promotion_ready(self) -> None:
        payload = self.load_schema("skill-report-v1.schema.json")
        properties = payload["properties"]
        self.assertIn("requested_state", payload["required"])
        self.assertIn("requested_state", properties)
        self.assertNotIn("promoted", properties["promotion_state"]["enum"])

    def test_golden_valid_and_invalid_examples_cover_every_format(self) -> None:
        fixture_root = ROOT / "tests" / "fixtures" / "skill-v1" / "contracts"
        for filename, format_version in SCHEMA_FILES.items():
            stem = filename.removesuffix(".schema.json")
            valid = json.loads((fixture_root / f"valid-{stem}.json").read_text(encoding="utf-8"))
            invalid = json.loads((fixture_root / f"invalid-{stem}-extra.json").read_text(encoding="utf-8"))
            with self.subTest(format_version=format_version):
                self.assertEqual(valid["format_version"], format_version)
                self.assertNotIn("unexpected", valid)
                self.assertEqual(invalid["format_version"], format_version)
                self.assertEqual(invalid["unexpected"], "SCHEMA_EXTRA")


@unittest.skipUnless(HAS_JSONSCHEMA, "install dev dependency: jsonschema")
class SkillSchemaInstanceTests(unittest.TestCase):
    def load_schema(self, filename: str) -> dict:
        return json.loads((REFERENCE_ROOT / filename).read_text(encoding="utf-8"))

    def test_golden_instances_validate_and_extra_fields_fail(self) -> None:
        import jsonschema

        fixture_root = ROOT / "tests" / "fixtures" / "skill-v1" / "contracts"
        for filename in SCHEMA_FILES:
            stem = filename.removesuffix(".schema.json")
            schema = self.load_schema(filename)
            with self.subTest(stem=stem, validity="valid"):
                jsonschema.Draft202012Validator(schema).validate(
                    json.loads((fixture_root / f"valid-{stem}.json").read_text())
                )
            with self.subTest(stem=stem, validity="invalid-extra"):
                with self.assertRaises(jsonschema.ValidationError):
                    jsonschema.Draft202012Validator(schema).validate(
                        json.loads((fixture_root / f"invalid-{stem}-extra.json").read_text())
                    )

    def test_adversarial_paths_are_schema_invalid(self) -> None:
        import jsonschema

        skill_schema = self.load_schema("skill-v1.schema.json")
        relative_path = skill_schema["$defs"]["relativePath"]
        evidence_path = skill_schema["$defs"]["evidencePath"]
        run_schema = self.load_schema("observed-run-v1.schema.json")
        run_path = run_schema["$defs"]["runPath"]
        for schema, values in (
            (relative_path, [".", "./foo", "a/../b", "a/./b", "../secret", ".verification/private", "C:\\secret", "a\\b", "nul\x00x"]),
            (evidence_path, [".verification/evidence/../secret", ".verification/evidence/./x"]),
            (run_path, ["runs/../secret", "runs/./x", "runs/a\\b"]),
        ):
            for value in values:
                with self.subTest(value=value):
                    self.assertFalse(jsonschema.Draft202012Validator(schema).is_valid(value))

    def test_assertion_types_and_mutation_class_are_schema_bound(self) -> None:
        import jsonschema

        fixture_root = ROOT / "tests" / "fixtures" / "skill-v1" / "contracts"
        base = json.loads((fixture_root / "valid-behavior-fixture-v1.json").read_text())
        schema = self.load_schema("behavior-fixture-v1.schema.json")
        validator = jsonschema.Draft202012Validator(schema)

        wrong_type = json.loads(json.dumps(base))
        wrong_type["expected"]["assertions"][0] = {
            "id": "ASSERT_1",
            "kind": "output_last_line_question",
            "value": "not-null",
        }
        self.assertFalse(validator.is_valid(wrong_type))

        unsafe_mutation = json.loads(json.dumps(base))
        unsafe_mutation["mutation"] = {
            "target": "../../outside",
            "operation": "delete_file",
            "selector": "file",
            "replacement": None,
            "expected_error_codes": ["FILE_MISSING"],
        }
        self.assertFalse(validator.is_valid(unsafe_mutation))

        missing_mutation = json.loads(json.dumps(base))
        missing_mutation["class"] = "mutation"
        self.assertFalse(validator.is_valid(missing_mutation))

    def test_report_rejects_contradictory_status_and_absolute_locations(self) -> None:
        import jsonschema

        fixture_root = ROOT / "tests" / "fixtures" / "skill-v1" / "contracts"
        base = json.loads((fixture_root / "valid-skill-report-v1.json").read_text())
        schema = self.load_schema("skill-report-v1.schema.json")
        validator = jsonschema.Draft202012Validator(schema)

        impossible = json.loads(json.dumps(base))
        impossible["promotion_ready"] = True
        self.assertFalse(validator.is_valid(impossible))

        failed_execution = json.loads(json.dumps(base))
        failed_execution["execution_success"] = False
        self.assertFalse(validator.is_valid(failed_execution))

        absolute_manifest = json.loads(json.dumps(base))
        absolute_manifest["manifest"]["path"] = "/opt/private/manifest.json"
        self.assertFalse(validator.is_valid(absolute_manifest))

    def test_report_finding_locations_are_typed_and_converter_v_empty_is_allowed(self) -> None:
        import jsonschema

        schema = self.load_schema("skill-report-v1.schema.json")
        finding_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$defs": schema["$defs"],
            "$ref": "#/$defs/finding",
        }
        validator = jsonschema.Draft202012Validator(finding_schema)
        valid = {
            "severity": "error",
            "dimension": "structure",
            "code": "CONVERSION/V∅",
            "location": {"kind": "relative_path", "value": "provenance/conversion.json"},
            "message": "Nested conversion corruption finding.",
            "evidence": ["CONVERSION/V∅"],
        }
        self.assertTrue(validator.is_valid(valid))
        leaked = json.loads(json.dumps(valid))
        leaked["location"] = {"kind": "relative_path", "value": "/opt/private"}
        self.assertFalse(validator.is_valid(leaked))
        leaked = json.loads(json.dumps(valid))
        leaked["evidence"] = ["/opt/private/session.db"]
        self.assertFalse(validator.is_valid(leaked))


class SkillRegistryContractTests(unittest.TestCase):
    def test_error_codes_match_the_exact_frozen_registry(self) -> None:
        text = (REFERENCE_ROOT / "error-codes.md").read_text(encoding="utf-8")
        codes = re.findall(r"^### `([A-Z][A-Z0-9_-]+)`$", text, flags=re.MULTILINE)
        self.assertEqual(len(codes), len(set(codes)), "duplicate error code")
        self.assertEqual(set(codes), EXPECTED_ERROR_CODES)

        architecture = (ROOT / "design" / "SKILL_V1_ARCHITECTURE.md").read_text(encoding="utf-8")
        architecture_codes = set(re.findall(r"\| `([A-Z][A-Z0-9_-]+)` \|", architecture))
        self.assertEqual(architecture_codes, EXPECTED_ERROR_CODES)

    def test_formation_protocol_contains_exact_status_vocabularies(self) -> None:
        text = (REFERENCE_ROOT / "formation-protocol.md").read_text(encoding="utf-8")
        for field, vocabulary in STATUS_VOCABULARY.items():
            with self.subTest(field=field):
                marker = f"`{field}`: "
                line = next(line for line in text.splitlines() if line.startswith(marker))
                tokens = re.findall(r"`([^`]+)`", line)
                documented = set(tokens[1:])
                self.assertEqual(documented, vocabulary)


if __name__ == "__main__":
    unittest.main()
