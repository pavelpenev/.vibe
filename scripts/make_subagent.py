#!/usr/bin/env python3
# SCRIPT-METADATA:
# name: make_subagent
# description: Generate a model-tiered subagent variant from a role template, register it in config.toml, and wire it into the system prompt and README
# tags: config,subagent

"""Generate a model-tiered subagent variant and wire it everywhere.

Vibe CLI binds a subagent's model at config time, so model diversity for a
shared-prompt role requires separate agent TOMLs. This script stamps a new
variant from the role's canonical template and wires it into config.toml, the
system-prompt delegation table, and the README agents table. For reviewers, it
also updates the tier tables and the review skill's subagents table.

Roles (see ROLES below):
  - reviewer: tiered review spread (has tier tables + skill table)
  - generic-implementor: intent-based Python/JSON/YAML/MD/TOML editing
  - lisp-implementor: intent-based Lisp editing with form extraction
  - advisor: independent perspective on architectural/risky decisions

Usage:
    make_subagent.py <model-alias> <suffix> --role <role> [flags]

Examples:
    make_subagent.py gpt-5.6-luna luna --role generic-implementor
        -> agents/generic-implementor-luna.toml
    make_subagent.py claude-opus opus --role reviewer --quick --standard
        -> agents/reviewer-opus.toml, in quick + standard + deep
    make_subagent.py gpt-5.6-luna luna --role advisor --dry-run
        -> preview only, write nothing

The <model-alias> must exist as an `alias` in config.toml's [[models]].
The <suffix> becomes the agent name: <role-base>-<suffix> (e.g., reviewer-sol,
generic-implementor-luna, advisor-luna).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    sys.exit("error: this script requires Python 3.11+ (tomllib).")

VIBE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = VIBE_DIR / "config.toml"
AGENTS_DIR = VIBE_DIR / "agents"
SYSTEM_PROMPT_PATH = VIBE_DIR / "prompts" / "system-prompt-large.md"
README_PATH = VIBE_DIR / "README.md"
SKILL_PATH = VIBE_DIR / "skills" / "review" / "SKILL.md"


# ── role registry ───────────────────────────────────────────────────────────

# Each role defines how to stamp the TOML, what delegation/agents-table row to
# generate, and whether tier/skill edits apply.
#
# Fields with {suffix}, {model}, {agent}, {alias} are format-substituted.
ROLES: dict[str, dict] = {
    "reviewer": {
        "template": "reviewer-deepseek.toml",
        "prompt_id": "reviewer",
        "display": "Reviewer ({suffix})",
        "description": "Independent artifact reviewer on {model}; read-only review of code, docs, specs, plans",
        "delegation_anchor": r"`reviewer-sol`",
        "delegation_row": "| `{agent}` | Markdown report | Independent review on {model} | Verifying runtime behavior — it can't execute code |",
        "agents_purpose": "Independent artifact review",
        "agents_anchor": r"reviewer-sol.*Independent artifact review",
        "safety": "Safe",
        "has_tiers": True,
        "has_skill": True,
    },
    "generic-implementor": {
        "template": "generic-implementor.toml",
        "prompt_id": "generic-implementor",
        "display": "Generic Implementor ({suffix})",
        "description": "Backup generic implementor on {model}; intent-based Python/JSON/YAML/MD/TOML file editing",
        "delegation_anchor": r"`generic-implementor`",
        "delegation_row": "| `{agent}` | JSON summary | Backup generic implementor on {model}; same role as `generic-implementor` when deepseek is down or usage exhausted | Lisp files (use `lisp-implementor`) |",
        "agents_purpose": "Backup generic implementor ({model})",
        "agents_anchor": r"\| generic-implementor \|",
        "safety": "Neutral",
        "has_tiers": False,
        "has_skill": False,
    },
    "lisp-implementor": {
        "template": "lisp-implementor.toml",
        "prompt_id": "lisp-implementor",
        "display": "Lisp Implementor ({suffix})",
        "description": "Backup Lisp implementor on {model}; intent-based Lisp editing with form extraction for s-expression safety",
        "delegation_anchor": r"`lisp-implementor`",
        "delegation_row": "| `{agent}` | JSON summary | Backup Lisp implementor on {model}; same role as `lisp-implementor` when deepseek is down or usage exhausted | Non-Lisp files (use `generic-implementor`) |",
        "agents_purpose": "Backup Lisp implementor ({model})",
        "agents_anchor": r"\| lisp-implementor \|",
        "safety": "Neutral",
        "has_tiers": False,
        "has_skill": False,
    },
    "advisor": {
        "template": "advisor.toml",
        "prompt_id": "advisor",
        "display": "Advisor ({suffix})",
        "description": "Backup advisor on {model}; independent perspective on difficult decisions, architectural choices, and risky operations",
        "delegation_anchor": r"`advisor`",
        "delegation_row": "| `{agent}` | Markdown advice | Backup advisor on {model}; same role as `advisor` | Routine work, execution, file modifications |",
        "agents_purpose": "Backup advisor ({model})",
        "agents_anchor": r"\| advisor \|",
        "safety": "Safe",
        "has_tiers": False,
        "has_skill": False,
    },
}


# ── config.toml ──────────────────────────────────────────────────────────────

def load_model_aliases() -> dict[str, str]:
    """Return {alias: model_name} from config.toml's [[models]]."""
    with open(CONFIG_PATH, "rb") as fh:
        cfg = tomllib.load(fh)
    aliases: dict[str, str] = {}
    for model in cfg.get("models", []):
        alias = model.get("alias")
        if alias:
            aliases[alias] = model.get("name", alias)
    return aliases


def register_in_allowlist(agent_name: str) -> str:
    """Insert agent_name into config.toml's [tools.task] allowlist if absent.

    Returns the (possibly modified) config text. Idempotent.
    """
    text = CONFIG_PATH.read_text()

    section_match = re.search(r"^\[tools\.task\]\s*$", text, flags=re.MULTILINE)
    if not section_match:
        sys.exit("error: [tools.task] section not found in config.toml")
    section_start = section_match.end()

    allow_match = re.search(r"allowlist\s*=\s*\[", text[section_start:])
    if not allow_match:
        sys.exit("error: allowlist not found in [tools.task] section")
    allow_start = section_start + allow_match.end()

    bracket_depth = 1
    i = allow_start
    while i < len(text) and bracket_depth > 0:
        if text[i] == "[":
            bracket_depth += 1
        elif text[i] == "]":
            bracket_depth -= 1
        i += 1
    if bracket_depth != 0:
        sys.exit("error: unmatched brackets in [tools.task] allowlist")
    allow_body = text[allow_start : i - 1]

    if re.search(rf'"{re.escape(agent_name)}"\s*,?', allow_body):
        return text

    entry_match = re.search(r"^(\s*)\"\w+\"", allow_body, flags=re.MULTILINE)
    indent = entry_match.group(1) if entry_match else "    "

    insertion = f"\n{indent}\"{agent_name}\","
    return text[:allow_start] + insertion + text[allow_start:]


# ── agent TOML ───────────────────────────────────────────────────────────────

def stamp_template(role: dict, alias: str, suffix: str, model_name: str) -> str:
    """Read the role's template TOML and swap the three model-specific fields."""
    template_path = AGENTS_DIR / role["template"]
    if not template_path.exists():
        sys.exit(f"error: template not found: {template_path}")
    text = template_path.read_text()

    display = role["display"].format(suffix=suffix.capitalize())
    description = role["description"].format(model=model_name)

    def replace_field(body: str, field: str, value: str) -> str:
        pattern = rf'^({field}\s*=\s*)"[^"]*"\s*$'
        repl = lambda m: f'{m.group(1)}"{value}"'
        new, n = re.subn(pattern, repl, body, count=1, flags=re.MULTILINE)
        if n != 1:
            sys.exit(f"error: could not find {field!r} in template {template_path}")
        return new

    text = replace_field(text, "display_name", display)
    text = replace_field(text, "description", description)
    text = replace_field(text, "active_model", alias)
    return text


# ── tier tables (reviewer only) ─────────────────────────────────────────────

def _find_tier_line(lines: list[str], keyword: str) -> int:
    """Return index of the tier table row whose first cell contains keyword."""
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = stripped.split("|")
        if len(cells) < 4:
            continue
        if keyword in cells[1] and "reviewer-" in line:
            return i
    return -1


def _append_to_composition(line: str, agent_name: str) -> str:
    """Append ' + agent_name' after the last reviewer-xxx before the trailing |."""
    return re.sub(
        r"(reviewer-\w+)(\s*\|\s*)$",
        r"\1 + " + agent_name + r"\2",
        line,
        count=1,
    )


def edit_tier_table(
    text: str, agent_name: str, quick: bool, standard: bool
) -> tuple[str, list[str]]:
    """Edit the Quick/Standard/Deep rows' Composition cells.

    Returns (new_text, list_of_changes).
    """
    lines = text.split("\n")
    changes: list[str] = []

    quick_i = _find_tier_line(lines, "Quick")
    if quick_i >= 0 and quick and agent_name not in lines[quick_i]:
        line = lines[quick_i]
        if "}" in line:
            lines[quick_i] = line.replace("}", ", " + agent_name + "}", 1)
            changes.append("quick")
        else:
            sys.exit(f"error: Quick tier row has no set notation: {line!r}")

    std_i = _find_tier_line(lines, "Standard")
    if std_i >= 0 and standard and agent_name not in lines[std_i]:
        lines[std_i] = _append_to_composition(lines[std_i], agent_name)
        changes.append("standard")

    deep_i = _find_tier_line(lines, "Deep")
    if deep_i >= 0 and not standard and agent_name not in lines[deep_i]:
        lines[deep_i] = _append_to_composition(lines[deep_i], agent_name)
        changes.append("deep")

    if quick_i < 0 or std_i < 0 or deep_i < 0:
        missing = []
        if quick_i < 0:
            missing.append("Quick")
        if std_i < 0:
            missing.append("Standard")
        if deep_i < 0:
            missing.append("Deep")
        sys.exit(
            f"error: tier row(s) not found: {', '.join(missing)} "
            f"(file may have been hand-edited)"
        )

    return "\n".join(lines), changes


# ── delegation / agents / subagents table rows ──────────────────────────────

def add_row_after(
    text: str, anchor_pattern: str, new_row: str, exists_check: str, label: str
) -> tuple[str, bool]:
    """Insert new_row after the first line matching anchor_pattern.

    Idempotent: if exists_check is found in text, returns (text, False).
    Use a table-specific check (e.g. backtick-wrapped name, or `| name |`)
    to avoid false positives from other tables in the same file.
    """
    if exists_check in text:
        return text, False
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if re.search(anchor_pattern, line):
            lines.insert(i + 1, new_row)
            return "\n".join(lines), True
    sys.exit(f"error: {label} insertion anchor not found (pattern: {anchor_pattern!r})")


def add_delegation_row(text: str, role: dict, agent_name: str, model_name: str) -> tuple[str, bool]:
    """Add a role-specific row to the system-prompt delegation table."""
    row = role["delegation_row"].format(agent=agent_name, model=model_name)
    return add_row_after(
        text, role["delegation_anchor"], row, f"`{agent_name}`", "delegation table"
    )


def add_agents_table_row(
    text: str, role: dict, agent_name: str, alias: str, model_name: str
) -> tuple[str, bool]:
    """Add a role-specific row to the README agents table and bump the count."""
    purpose = role["agents_purpose"].format(model=model_name)
    row = f"| {agent_name} | {purpose} | {alias} | {role['safety']} |"
    text, inserted = add_row_after(
        text, role["agents_anchor"], row, f"| {agent_name} |", "agents table"
    )
    if inserted:
        text = re.sub(
            r"(## Agents \()(\d+)(\))",
            lambda m: f"{m.group(1)}{int(m.group(2)) + 1}{m.group(3)}",
            text,
            count=1,
        )
    return text, inserted


def add_skill_subagent_row(
    text: str, agent_name: str, model_name: str, alias: str
) -> tuple[str, bool]:
    """Add a generic reviewer row to the review skill's subagents table."""
    model_display = f"{model_name} ({alias})" if model_name != alias else model_name
    row = f"| `{agent_name}` | {model_display} | — |"
    return add_row_after(
        text, r"`reviewer-sol`.*strongest", row, f"`{agent_name}`", "skill subagents table"
    )


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Generate a model-tiered subagent variant and wire it in.",
    )
    ap.add_argument("model_alias", help="Model alias from config.toml [[models]]")
    ap.add_argument("suffix", help="Agent name suffix -> <role>-<suffix>")
    ap.add_argument("--role", default="reviewer", choices=sorted(ROLES),
                    help="Role to generate (default: reviewer)")
    ap.add_argument("--quick", action="store_true", help="Also add to Quick tier (reviewer only)")
    ap.add_argument("--standard", action="store_true", help="Also add to Standard tier (reviewer only)")
    ap.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    ap.add_argument("--force", action="store_true", help="Overwrite an existing agent TOML")
    args = ap.parse_args()

    role = ROLES[args.role]

    if (args.quick or args.standard) and not role["has_tiers"]:
        sys.exit(f"error: --quick/--standard only apply to tiered roles (reviewer), not {args.role!r}")

    aliases = load_model_aliases()
    if args.model_alias not in aliases:
        known = ", ".join(sorted(aliases)) or "(none)"
        sys.exit(f"error: model alias {args.model_alias!r} not found in config.toml. Known: {known}")
    model_name = aliases[args.model_alias]

    # Agent name: <role-base>-<suffix>. For reviewer the base is "reviewer", for
    # generic-implementor it's "generic-implementor", etc.
    agent_name = f"{args.role}-{args.suffix}"
    toml_path = AGENTS_DIR / f"{agent_name}.toml"

    exists = toml_path.exists()
    if exists and not args.force and not args.dry_run:
        sys.exit(f"error: {toml_path} already exists (use --force to overwrite)")

    # Compute all changes before writing anything.
    stamped = stamp_template(role, args.model_alias, args.suffix, model_name)
    new_config = register_in_allowlist(agent_name)

    sys_text = SYSTEM_PROMPT_PATH.read_text()
    tier_changes: list[str] = []
    subagent_added = False
    if role["has_tiers"]:
        sys_text, tier_changes = edit_tier_table(sys_text, agent_name, args.quick, args.standard)
    sys_text, deleg_added = add_delegation_row(sys_text, role, agent_name, model_name)

    readme_text = README_PATH.read_text()
    readme_tier_changes: list[str] = []
    if role["has_tiers"]:
        readme_text, readme_tier_changes = edit_tier_table(readme_text, agent_name, args.quick, args.standard)
    readme_text, agents_added = add_agents_table_row(readme_text, role, agent_name, args.model_alias, model_name)

    skill_changes: list[str] = []
    if role["has_skill"]:
        skill_text = SKILL_PATH.read_text()
        skill_text, skill_tier_changes = edit_tier_table(skill_text, agent_name, args.quick, args.standard)
        skill_text, subagent_added = add_skill_subagent_row(skill_text, agent_name, model_name, args.model_alias)

    # Summary
    print(f"role        : {args.role}")
    print(f"model alias : {args.model_alias} (model name: {model_name})")
    print(f"agent name  : {agent_name}")
    print(f"display     : {role['display'].format(suffix=args.suffix.capitalize())}")
    print(f"toml path   : {toml_path}")
    if role["has_tiers"]:
        tiers = ["deep"]
        if args.standard:
            tiers = ["standard", "deep (via standard)"]
        if args.quick:
            tiers.append("quick")
        print(f"tiers       : {', '.join(tiers)}")
    config_changed = new_config != CONFIG_PATH.read_text()
    print(f"config      : {'add to allowlist' if config_changed else 'already in allowlist'}")
    if exists:
        print(f"toml        : {'overwrite' if args.force else 'exists (use --force)'}")
    else:
        print(f"toml        : create")
    print(f"system prompt: tiers={tier_changes or 'n/a'}, delegation row={'yes' if deleg_added else 'already present'}")
    print(f"README      : tiers={readme_tier_changes or 'n/a'}, agents row={'yes' if agents_added else 'already present'}")
    if role["has_skill"]:
        print(f"review skill: tiers={skill_tier_changes or 'none'}, subagents row={'yes' if subagent_added else 'already present'}")

    if args.dry_run:
        print("\n--- dry run: no files written ---")
        return 0

    toml_path.write_text(stamped)
    if config_changed:
        CONFIG_PATH.write_text(new_config)
    SYSTEM_PROMPT_PATH.write_text(sys_text)
    README_PATH.write_text(readme_text)
    if role["has_skill"]:
        SKILL_PATH.write_text(skill_text)

    print(f"\ncreated {toml_path}")
    if config_changed:
        print(f"registered {agent_name!r} in {CONFIG_PATH}")
    print(f"updated {SYSTEM_PROMPT_PATH}")
    print(f"updated {README_PATH}")
    if role["has_skill"]:
        print(f"updated {SKILL_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
