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
        self.assertIn(f"## {version} -", changelog)
        for tool in (
            "fiveqln_inventory_source",
            "fiveqln_create_manifest",
            "fiveqln_compile_manifest",
            "fiveqln_validate_research_prompt",
        ):
            self.assertIn(f"  - {tool}", manifest)

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
