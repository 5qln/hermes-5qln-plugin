"""Repository policy and licensing invariants."""

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRIBUTION = "Based on the 5QLN Constitutional Grammar by Amihai Loven (5qln.com)."


class RepositoryPolicyTests(unittest.TestCase):
    def test_license_set_and_attribution(self) -> None:
        required = [
            ROOT / "LICENSE",
            ROOT / "LICENSE-5QLN-KERNEL.md",
            ROOT / "LICENSE-APACHE-2.0.txt",
            ROOT / "NOTICE",
        ]
        for path in required:
            self.assertTrue(path.is_file(), path)
        self.assertIn(ATTRIBUTION, (ROOT / "NOTICE").read_text(encoding="utf-8"))
        self.assertIn("Apache License", (ROOT / "LICENSE-APACHE-2.0.txt").read_text(encoding="utf-8"))
        self.assertIn("Specific Extension Exception", (ROOT / "LICENSE-5QLN-KERNEL.md").read_text(encoding="utf-8"))

    def test_code_owner_and_protection_policy(self) -> None:
        codeowners = (ROOT / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
        self.assertIn("* @5qln", codeowners)
        policy = json.loads((ROOT / ".github" / "branch-protection.json").read_text(encoding="utf-8"))
        reviews = policy["required_pull_request_reviews"]
        self.assertTrue(reviews["require_code_owner_reviews"])
        self.assertEqual(reviews["required_approving_review_count"], 1)
        self.assertTrue(reviews["require_last_push_approval"])
        self.assertFalse(policy["allow_force_pushes"])
        self.assertFalse(policy["allow_deletions"])

    def test_manifest_version_and_registered_surface_are_documented(self) -> None:
        manifest = (ROOT / "plugin.yaml").read_text(encoding="utf-8")
        version_line = next(line for line in manifest.splitlines() if line.startswith("version:"))
        version = version_line.split(":", 1)[1].strip()
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        formation_skill = (
            ROOT / "skills" / "5qln-skill-formation" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn(f"## {version} -", changelog)
        self.assertIn(f"version: {version}", formation_skill)
        self.assertIn("provides_hooks:\n  - pre_llm_call", manifest)
        for tool in (
            "fiveqln_inventory_source",
            "fiveqln_create_manifest",
            "fiveqln_compile_manifest",
            "fiveqln_validate_research_prompt",
            "fiveqln_fractal_memory",
            "fiveqln_create_skill_manifest",
            "fiveqln_verify_skill",
        ):
            self.assertIn(f"  - {tool}", manifest)

    def test_runtime_and_optional_dependencies_are_declared(self) -> None:
        runtime = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        development = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8")
        optional = (ROOT / "requirements-optional.txt").read_text(encoding="utf-8")
        workflow = (ROOT / ".github" / "workflows" / "test.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("PyYAML", runtime)
        self.assertIn("jsonschema", development)
        self.assertIn("-r requirements.txt", development)
        self.assertIn("python-docx", optional)
        self.assertIn("pypdf", optional)
        self.assertIn("pip install -r requirements-dev.txt", workflow)

    def test_current_documentation_matches_registered_surface(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        development = (ROOT / "docs" / "DEVELOPMENT.md").read_text(encoding="utf-8")
        architecture = (ROOT / "docs" / "ARCHITECTURE.md").read_text(encoding="utf-8")
        publishing = (ROOT / "docs" / "PUBLISHING.md").read_text(encoding="utf-8")
        usage = (ROOT / "docs" / "USAGE.md").read_text(encoding="utf-8")
        parametric = (ROOT / "docs" / "PARAMETRIC_FRACTAL.md").read_text(encoding="utf-8")
        agent = (ROOT / "skills" / "5qln-agent" / "SKILL.md").read_text(encoding="utf-8")
        genesis = (
            ROOT
            / "skills"
            / "5qln-manifest-compilation"
            / "references"
            / "genesis-pattern.md"
        ).read_text(encoding="utf-8")
        aligner_reference = (
            ROOT / "skills" / "symbolic-interpretation" / "references" / "learning-aligner.md"
        ).read_text(encoding="utf-8")
        symbolic_skill = (
            ROOT / "skills" / "symbolic-interpretation" / "SKILL.md"
        ).read_text(encoding="utf-8")
        centrifuge_skill = (
            ROOT / "skills" / "5qln-centrifuge" / "SKILL.md"
        ).read_text(encoding="utf-8")
        design_history = (ROOT / "design" / "SKILL_V1_ARCHITECTURE.md").read_text(
            encoding="utf-8"
        )

        for document in (development, architecture, publishing):
            self.assertRegex(document, r"seven(?: JSON-schema)? tools")
            self.assertRegex(document, r"fourteen(?: namespaced)? skills")
        self.assertIn("requirements-dev.txt", development)
        self.assertNotIn("requires no third-party Python packages", development)
        self.assertNotIn("Three operations, all deterministic", readme)
        self.assertNotIn("agents/openai.yaml", architecture)
        self.assertNotIn("signature tools) can detect drift", agent)
        source_rows = (
            "| S | `emergent` | `mechanical` |",
            "| G | `revealed` | `imposed` |",
            "| Q | `lived` | `logical` |",
            "| P | `felt` | `calculated` |",
            "| V | `opened` | `closed` |",
        )
        for document in (usage, parametric):
            for row in source_rows:
                self.assertIn(row, document)
        self.assertIn("STATUS: HISTORICAL PROPOSAL — NOT SHIPPED", genesis)
        self.assertNotIn("python3 scripts/phase_log.py", aligner_reference)
        self.assertNotIn("phase_log.py append", aligner_reference)
        self.assertIn(
            "skills/5qln-learning-aligner/scripts/phase_log.py", aligner_reference
        )
        self.assertIn("$PHASE_LOG_PATH", centrifuge_skill)
        self.assertIn("$HERMES_HOME/5qln/phase_log.json", centrifuge_skill)
        self.assertNotIn("zero dependencies", symbolic_skill)
        self.assertIn("scripts/decoding.py", symbolic_skill)
        self.assertIn(
            "skills/5qln-learning-aligner/scripts/phase_log.py", symbolic_skill
        )
        self.assertIn("are superseded by the 0.7.0 runtime", design_history)

    def test_deep_research_import_checksums_match_provenance(self) -> None:
        provenance = (ROOT / "docs" / "PROVENANCE.md").read_text(encoding="utf-8")
        skill_root = ROOT / "skills" / "5qln-deep-research"
        for relative in (
            "SKILL.md",
            "references/research-prompt-contract.md",
            "scripts/validate_research_prompt.py",
        ):
            digest = hashlib.sha256((skill_root / relative).read_bytes()).hexdigest()
            self.assertIn(f"| `{relative}` | `{digest}` |", provenance)


if __name__ == "__main__":
    unittest.main()
