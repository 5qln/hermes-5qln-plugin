"""Tests for skills/5qln-skill-formation/scripts/verify_skill.py."""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "5qln-skill-formation" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import skill_common
import new_skill_manifest
import verify_skill


class SkillVerifierCoreTests(unittest.TestCase):
    """Tests for verify_skill core pipeline."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @property
    def minimal_fixture(self) -> Path:
        return ROOT / "tests" / "fixtures" / "skill-v1" / "valid-minimal"

    def _scaffold_and_write(self, suffix: str = "") -> Path:
        """Create a scaffolded manifest in temp dir."""
        dest = self.tmp / f"bundle{suffix}"
        shutil.copytree(str(self.minimal_fixture), str(dest), dirs_exist_ok=True)

        manifest = new_skill_manifest.build_manifest(
            dest, "provenance/conversion-manifest.json"
        )
        out = dest / "skill-formation-manifest.json"
        skill_common.atomic_write_json(out, manifest, overwrite=False)
        return out

    def test_verifier_reports_execution_success(self) -> None:
        manifest_path = self._scaffold_and_write()
        report = verify_skill.verify_skill(manifest_path)
        self.assertTrue(report["execution_success"])
        self.assertIn(report["structural_status"], ("passed", "failed"))

    def test_report_is_deterministic(self) -> None:
        manifest_path = self._scaffold_and_write()
        a = verify_skill.verify_skill(manifest_path)
        a.pop("conversion_report", None)
        a.pop("findings", None)

        manifest_path2 = self._scaffold_and_write("2")
        b = verify_skill.verify_skill(manifest_path2)
        b.pop("conversion_report", None)
        b.pop("findings", None)

        for key in ("format_version", "structural_status", "behavioral_status",
                     "human_review_status", "promotion_state", "promotion_ready"):
            self.assertEqual(a.get(key), b.get(key), f"mismatch on {key}")

    def test_report_has_no_valid_certified_living(self) -> None:
        manifest_path = self._scaffold_and_write()
        report = verify_skill.verify_skill(manifest_path)
        serialized = json.dumps(report)
        for forbidden in ('"valid"', '"certified"', '"living"'):
            self.assertNotIn(forbidden, serialized)

    def test_missing_manifest_raises(self) -> None:
        with self.assertRaises(skill_common.SkillContractError) as ctx:
            verify_skill.verify_skill(self.tmp / "nonexistent.json")
        self.assertEqual(ctx.exception.code, "FILE_MISSING")

    def test_malformed_json_returns_failure(self) -> None:
        bad = self.tmp / "bad.json"
        bad.write_text("not json")
        report = verify_skill.verify_skill(bad)
        self.assertFalse(report["execution_success"])

    def test_bundle_hash_mismatch_detected(self) -> None:
        manifest_path = self._scaffold_and_write()
        manifest = json.loads(manifest_path.read_text())
        manifest["skill"]["bundle_sha256"] = "0" * 64
        manifest_path.write_text(json.dumps(manifest))
        report = verify_skill.verify_skill(manifest_path)
        findings = report.get("findings", [])
        self.assertTrue(any("HASH_MISMATCH" in (f.get("code") or "") for f in findings))

    def test_frontmatter_parses_correctly(self) -> None:
        fm, body = verify_skill.parse_skill_frontmatter(
            "---\nname: test\ndescription: x\n---\n\n# Body\n"
        )
        self.assertEqual(fm["name"], "test")
        self.assertIn("# Body", body)

    def test_frontmatter_rejects_missing_delimiter(self) -> None:
        with self.assertRaises(skill_common.SkillContractError) as ctx:
            verify_skill.parse_skill_frontmatter("no frontmatter")
        self.assertEqual(ctx.exception.code, "FRONTMATTER_INVALID")

    def test_frontmatter_rejects_non_mapping(self) -> None:
        with self.assertRaises(skill_common.SkillContractError) as ctx:
            verify_skill.parse_skill_frontmatter("---\n- list\n- not mapping\n---\n\nbody")
        self.assertEqual(ctx.exception.code, "FRONTMATTER_INVALID")

    def test_skill_md_inspection_detects_name_mismatch(self) -> None:
        skill_md = self.tmp / "SKILL.md"
        skill_md.write_text("---\nname: wrong-name\ndescription: test\n---\n\nTrigger: when testing\nNon-trigger: otherwise\n")
        findings = verify_skill.inspect_skill_md(skill_md, "expected-name", "local-skill")
        self.assertTrue(any("SKILL_NAME_MISMATCH" in (f.get("code") or "") for f in findings))

    def test_skill_md_requires_trigger(self) -> None:
        skill_md = self.tmp / "SKILL.md"
        skill_md.write_text("---\nname: test\ndescription: test\n---\n\nJust body, no trigger.\n")
        findings = verify_skill.inspect_skill_md(skill_md, "test", "local-skill")
        self.assertTrue(any("TRIGGER_MISSING" in (f.get("code") or "") for f in findings))

    def test_syntax_check_python_valid(self) -> None:
        s = self.tmp / "valid.py"
        s.write_text("def foo():\n    return 42\n")
        findings = verify_skill._check_script_syntax(s)
        self.assertEqual(findings, [])

    def test_syntax_check_python_invalid(self) -> None:
        s = self.tmp / "invalid.py"
        s.write_text("def foo(\n")
        findings = verify_skill._check_script_syntax(s)
        self.assertTrue(any("SCRIPT_SYNTAX" in (f.get("code") or "") for f in findings))

    def test_syntax_check_json_valid(self) -> None:
        s = self.tmp / "valid.json"
        s.write_text('{"a": 1}')
        findings = verify_skill._check_script_syntax(s)
        self.assertEqual(findings, [])

    def test_conversion_compiler_refuses_stale_hash(self) -> None:
        manifest_path = self._scaffold_and_write()
        manifest = json.loads(manifest_path.read_text())
        manifest["provenance"]["conversion_manifest"]["sha256"] = "0" * 64
        manifest_path.write_text(json.dumps(manifest))
        report = verify_skill.verify_skill(manifest_path)
        findings = report.get("findings", [])
        self.assertTrue(any("CONVERSION_HASH" in (f.get("code") or "") for f in findings))

    def test_cli_structural_pass(self) -> None:
        manifest_path = self._scaffold_and_write()
        exit_code = verify_skill.main([
            "verify_skill.py", str(manifest_path),
        ])
        self.assertIn(exit_code, (0, 1))

    def test_cli_missing_file(self) -> None:
        exit_code = verify_skill.main([
            "verify_skill.py", str(self.tmp / "nope.json"),
        ])
        self.assertEqual(exit_code, 2)

    def test_cli_report_output(self) -> None:
        manifest_path = self._scaffold_and_write()
        out = self.tmp / "report.json"
        exit_code = verify_skill.main([
            "verify_skill.py", str(manifest_path),
            "--report", str(out),
        ])
        self.assertIn(exit_code, (0, 1))
        if exit_code != 2:
            self.assertTrue(out.exists())
            report = json.loads(out.read_text())
            self.assertEqual(report["format_version"], "skill-report-v1")


if __name__ == "__main__":
    unittest.main()



class SkillTraceabilityTests(unittest.TestCase):
    """Tests for requirement traceability (Task 10)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_empty_traces_passes_boundary_checks(self) -> None:
        findings = verify_skill._verify_requirement_traceability(
            {"requirement_traceability": [], "contract": {"behavioral_requirements": []},
             "behavioral_fixtures": []}, {}
        )
        self.assertEqual(findings, [])

    def test_source_requirement_needs_basis(self) -> None:
        manifest = {
            "requirement_traceability": [{
                "requirement_id": "REQ_TEST",
                "class": "source",
                "statement": "test",
                "basis_source_unit_ids": [],
                "basis_derived_insight_ids": [],
                "skill_sections": ["#overview"],
                "verifier_checks": ["CHECK_TEST"],
                "fixture_ids": [],
            }],
            "behavioral_fixtures": [],
            "contract": {"behavioral_requirements": []},
        }
        findings = verify_skill._verify_requirement_traceability(manifest, {})
        self.assertTrue(any("REQUIREMENT_BASIS" in (f.get("code") or "") for f in findings))

    def test_proposal_with_basis_is_invalid(self) -> None:
        manifest = {
            "requirement_traceability": [{
                "requirement_id": "REQ_PROP",
                "class": "proposal",
                "statement": "test",
                "basis_source_unit_ids": ["SRC-1"],
                "basis_derived_insight_ids": [],
                "skill_sections": ["#overview"],
                "verifier_checks": ["CHECK_TEST"],
                "fixture_ids": [],
            }],
            "behavioral_fixtures": [],
            "contract": {"behavioral_requirements": []},
        }
        findings = verify_skill._verify_requirement_traceability(manifest, {})
        self.assertTrue(any("SOURCE_CLASS_INVALID" in (f.get("code") or "") for f in findings))

    def test_section_anchor_not_found(self) -> None:
        md = self.tmp / "SKILL.md"
        md.write_text("# Real Heading\n\ncontent\n")
        manifest = {
            "requirement_traceability": [{
                "requirement_id": "REQ_X",
                "class": "source",
                "statement": "test",
                "basis_source_unit_ids": ["SRC-1"],
                "basis_derived_insight_ids": [],
                "skill_sections": ["#nonexistent-heading"],
                "verifier_checks": ["CHECK_TEST"],
                "fixture_ids": [],
            }],
        }
        findings = verify_skill._verify_section_anchors(manifest, md)
        self.assertTrue(any("SECTION_MISSING" in (f.get("code") or "") for f in findings))

    def test_return_not_question(self) -> None:
        manifest = {"requirement_traceability": []}
        conv = {
            "document_cell": {
                "V": {"return_question": "this is not a question", "return_status": "open"}
            },
            "cells": [],
        }
        findings = verify_skill._verify_requirement_traceability(manifest, conv)
        self.assertTrue(any("RETURN_NOT_QUESTION" in (f.get("code") or "") for f in findings))


class SkillHumanReviewTests(unittest.TestCase):
    """Tests for human review evidence (Task 15)."""

    def test_accepted_without_reviewer(self) -> None:
        manifest = {
            "human_review": {"status": "accepted", "reviewer": None, "evidence": []},
            "skill": {"bundle_sha256": "a" * 64},
        }
        findings = verify_skill._verify_human_review(manifest, None)
        self.assertTrue(any("HUMAN_EVIDENCE_MISSING" in (f.get("code") or "") for f in findings))

    def test_evidence_scope_mismatch(self) -> None:
        manifest = {
            "human_review": {
                "status": "accepted",
                "reviewer": "tester",
                "evidence": [{
                    "id": "EV_TEST",
                    "kind": "review_acceptance",
                    "statement": "approved",
                    "source": {"path": ".verification/evidence/ok.txt", "sha256": "b" * 64, "size_bytes": 1},
                    "location": "inline",
                    "scope_bundle_sha256": "0" * 64,
                    "scope_contract_sha256": "c" * 64,
                    "promotion_scope": "local",
                }],
            },
            "skill": {"bundle_sha256": "a" * 64},
        }
        findings = verify_skill._verify_human_review(manifest, None)
        self.assertTrue(any("HUMAN_EVIDENCE_SCOPE" in (f.get("code") or "") for f in findings))


class SkillPromotionTests(unittest.TestCase):
    """Tests for promotion inspection (Task 16)."""

    def test_promotion_without_accepted_review(self) -> None:
        manifest = {
            "promotion": {"target": "bundled-plugin", "requested_state": "promotion_requested", "authorization_evidence_ids": []},
            "human_review": {"status": "open", "reviewer": None, "evidence": []},
        }
        findings = verify_skill._inspect_promotion_readiness(manifest, None)
        self.assertTrue(any("PROMOTION_UNAUTHORIZED" in (f.get("code") or "") for f in findings))

    def test_local_skill_no_promotion_checks(self) -> None:
        manifest = {
            "promotion": {"target": "local-skill", "requested_state": "draft", "authorization_evidence_ids": []},
            "human_review": {"status": "open", "reviewer": None, "evidence": []},
        }
        findings = verify_skill._inspect_promotion_readiness(manifest, None)
        self.assertEqual(findings, [])


class SkillObservedRunTests(unittest.TestCase):
    """Tests for observed-run ingestion (Task 14)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_no_fixtures_returns_not_declared(self) -> None:
        manifest = {"behavioral_fixtures": []}
        status, findings = verify_skill._ingest_observed_runs(manifest, [])
        self.assertEqual(status, "not_declared")

    def test_fixtures_without_runs_returns_not_observed(self) -> None:
        manifest = {
            "behavioral_fixtures": [{"id": "FIX_1", "class": "positive_trigger", "spec": {"sha256": "a"*64}, "required": True}],
        }
        status, findings = verify_skill._ingest_observed_runs(manifest, [])
        self.assertEqual(status, "not_observed")

    def test_bundle_digest_mismatch(self) -> None:
        obs = self.tmp / "obs.json"
        obs.write_text(json.dumps({
            "bundle_sha256": "0" * 64,
            "fixture_sha256": "a" * 64,
            "results": [{"status": "pass"}],
        }))
        manifest = {
            "behavioral_fixtures": [{"id": "FIX_1", "class": "positive_trigger", "spec": {"sha256": "a"*64}, "required": True}],
            "skill": {"bundle_sha256": "f" * 64},
        }
        status, findings = verify_skill._ingest_observed_runs(manifest, [obs])
        self.assertTrue(any("OBSERVATION_HASH" in (f.get("code") or "") for f in findings))

