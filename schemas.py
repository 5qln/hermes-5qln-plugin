"""Hermes tool schemas for the 5QLN plugin."""

FIVEQLN_INVENTORY_SOURCE = {
    "name": "fiveqln_inventory_source",
    "description": (
        "Create an atomic, SHA-256-addressed source ledger before a 5QLN conversion. "
        "Use this first for local Markdown, text, RST, log, CSV, TSV, JSON, DOCX, or PDF files. "
        "This inventories K-context; it does not attest that the source is X or certify preservation by itself."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "source_paths": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
                "description": "Absolute or working-directory-relative paths to source files, in source order.",
            },
            "output_path": {
                "type": "string",
                "description": "Path for the JSON source inventory.",
            },
            "compact": {
                "type": "boolean",
                "default": False,
                "description": "Write compact JSON instead of indented JSON.",
            },
            "overwrite": {
                "type": "boolean",
                "default": False,
                "description": "Permit replacing an existing output file.",
            },
        },
        "required": ["source_paths", "output_path"],
        "additionalProperties": False,
    },
}


FIVEQLN_CREATE_MANIFEST = {
    "name": "fiveqln_create_manifest",
    "description": (
        "Create an exact 5QLN conversion-manifest scaffold from a source inventory. "
        "The scaffold preserves the sealed constitutional block, creates 25 literal-v1 lens checks, "
        "and starts all human-dependent claims as open or candidate. It is intentionally incomplete."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "inventory_path": {
                "type": "string",
                "description": "Path to a JSON inventory produced by fiveqln_inventory_source.",
            },
            "output_path": {
                "type": "string",
                "description": "Path for the conversion-manifest JSON scaffold.",
            },
            "title": {
                "type": "string",
                "default": "Untitled 5QLN conversion",
                "description": "Human-readable conversion title.",
            },
            "overwrite": {
                "type": "boolean",
                "default": False,
                "description": "Permit replacing an existing output file.",
            },
        },
        "required": ["inventory_path", "output_path"],
        "additionalProperties": False,
    },
}


FIVEQLN_COMPILE_MANIFEST = {
    "name": "fiveqln_compile_manifest",
    "description": (
        "Compile and audit a completed 5QLN conversion manifest for exact symbols, constitutional drift, "
        "literal-v1 lens orientation, source coverage, traceability, attestation boundaries, corruption guards, "
        "and question-bearing return. A passing report is structural evidence, not AI self-certification of ∞0'."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "manifest_path": {
                "type": "string",
                "description": "Path to the completed conversion-manifest JSON.",
            },
            "report_path": {
                "type": "string",
                "description": "Optional path at which to persist the full compiler report JSON.",
            },
            "overwrite": {
                "type": "boolean",
                "default": False,
                "description": "Permit replacing an existing report file.",
            },
        },
        "required": ["manifest_path"],
        "additionalProperties": False,
    },
}


FIVEQLN_FRACTAL_MEMORY = {
    "name": "fiveqln_fractal_memory",
    "description": (
        "Install, inspect, or export a bounded 5QLN parametric-fractal seed. "
        "The seed drives the session orchestrator through ephemeral per-turn K-context; it carries no transcript. "
        "Evidence-bearing calibration is intentionally CLI-only so exact wording never crosses a Hermes tool-call boundary."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["install", "show", "export"],
            },
            "seed_path": {"type": "string", "description": "Portable JSON seed for install."},
            "output_path": {"type": "string", "description": "Portable JSON destination for export."},
            "hermes_home": {
                "type": "string",
                "description": "Optional Hermes profile home; active HERMES_HOME is used when omitted.",
            },
            "replace": {"type": "boolean", "default": False},
        },
        "required": ["action"],
        "additionalProperties": False,
    },
}


FIVEQLN_VALIDATE_RESEARCH_PROMPT = {
    "name": "fiveqln_validate_research_prompt",
    "description": (
        "Validate one file-based standalone 5QLN deep-research prompt for the exact constitutional kernel, "
        "ordered phase records, evidence and counterevidence gates, source/derived/proposal separation, "
        "delta_E/delta_V flow, two-pass composition, corruption guards, and a question-bearing return. "
        "A passing report is structural evidence; it does not prove research quality, source truth, "
        "human resonance, value alignment, or completion."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "prompt_path": {
                "type": "string",
                "description": "Path to one UTF-8 Markdown or text research prompt.",
            },
            "report_path": {
                "type": "string",
                "description": "Optional path at which to persist the full validation report JSON.",
            },
            "overwrite": {
                "type": "boolean",
                "default": False,
                "description": "Permit replacing an existing report file.",
            },
        },
        "required": ["prompt_path"],
        "additionalProperties": False,
    },
}


# ---- skill-v1 formation tools (0.6.0) ----

FIVEQLN_CREATE_SKILL_MANIFEST = {
    "name": "fiveqln_create_skill_manifest",
    "description": (
        "Create a skill-v1 formation manifest scaffold from a candidate skill bundle directory. "
        "The scaffold inventories every regular file, computes bundle and contract digests, and "
        "leaves all human-dependent fields (triggers, requirements, behavioral fixtures, review, "
        "promotion) open. This tool does not claim the bundle is verified, certified, or living."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "bundle_root": {
                "type": "string",
                "description": "Path to the candidate skill bundle directory.",
            },
            "output_path": {
                "type": "string",
                "description": "Path for the skill-formation-manifest.json scaffold.",
            },
            "conversion_manifest": {
                "type": "string",
                "description": "Optional bundle-relative path to a conversion manifest (default: provenance/conversion-manifest.json).",
            },
            "compact": {
                "type": "boolean",
                "default": False,
                "description": "Write compact JSON instead of indented JSON.",
            },
            "overwrite": {
                "type": "boolean",
                "default": False,
                "description": "Permit replacing an existing output file.",
            },
        },
        "required": ["bundle_root", "output_path"],
        "additionalProperties": False,
    },
}

FIVEQLN_VERIFY_SKILL = {
    "name": "fiveqln_verify_skill",
    "description": (
        "Verify a skill-v1 formation manifest against the published contract. Runs deterministic "
        "structural checks (schema, bundle integrity, SKILL.md frontmatter, script syntax, "
        "conversion provenance), plus optional behavioral observations, human review scoping, "
        "and promotion inspection. Returns a skill-report-v1 with independent evidence dimensions. "
        "A machine pass is structural conformance — it is never certification of living 5QLN."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "manifest_path": {
                "type": "string",
                "description": "Path to the skill-formation-manifest.json to verify.",
            },
            "report_path": {
                "type": "string",
                "description": "Optional path at which to persist the full skill-report-v1 JSON.",
            },
            "observation_paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional paths to observed-run-v1 JSON files for behavioral evidence.",
            },
            "capability_snapshot_path": {
                "type": "string",
                "description": "Optional path to a JSON capability snapshot for tool/skill resolution.",
            },
            "promotion_mode": {
                "type": "boolean",
                "default": False,
                "description": "When true, also inspect promotion readiness for bundled-plugin targets.",
            },
            "loop_mode": {
                "type": "boolean",
                "default": False,
                "description": "When true, verify against the centrifuged axis (standing H direction) so the loop runs without per-iteration human stops. Fails closed on missing/drifted axis.",
            },
            "overwrite": {
                "type": "boolean",
                "default": False,
                "description": "Permit replacing an existing report file.",
            },
        },
        "required": ["manifest_path"],
        "additionalProperties": False,
    },
}
