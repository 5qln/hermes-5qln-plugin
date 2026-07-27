"""Published contract tests for skill-v1 formation artifacts."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_ROOT = ROOT / "skills" / "5qln-skill-formation" / "references"
SCHEMA_FILES = {
    "skill-v1.schema.json": "skill-v1",
    "behavior-fixture-v1.schema.json": "behavior-fixture-v1",
    "observed-run-v1.schema.json": "observed-run-v1",
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
        if "properties" in value:
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
                self.assertFalse(payload["additionalProperties"])
                self.assertEqual(
                    payload["properties"]["format_version"]["const"],
                    format_version,
                )

    def test_every_declared_object_with_properties_rejects_unknown_fields(self) -> None:
        for filename in SCHEMA_FILES:
            payload = self.load_schema(filename)
            for pointer, schema in iter_object_schemas(payload):
                with self.subTest(filename=filename, pointer=pointer):
                    self.assertIs(
                        schema.get("additionalProperties"),
                        False,
                        f"open object schema at {pointer}",
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
        kinds = payload["$defs"]["assertion"]["properties"]["kind"]["enum"]
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
