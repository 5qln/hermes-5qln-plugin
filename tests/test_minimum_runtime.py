"""Behavior tests for the self-contained minimum 5QLN cycle runtime."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
XYZAB = ROOT / "skills" / "symbolic-interpretation" / "scripts" / "xyzab_state.py"
DECODING = XYZAB.with_name("decoding.py")
PHASE_LOG = (
    ROOT / "skills" / "5qln-learning-aligner" / "scripts" / "phase_log.py"
)
CENTRIFUGE = ROOT / "skills" / "5qln-centrifuge" / "scripts" / "centrifuge.py"
PARAMETRIC_CENTRIFUGE = CENTRIFUGE.with_name("centrifuge_parametric.py")


def load_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class BundledDecodingTests(unittest.TestCase):
    def test_decoder_is_bundled_next_to_xyzab(self) -> None:
        self.assertTrue(DECODING.is_file())

    def test_start_gate_rejects_statement_instead_of_question(self) -> None:
        decoding = load_script("fiveqln_test_decoding", DECODING)
        violations, _warnings = decoding.check_fields(
            "S", {"X": "This is a manufactured statement."}
        )
        self.assertIn("X must be a question ending with ?", violations)

    def test_start_gate_accepts_question(self) -> None:
        decoding = load_script("fiveqln_test_decoding_valid", DECODING)
        violations, warnings = decoding.check_fields(
            "S", {"X": "What is trying to emerge?"}
        )
        self.assertEqual(violations, [])
        self.assertEqual(warnings, [])

    def test_none_and_forced_alignment_require_z_to_be_omitted(self) -> None:
        decoding = load_script("fiveqln_test_decoding_forbidden_z", DECODING)
        for alignment in ("none", "forced"):
            for z_value in ("", "manufactured overlap"):
                with self.subTest(alignment=alignment, z_value=z_value):
                    violations, _warnings = decoding.check_fields(
                        "Q",
                        {
                            "PHI": "the work's seeking",
                            "OMEGA": "the wider field",
                            "ALIGNMENT": alignment,
                            "EXTENT": "0",
                            "Z": z_value,
                        },
                    )
                    self.assertIn(
                        "Z must be omitted when ALIGNMENT is none or forced",
                        violations,
                    )

    def test_return_comparison_normalizes_unicode_spacing_and_punctuation(self) -> None:
        decoding = load_script("fiveqln_test_decoding_normalization", DECODING)
        cases = (
            ("What is trying to emerge?   ", "WHAT   IS TRYING TO EMERGE？"),
            ("What—exactly is trying?", "What, exactly is trying？"),
            ("What’s trying to emerge?", "What's trying to emerge?"),
            ("What's trying to emerge?", "Whats trying to emerge?"),
            ("What is trying to emerge?", "What\u200bis trying to emerge?"),
            ("What is trying to emerge?", "What\u00adis trying to emerge?"),
            ("What is trying to emerge?", "What\u2060is trying to emerge?"),
        )
        for opening, candidate in cases:
            with self.subTest(opening=opening, candidate=candidate):
                fields = {
                    "L": "result",
                    "B2": "artifact",
                    "INF0P": candidate,
                    "LIVENESS": "8",
                }
                violations, _warnings = decoding.check_fields("V", fields, opening)
                self.assertIn(
                    "INF0P must not repeat the cycle opening question", violations
                )


class XyzabStrictDecodingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.state_dir = Path(self.tempdir.name) / "xyzab"
        self.wiki_dir = Path(self.tempdir.name) / "wiki"
        self.env = os.environ.copy()
        self.env["XYZAB_STATE_DIR"] = str(self.state_dir)
        self.env["QLN_WIKI"] = str(self.wiki_dir)
        self.env.pop("PHASE_LOG_PATH", None)
        self.env["PYTHONDONTWRITEBYTECODE"] = "1"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def run_xyzab(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(XYZAB), *args],
            text=True,
            capture_output=True,
            env=self.env,
            check=False,
        )

    def test_malformed_start_does_not_open_gate(self) -> None:
        result = self.run_xyzab("open", "x", "-c", "This is not a question.")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])

        status = self.run_xyzab("gate")
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertEqual(json.loads(status.stdout)["gate"], "x")

    def test_start_rejects_footer_shaped_or_multiline_bare_content(self) -> None:
        cases = (
            ("EXTRA: accepted as a question?", "unknown field EXTRA"),
            ("x: disguised lowercase footer?", "field names must be uppercase"),
            ("x∶ disguised lowercase-ratio footer?", "non-footer line"),
            ("Χ∶ disguised Greek-X footer?", "non-footer line"),
            ("εχτρα∶ disguised Greek footer?", "non-footer line"),
            ("Х: disguised Cyrillic-X footer?", "unknown field Х"),
            ("X\u200b: disguised zero-width key?", "unknown field"),
            ("X\u00ad: disguised soft-hyphen key?", "unknown field"),
            ("X\u2060: disguised word-joiner key?", "unknown field"),
            ("\u200bX: disguised leading-zero-width key?", "unknown field"),
            ("\u200b X: disguised leading-control-space key?", "unknown field"),
            ("X \u200b: disguised post-space zero-width key?", "unknown field"),
            ("X \u2060 ∶ disguised spaced word-joiner ratio key?", "non-footer line"),
            ("AL\U000e003aPHA∶ disguised tag-colon key?", "non-footer line"),
            ("AL\u065ePHA∶ disguised combining-two-dots key?", "non-footer line"),
            ("X： disguised compatibility footer?", "non-footer line"),
            ("X﹕ disguised small-colon footer?", "non-footer line"),
            ("X︓ disguised vertical-colon footer?", "non-footer line"),
            ("X∶ disguised ratio footer?", "non-footer line"),
            ("X꞉ disguised modifier-colon footer?", "non-footer line"),
            ("Xː disguised triangular-colon footer?", "non-footer line"),
            ("X⁚ disguised two-dot footer?", "non-footer line"),
            ("X։ disguised Armenian-stop footer?", "non-footer line"),
            ("What is this? What is that?", "X must be a question ending with ?"),
            ("X: What is this? What is that?", "X must be a question ending with ?"),
            ("This is free-form prose.\nWhat is trying to emerge?", "non-footer line"),
        )
        for content, message in cases:
            with self.subTest(content=content, message=message):
                result = self.run_xyzab("open", "x", "-c", content)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stdout)
                self.assertEqual(json.loads(self.run_xyzab("gate").stdout)["gate"], "x")

    def test_override_cannot_bypass_structural_violations(self) -> None:
        result = self.run_xyzab(
            "open",
            "x",
            "-c",
            "This is not a question.",
            "--override",
            "human requested",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("X must be a question", result.stdout)
        self.assertEqual(json.loads(self.run_xyzab("gate").stdout)["gate"], "x")

    def test_valid_start_opens_gate_with_bundled_decoder(self) -> None:
        result = self.run_xyzab("open", "x", "-c", "What is trying to emerge?")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["check"], "passed")
        self.assertEqual(payload["next"], "y")

    def test_start_accepts_non_footer_semicolon_question(self) -> None:
        result = self.run_xyzab("open", "x", "-c", "What; is trying to emerge?")
        self.assertEqual(result.returncode, 0, result.stdout or result.stderr)
        self.assertEqual(json.loads(result.stdout)["next"], "y")

    def test_gate_requires_content(self) -> None:
        result = self.run_xyzab("open", "x")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("content is required", result.stderr)

    def test_growth_gate_requires_canonical_footer(self) -> None:
        opened = self.run_xyzab("open", "x", "-c", "What is trying to emerge?")
        self.assertEqual(opened.returncode, 0, opened.stderr)

        bare = self.run_xyzab("open", "y", "-c", "A pattern")
        self.assertNotEqual(bare.returncode, 0)
        self.assertIn("missing SEEKS", bare.stdout)

        complete = self.run_xyzab(
            "open",
            "y",
            "-c",
            "ALPHA: A pattern\nSEEKS: expression across scales",
        )
        self.assertEqual(complete.returncode, 0, complete.stderr)

    def test_growth_footer_rejects_noncanonical_lines(self) -> None:
        opened = self.run_xyzab("open", "x", "-c", "What is trying to emerge?")
        self.assertEqual(opened.returncode, 0, opened.stderr)

        cases = (
            (
                "ALPHA: first\nALPHA: replacement\nSEEKS: expression",
                "duplicate field ALPHA",
            ),
            (
                "ALPHA: pattern\nSEEKS: expression\nEXTRA: not canonical",
                "unknown field EXTRA",
            ),
            (
                "ALPHA: pattern\nfree-form prose\nSEEKS: expression",
                "non-footer line",
            ),
        )
        for content, message in cases:
            with self.subTest(message=message):
                result = self.run_xyzab("open", "y", "-c", content)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stdout)
                self.assertEqual(json.loads(self.run_xyzab("gate").stdout)["gate"], "y")

    def test_quality_gate_rejects_z_when_alignment_is_forced(self) -> None:
        start = self.run_xyzab("open", "x", "-c", "What is trying to emerge?")
        self.assertEqual(start.returncode, 0, start.stderr)
        growth = self.run_xyzab(
            "open",
            "y",
            "-c",
            "ALPHA: A pattern that holds\nSEEKS: honest relation",
        )
        self.assertEqual(growth.returncode, 0, growth.stderr)

        forced_z = self.run_xyzab(
            "open",
            "z",
            "-c",
            "PHI: the work seeks adoption\nOMEGA: the field resists it\n"
            "ALIGNMENT: forced\nEXTENT: 0\nZ: total acceptance",
        )
        self.assertNotEqual(forced_z.returncode, 0)
        self.assertIn("Z must be omitted", forced_z.stdout)
        self.assertEqual(json.loads(self.run_xyzab("gate").stdout)["gate"], "z")

        empty_z = self.run_xyzab(
            "open",
            "z",
            "-c",
            "PHI: adoption\nOMEGA: resistance\n"
            "ALIGNMENT: forced\nEXTENT: 0\nZ:",
        )
        self.assertNotEqual(empty_z.returncode, 0)
        self.assertIn("Z must be omitted", empty_z.stdout)
        self.assertEqual(json.loads(self.run_xyzab("gate").stdout)["gate"], "z")

    def test_value_gate_requires_artifact_and_return_question(self) -> None:
        deposits = [
            ("x", "What is trying to emerge?"),
            ("y", "ALPHA: A pattern that holds across scales\nSEEKS: clearer expression"),
            (
                "z",
                "PHI: the work seeks clarity\nOMEGA: transparent systems\n"
                "ALIGNMENT: partial\nEXTENT: 6\nZ: explicit runtime ownership",
            ),
            (
                "a",
                "VALUE_MAX: one reproducible engine\nENERGY: reuse bundled code\n"
                "A: make dependencies explicit",
            ),
        ]
        for gate, content in deposits:
            result = self.run_xyzab("open", gate, "-c", content)
            self.assertEqual(result.returncode, 0, result.stderr)

        bare_artifact = self.run_xyzab("open", "b", "-c", "A finished artifact")
        self.assertNotEqual(bare_artifact.returncode, 0)
        self.assertIn("missing INF0P", bare_artifact.stdout)

        multiple_returns = self.run_xyzab(
            "open",
            "b",
            "-c",
            "L: The local result\nB2: The finished artifact\n"
            "INF0P: What opens? What follows?\nLIVENESS: 7",
        )
        self.assertNotEqual(multiple_returns.returncode, 0)
        self.assertIn(
            "INF0P must be a return question ending with ?", multiple_returns.stdout
        )

        footer = "\n".join(
            [
                "L: The local result",
                "B2: The finished artifact",
                "INF0P: What does this open next?",
                "LIVENESS: 7",
            ]
        )
        complete = self.run_xyzab("open", "b", "-c", footer)
        self.assertEqual(complete.returncode, 0, complete.stderr)
        self.assertTrue(json.loads(complete.stdout)["ok"])

    def test_value_gate_rejects_return_that_repeats_canonical_start(self) -> None:
        deposits = [
            ("x", "X: What is trying to emerge?   "),
            ("y", "ALPHA: A pattern that holds\nSEEKS: clearer expression"),
            (
                "z",
                "PHI: the work seeks clarity\nOMEGA: transparent systems\n"
                "ALIGNMENT: natural\nEXTENT: 8\nZ: explicit ownership",
            ),
            (
                "a",
                "VALUE_MAX: a reproducible engine\nENERGY: bundled code\n"
                "A: preserve one authority",
            ),
        ]
        for gate, content in deposits:
            result = self.run_xyzab("open", gate, "-c", content)
            self.assertEqual(result.returncode, 0, result.stderr)

        repeated_return = self.run_xyzab(
            "open",
            "b",
            "-c",
            "L: The local result\nB2: The artifact\n"
            "INF0P: What is trying to emerge?\nLIVENESS: 8",
        )
        self.assertNotEqual(repeated_return.returncode, 0)
        self.assertIn("must not repeat", repeated_return.stdout)
        self.assertEqual(json.loads(self.run_xyzab("gate").stdout)["gate"], "b")

        normalized_repeat = self.run_xyzab(
            "open",
            "b",
            "-c",
            "L: The local result\nB2: The artifact\n"
            "INF0P: WHAT   IS TRYING TO EMERGE ?\nLIVENESS: 8",
        )
        self.assertNotEqual(normalized_repeat.returncode, 0)
        self.assertIn("must not repeat", normalized_repeat.stdout)
        self.assertEqual(json.loads(self.run_xyzab("gate").stdout)["gate"], "b")

    def test_opening_gate_appends_source_record_to_phase_log(self) -> None:
        result = self.run_xyzab(
            "open",
            "x",
            "-c",
            "What is trying to emerge?",
            "--source-tag",
            "emergent",
            "--signal",
            "human validated",
            "--session-id",
            "session-test",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        log_path = self.wiki_dir / "state" / "phase_log.json"
        payload = json.loads(log_path.read_text(encoding="utf-8"))
        self.assertEqual(len(payload["entries"]), 1)
        entry = payload["entries"][0]
        self.assertEqual(entry["phase"], "S")
        self.assertEqual(entry["gate"], "x")
        self.assertEqual(entry["source"], "emergent")
        self.assertEqual(entry["signal"], "human validated")
        self.assertEqual(entry["session"], "session-test")

    def test_state_save_failure_rolls_back_phase_log_append(self) -> None:
        previous_state_dir = os.environ.get("XYZAB_STATE_DIR")
        previous_wiki = os.environ.get("QLN_WIKI")
        previous_phase_log = os.environ.pop("PHASE_LOG_PATH", None)
        os.environ["XYZAB_STATE_DIR"] = str(self.state_dir)
        os.environ["QLN_WIKI"] = str(self.wiki_dir)
        try:
            xyzab = load_script("fiveqln_test_xyzab_transaction", XYZAB)
            state = xyzab.fresh_state()
            log_path = self.wiki_dir / "state" / "phase_log.json"

            with mock.patch.object(xyzab, "save", side_effect=OSError("disk full")):
                with self.assertRaisesRegex(OSError, "disk full"):
                    xyzab.cmd_open(
                        state,
                        "x",
                        "What remains consistent when state persistence fails?",
                        source_tag="emergent",
                        signal="simulated state write failure",
                        session_id="transaction-test",
                    )

            self.assertFalse(log_path.exists())
            self.assertEqual(xyzab.next_pending(xyzab.load()), "x")
        finally:
            if previous_state_dir is None:
                os.environ.pop("XYZAB_STATE_DIR", None)
            else:
                os.environ["XYZAB_STATE_DIR"] = previous_state_dir
            if previous_wiki is None:
                os.environ.pop("QLN_WIKI", None)
            else:
                os.environ["QLN_WIKI"] = previous_wiki
            if previous_phase_log is not None:
                os.environ["PHASE_LOG_PATH"] = previous_phase_log

    def test_state_replace_failure_preserves_previous_state_file(self) -> None:
        previous_state_dir = os.environ.get("XYZAB_STATE_DIR")
        os.environ["XYZAB_STATE_DIR"] = str(self.state_dir)
        try:
            xyzab = load_script("fiveqln_test_xyzab_atomic_save", XYZAB)
            original = xyzab.fresh_state()
            xyzab.save(original)
            changed = json.loads(json.dumps(original))
            changed["gates"]["x"]["open"] = True

            with mock.patch.object(
                xyzab.os, "replace", side_effect=OSError("replace failed")
            ):
                with self.assertRaisesRegex(OSError, "replace failed"):
                    xyzab.save(changed)

            persisted = xyzab.load()
            self.assertFalse(persisted["gates"]["x"]["open"])
        finally:
            if previous_state_dir is None:
                os.environ.pop("XYZAB_STATE_DIR", None)
            else:
                os.environ["XYZAB_STATE_DIR"] = previous_state_dir

    def test_state_failure_rollback_cannot_erase_concurrent_log_append(self) -> None:
        previous_state_dir = os.environ.get("XYZAB_STATE_DIR")
        previous_wiki = os.environ.get("QLN_WIKI")
        previous_phase_log = os.environ.pop("PHASE_LOG_PATH", None)
        os.environ["XYZAB_STATE_DIR"] = str(self.state_dir)
        os.environ["QLN_WIKI"] = str(self.wiki_dir)
        workers: list[threading.Thread] = []
        try:
            xyzab = load_script("fiveqln_test_xyzab_concurrent_rollback", XYZAB)
            state = xyzab.fresh_state()
            log_path = self.wiki_dir / "state" / "phase_log.json"
            attempted = threading.Event()
            completed = threading.Event()

            def append_concurrently() -> None:
                attempted.set()
                xyzab.PHASE_LOG.append_entry(
                    "S",
                    "x",
                    "mechanical",
                    "Independent concurrent transition",
                    session_id="concurrent-session",
                    path=log_path,
                )
                completed.set()

            def fail_save(_state: dict[str, object]) -> None:
                worker = threading.Thread(target=append_concurrently)
                workers.append(worker)
                worker.start()
                self.assertTrue(attempted.wait(timeout=1))
                self.assertFalse(
                    completed.wait(timeout=0.1),
                    "concurrent append escaped the transaction lock",
                )
                raise OSError("disk full")

            with mock.patch.object(xyzab, "save", side_effect=fail_save):
                with self.assertRaisesRegex(OSError, "disk full"):
                    xyzab.cmd_open(
                        state,
                        "x",
                        "What survives a concurrent rollback?",
                        source_tag="emergent",
                        session_id="failing-session",
                    )

            workers[0].join(timeout=2)
            self.assertFalse(workers[0].is_alive())
            payload = json.loads(log_path.read_text(encoding="utf-8"))
            self.assertEqual(len(payload["entries"]), 1)
            self.assertEqual(payload["entries"][0]["session"], "concurrent-session")
            self.assertEqual(xyzab.next_pending(xyzab.load()), "x")
        finally:
            for worker in workers:
                worker.join(timeout=2)
            if previous_state_dir is None:
                os.environ.pop("XYZAB_STATE_DIR", None)
            else:
                os.environ["XYZAB_STATE_DIR"] = previous_state_dir
            if previous_wiki is None:
                os.environ.pop("QLN_WIKI", None)
            else:
                os.environ["QLN_WIKI"] = previous_wiki
            if previous_phase_log is not None:
                os.environ["PHASE_LOG_PATH"] = previous_phase_log


class ParametricCentrifugeTests(unittest.TestCase):
    def test_unclassified_sources_do_not_dilute_purity(self) -> None:
        module = load_script(
            "fiveqln_test_parametric_neutral_purity", PARAMETRIC_CENTRIFUGE
        )

        neutral_only = module.compute_source_purity(
            [{"phase": "S", "source": "unclassified"}]
        )
        self.assertIsNone(neutral_only["S"])

        mixed = module.compute_source_purity(
            [
                {"phase": "S", "source": "emergent"},
                {"phase": "S", "source": "unclassified"},
            ]
        )
        self.assertEqual(mixed["S"], 1.0)

        classified = module.compute_source_purity(
            [
                {"phase": "S", "source": "emergent"},
                {"phase": "S", "source": "mechanical"},
                {"phase": "S", "source": "unclassified"},
            ]
        )
        self.assertEqual(classified["S"], 0.5)


class PhaseLogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.wiki_dir = Path(self.tempdir.name) / "wiki"
        self.env = os.environ.copy()
        self.env["QLN_WIKI"] = str(self.wiki_dir)
        self.env.pop("PHASE_LOG_PATH", None)
        self.env["PYTHONDONTWRITEBYTECODE"] = "1"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def run_phase_log(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(PHASE_LOG), *args],
            text=True,
            capture_output=True,
            env=self.env,
            check=False,
        )

    def test_phase_log_is_bundled_with_learning_aligner(self) -> None:
        self.assertTrue(PHASE_LOG.is_file())

    def test_concurrent_appends_are_serialized(self) -> None:
        phase_log = load_script("fiveqln_test_phase_log_lock", PHASE_LOG)
        log_path = Path(self.tempdir.name) / "concurrent" / "phase-log.json"
        original_save = phase_log.save_log
        first_in_save = threading.Event()
        second_in_save = threading.Event()
        release_first = threading.Event()
        errors: list[BaseException] = []

        def delayed_save(data, path=None):
            session = data["entries"][-1]["session"]
            if session == "first":
                first_in_save.set()
                release_first.wait(timeout=5)
            else:
                second_in_save.set()
            original_save(data, path)

        def append(session: str) -> None:
            try:
                phase_log.append_entry(
                    "S",
                    "x",
                    "emergent",
                    "What is trying to emerge?",
                    session_id=session,
                    path=log_path,
                )
            except BaseException as exc:  # surfaced after both threads join
                errors.append(exc)

        with mock.patch.object(phase_log, "save_log", side_effect=delayed_save):
            first = threading.Thread(target=append, args=("first",))
            second = threading.Thread(target=append, args=("second",))
            first.start()
            self.assertTrue(first_in_save.wait(timeout=5))
            second.start()
            overlapped = second_in_save.wait(timeout=0.5)
            release_first.set()
            first.join(timeout=5)
            second.join(timeout=5)

        self.assertFalse(overlapped, "second writer entered save before first completed")
        self.assertEqual(errors, [])
        entries = phase_log.load_log(log_path)["entries"]
        self.assertEqual([entry["session"] for entry in entries], ["first", "second"])

    def test_append_and_tagline_are_deterministic(self) -> None:
        append = self.run_phase_log(
            "append",
            "S",
            "x",
            "emergent",
            "-c",
            "What is trying to emerge?",
            "--session-id",
            "session-test",
            "--cycle",
            "1",
        )
        self.assertEqual(append.returncode, 0, append.stderr)
        self.assertTrue(json.loads(append.stdout)["ok"])

        tagline = self.run_phase_log("tagline", "--session-id", "session-test")
        self.assertEqual(tagline.returncode, 0, tagline.stderr)
        self.assertEqual(tagline.stdout.strip(), "S:emergent")

        payload = json.loads(
            (self.wiki_dir / "state" / "phase_log.json").read_text(encoding="utf-8")
        )
        self.assertEqual(payload["version"], 1)
        self.assertEqual(payload["entries"][0]["cycle"], 1)

    def test_unclassified_source_remains_neutral(self) -> None:
        append = self.run_phase_log(
            "append",
            "S",
            "x",
            "unclassified",
            "-c",
            "What is trying to emerge?",
        )
        self.assertEqual(append.returncode, 0, append.stderr)
        entry = json.loads(append.stdout)["entry"]
        self.assertIsNone(entry["side"])

    def test_source_tag_must_match_phase(self) -> None:
        mismatch = self.run_phase_log(
            "append",
            "S",
            "x",
            "revealed",
            "-c",
            "What is trying to emerge?",
        )
        self.assertNotEqual(mismatch.returncode, 0)
        self.assertIn("source tag revealed is not valid for phase S", mismatch.stderr)

    def test_centrifuge_reads_the_same_explicit_phase_log(self) -> None:
        explicit_log = Path(self.tempdir.name) / "runtime" / "phase-log.json"
        self.env["PHASE_LOG_PATH"] = str(explicit_log)
        append = self.run_phase_log(
            "append",
            "S",
            "x",
            "emergent",
            "-c",
            "What is trying to emerge?",
            "--session-id",
            "shared-runtime",
        )
        self.assertEqual(append.returncode, 0, append.stderr)

        result = subprocess.run(
            [sys.executable, str(CENTRIFUGE), "chain"],
            text=True,
            capture_output=True,
            env=self.env,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "shared-runtime: S:emergent")

    def test_parametric_centrifuge_reads_the_same_explicit_phase_log(self) -> None:
        explicit_log = Path(self.tempdir.name) / "runtime" / "phase-log.json"
        self.env["PHASE_LOG_PATH"] = str(explicit_log)
        append = self.run_phase_log(
            "append",
            "S",
            "x",
            "emergent",
            "-c",
            "What is trying to emerge?",
            "--session-id",
            "shared-parametric-runtime",
        )
        self.assertEqual(append.returncode, 0, append.stderr)

        result = subprocess.run(
            [sys.executable, str(PARAMETRIC_CENTRIFUGE), "serve"],
            text=True,
            capture_output=True,
            env=self.env,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["current"]["cycles"], 1)


if __name__ == "__main__":
    unittest.main()
