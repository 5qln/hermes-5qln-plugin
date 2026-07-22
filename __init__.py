"""5QLN for Hermes Agent: plugin registration."""

from pathlib import Path

from . import schemas, tools


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
    ):
        skill_md = skill_root / skill_name / "SKILL.md"
        if not skill_md.is_file():
            raise FileNotFoundError(f"Bundled 5QLN skill is missing: {skill_md}")
        ctx.register_skill(skill_name, skill_md)


__all__ = ["register"]
