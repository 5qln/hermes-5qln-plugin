"""End-to-end tests for the Hermes 5QLN plugin."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_plugin():
    """Load the repository root as a package, matching Hermes discovery."""
    name = "hermes_5qln_plugin"
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(
        name,
        ROOT / "__init__.py",
        submodule_search_locations=[str(ROOT)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load plugin package")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PLUGIN = load_plugin()
TOOLS = sys.modules["hermes_5qln_plugin.tools"]


def load_research_validator():
    """Load the bundled prompt validator without importing a hyphenated package."""
    name = "hermes_5qln_research_validator"
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    path = ROOT / "skills" / "5qln-deep-research" / "scripts" / "validate_research_prompt.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load research prompt validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


RESEARCH_VALIDATOR = load_research_validator()


def load_centrifuge():
    """Load the experimental centrifuge script for focused regression tests."""
    name = "hermes_5qln_centrifuge"
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    path = ROOT / "skills" / "5qln-centrifuge" / "scripts" / "centrifuge.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load centrifuge script")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CENTRIFUGE = load_centrifuge()


class FakeContext:
    def __init__(self) -> None:
        self.tools: dict[str, dict] = {}
        self.skills: dict[str, Path] = {}
        self.hooks: dict[str, list] = {}

    def register_tool(self, **kwargs) -> None:
        self.tools[kwargs["name"]] = kwargs

    def register_skill(self, name, path) -> None:
        self.skills[name] = Path(path)

    def register_hook(self, name, callback) -> None:
        self.hooks.setdefault(name, []).append(callback)


class PluginRegistrationTests(unittest.TestCase):
    def test_registers_tools_and_namespaced_skills(self) -> None:
        ctx = FakeContext()
        PLUGIN.register(ctx)
        self.assertEqual(
            set(ctx.tools),
            {
                "fiveqln_inventory_source",
                "fiveqln_create_manifest",
                "fiveqln_compile_manifest",
                "fiveqln_validate_research_prompt",
                "fiveqln_fractal_memory",
                "fiveqln_create_skill_manifest",
                "fiveqln_verify_skill",
            },
        )
        self.assertEqual(
            set(ctx.skills),
            {
                "5qln-agent",
                "5qln-cycle",
                "5qln-initiation",
                "symbolic-interpretation",
                "5qln-converter",
                "5qln-learning-aligner",
                "5qln-manifest-compilation",
                "5qln-deep-research",
                "5qln-centrifuge",
                "5qln-signature-engine",
                "5qln-skill-formation",
                "5qln-aimless-openness",
                "5qln-corruption-watcher",
                "5qln-self-evolution",
            },
        )
        for skill_path in ctx.skills.values():
            self.assertTrue(skill_path.is_file())
        for registered in ctx.tools.values():
            self.assertEqual(registered["toolset"], "5qln")
            self.assertTrue(callable(registered["handler"]))
        self.assertEqual(set(ctx.hooks), {"pre_llm_call"})
        self.assertEqual(len(ctx.hooks["pre_llm_call"]), 1)
        self.assertTrue(callable(ctx.hooks["pre_llm_call"][0]))

    def test_empty_centrifuge_does_not_report_false_contamination(self) -> None:
        card = CENTRIFUGE.signature_card([])
        self.assertIn("Integrity: NO DATA", card)
        self.assertNotIn("K contamination detected", card)

    def test_research_contract_uses_canonical_constitution(self) -> None:
        constitution = (
            ROOT / "skills" / "5qln-converter" / "references" / "constitution.md"
        ).read_text(encoding="utf-8")
        contract = (
            ROOT
            / "skills"
            / "5qln-deep-research"
            / "references"
            / "research-prompt-contract.md"
        ).read_text(encoding="utf-8")
        for exact in RESEARCH_VALIDATOR.REQUIRED_EXACT:
            self.assertIn(exact, constitution)
            self.assertIn(exact, contract)


class ToolWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.work = Path(self.tempdir.name)
        self.source = self.work / "source.md"
        self.source.write_text(
            "# Requirement\n\nREQ-1 [P0] The system MUST preserve the source.\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _inventory(self) -> Path:
        output = self.work / "source-inventory.json"
        result = json.loads(
            TOOLS.inventory_source(
                {"source_paths": [str(self.source)], "output_path": str(output)}
            )
        )
        self.assertTrue(result["success"], result)
        self.assertEqual(result["summary"]["source_count"], 1)
        self.assertGreaterEqual(result["summary"]["unit_count"], 2)
        return output

    def _manifest(self) -> Path:
        inventory = self._inventory()
        output = self.work / "conversion-manifest.json"
        result = json.loads(
            TOOLS.create_manifest(
                {
                    "inventory_path": str(inventory),
                    "output_path": str(output),
                    "title": "Test conversion",
                }
            )
        )
        self.assertTrue(result["success"], result)
        self.assertEqual(result["lens_checks"], 25)
        self.assertEqual(result["completion_status"], "open")
        return output

    def _complete_minimal_manifest(self, path: Path) -> None:
        payload = json.loads(path.read_text(encoding="utf-8"))
        source_ids = [unit["id"] for unit in payload["source"]["units"]]
        payload["cells"] = [
            {
                "address": "SS",
                "lens": "S",
                "parent": "S",
                "parent_equation": "S = ∞0 → ?",
                "parent_target": "X",
                "source_unit_ids": source_ids,
                "formation": {
                    "S": "The source remains open and is not promoted to X.",
                    "G": "The preservation identity persists across every source unit.",
                    "Q": "Human attestation remains absent and therefore open.",
                    "P": "Exact recovery provides more value than symbolic repetition.",
                    "V": "The local ledger returns as an open preservation question.",
                },
                "domain_items": ["REQ-1"],
                "evidence": ["Every source unit is mapped to this cell."],
                "guards": ["L2", "L4", "V∅"],
            }
        ]
        for item in payload["lens_audit"]:
            if item["address"] == "SS":
                item["status"] = "used"
                item["reason"] = "Primary Start-within-Start preservation cell."
            else:
                item["status"] = "not_applicable"
                item["reason"] = "No additional lens depth is required for this test artifact."
        for item in payload["traceability"]:
            item["primary_cell"] = "SS"
            item["output_refs"] = ["test-output"]
            item["preserved"] = True
            item["note"] = "Mapped without changing source text."
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def test_full_deterministic_workflow_passes(self) -> None:
        manifest = self._manifest()
        self._complete_minimal_manifest(manifest)
        report_path = self.work / "compiler-report.json"
        result = json.loads(
            TOOLS.compile_manifest(
                {"manifest_path": str(manifest), "report_path": str(report_path)}
            )
        )
        self.assertTrue(result["success"], result)
        self.assertTrue(result["valid"], result)
        self.assertEqual(result["report"]["status"], "passed")
        self.assertTrue(report_path.is_file())

    def test_constitutional_drift_fails(self) -> None:
        manifest = self._manifest()
        self._complete_minimal_manifest(manifest)
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        payload["constitution"]["law"] = "changed"
        manifest.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        result = json.loads(TOOLS.compile_manifest({"manifest_path": str(manifest)}))
        self.assertTrue(result["success"], result)
        self.assertFalse(result["valid"])
        codes = {finding["code"] for finding in result["report"]["errors"]}
        self.assertIn("CONSTITUTION_DRIFT", codes)

    def test_outputs_are_not_overwritten_without_consent(self) -> None:
        output = self.work / "existing.json"
        output.write_text("keep", encoding="utf-8")
        result = json.loads(
            TOOLS.inventory_source(
                {"source_paths": [str(self.source)], "output_path": str(output)}
            )
        )
        self.assertFalse(result["success"])
        self.assertIn("overwrite=true", result["error"])
        self.assertEqual(output.read_text(encoding="utf-8"), "keep")

    def test_fractal_memory_tool_excludes_evidence_bearing_calibration(self) -> None:
        seed_path = ROOT / "examples" / "parametric-fractal.example.json"
        home = self.work / "profile"
        exported_path = self.work / "portable.json"

        installed = json.loads(
            TOOLS.fractal_memory(
                {
                    "action": "install",
                    "seed_path": str(seed_path),
                    "hermes_home": str(home),
                }
            )
        )
        shown = json.loads(
            TOOLS.fractal_memory(
                {"action": "show", "hermes_home": str(home)}
            )
        )
        exported = json.loads(
            TOOLS.fractal_memory(
                {
                    "action": "export",
                    "hermes_home": str(home),
                    "output_path": str(exported_path),
                }
            )
        )

        self.assertTrue(installed["success"], installed)
        self.assertTrue(shown["success"], shown)
        self.assertTrue(exported["success"], exported)
        self.assertTrue(exported_path.is_file())
        schema = PLUGIN.schemas.FIVEQLN_FRACTAL_MEMORY["parameters"]
        self.assertNotIn("calibrate", schema["properties"]["action"]["enum"])
        self.assertNotIn("evidence", schema["properties"])

    def test_research_prompt_validation_passes(self) -> None:
        prompt = ROOT / "tests" / "fixtures" / "valid-research-prompt.md"
        report_path = self.work / "research-prompt-report.json"
        result = json.loads(
            TOOLS.validate_research_prompt(
                {"prompt_path": str(prompt), "report_path": str(report_path)}
            )
        )
        self.assertTrue(result["success"], result)
        self.assertTrue(result["valid"], result)
        self.assertEqual(result["report"]["status"], "passed")
        self.assertEqual(result["report"]["counts"], {"errors": 0, "warnings": 0})
        self.assertTrue(report_path.is_file())

    def test_invalid_research_prompt_is_a_review_state(self) -> None:
        result = json.loads(
            TOOLS.validate_research_prompt({"prompt_path": str(self.source)})
        )
        self.assertTrue(result["success"], result)
        self.assertFalse(result["valid"], result)
        self.assertEqual(result["report"]["status"], "failed")
        self.assertGreater(result["report"]["counts"]["errors"], 0)

    def test_research_report_is_not_overwritten_without_consent(self) -> None:
        prompt = ROOT / "tests" / "fixtures" / "valid-research-prompt.md"
        report_path = self.work / "existing-research-report.json"
        report_path.write_text("keep", encoding="utf-8")
        result = json.loads(
            TOOLS.validate_research_prompt(
                {"prompt_path": str(prompt), "report_path": str(report_path)}
            )
        )
        self.assertFalse(result["success"], result)
        self.assertIn("overwrite=true", result["error"])
        self.assertEqual(report_path.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
