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
