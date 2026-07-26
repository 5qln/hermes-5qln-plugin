"""Behavior tests for the portable 5QLN parametric-fractal memory."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import multiprocessing
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "fractal_memory.py"
CODEX_SHA256 = "feaa46b4147d4e023cdd3fd59c051d063e8ec654ee7b38a481dcd5e4c781859b"


def load_module():
    spec = importlib.util.spec_from_file_location("fiveqln_fractal_memory", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load fractal memory module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def seal_seed(seed: dict) -> dict:
    payload = {key: value for key, value in seed.items() if key != "state_sha256"}
    seed["state_sha256"] = hashlib.sha256(
        json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()
    return seed


def calibrate_worker(home: str, start_barrier) -> None:
    start_barrier.wait(timeout=10)
    memory = load_module()
    memory.calibrate_installed(
        Path(home),
        phase="Q",
        source_tag="lived",
        evidence="synthetic explicit attestation",
    )


def valid_seed() -> dict:
    return seal_seed(
        {
            "format": "5qln-parametric-fractal",
            "version": "1.0",
            "codex_sha256": CODEX_SHA256,
            "profile": {
                "memory_function": "session-orchestrator",
                "resonance_criterion": "thoughtless-emergence",
                "k_container": "5qln-operating-language",
                "directionality": "hold-not-direct",
                "attestation": "human-explicit-only",
            },
            "calibration": {
                "S": 0.58,
                "G": 0.93,
                "Q": 0.56,
                "P": 0.91,
                "V": 0.88,
            },
            "state_sha256": "0" * 64,
        }
    )


class InstallTests(unittest.TestCase):
    def test_install_copies_valid_seed_and_protects_existing_state(self) -> None:
        memory = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "portable.json"
            source.write_text(json.dumps(valid_seed()), encoding="utf-8")
            home = root / "fresh-hermes"

            result = memory.install_seed(source, home)

            installed = home / "5qln" / "parametric-fractal.json"
            self.assertEqual(result["state_path"], str(installed))
            self.assertEqual(json.loads(installed.read_text(encoding="utf-8")), valid_seed())
            with self.assertRaisesRegex(FileExistsError, "replace"):
                memory.install_seed(source, home)

    def test_checked_in_example_seed_is_valid(self) -> None:
        memory = load_module()
        seed = json.loads(
            (ROOT / "examples" / "parametric-fractal.example.json").read_text(
                encoding="utf-8"
            )
        )
        memory.validate_seed(seed)
        self.assertRegex(seed["state_sha256"], r"^[0-9a-f]{64}$")

    def test_validation_rejects_wrong_seal(self) -> None:
        memory = load_module()
        wrong_seal = valid_seed()
        wrong_seal["codex_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "constitutional seal"):
            memory.validate_seed(wrong_seal)

    def test_validation_rejects_unknown_top_level_field(self) -> None:
        seed = valid_seed()
        seed["notes"] = "discarded conversation"
        with self.assertRaisesRegex(ValueError, "top-level keys"):
            load_module().validate_seed(seed)

    def test_validation_rejects_free_form_profile_value(self) -> None:
        seed = valid_seed()
        seed["profile"]["directionality"] = "a remembered personal instruction"
        with self.assertRaisesRegex(ValueError, "profile"):
            load_module().validate_seed(seed)

    def test_validation_rejects_out_of_range_and_boolean_numbers(self) -> None:
        memory = load_module()
        for bad in (-0.01, 1.01, True):
            with self.subTest(value=bad):
                seed = valid_seed()
                seed["calibration"]["S"] = bad
                with self.assertRaises(ValueError):
                    memory.validate_seed(seed)

    def test_validation_rejects_noncanonical_precision_and_checksum(self) -> None:
        memory = load_module()
        mutations = (
            ("precision", lambda seed: seed["calibration"].__setitem__("S", 0.123456)),
            ("state_sha256", lambda seed: seed.__setitem__("state_sha256", "ABC")),
        )
        for label, mutate in mutations:
            with self.subTest(field=label):
                seed = valid_seed()
                mutate(seed)
                with self.assertRaises(ValueError):
                    memory.validate_seed(seed)

    def test_validation_rejects_mutation_with_unchanged_checksum(self) -> None:
        memory = load_module()
        tampered = valid_seed()
        tampered["calibration"]["Q"] = 0.123
        with self.assertRaisesRegex(ValueError, "state_sha256 does not match"):
            memory.validate_seed(tampered)

    def test_validation_rejects_seed_over_4096_bytes(self) -> None:
        seed = valid_seed()
        seed["padding"] = "x" * 5000
        with self.assertRaisesRegex(ValueError, "4096"):
            load_module().validate_seed(seed)


class OrchestrationContextTests(unittest.TestCase):
    def test_pre_llm_hook_loads_compact_k_context_from_active_profile(self) -> None:
        memory = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            state_path = home / "5qln" / "parametric-fractal.json"
            state_path.parent.mkdir(parents=True)
            state_path.write_text(json.dumps(valid_seed()), encoding="utf-8")

            with mock.patch.dict(os.environ, {"HERMES_HOME": str(home)}):
                result = memory.pre_llm_context(session_id="fresh", user_message="new signal")

            self.assertIsInstance(result, dict)
            context = result["context"]
            self.assertIn("K-CONTEXT", context)
            self.assertIn("Memory function: session orchestrator, not recall.", context)
            self.assertIn("Resonance criterion: quality of thoughtless emergence", context)
            self.assertIn("K cannot attest resonance", context)
            self.assertIn("A = K", context)
            self.assertIn("H and K remain distinct", context)
            self.assertIn("S=0.580", context)
            self.assertNotIn("identity", context)
            self.assertNotIn("Aim:", context)

    def test_pre_llm_hook_is_silent_when_no_seed_is_installed(self) -> None:
        memory = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {"HERMES_HOME": tmp}):
                self.assertIsNone(memory.pre_llm_context(session_id="fresh"))


class CalibrationTests(unittest.TestCase):
    def test_calibration_updates_bounded_state_and_discards_attestation_text(self) -> None:
        memory = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "profile"
            source = Path(tmp) / "seed.json"
            source.write_text(json.dumps(valid_seed()), encoding="utf-8")
            memory.install_seed(source, home)

            result = memory.calibrate_installed(
                home,
                phase="Q",
                source_tag="lived",
                evidence="synthetic explicit attestation",
            )
            updated = memory.load_installed_seed(home)

            self.assertEqual(result["status"], "calibrated")
            expected = round(0.56 + 0.1 * (1.0 - 0.56), 3)
            self.assertEqual(updated["calibration"]["Q"], expected)
            self.assertNotEqual(updated["state_sha256"], "0" * 64)
            serialized = json.dumps(updated)
            self.assertNotIn("synthetic explicit attestation", serialized)
            self.assertNotIn("events", updated)
            self.assertEqual(set(updated), set(valid_seed()))

    def test_checksum_is_independent_of_attestation_wording(self) -> None:
        memory = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home_a = root / "a"
            home_b = root / "b"
            source = root / "seed.json"
            source.write_text(json.dumps(valid_seed()), encoding="utf-8")
            memory.install_seed(source, home_a)
            memory.install_seed(source, home_b)

            a = memory.calibrate_installed(
                home_a, phase="Q", source_tag="lived", evidence="synthetic explicit attestation"
            )
            b = memory.calibrate_installed(
                home_b,
                phase="Q",
                source_tag="lived",
                evidence="different explicit words",
            )

            self.assertEqual(a["state_sha256"], b["state_sha256"])
            self.assertNotIn(
                "synthetic explicit attestation", json.dumps(memory.load_installed_seed(home_a))
            )

    def test_calibration_requires_explicit_evidence_and_canonical_source_tag(self) -> None:
        memory = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "profile"
            source = Path(tmp) / "seed.json"
            source.write_text(json.dumps(valid_seed()), encoding="utf-8")
            memory.install_seed(source, home)

            with self.assertRaisesRegex(ValueError, "explicit human-attestation evidence"):
                memory.calibrate_installed(home, phase="Q", source_tag="lived", evidence="")
            with self.assertRaisesRegex(ValueError, "source_tag"):
                memory.calibrate_installed(
                    home,
                    phase="Q",
                    source_tag="the model thinks it resonates",
                    evidence="yes",
                )

    def test_concurrent_calibrations_do_not_lose_updates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "profile"
            source = Path(tmp) / "seed.json"
            source.write_text(json.dumps(valid_seed()), encoding="utf-8")
            load_module().install_seed(source, home)

            context = multiprocessing.get_context("spawn")
            start_barrier = context.Barrier(7)
            workers = [
                context.Process(
                    target=calibrate_worker, args=(str(home), start_barrier)
                )
                for _ in range(6)
            ]
            for worker in workers:
                worker.start()
            start_barrier.wait(timeout=10)
            for worker in workers:
                worker.join(timeout=15)
                self.assertEqual(worker.exitcode, 0)

            updated = load_module().load_installed_seed(home)
            expected = 0.56
            for _ in range(6):
                expected = round(expected + 0.1 * (1.0 - expected), 3)
            self.assertEqual(updated["calibration"]["Q"], expected)


class CliTests(unittest.TestCase):
    def _run(
        self, *args: str, input_text: str | None = None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(MODULE_PATH), *args],
            check=False,
            capture_output=True,
            text=True,
            input=input_text,
        )

    def test_cli_installs_and_shows_seed_in_fresh_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "profile"
            source = root / "seed.json"
            source.write_text(json.dumps(valid_seed()), encoding="utf-8")

            installed = self._run("install", str(source), "--hermes-home", str(home))
            shown = self._run("show", "--hermes-home", str(home))

            self.assertEqual(installed.returncode, 0, installed.stderr)
            self.assertEqual(json.loads(installed.stdout)["status"], "installed")
            self.assertEqual(shown.returncode, 0, shown.stderr)
            self.assertEqual(json.loads(shown.stdout)["format"], "5qln-parametric-fractal")

    def test_cli_calibrates_and_exports_without_attestation_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "profile"
            source = root / "seed.json"
            exported = root / "portable-export.json"
            source.write_text(json.dumps(valid_seed()), encoding="utf-8")
            self.assertEqual(
                self._run("install", str(source), "--hermes-home", str(home)).returncode,
                0,
            )

            calibrated = self._run(
                "calibrate",
                "--hermes-home",
                str(home),
                "--phase",
                "Q",
                "--source-tag",
                "lived",
                "--evidence-stdin",
                input_text="synthetic explicit attestation\n",
            )
            exported_result = self._run(
                "export", str(exported), "--hermes-home", str(home)
            )

            self.assertEqual(calibrated.returncode, 0, calibrated.stderr)
            self.assertEqual(json.loads(calibrated.stdout)["status"], "calibrated")
            self.assertEqual(exported_result.returncode, 0, exported_result.stderr)
            exported_text = exported.read_text(encoding="utf-8")
            self.assertNotIn("synthetic explicit attestation", exported_text)
            self.assertEqual(json.loads(exported_text)["calibration"]["Q"], 0.604)


if __name__ == "__main__":
    unittest.main()
