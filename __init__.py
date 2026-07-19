"""5QLN for Hermes Agent: plugin registration."""

from pathlib import Path

from . import schemas, tools


def register(ctx):
    """Register deterministic 5QLN tools and the namespaced conversion skill."""
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

    skill_md = Path(__file__).resolve().parent / "skills" / "5qln-converter" / "SKILL.md"
    if not skill_md.is_file():
        raise FileNotFoundError(f"Bundled 5QLN skill is missing: {skill_md}")
    ctx.register_skill("5qln-converter", skill_md)


__all__ = ["register"]

