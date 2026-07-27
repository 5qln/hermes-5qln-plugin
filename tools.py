"""Tool handlers for the Hermes 5QLN plugin.

Handlers invoke the bundled deterministic scripts without a shell. They return
JSON strings on success and failure, as required by Hermes' plugin contract.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from . import fractal_memory as fractal_runtime


_PLUGIN_DIR = Path(__file__).resolve().parent
_CONVERTER_SCRIPT_DIR = _PLUGIN_DIR / "skills" / "5qln-converter" / "scripts"
_RESEARCH_SCRIPT_DIR = _PLUGIN_DIR / "skills" / "5qln-deep-research" / "scripts"
_SKILL_FORMATION_SCRIPT_DIR = _PLUGIN_DIR / "skills" / "5qln-skill-formation" / "scripts"
_TIMEOUT_SECONDS = 300


def _json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False)


def _path(value: Any, field: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty path string")
    return Path(value).expanduser().resolve()


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text")
    return value.strip()


def _input_path(value: Any, field: str) -> Path:
    path = _path(value, field)
    if not path.is_file():
        raise ValueError(f"{field} is not a readable file: {path}")
    return path


def _output_path(value: Any, field: str, overwrite: bool) -> Path:
    path = _path(value, field)
    if path.exists() and not overwrite:
        raise ValueError(f"{field} already exists; set overwrite=true to replace it: {path}")
    return path


def _run(
    script_dir: Path, script_name: str, arguments: list[str]
) -> subprocess.CompletedProcess[str]:
    script = script_dir / script_name
    if not script.is_file():
        raise RuntimeError(f"Bundled script is missing: {script_name}")
    return subprocess.run(
        [sys.executable, str(script), *arguments],
        check=False,
        capture_output=True,
        text=True,
        timeout=_TIMEOUT_SECONDS,
    )


def _failure(operation: str, exc: Exception) -> str:
    return _json({"success": False, "operation": operation, "error": str(exc)})


def inventory_source(args: dict[str, Any], **kwargs: Any) -> str:
    """Create an atomic source inventory."""
    del kwargs
    operation = "inventory_source"
    try:
        source_values = args.get("source_paths")
        if not isinstance(source_values, list) or not source_values:
            raise ValueError("source_paths must contain at least one file path")
        sources = [_input_path(value, f"source_paths[{index}]") for index, value in enumerate(source_values)]
        overwrite = bool(args.get("overwrite", False))
        output = _output_path(args.get("output_path"), "output_path", overwrite)
        command = [*(str(path) for path in sources), "--out", str(output)]
        if bool(args.get("compact", False)):
            command.append("--compact")
        completed = _run(_CONVERTER_SCRIPT_DIR, "inventory_source.py", command)
        if completed.returncode != 0:
            return _json(
                {
                    "success": False,
                    "operation": operation,
                    "exit_code": completed.returncode,
                    "stdout": completed.stdout.strip(),
                    "stderr": completed.stderr.strip(),
                }
            )
        payload = json.loads(output.read_text(encoding="utf-8"))
        return _json(
            {
                "success": True,
                "operation": operation,
                "output_path": str(output),
                "summary": payload.get("summary", {}),
                "warnings": payload.get("warnings", []),
                "stdout": completed.stdout.strip(),
            }
        )
    except Exception as exc:  # Hermes handlers must not raise into the tool loop.
        return _failure(operation, exc)


def create_manifest(args: dict[str, Any], **kwargs: Any) -> str:
    """Create an exact conversion-manifest scaffold."""
    del kwargs
    operation = "create_manifest"
    try:
        inventory = _input_path(args.get("inventory_path"), "inventory_path")
        overwrite = bool(args.get("overwrite", False))
        output = _output_path(args.get("output_path"), "output_path", overwrite)
        title = args.get("title", "Untitled 5QLN conversion")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title must be non-empty text")
        completed = _run(
            _CONVERTER_SCRIPT_DIR,
            "new_manifest.py",
            [str(inventory), "--out", str(output), "--title", title.strip()],
        )
        if completed.returncode != 0:
            return _json(
                {
                    "success": False,
                    "operation": operation,
                    "exit_code": completed.returncode,
                    "stdout": completed.stdout.strip(),
                    "stderr": completed.stderr.strip(),
                }
            )
        payload = json.loads(output.read_text(encoding="utf-8"))
        return _json(
            {
                "success": True,
                "operation": operation,
                "output_path": str(output),
                "title": payload.get("title"),
                "source_units": len(payload.get("source", {}).get("units", [])),
                "lens_checks": len(payload.get("lens_audit", [])),
                "completion_status": payload.get("completion", {}).get("status"),
                "stdout": completed.stdout.strip(),
            }
        )
    except Exception as exc:
        return _failure(operation, exc)


def compile_manifest(args: dict[str, Any], **kwargs: Any) -> str:
    """Compile a manifest and return the full report."""
    del kwargs
    operation = "compile_manifest"
    temporary_report: Path | None = None
    try:
        manifest = _input_path(args.get("manifest_path"), "manifest_path")
        overwrite = bool(args.get("overwrite", False))
        report_value = args.get("report_path")
        if report_value is None:
            handle = tempfile.NamedTemporaryFile(prefix="5qln-report-", suffix=".json", delete=False)
            handle.close()
            temporary_report = Path(handle.name)
            report = temporary_report
        else:
            report = _output_path(report_value, "report_path", overwrite)

        completed = _run(
            _CONVERTER_SCRIPT_DIR,
            "5qln_compiler.py",
            [str(manifest), "--report", str(report)],
        )
        if completed.returncode not in {0, 1} or not report.is_file():
            return _json(
                {
                    "success": False,
                    "operation": operation,
                    "exit_code": completed.returncode,
                    "stdout": completed.stdout.strip(),
                    "stderr": completed.stderr.strip(),
                }
            )
        payload = json.loads(report.read_text(encoding="utf-8"))
        return _json(
            {
                "success": True,
                "operation": operation,
                "valid": payload.get("status") == "passed",
                "report_path": None if temporary_report is not None else str(report),
                "report": payload,
                "stdout": completed.stdout.strip(),
                "stderr": completed.stderr.strip(),
            }
        )
    except Exception as exc:
        return _failure(operation, exc)
    finally:
        if temporary_report is not None:
            try:
                temporary_report.unlink(missing_ok=True)
            except OSError:
                pass


def fractal_memory(args: dict[str, Any], **kwargs: Any) -> str:
    """Install, inspect, or export bounded session-orchestrator state."""
    del kwargs
    operation = "fractal_memory"
    try:
        action = args.get("action")
        home_value = args.get("hermes_home")
        home = (
            Path(home_value).expanduser().resolve()
            if isinstance(home_value, str) and home_value.strip()
            else Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).expanduser().resolve()
        )
        if action == "install":
            seed_path = _input_path(args.get("seed_path"), "seed_path")
            result = fractal_runtime.install_seed(
                seed_path,
                home,
                replace=bool(args.get("replace", False)),
            )
        elif action == "show":
            result = fractal_runtime.load_installed_seed(home)
            if result is None:
                raise FileNotFoundError("no parametric-fractal state is installed")
        elif action == "export":
            output_path = _path(args.get("output_path"), "output_path")
            result = fractal_runtime.export_seed(
                home,
                output_path,
                replace=bool(args.get("replace", False)),
            )
        else:
            raise ValueError("action must be install, show, or export")
        return _json({"success": True, "operation": operation, "action": action, "result": result})
    except Exception as exc:
        return _failure(operation, exc)


def validate_research_prompt(args: dict[str, Any], **kwargs: Any) -> str:
    """Validate one standalone 5QLN deep-research prompt."""
    del kwargs
    operation = "validate_research_prompt"
    try:
        prompt = _input_path(args.get("prompt_path"), "prompt_path")
        overwrite = bool(args.get("overwrite", False))
        report_value = args.get("report_path")
        report_path = (
            None
            if report_value is None
            else _output_path(report_value, "report_path", overwrite)
        )

        completed = _run(
            _RESEARCH_SCRIPT_DIR,
            "validate_research_prompt.py",
            [str(prompt), "--json"],
        )
        if completed.returncode not in {0, 1}:
            return _json(
                {
                    "success": False,
                    "operation": operation,
                    "exit_code": completed.returncode,
                    "stdout": completed.stdout.strip(),
                    "stderr": completed.stderr.strip(),
                }
            )

        try:
            report = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Validator returned invalid JSON: {exc}") from exc

        if report_path is not None:
            report_path.write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

        return _json(
            {
                "success": True,
                "operation": operation,
                "valid": report.get("valid") is True,
                "report_path": None if report_path is None else str(report_path),
                "report": report,
                "stderr": completed.stderr.strip(),
            }
        )
    except Exception as exc:
        return _failure(operation, exc)


def create_skill_manifest(args: dict[str, Any], **kwargs: Any) -> str:
    """Create a skill-v1 formation manifest scaffold."""
    del kwargs
    operation = "create_skill_manifest"
    try:
        bundle_root = _path(args.get("bundle_root"), "bundle_root")
        if not bundle_root.is_dir():
            raise ValueError("bundle_root must be a directory")
        overwrite = bool(args.get("overwrite", False))
        output = _output_path(args.get("output_path"), "output_path", overwrite)
        conversion = args.get("conversion_manifest", "provenance/conversion-manifest.json")
        if not isinstance(conversion, str) or not conversion.strip():
            raise ValueError("conversion_manifest must be a non-empty relative path")

        completed = _run(
            _SKILL_FORMATION_SCRIPT_DIR,
            "new_skill_manifest.py",
            [str(bundle_root), "--out", str(output), "--conversion-manifest", conversion.strip()],
        )
        if completed.returncode != 0:
            return _json({
                "success": False, "operation": operation,
                "exit_code": completed.returncode,
                "stdout": completed.stdout.strip(), "stderr": completed.stderr.strip(),
            })
        payload = json.loads(output.read_text(encoding="utf-8"))
        return _json({
            "success": True, "operation": operation, "output_path": str(output),
            "skill_name": payload.get("skill", {}).get("name"),
            "bundle_sha256": payload.get("skill", {}).get("bundle_sha256"),
            "human_review_status": payload.get("human_review", {}).get("status", "open"),
            "promotion_state": payload.get("promotion", {}).get("requested_state", "draft"),
            "stdout": completed.stdout.strip(),
        })
    except Exception as exc:
        return _failure(operation, exc)


def verify_skill(args: dict[str, Any], **kwargs: Any) -> str:
    """Verify a skill-v1 formation manifest."""
    del kwargs
    operation = "verify_skill"
    try:
        manifest = _input_path(args.get("manifest_path"), "manifest_path")
        overwrite = bool(args.get("overwrite", False))
        promotion_mode = bool(args.get("promotion_mode", False))

        report_value = args.get("report_path")
        report_path: Path | None = None
        if report_value is not None:
            report_path = _output_path(report_value, "report_path", overwrite)

        command = [str(manifest)]
        if report_path is not None:
            command += ["--report", str(report_path)]
        if promotion_mode:
            command.append("--promotion-mode")

        completed = _run(_SKILL_FORMATION_SCRIPT_DIR, "verify_skill.py", command)
        if completed.returncode not in {0, 1, 2}:
            return _json({
                "success": False, "operation": operation,
                "exit_code": completed.returncode,
                "stdout": completed.stdout.strip(), "stderr": completed.stderr.strip(),
            })

        report: dict[str, Any] = {}
        if report_path is not None and report_path.is_file():
            report = json.loads(report_path.read_text(encoding="utf-8"))
        elif completed.stdout.strip():
            try:
                report = json.loads(completed.stdout)
            except json.JSONDecodeError:
                pass

        execution_success = report.get("execution_success", completed.returncode != 2)
        return _json({
            "success": execution_success,
            "operation": operation,
            "execution_success": execution_success,
            "structural_status": report.get("structural_status", "failed"),
            "behavioral_status": report.get("behavioral_status", "not_declared"),
            "human_review_status": report.get("human_review_status", "open"),
            "promotion_ready": report.get("promotion_ready", False),
            "report": report,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        })
    except Exception as exc:
        return _failure(operation, exc)
