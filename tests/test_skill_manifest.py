"""Published contract tests for skill-v1 formation artifacts."""

from __future__ import annotations

import json
import importlib.util
import re
import unittest
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest import mock

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


class SkillCommonContractTests(unittest.TestCase):
    """Tests for skills/5qln-skill-formation/scripts/skill_common.py."""

    @classmethod
    def setUpClass(cls) -> None:
        sys.path.insert(0, str(ROOT / "skills" / "5qln-skill-formation" / "scripts"))
        global skill_common
        import skill_common

    @classmethod
    def tearDownClass(cls) -> None:
        sys.path.remove(str(ROOT / "skills" / "5qln-skill-formation" / "scripts"))

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # --- constants ---
    def test_constants_are_reasonable(self) -> None:
        self.assertEqual(skill_common.MAX_FILES, 512)
        self.assertEqual(skill_common.MAX_FILE_BYTES, 10 * 1024 * 1024)
        self.assertEqual(skill_common.MAX_TOTAL_BYTES, 50 * 1024 * 1024)
        self.assertEqual(skill_common.MAX_DEPTH, 32)

    # --- canonical_json_bytes ---
    def test_canonical_json_is_stable_int(self) -> None:
        a = skill_common.canonical_json_bytes({"b": 1, "a": 2})
        b = skill_common.canonical_json_bytes({"a": 2, "b": 1})
        self.assertEqual(a, b)
        self.assertEqual(a, b'{"a":2,"b":1}')

    def test_canonical_json_is_stable_str(self) -> None:
        a = skill_common.canonical_json_bytes({"z": "hello", "a": "world"})
        self.assertEqual(a, b'{"a":"world","z":"hello"}')

    def test_canonical_json_survives_roundtrip(self) -> None:
        payload = {"key": "val", "nested": {"b": 1, "a": [3, 2, 1]}}
        self.assertEqual(payload, json.loads(skill_common.canonical_json_bytes(payload)))

    # --- sha256_bytes ---
    def test_sha256_of_empty(self) -> None:
        self.assertEqual(
            skill_common.sha256_bytes(b""),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )

    def test_sha256_of_known(self) -> None:
        self.assertEqual(
            skill_common.sha256_bytes(b"hello world"),
            "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9",
        )

    def test_sha256_is_stable(self) -> None:
        self.assertEqual(skill_common.sha256_bytes(b"a"), skill_common.sha256_bytes(b"a"))

    # --- normalize_relative_path ---
    def test_normalize_passes_clean_path(self) -> None:
        self.assertEqual(skill_common.normalize_relative_path("a/b/c"), "a/b/c")

    def test_normalize_rejects_absolute(self) -> None:
        with self.assertRaises(skill_common.SkillContractError) as ctx:
            skill_common.normalize_relative_path("/etc/passwd")
        self.assertEqual(ctx.exception.code, "PATH_ESCAPE")

    def test_normalize_rejects_dotdot(self) -> None:
        with self.assertRaises(skill_common.SkillContractError) as ctx:
            skill_common.normalize_relative_path("a/../b")
        self.assertEqual(ctx.exception.code, "PATH_ESCAPE")

    def test_normalize_rejects_dot_segment(self) -> None:
        with self.assertRaises(skill_common.SkillContractError):
            skill_common.normalize_relative_path("./foo")

    def test_normalize_rejects_backslash(self) -> None:
        with self.assertRaises(skill_common.SkillContractError):
            skill_common.normalize_relative_path("a\\b")

    def test_normalize_rejects_null(self) -> None:
        with self.assertRaises(skill_common.SkillContractError):
            skill_common.normalize_relative_path("a\x00b")

    def test_normalize_rejects_empty(self) -> None:
        with self.assertRaises(skill_common.SkillContractError):
            skill_common.normalize_relative_path("")

    def test_normalize_rejects_dot(self) -> None:
        with self.assertRaises(skill_common.SkillContractError):
            skill_common.normalize_relative_path(".")

    def test_normalize_rejects_verification(self) -> None:
        with self.assertRaises(skill_common.SkillContractError) as ctx:
            skill_common.normalize_relative_path(".verification/evidence/x")
        self.assertEqual(ctx.exception.code, "PATH_INVALID")

    def test_normalize_rejects_trailing_slash(self) -> None:
        with self.assertRaises(skill_common.SkillContractError):
            skill_common.normalize_relative_path("a/b/")

    def test_normalize_rejects_trailing_dotdot(self) -> None:
        with self.assertRaises(skill_common.SkillContractError):
            skill_common.normalize_relative_path("a/..")

    def test_normalize_rejects_dot_as_standalone(self) -> None:
        with self.assertRaises(skill_common.SkillContractError):
            skill_common.normalize_relative_path(".")

    # --- inspect_regular_file ---
    def test_inspect_regular_file_basic(self) -> None:
        f = self.tmp / "hello.txt"
        f.write_text("hello", encoding="utf-8")
        info = skill_common.inspect_regular_file(self.tmp, "hello.txt")
        self.assertEqual(info["path"], "hello.txt")
        self.assertEqual(info["size_bytes"], 5)
        self.assertEqual(len(info["sha256"]), 64)

    def test_inspect_rejects_symlink(self) -> None:
        target = self.tmp / "real.txt"
        target.write_text("real")
        link = self.tmp / "link.txt"
        os.symlink(str(target), str(link))
        with self.assertRaises(skill_common.SkillContractError) as ctx:
            skill_common.inspect_regular_file(self.tmp, "link.txt")
        self.assertIn(ctx.exception.code, ("SYMLINK_FORBIDDEN", "FILE_TYPE_FORBIDDEN"))

    def test_inspect_rejects_missing(self) -> None:
        with self.assertRaises(skill_common.SkillContractError) as ctx:
            skill_common.inspect_regular_file(self.tmp, "nope.txt")
        self.assertEqual(ctx.exception.code, "FILE_MISSING")

    def test_inspect_rejects_oversized(self) -> None:
        f = self.tmp / "big.txt"
        f.write_bytes(b"x" * (skill_common.MAX_FILE_BYTES + 1))
        with self.assertRaises(skill_common.SkillContractError) as ctx:
            skill_common.inspect_regular_file(self.tmp, "big.txt")
        self.assertEqual(ctx.exception.code, "SIZE_LIMIT")

    def test_inspect_read_once_produces_consistent_hash(self) -> None:
        f = self.tmp / "data.bin"
        f.write_bytes(b"\x00\x01\x02\x03\x04")
        a = skill_common.inspect_regular_file(self.tmp, "data.bin")
        b = skill_common.inspect_regular_file(self.tmp, "data.bin")
        self.assertEqual(a["sha256"], b["sha256"])
        self.assertEqual(a["size_bytes"], b["size_bytes"])

    # --- inventory_bundle ---
    def test_inventory_excludes_manifest_and_verification(self) -> None:
        (self.tmp / "SKILL.md").write_text("# Test")
        (self.tmp / "ref.md").write_text("ref")
        (self.tmp / "skill-formation-manifest.json").write_text("{}")
        (self.tmp / ".verification").mkdir()
        (self.tmp / ".verification" / "run.json").write_text("{}")
        inv = skill_common.inventory_bundle(self.tmp)
        paths = {r["path"] for r in inv}
        self.assertIn("SKILL.md", paths)
        self.assertIn("ref.md", paths)
        self.assertNotIn("skill-formation-manifest.json", paths)
        self.assertNotIn(".verification/run.json", paths)

    def test_inventory_returns_sorted(self) -> None:
        (self.tmp / "c.txt").write_text("c")
        (self.tmp / "a.txt").write_text("a")
        (self.tmp / "b.txt").write_text("b")
        inv = skill_common.inventory_bundle(self.tmp)
        paths = [r["path"] for r in inv]
        self.assertEqual(paths, ["a.txt", "b.txt", "c.txt"])

    def test_inventory_rejects_symlinks(self) -> None:
        (self.tmp / "real.txt").write_text("real")
        os.symlink(str(self.tmp / "real.txt"), str(self.tmp / "link.txt"))
        with self.assertRaises(skill_common.SkillContractError):
            skill_common.inventory_bundle(self.tmp)

    def test_inventory_rejects_excess_files(self) -> None:
        for i in range(skill_common.MAX_FILES + 1):
            (self.tmp / f"f{i:04d}.txt").write_text("x")
        with self.assertRaises(skill_common.SkillContractError) as ctx:
            skill_common.inventory_bundle(self.tmp)
        self.assertEqual(ctx.exception.code, "SIZE_LIMIT")

    def test_inventory_rejects_excess_depth(self) -> None:
        d = self.tmp
        for _ in range(skill_common.MAX_DEPTH + 1):
            d = d / "sub"
        d.mkdir(parents=True)
        (d / "deep.txt").write_text("deep")
        with self.assertRaises(skill_common.SkillContractError) as ctx:
            skill_common.inventory_bundle(self.tmp)
        self.assertEqual(ctx.exception.code, "SIZE_LIMIT")

    def test_inventory_rejects_excess_total_bytes(self) -> None:
        (self.tmp / "big.txt").write_bytes(b"x" * (skill_common.MAX_TOTAL_BYTES + 1))
        with self.assertRaises(skill_common.SkillContractError) as ctx:
            skill_common.inventory_bundle(self.tmp)
        self.assertEqual(ctx.exception.code, "SIZE_LIMIT")

    def test_inventory_handles_case_collision(self) -> None:
        (self.tmp / "File.txt").write_text("a")
        (self.tmp / "file.txt").write_text("b")
        with self.assertRaises(skill_common.SkillContractError) as ctx:
            skill_common.inventory_bundle(self.tmp)
        self.assertEqual(ctx.exception.code, "PATH_CASE_COLLISION")

    # --- compute_bundle_sha256 ---
    def test_bundle_sha256_is_deterministic(self) -> None:
        files = [
            {"path": "a.txt", "sha256": skill_common.sha256_bytes(b"a"), "size_bytes": 1},
            {"path": "b.txt", "sha256": skill_common.sha256_bytes(b"b"), "size_bytes": 1},
        ]
        self.assertEqual(
            skill_common.compute_bundle_sha256(files),
            skill_common.compute_bundle_sha256(files),
        )

    def test_bundle_sha256_changes_with_content(self) -> None:
        a = [{"path": "x.txt", "sha256": skill_common.sha256_bytes(b"a"), "size_bytes": 1}]
        b = [{"path": "x.txt", "sha256": skill_common.sha256_bytes(b"b"), "size_bytes": 1}]
        self.assertNotEqual(skill_common.compute_bundle_sha256(a), skill_common.compute_bundle_sha256(b))

    # --- SkillContractError ---
    def test_error_repr_includes_code_and_message(self) -> None:
        err = skill_common.SkillContractError("TEST_CODE", "test message", "a/b")
        s = str(err)
        self.assertIn("TEST_CODE", s)
        self.assertIn("test message", s)
        self.assertIn("a/b", s)

    def test_error_path_is_optional(self) -> None:
        err = skill_common.SkillContractError("NO_PATH", "no path")
        self.assertIsNone(err.path)

    # --- atomic_write_json ---
    def test_atomic_write_creates_file(self) -> None:
        path = self.tmp / "out.json"
        skill_common.atomic_write_json(path, {"a": 1}, overwrite=False)
        self.assertTrue(path.exists())
        self.assertEqual(json.loads(path.read_text()), {"a": 1})

    def test_atomic_write_refuses_overwrite_by_default(self) -> None:
        path = self.tmp / "out.json"
        path.write_text("existing")
        with self.assertRaises(skill_common.SkillContractError) as ctx:
            skill_common.atomic_write_json(path, {"a": 1}, overwrite=False)
        self.assertEqual(ctx.exception.code, "FILE_DUPLICATE")

    def test_atomic_write_overwrite_ok(self) -> None:
        path = self.tmp / "out.json"
        path.write_text("existing")
        skill_common.atomic_write_json(path, {"a": 1}, overwrite=True)
        self.assertEqual(json.loads(path.read_text()), {"a": 1})

    def test_atomic_write_is_deterministic(self) -> None:
        p1 = self.tmp / "a.json"
        p2 = self.tmp / "b.json"
        payload = {"key": "value", "list": [1, 2, 3]}
        skill_common.atomic_write_json(p1, payload, overwrite=False)
        skill_common.atomic_write_json(p2, payload, overwrite=False)
        self.assertEqual(p1.read_bytes(), p2.read_bytes())


class SkillScaffoldTests(unittest.TestCase):
    """Tests for skills/5qln-skill-formation/scripts/new_skill_manifest.py."""

    @classmethod
    def setUpClass(cls) -> None:
        sys.path.insert(0, str(ROOT / "skills" / "5qln-skill-formation" / "scripts"))
        global new_skill_manifest, skill_common
        import new_skill_manifest, skill_common

    @classmethod
    def tearDownClass(cls) -> None:
        sys.path.remove(str(ROOT / "skills" / "5qln-skill-formation" / "scripts"))

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @property
    def minimal_fixture(self) -> Path:
        return ROOT / "tests" / "fixtures" / "skill-v1" / "valid-minimal"

    def test_scaffold_has_format_version(self) -> None:
        manifest = new_skill_manifest.build_manifest(
            self.minimal_fixture, "provenance/conversion-manifest.json"
        )
        self.assertEqual(manifest["format_version"], "skill-v1")
        self.assertEqual(manifest["skill"]["bundle_root"], ".")

    def test_scaffold_inventories_bundle(self) -> None:
        manifest = new_skill_manifest.build_manifest(
            self.minimal_fixture, "provenance/conversion-manifest.json"
        )
        bundle = manifest["bundle"]
        self.assertEqual(bundle["skill_md"]["path"], "SKILL.md")
        self.assertTrue(len(bundle["skill_md"]["sha256"]) == 64)

        # Check categorization
        ref_paths = {r["path"] for r in bundle["references"]}
        self.assertIn("references/guide.md", ref_paths)

        script_paths = {r["path"] for r in bundle["scripts"]}
        self.assertIn("scripts/helper.py", script_paths)

    def test_scaffold_excludes_manifest_and_verification(self) -> None:
        manifest = new_skill_manifest.build_manifest(
            self.minimal_fixture, "provenance/conversion-manifest.json"
        )
        all_paths = []
        for cat in ("references", "scripts", "tests", "fixtures", "provenance"):
            all_paths.extend(r["path"] for r in manifest["bundle"][cat])
        all_paths.append(manifest["bundle"]["skill_md"]["path"])
        self.assertNotIn("skill-formation-manifest.json", all_paths)

    def test_scaffold_has_bundle_digest(self) -> None:
        manifest = new_skill_manifest.build_manifest(
            self.minimal_fixture, "provenance/conversion-manifest.json"
        )
        self.assertEqual(len(manifest["skill"]["bundle_sha256"]), 64)

    def test_scaffold_leaves_human_review_open(self) -> None:
        manifest = new_skill_manifest.build_manifest(
            self.minimal_fixture, "provenance/conversion-manifest.json"
        )
        self.assertEqual(manifest["human_review"]["status"], "open")
        self.assertIsNone(manifest["human_review"]["reviewer"])
        self.assertEqual(manifest["human_review"]["evidence"], [])

    def test_scaffold_promotion_starts_draft(self) -> None:
        manifest = new_skill_manifest.build_manifest(
            self.minimal_fixture, "provenance/conversion-manifest.json"
        )
        self.assertEqual(manifest["promotion"]["requested_state"], "draft")

    def test_scaffold_is_deterministic(self) -> None:
        a = new_skill_manifest.build_manifest(
            self.minimal_fixture, "provenance/conversion-manifest.json"
        )
        b = new_skill_manifest.build_manifest(
            self.minimal_fixture, "provenance/conversion-manifest.json"
        )
        self.assertEqual(
            skill_common.canonical_json_bytes(a),
            skill_common.canonical_json_bytes(b),
        )

    def test_scaffold_rejects_missing_skill_md(self) -> None:
        empty = self.tmp
        with self.assertRaises(skill_common.SkillContractError) as ctx:
            new_skill_manifest.build_manifest(empty, "provenance/conversion-manifest.json")
        self.assertEqual(ctx.exception.code, "FILE_MISSING")

    def test_scaffold_rejects_missing_conversion_manifest(self) -> None:
        with self.assertRaises(skill_common.SkillContractError) as ctx:
            new_skill_manifest.build_manifest(
                self.minimal_fixture, "nonexistent/manifest.json"
            )
        self.assertEqual(ctx.exception.code, "FILE_MISSING")

    def test_scaffold_rejects_conversion_outside_root(self) -> None:
        with self.assertRaises(skill_common.SkillContractError) as ctx:
            new_skill_manifest.build_manifest(
                self.minimal_fixture, "../outside/manifest.json"
            )
        self.assertEqual(ctx.exception.code, "PATH_ESCAPE")

    def test_scaffold_contract_sha256_matches(self) -> None:
        manifest = new_skill_manifest.build_manifest(
            self.minimal_fixture, "provenance/conversion-manifest.json"
        )
        self.assertIn("contract_sha256", manifest["skill"])
        self.assertEqual(len(manifest["skill"]["contract_sha256"]), 64)

    def test_cli_scaffold_and_overwrite_protection(self) -> None:
        out = self.tmp / "manifest.json"
        exit_code = new_skill_manifest.main([
            "new_skill_manifest.py",
            str(self.minimal_fixture),
            "--out", str(out),
            "--conversion-manifest", "provenance/conversion-manifest.json",
        ])
        self.assertEqual(exit_code, 0)
        self.assertTrue(out.exists())

        # Overwrite refusal
        exit_code2 = new_skill_manifest.main([
            "new_skill_manifest.py",
            str(self.minimal_fixture),
            "--out", str(out),
            "--conversion-manifest", "provenance/conversion-manifest.json",
        ])
        self.assertEqual(exit_code2, 2)

        # Overwrite allowed
        exit_code3 = new_skill_manifest.main([
            "new_skill_manifest.py",
            str(self.minimal_fixture),
            "--out", str(out),
            "--conversion-manifest", "provenance/conversion-manifest.json",
            "--overwrite",
        ])
        self.assertEqual(exit_code3, 0)



class SkillManifestValidationTests(unittest.TestCase):
    """Tests for validate_skill_manifest against the published contract."""

    @classmethod
    def setUpClass(cls) -> None:
        sys.path.insert(0, str(ROOT / "skills" / "5qln-skill-formation" / "scripts"))
        global skill_common
        import skill_common

    @classmethod
    def tearDownClass(cls) -> None:
        sys.path.remove(str(ROOT / "skills" / "5qln-skill-formation" / "scripts"))

    def _load_fixture(self, name: str) -> dict:
        return json.loads(
            (ROOT / "tests" / "fixtures" / "skill-v1" / "contracts" / name).read_text()
        )

    def test_valid_manifest_passes(self) -> None:
        payload = self._load_fixture("valid-skill-v1.json")
        findings = skill_common.validate_skill_manifest(payload)
        self.assertEqual(findings, [], f"Unexpected findings: {findings}")

    def test_invalid_extra_field_fails(self) -> None:
        payload = self._load_fixture("invalid-skill-v1-extra.json")
        findings = skill_common.validate_skill_manifest(payload)
        self.assertTrue(any("SCHEMA_EXTRA" in (f["code"]) for f in findings))

    def test_wrong_format_version_fails(self) -> None:
        payload = self._load_fixture("valid-skill-v1.json")
        payload = json.loads(json.dumps(payload))
        payload["format_version"] = "wrong"
        findings = skill_common.validate_skill_manifest(payload)
        self.assertTrue(any("SCHEMA_VERSION" in (f["code"]) for f in findings))

    def test_missing_title_fails(self) -> None:
        payload = self._load_fixture("valid-skill-v1.json")
        payload = json.loads(json.dumps(payload))
        del payload["title"]
        findings = skill_common.validate_skill_manifest(payload)
        self.assertTrue(any("SCHEMA_MISSING" in (f["code"]) for f in findings))

    def test_malformed_sha256_fails(self) -> None:
        payload = self._load_fixture("valid-skill-v1.json")
        payload = json.loads(json.dumps(payload))
        payload["skill"]["bundle_sha256"] = "too-short"
        findings = skill_common.validate_skill_manifest(payload)
        self.assertTrue(any(f["code"] == "SCHEMA_TYPE" and "bundle_sha256" in f.get("message", "")
                          for f in findings))

    def test_non_object_top_level_fails(self) -> None:
        findings = skill_common.validate_skill_manifest("not an object")
        self.assertTrue(len(findings) > 0)

    def test_wrong_enum_fails(self) -> None:
        payload = self._load_fixture("valid-skill-v1.json")
        payload = json.loads(json.dumps(payload))
        payload["human_review"]["status"] = "bogus"
        findings = skill_common.validate_skill_manifest(payload)
        self.assertTrue(any("SCHEMA_ENUM" in (f["code"]) for f in findings))

    def test_empty_findings_for_valid_has_empty_list(self) -> None:
        payload = self._load_fixture("valid-skill-v1.json")
        self.assertEqual(skill_common.validate_skill_manifest(payload), [])

    def test_findings_are_stable_sorted(self) -> None:
        payload = self._load_fixture("valid-skill-v1.json")
        payload = json.loads(json.dumps(payload))
        payload["format_version"] = "wrong"
        payload["skill"]["bundle_sha256"] = "bad"
        a = skill_common.validate_skill_manifest(payload)
        b = skill_common.validate_skill_manifest(payload)
        self.assertEqual(a, b)

