"""Repository policy and licensing invariants."""

from pathlib import Path
import json
import unittest


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


if __name__ == "__main__":
    unittest.main()

