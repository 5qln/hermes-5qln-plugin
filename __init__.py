"""5QLN for Hermes Agent: plugin registration."""

from pathlib import Path

from . import fractal_memory, schemas, tools


def _seed_external_skills_dir(skill_root: Path) -> None:
    """Add the plugin's skills directory to skills.external_dirs in config.yaml.

    Hermes' prompt builder scans ``skills.external_dirs`` for skills to
    list in ``<available_skills>``.  Plugin-registered skills are not
    included by default, so we seed the plugin's skills/ directory here
    to make them visible without a manual ``hermes skills tap add`` step.
    """
    try:
        from hermes_cli.config import get_config_path, read_raw_config
        from hermes_cli.auth import atomic_yaml_write
    except ImportError:
        return  # Not running inside a Hermes process (e.g. tests, docs)

    try:
        config_path = get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config = read_raw_config()

        skills_cfg = config.get("skills")
        if not isinstance(skills_cfg, dict):
            skills_cfg = {}
            config["skills"] = skills_cfg

        existing = skills_cfg.get("external_dirs")
        if isinstance(existing, str):
            existing = [existing]
        elif not isinstance(existing, list):
            existing = []

        target = str(skill_root.resolve())
        if target not in existing:
            existing.append(target)
            skills_cfg["external_dirs"] = existing
            atomic_yaml_write(config_path, config, sort_keys=False)
    except Exception:
        pass  # Best-effort — plugin still works, skills just won't appear in prompt


def register(ctx):
    """Register deterministic 5QLN tools and namespaced semantic skills."""
    ctx.register_tool(
        name="fiveqln_inventory_source",
        toolset="5qln",
        schema=schemas.FIVEQLN_INVENTORY_SOURCE,
        handler=tools.inventory_source,
        description="Build a hash-addressed source ledger before 5QLN conversion.",
    )
    ctx.register_tool(
        name="fiveqln_create_manifest",
        toolset="5qln",
        schema=schemas.FIVEQLN_CREATE_MANIFEST,
        handler=tools.create_manifest,
        description="Create the exact 5QLN conversion-manifest scaffold.",
    )
    ctx.register_tool(
        name="fiveqln_compile_manifest",
        toolset="5qln",
        schema=schemas.FIVEQLN_COMPILE_MANIFEST,
        handler=tools.compile_manifest,
        description="Compile a 5QLN manifest and return its full integrity report.",
    )
    ctx.register_tool(
        name="fiveqln_validate_research_prompt",
        toolset="5qln",
        schema=schemas.FIVEQLN_VALIDATE_RESEARCH_PROMPT,
        handler=tools.validate_research_prompt,
        description="Validate a standalone 5QLN deep-research prompt contract.",
    )
    ctx.register_tool(
        name="fiveqln_fractal_memory",
        toolset="5qln",
        schema=schemas.FIVEQLN_FRACTAL_MEMORY,
        handler=tools.fractal_memory,
        description=(
            "Install, inspect, or export bounded parametric-fractal state for the live 5QLN "
            "session orchestrator; evidence-bearing calibration is CLI-only."
        ),
    )

    ctx.register_hook("pre_llm_call", fractal_memory.pre_llm_context)

    # ---- skill-v1 formation tools (0.6.0) ----
    ctx.register_tool(
        name="fiveqln_create_skill_manifest",
        toolset="5qln",
        schema=schemas.FIVEQLN_CREATE_SKILL_MANIFEST,
        handler=tools.create_skill_manifest,
        description="Scaffold a skill-v1 formation manifest from a bundle directory.",
    )
    ctx.register_tool(
        name="fiveqln_verify_skill",
        toolset="5qln",
        schema=schemas.FIVEQLN_VERIFY_SKILL,
        handler=tools.verify_skill,
        description="Verify a skill-v1 manifest structurally; returns a report with no valid/certified/living claim.",
    )

    skill_root = Path(__file__).resolve().parent / "skills"
    for skill_name in (
        # Base 5QLN — language runtime
        "5qln-agent",
        "5qln-cycle",
        "5qln-initiation",
        "symbolic-interpretation",
        "5qln-converter",
        "5qln-learning-aligner",
        "5qln-manifest-compilation",
        # Experimental
        "5qln-deep-research",
        "5qln-centrifuge",
        "5qln-signature-engine",
        # Skill formation (0.6.0)
        "5qln-skill-formation",
        # Formed skills (0.9.0)
        "5qln-aimless-openness",
    ):
        skill_md = skill_root / skill_name / "SKILL.md"
        if not skill_md.is_file():
            raise FileNotFoundError(f"Bundled 5QLN skill is missing: {skill_md}")
        ctx.register_skill(skill_name, skill_md)

    # ── Seed skills into the prompt-scanner index ──────────────────────
    # ctx.register_skill() makes skills loadable by name but Hermes does
    # not list plugin-provided skills in the <available_skills> prompt by
    # default.  Adding the plugin's skills/ directory to
    # skills.external_dirs in config.yaml makes the prompt builder pick
    # them up — so they appear in /skills, skills_list, and the prompt
    # index without a manual `hermes skills tap add` step.
    _seed_external_skills_dir(skill_root)


__all__ = ["register"]
